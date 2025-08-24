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
from ui.display import UIDisplay
from ui.input import InputHandler
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
        self.ui = UIDisplay(self.ascii_art, screen_width=self.config.SCREEN_WIDTH)
        self.input = InputHandler(self.ui)

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
