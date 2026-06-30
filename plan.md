# ASTRA 2.1 Roadmap — System Development Plan

> **Vision**: ASTRA as your daily AI assistant — knows everything about your projects, remembers everything, orchestrates all modern AI tech, and grows autonomously via FPF.

---

## Current Status (v2.0 — Foundation)

| Component | Status | Maturity |
|-----------|--------|----------|
| SQLite Persistence (chat, events, metrics) | ✅ Working | 95% |
| System Monitor (CPU/RAM/GPU/Disk) | ✅ Working | 100% |
| FPF Engine (L/A/D/E, R-M-W, F-G-R) | ✅ Working | 90% |
| Tool System (8 tools with safety) | ✅ Working | 80% |
| Smart Router (auto model selection) | ✅ Working | 75% |
| AutoModel Manager (discovery, benchmark) | ✅ Working | 70% |
| Desktop App (PySide6, Fluent Design) | ✅ Working | 60% |
| GitHub Repository | ✅ Created | 100% |
| Vector Memory (ChromaDB + SQLite FTS) | ✅ Created | 50% |
| OpenRouter API Integration | 🔄 Started | 30% |
| LangGraph (FPF as state graph) | ⏳ Planned | 0% |
| Self-Modification Loop | ⏳ Planned | 0% |
| Daily Assistant Mode | ⏳ Planned | 0% |

**Overall Maturity: 45.8% → Target 70% for v2.1**

---

## Phase 1 — Memory & Knowledge (Week 1-2)

### 1.1 Mem0-Style Vector Memory ✅
- **Done**: `memory_vector.py` — ChromaDB + SQLite FTS fallback
- **Interface**: `add()`, `search()`, `get()`, `delete()`
- **Features**: Semantic search, user isolation, source tracking

### 1.2 Project Knowledge Graph
- **Goal**: Connect projects (Bomberfun, Trading, Cogito) via relationships
- **Tool**: NetworkX or Neo4j for graph memory
- **Use case**: "What did I do for Bomberfun last week?" → traverses graph

### 1.3 Daily Log Integration
- **Goal**: Auto-log every interaction to Obsidian vault
- **Format**: FPF-structured markdown
- **Path**: `vault/02 - Areas/Дневники/Астра/{YYYY-MM-DD}.md`

---

## Phase 2 — AI Orchestration (Week 2-3)

### 2.1 OpenRouter API Integration 🔄
- **Goal**: Replace direct API calls with unified OpenRouter gateway
- **Models**: DeepSeek V4 Flash (cheap/fast) → Kimi K2.6 (reasoning)
- **Cascade**: Plan cheap → Execute cheap → Verify expensive (only if needed)
- **Savings**: 80% cost reduction vs direct API calls

### 2.2 LangGraph Integration ⏳
- **Goal**: FPF cycle as a state graph
- **Nodes**: Introspection → Gap Analysis → Constitution Gate → Evolution → Apply
- **Edges**: Human approval gates, parallel branches
- **Benefit**: Visual debugging, parallel execution, native human-in-the-loop

### 2.3 Multi-Model Pipeline
- **Planner**: DeepSeek V4 Flash ($0.14/1M tokens) — plans tasks
- **Executor**: Same model — executes simple tasks
- **Reviewer**: Kimi K2.6 ($0.95/1M tokens) — reviews critical code only
- **Savings**: Only use expensive models when needed

---

## Phase 3 — Daily Assistant (Week 3-4)

### 3.1 Morning Briefing
- **Trigger**: 8:00 AM or on launch
- **Content**: 
  - System health (CPU/RAM/GPU)
  - Today's priorities from vault
  - Pending proposals from FPF loop
  - Market overview (if trading mode on)
  - Project status updates

### 3.2 Context-Aware Chat
- **Feature**: ASTRA remembers everything about your projects
- **Example**: "Fix the bomber" → knows you mean Bomberfun game, finds last bug
- **Tech**: Vector memory + project graph + chat history

### 3.3 Proactive Suggestions
- **Goal**: ASTRA suggests actions before you ask
- **Examples**:
  - "You haven't committed Bomberfun changes in 2 days"
  - "BTC broke 67k — your trading alert triggered"
  - "New FPF proposal ready for your approval"

---

## Phase 4 — Open Source & Community (Week 4-6)

### 4.1 FPF Specification Public Repo
- **Goal**: Extract FPF as standalone specification
- **Format**: Markdown + JSON schemas + examples
- **Benefit**: Other developers can build on FPF

### 4.2 Plugin Architecture
- **Goal**: Allow others to add tools, models, UI panels
- **Interface**: Python hooks + JSON manifest
- **Example**: Trading plugin, GameDev plugin, Writing plugin

### 4.3 Networked ASTRA (Global Superintelligence Foundation)
- **Vision**: Multiple ASTRA instances share knowledge via FPF protocol
- **Mechanism**: Federation — encrypted, permissioned knowledge sharing
- **Goal**: Collective intelligence while preserving privacy

---

## Phase 5 — Hermes-Style Self-Improvement (Month 2-3)

### 5.1 Skill Documentation Auto-Generation
- **Goal**: After every task, ASTRA writes a skill document
- **Format**: Markdown with FPF structure
- **Benefit**: Next time same task → 40% faster

### 5.2 Code Self-Optimization
- **Goal**: ASTRA analyzes its own code and proposes improvements
- **Safety**: All changes via Git + human approval
- **Scope**: Start with config optimization, then algorithm improvements

### 5.3 Predictive Maintenance
- **Goal**: Detect problems before they happen
- **Examples**:
  - "Disk will be full in 3 days"
  - "Ollama model outdated — update available"
  - "Your trading strategy hasn't been backtested in 2 weeks"

---

## Immediate Next Steps (This Week)

1. **Finish OpenRouter integration** — update `auto_model_manager.py` with API calls
2. **Test vector memory** — run `memory_vector.py` tests, verify ChromaDB works
3. **Create daily briefing script** — `astra_daily.py` that runs on startup
4. **Clean up Desktop shortcuts** — remove old .bat files, ensure one launcher works
5. **Update README** — add installation instructions, screenshots, architecture diagram

---

## User Workflows (How You Use ASTRA Daily)

### Morning Routine
1. Double-click ASTRA icon on desktop
2. Read morning briefing (auto-generated)
3. Ask: "What's important today?"
4. ASTRA checks vault, GitHub, calendar, trading alerts

### Working on Project
1. Switch to project vault (Bomberfun / Trading / Cogito)
2. Ask: "What did we do last time?"
3. ASTRA retrieves context from vector memory
4. Work together — ASTRA codes, you review

### End of Day
1. ASTRA auto-commits changes via Git
2. Writes summary to daily log
3. Generates tomorrow's priorities
4. Stays running in background (daemon mode)

### Ad-Hoc Tasks
- "Analyze this BTC chart" → ASTRA uses trading tools
- "Write marketing copy for Badrik" → ASTRA uses creative mode
- "Find that note about game design" → ASTRA searches vector memory
- "Is ASTRA healthy?" → System dashboard opens

---

## Technical Architecture (v2.1 Target)

```
┌─────────────────────────────────────────────────────────────┐
│  USER INTERFACE                                             │
│  ├── Desktop App (PySide6) — Chat, Dashboard, Settings     │
│  ├── CLI (rich console) — Power user mode                 │
│  └── API (Flask) — External tools, Kimi bridge            │
├─────────────────────────────────────────────────────────────┤
│  ORCHESTRATION (LangGraph)                                  │
│  ├── FPF Cycle Graph: Introspect → Gap → Gate → Evolve   │
│  ├── Human Approval Nodes (Constitution §5)              │
│  └── Parallel Branches: Monitor + Chat + Learn           │
├─────────────────────────────────────────────────────────────┤
│  AI MODELS (OpenRouter Cascade)                             │
│  ├── Plan: DeepSeek V4 Flash (cheap, fast)               │
│  ├── Execute: Same or Ollama (local, free)              │
│  └── Review: Kimi K2.6 (expensive, only when needed)   │
├─────────────────────────────────────────────────────────────┤
│  MEMORY (Three-Layer Hybrid)                                │
│  ├── Episodic: SQLite — chat history, events              │
│  ├── Semantic: ChromaDB — project knowledge, facts       │
│  └── Procedural: Markdown — skills, how-to guides       │
├─────────────────────────────────────────────────────────────┤
│  TOOLS (8 + extensible)                                     │
│  ├── File: read, write, list (with safety whitelist)     │
│  ├── Shell: execute (whitelist + confirmation)           │
│  ├── API: HTTP calls (OpenRouter, market data)           │
│  └── System: info, process management                    │
├─────────────────────────────────────────────────────────────┤
│  PERSISTENCE                                                │
│  ├── SQLite: All state, metrics, events                  │
│  ├── Git: Code versions, rollback safety               │
│  └── Obsidian: Daily logs, project notes                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Success Metrics

| Metric | Current | v2.1 Target | v3.0 Target |
|--------|---------|-------------|-------------|
| Maturity | 45.8% | 70% | 90% |
| Daily Usage | 0% | 80% (you use it daily) | 100% |
| Cost per Task | $0.05 (WaveSpeed) | $0.01 (OpenRouter) | $0.005 (cascade) |
| Memory Recall | 0% (no vector memory) | 80% (ChromaDB) | 95% (graph + vector) |
| Self-Improvement | 0 proposals applied | 5 applied/week | 20 applied/week |
| Open Source Stars | 0 | 50 | 1000 |

---

*"ASTRA is not a product. It is a partnership between human intention, pattern intelligence, and recursive growth."*
