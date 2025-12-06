from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal
from textual.app import ComposeResult
from typing import List, Tuple, Optional


class GameBanner(Static):
    """Base overlay banner widget for game notifications and prompts.
    
    Provides a consistent structure for all game banners with:
    - A main message area
    - Optional action buttons
    - Configurable styling via CSS classes
    
    Subclasses should override compose() or use the default layout.
    """
    
    def __init__(
        self, 
        message: str = "",
        buttons: Optional[List[Tuple[str, str, str]]] = None,
        banner_id: str = "game_banner",
        message_classes: str = "banner_message",
        **kwargs
    ):
        """Initialize the banner.
        
        Args:
            message: Main text to display
            buttons: List of (label, id, variant) tuples for buttons
            banner_id: ID for the container element
            message_classes: CSS classes for the message Static
        """
        super().__init__(**kwargs)
        self.message = message
        self.buttons = buttons or []
        self.banner_id = banner_id
        self.message_classes = message_classes
    
    def compose(self) -> ComposeResult:
        """Compose the default banner layout: message + buttons."""
        with Vertical(id=f"{self.banner_id}_container"):
            self.message_widget = Static(
                self.message, 
                id=f"{self.banner_id}_message", 
                classes=self.message_classes
            )
            yield self.message_widget
            
            if self.buttons:
                with Horizontal(id=f"{self.banner_id}_buttons"):
                    for label, btn_id, variant in self.buttons:
                        yield Button(label, id=btn_id, variant=variant)
    
    def update_message(self, new_message: str) -> None:
        """Update the banner message text."""
        self.message = new_message
        try:
            self.message_widget.update(new_message)
        except Exception:
            pass
