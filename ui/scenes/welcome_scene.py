"""
Welcome Scene - First screen shown to the player.
"""

import pygame
from ui.scenes.base_scene import BaseScene
from config import GameConfig


class WelcomeScene(BaseScene):
    """
    Welcome scene with sizing guide.
    
    Shows a message prompting the player to press any key to continue.
    """
    
    def on_enter(self) -> None:
        """Initialize the welcome scene."""
        self.font_title = pygame.font.Font(None, GameConfig.FONT_SIZE_TITLE)
        self.font_normal = pygame.font.Font(None, GameConfig.FONT_SIZE_NORMAL)
        self.any_key_pressed = False
        
    def on_exit(self) -> None:
        """Clean up welcome scene."""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle events - any key press goes to menu."""
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            # Transition to menu scene
            from ui.scenes.menu_scene import MenuScene
            self.app.replace_scene(MenuScene(self.app))
    
    def update(self, delta_time: float) -> None:
        """Update welcome scene."""
        pass
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the welcome scene."""
        # Draw border box (sizing guide)
        width, height = 600, 400
        x = (self.app.width - width) // 2
        y = (self.app.height - height) // 2
        
        pygame.draw.rect(surface, GameConfig.COLOR_PRIMARY, (x, y, width, height), 2)
        
        # Draw title
        title_text = self.font_title.render(
            self.app.text_manager.get_text("welcome.title"),
            True,
            GameConfig.COLOR_PRIMARY
        )
        title_rect = title_text.get_rect(center=(self.app.width // 2, y + 80))
        surface.blit(title_text, title_rect)
        
        # Draw instruction
        instruction_text = self.font_normal.render(
            self.app.text_manager.get_text("welcome.prompt"),
            True,
            GameConfig.COLOR_TEXT
        )
        instr_rect = instruction_text.get_rect(center=(self.app.width // 2, self.app.height // 2 + 100))
        surface.blit(instruction_text, instr_rect)
