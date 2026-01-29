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
        self.button_rects = {}  # Button click detection
        
        # Game flow state
        self.selected_card_index = None
        self.waiting_for_opponent = False
        self.waiting_for_ai_truco_response = False
        self.showing_player_truco_call = False  # Show "Você pediu Truco"
        self.showing_ai_truco_result = False  # Show AI decision result
        self.showing_opponent_fugir = False
        self.showing_round_result = False
        self.result_timer = 0
        self.round_result_text = ""
        self.ai_truco_decision = None  # Store AI decision
        self.pending_hand_results = None  # Store hand results for delayed transition
        
        # Check if this is the first hand (hand_active might not exist yet)
        if not hasattr(self.app.controller, 'hand_active') or not self.app.controller.hand_active:
            # First hand or transitioning from results - start new hand
            self.app.controller.start_new_hand()
        
        # Get initial snapshot
        self.snapshot = self._get_snapshot()
        
        # Check if opponent should play first
        if not self.snapshot.get("player_starts_round"):
            print("[DEBUG] Opponent starts round, triggering opponent play")
            self.waiting_for_opponent = True
        
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
                # Check if user clicked on a button first
                mouse_pos = event.pos
                for button_name, button_rect in self.button_rects.items():
                    if button_rect.collidepoint(mouse_pos):
                        self._handle_button_click(button_name)
                        return
                
                # Don't allow card clicks if waiting or showing results or during truco
                if (self.waiting_for_opponent or self.showing_round_result or 
                    self.showing_player_truco_call or self.showing_ai_truco_result):
                    print(f"[DEBUG] Card click blocked - waiting_for_opponent: {self.waiting_for_opponent}, "
                          f"showing_round_result: {self.showing_round_result}, "
                          f"showing_player_truco_call: {self.showing_player_truco_call}, "
                          f"showing_ai_truco_result: {self.showing_ai_truco_result}")
                    return
                
                # Check if both players have played (need to resolve)
                battle = self.snapshot.get("battle", {})
                
                if battle.get("player_card") and battle.get("opponent_card"):
                    # Click anywhere to resolve round
                    self._resolve_round()
                    return
                
                # Check if it's player's turn
                if not self._is_player_turn():
                    print(f"[DEBUG] Not player's turn - _is_player_turn returned False")
                    return
                
                # Check if user clicked on a card
                mouse_pos = event.pos
                print(f"[DEBUG] Card click at {mouse_pos}, num card displays: {len(self.card_displays)}")
                for i, card_display in enumerate(self.card_displays):
                    if card_display.get_rect().collidepoint(mouse_pos):
                        print(f"[DEBUG] Card {i} clicked")
                        self._on_card_clicked(i)
                        break
                else:
                    print(f"[DEBUG] Click didn't hit any card")
    
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
        """Opponent plays their card or decides to fugir."""
        # Check if opponent should fugir (give up hand) because they're losing
        vitorias_jogador = self.snapshot.get("round_results", []).count("Jogador")
        vitorias_oponente = self.snapshot.get("round_results", []).count("Oponente")
        
        if self.app.controller.truco.should_opponent_fugir(None, None, vitorias_jogador, vitorias_oponente):
            # Opponent gives up the hand
            print("[DEBUG] Opponent decided to fugir!")
            hand_results = self.app.controller.opponent_fugir()
            
            # Check if match is over
            match_info = self.app.controller.check_match_winner()
            match_active = not match_info['match_over']

            # Store results for delayed transition
            self.pending_hand_results = {
                "hand_winner": hand_results['hand_winner'],
                "points_awarded": hand_results['points_awarded'],
                "match_active": match_active
            }

            # Show fugir overlay
            self.showing_opponent_fugir = True
            self.result_timer = 2.0
            return
        
        # Random chance for opponent to call truco before playing
        import random
        if random.random() < 0.15:  # 15% chance
            # Check if opponent can raise truco
            if self.app.controller.truco.can_raise_truco("Oponente"):
                self._opponent_calls_truco()
                return
        
        self.snapshot = self.app.controller.play_opponent_card()
        self.waiting_for_opponent = False
    
    def _opponent_calls_truco(self) -> None:
        """Opponent initiates a truco call."""
        # Clear any lingering round result display so clicks won't be blocked
        self.showing_round_result = False
        self.snapshot = self.app.controller.call_truco("Oponente")
        pending = self.snapshot.get("pending_truco")
        
        if pending:
            opponent_name = self.snapshot.get("opponent_name", "Oponente")
            # Show truco overlay for player to respond
            self.truco_overlay.set_message(
                opponent_name,
                pending["name"],
                pending.get("can_reraise", True)
            )
            self.showing_truco_overlay = True
            self.pending_truco_data = {
                "caller": "Oponente",
                "value": pending["value"],
                "name": pending["name"]
            }
            self.waiting_for_opponent = False  # Stop waiting, now waiting for player response
    
    def _player_calls_truco(self) -> None:
        """Handle player calling truco (T key)."""
        # Check if truco can be called (not while cards are being played, etc.)
        if self.waiting_for_opponent or self.showing_truco_overlay:
            return
        # Clear any lingering round result display so player can proceed
        self.showing_round_result = False
        
        self.snapshot = self.app.controller.call_truco("Jogador")
        pending = self.snapshot.get("pending_truco")
        
        if pending:
            # First, show that YOU called truco (informational message, no buttons)
            self.round_result_text = f"Você pediu {pending['name']}!"
            self.showing_player_truco_call = True
            self.result_timer = 1.5  # Show for 1.5 seconds
            self.pending_truco_data = pending
            self.pending_truco_data["caller"] = "Jogador"
    
    def _reset_truco_state(self) -> None:
        """Reset all truco-related state flags."""
        self.showing_truco_overlay = False
        self.showing_player_truco_call = False
        self.showing_ai_truco_result = False
        self.waiting_for_ai_truco_response = False
        # Also clear any lingering round result display that could block clicks
        self.showing_round_result = False
        self.pending_truco_data = None
        self.ai_truco_decision = None
    
    def _handle_truco_response(self, action: str) -> None:
        """Handle player response to opponent's truco call."""
        print(f"[DEBUG] Player truco response: {action}")
        if self.pending_truco_data:
            caller = self.pending_truco_data["caller"]
            value = self.pending_truco_data["value"]
            print(f"[DEBUG] Caller: {caller}, Value: {value}")
            
            if action == "reraise":
                # Player wants to reraise - initiate a truco call from the player
                next_value = value + 3
                if next_value <= 12:
                    # Accept current value first, then player calls the reraise
                    self.snapshot = self.app.controller.respond_to_truco("accept", caller, value)
                    
                    # Now player calls the next level
                    self.snapshot = self.app.controller.call_truco("Jogador")
                    pending = self.snapshot.get("pending_truco")
                    
                    if pending:
                        # Show player's reraise announcement
                        self.round_result_text = f"Você pediu {pending['name']}!"
                        self.showing_player_truco_call = True
                        self.result_timer = 1.5
                        self.pending_truco_data = pending
                        self.pending_truco_data["caller"] = "Jogador"
                        # Will continue to get AI response in update()
                        self.waiting_for_ai_truco_response = True
                    return
                else:
                    # Can't reraise beyond 12, auto-accept
                    self.snapshot = self.app.controller.respond_to_truco("accept", caller, value)
                    # Reset truco state
                    self._reset_truco_state()
                    # Refresh snapshot
                    self.snapshot = self._get_snapshot()
                    # Check if opponent should play
                    battle = self.snapshot.get("battle", {})
                    if not battle.get("opponent_card") and not self._is_player_turn():
                        print("[DEBUG] Player can't reraise, auto-accept, triggering opponent play")
                        self.waiting_for_opponent = True
                    return
            else:
                print(f"[DEBUG] Calling respond_to_truco with action: {action}")
                self.snapshot = self.app.controller.respond_to_truco(action, caller, value)
            
            # Check if hand ended due to running
            truco_result = self.snapshot.get("truco_result")
            if truco_result and truco_result.get("action") == "run":
                print(f"[DEBUG] Player accepted but hand ended due to run - winner: {truco_result.get('winner')}")
                
                # Hand ended - transition to results
                self._reset_truco_state()
                self.snapshot = self._get_snapshot()
                
                # Calculate winner and points
                winner = truco_result.get("winner")
                points = truco_result.get("points", self.app.controller.truco.current_hand_value)
                
                # Determine match status
                sidebar = self.snapshot.get("sidebar", {})
                player_score = sidebar.get("player_score", 0)
                opponent_score = sidebar.get("opponent_score", 0)
                match_active = player_score < 12 and opponent_score < 12
                
                print(f"[DEBUG] Hand winner: {winner}, Points: {points}")
                self._show_hand_results(winner, points, match_active)
                return  # Stop processing
            
            # Reset ALL truco state
            print("[DEBUG] Resetting truco state after response")
            self._reset_truco_state()
            
            # Force snapshot refresh after truco response
            self.snapshot = self._get_snapshot()
            
            print(f"[DEBUG] After truco response - player_starts_round: {self.snapshot.get('player_starts_round')}")
            print(f"[DEBUG] After truco response - player_turn: {self._is_player_turn()}")
            print(f"[DEBUG] After truco response - battle: {self.snapshot.get('battle')}")

            # If it's opponent's turn and they haven't played, trigger their play
            battle = self.snapshot.get("battle", {})
            if not battle.get("opponent_card") and not self._is_player_turn():
                print("[DEBUG] Truco response complete, triggering opponent play")
                self.waiting_for_opponent = True
    
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
            print("[DEBUG] Hand ended, preparing to show results...")
            # Hand ended - calculate hand winner and points
            sidebar = self.snapshot.get("sidebar", {})
            player_score = sidebar.get("player_score", 0)
            opponent_score = sidebar.get("opponent_score", 0)
            round_results = self.snapshot.get("round_results", [])
            
            print(f"[DEBUG] Scores: Player={player_score}, Opponent={opponent_score}")
            
            # Determine hand winner
            vitorias_jogador = round_results.count("Jogador")
            vitorias_oponente = round_results.count("Oponente")
            
            if vitorias_jogador > vitorias_oponente:
                hand_winner = "Jogador"
            elif vitorias_oponente > vitorias_jogador:
                hand_winner = "Oponente"
            else:
                # Tied - use first winner
                primeira_vitoria = None
                for result in round_results:
                    if result != "Empate":
                        primeira_vitoria = result
                        break
                hand_winner = primeira_vitoria if primeira_vitoria else "Jogador"
            
            # Points awarded is the truco value
            points_awarded = self.app.controller.truco.current_hand_value
            
            # Check if match is over using controller method
            match_info = self.app.controller.check_match_winner()
            match_active = not match_info['match_over']
            
            print(f"[DEBUG] Hand winner: {hand_winner}, Points: {points_awarded}, Match active: {match_active}")
            if match_info['match_over']:
                print(f"[DEBUG] MATCH OVER! Winner: {match_info['winner']}, Final scores: Player {match_info['player_score']}, Opponent {match_info['opponent_score']}")
            
            # Store results data for transition after round result display
            self.pending_hand_results = {
                "hand_winner": hand_winner,
                "points_awarded": points_awarded,
                "match_active": match_active
            }
            
            # Don't transition immediately - wait for round result timer to finish
            # Transition will happen in update() when result_timer expires
    
    def _show_hand_results(self, hand_winner: str, points_awarded: int, match_active: bool) -> None:
        """Transition to results scene after hand ends."""
        print(f"[DEBUG] Creating ResultsScene: winner={hand_winner}, points={points_awarded}, match_active={match_active}")
        try:
            from ui.scenes.results_scene import ResultsScene
            results_scene = ResultsScene(self.app, hand_winner, points_awarded, match_active)
            print("[DEBUG] ResultsScene created, calling replace_scene...")
            self.app.replace_scene(results_scene)
            print("[DEBUG] replace_scene completed")
        except Exception as e:
            print(f"[ERROR] Failed to create/show ResultsScene: {e}")
            import traceback
            traceback.print_exc()
    
    def update(self, delta_time: float) -> None:
        """Update game scene."""
        # Refresh snapshot each frame (for live game state), but NOT during truco sequences
        if not (self.showing_truco_overlay or self.waiting_for_ai_truco_response or 
                self.showing_player_truco_call or self.showing_ai_truco_result):
            self.snapshot = self._get_snapshot()
        
        # Update button hover states if truco overlay is showing
        if self.showing_truco_overlay:
            mouse_pos = pygame.mouse.get_pos()
            self.truco_overlay.update(mouse_pos)
        
        # Handle showing player's truco call announcement
        if self.showing_player_truco_call:
            self.result_timer -= delta_time
            if self.result_timer <= 0:
                self.showing_player_truco_call = False
                # Now get AI response
                pending = self.snapshot.get("pending_truco")
                if pending:
                    value = pending["value"]
                    self.ai_truco_decision = self.app.controller.ai_truco_response(value)
                    # Show AI decision result
                    self.showing_ai_truco_result = True
                    self.result_timer = 2.0  # Show for 2 seconds
        
        # Handle showing AI truco decision result
        if self.showing_ai_truco_result:
            self.result_timer -= delta_time
            if self.result_timer <= 0:
                self.showing_ai_truco_result = False
                # Apply the decision
                if self.pending_truco_data and self.ai_truco_decision:
                    caller = self.pending_truco_data["caller"]
                    value = self.pending_truco_data["value"]
                    
                    if self.ai_truco_decision == "reraise":
                        # Opponent reraised - get the new value
                        next_value = value + 3
                        if next_value <= 12:
                            truco_name = {3: "Truco", 6: "Seis", 9: "Nove", 12: "Doze"}.get(next_value, str(next_value))
                            # Update snapshot with new pending truco for player to respond
                            self.snapshot = self.app.controller.get_snapshot()
                            self.snapshot["pending_truco"] = {
                                "caller": "Oponente",
                                "value": next_value,
                                "name": truco_name,
                                "can_reraise": next_value < 12
                            }
                            # Show overlay for player to respond
                            self.truco_overlay.set_message(
                                "Oponente",
                                truco_name,
                                next_value < 12
                            )
                            self.showing_truco_overlay = True
                            self.pending_truco_data = {
                                "caller": "Oponente",
                                "value": next_value,
                                "name": truco_name
                            }
                        else:
                            # Can't reraise beyond 12, auto-accept
                            self.snapshot = self.app.controller.respond_to_truco("accept", caller, value)
                            self.pending_truco_data = None
                            self.ai_truco_decision = None
                            self.waiting_for_ai_truco_response = False
                            self.snapshot = self._get_snapshot()
                            
                            # If it's opponent's turn and they haven't played, trigger their play
                            battle = self.snapshot.get("battle", {})
                            if not battle.get("opponent_card") and not self._is_player_turn():
                                print("[DEBUG] Truco auto-accept (can't reraise), triggering opponent play")
                                self.waiting_for_opponent = True
                    else:
                        # Accept or run
                        self.snapshot = self.app.controller.respond_to_truco(
                            self.ai_truco_decision, caller, value
                        )
                        
                        # Check if hand ended due to running
                        truco_result = self.snapshot.get("truco_result")
                        if truco_result and truco_result.get("action") == "run":
                            print(f"[DEBUG] Opponent ran from truco, caller: {caller}, winner: {truco_result.get('winner')}")
                            self.hand_active = False
                            
                            # Hand ended due to run - transition to results
                            self._reset_truco_state()
                            self.snapshot = self._get_snapshot()
                            
                            # Calculate winner and points
                            winner = truco_result.get("winner")
                            points = truco_result.get("points", self.app.controller.truco.current_hand_value)
                            
                            # Determine match status
                            sidebar = self.snapshot.get("sidebar", {})
                            player_score = sidebar.get("player_score", 0)
                            opponent_score = sidebar.get("opponent_score", 0)
                            match_active = player_score < 12 and opponent_score < 12
                            
                            print(f"[DEBUG] Hand winner: {winner}, Points: {points}")
                            self._show_hand_results(winner, points, match_active)
                            return  # Stop processing, scene has been replaced
                        
                        # Reset ALL truco state
                        self._reset_truco_state()
                        
                        # Force snapshot refresh after truco completes
                        self.snapshot = self._get_snapshot()
                        
                        # If it's opponent's turn and they haven't played, trigger their play
                        battle = self.snapshot.get("battle", {})
                        if not battle.get("opponent_card") and not self._is_player_turn():
                            print("[DEBUG] Truco complete, triggering opponent play")
                            self.waiting_for_opponent = True
        
        # Handle opponent turn with delay
        if self.waiting_for_opponent:
            self._opponent_plays()
        
        # Handle round result display timer
        if self.showing_round_result:
            self.result_timer -= delta_time
            if self.result_timer <= 0:
                self.showing_round_result = False
                
                # Check if we need to transition to results scene
                if self.pending_hand_results:
                    print("[DEBUG] Transitioning to results scene...")
                    self._show_hand_results(
                        self.pending_hand_results["hand_winner"],
                        self.pending_hand_results["points_awarded"],
                        self.pending_hand_results["match_active"]
                    )
                    return  # Don't continue with opponent turn logic
                
                # Check if opponent should start next round AND hasn't played yet
                battle = self.snapshot.get("battle", {})
                if not self.snapshot.get("player_starts_round") and not battle.get("opponent_card"):
                    self.waiting_for_opponent = True

        # Handle opponent fugir display timer
        if self.showing_opponent_fugir:
            self.result_timer -= delta_time
            if self.result_timer <= 0:
                self.showing_opponent_fugir = False
                # Transition to results screen
                if self.pending_hand_results:
                    self._show_hand_results(
                        self.pending_hand_results['hand_winner'],
                        self.pending_hand_results['points_awarded'],
                        self.pending_hand_results['match_active']
                    )
                    self.pending_hand_results = None
            return
    
    
    def render(self, surface: pygame.Surface) -> None:
        """Render the game scene."""
        # Use renderer to draw the entire game state and get card displays and button rects
        self.card_displays, self.button_rects = self.renderer.render_game_state(self.snapshot)
        
        # Overlay truco if showing
        if self.showing_truco_overlay:
            self.truco_overlay.render(surface)
        
        # Overlay player's truco call if showing
        if self.showing_player_truco_call:
            self._render_round_result_overlay(surface)
        
        # Overlay AI truco decision if showing
        if self.showing_ai_truco_result:
            self._render_ai_truco_decision_overlay(surface)

        # Overlay opponent fugir if showing
        if self.showing_opponent_fugir:
            self._render_opponent_fugir_overlay(surface)
        
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
    
    def _render_ai_truco_decision_overlay(self, surface: pygame.Surface) -> None:
        """Render AI truco decision overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.app.width, self.app.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # Decision text
        opponent_name = self.snapshot.get("opponent_name", "Oponente")
        font_large = pygame.font.Font(None, GameConfig.FONT_SIZE_TITLE)
        font_normal = pygame.font.Font(None, GameConfig.FONT_SIZE_LARGE)
        
        if self.ai_truco_decision == "accept":
            text = f"{opponent_name} aceitou!"
            color = GameConfig.COLOR_PRIMARY
        elif self.ai_truco_decision == "run":
            text = f"{opponent_name} correu!"
            color = GameConfig.COLOR_DANGER
        elif self.ai_truco_decision == "reraise":
            # Get the next truco name
            if self.pending_truco_data:
                next_value = self.pending_truco_data.get("value", 3) + 3
                if next_value <= 12:
                    truco_names = {3: "Truco", 6: "Seis", 9: "Nove", 12: "Doze"}
                    next_name = truco_names.get(next_value, str(next_value))
                    text = f"{opponent_name} pediu {next_name}!"
                else:
                    text = f"{opponent_name} aceitou!"
            else:
                text = f"{opponent_name} aumentou!"
            color = GameConfig.COLOR_WARNING
        else:
            text = f"{opponent_name} respondeu"
            color = GameConfig.COLOR_PRIMARY
        
        text_surface = font_large.render(text, True, color)
        text_rect = text_surface.get_rect(center=(self.app.width // 2, self.app.height // 2))
        surface.blit(text_surface, text_rect)

    def _render_opponent_fugir_overlay(self, surface: pygame.Surface) -> None:
        """Render opponent fugir overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.app.width, self.app.height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # Fugir text
        font_large = pygame.font.Font(None, GameConfig.FONT_SIZE_TITLE)
        text_surface = font_large.render(
            "Oponente Fugiu!",
            True,
            GameConfig.COLOR_DANGER
        )
        text_rect = text_surface.get_rect(center=(self.app.width // 2, self.app.height // 2))
        surface.blit(text_surface, text_rect)
    
    def _handle_button_click(self, button_name: str) -> None:
        """Handle clicks on game control buttons."""
        if button_name == "truco":
            # Simulate pressing T key
            self._player_calls_truco()
        elif button_name == "fugir":
            # Player gives up the hand - opponent gets truco value points
            self._player_fugir()
        elif button_name == "menu":
            # Go back to menu
            from ui.scenes.menu_scene import MenuScene
            self.app.replace_scene(MenuScene(self.app))
        elif button_name == "opções":
            # TODO: Implement settings/options scene
            print("[DEBUG] Opções button clicked - not yet implemented")
        elif button_name == "sair":
            # Quit the game
            from utils import safe_exit
            safe_exit()
    
    def _player_fugir(self) -> None:
        """Handle player giving up (fugir) the hand."""
        # Get hand results from controller
        hand_results = self.app.controller.player_fugir()
        
        # Check if match is over
        match_info = self.app.controller.check_match_winner()
        match_active = not match_info['match_over']
        
        print(f"[DEBUG] Player fugiu! Hand winner: {hand_results['hand_winner']}, Points: {hand_results['points_awarded']}, Match active: {match_active}")
        
        # Transition to results scene
        self._show_hand_results(
            hand_results['hand_winner'],
            hand_results['points_awarded'],
            match_active
        )
