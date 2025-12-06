from textual.widgets import Static
from typing import Dict, List

from config import GameConfig

class SidebarWidget(Static):
    """Sidebar showing scores, vira and manilha, and round history."""
    def __init__(self, snapshot: Dict = None, **kwargs):
        snapshot = snapshot or {}
        content = self.render_snapshot(snapshot)
        super().__init__(content, **kwargs)

    def render_snapshot(self, snapshot: Dict) -> str:
        lines: List[str] = []
        scores = snapshot.get("scores", {})
        p_score = scores.get("player", 0)
        o_score = scores.get("opponent", 0)
        lines.append(f"PLACAR: Você {p_score} x {o_score} Oponente")
        if p_score >= GameConfig.WINNING_SCORE or o_score >= GameConfig.WINNING_SCORE:
            winner = "Você" if p_score >= GameConfig.WINNING_SCORE else "Oponente"
            lines.append("")
            lines.append(f"VENCEDOR: {winner}")
        lines.append("")
        lines.append(f"VIRA: {snapshot.get('carta_vira', '-')}")
        lines.append(f"MANILHA: {snapshot.get('manilha', '-')}")
        lines.append("")
        rounds = snapshot.get('round_results', [])
        lines.append("RESULTADOS:")
        for i, r in enumerate(rounds):
            lines.append(f"  Rodada {i+1}: {r}")
        # Optional transient message to show in the sidebar
        lines.append("")
        msg = snapshot.get("message")
        if msg:
            lines.append(f"! {msg}")
            lines.append("")
        return "\n".join(lines)

    def update_snapshot(self, snapshot: Dict):
        self.update(self.render_snapshot(snapshot))
