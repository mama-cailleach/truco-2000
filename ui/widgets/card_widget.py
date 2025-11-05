from textual.widgets import Static
from typing import List

class CardWidget(Static):
    """Render a single ASCII card block.

    Expects card_lines as a list of strings (each line of ASCII art).
    """
    def __init__(self, card_lines: List[str], **kwargs):
        content = "\n".join(card_lines)
        super().__init__(content, **kwargs)

    def update_card(self, card_lines: List[str]):
        self.update("\n".join(card_lines))
