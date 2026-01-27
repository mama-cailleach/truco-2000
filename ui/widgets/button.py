"""
Simple Pygame Button widget.

Handles hover state, click detection, and drawing.
"""

import pygame
from typing import Tuple
from config import GameConfig


class Button:
    def __init__(self, label: str, rect: pygame.Rect, action: str):
        self.label = label
        self.rect = rect
        self.action = action
        self.hovered = False

    def update(self, mouse_pos: Tuple[int, int]) -> None:
        self.hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        color = GameConfig.COLOR_BUTTON_HOVER if self.hovered else GameConfig.COLOR_PRIMARY
        pygame.draw.rect(surface, color, self.rect, 2)
        text = font.render(self.label, True, color)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
