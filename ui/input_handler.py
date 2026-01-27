"""
InputHandler for Pygame events.

Provides global shortcut handling and routes events to the current scene.
"""

import pygame
from typing import Callable, Dict


class InputHandler:
    """
    Central input handler for the Pygame app.
    
    - Registers global key shortcuts (e.g., Q to quit, ESC to go back)
    - Routes events to the active scene
    """

    def __init__(self, app) -> None:
        self.app = app
        self.global_key_handlers: Dict[int, Callable[[], None]] = {}

    def register_global_key(self, key: int, callback: Callable[[], None]) -> None:
        """Register a global keypress callback."""
        self.global_key_handlers[key] = callback

    def process_event(self, event: pygame.event.Event) -> None:
        """Process a single Pygame event."""
        # Handle window close
        if event.type == pygame.QUIT:
            self.app.running = False
            return

        # Global key shortcuts
        if event.type == pygame.KEYDOWN:
            handler = self.global_key_handlers.get(event.key)
            if handler:
                handler()
                # If handler quits or navigates, stop further processing
                return

        # Route to current scene
        current_scene = self.app.get_current_scene()
        if current_scene:
            current_scene.handle_event(event)
