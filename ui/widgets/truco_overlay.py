"""
Truco Overlay Widget

Displays the truco negotiation UI with call/response options.
Shows when someone calls truco and provides buttons for Accept/Run/Reraise.
"""

import pygame
from ui.widgets.button import Button
from config import GameConfig


class TrucoOverlay:
    """
    Overlay widget for truco negotiation.
    
    Displays:
    - Semi-transparent background
    - Message text (who called truco and current level)
    - Action buttons (Accept, Run, Reraise)
    """
    
    def __init__(self, width: int, height: int):
        """
        Initialize the truco overlay.
        
        Args:
            width: Overlay width (typically screen width)
            height: Overlay height (typically screen height)
        """
        self.width = width
        self.height = height
        
        # Fonts
        self.font_title = pygame.font.Font(None, GameConfig.FONT_SIZE_TITLE)
        self.font_button = pygame.font.Font(None, GameConfig.FONT_SIZE_LARGE)
        
        # Create buttons
        button_width = 180
        button_height = 50
        button_spacing = 20
        center_x = width // 2
        center_y = height // 2 + 50
        
        # Position buttons horizontally centered
        total_width = (button_width * 3) + (button_spacing * 2)
        start_x = center_x - (total_width // 2)
        
        self.accept_button = Button(
            "ACEITAR",
            pygame.Rect(start_x, center_y, button_width, button_height),
            "accept"
        )
        
        self.run_button = Button(
            "CORRER",
            pygame.Rect(start_x + button_width + button_spacing, center_y, button_width, button_height),
            "run"
        )
        
        self.reraise_button = Button(
            "AUMENTAR",
            pygame.Rect(start_x + (button_width + button_spacing) * 2, center_y, button_width, button_height),
            "reraise"
        )
        
        self.buttons = [self.accept_button, self.run_button, self.reraise_button]
        
        # State
        self.message = ""
        self.can_reraise = True
        
    def set_message(self, who_called: str, truco_name: str, can_reraise: bool = True):
        """
        Set the message to display.
        
        Args:
            who_called: Name of who called truco ("Você" or opponent name)
            truco_name: Current truco level name ("Truco", "Seis", "Nove", "Doze")
            can_reraise: Whether reraise is possible (False at max level "Doze")
        """
        self.message = f"{who_called} pediu {truco_name}!"
        self.can_reraise = can_reraise
        
    def handle_event(self, event: pygame.event.Event) -> str:
        """
        Handle mouse events on the overlay.
        
        Args:
            event: Pygame event
            
        Returns:
            str: Action taken ("accept", "run", "reraise", or None)
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check each button
            if self.accept_button.handle_event(event):
                return "accept"
            
            if self.run_button.handle_event(event):
                return "run"
            
            if self.can_reraise and self.reraise_button.handle_event(event):
                return "reraise"
        
        return None
    
    def update(self, mouse_pos):
        """Update button hover states."""
        for button in self.buttons:
            button.update(mouse_pos)
    
    def render(self, surface: pygame.Surface):
        """
        Render the truco overlay.
        
        Args:
            surface: Surface to render on
        """
        # Semi-transparent black background
        overlay_surface = pygame.Surface((self.width, self.height))
        overlay_surface.set_alpha(200)
        overlay_surface.fill((0, 0, 0))
        surface.blit(overlay_surface, (0, 0))
        
        # Message text (centered, above buttons)
        message_surface = self.font_title.render(
            self.message,
            True,
            GameConfig.COLOR_PRIMARY
        )
        message_rect = message_surface.get_rect(
            center=(self.width // 2, self.height // 2 - 50)
        )
        surface.blit(message_surface, message_rect)
        
        # Render buttons
        self.accept_button.draw(surface, self.font_button)
        self.run_button.draw(surface, self.font_button)
        
        # Render reraise button (grayed out if at max level)
        if self.can_reraise:
            self.reraise_button.draw(surface, self.font_button)
        else:
            # Draw in darker color to indicate disabled
            color_backup = self.reraise_button.hovered
            self.reraise_button.hovered = False
            pygame.draw.rect(surface, GameConfig.COLOR_TEXT_MUTED, self.reraise_button.rect, 2)
            text = self.font_button.render("AUMENTAR", True, GameConfig.COLOR_TEXT_MUTED)
            text_rect = text.get_rect(center=self.reraise_button.rect.center)
            surface.blit(text, text_rect)
