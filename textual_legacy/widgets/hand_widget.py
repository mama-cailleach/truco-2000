from textual.widgets import Static, Button
from textual.containers import Horizontal, Vertical
from textual.app import ComposeResult
from typing import List

class HandWidget(Static):
    """Render player's hand with buttons under each card for direct selection.
    
    Layout:
    - Top: horizontal display of 3 cards side-by-side
    - Bottom: 3 buttons labeled 1, 2, 3 under each card
    """
    def __init__(self, hand_cards: List[List[str]] = None, **kwargs):
        super().__init__(**kwargs)
        self.hand_cards = hand_cards or []
        self.selected_index = None
        self.card_buttons = []

    def compose(self) -> ComposeResult:
        # Create vertical container: cards on top, buttons on bottom
        with Vertical(id="hand_container"):
            # Card display area (Static widget)
            self.card_display = Static(self._render_cards(), id="card_display")
            yield self.card_display
            
            # Button row: 3 buttons for cards 1, 2, 3
            with Horizontal(id="card_button_row"):
                for i in range(1, 4):
                    btn = Button(str(i), id=f"card_{i}")
                    self.card_buttons.append(btn)
                    yield btn

    def _render_cards(self) -> str:
        """Render just the cards without buttons."""
        if not self.hand_cards:
            return "(sem cartas)"

        # Determine card block height and normalize
        card_height = max(len(c) for c in self.hand_cards)
        norm_cards = []
        for c in self.hand_cards:
            lines = c[:] + ["      "] * (card_height - len(c))
            norm_cards.append(lines)

        # Combine horizontally: join corresponding lines from each card
        out_lines = []
        for row in range(card_height):
            row_parts = [norm_cards[i][row] for i in range(len(norm_cards))]
            out_lines.append("  " + "  ".join(row_parts))

        # Add an index line under cards for quick reference. Highlight selection.
        index_parts = []
        out_lines.append("  ".join(index_parts))

        return "\n".join(out_lines)

    def update_hand(self, hand_cards: List[List[str]], selected_index: int | None = None):
        """Update the hand display with new cards and selection state."""
        self.hand_cards = hand_cards
        self.selected_index = selected_index
        
        # Update card display
        try:
            self.card_display.update(self._render_cards())
        except Exception:
            pass
        
        # Update button visibility and state
        # Show buttons for available cards, hide others
        try:
            for i, btn in enumerate(self.card_buttons):
                card_idx = i + 1
                if card_idx <= len(hand_cards):
                    btn.display = True
                else:
                    btn.display = False
        except Exception:
            pass
    
    def set_card_buttons_disabled(self, disabled: bool):
        """Enable or disable card buttons."""
        try:
            for btn in self.card_buttons:
                btn.disabled = disabled
        except Exception:
            pass

