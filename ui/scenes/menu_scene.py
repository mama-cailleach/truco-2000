"""
Menu Scene - Main menu with game options.
"""

import pygame
from ui.scenes.base_scene import BaseScene
from ui.widgets import Button
from config import GameConfig


class MenuScene(BaseScene):
    """
    Main menu scene.
    
    Shows buttons for: Jogar, Configurações, Tutorial, Sair.
    """
    
    def on_enter(self) -> None:
        """Initialize the menu scene."""
        self.font_title = pygame.font.Font(None, GameConfig.FONT_SIZE_TITLE)
        self.font_button = pygame.font.Font(None, GameConfig.FONT_SIZE_LARGE)
        
        # Button rectangles
        button_width = 150
        button_height = 50
        button_x = (self.app.width - button_width) // 2
        
        tm = self.app.text_manager
        self.buttons = [
            Button(tm.get_text("menu.play"), pygame.Rect(button_x, 200, button_width, button_height), "play"),
            Button(tm.get_text("menu.settings"), pygame.Rect(button_x, 280, button_width, button_height), "settings"),
            Button(tm.get_text("menu.tutorial"), pygame.Rect(button_x, 360, button_width, button_height), "tutorial"),
            Button(tm.get_text("menu.quit"), pygame.Rect(button_x, 440, button_width, button_height), "quit"),
        ]
        
    def on_exit(self) -> None:
        """Clean up menu scene."""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle menu events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in self.buttons:
                if button.handle_event(event):
                    self._handle_button_click(button.action)
        elif event.type == pygame.KEYDOWN:
            # Optional keyboard shortcuts: 1-4 correspond to buttons
            if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                idx = event.key - pygame.K_1
                if 0 <= idx < len(self.buttons):
                    self._handle_button_click(self.buttons[idx].action)
    
    def _handle_button_click(self, action: str) -> None:
        """Handle button click actions."""
        if action == "play":
            # Transition to game scene
            from ui.scenes.game_scene import GameScene
            self.app.replace_scene(GameScene(self.app))
        elif action == "settings":
            print("[TODO] Settings scene not yet implemented")
        elif action == "tutorial":
            print("[TODO] Tutorial scene not yet implemented")
        elif action == "quit":
            self.app.running = False
    
    def update(self, delta_time: float) -> None:
        """Update menu scene (track hover state)."""
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the menu scene."""
        # Draw title
        title_text = self.font_title.render(
            self.app.text_manager.get_text("welcome.title"),
            True,
            GameConfig.COLOR_PRIMARY
        )
        title_rect = title_text.get_rect(center=(self.app.width // 2, 80))
        surface.blit(title_text, title_rect)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(surface, self.font_button)
