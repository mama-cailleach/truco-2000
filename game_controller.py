"""
Game Controller Module for Truco 2000

This module orchestrates the main game flow:
- Main game loop
- Hand and round management
- Coordination between core logic, truco logic, and UI

This is the central conductor of the game, keeping all modules in sync.
"""

from game_core import GameCore
from truco_logic import TrucoLogic
from ui.ascii_art import ASCIIArt
from config import GameConfig
from utils import safe_exit
import time


class GameController:
    """
    Orchestrates the main game flow and coordinates all modules.
    """
    def __init__(self):
        # Initialize all modules
        self.config = GameConfig
        self.core = GameCore()
        self.truco = TrucoLogic()
        self.ascii_art = ASCIIArt()
        # Note: Old UI modules (ui.display, ui.input) removed for Pygame refactor
        # Pygame app manages its own UI through scenes and renderer
        
        # Pygame-specific state
        self.player_hand = []
        self.opponent_hand = []
        self.carta_vira = None
        self.manilha = None
        self.round_results = []
        self.current_round = 0
        self.played_cards = {"player": None, "opponent": None}
        self.hand_active = False
        
    def start_new_hand(self):
        """Initialize a new hand for Pygame UI."""
        self.core.reiniciar_baralho()
        self.truco.reset_truco_state()
        self.core.player_starts_round = self.core.player_starts_hand
        self.carta_vira, self.manilha = self.core.determinar_manilha()
        self.player_hand = self.core.distribuir_cartas(self.config.CARDS_PER_HAND)
        self.opponent_hand = self.core.distribuir_cartas(self.config.CARDS_PER_HAND)
        self.round_results = []
        self.current_round = 1
        self.played_cards = {"player": None, "opponent": None}
        self.hand_active = True
    
    def check_match_winner(self) -> dict:
        """
        Check if either player has reached 12 points (match winner).
        
        Returns:
            dict with keys:
                - 'match_over': bool (True if someone reached 12 points)
                - 'winner': str ('Jogador', 'Oponente', or None)
                - 'player_score': int
                - 'opponent_score': int
        """
        player_score = self.core.pontos_jogador
        opponent_score = self.core.pontos_oponente
        
        match_over = player_score >= 12 or opponent_score >= 12
        
        if match_over:
            winner = "Jogador" if player_score >= 12 else "Oponente"
        else:
            winner = None
        
        return {
            'match_over': match_over,
            'winner': winner,
            'player_score': player_score,
            'opponent_score': opponent_score
        }
    
    def player_fugir(self) -> dict:
        """
        Player gives up (fugir) the current hand.
        Opponent wins the hand and gets points equal to current truco value.
        
        Returns:
            dict with hand results (hand_winner, points_awarded, match_active)
        """
        # Award points to opponent
        points = self.truco.current_hand_value
        self.core.pontos_oponente += points
        
        # Opponent starts next hand
        self.core.player_starts_hand = False
        
        # End the hand
        self.hand_active = False
        
        print(f"[DEBUG] Player fugiu! Opponent gets {points} points")
        
        return {
            'hand_winner': 'Oponente',
            'points_awarded': points,
            'match_active': self.core.pontos_oponente < 12 and self.core.pontos_jogador < 12
        }
    
    def opponent_fugir(self) -> dict:
        """
        Opponent gives up (fugir) the current hand.
        Player wins the hand and gets points equal to current truco value.
        
        Returns:
            dict with hand results (hand_winner, points_awarded, match_active)
        """
        # Award points to player
        points = self.truco.current_hand_value
        self.core.pontos_jogador += points
        
        # Player starts next hand
        self.core.player_starts_hand = True
        
        # End the hand
        self.hand_active = False
        
        print(f"[DEBUG] Opponent fugiu! Player gets {points} points")
        
        return {
            'hand_winner': 'Jogador',
            'points_awarded': points,
            'match_active': self.core.pontos_jogador < 12 and self.core.pontos_oponente < 12
        }
        
    def play_player_card(self, card_index: int):
        """
        Player plays a card. Returns updated game state.
        Non-blocking version for Pygame UI.
        """
        if not self.hand_active or card_index >= len(self.player_hand):
            return self.get_snapshot()
        
        # Player plays card
        self.played_cards["player"] = self.player_hand.pop(card_index)
        return self.get_snapshot()
    
    def play_opponent_card(self):
        """
        Opponent plays a card. Returns updated game state.
        Uses simple AI (first card for now).
        """
        if not self.hand_active or not self.opponent_hand:
            return self.get_snapshot()
        
        # Simple AI: play first card (can be enhanced later)
        self.played_cards["opponent"] = self.opponent_hand.pop(0)
        return self.get_snapshot()
    
    def resolve_round(self):
        """
        Resolve the current round after both players have played cards.
        Returns updated game state with round winner.
        """
        if not self.played_cards["player"] or not self.played_cards["opponent"]:
            return self.get_snapshot()
        
        try:
            # Determine round winner
            player_card = self.played_cards["player"]
            opponent_card = self.played_cards["opponent"]
            
            winner = self.core.vencedor_rodada(
                player_card, opponent_card, self.manilha
            )
            
            # Track result
            if winner == "Empate":
                self.round_results.append("Empate")
            elif winner == "Jogador":
                self.round_results.append("Jogador")
                self.core.player_starts_round = True
            else:
                self.round_results.append("Oponente")
                self.core.player_starts_round = False
            
            # Clear played cards
            self.played_cards = {"player": None, "opponent": None}
            
            # Check if hand is over
            # check_hand_winner needs: round number, results, player wins, opponent wins, first winner
            # For now, calculate wins from results
            vitorias_jogador = self.round_results.count("Jogador")
            vitorias_oponente = self.round_results.count("Oponente")
            primeira_vitoria = None
            for result in self.round_results:
                if result != "Empate":
                    primeira_vitoria = result
                    break
            
            rodada_number = len(self.round_results) - 1  # 0-indexed
            end_hand, winner_message = self.core.check_hand_winner(
                rodada_number,  # current round (0, 1, or 2)
                self.round_results,
                vitorias_jogador,
                vitorias_oponente,
                primeira_vitoria
            )
            
            if end_hand:
                # Determine who won
                if vitorias_jogador > vitorias_oponente:
                    hand_winner = "Jogador"
                elif vitorias_oponente > vitorias_jogador:
                    hand_winner = "Oponente"
                else:
                    # Tied, use primeira_vitoria
                    hand_winner = primeira_vitoria if primeira_vitoria else "Jogador"
                
                # Award points
                points = self.truco.current_hand_value
                if hand_winner == "Jogador":
                    self.core.pontos_jogador += points
                    self.core.player_starts_hand = True
                else:
                    self.core.pontos_oponente += points
                    self.core.player_starts_hand = False
                
                self.hand_active = False
            else:
                # Continue to next round
                self.current_round += 1
            
            return self.get_snapshot()
        except Exception as e:
            print(f"[ERROR] resolve_round failed: {e}")
            import traceback
            traceback.print_exc()
            return self.get_snapshot()
    
    def call_truco(self, caller: str) -> dict:
        """
        Caller initiates a truco request.
        
        Args:
            caller: "Jogador" or "Oponente"
            
        Returns:
            dict: Updated snapshot with pending_truco information
        """
        if not self.truco.can_raise_truco(caller):
            # Cannot raise, return current state
            return self.get_snapshot()
        
        next_value = self.truco.get_next_truco_value()
        if next_value is None:
            # Already at max
            return self.get_snapshot()
        
        # Mark as pending for UI to handle
        snapshot = self.get_snapshot()
        snapshot["pending_truco"] = {
            "caller": caller,
            "value": next_value,
            "name": self.truco.get_truco_name(next_value),
            "can_reraise": next_value < 12
        }
        return snapshot
    
    def respond_to_truco(self, response: str, caller: str, value: int) -> dict:
        """
        Respond to a truco call.
        
        Args:
            response: "accept", "run", or "reraise"
            caller: Who called the truco
            value: The truco value that was called
            
        Returns:
            dict: Updated snapshot
        """
        responder = "Oponente" if caller == "Jogador" else "Jogador"
        
        if response == "accept":
            # Accept the truco
            self.truco.current_hand_value = value
            self.truco.last_raiser = caller
            self.truco.last_accepted_value = value
            return self.get_snapshot()
        
        elif response == "run":
            # Run away - hand ends, caller wins the current hand value
            points = self.truco.current_hand_value
            if caller == "Jogador":
                self.core.pontos_jogador += points
                self.core.player_starts_hand = True
            else:
                self.core.pontos_oponente += points
                self.core.player_starts_hand = False
            
            self.hand_active = False
            snapshot = self.get_snapshot()
            snapshot["truco_result"] = {
                "winner": caller,
                "action": "run",
                "points": points
            }
            return snapshot
        
        elif response == "reraise":
            # Reraise - call truco again from responder's side
            return self.call_truco(responder)
        
        return self.get_snapshot()
    
    def ai_truco_response(self, value: int) -> str:
        """
        Get AI response to a truco call.
        
        Args:
            value: The truco value being proposed
            
        Returns:
            str: "accept", "run", or "reraise"
        """
        return self.truco.get_opponent_truco_response(value)
    
    def get_snapshot(self):
        """
        Return current game state as a dictionary for Pygame UI.
        """
        return {
            "player_hand": self.player_hand.copy(),
            "opponent_hand": self.opponent_hand.copy(),
            "opponent_card_count": len(self.opponent_hand),
            "carta_vira": self.carta_vira,
            "manilha": self.manilha,
            "round_results": self.round_results.copy(),
            "current_round": self.current_round,
            "played": self.played_cards.copy(),
            "scores": {
                "player": self.core.pontos_jogador,
                "opponent": self.core.pontos_oponente
            },
            "current_hand_value": self.truco.current_hand_value,
            "player_starts_round": self.core.player_starts_round,
            "player_starts_hand": self.core.player_starts_hand,
            "hand_active": self.hand_active,
            "opponent_name": "INIT-RAM"
        }

    def start_game(self):
        """Main game loop function."""
        while True:
            self.ui.show_game_intro()
            jogar_novamente = self.input.get_yes_no_input(self.config.MESSAGES['welcome'])
            if not jogar_novamente:
                self.ui.show_quit_message()
                safe_exit()

            self.core.reset_game_state()
            self.truco.reset_truco_state()
            self.core.baralho = self.core.baralho_original.copy()
            self.core.embaralhar()

            # Player always starts the first hand
            self.core.player_starts_hand = True

            while self.core.pontos_jogador < self.config.WINNING_SCORE and self.core.pontos_oponente < self.config.WINNING_SCORE:
                self.play_hand()

            # Show game winner
            winner = self.core.get_game_winner()
            self.ui.show_game_winner(winner)

            # Ask to play again
            jogar_novamente = self.input.get_yes_no_input(self.config.MESSAGES['play_again'])
            if not jogar_novamente:
                self.ui.show_quit_message()
                safe_exit()

    def play_hand(self):
        """Plays one hand of the game."""
        self.core.reiniciar_baralho()
        self.truco.reset_truco_state()
        # Ensure the first round of the hand starts with the correct player
        self.core.player_starts_round = self.core.player_starts_hand
        carta_vira, manilha = self.core.determinar_manilha()
        mao_do_jogador = self.core.distribuir_cartas(self.config.CARDS_PER_HAND)
        mao_do_oponente = self.core.distribuir_cartas(self.config.CARDS_PER_HAND)
        resultados_rodadas = []
        primeira_vitoria = None
        vitorias_jogador = 0
        vitorias_oponente = 0

        for rodada in range(3):
            # Show layout before each round
            self.ui.display_game_layout(
                self.core, self.truco, rodada, mao_do_jogador, manilha, resultados_rodadas, carta_vira,
                self.core.player_starts_round, primeira_vitoria
            )

            # --- Play a single round ---
            # Decide who starts
            player_starts = self.core.player_starts_round
            carta_jogador = None
            carta_oponente = None
            special_result = None
            last_raiser = self.truco.last_raiser
            current_hand_value = self.truco.current_hand_value

            if player_starts:
                # Player's turn: can truco/fugir or play card
                escolha = self.input.get_card_choice(
                    mao_do_jogador, self.truco,
                    allow_truco=self.truco.can_raise_truco("Jogador"),
                    allow_fugir=(current_hand_value > 1)
                )
                if escolha.lower() == 'f':
                    # Player runs from truco
                    winner, points = self.truco.calculate_points_for_runner("Jogador", current_hand_value, current_hand_value)
                    self.core.update_score(winner, points)
                    if points == 1:
                        self.ui.show_message(f"Você fugiu! Oponente ganha {points} ponto.", 3)
                    else:
                        self.ui.show_message(f"Você fugiu! Oponente ganha {points} pontos.", 3)
                    self.core.player_starts_hand = False
                    return
                elif escolha.lower() == 't':
                    # Player calls truco
                    self.ui.show_truco_call("Jogador", self.truco.get_next_truco_value(), self.truco.truco_names)
                    accepted, final_value, who_ran, final_raiser, last_accepted_value = self.truco.handle_truco_sequence(
                        "Jogador", self.truco.get_next_truco_value(), self.input, self.ui
                    )
                    self.truco.update_truco_state(final_value, final_raiser)
                    if not accepted:
                        winner, points = self.truco.calculate_points_for_runner(who_ran, final_value, last_accepted_value)
                        self.core.update_score(winner, points)
                        if points == 1:
                            self.ui.show_message(f"{winner} ganha {points} ponto!", 3)
                        else:
                            self.ui.show_message(f"{winner} ganha {points} pontos!", 3)
                        self.core.player_starts_hand = (winner == "Jogador")
                        return
                    # After truco, ask for card again
                    escolha = self.input.get_card_choice(
                        mao_do_jogador, self.truco,
                        allow_truco=False, allow_fugir=(self.truco.current_hand_value > 1)
                    )
                    if escolha.lower() == 'f':
                        winner, points = self.truco.calculate_points_for_runner("Jogador", self.truco.current_hand_value, self.truco.current_hand_value)
                        self.core.update_score(winner, points)
                        if points == 1:
                            self.ui.show_message(f"Você fugiu! Oponente ganha {points} ponto.", 3)
                        else:
                            self.ui.show_message(f"Você fugiu! Oponente ganha {points} pontos.", 3)
                        self.core.player_starts_hand = False
                        return
                # Play card
                carta_index = int(escolha) - 1
                carta_jogador = mao_do_jogador.pop(carta_index)
                # Show player's card
                battle_zone = {"carta_jogador": carta_jogador}
                self.ui.display_game_layout(
                    self.core, self.truco, rodada, mao_do_jogador, manilha, resultados_rodadas, carta_vira,
                    player_starts, primeira_vitoria, battle_zone
                )
                self.ui.show_message("Você jogou sua carta! Aguardando oponente...", 2)
                # Opponent plays
                if mao_do_oponente:
                    carta_oponente = mao_do_oponente.pop(0)
            else:
                # Opponent's turn: may truco, then plays card
                can_opponent_truco = self.truco.can_raise_truco("Oponente")
                if can_opponent_truco and self.truco.should_opponent_initiate_truco(current_hand_value):
                    self.ui.show_truco_call("Oponente", self.truco.get_next_truco_value(), self.truco.truco_names)
                    accepted, final_value, who_ran, final_raiser, last_accepted_value = self.truco.handle_truco_sequence(
                        "Oponente", self.truco.get_next_truco_value(), self.input, self.ui
                    )
                    self.truco.update_truco_state(final_value, final_raiser)
                    if not accepted:
                        winner, points = self.truco.calculate_points_for_runner(who_ran, final_value, last_accepted_value)
                        self.core.update_score(winner, points)
                        if points == 1:
                            self.ui.show_message(f"{winner} ganha {points} ponto!", 3)
                        else:
                            self.ui.show_message(f"{winner} ganha {points} pontos!", 3)
                        self.core.player_starts_hand = (winner == "Jogador")
                        return
                # Opponent plays card
                if mao_do_oponente:
                    carta_oponente = mao_do_oponente.pop(0)
                # Show battle zone with only opponent's card
                battle_zone = {"carta_oponente": carta_oponente}
                self.ui.display_game_layout(
                    self.core, self.truco, rodada, mao_do_jogador, manilha, resultados_rodadas, carta_vira,
                    player_starts, primeira_vitoria, battle_zone
                )
                self.ui.show_message("Oponente jogou a carta! Sua vez.", 1.5)
                # Player can truco after seeing opponent's card
                escolha = self.input.get_card_choice(
                    mao_do_jogador, self.truco,
                    allow_truco=self.truco.can_raise_truco("Jogador"),
                    allow_fugir=(self.truco.current_hand_value > 1)
                )
                if escolha.lower() == 'f':
                    winner, points = self.truco.calculate_points_for_runner("Jogador", self.truco.current_hand_value, self.truco.current_hand_value)
                    self.core.update_score(winner, points)
                    if points == 1:
                        self.ui.show_message(f"Você fugiu! Oponente ganha {points} ponto.", 3)
                    else:
                        self.ui.show_message(f"Você fugiu! Oponente ganha {points} pontos.", 3)
                    self.core.player_starts_hand = False
                    return
                elif escolha.lower() == 't':
                    self.ui.show_truco_call("Jogador", self.truco.get_next_truco_value(), self.truco.truco_names)
                    accepted, final_value, who_ran, final_raiser, last_accepted_value = self.truco.handle_truco_sequence(
                        "Jogador", self.truco.get_next_truco_value(), self.input, self.ui
                    )
                    self.truco.update_truco_state(final_value, final_raiser)
                    if not accepted:
                        winner, points = self.truco.calculate_points_for_runner(who_ran, final_value, last_accepted_value)
                        self.core.update_score(winner, points)
                        if points == 1:
                            self.ui.show_message(f"{winner} ganha {points} ponto!", 3)
                        else:
                            self.ui.show_message(f"{winner} ganha {points} pontos!", 3)
                        self.core.player_starts_hand = (winner == "Jogador")
                        return
                    escolha = self.input.get_card_choice(
                        mao_do_jogador, self.truco,
                        allow_truco=False, allow_fugir=(self.truco.current_hand_value > 1)
                    )
                    if escolha.lower() == 'f':
                        winner, points = self.truco.calculate_points_for_runner("Jogador", self.truco.current_hand_value, self.truco.current_hand_value)
                        self.core.update_score(winner, points)
                        if points == 1:
                            self.ui.show_message(f"Você fugiu! Oponente ganha {points} ponto.", 3)
                        else:
                            self.ui.show_message(f"Você fugiu! Oponente ganha {points} pontos.", 3)
                        self.core.player_starts_hand = False
                        return
                carta_index = int(escolha) - 1
                carta_jogador = mao_do_jogador.pop(carta_index)
            # Show both cards in battle zone
            battle_zone = {"carta_jogador": carta_jogador, "carta_oponente": carta_oponente}
            # Determine winner
            vencedor = self.core.vencedor_rodada(carta_jogador, carta_oponente, manilha)
            # Show result
            battle_zone.update({"round_result": f"Vencedor: {vencedor}", "show_result": True})
            self.ui.display_game_layout(
                self.core, self.truco, rodada, mao_do_jogador, manilha, resultados_rodadas, carta_vira,
                player_starts, primeira_vitoria, battle_zone
            )
            self.ui.show_message(f"Resultado da rodada: {vencedor}", 2)
            # Update who starts next round
            if vencedor == "Jogador":
                self.core.player_starts_round = True
            elif vencedor == "Oponente":
                self.core.player_starts_round = False
            # Update results and counters
            resultados_rodadas.append(vencedor)
            if vencedor != "Empate" and primeira_vitoria is None:
                primeira_vitoria = vencedor
            if vencedor == "Jogador":
                vitorias_jogador += 1
            elif vencedor == "Oponente":
                vitorias_oponente += 1
            # Check for hand winner
            end_hand, winner_message = self.core.check_hand_winner(
                rodada, resultados_rodadas, vitorias_jogador, vitorias_oponente, primeira_vitoria
            )
            if end_hand:
                self.ui.show_message(winner_message, 3)
                break

        # Award points for hand
        if vitorias_jogador > vitorias_oponente:
            self.core.update_score("Jogador", self.truco.current_hand_value)
            self.ui.show_hand_result("Jogador", self.truco.current_hand_value, self.core)
            self.core.player_starts_hand = True
        elif vitorias_oponente > vitorias_jogador:
            self.core.update_score("Oponente", self.truco.current_hand_value)
            self.ui.show_hand_result("Oponente", self.truco.current_hand_value, self.core)
            self.core.player_starts_hand = False
        elif resultados_rodadas.count("Empate") == 3:
            # All rounds tied
            self.ui.show_message("Mão empatada! Nenhum ponto atribuído.", 3)
        else:
            # Last round is tie, check who won the first round
            if resultados_rodadas[0] == "Jogador":
                self.core.update_score("Jogador", self.truco.current_hand_value)
                self.ui.show_hand_result("Jogador", self.truco.current_hand_value, self.core)
                self.core.player_starts_hand = True
            elif resultados_rodadas[0] == "Oponente":
                self.core.update_score("Oponente", self.truco.current_hand_value)
                self.ui.show_hand_result("Oponente", self.truco.current_hand_value, self.core)
                self.core.player_starts_hand = False
            else:
                # Defensive fallback (should never happen)
                self.ui.show_message("Mão empatada! Nenhum ponto atribuído.", 3) 
