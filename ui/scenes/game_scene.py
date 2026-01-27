"""
Game Scene - Main gameplay screen.

This is a placeholder that will be fleshed out in Phase 3+.
"""

import pygame
from ui.scenes.base_scene import BaseScene
from config import GameConfig


class GameScene(BaseScene):
    """
    Main game scene.
    
    Displays the game board, player hand, opponent area, and controls.
    Will be expanded in Phase 3+ to include full gameplay logic.
    """
    
    def on_enter(self) -> None:
        """Initialize the game scene."""
        self.font_title = pygame.font.Font(None, GameConfig.FONT_SIZE_TITLE)
        self.font_normal = pygame.font.Font(None, GameConfig.FONT_SIZE_NORMAL)
        
    def on_exit(self) -> None:
        """Clean up game scene."""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle game scene events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Return to menu
                from ui.scenes.menu_scene import MenuScene
                self.app.replace_scene(MenuScene(self.app))
    
    def update(self, delta_time: float) -> None:
        """Update game scene."""
        pass
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the game scene."""
        # Draw title
        title_text = self.font_title.render("TRUCO 2000 - Jogo", True, GameConfig.COLOR_PRIMARY)
        title_rect = title_text.get_rect(center=(self.app.width // 2, 40))
        surface.blit(title_text, title_rect)
        
        # Draw placeholder text
        placeholder = self.font_normal.render(
            "Game scene - Phase 3+ implementation",
            True,
            GameConfig.COLOR_TEXT
        )
        placeholder_rect = placeholder.get_rect(center=(self.app.width // 2, self.app.height // 2))
        surface.blit(placeholder, placeholder_rect)
        
        # Draw escape hint
        hint = self.font_normal.render("ESC para voltar ao menu", True, GameConfig.COLOR_TEXT_SECONDARY)
        hint_rect = hint.get_rect(center=(self.app.width // 2, self.app.height - 40))
        surface.blit(hint, hint_rect)
