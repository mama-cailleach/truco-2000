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

        # Truco state tracking
        self.current_hand_value = 1  # Current value of the hand (1, 3, 6, 9, 12)
        self.last_raiser = None  # Who made the last raise ("Jogador" or "Oponente")
        self.truco_names = {1: "Normal", 3: "Truco", 6: "Retruco", 9: "Vale 9", 12: "Vale 12"}

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

    def get_truco_response(self, current_value, raiser):
        """
        Gets the player's response to a truco call: run, accept, or reraise
        
        Args:
            current_value (int): Current value being proposed (3, 6, 9, 12)
            raiser (str): Who made the truco call ("Oponente")
        
        Returns:
            str: 'run', 'accept', or 'reraise'
        """
        next_value = current_value + 3
        can_reraise = next_value <= 12
        
        print(f"Oponente pediu {self.truco_names[current_value]} (vale {current_value} pontos)")
        
        valid_options = ['f', 'a']  # fugir, aceitar
        prompt = "F: Fugir, A: Aceitar"
        
        if can_reraise:
            valid_options.append('r')
            prompt += f", R: {self.truco_names[next_value]} (vale {next_value})"
        
        prompt += ": "
        
        choice = self.get_valid_input(prompt, valid_options)
        
        if choice == 'f':
            return 'run'
        elif choice == 'a':
            return 'accept'
        elif choice == 'r':
            return 'reraise'

    def get_opponent_truco_response(self, current_value):
        """
        Gets the opponent's response to a truco call (random for now)
        
        Args:
            current_value (int): Current value being proposed
        
        Returns:
            str: 'run', 'accept', or 'reraise'
        """
        next_value = current_value + 3
        can_reraise = next_value <= 12
        
        if can_reraise:
            # Random choice between all three options
            return random.choice(['run', 'accept', 'reraise'])
        else:
            # Can only run or accept at max value
            return random.choice(['run', 'accept'])

    def handle_truco_sequence(self, initiator, current_value=3, mao_do_jogador=None):
        """
        Handles a complete truco sequence until someone accepts or runs
        
        Args:
            initiator (str): Who started the truco ("Jogador" or "Oponente")
            current_value (int): Starting value of the truco
            mao_do_jogador (list): Player's hand for display purposes
        
        Returns:
            tuple: (accepted, final_value, who_ran, final_raiser)
        """
        raiser = initiator
        value = current_value
        
        while value <= 12:
            if raiser == "Oponente":
                # Player responds to opponent's truco/reraise
                if mao_do_jogador:  # Only show hand if provided
                    self.exibir_mao(mao_do_jogador)
                response = self.get_truco_response(value, raiser)
                
                if response == 'run':
                    print(f"Você correu do {self.truco_names[value]}!")
                    return False, value, "Jogador", raiser
                elif response == 'accept':
                    print(f"Você aceitou o {self.truco_names[value]}! Agora vale {value} pontos.")
                    return True, value, None, raiser
                elif response == 'reraise':
                    value += 3
                    raiser = "Jogador"
                    print(f"Você pediu {self.truco_names[value]}!")
                    if value > 12:
                        break
            else:
                # Opponent responds to player's truco/reraise
                response = self.get_opponent_truco_response(value)
                
                if response == 'run':
                    print(f"Oponente correu do {self.truco_names[value]}!")
                    return False, value, "Oponente", raiser
                elif response == 'accept':
                    print(f"Oponente aceitou o {self.truco_names[value]}! Agora vale {value} pontos.")
                    return True, value, None, raiser
                elif response == 'reraise':
                    value += 3
                    raiser = "Oponente"
                    print(f"Oponente pediu {self.truco_names[value]}!")
                    if value > 12:
                        break
        
        # Should never reach here, but safety fallback
        return True, value, None, raiser

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

    def get_card_choice(self, mao, allow_truco=True, allow_fugir=True, current_hand_value=1, last_raiser=None):
        """
        Gets a valid card choice from the player.

        Args:
            mao (list): The player's hand
            allow_truco (bool): Whether to allow the "truco" option
            allow_fugir (bool): Whether to allow the "fugir" option
            current_hand_value (int): Current value of the hand
            last_raiser (str): Who made the last raise

        Returns:
            str: The validated choice (number as string, 't', or 'f')
        """
        valid_options = [str(i + 1) for i in range(len(mao))]

        # Check if player can call truco/reraise
        # Reset restrictions if current hand value is 1 (no active truco)
        can_truco = (allow_truco and
                     current_hand_value < 12 and
                     (current_hand_value == 1 or last_raiser != "Jogador"))

        if can_truco:
            valid_options.append('t')
            next_value = current_hand_value + 3 if current_hand_value > 1 else 3
            print(f"T: {self.truco_names[next_value]}")
        elif allow_truco and current_hand_value > 1 and last_raiser == "Jogador":
            print("(Você já pediu o último truco/reraise desta mão)")

        if allow_fugir:
            valid_options.append('f')
            print("F: Fugir")

        prompt_options = ""
        if can_truco:
            next_value = current_hand_value + 3 if current_hand_value > 1 else 3
            prompt_options += f", T ({self.truco_names[next_value]})"
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

        # Reset truco state for new hand
        self.current_hand_value = 1
        self.last_raiser = None

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

        for rodada in range(3):
            # Play a single round
            resultado = self.jogar_rodada(rodada, mao_do_jogador, mao_do_oponente,
                                        manilha, resultados_rodadas, primeira_vitoria,
                                        self.current_hand_value, self.last_raiser,
                                        self.player_starts_round)

            # Unpack the results - now includes final_raiser from truco sequences
            vencedor, mao_do_jogador, mao_do_oponente, hand_value, last_raiser, special_result = resultado

            # Update truco state
            self.current_hand_value = hand_value
            self.last_raiser = last_raiser

            # Check if someone ran from truco - this ends the hand immediately
            if special_result:
                if special_result[0] == "player_ran":
                    print("Fuééén! Você correu do truco! Oponente venceu a mão!")
                    self.pontos_oponente += self.current_hand_value
                    print(f"Oponente venceu a mão e ganhou {self.current_hand_value} pontos!")
                    self.player_starts_hand = False  # Opponent starts next hand
                    
                    # Show final score and return immediately
                    print(f"\nPontuação:")
                    print(f"Jogador | Pontos: {self.pontos_jogador}")
                    print(f"Oponente | Pontos: {self.pontos_oponente}")
                    
                    next_starter = "Você" if self.player_starts_hand else "Oponente"
                    print(f"\n{next_starter} começará a próxima mão.")
                    time.sleep(1.5)
                    return  # End the hand immediately
                    
                elif special_result[0] == "opponent_ran":
                    print("Fuééén! Oponente correu do truco! Você venceu a mão!")
                    self.pontos_jogador += self.current_hand_value
                    print(f"Você venceu a mão e ganhou {self.current_hand_value} pontos!")
                    self.player_starts_hand = True  # Player starts next hand
                    
                    # Show final score and return immediately
                    print(f"\nPontuação:")
                    print(f"Jogador | Pontos: {self.pontos_jogador}")
                    print(f"Oponente | Pontos: {self.pontos_oponente}")
                    
                    next_starter = "Você" if self.player_starts_hand else "Oponente"
                    print(f"\n{next_starter} começará a próxima mão.")
                    time.sleep(1.5)
                    return  # End the hand immediately

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

        # This code only runs if the hand ended normally (not from truco running)
        # Update points based on the winner of the hand
        if vitorias_jogador > vitorias_oponente:
            # Add points to winning player
            self.pontos_jogador += self.current_hand_value
            print(f"Você venceu a mão e ganhou {self.current_hand_value} pontos!")
            self.player_starts_hand = True  # Ensure player starts next hand
        elif vitorias_oponente > vitorias_jogador:
            # Add points to opponent
            self.pontos_oponente += self.current_hand_value
            print(f"Oponente venceu a mão e ganhou {self.current_hand_value} pontos!")
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

    def jogar_rodada(self, rodada, mao_do_jogador, mao_do_oponente, manilha, resultados_rodadas, 
                 primeira_vitoria, current_hand_value, last_raiser, player_starts):
        """Plays a single round and returns the updated game state"""
        print(f"\nRodada {rodada + 1}:")
        
        # DEBUG: Print truco state at start of round
        print(f"DEBUG - Estado do truco no início da rodada:")
        print(f"  current_hand_value: {current_hand_value}")
        print(f"  last_raiser: {last_raiser}")
        print(f"  truco_name: {self.truco_names[current_hand_value]}")

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

        carta_oponente = None
        if not player_starts:
            # Opponent's turn - can truco/reraise if allowed
            # Can call truco if: no truco active OR opponent wasn't the last one to raise in current truco
            can_opponent_truco = (current_hand_value < 12 and 
                                (current_hand_value == 1 or last_raiser != "Oponente"))

            print(f"DEBUG - Oponente pode pedir truco? {can_opponent_truco}")

            if can_opponent_truco and mao_do_oponente:
                oponente_acao = random.choice(['truco', 'jogar'])
                print(f"DEBUG - Ação do oponente: {oponente_acao}")
                
                if oponente_acao == 'truco':
                    next_value = current_hand_value + 3 if current_hand_value > 1 else 3
                    print(f"Oponente pediu {self.truco_names[next_value]}!")

                    # Handle the truco sequence - pass mao_do_jogador
                    accepted, final_value, who_ran, final_raiser = self.handle_truco_sequence("Oponente", next_value, mao_do_jogador)

                    print(f"DEBUG - Resultado do truco do oponente:")
                    print(f"  accepted: {accepted}, final_value: {final_value}")
                    print(f"  who_ran: {who_ran}, final_raiser: {final_raiser}")

                    if who_ran:
                        return ("Oponente" if who_ran == "Jogador" else "Jogador", 
                                mao_do_jogador, mao_do_oponente, 
                                final_value, final_raiser, (who_ran + "_ran",))
                    
                    # Update state if truco was accepted - use final_raiser from the sequence
                    current_hand_value = final_value
                    last_raiser = final_raiser
                    
                    print(f"DEBUG - Estado atualizado após truco do oponente:")
                    print(f"  current_hand_value: {current_hand_value}")
                    print(f"  last_raiser: {last_raiser}")
            
            # Opponent plays card (whether truco was called or not)
            if mao_do_oponente:
                carta_oponente = random.choice(mao_do_oponente)
                mao_do_oponente.remove(carta_oponente)
                print("O oponente jogou:")
                print(self.cards_database[carta_oponente])
            else:
                print("Erro: Oponente não tem cartas para jogar!")
                return "Jogador", mao_do_jogador, [], current_hand_value, last_raiser, None

        # Show player's hand and get choice
        self.exibir_mao(mao_do_jogador)
        
        print(f"DEBUG - Estado antes da escolha do jogador:")
        print(f"  current_hand_value: {current_hand_value}")
        print(f"  last_raiser: {last_raiser}")
        
        escolha_jogador = self.get_card_choice(mao_do_jogador, allow_truco=(current_hand_value < 12),
                                            allow_fugir=(current_hand_value > 1),
                                            current_hand_value=current_hand_value,
                                            last_raiser=last_raiser)

        # Handle player's choice
        if escolha_jogador.lower() == 'f':
            print("Arregou!")
            return ("Oponente", mao_do_jogador, mao_do_oponente, 
                    current_hand_value, last_raiser, ("player_ran",))
        elif escolha_jogador.lower() == 't':
            # Player called truco/reraise
            next_value = current_hand_value + 3 if current_hand_value > 1 else 3
            print(f"Você pediu {self.truco_names[next_value]}!")
            
            # Handle the truco sequence - pass mao_do_jogador
            accepted, final_value, who_ran, final_raiser = self.handle_truco_sequence("Jogador", next_value, mao_do_jogador)
            
            print(f"DEBUG - Resultado do truco do jogador:")
            print(f"  accepted: {accepted}, final_value: {final_value}")
            print(f"  who_ran: {who_ran}, final_raiser: {final_raiser}")
            
            if who_ran:
                return ("Jogador" if who_ran == "Oponente" else "Oponente",
                        mao_do_jogador, mao_do_oponente,
                        final_value, final_raiser, (who_ran + "_ran",))
            
            # Update state if truco was accepted - use final_raiser from the sequence
            current_hand_value = final_value
            last_raiser = final_raiser
            
            print(f"DEBUG - Estado atualizado após truco do jogador:")
            print(f"  current_hand_value: {current_hand_value}")
            print(f"  last_raiser: {last_raiser}")
            
            # Player must now play a card
            self.exibir_mao(mao_do_jogador)
            escolha_jogador = self.get_card_choice(mao_do_jogador, 
                                                allow_truco=False,
                                                allow_fugir=(current_hand_value > 1),
                                                current_hand_value=current_hand_value,
                                                last_raiser=last_raiser)
            if escolha_jogador.lower() == 'f':
                print("Arregou!")
                return ("Oponente", mao_do_jogador, mao_do_oponente,
                        current_hand_value, last_raiser, ("player_ran",))

        # Play the card
        carta_index = int(escolha_jogador) - 1
        carta_jogador = mao_do_jogador.pop(carta_index)
        print("O jogador jogou:")
        print(self.cards_database[carta_jogador])

        # Handle opponent playing after player if needed
        if player_starts and mao_do_oponente:
            carta_oponente = random.choice(mao_do_oponente)
            mao_do_oponente.remove(carta_oponente)
            print("O oponente jogou:")
            print(self.cards_database[carta_oponente])

        # Determine winner
        vencedor = self.vencedor_rodada(carta_jogador, carta_oponente, manilha)
        print("Vencedor da rodada:", vencedor)

        print(f"DEBUG - Estado final da rodada sendo retornado:")
        print(f"  current_hand_value: {current_hand_value}")
        print(f"  last_raiser: {last_raiser}")

        return (vencedor, mao_do_jogador, mao_do_oponente, 
                current_hand_value, last_raiser, None)

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