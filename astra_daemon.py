# -*- coding: utf-8 -*-
"""ASTRA Background Daemon — APScheduler-based background jobs."""
import os
import sys
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

# ── Paths ──
PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from astra_core.config import get, PROJECT_ROOT as ASTRA_ROOT
from astra_core.astra_persistence import ASTRAPersistence
from astra_core.soma import get_soma

# ── Global Scheduler ──
_scheduler: BackgroundScheduler = None


def get_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
    return _scheduler


# ── Job Definitions ──


def job_metrics():
    """Collect system metrics every 1 minute."""
    try:
        soma = get_soma()
        if soma:
            metrics = soma.heartbeat()
            p = ASTRAPersistence()
            p.log_event("METRICS", "daemon", "System metrics collected", work_description=json.dumps(metrics, ensure_ascii=False)[:500])
    except Exception as e:
        print(f"[DAEMON][metrics] {e}")


def job_health():
    """Health check every 5 minutes."""
    try:
        p = ASTRAPersistence()
        p.log_event("HEALTH", "daemon", "Health check", work_description="Daemon alive")
    except Exception as e:
        print(f"[DAEMON][health] {e}")


def job_auto_discover():
    """Auto-discover models every 15 minutes."""
    try:
        from astra_core.auto_model_manager import AutoModelManager
        mgr = AutoModelManager()
        mgr.auto_discover()
        p = ASTRAPersistence()
        p.log_event("AUTO_DISCOVER", "daemon", "Auto model discovery", work_description="Models checked")
    except Exception as e:
        print(f"[DAEMON][auto_discover] {e}")


def job_benchmark():
    """Benchmark models every 1 hour."""
    try:
        from astra_core.auto_model_manager import AutoModelManager
        mgr = AutoModelManager()
        mgr.benchmark_all()
        p = ASTRAPersistence()
        p.log_event("BENCHMARK", "daemon", "Model benchmark", work_description="Benchmark completed")
    except Exception as e:
        print(f"[DAEMON][benchmark] {e}")


def job_self_reflection():
    """Self-reflection every 1 hour."""
    try:
        p = ASTRAPersistence()
        p.log_event("REFLECTION", "daemon", "Self-reflection cycle", work_description="System self-check")
    except Exception as e:
        print(f"[DAEMON][reflection] {e}")


def job_fpf_introspection():
    """FPF introspection every 4 hours."""
    try:
        from astra_core.fpf_autonomous_loop import FPFAutonomousLoop
        loop = FPFAutonomousLoop()
        result = loop.run_cycle(dry_run=True)
        p = ASTRAPersistence()
        p.log_event("FPF_INTROSPECTION", "daemon", "FPF cycle", work_description=json.dumps(result, ensure_ascii=False)[:500])
    except Exception as e:
        print(f"[DAEMON][fpf] {e}")


def job_growth_report():
    """Growth report every 24 hours."""
    try:
        from astra_core.fpf_mission import ASTRAGrowthAssessment
        assessment = ASTRAGrowthAssessment()
        report = assessment.generate_report()
        p = ASTRAPersistence()
        p.log_event("GROWTH", "daemon", "Growth report", work_description=report[:500])
    except Exception as e:
        print(f"[DAEMON][growth] {e}")


# ── Scheduler Setup ──

JOBS = [
    (job_metrics, 1, "minutes", "metrics"),
    (job_health, 5, "minutes", "health"),
    (job_auto_discover, 15, "minutes", "auto_discover"),
    (job_benchmark, 1, "hours", "benchmark"),
    (job_self_reflection, 1, "hours", "self_reflection"),
    (job_fpf_introspection, 4, "hours", "fpf_introspection"),
    (job_growth_report, 24, "hours", "growth_report"),
]


def start_daemon():
    """Start all background jobs."""
    sched = get_scheduler()
    for func, interval, unit, name in JOBS:
        kwargs = {unit: interval}
        sched.add_job(func, IntervalTrigger(**kwargs), id=name, replace_existing=True)
    sched.start()
    print(f"[DAEMON] Started {len(JOBS)} jobs")
    return sched


def stop_daemon():
    """Stop all background jobs."""
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        print("[DAEMON] Stopped")


def is_running() -> bool:
    return _scheduler is not None and _scheduler.running


# ── CLI ──
if __name__ == "__main__":
    print("=" * 60)
    print("  ASTRA Daemon")
    print("=" * 60)
    start_daemon()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_daemon()
