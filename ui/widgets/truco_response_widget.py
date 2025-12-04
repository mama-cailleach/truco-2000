from textual.widgets import Static, Button
from textual.containers import Horizontal, Vertical
from textual.app import ComposeResult


class TrucoResponseWidget(Static):
    """Banner widget shown when player must respond to opponent's truco call/reraise.
    
    Displays the pending value and offers Accept, Run, Reraise buttons.
    This overlays the main play area and blocks other interactions.
    """
    
    def __init__(self, pending_truco_name: str = "Truco", **kwargs):
        super().__init__(**kwargs)
        self.pending_truco_name = pending_truco_name
    
    def compose(self) -> ComposeResult:
        with Vertical(id="truco_response_container"):
            yield Static(f"Oponente pediu {self.pending_truco_name}", id="truco_message", classes="truco_title")
            with Horizontal(id="truco_buttons"):
                yield Button("Aceitar", id="truco_accept", variant="primary")
                yield Button("Fugir", id="truco_run", variant="warning")
                yield Button("Aumentar", id="truco_reraise", variant="default")
    
    def update_message(self, pending_truco_name: str):
        """Update the pending truco message."""
        self.pending_truco_name = pending_truco_name
        try:
            msg_widget = self.query_one("#truco_message", Static)
            msg_widget.update(f"Oponente pediu {pending_truco_name}")
        except Exception:
            pass
