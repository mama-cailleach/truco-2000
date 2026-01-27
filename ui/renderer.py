"""
Rendering Pipeline for Pygame.

High-level rendering methods for game state visualization.
Coordinates with adapter snapshots to draw all game elements.
"""

import pygame
from typing import List, Dict, Any, Optional
from config import GameConfig
from ui.widgets.card_display import CardDisplay


class Renderer:
    """Handles all rendering for the game state."""

    def __init__(self, surface: pygame.Surface, font: pygame.font.Font):
        """
        Initialize the renderer.
        
        Args:
            surface: Pygame surface to render onto
            font: Default font for text rendering
        """
        self.surface = surface
        self.font = font
        self.screen_width = GameConfig.WINDOW_WIDTH
        self.screen_height = GameConfig.WINDOW_HEIGHT

    def render_game_state(self, snapshot: Dict[str, Any]) -> List[CardDisplay]:
        """
        Render the entire game state from a snapshot.
        
        Layout:
        - Top 20%: Opponent area
        - Middle 30%: Battle zone
        - Bottom 50%: Player hand + sidebar
        
        Args:
            snapshot: Game state snapshot from adapter
            
        Returns:
            List of CardDisplay objects for click detection
        """
        # Calculate layout regions
        opponent_height = int(self.screen_height * 0.20)
        battle_height = int(self.screen_height * 0.50)  # Battle zone now 50%
        player_height = self.screen_height - opponent_height - battle_height  # Hand now 30%
        
        # Render each region
        self.render_opponent_area(snapshot, 0, opponent_height)
        self.render_battle_zone(snapshot, opponent_height, battle_height)
        card_displays = self.render_player_area(snapshot, opponent_height + battle_height, player_height)
        
        return card_displays

    def render_opponent_area(self, snapshot: Dict[str, Any], y_offset: int, height: int) -> None:
        """
        Render opponent's area (top 20%).
        
        Args:
            snapshot: Game state snapshot
            y_offset: Y position to start rendering
            height: Height of this region
        """
        # Draw region background
        region_rect = pygame.Rect(10, y_offset + 10, self.screen_width - 20, height - 20)
        pygame.draw.rect(self.surface, GameConfig.COLOR_BACKGROUND_DARK, region_rect)
        # Green border
        pygame.draw.rect(self.surface, GameConfig.COLOR_SECONDARY, region_rect, 2)
        
        # Render opponent name and card count
        opponent_name = snapshot.get("opponent_name", "Oponente")
        opponent_cards = snapshot.get("opponent_card_count", 0)
        
        text = f"{opponent_name} - {opponent_cards} cartas"
        text_surface = self.font.render(text, True, GameConfig.COLOR_TEXT)
        text_rect = text_surface.get_rect(center=(self.screen_width // 3, y_offset + height // 2))
        self.surface.blit(text_surface, text_rect)

    def render_battle_zone(self, snapshot: Dict[str, Any], y_offset: int, height: int) -> None:
        """
        Render battle zone (middle 30%).
        
        Args:
            snapshot: Game state snapshot
            y_offset: Y position to start rendering
            height: Height of this region
        """
        # Draw region background with green border
        region_rect = pygame.Rect(10, y_offset + 10, self.screen_width - 270, height - 20)
        pygame.draw.rect(self.surface, GameConfig.COLOR_BACKGROUND, region_rect)
        # Green border for battle zone
        pygame.draw.rect(self.surface, GameConfig.COLOR_SECONDARY, region_rect, 2)
        
        battle_data = snapshot.get("battle", {})
        player_card = battle_data.get("player_card")
        opponent_card = battle_data.get("opponent_card")
        
        center_x = (self.screen_width - 260) // 2
        center_y = y_offset + height // 2
        
        # Render opponent's played card (top right)
        if opponent_card:
            card_display = CardDisplay(opponent_card, (center_x + 20, center_y - 160))
            card_display.draw(self.surface, self.font)
        
        # Render player's played card (bottom left)
        if player_card:
            card_display = CardDisplay(player_card, (center_x - 120, center_y + 10))
            card_display.draw(self.surface, self.font)
        
        # Show current round info
        round_num = snapshot.get("current_round", 1)
        round_text = f"Rodada {round_num}/3"
        text_surface = self.font.render(round_text, True, GameConfig.COLOR_TEXT)
        self.surface.blit(text_surface, (20, y_offset + 20))

    def render_player_area(self, snapshot: Dict[str, Any], y_offset: int, height: int) -> List[CardDisplay]:
        """
        Render player area (bottom 50%): hand + sidebar.
        
        Args:
            snapshot: Game state snapshot
            y_offset: Y position to start rendering
            height: Height of this region
            
        Returns:
            List of CardDisplay objects for click detection
        """
        # Split into hand (left) and sidebar (right 250px)
        hand_width = self.screen_width - 260
        sidebar_width = 250
        
        # Draw hand background with green border
        hand_rect = pygame.Rect(10, y_offset + 10, hand_width - 20, height - 20)
        pygame.draw.rect(self.surface, GameConfig.COLOR_BACKGROUND, hand_rect)
        pygame.draw.rect(self.surface, GameConfig.COLOR_SECONDARY, hand_rect, 2)
        
        # Draw sidebar background with green border (starts from top of screen)
        sidebar_rect = pygame.Rect(self.screen_width - 260, 10, sidebar_width, self.screen_height - 20)
        pygame.draw.rect(self.surface, GameConfig.COLOR_BACKGROUND_DARK, sidebar_rect)
        pygame.draw.rect(self.surface, GameConfig.COLOR_SECONDARY, sidebar_rect, 2)
        
        card_displays = self.render_hand(snapshot, 10, y_offset + 10, hand_width - 20, height - 20)
        self.render_sidebar(snapshot, self.screen_width - 260, 10, sidebar_width, self.screen_height - 20)
        
        return card_displays

    def render_hand(self, snapshot: Dict[str, Any], x: int, y: int, width: int, height: int) -> List[CardDisplay]:
        """
        Render player's hand.
        
        Args:
            snapshot: Game state snapshot
            x: X position
            y: Y position
            width: Width of hand area
            height: Height of hand area
            
        Returns:
            List of CardDisplay objects for click detection
        """
        hand_data = snapshot.get("hand", [])
        card_displays = []
        
        if not hand_data:
            # No cards message
            text = "Aguardando cartas..."
            text_surface = self.font.render(text, True, GameConfig.COLOR_TEXT_MUTED)
            text_rect = text_surface.get_rect(center=(width // 2, y + height // 2))
            self.surface.blit(text_surface, text_rect)
            return card_displays
        
        # Calculate card positions (center them horizontally)
        num_cards = len(hand_data)
        card_spacing = 120
        total_width = num_cards * 100 + (num_cards - 1) * card_spacing
        start_x = x + (width - total_width) // 2
        card_y = y + (height - 140) // 2
        
        for i, card_code in enumerate(hand_data):
            card_x = start_x + i * (100 + card_spacing)
            card_display = CardDisplay(card_code, (card_x, card_y))
            card_display.draw(self.surface, self.font)
            card_displays.append(card_display)
        
        return card_displays

    def render_sidebar(self, snapshot: Dict[str, Any], x: int, y: int, width: int, height: int) -> None:
        """
        Render sidebar with game info.
        
        Args:
            snapshot: Game state snapshot
            x: X position
            y: Y position
            width: Width of sidebar
            height: Height of sidebar
        """
        sidebar_data = snapshot.get("sidebar", {})
        
        # Render sidebar info
        y_pos = y + 20
        line_height = 35
        
        # Title
        title = "PLACAR"
        text_surface = self.font.render(title, True, GameConfig.COLOR_PRIMARY)
        self.surface.blit(text_surface, (x + 20, y_pos))
        y_pos += line_height + 10
        
        # Player score
        player_score = sidebar_data.get("player_score", 0)
        text = f"Voce: {player_score}"
        text_surface = self.font.render(text, True, GameConfig.COLOR_PRIMARY)
        self.surface.blit(text_surface, (x + 20, y_pos))
        y_pos += line_height
        
        # Opponent score
        opponent_score = sidebar_data.get("opponent_score", 0)
        text = f"Oponente: {opponent_score}"
        text_surface = self.font.render(text, True, GameConfig.COLOR_DANGER)
        self.surface.blit(text_surface, (x + 20, y_pos))
        y_pos += line_height * 2
        
        # Truco value
        truco_value = sidebar_data.get("truco_value", 1)
        truco_name = sidebar_data.get("truco_name", "Normal")
        text = f"Valor: {truco_value}"
        text_surface = self.font.render(text, True, GameConfig.COLOR_TEXT)
        self.surface.blit(text_surface, (x + 20, y_pos))
        y_pos += line_height
        
        text = f"({truco_name})"
        text_surface = self.font.render(text, True, GameConfig.COLOR_TEXT_MUTED)
        self.surface.blit(text_surface, (x + 20, y_pos))
        y_pos += line_height * 2
        
        # Manilha
        manilha = sidebar_data.get("manilha", "?")
        text = f"Manilha: {manilha}"
        text_surface = self.font.render(text, True, GameConfig.COLOR_TEXT)
        self.surface.blit(text_surface, (x + 20, y_pos))
