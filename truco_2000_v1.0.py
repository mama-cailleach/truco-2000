import random
import time


class TrucoGame:
    def __init__(self):
        # Card-related attributes
        self.baralho = self.create_baralho()
        self.baralho_original = self.baralho.copy()
        self.cards_database = self.fill_cards_database()

        # Game state attributes
        self.pontos_jogador = 0
        self.pontos_oponente = 0

        # track who goes first
        self.player_starts_hand = True  # Player starts the first hand
        self.player_starts_round = True  # Player starts the first round in a hand

        # UI elements
        self.ursinho = r'''
   _     _   
  (c).-.(c)  
   / ._. \   
 __\( Y )/__ 
(_.-/'-'\-._)
   ||   ||   
 _.' `-' '._ 
(.-./`-'\.-.)
 `-'     `-'  
            '''

        self.ursinho_tchau = r'''
  (c).-.(c)   ___________________
   / ._. \   | Ok! Então tchau!  |
   \( Y )/   |___________________|
    /'-'\    

                        '''

    def create_baralho(self):
        # Define deck with Unicode suit symbols
        return ['4♣', '5♣', '6♣', '7♣', 'Q♣', 'J♣', 'K♣', 'A♣', '2♣', '3♣',
                '4♥', '5♥', '6♥', '7♥', 'Q♥', 'J♥', 'K♥', 'A♥', '2♥', '3♥',
                '4♦', '5♦', '6♦', '7♦', 'Q♦', 'J♦', 'K♦', 'A♦', '2♦', '3♦',
                '4♠', '5♠', '6♠', '7♠', 'Q♠', 'J♠', 'K♠', 'A♠', '2♠', '3♠']

    def reiniciar_baralho(self):
        self.baralho = self.baralho_original.copy()
        self.embaralhar()

    def embaralhar(self):
        random.shuffle(self.baralho)

    def distribuir_cartas(self, quantidade):
        cartas = []
        for _ in range(quantidade):
            if self.baralho:
                cartas.append(self.baralho.pop())
        return cartas

    def get_valid_input(self, prompt, valid_options):
        """
        Gets and validates user input.

        Args:
            prompt (str): The prompt to display to the user
            valid_options (list): List of valid options (can include numbers as strings,
                                and special options like 't', 'f', etc.)

        Returns:
            str: The validated user input
        """
        while True:
            user_input = input(prompt).strip().lower()

            # Check if the input is empty
            if user_input == "":
                print("Por favor, insira uma escolha válida.")
                continue

            # Check if the input is a valid special command
            if user_input in [option.lower() for option in valid_options if isinstance(option, str)]:
                return user_input

            # Check if the input is a valid number within range
            if user_input.isdigit():
                num = int(user_input)
                if str(num) in valid_options:
                    return user_input

            # If we get here, the input is not valid
            options_display = ", ".join(valid_options)
            print(f"Escolha inválida. Por favor, escolha uma dessas opções: {options_display}")

    def get_yes_no_input(self, prompt):
        """
        Gets a yes/no input from the user.

        Args:
            prompt (str): The prompt to display to the user

        Returns:
            bool: True if yes, False if no
        """
        valid_yes = ['s', 'sim', 'y', 'yes']
        valid_no = ['n', 'nao', 'não', 'no']
        valid_options = valid_yes + valid_no

        while True:
            user_input = input(prompt).strip().lower()

            if user_input in valid_yes:
                return True
            elif user_input in valid_no:
                return False
            else:
                print("Por favor, responda com 's' para sim ou 'n' para não.")

    def determinar_manilha(self):
        """
        Determina a carta "vira" e a manilha correspondente.

        Returns:
            tuple: (carta_vira, manilha_rank)
                - carta_vira (str): A carta virada que determina a manilha
                - manilha_rank (str): O valor da manilha (4, 5, 6, 7, Q, J, K, A, 2, 3)
        """
        # Os valores das cartas em ordem
        valores = ['4', '5', '6', '7', 'Q', 'J', 'K', 'A', '2', '3']
        naipes = ['♦', '♠', '♥', '♣']

        # Escolhe uma carta aleatória como "vira"
        naipe_vira = random.choice(naipes)
        valor_vira = random.choice(valores)
        carta_vira = valor_vira + naipe_vira

        # Determina qual será o valor da manilha (próximo valor após o "vira")
        indice_atual = valores.index(valor_vira)
        indice_manilha = (indice_atual + 1) % len(valores)
        manilha = valores[indice_manilha]

        return carta_vira, manilha

    def valor_carta(self, carta):
        # Os valores das cartas em ordem crescente
        valores = {'4': 1, '5': 2, '6': 3, '7': 4, 'Q': 5, 'J': 6, 'K': 7, 'A': 8, '2': 9, '3': 10}
        return valores.get(carta[0], 0)

    def vencedor_rodada(self, carta_jogador, carta_oponente, manilha):
        valor_jogador = self.valor_carta(carta_jogador)
        valor_oponente = self.valor_carta(carta_oponente)

        # Verifica se as cartas são manilhas
        if carta_jogador[0] == manilha[0]:
            valor_jogador += 10
        if carta_oponente[0] == manilha[0]:
            valor_oponente += 10

        if valor_jogador > valor_oponente:
            return "Jogador"
        elif valor_oponente > valor_jogador:
            return "Oponente"
        else:
            # Desempate por naipe apenas se as duas cartas forem manilhas
            if carta_jogador[0] == manilha[0] and carta_oponente[0] == manilha[0]:
                naipes = {'♣': 4, '♥': 3, '♠': 2, '♦': 1}
                if naipes[carta_jogador[1]] > naipes[carta_oponente[1]]:
                    return "Jogador"
                else:
                    return "Oponente"
            else:
                return "Empate"

    def exibir_mao(self, mao):
        print("Suas cartas:")
        for i, carta in enumerate(mao):
            carta_ascii = self.cards_database[carta]
            print(f"{i + 1}:")
            print(carta_ascii)

    def get_card_choice(self, mao, allow_truco=True, allow_fugir=True):
        """
        Gets a valid card choice from the player.

        Args:
            mao (list): The player's hand
            allow_truco (bool): Whether to allow the "truco" option
            allow_fugir (bool): Whether to allow the "fugir" option

        Returns:
            str: The validated choice (number as string, 't', or 'f')
        """
        valid_options = [str(i + 1) for i in range(len(mao))]

        if allow_truco:
            valid_options.append('t')
            print("T: Truco")
        if allow_fugir:
            valid_options.append('f')
            print("F: Fugir")

        prompt_options = ""
        if allow_truco:
            prompt_options += ", T (Truco)"
        if allow_fugir:
            prompt_options += ", F (Fugir)"

        prompt = f"Escolha o número da carta que deseja jogar{prompt_options}: "

        return self.get_valid_input(prompt, valid_options)

    def fill_cards_database(self):
        """
        Fill the cards database with ASCII art for all cards.
        """
        cards_database = {}
        ranks = ['4', '5', '6', '7', 'Q', 'J', 'K', 'A', '2', '3']
        suits = ['♠', '♥', '♦', '♣']  # Unicode suits

        for rank in ranks:
            for suit in suits:
                card_code = f"{rank}{suit}"
                card_ascii = self.generate_card_ascii(rank, suit)
                cards_database[card_code] = card_ascii

        return cards_database

    def generate_card_ascii(self, rank, suit):
        """
        Generate ASCII art for a card with given rank and suit.
        """
        # Define the top and bottom lines of the card
        top_bottom_line = "┌───────┐"
        rank_line = f"│ {rank:<2}    │"
        suit_line = f"│   {suit}   │"
        middle_line = "│       │"
        bottom_rank_line = f"│     {rank} │"
        bottom_bottom_line = "└───────┘"

        # Concatenate all lines to form the ASCII art
        card_ascii = '\n'.join(
            [top_bottom_line, rank_line, suit_line, middle_line, suit_line, bottom_rank_line, bottom_bottom_line])

        return card_ascii

    def display_intro(self):
        banner = '''
         ______   ______     __  __     ______     ______    
        /\\__  _\\ /\\  == \\   /\\ \\/\\ \\   /\\  ___\\   /\\  __ \\   
        \\/_/\\ \\/ \\ \\  __<   \\ \\ \\_\\ \\  \\ \\ \\____  \\ \\ \\/\\ \\  
           \\ \\_\\  \\ \\_\\ \\_\\  \\ \\_____\\  \\ \\_____\\  \\ \\_____\\ 
            \\/_/   \\/_/ /_/   \\/_____/   \\/_____/   \\/_____/ 
        '''
        # Split the banner into lines and print with delay
        lines = banner.split('\n')
        for line in lines:
            print(line)
            time.sleep(0.1)

        banner2 = r'''
                .------..------..------..------.
                |2.--. ||0.--. ||0.--. ||0.--. |
                | (\/) || :/\: || :/\: || :/\: |
                | :\/: || :\/: || :\/: || :\/: |
                | '--'2|| '--'0|| '--'0|| '--'0|
                `------'`------'`------'`------'
                .------..------..------..------.
                | .--. || .--. || .--. || .--. |
                | :/\: || :(): || :/\: || (\/) |
                | (__) || ()() || :\/: || :\/: |
                | '--' || '--' || '--' || '--' |
                `------'`------'`------'`------'          
                    '''
        print(banner2)

        print(
            "                             ♠♥♦♣\n                          Truco 2000\n                       Um jogo em python\n                           por mama\n                             ♠♥♦♣")

    def jogar(self):
        """Main game loop function"""
        while True:
            self.display_intro()

            jogar_novamente = self.get_yes_no_input("E aí... Que tal jogar um truquinho? (s/n): ")
            if not jogar_novamente:
                print(self.ursinho_tchau)
                time.sleep(3)
                break

            self.baralho = self.baralho_original.copy()
            self.embaralhar()
            self.pontos_jogador = 0
            self.pontos_oponente = 0

            # Reset who starts for a new game - player always starts the first hand
            self.player_starts_hand = True

            while self.pontos_jogador < 12 and self.pontos_oponente < 12:
                self.jogar_mao()

            # Verifica o vencedor do jogo
            if self.pontos_jogador >= 12:
                print("Parabéns! Você venceu o jogo! :D")
            elif self.pontos_oponente >= 12:
                print("Ah que pena, você perdeu. :(")
            else:
                print("O jogo empatou!")

            # Pergunta se deseja jogar novamente
            jogar_novamente = self.get_yes_no_input("Deseja jogar novamente? (s/n): ")
            if not jogar_novamente:
                print(self.ursinho_tchau)
                break

    def jogar_mao(self):
        """Plays one hand of the game"""
        self.reiniciar_baralho()

        # Reset who starts each round for this hand - based on who won the last hand
        self.player_starts_round = self.player_starts_hand

        # Show who starts this hand
        starter = "Você" if self.player_starts_hand else "Oponente"
        print(f"\n{starter} começa esta mão.")

        # Determina a manilha para a rodada
        carta_vira, manilha = self.determinar_manilha()

        print("\nCarta virada:")
        print(self.cards_database[carta_vira])
        print(f"Manilhas desta mão: {manilha}♣, {manilha}♥, {manilha}♠, {manilha}♦")

        # Distribui as cartas para o jogador e o oponente
        mao_do_jogador = self.distribuir_cartas(3)
        mao_do_oponente = self.distribuir_cartas(3)

        # conta os resultados da rodada
        resultados_rodadas = []
        primeira_vitoria = None  # quem vence a primeira mão não empate (caminhão)

        # Variável para contar as vitórias
        vitorias_jogador = 0
        vitorias_oponente = 0

        # Verifica se truco foi usado
        truco_ladrao = False
        player_ran_from_truco = False  # Flag to track if player ran from truco
        opponent_ran_from_truco = False  # Flag to track if opponent ran from truco

        for rodada in range(3):
            # Play a single round
            resultado = self.jogar_rodada(rodada, mao_do_jogador, mao_do_oponente,
                                          manilha, resultados_rodadas, primeira_vitoria,
                                          truco_ladrao, self.player_starts_round)

            # Unpack the results
            vencedor, mao_do_jogador, mao_do_oponente, truco_result = resultado

            # Check if someone ran from truco
            if isinstance(truco_result, tuple) and len(truco_result) == 2:
                # This is a special result indicating someone ran from truco
                truco_ladrao = truco_result[0]

                if truco_result[1] == "player_ran":
                    player_ran_from_truco = True
                    truco_ladrao = False # Reset truco_ladrao since player ran
                    vencedor = "Oponente"  # Override the winner
                    break  # End the hand immediately
                elif truco_result[1] == "opponent_ran":
                    opponent_ran_from_truco = True
                    truco_ladrao = False  # Reset truco_ladrao since opponent ran
                    vencedor = "Jogador"  # Override the winner
                    break  # End the hand immediately
            else:
                # Normal round result
                truco_ladrao = truco_result

            # Update who starts the next round based on the winner of this round
            if vencedor == "Jogador":
                self.player_starts_round = True
            elif vencedor == "Oponente":
                self.player_starts_round = False
            # If it's a draw, player_starts_round remains unchanged

            # Update results and counters
            resultados_rodadas.append(vencedor)

            # Register first non-draw winner
            if vencedor != "Empate" and primeira_vitoria is None:
                primeira_vitoria = vencedor

            # Count victories
            if vencedor == "Jogador":
                vitorias_jogador += 1
            elif vencedor == "Oponente":
                vitorias_oponente += 1

            # Check if we have enough information to determine the hand winner
            end_hand, winner_message = self.check_hand_winner(rodada, resultados_rodadas,
                                                              vitorias_jogador, vitorias_oponente,
                                                              primeira_vitoria)

            if end_hand:
                if "Jogador" in winner_message:
                    vitorias_jogador = 2
                    self.player_starts_hand = True  # Player starts next hand
                elif "Oponente" in winner_message:
                    vitorias_oponente = 2
                    self.player_starts_hand = False  # Opponent starts next hand
                else:
                    # It was a complete draw - keep the same starter
                    pass

                print(winner_message)
                break

        # Handle running from truco specifically
        if player_ran_from_truco:
            print("Fuééén! Você correu do truco! Oponente venceu a mão!")
            vitorias_oponente = 2
            self.player_starts_hand = False  # Opponent starts next hand
        elif opponent_ran_from_truco:
            print("Fuééén! Oponente correu do truco! Você venceu a mão!")
            vitorias_jogador = 2
            self.player_starts_hand = True  # Player starts next hand

        # Update points based on the winner of the hand
        if vitorias_jogador > vitorias_oponente:
            # Add points to winning player
            if truco_ladrao:
                self.pontos_jogador += 3
                print(f"Você venceu a mão e ganhou 3 pontos!")
            else:
                self.pontos_jogador += 1
                print(f"Você venceu a mão e ganhou 1 ponto!")
            self.player_starts_hand = True  # Ensure player starts next hand
        elif vitorias_oponente > vitorias_jogador:
            # Add points to opponent
            if truco_ladrao:
                self.pontos_oponente += 3
                print(f"Oponente venceu a mão e ganhou 3 pontos!")
            else:
                self.pontos_oponente += 1
                print(f"Oponente venceu a mão e ganhou 1 ponto!")
            self.player_starts_hand = False  # Ensure opponent starts next hand
        else:
            # Complete draw (all three rounds were draws)
            print("Mão empatada! Nenhum ponto atribuído.")

        print(f"\nPontuação:")
        print(f"Jogador | Pontos: {self.pontos_jogador}")
        print(f"Oponente | Pontos: {self.pontos_oponente}")

        # Show who starts the next hand
        next_starter = "Você" if self.player_starts_hand else "Oponente"
        print(f"\n{next_starter} começará a próxima mão.")

        # Small pause before next hand
        time.sleep(1.5)

    def jogar_rodada(self, rodada, mao_do_jogador, mao_do_oponente, manilha, resultados_rodadas, primeira_vitoria,
                     truco_ladrao, player_starts):
        """Plays a single round and returns the updated game state"""
        print(f"\nRodada {rodada + 1}:")

        # Display current game state
        if rodada > 0:
            print("Status da mão:")
            for i, resultado in enumerate(resultados_rodadas):
                print(f"Rodada {i + 1}: {resultado}")

            if primeira_vitoria:
                if rodada == 1 and resultados_rodadas[0] != "Empate":
                    print(f"Se esta rodada for empate, {primeira_vitoria} vence a mão!")
                elif rodada == 1 and resultados_rodadas[0] == "Empate":
                    print(f"Como a primeira rodada foi empate, quem vencer esta rodada ganha a mão!")

        # Show who starts this round
        starter = "Você" if player_starts else "Oponente"
        print(f"{starter} começa esta rodada.")

        # If opponent starts, they play first
        carta_oponente = None
        if not player_starts:
            # Check if opponent has cards left
            if mao_do_oponente:
                carta_oponente = random.choice(mao_do_oponente)
                mao_do_oponente.remove(carta_oponente)
                print("O oponente jogou:")
                print(self.cards_database[carta_oponente])
            else:
                print("Erro: Oponente não tem cartas para jogar!")
                return "Jogador", mao_do_jogador, [], truco_ladrao

        # Show player's hand and get choice
        self.exibir_mao(mao_do_jogador)
        escolha_jogador = self.get_card_choice(mao_do_jogador, allow_truco=(not truco_ladrao),
                                               allow_fugir=(truco_ladrao))

        # Handle player's choice
        if escolha_jogador.lower() == 'f':
            print("Arregou!")
            # Special tuple return value to indicate player ran from truco
            return "Oponente", mao_do_jogador, mao_do_oponente, (truco_ladrao, "player_ran")
        elif escolha_jogador.lower() == 't':
            print("-TRUUUUCO!\n")

            # Opponent decides whether to accept the truco or run away
            aceita_truco = random.choice([True, False])

            if aceita_truco:
                print(" -Cai dentro mané!!!")
                truco_ladrao = True
                # Now the player must choose a card (with option to run)
                self.exibir_mao(mao_do_jogador)
                escolha_jogador = self.get_card_choice(mao_do_jogador, allow_truco=False, allow_fugir=True)
                if escolha_jogador.lower() == 'f':
                    print("Arregou!")
                    # Special tuple return value to indicate player ran from truco
                    return "Oponente", mao_do_jogador, mao_do_oponente, (truco_ladrao, "player_ran")
            else:
                print(" -Não tô afim, toma essa mão aí!")
                # Opponent runs away, player wins the hand
                # Special tuple return value to indicate opponent ran from truco
                return "Jogador", mao_do_jogador, mao_do_oponente, (True, "opponent_ran")

        # Play the player's card
        carta_index = int(escolha_jogador) - 1
        carta_jogador = mao_do_jogador.pop(carta_index)

        # Always display player's card after they play it
        print("O jogador jogou:")
        print(self.cards_database[carta_jogador])

        # If player starts, opponent plays after
        if player_starts:
            # Make sure the opponent has cards to play
            if mao_do_oponente:
                carta_oponente = random.choice(mao_do_oponente)
                mao_do_oponente.remove(carta_oponente)
                print("O oponente jogou:")
                print(self.cards_database[carta_oponente])
            else:
                print("Erro: Oponente não tem cartas para jogar!")
                return "Jogador", mao_do_jogador, [], truco_ladrao

        # Determine winner
        vencedor = self.vencedor_rodada(carta_jogador, carta_oponente, manilha)
        print("Vencedor da rodada:", vencedor)

        # Return a normal result (not from running away)
        return vencedor, mao_do_jogador, mao_do_oponente, truco_ladrao

    def check_hand_winner(self, rodada, resultados_rodadas, vitorias_jogador, vitorias_oponente, primeira_vitoria):
        """Checks if there's a winner for the current hand"""
        if rodada == 0:  # First round
            # No decision yet, continue to next round
            return False, ""
        elif rodada == 1:  # Second round
            if resultados_rodadas[0] != "Empate":  # First round wasn't a draw
                # If same player won both rounds
                if resultados_rodadas[0] == resultados_rodadas[1] and resultados_rodadas[1] != "Empate":
                    if resultados_rodadas[0] == "Jogador":
                        return True, "Você venceu a mão por ganhar duas rodadas seguidas!"
                    else:
                        return True, "Oponente venceu a mão por ganhar duas rodadas seguidas!"
                # If first round was won and second is a draw
                elif resultados_rodadas[1] == "Empate":
                    if resultados_rodadas[0] == "Jogador":
                        return True, "Você venceu a mão! (Primeira rodada ganha + segunda empatada)"
                    else:
                        return True, "Oponente venceu a mão! (Primeira rodada ganha + segunda empatada)"
            else:  # First round was a draw
                if resultados_rodadas[1] != "Empate":  # Second round isn't a draw
                    if resultados_rodadas[1] == "Jogador":
                        return True, "Você venceu a mão! (Primeira rodada empatada, segunda ganha)"
                    else:
                        return True, "Oponente venceu a mão! (Primeira rodada empatada, segunda ganha)"
        elif rodada == 2:  # Third round - only reached if we haven't determined a winner yet
            # If the third round is a draw
            if resultados_rodadas[2] == "Empate":
                # If one player has more wins (1 vs 0), they win
                if vitorias_jogador > vitorias_oponente:
                    return True, "Você venceu a mão com uma vitória e duas rodadas empatadas!"
                elif vitorias_oponente > vitorias_jogador:
                    return True, "Oponente venceu a mão com uma vitória e duas rodadas empatadas!"
                # If it's 1-1 or 0-0, use primeira_vitoria rule
                else:
                    if primeira_vitoria == "Jogador":
                        return True, "Você venceu a mão por ter ganho a primeira rodada não empatada!"
                    elif primeira_vitoria == "Oponente":
                        return True, "Oponente venceu a mão por ter ganho a primeira rodada não empatada!"
                    else:
                        return True, "Todas as rodadas empataram! A mão é considerada um empate."
            else:
                # Third round has a winner
                if vitorias_jogador > vitorias_oponente:
                    return True, "Você venceu a mão!"
                elif vitorias_oponente > vitorias_jogador:
                    return True, "Oponente venceu a mão!"
                # If it's 1-1, winner of the third round wins
                else:
                    if resultados_rodadas[2] == "Jogador":
                        return True, "Você venceu a mão na terceira rodada!"
                    else:
                        return True, "Oponente venceu a mão na terceira rodada!"

        # If we get here, we don't have enough information to determine a winner yet
        return False, ""

if __name__ == "__main__":
    game = TrucoGame()
    game.jogar()
