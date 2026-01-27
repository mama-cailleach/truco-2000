from textual.widgets import Static, Button
from textual.containers import Horizontal
from textual.app import ComposeResult
from typing import List, Tuple


class PromptWidget(Static):
    """Action button row with only Truco and Run buttons (main game actions).
    
    Card selection is now done via buttons under each card in HandWidget.
    Restart is done via 'W' key.
    """
    def compose(self) -> ComposeResult:
        # Create two main action buttons: Truco and Run
        with Horizontal(id="action_buttons"):
            self.truco_btn = Button("Truco", id="truco")
            yield self.truco_btn
            self.run_btn = Button("Fugir", id="run")
            yield self.run_btn
