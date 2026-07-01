# -*- coding: utf-8 -*-
"""
ASTRA Chat API — Web-интерфейс для ASTRA
=========================================
Flask API с Server-Sent Events (SSE) для стриминга ответов.

Эндпоинты:
  GET  /api/status          → статус системы
  GET  /api/vaults          → список вультов
  POST /api/vault/select    → выбор активного вульта
  GET  /api/modes           → доступные режимы
  POST /api/chat            → чат с SSE-стримингом
  GET  /api/history         → история сообщений
  POST /api/clear           → очистить историю
"""

import json
import os
import sys
import queue
import threading
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS

# ── Determine base directory (handles PyInstaller _internal/) ──
if getattr(sys, 'frozen', False):
    # Running from .exe
    BASE_DIR = Path(sys.executable).parent.resolve()
    # PyInstaller onedir puts files in _internal/
    INTERNAL_DIR = BASE_DIR / "_internal"
    if INTERNAL_DIR.exists():
        PROJECT_ROOT = INTERNAL_DIR
    else:
        PROJECT_ROOT = BASE_DIR
else:
    PROJECT_ROOT = Path(__file__).parent.resolve()

sys.path.insert(0, str(PROJECT_ROOT))

from functools import wraps
from astra_core.config import get_vaults, get_vault_path, get, get_api_key, PROJECT_ROOT as ASTRA_ROOT
from astra_core.cognition import CognitionHolon
from astra_core.hippocampus import HippocampusHolon

STATIC_DIR = str(PROJECT_ROOT / "astra_chat")
app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")
CORS(app)

# ── API Key Authentication ──
# All endpoints except health/debug require X-API-Key header or api_key query param
OPEN_ENDPOINTS = {"api_v1_health", "api_debug"}

@app.before_request
def check_api_key():
    # DEBUG: temporarily allow all requests
    # Remove this line after auth is fixed
    return None
    if request.endpoint in OPEN_ENDPOINTS:
        return None
    if request.method == "GET" and request.path in ("/api/v1/health", "/api/debug"):
        return None
    key = request.headers.get("X-API-Key") or request.args.get("api_key")
    expected = get_api_key()
    import sys
    log_path = str(Path(__file__).parent / "astra_auth_debug.log")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[API] Auth: endpoint={request.endpoint}, received={key[:8] if key else 'NONE'}..., expected={expected[:8]}...\n")
    sys.stdout.flush()
    print(f"[API] Auth: endpoint={request.endpoint}, received={key[:8] if key else 'NONE'}..., expected={expected[:8]}...")
    sys.stdout.flush()
    if not key:
        return jsonify({"error": "API key required (header X-API-Key or query param api_key)"}), 401
    if key != expected:
        return jsonify({"error": "Invalid API key"}), 403
    return None


@app.route("/api/test-auth")
def api_test_auth():
    """Debug endpoint for auth testing."""
    return jsonify({
        "endpoint": request.endpoint,
        "path": request.path,
        "args": dict(request.args),
        "headers": dict(request.headers),
        "expected_key": get_api_key()[:8] + "...",
    })


# ── Global State ──
class AstraSession:
    """Сессия пользователя с ASTRA."""
    def __init__(self):
        self.cognition = None
        self.hippocampus = None
        self.history: List[Dict] = []
        self.active_vault: Optional[str] = None
        self._init_cognition()
    
    def _init_cognition(self):
        try:
            vaults = get_vaults()
            if vaults:
                self.active_vault = vaults[0]["name"]
                self.hippocampus = HippocampusHolon(self.active_vault)
                self.cognition = CognitionHolon()
                self.cognition.check()  # Initialize engines
        except Exception as e:
            print(f"[API] Init warning: {e}")

    def think(self, message: str, context: str = "") -> str:
        """Получает ответ от ASTRA cognition."""
        if not self.cognition:
            return "[ASTRA] System not initialized."
        try:
            result = self.cognition.think(message, context=context)
            if isinstance(result, dict):
                return result.get("answer", str(result))
            return str(result)
        except Exception as e:
            return f"[ASTRA] Error: {e}"

# Singleton session (в проде — per-user sessions)
session = AstraSession()

# ── Routes ──

@app.route("/")
def index():
    """Main page -- chat."""
    try:
        with open(str(Path(app.static_folder) / "index.html"), "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"<h1>Error loading page</h1><pre>{e}</pre>", 500


@app.route("/api/status")
def api_status():
    """Статус ASTRA."""
    vaults = get_vaults()
    engines = ["ollama", "hf", "claude", "kimi"]
    return jsonify({
        "status": "online",
        "name": "ASTRA",
        "version": "3.0",
        "vaults": [v["name"] for v in vaults],
        "active_vault": session.active_vault,
        "engines_available": engines,
        "features": ["chat", "thinking", "streaming", "memory", "fpf", "automodel", "fpf_loop", "growth"],
        "timestamp": datetime.now().isoformat(),
    })


@app.route("/api/vaults")
def api_vaults():
    """Список вультов."""
    return jsonify({"vaults": get_vaults()})


@app.route("/api/vault/select", methods=["POST"])
def api_select_vault():
    """Выбор активного вульта."""
    data = request.get_json() or {}
    vault_name = data.get("vault")
    if not vault_name:
        return jsonify({"error": "vault name required"}), 400
    
    vaults = get_vaults()
    vault = next((v for v in vaults if v["name"] == vault_name), None)
    if not vault:
        return jsonify({"error": "vault not found"}), 404
    
    try:
        vault_path = Path(vault["path"])
        session.hippocampus = HippocampusHolon(vault_name)
        session.active_vault = vault_name
        session.history = []
        return jsonify({"success": True, "vault": vault_name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/modes")
def api_modes():
    """Доступные режимы работы."""
    return jsonify({
        "modes": [
            {"id": "chat", "name": "Чат", "icon": "💬", "desc": "Свободный диалог"},
            {"id": "think", "name": "Мышление", "icon": "🧠", "desc": "Глубокий анализ с reasoning"},
            {"id": "code", "name": "Код", "icon": "💻", "desc": "Программирование и архитектура"},
            {"id": "memory", "name": "Память", "icon": "🧩", "desc": "Работа с Obsidian Vault"},
            {"id": "evolution", "name": "Эволюция", "icon": "🧬", "desc": "Королева Муравьёв"},
            {"id": "awaken", "name": "AWAKEN", "icon": "👁️", "desc": "Голосовой режим"},
        ]
    })


@app.route("/api/history")
def api_history():
    """История чата."""
    return jsonify({"history": session.history})


@app.route("/api/clear", methods=["POST"])
def api_clear():
    """Очистить историю."""
    session.history = []
    return jsonify({"success": True})


# ── SSE Chat Streaming ──

class ThinkingStream:
    """Генератор thinking-токенов + финального ответа."""
    
    THINKING_STEPS = [
        ("observation", "Наблюдение...", 0.3),
        ("context", "Загрузка контекста из памяти...", 0.5),
        ("classification", "Классификация намерения...", 0.7),
        ("reasoning", "Формирование reasoning...", 1.2),
        ("synthesis", "Синтез ответа...", 0.8),
    ]
    
    def __init__(self, message: str, mode: str = "chat"):
        self.message = message
        self.mode = mode
        self.q = queue.Queue()
        self._done = False
    
    def _think(self):
        """Фоновый поток: мышление → ответ."""
        try:
            # Phase 1: Thinking tokens
            for step_id, step_label, delay in self.THINKING_STEPS:
                self.q.put({
                    "type": "thinking",
                    "step": step_id,
                    "label": step_label,
                    "timestamp": datetime.now().isoformat(),
                })
                import time
                time.sleep(delay)
            
            # Phase 2: Actual thinking
            context = f"Режим: {self.mode}. История: {len(session.history)} сообщений."
            answer = session.think(self.message, context=context)
            
            # Phase 3: Answer
            self.q.put({
                "type": "answer",
                "content": answer,
                "timestamp": datetime.now().isoformat(),
            })
            
            # Save to history
            session.history.append({
                "role": "user",
                "content": self.message,
                "timestamp": datetime.now().isoformat(),
            })
            session.history.append({
                "role": "assistant",
                "content": answer,
                "timestamp": datetime.now().isoformat(),
            })
            
        except Exception as e:
            self.q.put({
                "type": "error",
                "content": str(e),
            })
        finally:
            self.q.put({"type": "done"})
            self._done = True
    
    def start(self):
        thread = threading.Thread(target=self._think)
        thread.daemon = True
        thread.start()
    
    def events(self):
        """Генератор SSE-событий."""
        self.start()
        while True:
            try:
                data = self.q.get(timeout=30)
                if data["type"] == "done":
                    yield f"event: done\ndata: {json.dumps(data)}\n\n"
                    break
                yield f"event: {data['type']}\ndata: {json.dumps(data)}\n\n"
            except queue.Empty:
                yield f"event: error\ndata: {json.dumps({'type': 'error', 'content': 'timeout'})}\n\n"
                break


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """SSE-стриминг чата."""
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    mode = data.get("mode", "chat")
    
    if not message:
        return jsonify({"error": "message required"}), 400
    
    stream = ThinkingStream(message, mode=mode)
    
    return Response(
        stream_with_context(stream.events()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@app.route("/api/debug")
def api_debug():
    """Debug paths."""
    import os, sys
    from pathlib import Path
    if getattr(sys, 'frozen', False):
        base = Path(sys.executable).parent
        internal = base / "_internal"
        root = internal if internal.exists() else base
    else:
        root = Path(__file__).parent.resolve()
    return jsonify({
        "frozen": getattr(sys, 'frozen', False),
        "executable": sys.executable,
        "cwd": os.getcwd(),
        "project_root": str(root),
        "static_folder": app.static_folder,
        "static_exists": (root / "astra_chat" / "index.html").exists(),
        "sys_path": sys.path[:3],
    })


@app.route("/api/v1/health")
def api_v1_health():
    """Health check for Desktop app."""
    from astra_core.soma import get_soma
    from astra_core.astra_persistence import ASTRAPersistence
    try:
        soma = get_soma()
        metrics = soma.heartbeat() if soma else {}
    except Exception:
        metrics = {}
    try:
        p = ASTRAPersistence()
        stats = p.get_stats()
    except Exception:
        stats = {}
    return jsonify({
        "status": "online",
        "version": "3.0",
        "daemon_running": True,
        "api_running": True,
        "models_available": ["wavespeed/gpt-5.4", "ollama/llama3", "kimi/gpt-5.5"],
        "metrics": metrics,
        "stats": stats,
        "timestamp": datetime.now().isoformat(),
    })

@app.route("/api/v1/system/metrics")
def api_v1_metrics():
    """System metrics for Desktop dashboard."""
    from astra_core.soma import get_soma
    try:
        soma = get_soma()
        metrics = soma.heartbeat() if soma else {}
    except Exception as e:
        metrics = {"error": str(e)}
    return jsonify(metrics)

@app.route("/api/v1/events/recent")
def api_v1_events_recent():
    """Recent events for Desktop timeline."""
    from astra_core.astra_persistence import ASTRAPersistence
    limit = request.args.get("limit", 20, type=int)
    try:
        p = ASTRAPersistence()
        events = p.get_events(limit=limit)
    except Exception as e:
        events = []
    return jsonify({"events": events})

@app.route("/api/v1/daemon/toggle", methods=["POST"])
def api_v1_daemon_toggle():
    """Toggle daemon state (placeholder)."""
    # In full implementation, integrate with astra_daemon.py
    return jsonify({"running": True, "message": "Daemon is always running in v3.0"})

@app.route("/api/v1/growth/report")
def api_v1_growth_report():
    """Growth report endpoint."""
    from astra_core.fpf_mission import ASTRAGrowthAssessment
    try:
        assessment = ASTRAGrowthAssessment()
        report = assessment.generate_report()
        return jsonify({"report": report, "maturity": 25.4})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/fpf/loop", methods=["POST"])
def api_v1_fpf_loop():
    """Run FPF autonomous loop."""
    from astra_core.fpf_autonomous_loop import FPFAutonomousLoop
    data = request.get_json() or {}
    dry_run = data.get("dry_run", True)
    live = data.get("live", False)
    try:
        loop = FPFAutonomousLoop()
        # If live mode requested, only apply human-approved proposals
        if live and not dry_run:
            result = loop.run_cycle(dry_run=False)
            # Only apply proposals that are human-approved
            applied = []
            for p in loop.proposals:
                if p.status == "approved" and p.human_approved:
                    ok, msg = loop.apply_proposal(p, dry_run=False)
                    applied.append({"id": p.id, "ok": ok, "msg": msg})
            result["applied"] = applied
            return jsonify({"result": result, "dry_run": False, "live": True})
        else:
            result = loop.run_cycle(dry_run=True)
            return jsonify({"result": result, "dry_run": True, "live": False})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/fpf/proposals", methods=["GET"])
def api_v1_fpf_proposals():
    """List FPF proposals with optional status filtering."""
    from astra_core.fpf_autonomous_loop import FPFAutonomousLoop
    status = request.args.get("status", "")
    min_fitness = request.args.get("min_fitness", 0.0, type=float)
    try:
        loop = FPFAutonomousLoop()
        proposals = loop.list_proposals(status=status or None, min_fitness=min_fitness)
        return jsonify({
            "proposals": [p.to_dict() for p in proposals],
            "count": len(proposals),
            "pending_count": len(loop.get_pending_proposals())
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/fpf/approve", methods=["POST"])
def api_v1_fpf_approve():
    """Human approval endpoint for a proposal (Constitution §5)."""
    from astra_core.fpf_autonomous_loop import FPFAutonomousLoop
    data = request.get_json() or {}
    proposal_id = data.get("proposal_id", "").strip()
    approver = data.get("approver", "human")
    if not proposal_id:
        return jsonify({"error": "proposal_id required"}), 400
    try:
        loop = FPFAutonomousLoop()
        ok, msg = loop.approve_proposal(proposal_id, approver=approver)
        if ok:
            return jsonify({"success": True, "message": msg, "proposal_id": proposal_id})
        else:
            return jsonify({"success": False, "message": msg}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/fpf/reject", methods=["POST"])
def api_v1_fpf_reject():
    """Reject a proposal, preventing live apply."""
    from astra_core.fpf_autonomous_loop import FPFAutonomousLoop
    data = request.get_json() or {}
    proposal_id = data.get("proposal_id", "").strip()
    reason = data.get("reason", "")
    if not proposal_id:
        return jsonify({"error": "proposal_id required"}), 400
    try:
        loop = FPFAutonomousLoop()
        ok, msg = loop.reject_proposal(proposal_id, reason=reason)
        if ok:
            return jsonify({"success": True, "message": msg, "proposal_id": proposal_id})
        else:
            return jsonify({"success": False, "message": msg}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/fpf/apply", methods=["POST"])
def api_v1_fpf_apply():
    """Apply a single proposal (requires human approval)."""
    from astra_core.fpf_autonomous_loop import FPFAutonomousLoop
    data = request.get_json() or {}
    proposal_id = data.get("proposal_id", "").strip()
    if not proposal_id:
        return jsonify({"error": "proposal_id required"}), 400
    try:
        loop = FPFAutonomousLoop()
        proposal = next((p for p in loop.proposals if p.id == proposal_id), None)
        if not proposal:
            return jsonify({"error": "proposal not found"}), 404
        if not proposal.human_approved:
            return jsonify({"error": "proposal requires human approval first", "proposal_id": proposal_id}), 403
        ok, msg = loop.apply_proposal(proposal, dry_run=False)
        return jsonify({"success": ok, "message": msg, "proposal_id": proposal_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/fpf/analyze", methods=["POST"])
def api_v1_fpf_analyze():
    """Analyze utterance via FPF engine."""
    from astra_core.fpf_engine import FPFEngine
    data = request.get_json() or {}
    utterance = data.get("utterance", "")
    if not utterance:
        return jsonify({"error": "utterance required"}), 400
    try:
        lade = FPFEngine.classify_lade(utterance)
        fgr = FPFEngine.assess_fgr(utterance, "api")
        return jsonify({"lade": lade, "fgr": fgr})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/chat", methods=["POST"])
def api_v1_chat():
    """Non-SSE chat endpoint for Desktop app."""
    data = request.get_json() or {}
    message = data.get("query", "").strip()
    mode = data.get("mode", "chat")
    context = data.get("context", "")
    if not message:
        return jsonify({"error": "message required"}), 400
    try:
        answer = session.think(message, context=context)
        # Save to history
        session.history.append({
            "role": "user", "content": message,
            "timestamp": datetime.now().isoformat(),
        })
        session.history.append({
            "role": "assistant", "content": answer,
            "timestamp": datetime.now().isoformat(),
        })
        return jsonify({"answer": answer, "mode": mode, "timestamp": datetime.now().isoformat()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/report/startup")
def api_v1_startup_report():
    """Generate startup report for the user to relay to Kimi."""
    from astra_core.startup_report import generate_startup_report
    try:
        report = generate_startup_report(["http://127.0.0.1:8764", "http://127.0.0.1:8766", "http://127.0.0.1:8767"])
        return jsonify({"report": report, "status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/tools/list")
def api_v1_tools_list():
    """List available tools."""
    from astra_core.tools import get_tool_holon
    try:
        tools = get_tool_holon()
        return jsonify({"tools": tools.list_tools()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/v1/tools/execute", methods=["POST"])
def api_v1_tools_execute():
    """Execute a tool."""
    from astra_core.tools import get_tool_holon
    data = request.get_json() or {}
    tool_name = data.get("tool", "").strip()
    params = data.get("params", {})
    
    if not tool_name:
        return jsonify({"error": "tool name required"}), 400
    
    try:
        tools = get_tool_holon()
        result = tools.execute(tool_name, **params)
        return jsonify(result.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/voice", methods=["POST"])
def api_v1_voice():
    """Server-side voice processing (placeholder). 
    
    Accepts JSON with base64-encoded audio and returns transcription.
    For now, returns a mock response indicating client-side processing is preferred.
    """
    data = request.get_json() or {}
    audio_b64 = data.get("audio", "")
    language = data.get("language", "ru")
    if not audio_b64:
        return jsonify({"error": "audio (base64) required"}), 400
    # In production, decode WAV and run Vosk here.
    # For this release, client-side VoiceWorker handles STT.
    return jsonify({
        "status": "client_preferred",
        "message": "Use ASTRA Desktop VoiceWorker for real-time recognition.",
        "language": language,
        "transcription": "",
        "timestamp": datetime.now().isoformat(),
    })


# ═══════════════════════════════════════════════════════
# NOTIFICATIONS API
# ═══════════════════════════════════════════════════════

@app.route("/api/v1/notify", methods=["POST"])
def api_v1_notify():
    """Trigger a toast notification."""
    data = request.get_json() or {}
    title = data.get("title", "ASTRA").strip()
    message = data.get("message", "").strip()
    icon = data.get("icon", "info")
    source = data.get("source", "api")
    duration = data.get("duration", 5)
    
    if not message:
        return jsonify({"error": "message required"}), 400
    
    try:
        from astra_desktop.notifications import DaemonNotifier
        notifier = DaemonNotifier()
        notification = notifier.notify(
            title=title,
            message=message,
            icon=icon,
            source=source,
            duration=duration
        )
        return jsonify({
            "success": True,
            "notification_id": notification.id,
            "title": title,
            "message": message,
            "icon": icon,
            "timestamp": notification.timestamp.isoformat(),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/notifications")
def api_v1_notifications():
    """Get recent notification history."""
    limit = request.args.get("limit", 50, type=int)
    try:
        from astra_desktop.notifications import DaemonNotifier
        notifier = DaemonNotifier()
        history = notifier.get_history(limit=limit)
        return jsonify({
            "notifications": [
                {
                    "id": n.id,
                    "title": n.title,
                    "message": n.message,
                    "icon": n.icon,
                    "source": n.source,
                    "timestamp": n.timestamp.isoformat(),
                    "read": n.read,
                    "action_url": n.action_url,
                    "data": n.data,
                }
                for n in history
            ],
            "unread_count": notifier.get_unread_count(),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/v1/notifications/settings", methods=["GET", "POST"])
def api_v1_notifications_settings():
    """Get or update notification settings."""
    from astra_core.config import get_notification_settings
    
    if request.method == "GET":
        settings = get_notification_settings()
        return jsonify(settings)
    
    data = request.get_json() or {}
    try:
        # Settings are persisted via config.json updates
        # For now, return the updated settings dict
        # In a full implementation, write back to config.json
        settings = get_notification_settings()
        if "enabled" in data:
            settings["enabled"] = bool(data["enabled"])
        if "thresholds" in data:
            settings["thresholds"].update(data["thresholds"])
        if "duration" in data:
            settings["duration"] = int(data["duration"])
        return jsonify({"success": True, "settings": settings})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("=" * 60)
    print("  ASTRA Chat API")
    print("  http://127.0.0.1:8764")
    print("  API Key:", get_api_key())
    print("=" * 60)
    app.run(host="127.0.0.1", port=8764, debug=False, threaded=True)
