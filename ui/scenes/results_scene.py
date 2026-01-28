"""
Results Scene - Displays hand/match results and handles transitions.

Shows:
- Hand winner and points awarded
- Cumulative scores
- Next hand button or match winner
"""

import pygame
from ui.scenes.base_scene import BaseScene
from ui.widgets.button import Button
from ui.renderer import Renderer
from ui.adapter import snapshot_from_controller
from config import GameConfig


class ResultsScene(BaseScene):
    """
    Results screen shown after each hand ends.
    
    Displays hand winner, points awarded, and cumulative scores.
    Allows progression to next hand or return to menu if match is complete.
    """
    
    def __init__(self, app, hand_winner: str, points_awarded: int, match_active: bool):
        """
        Initialize results scene.
        
        Args:
            app: PygameApp instance
            hand_winner: "Jogador" or "Oponente"
            points_awarded: Points for winning the hand
            match_active: True if match continues, False if match over
        """
        super().__init__(app)
        self.hand_winner = hand_winner
        self.points_awarded = points_awarded
        self.match_active = match_active
        self.snapshot = None
        
    def on_enter(self) -> None:
        """Initialize results scene."""
        print(f"[DEBUG] ResultsScene.on_enter() called")
        print(f"[DEBUG] hand_winner={self.hand_winner}, points={self.points_awarded}, match_active={self.match_active}")
        
        self.font_title = pygame.font.Font(None, GameConfig.FONT_SIZE_TITLE)
        self.font_large = pygame.font.Font(None, GameConfig.FONT_SIZE_LARGE)
        self.font_normal = pygame.font.Font(None, GameConfig.FONT_SIZE_NORMAL)
        self.renderer = Renderer(self.app.screen, self.font_normal)
        
        # Get current game state
        self.snapshot = snapshot_from_controller(self.app.controller)
        print(f"[DEBUG] Snapshot obtained, scores: {self.snapshot.get('scores')}")
        
        # Create buttons based on match state
        self._create_buttons()
        print(f"[DEBUG] ResultsScene.on_enter() completed")
        
    def _create_buttons(self) -> None:
        """Create navigation buttons based on match state."""
        button_width = 200
        button_height = 50
        button_y = self.app.height - 100
        
        if self.match_active:
            # Match continues - show "Next Hand" button
            btn_rect = pygame.Rect(self.app.width // 2 - button_width // 2, button_y, button_width, button_height)
            self.next_button = Button("Próxima Mão", btn_rect, "next_hand")
        else:
            # Match over - show "Play Again" and "Menu" buttons
            btn_width_small = 150
            spacing = 30
            total_width = (btn_width_small * 2) + spacing
            start_x = (self.app.width - total_width) // 2
            
            self.again_button = Button("Jogar Novamente", 
                                      pygame.Rect(start_x, button_y, btn_width_small, button_height),
                                      "play_again")
            self.menu_button = Button("Menu", 
                                     pygame.Rect(start_x + btn_width_small + spacing, button_y, btn_width_small, button_height),
                                     "menu")
    
    def on_exit(self) -> None:
        """Clean up results scene."""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle scene events."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Return to menu
                from ui.scenes.menu_scene import MenuScene
                self.app.replace_scene(MenuScene(self.app))
                return
            elif event.key == pygame.K_q:
                # Quit game
                from utils import safe_exit
                safe_exit()
                return
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.match_active:
                if self.next_button.handle_event(event):
                    self._start_next_hand()
            else:
                if self.again_button.handle_event(event):
                    self._play_again()
                elif self.menu_button.handle_event(event):
                    from ui.scenes.menu_scene import MenuScene
                    self.app.replace_scene(MenuScene(self.app))
    
    def update(self, delta_time: float) -> None:
        """Update scene state."""
        mouse_pos = pygame.mouse.get_pos()
        if self.match_active:
            self.next_button.update(mouse_pos)
        else:
            self.again_button.update(mouse_pos)
            self.menu_button.update(mouse_pos)
    
    def render(self, surface: pygame.Surface) -> None:
        """Render results screen."""
        # Clear background
        surface.fill(GameConfig.COLOR_BACKGROUND)
        
        # Get current scores from sidebar
        sidebar = self.snapshot.get("sidebar", {})
        player_score = sidebar.get("player_score", 0)
        opponent_score = sidebar.get("opponent_score", 0)
        
        # Render title
        if self.match_active:
            title_text = "FIM DA MÃO"
        else:
            title_text = "FIM DO JOGO"
        
        title_surface = self.font_title.render(title_text, True, GameConfig.COLOR_TEXT)
        title_rect = title_surface.get_rect(center=(self.app.width // 2, 50))
        surface.blit(title_surface, title_rect)
        
        # Render hand winner
        if self.hand_winner == "Jogador":
            winner_text = "VOCÊ VENCEU A MÃO!"
            winner_color = GameConfig.COLOR_SUCCESS
        else:
            winner_text = "OPONENTE VENCEU A MÃO!"
            winner_color = GameConfig.COLOR_ERROR
        
        winner_surface = self.font_large.render(winner_text, True, winner_color)
        winner_rect = winner_surface.get_rect(center=(self.app.width // 2, 120))
        surface.blit(winner_surface, winner_rect)
        
        # Render points awarded
        points_text = f"Pontos: {self.points_awarded}"
        points_surface = self.font_normal.render(points_text, True, GameConfig.COLOR_TEXT)
        points_rect = points_surface.get_rect(center=(self.app.width // 2, 180))
        surface.blit(points_surface, points_rect)
        
        # Render current scores
        scores_y = 260
        scores_title = "PLACAR ATUAL"
        scores_title_surface = self.font_large.render(scores_title, True, GameConfig.COLOR_TEXT)
        scores_title_rect = scores_title_surface.get_rect(center=(self.app.width // 2, scores_y))
        surface.blit(scores_title_surface, scores_title_rect)
        
        # Player score
        player_score_text = f"Você: {player_score}"
        player_score_surface = self.font_normal.render(player_score_text, True, GameConfig.COLOR_TEXT)
        player_score_rect = player_score_surface.get_rect(center=(self.app.width // 2, scores_y + 60))
        surface.blit(player_score_surface, player_score_rect)
        
        # Opponent score
        opponent_score_text = f"Oponente: {opponent_score}"
        opponent_score_surface = self.font_normal.render(opponent_score_text, True, GameConfig.COLOR_TEXT)
        opponent_score_rect = opponent_score_surface.get_rect(center=(self.app.width // 2, scores_y + 100))
        surface.blit(opponent_score_surface, opponent_score_rect)
        
        # If match is over, show match winner
        if not self.match_active:
            match_winner_y = scores_y + 180
            if player_score >= 12:
                match_winner_text = "VOCÊ VENCEU O JOGO!"
                match_winner_color = GameConfig.COLOR_SUCCESS
            else:
                match_winner_text = "OPONENTE VENCEU O JOGO!"
                match_winner_color = GameConfig.COLOR_ERROR
            
            match_winner_surface = self.font_large.render(match_winner_text, True, match_winner_color)
            match_winner_rect = match_winner_surface.get_rect(center=(self.app.width // 2, match_winner_y))
            surface.blit(match_winner_surface, match_winner_rect)
        
        # Render buttons
        if self.match_active:
            self.next_button.draw(surface, self.font_normal)
        else:
            self.again_button.draw(surface, self.font_normal)
            self.menu_button.draw(surface, self.font_normal)
    
    def _start_next_hand(self) -> None:
        """Start the next hand and return to game scene."""
        # Reset all truco state
        self.app.controller.truco.reset_truco_state()
        
        # Start new hand
        self.app.controller.start_new_hand()
        
        # Return to game scene
        from ui.scenes.game_scene import GameScene
        self.app.replace_scene(GameScene(self.app))
    
    def _play_again(self) -> None:
        """Start a new match."""
        # Reset game state
        self.app.controller.core.reset_game_state()
        self.app.controller.truco.reset_truco_state()
        self.app.controller.core.baralho = self.app.controller.core.baralho_original.copy()
        self.app.controller.core.embaralhar()
        self.app.controller.core.player_starts_hand = True
        
        # Reset controller state
        self.app.controller.hand_active = True
        self.app.controller.current_round = 1
        self.app.controller.round_results = []
        self.app.controller.played_cards = {"player": None, "opponent": None}
        
        # Start first hand
        self.app.controller.start_new_hand()
        
        # Return to game scene
        from ui.scenes.game_scene import GameScene
        self.app.replace_scene(GameScene(self.app))
