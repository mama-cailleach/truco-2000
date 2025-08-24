import random
import time

ursinho = '''
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



# Define as cartas do baralho
baralho = ['4♣', '5♣', '6♣', '7♣', 'Q♣', 'J♣', 'K♣', 'A♣', '2♣', '3♣',
           '4♥', '5♥', '6♥', '7♥', 'Q♥', 'J♥', 'K♥', 'A♥', '2♥', '3♥',
           '4♦', '5♦', '6♦', '7♦', 'Q♦', 'J♦', 'K♦', 'A♦', '2♦', '3♦',
           '4♠', '5♠', '6♠', '7♠', 'Q♠', 'J♠', 'K♠', 'A♠', '2♠', '3♠']

# Crie uma cópia do baralho original
baralho_original = baralho.copy()

# Função para embaralhar o baralho
def embaralhar():
    random.shuffle(baralho)


def reiniciar_baralho():
    global baralho
    baralho = ['4♣', '5♣', '6♣', '7♣', 'Q♣', 'J♣', 'K♣', 'A♣',
               '4♥', '5♥', '6♥', '7♥', 'Q♥', 'J♥', 'K♥', 'A♥',
               '4♦', '5♦', '6♦', '7♦', 'Q♦', 'J♦', 'K♦', 'A♦',
               '4♠', '5♠', '6♠', '7♠', 'Q♠', 'J♠', 'K♠', 'A♠']
    embaralhar()

# Função para distribuir cartas
def distribuir_cartas(quantidade):
    mao = []
    for _ in range(quantidade):
        carta = baralho.pop()
        mao.append(carta)
    return mao

# Função para calcular o valor da carta
def valor_carta(carta):
    valores = {'4': 1, '5': 2, '6': 3, '7': 4, 'Q': 5, 'J': 6, 'K': 7, 'A': 8, '2': 9, '3': 10}
    return valores.get(carta[0], 0)

# Função para determinar quem ganha a rodada
def vencedor_rodada(carta_jogador, carta_oponente, manilha):
    valor_jogador = valor_carta(carta_jogador)
    valor_oponente = valor_carta(carta_oponente)

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

# Função para gerar a imagem ASCII de uma carta
def generate_card_ascii(rank, suit):
    """
    Generate ASCII art for a card with given rank and suit.
    """
    # Define the top and bottom lines of the card
    top_bottom_line = "┌───────┐"
    rank_line = f"│ {rank:<2}    │"
    suit_line = f"│   {suit}   │"
    middle_line = "│       │"
    bottom_rank_line = f"│    {rank}  │"
    bottom_bottom_line = "└───────┘"

    # Concatenate all lines to form the ASCII art
    card_ascii = '\n'.join(
        [top_bottom_line, rank_line, suit_line, middle_line, suit_line, rank_line, bottom_bottom_line])

    return card_ascii

# Função para preencher o banco de dados de cartas com suas imagens ASCII
def fill_cards_database():
    """
    Fill the cards database with ASCII art for all cards.
    """
    cards_database = {}
    ranks = ['4', '5', '6', '7', 'Q', 'J', 'K', 'A', '2', '3']  # Alterado para cartas usadas no jogo de truco
    suits = ['♠', '♥', '♦', '♣']

    for rank in ranks:
        for suit in suits:
            card_code = f"{rank}{suit}"
            card_ascii = generate_card_ascii(rank, suit)
            cards_database[card_code] = card_ascii

    return cards_database

# Inicializa o banco de dados de cartas
cards_database = fill_cards_database()

# Função para exibir a mão do jogador
def exibir_mao(mao):
    print("Suas cartas:")
    for i, carta in enumerate(mao):
        carta_ascii = cards_database[carta]
        print(f"{i + 1}:")
        print(carta_ascii)
    print("T: Truco")  # Opção de trucar
    print("F: Fugir") #Opção de fugir

# Função principal do jogo
def truco():
    while True:
        banner = '''
         ______   ______     __  __     ______     ______    
        /\\__  _\\ /\\  == \\   /\\ \\/\\ \\   /\\  ___\\   /\\  __ \\   
        \\/_/\\ \\/ \\ \\  __<   \\ \\ \\_\\ \\  \\ \\ \\____  \\ \\ \\/\\ \\  
           \\ \\_\\  \\ \\_\\ \\_\\  \\ \\_____\\  \\ \\_____\\  \\ \\_____\\ 
            \\/_/   \\/_/ /_/   \\/_____/   \\/_____/   \\/_____/ 
        '''
        # Split the banner into lines
        lines = banner.split('\n')

        # Print each line with a delay
        for line in lines:
            print(line)
            time.sleep(0.1)  # Adjust the delay time as needed

        banner2 = '''
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

        print("                             ♠♥♦♣\n                          Truco 2000\n                       Um jogo em python\n                           por mama\n                             ♠♥♦♣")

        ursinho_tchau = '''
  (c).-.(c)   ___________________
   / ._. \   | Ok! Então tchau!  |
   \( Y )/   |___________________|
    /'-'\    
      
                        '''
        jogar_novamente = input("E aí... Que tal jogar um truquinho? (s/n): ")
        if jogar_novamente.lower() != 's':
            print("Ok, então tchau!")
            print(ursinho_tchau)
            break

        baralho = baralho_original.copy()
        embaralhar()
        pontos_jogador = 0
        pontos_oponente = 0

        while pontos_jogador < 12 and pontos_oponente < 12:
            reiniciar_baralho()
            # Sorteia a manilha para a rodada
            baralho_paus = ['4♣', '5♣', '6♣', '7♣', 'Q♣', 'J♣', 'K♣', 'A♣', '2♣', '3♣']
            manilha = random.choice(baralho_paus)
            print(f"\nManilha da rodada: {manilha}")

            # Distribui as cartas para o jogador e o oponente
            mao_do_jogador = distribuir_cartas(3)
            mao_do_oponente = distribuir_cartas(3)

            # Variável para contar as vitórias
            vitorias_jogador = 0
            vitorias_oponente = 0

            # Verifica se truco foi usado
            truco_ladrao = False

            for rodada in range(3):
                print(f"\nRodada {rodada + 1}:")
                exibir_mao(mao_do_jogador)

                # Jogador escolhe uma carta ou truco
                escolha_jogador = input("Escolha o número da carta que deseja jogar, Trucar ou Fugir:")
                # Verifique se a entrada não está vazia
                if escolha_jogador.strip() == "":
                    print("Por favor, insira uma escolha válida.")
                    escolha_jogador = input("Escolha o número da carta que deseja jogar: ")
                if escolha_jogador.lower() == 'f':
                    print("Arregou!")
                    vitorias_oponente = vitorias_jogador + 2
                    break
                if escolha_jogador.lower() == 't':
                    if truco_ladrao:
                        print("A partida ja esta trucada")
                        escolha_jogador = input("Escolha o número da carta que deseja jogar: ")
                    else:
                        print("-TRUUUUCO!\n -Cai dentro mané!!!")
                        truco_ladrao = True
                        escolha_jogador = input("Escolha o número da carta que deseja jogar: ")

                escolha_jogador = int(escolha_jogador) - 1
                carta_jogador = mao_do_jogador.pop(escolha_jogador)


                # Oponente escolhe uma carta aleatória
                carta_oponente = random.choice(mao_do_oponente)
                mao_do_oponente.remove(carta_oponente)

                print("O jogador jogou:")
                print(cards_database[carta_jogador])
                print("O oponente jogou:")
                print(cards_database[carta_oponente])

                # Determina o vencedor da rodada
                vencedor = vencedor_rodada(carta_jogador, carta_oponente, manilha)
                print("Vencedor da rodada:", vencedor)

                if vencedor == "Jogador":
                    vitorias_jogador += 1
                elif vencedor == "Oponente":
                    vitorias_oponente += 1

                if vitorias_jogador == 2 or vitorias_oponente == 2:
                    baralho = baralho_original.copy()
                    break
            # Atualiza os pontos
            if truco_ladrao:
                if vitorias_jogador > vitorias_oponente:
                    pontos_jogador += 3
                elif vitorias_oponente > vitorias_jogador:
                    pontos_oponente += 3
            else:
                if vitorias_jogador > vitorias_oponente:
                    pontos_jogador += 1
                elif vitorias_oponente > vitorias_jogador:
                    pontos_oponente += 1

            print(f"\nPontuação:")
            print(f"Jogador | Pontos: {pontos_jogador}")
            print(f"Oponente | Pontos: {pontos_oponente}")

            # Embaralha o baralho para a próxima rodada
            embaralhar()

        # Verifica o vencedor do jogo
        if pontos_jogador > pontos_oponente:
            print("Parabéns! Você venceu o jogo! :D")
        elif pontos_oponente > pontos_jogador:
            print("Ah que pena, você perdeu. :(")
        else:
            print("O jogo empatou!")

        # Pergunta se deseja jogar novamente
        jogar_novamente = input("Deseja jogar novamente? (s/n): ")
        if jogar_novamente.lower() != 's':
            print(ursinho_tchau)
            break

# Inicia o jogo
truco()
