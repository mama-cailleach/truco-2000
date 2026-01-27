from textual.widgets import Static
from typing import Optional, List

class BattleZoneWidget(Static):
    """Render the central battle zone showing played cards."""
    def __init__(self, player_card: Optional[List[str]] = None, opponent_card: Optional[List[str]] = None, **kwargs):
        content = self.render_zone(player_card, opponent_card)
        super().__init__(content, **kwargs)

    def render_zone(self, player_card: Optional[List[str]], opponent_card: Optional[List[str]], status_text: str = "") -> str:
        # Render a simple left (player) / center (status) / right (opponent) layout.
        # Each card is expected to be a list of lines (card ASCII block) of equal height.
        card_height = 5

        def normalize(card: Optional[List[str]]) -> List[str]:
            if card and len(card) >= card_height:
                return card[:card_height]
            # Placeholder block of same height - render an empty card outline
            placeholder = [
                "┌─────┐",
                "│  X  │",
                "│  X  │",
                "│  X  │",
                "└─────┘",
            ]
            return placeholder

        left = normalize(player_card)
        right = normalize(opponent_card)

        # Center status lines (one of them may contain status_text) 
        # just blank now. Poss be the deck of cards or something.
        center = ["     "] * card_height

        # Build merged lines
        merged: List[str] = []
        merged.append("MESA".center(len(left[0]) + 15 + len(center[0]) + len(right[0]) + 4))
        for i in range(card_height):
            merged.append(f"{left[i]}   {center[i]}                    {right[i]}")

        return "\n".join(merged)

    def update_zone(self, player_card: Optional[List[str]], opponent_card: Optional[List[str]], status_text: str = ""):
        self.update(self.render_zone(player_card, opponent_card, status_text))
