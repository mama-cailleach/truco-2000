from textual.widgets import Static
from typing import Dict, List

class SidebarWidget(Static):
    """Sidebar showing scores, vira and manilha, and round history."""
    def __init__(self, snapshot: Dict = None, **kwargs):
        snapshot = snapshot or {}
        content = self.render_snapshot(snapshot)
        super().__init__(content, **kwargs)

    def render_snapshot(self, snapshot: Dict) -> str:
        lines: List[str] = []
        # Optional transient message to show in the sidebar
        msg = snapshot.get("message")
        if msg:
            lines.append(f"! {msg}")
            lines.append("")
        scores = snapshot.get("scores", {})
        lines.append(f"PLACAR: Você {scores.get('player', 0)} x {scores.get('opponent', 0)} Oponente")
        lines.append("")
        lines.append(f"VIRA: {snapshot.get('carta_vira', '-')}")
        lines.append(f"MANILHA: {snapshot.get('manilha', '-')}")
        lines.append("")
        rounds = snapshot.get('round_results', [])
        lines.append("RESULTADOS:")
        for i, r in enumerate(rounds):
            lines.append(f"  Rodada {i+1}: {r}")
        return "\n".join(lines)

    def update_snapshot(self, snapshot: Dict):
        self.update(self.render_snapshot(snapshot))
