from textual.widgets import Static
from typing import List

class HandWidget(Static):
    """Render player's hand as stacked ASCII card blocks.

    For the skeleton we render cards vertically; later we can render side-by-side.
    """
    def __init__(self, hand_cards: List[List[str]] = None, **kwargs):
        hand_cards = hand_cards or []
        content = self._render_hand(hand_cards)
        super().__init__(content, **kwargs)

    def _render_hand(self, hand_cards: List[List[str]], selected_index: int | None = None) -> str:
        if not hand_cards:
            return "(sem cartas)"

        # Determine card block height and normalize
        card_height = max(len(c) for c in hand_cards)
        norm_cards = []
        for c in hand_cards:
            lines = c[:] + ["     "] * (card_height - len(c))
            norm_cards.append(lines)

        # Combine horizontally: join corresponding lines from each card
        out_lines = []
        for row in range(card_height):
            row_parts = [norm_cards[i][row] for i in range(len(norm_cards))]
            out_lines.append("  ".join(row_parts))

        # Add an index line under cards for quick reference. Highlight selection.
        index_parts = []
        for i in range(len(norm_cards)):
            idx = i + 1
            if selected_index is not None and selected_index == idx:
                index_parts.append(f">({idx})<")
            else:
                index_parts.append(f" ({idx}) ")
        out_lines.append("  ".join(index_parts))

        return "\n".join(out_lines)

    def update_hand(self, hand_cards: List[List[str]], selected_index: int | None = None):
        """Update the hand display. selected_index is 1-based or None."""
        self.update(self._render_hand(hand_cards, selected_index))
