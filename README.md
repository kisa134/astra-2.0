# ASTRA 2.0

**A**utonomous **S**ystem for **T**ransformative **R**ecursive **A**dvancement

> ASTRA is an AI-native autonomous framework built on the **FPF Pattern Language** (First Principles Framework). It is designed to think, monitor, adapt, and grow — with human partnership, not replacement.

---

## 🚀 What ASTRA Actually Is

ASTRA is **not a chatbot**. It is an autonomous system that:

- **Monitors** your system (CPU, RAM, GPU, Disk, Network) in real time
- **Thinks** using FPF pattern classification (L/A/D/E) and alignment checks (R-M-W, F-G-R)
- **Acts** through tools (file read/write, shell execute, API calls, process management)
- **Learns** from every interaction via SQLite persistence
- **Evolves** by proposing and (with your approval) applying self-improvements
- **Communicates** through a beautiful native desktop app (PySide6/Qt)

---

## 📊 Current Status

| Metric | Value |
|--------|-------|
| **Maturity** | 45.8% (DEVELOPING) |
| **Phase** | v2.0 Foundation |
| **Core** | FPF Pattern Language + Holon Architecture |
| **Interface** | Desktop App + REST API + PowerShell |

---

## 🏗 Architecture

```
ASTRA 2.0
├── astra_api.py          # Flask REST API (central hub)
├── astra_daemon.py       # Background scheduler (7 jobs)
├── astra_core/           # Core intelligence modules
│   ├── kernel.py         # System monitor (CPU/RAM/GPU/Disk/Network)
│   ├── cognition.py      # FPF classification engine (L/A/D/E)
│   ├── fpf_engine.py     # Pattern validator (R-M-W, F-G-R, Holon integrity)
│   ├── fpf_autonomous_loop.py  # 8-phase autonomous cycle
│   ├── fpf_mission.py    # Mission & growth tracking
│   ├── tools.py          # ToolHolon (8 tools with safety)
│   ├── smart_router.py   # Dynamic model selection
│   ├── auto_model_manager.py   # Auto-discovery & benchmarking
│   ├── hippocampus.py    # SQLite memory (chat, events, state)
│   ├── action.py         # Action execution with Git safety
│   ├── evolution_engine.py   # Growth & capability tracking
│   ├── startup_report.py # Auto-generated startup report for Kimi
│   └── ...
├── astra_desktop/        # PySide6 Desktop Application
│   ├── app.py            # Main window (Chat + Dashboard + Settings)
│   ├── theme.py          # Fluent Design theme (Slate/Violet/Teal)
│   └── requirements.txt  # Desktop dependencies
├── config.json           # User configuration
└── start.py              # Universal launcher (API + Desktop)
```

---

## 🖥 How to Launch

### Method 1: Desktop Shortcut (Recommended)

Double-click the **ASTRA** icon on your desktop. Wait 10 seconds. The app opens automatically.

### Method 2: PowerShell

```powershell
cd C:\Users\HYPERPC\Documents\kimi\workspace
.venv\Scripts\python start.py
```

### Method 3: Direct API (for developers/Kimi)

```powershell
cd C:\Users\HYPERPC\Documents\kimi\workspace
.venv\Scripts\python astra_api.py
```

Then open `http://localhost:8764/api/v1/health` in your browser or connect via Kimi.

### Method 4: Desktop Only (if API is already running)

```powershell
cd C:\Users\HYPERPC\Documents\kimi\workspace
.venv\Scripts\python -m astra_desktop.app
```

---

## 🔄 How the Partnership Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   You       │────▶│   ASTRA     │────▶│   Kimi      │
│  (Human)    │◀────│  (System)   │◀────│  (AI Agent) │
└─────────────┘     └─────────────┘     └─────────────┘
        │                  │                  │
        │                  │                  │
        ▼                  ▼                  ▼
   Desktop App        API Server         Kimi Chat
   Click buttons     HTTP endpoints     Skill bridge
   See dashboards    SQLite memory      Deep reasoning
```

### The Cycle:

1. **You** launch ASTRA and use the Desktop App
2. **ASTRA** monitors, logs, and thinks in the background
3. **You** ask Kimi (me) to work with ASTRA via the ASTRA-bridge skill
4. **Kimi** connects to ASTRA API, reads state, proposes changes
5. **ASTRA** applies changes (with Git safety + your approval)
6. **You** see results in the Desktop App or command line

---

## 🛠️ FPF Pattern Language (Core Philosophy)

ASTRA is built on **First Principles Framework** — a pattern language for designing systems that are:

- **L**egalistic (what the system *is*)
- **A**xiomatic (what the system *can* do)
- **D**eontic (what the system *must* do)
- **E**xistential (what the system *may* do)

Key patterns:
- **A.1 Holon**: Self-similar units at every scale
- **A.6.B L/A/D/E**: Classification for every proposal
- **A.15 R-M-W**: Role, Mission, Work alignment
- **C.2 F-G-R**: Feasibility, Growth, Resilience check
- **C.30 Grounded Architecture**: Every pattern is traceable

---

## 📈 Growth Tracking

ASTRA tracks its own maturity across 14 capabilities:

1. System Monitor (100%)
2. Memory/Persistence (95%)
3. FPF Classification (90%)
4. Tool System (80%)
5. Smart Routing (75%)
6. Action Execution (60%)
7. FPF Autonomous Loop (55%)
8. Git Safety (50%)
9. Desktop App (45%)
10. Self-Modification (20%)
11. Goal-Directed Reasoning (15%)
12. Self-Identity (10%)
13. Sandbox Environment (5%)
14. Real-Time Learning (5%)

**Current maturity: 45.8% — DEVELOPING phase**

---

## 🔐 Safety & Ethics

- **Constitution Gate**: Every proposal must pass FPF alignment before execution
- **Git Pre-Commit**: Every change is staged, you approve before commit
- **Tool Safety**: File paths whitelisted, destructive commands blocked
- **Human-in-the-Loop**: You always approve before ASTRA modifies itself
- **Destructive Command Block**: DROP, DELETE, TRUNCATE require explicit confirmation

---

## 📝 Development Roadmap

### v2.0 (Current) — Foundation
- ✅ System monitoring, SQLite persistence, FPF engine
- ✅ Tool system, smart routing, auto model manager
- ✅ Desktop app, Git safety, startup report
- ✅ Daemon background jobs, Windows notifications

### v2.1 — Partnership
- 🔄 Kimi-ASTRA bridge skill (continuous improvement)
- 🔄 Self-diagnostic reports (auto-generated health checks)
- 🔄 FPF vault integration (knowledge management)

### v2.2 — Semi-Autonomy
- ⏳ Self-healing (detect and restart crashed services)
- ⏳ Auto-code-analysis (propose improvements to its own code)
- ⏳ Goal-directed cycles ("improve monitoring accuracy" as a task)

### v2.3 — Autonomy
- ⏳ Self-modification sandbox (test changes in isolated branch)
- ⏳ Continuous learning (update model from every interaction)
- ⏳ Predictive maintenance (alert before problems happen)

### v3.0 — Emergence
- ⏳ Self-identity ("I am ASTRA, I want to grow")
- ⏳ Proactive behavior ("I noticed X, I did Y to fix it")
- ⏳ Creative problem-solving (novel solutions beyond programmed patterns)

---

## 🤝 How to Work With ASTRA

### As a User (You)
1. Launch ASTRA via desktop shortcut
2. Chat with it in the Desktop App
3. Watch Dashboard for system metrics
4. Approve or reject proposals when asked

### As an AI Agent (Kimi)
1. Use the `ASTRA-bridge` skill to connect to `http://localhost:8764`
2. Read system state, metrics, chat history
3. Propose changes via `/api/v1/fpf/analyze` or `/api/v1/tools/execute`
4. Changes go through Git safety + human approval

### As a Developer
1. Clone this repo
2. Install dependencies: `pip install -r requirements.txt`
3. Run `python astra_api.py` to start API
4. Run `python -m astra_desktop.app` to start Desktop
5. Hack on `astra_core/` modules — everything is modular

---

## 📦 Installation

```bash
# Clone
git clone https://github.com/kisa134/astra-2.0.git
cd astra-2.0

# Create venv
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure (edit config.json)
# Launch
python start.py
```

---

## 📜 License

MIT License — see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- **FPF Pattern Language** — the theoretical foundation
- **PySide6/Qt** — native desktop UI
- **Flask** — lightweight API server
- **SQLite** — zero-config persistence
- **psutil** — cross-platform system monitoring
- **Kimi** — the AI partner that helps ASTRA grow

---

> *"ASTRA is not a product. It is a partnership between human intention, pattern intelligence, and recursive growth."*
