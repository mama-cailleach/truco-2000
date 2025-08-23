from game_controller import GameController

class DebugGameController(GameController):
    def __init__(self):
        super().__init__()

    def choose_opponent_card(self, mao_do_oponente):
        # Show opponent's hand for debugging
        print("\n[DEBUG] Escolha a carta do oponente para jogar:")
        for idx, card in enumerate(mao_do_oponente):
            print(f"{idx+1}: {card}")
        while True:
            escolha = input("Número da carta do oponente: ")
            if escolha.lower() == "quit":
                print("Saindo do jogo.")
                exit()
            if escolha.isdigit() and 1 <= int(escolha) <= len(mao_do_oponente):
                return mao_do_oponente.pop(int(escolha)-1)
            print("Escolha inválida.")

    def play_hand(self):
        """
        Overrides play_hand to allow manual selection of opponent's card.
        """
        self.core.reiniciar_baralho()
        self.truco.reset_truco_state()
        self.core.player_starts_round = self.core.player_starts_hand
        carta_vira, manilha = self.core.determinar_manilha()
        mao_do_jogador = self.core.distribuir_cartas(self.config.CARDS_PER_HAND)
        mao_do_oponente = self.core.distribuir_cartas(self.config.CARDS_PER_HAND)
        resultados_rodadas = []
        primeira_vitoria = None
        vitorias_jogador = 0
        vitorias_oponente = 0

        for rodada in range(3):
            self.ui.display_game_layout(
                self.core, self.truco, rodada, mao_do_jogador, manilha, resultados_rodadas, carta_vira,
                self.core.player_starts_round, primeira_vitoria
            )

            player_starts = self.core.player_starts_round
            carta_jogador = None
            carta_oponente = None
            special_result = None
            last_raiser = self.truco.last_raiser
            current_hand_value = self.truco.current_hand_value

            if player_starts:
                escolha = self.input.get_card_choice(
                    mao_do_jogador, self.truco,
                    allow_truco=self.truco.can_raise_truco("Jogador"),
                    allow_fugir=(current_hand_value > 1)
                )
                if escolha.lower() == 'f':
                    winner, points = self.truco.calculate_points_for_runner("Jogador", current_hand_value, current_hand_value)
                    self.core.update_score(winner, points)
                    self.ui.show_message(f"Você fugiu! Oponente ganha {points} pontos.", 3)
                    special_result = 'run'
                    break
                elif escolha.lower() == 't':
                    self.ui.show_truco_call("Jogador", self.truco.get_next_truco_value(), self.truco.truco_names)
                    accepted, final_value, who_ran, final_raiser, last_accepted_value = self.truco.handle_truco_sequence(
                        "Jogador", self.truco.get_next_truco_value(), self.input, self.ui
                    )
                    self.truco.update_truco_state(final_value, final_raiser)
                    if not accepted:
                        winner, points = self.truco.calculate_points_for_runner(who_ran, final_value, last_accepted_value)
                        self.core.update_score(winner, points)
                        self.ui.show_message(f"{winner} ganha {points} pontos!", 3)
                        special_result = 'run'
                        break
                    escolha = self.input.get_card_choice(
                        mao_do_jogador, self.truco,
                        allow_truco=False, allow_fugir=(self.truco.current_hand_value > 1)
                    )
                carta_index = int(escolha) - 1
                carta_jogador = mao_do_jogador.pop(carta_index)
                battle_zone = {"carta_jogador": carta_jogador}
                self.ui.display_game_layout(
                    self.core, self.truco, rodada, mao_do_jogador, manilha, resultados_rodadas, carta_vira,
                    player_starts, primeira_vitoria, battle_zone
                )
                self.ui.show_message("Você jogou sua carta! Aguardando oponente...", 2)
                # DEBUG: Let user pick opponent's card
                if mao_do_oponente:
                    carta_oponente = self.choose_opponent_card(mao_do_oponente)
            else:
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
                        self.ui.show_message(f"{winner} ganha {points} pontos!", 3)
                        special_result = 'run'
                        break
                # DEBUG: Let user pick opponent's card
                if mao_do_oponente:
                    carta_oponente = self.choose_opponent_card(mao_do_oponente)
                battle_zone = {"carta_oponente": carta_oponente}
                self.ui.display_game_layout(
                    self.core, self.truco, rodada, mao_do_jogador, manilha, resultados_rodadas, carta_vira,
                    player_starts, primeira_vitoria, battle_zone
                )
                self.ui.show_message("Oponente jogou a carta! Sua vez.", 1.5)
                escolha = self.input.get_card_choice(
                    mao_do_jogador, self.truco,
                    allow_truco=self.truco.can_raise_truco("Jogador"),
                    allow_fugir=(self.truco.current_hand_value > 1)
                )
                if escolha.lower() == 'f':
                    winner, points = self.truco.calculate_points_for_runner("Jogador", self.truco.current_hand_value, self.truco.current_hand_value)
                    self.core.update_score(winner, points)
                    self.ui.show_message(f"Você fugiu! Oponente ganha {points} pontos.", 3)
                    special_result = 'run'
                    break
                elif escolha.lower() == 't':
                    self.ui.show_truco_call("Jogador", self.truco.get_next_truco_value(), self.truco.truco_names)
                    accepted, final_value, who_ran, final_raiser, last_accepted_value = self.truco.handle_truco_sequence(
                        "Jogador", self.truco.get_next_truco_value(), self.input, self.ui
                    )
                    self.truco.update_truco_state(final_value, final_raiser)
                    if not accepted:
                        winner, points = self.truco.calculate_points_for_runner(who_ran, final_value, last_accepted_value)
                        self.core.update_score(winner, points)
                        self.ui.show_message(f"{winner} ganha {points} pontos!", 3)
                        special_result = 'run'
                        break
                    escolha = self.input.get_card_choice(
                        mao_do_jogador, self.truco,
                        allow_truco=False, allow_fugir=(self.truco.current_hand_value > 1)
                    )
                carta_index = int(escolha) - 1
                carta_jogador = mao_do_jogador.pop(carta_index)
            # Show both cards in battle zone
            battle_zone = {"carta_jogador": carta_jogador, "carta_oponente": carta_oponente}
            vencedor = self.core.vencedor_rodada(carta_jogador, carta_oponente, manilha)
            battle_zone.update({"round_result": f"Vencedor: {vencedor}", "show_result": True})
            self.ui.display_game_layout(
                self.core, self.truco, rodada, mao_do_jogador, manilha, resultados_rodadas, carta_vira,
                player_starts, primeira_vitoria, battle_zone
            )
            self.ui.show_message(f"Resultado da rodada: {vencedor}", 2)
            if vencedor == "Jogador":
                self.core.player_starts_round = True
            elif vencedor == "Oponente":
                self.core.player_starts_round = False
            resultados_rodadas.append(vencedor)
            if vencedor != "Empate" and primeira_vitoria is None:
                primeira_vitoria = vencedor
            if vencedor == "Jogador":
                vitorias_jogador += 1
            elif vencedor == "Oponente":
                vitorias_oponente += 1
            end_hand, winner_message = self.core.check_hand_winner(
                rodada, resultados_rodadas, vitorias_jogador, vitorias_oponente, primeira_vitoria
            )
            if end_hand:
                self.ui.show_message(winner_message, 3)
                break

        # Award points for hand (only if not already awarded)

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

if __name__ == "__main__":
    game = DebugGameController()
    game.start_game()