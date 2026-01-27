from ui.widgets.game_banner import GameBanner


class TrucoResponseWidget(GameBanner):
    """Banner widget shown when player must respond to opponent's truco call/reraise.
    
    Displays the pending value and offers Accept, Run, Reraise buttons.
    This overlays the main play area and blocks other interactions.
    """
    
    def __init__(self, pending_truco_name: str = "Truco", **kwargs):
        self.pending_truco_name = pending_truco_name
        buttons = [
            ("Aceitar", "truco_accept", "primary"),
            ("Fugir", "truco_run", "warning"),
            ("Aumentar", "truco_reraise", "default"),
        ]
        super().__init__(
            message=f"Oponente pediu {pending_truco_name}",
            buttons=buttons,
            banner_id="truco_response",
            message_classes="truco_title",
            **kwargs
        )
    
    def update_message(self, pending_truco_name: str):
        """Update the pending truco message."""
        self.pending_truco_name = pending_truco_name
        super().update_message(f"Oponente pediu {pending_truco_name}")
