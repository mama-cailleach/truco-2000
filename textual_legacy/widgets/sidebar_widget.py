from textual.widgets import Static
from typing import Dict, List

from config import GameConfig
from ui.ascii_art import ASCIIArt

class SidebarWidget(Static):
    """Sidebar showing scores, vira and manilha, and round history."""
    def __init__(self, snapshot: Dict = None, **kwargs):
        snapshot = snapshot or {}
        self.cards_db = ASCIIArt().fill_cards_database()
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
        vira = snapshot.get('carta_vira', '-')
        lines.append("VIRA:")
        vira_art = self.cards_db.get(vira)
        if vira_art:
            lines.extend(vira_art.split("\n"))
        else:
            lines.append(str(vira))
        lines.append("")
        
        # Display all four manilhas in strength order (♣ ♥ ♠ ♦)
        manilha_rank = snapshot.get('manilha', '-')
        if manilha_rank != '-':
            manilhas = f"{manilha_rank}♣ {manilha_rank}♥ {manilha_rank}♠ {manilha_rank}♦"
            lines.append(f"MANILHAS: {manilhas}")
        else:
            lines.append("MANILHAS: -")
        lines.append("")
        lines.append(f"Mão Valendo: {snapshot.get('current_hand_value', '-')}")
        lines.append("")
        rounds = snapshot.get('round_results', [])
        lines.append("RESULTADOS:")
        for i, r in enumerate(rounds):
            lines.append(f"  Rodada {i+1}: {r}")
        return "\n".join(lines)

    def update_snapshot(self, snapshot: Dict):
        self.update(self.render_snapshot(snapshot))
