# -*- coding: utf-8 -*-
"""ASTRA Kernel — System Core v2.2
Orchestrator of holons with Multi-Vault and Smart Router.
"""
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.table import Table
from rich import box

from astra_core.config import get, PROJECT_ROOT, VAULT_PATH, get_vaults, get_active_vault, get_vault_path
from astra_core.hearing import HearingHolon
from astra_core.voice import VoiceHolon
from astra_core.cognition import CognitionHolon
from astra_core.hippocampus import HippocampusHolon
from astra_core.action import ActionHolon
from astra_core.legal import LegalGuardian
from astra_core.soma import SomaHolon
from astra_core.smart_router import SmartRouter
from astra_core.fpf_engine import FPFEngine
from astra_core.fpf_autonomous_loop import FPFAutonomousLoop
from astra_core.fpf_mission import ASTRAGrowthAssessment
from astra_core.evolution_engine import AstraQueen, EvolutionLoop


class AstraKernel:
    """ASTRA Kernel — coordinates all holons."""

    def __init__(self):
        self.console = Console(legacy_windows=False, force_terminal=True)
        self.legal = LegalGuardian()
        self.soma = SomaHolon()
        self.hearing = HearingHolon()
        self.voice = VoiceHolon()
        self.cognition = CognitionHolon()
        self.memory = None
        self.action = None
        self.router = None
        self.current_vault = ""
        self.state: Dict[str, Any] = {
            "chat_history": [],
            "thought_trace": "System initializing...",
            "retrieved_memory": "",
            "gpu_temp": 0,
            "vram_load": "0.0",
            "last_heartbeat": "OFFLINE",
        }
        self.running = True

    def _select_vault(self) -> str:
        """Shows vault selection menu and returns name."""
        vaults = get_vaults()
        if len(vaults) == 1:
            return vaults[0].get("name", "default")

        self.console.print(Panel("[bold magenta]🏛️  VAULT SELECT[/bold magenta]", style="bold magenta"))
        for i, v in enumerate(vaults, 1):
            name = v.get("name", f"Vault {i}")
            path = v.get("path", "")
            role = v.get("role", "personal")
            icon = {"personal": "👤", "project": "📁", "shared": "🌐", "team": "👥"}.get(role, "📂")
            self.console.print(f"  [{i}] {icon} {name} — {path}")
        self.console.print(f"  [0] 🚪 Exit")

        choice = Prompt.ask("[bold]Select Vault[/bold]")
        try:
            idx = int(choice)
            if idx == 0:
                sys.exit(0)
            if 1 <= idx <= len(vaults):
                return vaults[idx - 1].get("name", "default")
        except ValueError:
            pass
        return vaults[0].get("name", "default")

    def _init_vault(self, vault_name: str) -> None:
        """Initialize holons for selected vault."""
        self.current_vault = vault_name
        v = get_active_vault(vault_name)
        self.console.print(f"[dim]📂 Vault: {vault_name} ({v.get('path', '')})[/dim]")
        self.memory = HippocampusHolon(vault_name)
        self.action = ActionHolon(vault_name)
        self.state_file = PROJECT_ROOT / f"agent_state_{vault_name}.json"

    def run_lifecycle_loop(self) -> None:
        """Main kernel lifecycle loop."""
        vault_name = self._select_vault()
        self._init_vault(vault_name)
        self._init_holons()
        self._load_state()
        self._print_banner()
        self._check_vitals()

        while self.running:
            self._print_menu()
            choice = Prompt.ask("[bold]Choice[/bold]")
            self._process_choice(choice)

        self._save_state()
        self.console.print("[bold green]ASTRA finished. Goodbye![/bold green]")

    def _init_holons(self) -> None:
        """Initialize all holons and check availability."""
        self.console.print("[bold cyan]🔧 Initializing holons...[/bold cyan]")
        self.soma.check()
        self.hearing.check()
        self.voice.check()
        self.cognition.check()
        self.memory.check()
        self.action.check()
        self.legal.check()
        self.router = SmartRouter(self.cognition._engines)
        self.console.print("[bold cyan]🔧 Smart Router activated[/bold cyan]")

    def _print_banner(self) -> None:
        banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║     ASTRA Genesis — AI Second Brain v3.0              ║
    ║     AutoModel | FPF Self-Construction | Growth         ║
    ║     Hearing · Voice · Cognition · Memory · Action · Evolution · Growth ║
    ╚═══════════════════════════════════════════════════════════╝
        """
        self.console.print(Panel(banner, style="bold magenta", title="[bold green]● ASTRA ONLINE v3.0[/bold green]"))

    def _check_vitals(self) -> None:
        vitals = self.soma.get_vitals()
        self.state.update(vitals)
        status_text = (
            f"Vault: {self.current_vault} | "
            f"Obsidian: {'OK' if self.memory.check() else 'OFF'} | "
            f"Ollama: {'OK' if self.cognition._engines.get('ollama') else 'OFF'} | "
            f"HF: {'OK' if self.cognition._engines.get('hf') else 'OFF'} | "
            f"Claude: {'OK' if self.cognition._engines.get('claude') else 'OFF'} | "
            f"Kimi: {'OK' if self.cognition._engines.get('kimi') else 'OFF'} | "
            f"Hearing: {'OK' if self.hearing.check() else 'OFF'} | "
            f"Voice: {'OK' if self.voice.check() else 'OFF'} | "
            f"GPU: {vitals['gpu_temp']}C | VRAM: {vitals['vram_load']} GB"
        )
        self.console.print(Panel(status_text, title="Status", style="bold blue"))

    def _print_menu(self) -> None:
        menu = """
  [1]  🎤 Listen + Answer (Smart Router + FPF)
  [2]  💡 Record idea → Vault Inbox
  [3]  📝 Create structured note
  [4]  🔍 Search Vault (by memory)
  [5]  📂 List Vault files
  [6]  🧠 Show thought_trace
  [7]  🔄 Reindex Vault
  [8]  ⚙️  Settings
  [9]  👁️  ASTRA AWAKEN — say "Astra"
  [10] 🧠 Smart Router — test routing
  [11] 🔬 FPF Introspection — analyze ASTRA by FPF
  [12] 🧬 EVOLUTION — run ant colony
  [13] 📈 GROWTH — maturity and growth report
  [14] 🔄 FPF LOOP — autonomous self-construction cycle
  [15] 📋 NEXT STEPS — priority growth tasks
  [0]  🚪 Exit
        """
        self.console.print(Panel(menu, title="Menu", style="bold yellow"))

    def _process_choice(self, choice: str) -> None:
        self.soma.heartbeat()
        if choice == "1":
            self._mode_listen_and_answer()
        elif choice == "2":
            self._mode_record_idea()
        elif choice == "3":
            self._mode_create_note()
        elif choice == "4":
            self._mode_search_vault()
        elif choice == "5":
            self._mode_list_files()
        elif choice == "6":
            self._show_thought_trace()
        elif choice == "7":
            self._reindex_vault()
        elif choice == "8":
            self._show_settings()
        elif choice == "9":
            self._mode_awaken()
        elif choice == "10":
            self._mode_test_router()
        elif choice == "11":
            self._mode_fpf_introspection()
        elif choice == "12":
            self._mode_evolution()
        elif choice == "13":
            self._mode_growth_report()
        elif choice == "14":
            self._mode_fpf_autonomous_loop()
        elif choice == "15":
            self._mode_next_steps()
        elif choice == "0":
            self.running = False
        else:
            self.console.print("[red]Invalid choice[/red]")

    def _mode_listen_and_answer(self) -> None:
        self.console.print("[bold yellow]🎤 Listening... Speak![/bold yellow]")
        text = self.hearing.transcribe(duration=7)
        if not text:
            self.console.print("[red]Speech not recognized[/red]")
            return
        self.console.print(f"[dim]Recognized: {text}[/dim]")
        self._add_to_history("user", text)
        engine, classification = self.router.select_engine(text)
        self.console.print(self.router.explain_routing(text))
        retrieved = self.memory.retrieve(text)
        self.state["retrieved_memory"] = retrieved
        self.console.print(f"[bold cyan]🧠 Thinking via {engine.upper()}...[/bold cyan]")
        result = self.cognition.think(text, context=retrieved, cot=True)
        self.state["thought_trace"] = result["thought_trace"]
        answer = result["answer"]
        self.console.print(Panel(answer, title=f"Answer ({result['source']})", style="bold green"))
        self._add_to_history("assistant", answer)
        if "fpf" in result:
            fpf = result["fpf"]
            lade = fpf["lade"]
            fgr = fpf["fgr"]
            rmw = fpf["rmw"]
            badge = FPFEngine.format_fpf_badge(lade, fgr, rmw)
            self.console.print(f"[dim]{badge}[/dim]")
            self._add_to_history("system", f"FPF: {lade['classification']} | {fgr['composite_label']}")
        audio_path = self.voice.speak(answer)
        if audio_path:
            self._add_to_history("system", f"🎤 Audio generated: {audio_path}")
        self._save_dialogue_to_vault(text, answer)
        self._save_state()

    def _mode_record_idea(self) -> None:
        self.console.print("[bold yellow]💡 Recording idea...[/bold yellow]")
        text = self.hearing.transcribe(duration=10)
        if not text:
            self.console.print("[red]Speech not recognized[/red]")
            return
        self._add_to_history("user", text, metadata={"mode": "idea"})
        result = self.action.create_note(
            folder="00 - Inbox",
            title=f"Idea_{datetime.now().strftime('%H%M')}",
            content=text,
            tags=["idea", "voice", "inbox"]
        )
        self.console.print(f"[green]{result}[/green]")
        self._add_to_history("assistant", result)
        self._save_state()

    def _mode_create_note(self) -> None:
        self.console.print("[bold yellow]📝 Speak topic and content of note...[/bold yellow]")
        text = self.hearing.transcribe(duration=15)
        if not text:
            self.console.print("[red]Speech not recognized[/red]")
            return
        title = text[:50].strip()
        result = self.action.create_note(
            folder="02 - Areas",
            title=title,
            content=text,
            tags=["voice", "note"]
        )
        self.console.print(f"[green]{result}[/green]")
        self._add_to_history("assistant", result)
        self._save_state()

    def _mode_search_vault(self) -> None:
        query = Prompt.ask("[bold]What to search?[/bold]")
        if not query:
            return
        retrieved = self.memory.retrieve(query)
        self.state["retrieved_memory"] = retrieved
        self.console.print(Panel(retrieved or "Nothing found", title="Search results", style="bold cyan"))

    def _mode_list_files(self) -> None:
        path = Prompt.ask("[bold]Path in Vault (Enter = root)[/bold]", default=".")
        result = self.action.list_files(path)
        self.console.print(Panel(result, title="Vault files", style="bold blue"))

    def _show_thought_trace(self) -> None:
        self.console.print(Panel(self.state.get("thought_trace", "No data"), title="Thought Trace", style="dim"))

    def _reindex_vault(self) -> None:
        self.console.print("[bold cyan]🔄 Indexing Vault...[/bold cyan]")
        count = self.memory.index_vault(max_files=100)
        self.console.print(f"[green]Indexed {count} files[/green]")

    def _show_settings(self) -> None:
        self.console.print("[bold]Configuration:[/bold]")
        self.console.print(f"Vault: {self.current_vault}")
        self.console.print(f"State: {self.state_file}")
        self.console.print(f"ChromaDB: {self.memory.chroma_dir}")
        self.console.print(f"Smart Router priority: {self.router.priority}")
        self.console.print("[dim]Edit config.json manually for changes[/dim]")

    def _mode_awaken(self) -> None:
        self.console.print("[bold magenta]👁️ ASTRA AWAKEN — continuous listening mode[/bold magenta]")
        self.console.print("[dim]Say 'Astra' and ask a question. Ctrl+C to exit.[/dim]")

        def handle_command(command: str):
            if not command:
                self.console.print("[yellow]Empty command.[/yellow]")
                return
            self.console.print(f"[bold green]Command: {command}[/bold green]")
            self._add_to_history("user", command, metadata={"mode": "awaken"})
            engine, classification = self.router.select_engine(command)
            self.console.print(self.router.explain_routing(command))
            retrieved = self.memory.retrieve(command)
            self.state["retrieved_memory"] = retrieved
            self.console.print(f"[bold cyan]🧠 Thinking via {engine.upper()}...[/bold cyan]")
            result = self.cognition.think(command, context=retrieved, cot=True)
            self.state["thought_trace"] = result["thought_trace"]
            answer = result["answer"]
            self.console.print(Panel(answer, title=f"Answer ({result['source']})", style="bold green"))
            self._add_to_history("assistant", answer)
            audio_path = self.voice.speak(answer)
            if audio_path:
                self._add_to_history("system", f"🎤 Audio: {audio_path}")
            self._save_dialogue_to_vault(command, answer)
            self._save_state()

        try:
            self.hearing.listen_continuous(handle_command)
        except Exception as e:
            self.console.print(f"[red]AWAKEN error: {e}[/red]")

    def _mode_test_router(self) -> None:
        self.console.print("[bold cyan]🧠 Smart Router — Routing test[/bold cyan]")
        test_queries = [
            "Record idea: add boss to bomberfun",
            "Analyze WebSockets network architecture",
            "Find Cogito notes in Vault",
            "How are you?",
            "Write marketing text for Badrik.com",
            "BTC broke 67k, what do you think?",
        ]
        for q in test_queries:
            engine, info = self.router.select_engine(q)
            self.console.print(f"[dim]Q: {q}[/dim]")
            self.console.print(f"[bold]→ {engine.upper()} ({info['level']}) | Intent: {info['intent']} | Complexity: {info['complexity']}[/bold]")
            self.console.print("")

    def _mode_fpf_introspection(self) -> None:
        self.console.print("[bold magenta]🔬 FPF Introspection — analyze ASTRA by First Principles Framework[/bold magenta]")
        import glob
        core_files = glob.glob(str(PROJECT_ROOT / "astra_core" / "*.py"))
        self.console.print(f"[dim]Found {len(core_files)} modules[/dim]")
        for fpath in sorted(core_files):
            fname = Path(fpath).name
            self.console.print(f"\n[bold cyan]📄 {fname}[/bold cyan]")
            result = FPFEngine.introspect_astra(fpath)
            for finding in result.get("findings", []):
                self.console.print(f"  {finding}")
            for rec in result.get("recommendations", [])[:3]:
                self.console.print(f"  [yellow]→ {rec}[/yellow]")
        self.console.print("\n[bold green]✅ Introspection complete[/bold green]")
        self.console.print("[dim]Recommendations saved to FPF Vault[/dim]")

    def _mode_evolution(self) -> None:
        self.console.print("[bold purple]🧬 EVOLUTION — Ant colony generation[/bold purple]")
        colony_state = PROJECT_ROOT / "colony_state.json"
        if colony_state.exists():
            self.console.print(f"[dim]📋 Loaded previous colony state: {colony_state}[/dim]")
        self.console.print("\n[bold]Select target files:[/bold]")
        self.console.print("  [1] All astra_core/ modules")
        self.console.print("  [2] Only kernel.py (core)")
        self.console.print("  [3] Only cognition.py (thinking)")
        self.console.print("  [4] Only fpf_engine.py (FPF)")
        self.console.print("  [5] Custom (comma-separated)")
        choice = self.console.input("[bold]\nChoice: [/bold]").strip()
        import glob
        if choice == "1":
            target_files = glob.glob(str(PROJECT_ROOT / "astra_core" / "*.py"))
        elif choice == "2":
            target_files = [str(PROJECT_ROOT / "astra_core" / "kernel.py")]
        elif choice == "3":
            target_files = [str(PROJECT_ROOT / "astra_core" / "cognition.py")]
        elif choice == "4":
            target_files = [str(PROJECT_ROOT / "astra_core" / "fpf_engine.py")]
        elif choice == "5":
            custom = self.console.input("Paths comma-separated: ").strip()
            target_files = [f.strip() for f in custom.split(",")]
        else:
            self.console.print("[yellow]Invalid choice, using all modules[/yellow]")
            target_files = glob.glob(str(PROJECT_ROOT / "astra_core" / "*.py"))
        self.console.print(f"\n[dim]🎯 Targets: {len(target_files)} files[/dim]")
        from astra_core.evolution_engine import AstraQueen, EvolutionLoop
        queen = AstraQueen()
        loop = EvolutionLoop(queen)
        self.console.print("\n[bold]👑 Ant Queen launching evolution...[/bold]")
        self.console.print("[dim]Pattern B.4: Observe → Notice → Stabilize → Route[/dim]")
        try:
            gen = loop.run_cycle(target_files)
            self.console.print("\n[bold green]" + "="*50 + "[/bold green]")
            self.console.print(f"[bold green]✅ Generation {gen.name} complete![/bold green]")
            self.console.print("[bold green]="*50 + "[/bold green]")
            fitness_table = Table(title="Fitness Evaluation", box=box.ROUNDED)
            fitness_table.add_column("Metric", style="cyan")
            fitness_table.add_column("Score", style="yellow")
            for key, val in gen.fitness.items():
                bar = "█" * int(val * 10) + "░" * (10 - int(val * 10))
                fitness_table.add_row(key, f"{bar} {val:.2f}")
            self.console.print(fitness_table)
            status = queen.colony_status()
            self.console.print("\n[bold]📊 Colony status:[/bold]")
            self.console.print(f"  Total generations: {status['total_generations']}")
            self.console.print(f"  Best generation: {status['best_generation']}")
            self.console.print(f"  Best fitness: {status['best_fitness']:.2f}")
            self.memory.add_axiom(f"Evolution: {gen.name} — fitness {gen.fitness.get('overall', 0):.2f}")
            self.console.print(f"\n[dim]📝 Report saved to Vault: fpf-vault/01 - Projects/Astra Evolution/[/dim]")
            self.console.print("\n[bold]What's next?[/bold]")
            self.console.print("  [c] Compare with previous generation")
            self.console.print("  [r] Show best generations")
            self.console.print("  [Enter] Return to menu")
            next_choice = self.console.input("[bold]Choice: [/bold]").strip().lower()
            if next_choice == "c" and status['total_generations'] > 1:
                comp = queen.compare_generations(status['total_generations'], status['total_generations'] - 1)
                self.console.print(f"\n[bold]Comparison:[/bold]")
                self.console.print(f"  {comp['gen_a']} vs {comp['gen_b']}")
                self.console.print(f"  Winner: {comp['winner']}")
                self.console.print(f"  Difference: {comp['fitness_diff']:.2f}")
            elif next_choice == "r":
                best = queen.select_best(3)
                self.console.print("\n[bold]🏆 Top 3 generations:[/bold]")
                for g in best:
                    self.console.print(f"  {g.name}: {g.fitness.get('overall', 0):.2f}")
        except Exception as e:
            self.console.print(f"[red]Evolution error: {e}[/red]")
            import traceback
            traceback.print_exc()

    def _mode_growth_report(self) -> None:
        self.console.print("[bold cyan]📈 ASTRA GROWTH REPORT — FPF-structured self-assessment[/bold cyan]")
        try:
            assessor = ASTRAGrowthAssessment()
            report = assessor.generate_report(verbose=False)
            self.console.print(report)
            self._add_to_history("system", f"Growth report: {assessor.assess_all()['summary']['overall_maturity']}% maturity")
        except Exception as e:
            self.console.print(f"[red]Growth report error: {e}[/red]")

    def _mode_fpf_autonomous_loop(self) -> None:
        self.console.print("[bold cyan]🔄 FPF Autonomous Self-Construction Loop[/bold cyan]")
        self.console.print("[dim]Runs introspection, gap analysis, constitution gate, evolution, dry-run apply.[/dim]")
        try:
            loop = FPFAutonomousLoop()
            result = loop.run_cycle(dry_run=True)
            self.console.print(f"\n[bold green]Cycle complete:[/bold green]")
            self.console.print(f"  Modules: {result['modules']}")
            self.console.print(f"  Proposals: {result['proposals_count']}")
            self.console.print(f"  Passed Constitution: {result['passed_count']}")
            self.console.print(f"  Evolved: {result['evolved_count']}")
            self.console.print(f"  Applied: {result['applied_count']}")
            self._add_to_history("system", f"FPF Loop: {result['proposals_count']} proposals, {result['passed_count']} passed, {result['applied_count']} applied (dry run)")
        except Exception as e:
            self.console.print(f"[red]FPF Loop error: {e}[/red]")

    def _mode_next_steps(self) -> None:
        self.console.print("[bold cyan]📋 NEXT STEPS — Priority growth tasks (dependency-respecting)[/bold cyan]")
        try:
            assessor = ASTRAGrowthAssessment()
            steps = assessor.get_next_steps(5)
            self.console.print("\n[bold]Top 5 priority tasks for ASTRA's growth:[/bold]\n")
            for i, s in enumerate(steps, 1):
                flag = "🔴 AUTONOMY BLOCKER" if s['required_for_autonomy'] else "🟡 Enhancement"
                self.console.print(f"{i}. [{s['id']}] {s['name']} (gap={s['gap']}) {flag}")
                self.console.print(f"   D: {s['action']}")
                self.console.print(f"   Evidence: {s['evidence_required']}")
                self.console.print()
            self._add_to_history("system", f"Next steps: {len(steps)} tasks generated")
        except Exception as e:
            self.console.print(f"[red]Next steps error: {e}[/red]")

    def _add_to_history(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        entry = {"role": role, "content": content, "timestamp": datetime.now().isoformat()}
        if metadata:
            entry["metadata"] = metadata
        self.state["chat_history"].append(entry)
        self.memory.add_episode(role, content, metadata)

    def _save_dialogue_to_vault(self, question: str, answer: str) -> None:
        date_str = datetime.now().strftime("%Y-%m-%d")
        ts = datetime.now().strftime("%H:%M:%S")
        relative_path = f"02 - Areas/Дневники/Голосовые диалоги/{date_str}.md"
        content = f"\n## {ts}\n\n**Q:** {question}\n\n**A:** {answer}\n\n---\n"
        self.action.append_file(relative_path, content)

    def _load_state(self) -> None:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self.state.update(loaded)
                if "axioms" in loaded:
                    for ax in loaded["axioms"]:
                        self.memory.add_axiom(ax)
                self.console.print("[dim]State loaded[/dim]")
            except Exception:
                pass

    def _save_state(self) -> None:
        try:
            state_to_save = self.state.copy()
            state_to_save["axioms"] = self.memory.axioms
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state_to_save, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.console.print(f"[red]State save error: {e}[/red]")


def main():
    try:
        kernel = AstraKernel()
        kernel.run_lifecycle_loop()
    except KeyboardInterrupt:
        print("\n[ASTRA] Interrupted by user. Saving state...")
    except Exception as e:
        print(f"\n[ASTRA] Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
