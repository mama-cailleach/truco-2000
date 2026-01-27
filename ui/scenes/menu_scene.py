"""
Menu Scene - Main menu with game options.
"""

import pygame
from ui.scenes.base_scene import BaseScene
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
            {"label": tm.get_text("menu.play"), "rect": pygame.Rect(button_x, 200, button_width, button_height), "action": "play", "hovered": False},
            {"label": tm.get_text("menu.settings"), "rect": pygame.Rect(button_x, 280, button_width, button_height), "action": "settings", "hovered": False},
            {"label": tm.get_text("menu.tutorial"), "rect": pygame.Rect(button_x, 360, button_width, button_height), "action": "tutorial", "hovered": False},
            {"label": tm.get_text("menu.quit"), "rect": pygame.Rect(button_x, 440, button_width, button_height), "action": "quit", "hovered": False},
        ]
        
    def on_exit(self) -> None:
        """Clean up menu scene."""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle menu events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for button in self.buttons:
                if button["rect"].collidepoint(mouse_pos):
                    self._handle_button_click(button["action"])
        elif event.type == pygame.KEYDOWN:
            # Placeholder for keyboard shortcuts
            pass
    
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
            button["hovered"] = button["rect"].collidepoint(mouse_pos)
    
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
            color = GameConfig.COLOR_BUTTON_HOVER if button["hovered"] else GameConfig.COLOR_PRIMARY
            pygame.draw.rect(surface, color, button["rect"], 2)
            
            # Draw button text
            text = self.font_button.render(button["label"], True, color)
            text_rect = text.get_rect(center=button["rect"].center)
            surface.blit(text, text_rect)
