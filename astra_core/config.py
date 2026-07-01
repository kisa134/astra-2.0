# -*- coding: utf-8 -*-
"""
ASTRA Config — централизованная конфигурация всех холонов.
Читает .env (приоритет) → config.json → дефолты ASTRA_CONFIG.
"""
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Any, Dict

# ── Determine PROJECT_ROOT (works from source OR frozen .exe) ──
if getattr(sys, 'frozen', False):
    # Running from PyInstaller .exe
    PROJECT_ROOT = Path(sys.executable).parent.resolve()
else:
    # Running from source
    PROJECT_ROOT = Path(__file__).parent.parent.resolve()

STATE_FILE = PROJECT_ROOT / "agent_state.json"
VAULT_PATH = Path(r"C:\Users\HYPERPC\Documents\mz-0")

# Читаем .env если есть (безопаснее для секретов)
try:
    from dotenv import load_dotenv
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

ASTRA_CONFIG = {
    "ollama_url": "http://localhost:11434",
    "model_main": "qwen2.5:32b",
    "model_vision": "llava",
    "whisper_model_size": "small",
    "tts_model": "edge-tts",
    "voice_ref": str(PROJECT_ROOT / "voice_ref.wav"),
    "sample_rate": 16000,
    "language": "ru",
    "record_seconds": 5,
    "chunk_size": 1024,
    "vault_path": str(VAULT_PATH),
    "temp_audio_dir": str(PROJECT_ROOT / "temp_audio"),
    "output_audio_dir": str(PROJECT_ROOT / "output_audio"),
    "chroma_db_dir": str(PROJECT_ROOT / "chroma_db"),
    "constitution_path": str(PROJECT_ROOT / "astra_core" / "constitution.txt"),
    "kimi_cli_path": "kimi",
    "claude_api_key": "",
    "claude_model": "claude-sonnet-4-20250514",
    "hf_api_key": "",
    "hf_model": "Qwen/Qwen2.5-7B-Instruct",
    "hf_use_local": False,
    "hf_local_model_path": "",
    "use_kimi": True,
    "use_ollama": True,
    "use_claude": False,
    "use_hf": False,
    "cognition_priority": ["ollama", "hf", "claude", "kimi"],
    "max_context_tokens": 8192,
    # ── Notifications ──
    "notifications_enabled": True,
    "notifications_threshold_cpu": 90.0,
    "notifications_threshold_ram": 90.0,
    "notifications_threshold_disk": 90.0,
    "notifications_duration_sec": 5,
}


def _load_secrets_from_env(cfg: Dict[str, Any]) -> None:
    """Переписывает секреты из переменных окружения (приоритет над config.json)."""
    env_map = {
        "HUGGINGFACE_TOKEN": "hf_api_key",
        "CLAUDE_API_KEY": "claude_api_key",
        "WHISPER_API_KEY": "speech_whisper_api_key",
        "OPENAI_API_KEY": "speech_whisper_api_key",  # fallback
    }
    for env_var, cfg_key in env_map.items():
        val = os.environ.get(env_var, "").strip()
        if val:
            cfg[cfg_key] = val


def load_config() -> Dict[str, Any]:
    """Загружает: .env → config.json → ASTRA_CONFIG."""
    external = PROJECT_ROOT / "config.json"
    cfg = ASTRA_CONFIG.copy()

    # 1. Сначала secrets из .env (если есть)
    _load_secrets_from_env(cfg)

    # 2. Затем config.json (может перезаписать .env для не-секретов)
    if external.exists():
        try:
            with open(external, "r", encoding="utf-8") as f:
                ext = json.load(f)
            for key in ["vault", "kimi", "speech", "tts", "obsidian", "ollama", "claude", "app", "hf", "vaults"]:
                if key in ext:
                    if key == "vaults":
                        cfg["vaults"] = ext["vaults"]
                    else:
                        for k, v in ext[key].items():
                            cfg_key = f"{key}_{k}"
                            cfg[cfg_key] = v
            # Маппинги совместимости
            if "kimi" in ext:
                if "cli_path" in ext["kimi"]:
                    cfg["kimi_cli_path"] = ext["kimi"]["cli_path"]
                if "use_cli" in ext["kimi"]:
                    cfg["use_kimi"] = ext["kimi"]["use_cli"]
                if "timeout" in ext["kimi"]:
                    cfg["kimi_timeout"] = ext["kimi"]["timeout"]
            if "ollama" in ext:
                if "url" in ext["ollama"]:
                    cfg["ollama_url"] = ext["ollama"]["url"]
                if "model" in ext["ollama"]:
                    cfg["model_main"] = ext["ollama"]["model"]
                if "enabled" in ext["ollama"]:
                    cfg["use_ollama"] = ext["ollama"]["enabled"]
            if "claude" in ext:
                if "api_key" in ext["claude"]:
                    cfg["claude_api_key"] = ext["claude"]["api_key"]
                if "model" in ext["claude"]:
                    cfg["claude_model"] = ext["claude"]["model"]
                if "enabled" in ext["claude"]:
                    cfg["use_claude"] = ext["claude"]["enabled"]
            if "hf" in ext:
                if "api_key" in ext["hf"]:
                    cfg["hf_api_key"] = ext["hf"]["api_key"]
                if "model" in ext["hf"]:
                    cfg["hf_model"] = ext["hf"]["model"]
                if "enabled" in ext["hf"]:
                    cfg["use_hf"] = ext["hf"]["enabled"]
                if "use_local" in ext["hf"]:
                    cfg["hf_use_local"] = ext["hf"]["use_local"]
                if "local_model_path" in ext["hf"]:
                    cfg["hf_local_model_path"] = ext["hf"]["local_model_path"]
            if "wavespeed" in ext:
                if "api_key" in ext["wavespeed"]:
                    cfg["wavespeed_api_key"] = ext["wavespeed"]["api_key"]
                if "model" in ext["wavespeed"]:
                    cfg["wavespeed_model"] = ext["wavespeed"]["model"]
                if "url" in ext["wavespeed"]:
                    cfg["wavespeed_url"] = ext["wavespeed"]["url"]
                if "enabled" in ext["wavespeed"]:
                    cfg["use_wavespeed"] = ext["wavespeed"]["enabled"]
            if "app" in ext and "cognition_priority" in ext["app"]:
                cfg["cognition_priority"] = ext["app"]["cognition_priority"]
            # ── API key from config.json ──
            if "api" in ext:
                if "internal_key" in ext["api"]:
                    cfg["api_internal_key"] = ext["api"]["internal_key"]
                if "url" in ext["api"]:
                    cfg["api_url"] = ext["api"]["url"]
                if "port" in ext["api"]:
                    cfg["api_port"] = ext["api"]["port"]
            # ── Notifications from config.json ──
            if "notifications" in ext:
                n = ext["notifications"]
                if "enabled" in n:
                    cfg["notifications_enabled"] = n["enabled"]
                if "thresholds" in n:
                    t = n["thresholds"]
                    if "cpu" in t:
                        cfg["notifications_threshold_cpu"] = t["cpu"]
                    if "ram" in t:
                        cfg["notifications_threshold_ram"] = t["ram"]
                    if "disk" in t:
                        cfg["notifications_threshold_disk"] = t["disk"]
                if "duration_sec" in n:
                    cfg["notifications_duration_sec"] = n["duration_sec"]
        except Exception as e:
            print(f"[Config] load_config error: {e}")
            pass

    # 3. .env секреты имеют ПРИОРИТЕТ над config.json
    _load_secrets_from_env(cfg)

    return cfg


def get(key: str, default: Any = None) -> Any:
    cfg = load_config()
    return cfg.get(key, default)


def get_vaults() -> list:
    """Возвращает список vault'ов из config.json."""
    cfg = load_config()
    vaults = cfg.get("vaults", [])
    if not vaults:
        # Fallback — один vault по старому пути
        default = {
            "name": "HYPERPC Main",
            "path": str(VAULT_PATH),
            "role": "personal",
            "inbox_path": "00 - Inbox",
            "areas_path": "02 - Areas",
            "resources_path": "03 - Resources",
            "archive_path": "04 - Archieve",
            "voice_dialogues_path": "02 - Areas/Дневники/Голосовые диалоги",
            "templates_path": "99 - Templates",
        }
        return [default]
    return vaults


def get_active_vault(vault_name: str = "") -> dict:
    """Возвращает конкретный vault по имени или первый доступный."""
    vaults = get_vaults()
    if vault_name:
        for v in vaults:
            if v.get("name", "").lower() == vault_name.lower():
                return v
    return vaults[0] if vaults else {}


def get_vault_path(vault_name: str = "") -> Path:
    """Возвращает Path к активному vault."""
    v = get_active_vault(vault_name)
    return Path(v.get("path", str(VAULT_PATH)))


def get_notification_settings() -> dict:
    """Return notification settings as a unified dict."""
    cfg = load_config()
    return {
        "enabled": cfg.get("notifications_enabled", True),
        "duration": cfg.get("notifications_duration_sec", 5),
        "thresholds": {
            "cpu": cfg.get("notifications_threshold_cpu", 90.0),
            "ram": cfg.get("notifications_threshold_ram", 90.0),
            "disk": cfg.get("notifications_threshold_disk", 90.0),
        },
    }


def get_api_key() -> str:
    """Return the internal API key for ASTRA API authentication.
    
    If no key exists in config.json, generates a new UUID key,
    saves it, and returns it. The key is stored under api.internal_key.
    """
    external = PROJECT_ROOT / "config.json"
    cfg = load_config()
    key = cfg.get("api_internal_key", "")
    print(f"[Config] get_api_key: loaded key={key[:8] if key else 'NONE'}...")
    if not key:
        key = str(uuid.uuid4())
        print(f"[Config] get_api_key: generating NEW key={key[:8]}...")
        cfg["api_internal_key"] = key
        # Write back to config.json preserving existing structure
        existing = {}
        if external.exists():
            try:
                with open(external, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            except Exception as e:
                print(f"[Config] get_api_key: read error: {e}")
                pass
        if "api" not in existing:
            existing["api"] = {}
        existing["api"]["internal_key"] = key
        try:
            with open(external, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2, ensure_ascii=False)
            print(f"[Config] get_api_key: saved to config.json")
        except Exception as e:
            print(f"[Config] Warning: could not save API key: {e}")
    return key


config = ASTRA_CONFIG
