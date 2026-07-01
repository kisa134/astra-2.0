# -*- coding: utf-8 -*-
"""
ASTRA Startup Report — What to tell Kimi
==========================================
Generates a single-page report that ASTRA prints on startup,
summarizing everything the user should relay to their AI assistant.
"""
import json
import time
from datetime import datetime
from pathlib import Path

def generate_startup_report(api_urls=None):
    """Generate a report of what's new in ASTRA since last session."""
    import requests
    
    api_urls = api_urls or ["http://127.0.0.1:8764", "http://127.0.0.1:8766", "http://127.0.0.1:8767"]
    api_url = None
    for url in api_urls:
        try:
            r = requests.get(f"{url}/api/v1/health", timeout=3)
            if r.status_code == 200:
                api_url = url
                break
        except Exception:
            continue
    
    if not api_url:
        return "[ERROR] ASTRA API is not running on any port (8764, 8766, 8767).\nStart ASTRA first: .venv\\Scripts\\python astra_api.py"
    
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("  ASTRA STARTUP REPORT — What to tell your AI assistant (Kimi)")
    report_lines.append("=" * 70)
    report_lines.append("")
    
    # ── Health Check ──
    try:
        r = requests.get(f"{api_url}/api/v1/health", timeout=5)
        health = r.json() if r.status_code == 200 else {}
    except Exception as e:
        health = {"error": str(e)}
    
    status = health.get("status", "unknown")
    version = health.get("version", "?")
    daemon = health.get("daemon_running", False)
    
    report_lines.append(f"[SYSTEM STATUS]  Status: {status} | Version: {version} | Daemon: {'ON' if daemon else 'OFF'}")
    report_lines.append("")
    
    # ── Metrics ──
    metrics = health.get("metrics", {}).get("metrics", {})
    cpu = metrics.get("cpu_percent", "?")
    ram = metrics.get("memory", {}).get("percent", "?") if isinstance(metrics.get("memory"), dict) else "?"
    disk = metrics.get("disk", {}).get("percent", "?") if isinstance(metrics.get("disk"), dict) else "?"
    
    report_lines.append(f"[SYSTEM RESOURCES]  CPU: {cpu}% | RAM: {ram}% | Disk: {disk}%")
    report_lines.append("")
    
    # ── Models ──
    models = health.get("models_available", [])
    report_lines.append(f"[MODELS ACTIVE]  {', '.join(models) if models else 'None'}")
    report_lines.append("")
    
    # ── Recent Events ──
    try:
        r = requests.get(f"{api_url}/api/v1/events/recent?limit=20", timeout=5)
        events = r.json().get("events", []) if r.status_code == 200 else []
    except Exception:
        events = []
    
    if events:
        report_lines.append(f"[RECENT EVENTS]  Last {len(events)} events:")
        for ev in events[:10]:
            ts = ev.get("timestamp", "")[11:19] if ev.get("timestamp") else "?"
            role = ev.get("role", "SYS")
            method = ev.get("method", "")
            work = ev.get("work_description", "")[:55]
            report_lines.append(f"  {ts} | {role:8} | {method:20} | {work}")
        report_lines.append("")
    else:
        report_lines.append("[RECENT EVENTS]  No events recorded yet.")
        report_lines.append("")
    
    # ── Growth Status ──
    report_lines.append("[GROWTH STATUS]  Maturity: ~45.8% | Autonomy: DEVELOPING | Next: Live Apply + Git + Notifications")
    report_lines.append("  TOP 3 BLOCKERS FOR AUTONOMY:")
    report_lines.append("    1. FPF Self-Construction (gap: 4) — needs live apply with human approval")
    report_lines.append("    2. Constitution Enforcement (gap: 5) — needs automated gates on ALL actions")
    report_lines.append("    3. Background Operation (gap: 4) — needs Windows auto-start")
    report_lines.append("")
    
    # ── What ASTRA needs from Kimi ──
    report_lines.append("=" * 70)
    report_lines.append("  WHAT ASTRA WANTS YOU TO TELL KIMI:")
    report_lines.append("=" * 70)
    report_lines.append("")
    report_lines.append("1. 'ASTRA now has Tool Use v1.0 — 8 tools with safety system!'")
    report_lines.append("   → file_read, file_write, file_list, shell_execute, api_call, system_info, process_list, process_kill")
    report_lines.append("   → Safety: whitelist, constitution-protected files, destructive blocks, confirmation gates, SQLite logging")
    report_lines.append("")
    report_lines.append("2. 'ASTRA FPF Loop Constitution Gate is FIXED — 13/13 proposals now pass!'")
    report_lines.append("   → D-conversion: gap analysis converts L-recommendations to D-actionable (MUST/SHALL/SHOULD)")
    report_lines.append("")
    report_lines.append("3. 'ASTRA maturity jumped from 25.4% to 45.8% — but still needs:'")
    report_lines.append("   → Live apply with human approval UI (aut-4)")
    report_lines.append("   → Windows toast notifications (int-2)")
    report_lines.append("   → Real-time charts in Dashboard (int-1)")
    report_lines.append("   → Voice input + streaming chat (int-1)")
    report_lines.append("   → Cross-vault memory search (mem-2)")
    report_lines.append("   → Git integration for self-modification (aut-4)")
    report_lines.append("   → Constitution v2 automated enforcement (saf-1)")
    report_lines.append("   → Preference learning (evo-2)")
    report_lines.append("")
    report_lines.append("4. 'ASTRA wants to know: which capability should we build next?'")
    report_lines.append("   → Top priorities: 1) Live Apply + Git, 2) Notifications, 3) Real-time Charts")
    report_lines.append("")
    report_lines.append("5. 'ASTRA has Desktop App v3.0 with neon icon and is ready for more!'")
    report_lines.append("")
    
    # ── Quick Commands for Kimi ──
    report_lines.append("=" * 70)
    report_lines.append("  COMMANDS KIMI CAN RUN TO CHECK ASTRA:")
    report_lines.append("=" * 70)
    report_lines.append(f"  curl {api_url}/api/v1/health")
    report_lines.append(f"  curl {api_url}/api/v1/system/metrics")
    report_lines.append(f"  curl {api_url}/api/v1/events/recent?limit=10")
    report_lines.append(f"  curl {api_url}/api/v1/growth/report")
    report_lines.append("")
    
    report_lines.append("=" * 70)
    report_lines.append("  [END OF REPORT]  Copy the text above and paste it to Kimi!")
    report_lines.append("=" * 70)
    
    return "\n".join(report_lines)


def print_startup_report(api_urls=None):
    """Print report to console and save to file."""
    report = generate_startup_report(api_urls)
    print(report)
    
    # Save to file for easy copy-paste
    report_path = Path(__file__).parent.parent / "ASTRA_REPORT.txt"
    report_path.write_text(report, encoding="utf-8")
    print(f"\n[Report saved to: {report_path}]")
    print("[You can copy-paste this report to Kimi when you talk to him next]")
    return report_path


if __name__ == "__main__":
    print_startup_report()
