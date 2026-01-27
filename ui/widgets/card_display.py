"""
Card Display Widget for Pygame.

Renders individual cards with ASCII art or graphical representation.
Supports selection/hover states.
"""

import pygame
from typing import Optional, List
from config import GameConfig


class CardDisplay:
    """Renders a single card with ASCII representation."""

    def __init__(self, card_code: Optional[str], position: tuple, selected: bool = False, hovered: bool = False):
        """
        Initialize a card display.
        
        Args:
            card_code: Card code like "A♠", "7♥", etc. (None for no card)
            position: (x, y) top-left position
            selected: Whether this card is currently selected
            hovered: Whether this card is hovered
        """
        self.card_code = card_code
        self.position = position
        self.selected = selected
        self.hovered = hovered
        self.width = 100
        self.height = 140

    def get_rect(self) -> pygame.Rect:
        """Get the bounding rectangle for click detection."""
        return pygame.Rect(self.position[0], self.position[1], self.width, self.height)

    def render_ascii_lines(self) -> List[str]:
        """Generate display text for the card."""
        if not self.card_code:
            return [""]
        
        rank = self.card_code[:-1]
        suit_symbol = self.card_code[-1]
        
        # Convert Unicode suit symbols to ASCII-safe characters
        suit_map = {
            '♠': 'P',  # Paus (Spades)
            '♥': 'C',  # Copas (Hearts)
            '♦': 'O',  # Ouros (Diamonds)
            '♣': 'Z'   # Zap (Clubs)
        }
        suit = suit_map.get(suit_symbol, suit_symbol)
        
        return [f"{rank}{suit}"]

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw the card to the surface."""
        x, y = self.position
        
        # Background color based on state
        if self.selected:
            bg_color = GameConfig.COLOR_BUTTON_PRESSED
        elif self.hovered:
            bg_color = GameConfig.COLOR_BUTTON_HOVER
        else:
            bg_color = (20, 20, 25)  # Slightly lighter than background for card
        
        # Draw background
        pygame.draw.rect(surface, bg_color, (x, y, self.width, self.height))
        
        # Draw border
        border_color = GameConfig.COLOR_PRIMARY if (self.selected or self.hovered) else GameConfig.COLOR_SECONDARY
        pygame.draw.rect(surface, border_color, (x, y, self.width, self.height), 3)
        
        # Render card text centered
        lines = self.render_ascii_lines()
        if lines and lines[0]:
            # Use larger font for card
            large_font = pygame.font.Font(None, 48)
            text_surface = large_font.render(lines[0], True, GameConfig.COLOR_TEXT)
            text_rect = text_surface.get_rect(center=(x + self.width // 2, y + self.height // 2))
            surface.blit(text_surface, text_rect)
