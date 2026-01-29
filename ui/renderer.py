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

    def render_game_state(self, snapshot: Dict[str, Any]) -> tuple:
        """
        Render the entire game state from a snapshot.
        
        Layout:
        - Top 20%: Opponent area
        - Middle 30%: Battle zone
        - Bottom 50%: Player hand + sidebar
        
        Args:
            snapshot: Game state snapshot from adapter
            
        Returns:
            Tuple of (card_displays list, button_rects dict)
        """
        # Calculate layout regions
        opponent_height = int(self.screen_height * 0.20)
        battle_height = int(self.screen_height * 0.50)  # Battle zone now 50%
        player_height = self.screen_height - opponent_height - battle_height  # Hand now 30%
        
        # Render each region
        self.render_opponent_area(snapshot, 0, opponent_height)
        self.render_battle_zone(snapshot, opponent_height, battle_height)
        card_displays, button_rects = self.render_player_area(snapshot, opponent_height + battle_height, player_height)
        
        return card_displays, button_rects

    def render_opponent_area(self, snapshot: Dict[str, Any], y_offset: int, height: int) -> None:
        """
        Render opponent's area (top 20%).
        
        Args:
            snapshot: Game state snapshot
            y_offset: Y position to start rendering
            height: Height of this region
        """
        # Draw region background with padding from sidebar (right margin: 300px for 250px sidebar + 20px gap + 30px margin)
        region_rect = pygame.Rect(10, y_offset + 10, self.screen_width - 300, height - 20)
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
        # Draw region background with green border (padding from sidebar: 300px)
        region_rect = pygame.Rect(10, y_offset + 10, self.screen_width - 300, height - 20)
        pygame.draw.rect(self.surface, GameConfig.COLOR_BACKGROUND, region_rect)
        # Green border for battle zone
        pygame.draw.rect(self.surface, GameConfig.COLOR_SECONDARY, region_rect, 2)
        
        battle_data = snapshot.get("battle", {})
        player_card = battle_data.get("player_card")
        opponent_card = battle_data.get("opponent_card")
        
        center_x = (self.screen_width - 300) // 2
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

    def render_player_area(self, snapshot: Dict[str, Any], y_offset: int, height: int) -> tuple:
        """
        Render player area (bottom 50%): hand + sidebar.
        
        Args:
            snapshot: Game state snapshot
            y_offset: Y position to start rendering
            height: Height of this region
            
        Returns:
            Tuple of (card_displays list, button_rects dict)
        """
        # Sidebar dimensions
        sidebar_width = 250
        sidebar_x = self.screen_width - 270  # 20px gap from right edge
        
        # Draw hand background with green border (FULL WIDTH)
        hand_rect = pygame.Rect(10, y_offset + 10, self.screen_width - 20, height - 20)
        pygame.draw.rect(self.surface, GameConfig.COLOR_BACKGROUND, hand_rect)
        pygame.draw.rect(self.surface, GameConfig.COLOR_SECONDARY, hand_rect, 2)
        
        # Draw sidebar background with green border (ends BEFORE player hand box)
        # Sidebar height should end at y_offset (where player hand starts)
        sidebar_height = y_offset - 20  # Leave 10px margin at top and bottom
        sidebar_rect = pygame.Rect(sidebar_x, 10, sidebar_width, sidebar_height)
        pygame.draw.rect(self.surface, GameConfig.COLOR_BACKGROUND_DARK, sidebar_rect)
        pygame.draw.rect(self.surface, GameConfig.COLOR_SECONDARY, sidebar_rect, 2)
        
        card_displays, button_rects = self.render_hand(snapshot, 10, y_offset + 10, self.screen_width - 20, height - 20)
        self.render_sidebar(snapshot, sidebar_x, 10, sidebar_width, sidebar_height)
        
        return card_displays, button_rects

    def render_hand(self, snapshot: Dict[str, Any], x: int, y: int, width: int, height: int) -> tuple:
        """
        Render player's hand with cards on left/center and action buttons on right.
        
        Args:
            snapshot: Game state snapshot
            x: X position
            y: Y position
            width: Width of hand area
            height: Height of hand area
            
        Returns:
            Tuple of (card_displays list, button_rects dict)
        """
        hand_data = snapshot.get("hand", [])
        card_displays = []
        
        # Reserve space for action buttons on the right (170px width + margins)
        action_button_area_width = 170
        # Reserve space for game control buttons below (3 columns x 50px = 150px + margins)
        game_button_area_width = 180
        # Cards area is what remains
        cards_area_width = width - action_button_area_width - game_button_area_width
        
        # Render action buttons (Truco, Esconder, Fugir)
        action_button_rects = self._render_action_buttons(x + cards_area_width, y, action_button_area_width, height)
        
        # Render game control buttons (Menu, Opções, Sair)
        game_button_rects = self._render_game_control_buttons(x + cards_area_width + action_button_area_width, y, game_button_area_width, height)
        
        # Combine button rects
        button_rects = {**action_button_rects, **game_button_rects}
        
        if not hand_data:
            # No cards message
            text = "Aguardando cartas..."
            text_surface = self.font.render(text, True, GameConfig.COLOR_TEXT_MUTED)
            text_rect = text_surface.get_rect(center=(cards_area_width // 2, y + height // 2))
            self.surface.blit(text_surface, text_rect)
            return card_displays, button_rects
        
        # Calculate card positions (center them in available space)
        num_cards = len(hand_data)
        card_width = 100
        card_padding = 30  # Padding between cards
        total_cards_width = num_cards * card_width + (num_cards - 1) * card_padding
        
        # Center cards in the available area
        start_x = x + (cards_area_width - total_cards_width) // 2
        card_y = y + (height - 140) // 2
        
        for i, card_code in enumerate(hand_data):
            card_x = start_x + i * (card_width + card_padding)
            card_display = CardDisplay(card_code, (card_x, card_y))
            card_display.draw(self.surface, self.font)
            card_displays.append(card_display)
        
        return card_displays, button_rects
    
    def _render_action_buttons(self, x: int, y: int, width: int, height: int) -> Dict[str, pygame.Rect]:
        """
        Render action buttons (Truco, Esconder, Fugir) on the right side of hand area.
        
        Args:
            x: X position
            y: Y position  
            width: Width of button area
            height: Height of button area
            
        Returns:
            Dict mapping button names to their rects
        """
        button_width = 140
        button_height = 45
        button_spacing = 20
        
        # Center buttons vertically in the hand area
        total_buttons_height = 3 * button_height + 2 * button_spacing
        start_y = y + (height - total_buttons_height) // 2
        button_x = x + (width - button_width) // 2
        
        buttons = [
            ("TRUCO", (20, 20, 25)),      # Card background color
            ("ESCONDER", (20, 20, 25)),   # Card background color
            ("FUGIR", (20, 20, 25))       # Card background color
        ]
        
        button_rects = {}
        
        for i, (label, color) in enumerate(buttons):
            button_y = start_y + i * (button_height + button_spacing)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Draw button background
            pygame.draw.rect(self.surface, color, button_rect)
            pygame.draw.rect(self.surface, GameConfig.COLOR_TEXT, button_rect, 2)
            
            # Draw button text
            text_surface = self.font.render(label, True, GameConfig.COLOR_TEXT)
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.surface.blit(text_surface, text_rect)
            
            button_rects[label.lower()] = button_rect
        
        return button_rects
    
    def _render_game_control_buttons(self, x: int, y: int, width: int, height: int) -> Dict[str, pygame.Rect]:
        """
        Render game control buttons (Menu, Opções, Sair) on the far right side.
        
        Args:
            x: X position
            y: Y position  
            width: Width of button area
            height: Height of button area
            
        Returns:
            Dict mapping button names to their rects
        """
        button_width = 140
        button_height = 45
        button_spacing = 20
        
        # Center buttons vertically in the hand area
        total_buttons_height = 3 * button_height + 2 * button_spacing
        start_y = y + (height - total_buttons_height) // 2
        button_x = x + (width - button_width) // 2
        
        buttons = [
            ("MENU", (20, 20, 25)),      # Card background color
            ("OPÇÕES", (20, 20, 25)),    # Card background color
            ("SAIR", (20, 20, 25))       # Card background color
        ]
        
        button_rects = {}
        
        for i, (label, color) in enumerate(buttons):
            button_y = start_y + i * (button_height + button_spacing)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Draw button background
            pygame.draw.rect(self.surface, color, button_rect)
            pygame.draw.rect(self.surface, GameConfig.COLOR_TEXT, button_rect, 2)
            
            # Draw button text
            text_surface = self.font.render(label, True, GameConfig.COLOR_TEXT)
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.surface.blit(text_surface, text_rect)
            
            button_rects[label.lower()] = button_rect
        
        return button_rects

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
        
        # Player score and Opponent score (single line)
        player_score = sidebar_data.get("player_score", 0)
        opponent_score = sidebar_data.get("opponent_score", 0)
        opponent_name = sidebar_data.get("opponent_name", "Oponente")
        text = f"Voce {player_score} x {opponent_score} {opponent_name}"
        text_surface = self.font.render(text, True, GameConfig.COLOR_PRIMARY)
        self.surface.blit(text_surface, (x + 20, y_pos))
        y_pos += line_height * 2
        
        # Truco value
        truco_value = sidebar_data.get("truco_value", 1)
        text = f"Valor: {truco_value}"
        text_surface = self.font.render(text, True, GameConfig.COLOR_TEXT)
        self.surface.blit(text_surface, (x + 20, y_pos))
        y_pos += line_height * 2
        
        # Vira
        vira = sidebar_data.get("vira", "?")
        # Convert suit symbols like CardDisplay does
        suit_map = {
            '♠': 'P',  # Paus (Spades)
            '♥': 'C',  # Copas (Hearts)
            '♦': 'O',  # Ouros (Diamonds)
            '♣': 'Z'   # Zap (Clubs)
        }
        vira_display = vira
        if len(vira) > 1:
            rank = vira[:-1]
            suit_symbol = vira[-1]
            suit = suit_map.get(suit_symbol, suit_symbol)
            vira_display = f"{rank}{suit}"
        text = f"Vira: {vira_display}"
        text_surface = self.font.render(text, True, GameConfig.COLOR_TEXT)
        self.surface.blit(text_surface, (x + 20, y_pos))
        y_pos += line_height
        
        # Manilha
        manilha = sidebar_data.get("manilha", "?")
        text = f"Manilha: {manilha}"
        text_surface = self.font.render(text, True, GameConfig.COLOR_TEXT)
        self.surface.blit(text_surface, (x + 20, y_pos))
