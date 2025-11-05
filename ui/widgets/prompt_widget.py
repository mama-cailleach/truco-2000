from textual.widgets import Static, Button
from textual.containers import Horizontal
from textual.app import ComposeResult
from typing import List, Tuple


class PromptWidget(Static):
    """Action button row under the player's hand.

    Buttons are updated dynamically via `update_actions`, which accepts a list
    of (id, label) tuples up to 4 items. Buttons beyond the provided list are hidden.
    """
    def compose(self) -> ComposeResult:
        # Create four slots for buttons. We'll update their labels/ids at runtime.
        with Horizontal():
            self.btn1 = Button("Play Card", id="play")
            yield self.btn1
            self.btn2 = Button("Truco", id="truco")
            yield self.btn2
            self.btn3 = Button("Run", id="run")
            yield self.btn3
            self.btn4 = Button("Restart", id="restart")
            yield self.btn4

    def update_actions(self, actions: List[Tuple[str, str]]):
        """Update up to 4 button slots with (id, label).

        actions: list of (id, label). If fewer than 4 provided, remaining buttons are hidden.
        """
        slots = [self.btn1, self.btn2, self.btn3, self.btn4]
        for i, btn in enumerate(slots):
            if i < len(actions):
                btn_id, label = actions[i]
                btn.id = btn_id
                btn.label = label
                btn.display = True
            else:
                # hide unused buttons
                btn.display = False
