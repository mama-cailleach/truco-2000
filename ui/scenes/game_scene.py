"""
Game Scene - Main gameplay screen.

Displays game state using the renderer pipeline.
Integrates with GameController via adapter snapshots.
"""

import pygame
from ui.scenes.base_scene import BaseScene
from ui.renderer import Renderer
from ui.adapter import snapshot_from_controller
from ui.widgets.truco_overlay import TrucoOverlay
from config import GameConfig


class GameScene(BaseScene):
    """
    Main game scene.
    
    Displays the game board using:
    - Top 20%: Opponent area
    - Middle 50%: Battle zone (played cards)
    - Bottom 30%: Player hand + sidebar
    """
    
    def on_enter(self) -> None:
        """Initialize the game scene."""
        self.font_normal = pygame.font.Font(None, GameConfig.FONT_SIZE_NORMAL)
        self.renderer = Renderer(self.app.screen, self.font_normal)
        
        # Truco overlay
        self.truco_overlay = TrucoOverlay(self.app.width, self.app.height)
        self.showing_truco_overlay = False
        self.pending_truco_data = None
        
        # Track card displays for click detection (will be populated by renderer)
        self.card_displays = []
        
        # Game flow state
        self.selected_card_index = None
        self.waiting_for_opponent = False
        self.waiting_for_ai_truco_response = False
        self.showing_round_result = False
        self.result_timer = 0
        self.round_result_text = ""
        
        # Start a new hand
        self.app.controller.start_new_hand()
        
        # Get initial snapshot
        self.snapshot = self._get_snapshot()
        
    def on_exit(self) -> None:
        """Clean up game scene."""
        pass
    
    def _get_snapshot(self) -> dict:
        """Get current game state snapshot from controller."""
        try:
            return snapshot_from_controller(self.app.controller)
        except Exception:
            # Fallback to empty state
            return {
                "opponent_name": "Oponente",
                "opponent_card_count": 0,
                "hand": [],
                "battle": {"player_card": None, "opponent_card": None},
                "current_round": 1,
                "sidebar": {
                    "player_score": 0,
                    "opponent_score": 0,
                    "truco_value": 1,
                    "truco_name": "Normal",
                    "manilha": "?"
                },
                "player_starts_round": True,
                "player_starts_hand": True,
                "pending_truco": None,
                "round_results": []
            }
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle game scene events."""
        # If truco overlay is showing, handle it first
        if self.showing_truco_overlay:
            action = self.truco_overlay.handle_event(event)
            if action:
                self._handle_truco_response(action)
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Return to menu
                from ui.scenes.menu_scene import MenuScene
                self.app.replace_scene(MenuScene(self.app))
            
            elif event.key == pygame.K_t:
                # Player calls truco (T key)
                self._player_calls_truco()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # Don't allow card clicks if waiting or showing results
                if self.waiting_for_opponent or self.showing_round_result:
                    return
                
                # Check if both players have played (need to resolve)
                battle = self.snapshot.get("battle", {})
                
                if battle.get("player_card") and battle.get("opponent_card"):
                    # Click anywhere to resolve round
                    self._resolve_round()
                    return
                
                # Check if it's player's turn
                if not self._is_player_turn():
                    return
                
                # Check if user clicked on a card
                mouse_pos = event.pos
                for i, card_display in enumerate(self.card_displays):
                    if card_display.get_rect().collidepoint(mouse_pos):
                        self._on_card_clicked(i)
                        break
    
    def _is_player_turn(self) -> bool:
        """Check if it's the player's turn to play."""
        battle = self.snapshot.get("battle", {})
        player_starts = self.snapshot.get("player_starts_round", True)
        
        # If player starts and hasn't played yet
        if player_starts and not battle.get("player_card"):
            return True
        
        # If opponent starts, played, and player hasn't played yet
        if not player_starts and battle.get("opponent_card") and not battle.get("player_card"):
            return True
        
        return False
    
    def _on_card_clicked(self, card_index: int) -> None:
        """Handle card click - player plays a card."""
        # Check who started this round BEFORE playing
        player_started = self.snapshot.get("player_starts_round", True)
        
        # Play the card
        self.snapshot = self.app.controller.play_player_card(card_index)
        
        # Only trigger opponent to play if PLAYER started this round
        # (if opponent started, they already played)
        if player_started:
            self.waiting_for_opponent = True
    
    def _opponent_plays(self) -> None:
        """Opponent plays their card."""
        self.snapshot = self.app.controller.play_opponent_card()
        self.waiting_for_opponent = False
    
    def _player_calls_truco(self) -> None:
        """Handle player calling truco (T key)."""
        # Check if truco can be called (not while cards are being played, etc.)
        if self.waiting_for_opponent or self.showing_round_result or self.showing_truco_overlay:
            return
        
        self.snapshot = self.app.controller.call_truco("Jogador")
        pending = self.snapshot.get("pending_truco")
        
        if pending:
            # Show truco overlay with opponent response options
            self.truco_overlay.set_message(
                "Você",
                pending["name"],
                pending.get("can_reraise", True)
            )
            # Wait for AI response
            self.waiting_for_ai_truco_response = True
            self.showing_truco_overlay = True  # Show immediately!
    
    def _handle_truco_response(self, action: str) -> None:
        """Handle player response to opponent's truco call."""
        if self.pending_truco_data:
            caller = self.pending_truco_data["caller"]
            value = self.pending_truco_data["value"]
            self.snapshot = self.app.controller.respond_to_truco(action, caller, value)
            
            # Check if hand ended due to running
            truco_result = self.snapshot.get("truco_result")
            if truco_result and truco_result.get("action") == "run":
                self.hand_active = False
                # Show hand ended message (can add overlay later)
            
            self.showing_truco_overlay = False
            self.pending_truco_data = None
    
    def _resolve_round(self) -> None:
        """Resolve the current round and determine winner."""
        self.snapshot = self.app.controller.resolve_round()
        
        # Show round result
        round_results = self.snapshot.get("round_results", [])
        if round_results:
            last_result = round_results[-1]
            if last_result == "Empate":
                self.round_result_text = "EMPATE!"
            elif last_result == "Jogador":
                self.round_result_text = "VOCÊ VENCEU A RODADA!"
            else:
                self.round_result_text = "OPONENTE VENCEU A RODADA!"
            
            self.showing_round_result = True
            self.result_timer = 2.0  # Show for 2 seconds
        
        # Check if hand is over
        if not self.snapshot.get("hand_active"):
            # Hand ended, check for game winner
            scores = self.snapshot.get("scores", {})
            if scores.get("player") >= 12 or scores.get("opponent") >= 12:
                # Game over - transition to results scene
                self._show_game_results()
            else:
                # Start a new hand
                self.app.controller.start_new_hand()
                self.snapshot = self._get_snapshot()
    
    def update(self, delta_time: float) -> None:
        """Update game scene."""
        # Refresh snapshot each frame (for live game state), but NOT during truco overlay
        if not self.showing_truco_overlay and not self.waiting_for_ai_truco_response:
            self.snapshot = self._get_snapshot()
        
        # Update button hover states if truco overlay is showing
        if self.showing_truco_overlay:
            mouse_pos = pygame.mouse.get_pos()
            self.truco_overlay.update(mouse_pos)
        
        # Handle AI truco response
        if self.waiting_for_ai_truco_response:
            pending = self.snapshot.get("pending_truco")
            if pending:
                value = pending["value"]
                ai_response = self.app.controller.ai_truco_response(value)
                
                # Show the overlay for opponent's response
                opponent_name = self.snapshot.get("opponent_name", "Oponente")
                self.truco_overlay.set_message(
                    opponent_name,
                    pending["name"],
                    pending.get("can_reraise", True)
                )
                self.showing_truco_overlay = True
                self.pending_truco_data = pending
                self.pending_truco_data["caller"] = "Oponente"
                
                # Simulate "opponent thinking" - respond after a short delay
                if not hasattr(self, "ai_response_timer"):
                    self.ai_response_timer = 1.0  # 1 second to think
                else:
                    self.ai_response_timer -= delta_time
                    if self.ai_response_timer <= 0:
                        # Actually handle the response
                        self._handle_truco_response(ai_response)
                        self.waiting_for_ai_truco_response = False
                        del self.ai_response_timer
        
        # Handle opponent turn with delay
        if self.waiting_for_opponent:
            self._opponent_plays()
        
        # Handle round result display timer
        if self.showing_round_result:
            self.result_timer -= delta_time
            if self.result_timer <= 0:
                self.showing_round_result = False
                # Check if opponent should start next round AND hasn't played yet
                battle = self.snapshot.get("battle", {})
                if not self.snapshot.get("player_starts_round") and not battle.get("opponent_card"):
                    self.waiting_for_opponent = True
    
    def _show_game_results(self) -> None:
        """Transition to results scene (placeholder for Phase 5)."""
        print("[TODO] Game over - transition to results scene")
        # For now, return to menu
        from ui.scenes.menu_scene import MenuScene
        self.app.replace_scene(MenuScene(self.app))
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the game scene."""
        # Use renderer to draw the entire game state and get card displays
        self.card_displays = self.renderer.render_game_state(self.snapshot)
        
        # Overlay truco if showing
        if self.showing_truco_overlay:
            self.truco_overlay.render(surface)
        
        # Overlay round result if showing
        if self.showing_round_result:
            self._render_round_result_overlay(surface)
    
    def _render_round_result_overlay(self, surface: pygame.Surface) -> None:
        """Render round result overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.app.width, self.app.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Result text
        font_large = pygame.font.Font(None, GameConfig.FONT_SIZE_TITLE)
        text_surface = font_large.render(
            self.round_result_text,
            True,
            GameConfig.COLOR_PRIMARY
        )
        text_rect = text_surface.get_rect(center=(self.app.width // 2, self.app.height // 2))
        surface.blit(text_surface, text_rect)
