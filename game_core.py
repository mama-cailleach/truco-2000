"""
Core Game Logic Module for Truco 2000

This module contains pure game logic that is UI-independent:
- Card deck management
- Game rules (card values, round winners, manilha system)
- Hand/round winner determination
- Core game state management

All functions here should work independently of any UI or display logic.
"""

import random


class GameCore:
    """
    Handles core Truco game logic and rules.
    
    This class manages the fundamental game mechanics without any UI dependencies.
    It can be used for testing, different UI implementations, or AI training.
    """
    
    def __init__(self):
        """Initialize the core game components."""
        # Card-related attributes
        self.baralho = self.create_baralho()
        self.baralho_original = self.baralho.copy()
        
        # Game state attributes
        self.pontos_jogador = 0
        self.pontos_oponente = 0
        
        # Track who goes first
        self.player_starts_hand = True  # Player starts the first hand
        self.player_starts_round = True  # Player starts the first round in a hand
    
    def create_baralho(self):
        """
        Create a standard Truco deck of 40 cards.
        
        Uses Unicode suit symbols for better display.
        Cards are ordered by value within each suit.
        
        Returns:
            list: Complete deck of 40 cards with format 'RankSuit' (e.g., '4♣', 'A♠')
        """
        return ['4♣', '5♣', '6♣', '7♣', 'Q♣', 'J♣', 'K♣', 'A♣', '2♣', '3♣',
                '4♥', '5♥', '6♥', '7♥', 'Q♥', 'J♥', 'K♥', 'A♥', '2♥', '3♥',
                '4♦', '5♦', '6♦', '7♦', 'Q♦', 'J♦', 'K♦', 'A♦', '2♦', '3♦',
                '4♠', '5♠', '6♠', '7♠', 'Q♠', 'J♠', 'K♠', 'A♠', '2♠', '3♠']
    
    def reiniciar_baralho(self):
        """
        Reset the deck to its original state and shuffle it.
        
        This should be called at the beginning of each hand.
        """
        self.baralho = self.baralho_original.copy()
        self.embaralhar()
    
    def embaralhar(self):
        """Shuffle the current deck randomly."""
        random.shuffle(self.baralho)
    
    def distribuir_cartas(self, quantidade):
        """
        Deal a specified number of cards from the deck.
        
        Args:
            quantidade (int): Number of cards to deal
            
        Returns:
            list: List of cards dealt from the deck
            
        Note:
            Cards are removed from self.baralho when dealt.
        """
        cartas = []
        for _ in range(quantidade):
            if self.baralho:
                cartas.append(self.baralho.pop(0))
        return cartas
    
    def determinar_manilha(self):
        """
        Determine the 'vira' card and corresponding manilha rank.
        
        In Truco, a random card is turned face up (vira), and the next rank
        in sequence becomes the manilha (trump card).
        
        Returns:
            tuple: (carta_vira, manilha_rank)
                - carta_vira (str): The face-up card that determines the manilha
                - manilha_rank (str): The rank that becomes the manilha (4, 5, 6, 7, Q, J, K, A, 2, 3)
        """
        # Card ranks in order
        valores = ['4', '5', '6', '7', 'Q', 'J', 'K', 'A', '2', '3']
        naipes = ['♦', '♠', '♥', '♣']
        
        # Choose a random card as "vira"
        naipe_vira = random.choice(naipes)
        valor_vira = random.choice(valores)
        carta_vira = valor_vira + naipe_vira
        
        # Determine the manilha rank (next rank after the vira)
        indice_atual = valores.index(valor_vira)
        indice_manilha = (indice_atual + 1) % len(valores)
        manilha = valores[indice_manilha]
        
        return carta_vira, manilha
    
    def valor_carta(self, carta):
        """
        Get the base value of a card (without considering manilha status).
        
        Args:
            carta (str): Card in format 'RankSuit' (e.g., '7♠', 'A♥')
            
        Returns:
            int: Base value from 1 (lowest: 4) to 10 (highest: 3)
        """
        # Card values in ascending order
        valores = {'4': 1, '5': 2, '6': 3, '7': 4, 'Q': 5, 'J': 6, 'K': 7, 'A': 8, '2': 9, '3': 10}
        return valores.get(carta[0], 0)
    
    def vencedor_rodada(self, carta_jogador, carta_oponente, manilha):
        """
        Determine the winner of a single round based on card values and manilha rules.
        
        Args:
            carta_jogador (str): Player's card
            carta_oponente (str): Opponent's card
            manilha (str): Current manilha rank (e.g., 'A', '7', 'Q')
            
        Returns:
            str: 'Jogador', 'Oponente', or 'Empate' (tie)
            
        Rules:
            - Manilhas beat all regular cards
            - Between manilhas, suit order determines winner: ♣ > ♥ > ♠ > ♦
            - Between regular cards, higher rank wins
            - If same rank and both non-manilha, it's a tie
        """
        valor_jogador = self.valor_carta(carta_jogador)
        valor_oponente = self.valor_carta(carta_oponente)
        
        # Check if cards are manilhas and add bonus value
        if carta_jogador[0] == manilha:
            valor_jogador += 10
        if carta_oponente[0] == manilha:
            valor_oponente += 10
        
        if valor_jogador > valor_oponente:
            return "Jogador"
        elif valor_oponente > valor_jogador:
            return "Oponente"
        else:
            # Tie: check suit order only if both cards are manilhas
            if carta_jogador[0] == manilha and carta_oponente[0] == manilha:
                # Manilha suit hierarchy: ♣ > ♥ > ♠ > ♦
                hierarchy = {'♣': 4, '♥': 3, '♠': 2, '♦': 1}
                suit_jogador = hierarchy.get(carta_jogador[1], 0)
                suit_oponente = hierarchy.get(carta_oponente[1], 0)
                
                if suit_jogador > suit_oponente:
                    return "Jogador"
                elif suit_oponente > suit_jogador:
                    return "Oponente"
                else:
                    return "Empate"
            else:
                # Regular tie between non-manilhas
                return "Empate"
    
    def check_hand_winner(self, rodada, resultados_rodadas, vitorias_jogador, vitorias_oponente, primeira_vitoria):
        """
        Check if there's a winner for the current hand based on round results.
        
        Args:
            rodada (int): Current round number (0, 1, or 2)
            resultados_rodadas (list): List of round results
            vitorias_jogador (int): Number of rounds won by player
            vitorias_oponente (int): Number of rounds won by opponent
            primeira_vitoria (str): Who won the first non-tie round (for tie-breaking)
            
        Returns:
            tuple: (end_hand, winner_message)
                - end_hand (bool): True if hand should end
                - winner_message (str): Message explaining the result, or None
                
        Truco hand rules:
            - First to win 2 rounds wins the hand
            - If first round is won and second is tied, first round winner wins
            - If all rounds are tied, primeira_vitoria determines winner
        """
        if rodada == 0:
            # After first round, can only end if someone won
            if vitorias_jogador >= 2:
                return True, "Você venceu a mão (2-0)!"
            elif vitorias_oponente >= 2:
                return True, "Oponente venceu a mão (2-0)!"
            
        elif rodada == 1:
            # After second round, check for decisive victories or special cases
            if vitorias_jogador >= 2:
                return True, "Você venceu a mão (2 rodadas)!"
            elif vitorias_oponente >= 2:
                return True, "Oponente venceu a mão (2 rodadas)!"
            elif vitorias_jogador == 1 and vitorias_oponente == 0 and "Empate" in resultados_rodadas:
                # Player won first round, second was tie -> player wins
                return True, "Você venceu a mão (1 vitória + empate)!"
            elif vitorias_oponente == 1 and vitorias_jogador == 0 and "Empate" in resultados_rodadas:
                # Opponent won first round, second was tie -> opponent wins
                return True, "Oponente venceu a mão (1 vitória + empate)!"
                
        elif rodada == 2:
            # After third round, determine final winner
            if vitorias_jogador > vitorias_oponente:
                return True, f"Você venceu a mão ({vitorias_jogador}-{vitorias_oponente})!"
            elif vitorias_oponente > vitorias_jogador:
                return True, f"Oponente venceu a mão ({vitorias_oponente}-{vitorias_jogador})!"
            else:
                # All rounds were ties, use primeira_vitoria as tiebreaker
                if primeira_vitoria == "Jogador":
                    return True, "Você venceu a mão (empate decidido pela primeira vitória)!"
                elif primeira_vitoria == "Oponente":
                    return True, "Oponente venceu a mão (empate decidido pela primeira vitória)!"
                else:
                    return True, "Mão completamente empatada!"
        
        # Hand should continue
        return False, None
    
    def reset_game_state(self):
        """
        Reset the game state for a new game.
        
        This resets scores and starting positions but preserves deck state.
        """
        self.pontos_jogador = 0
        self.pontos_oponente = 0
        self.player_starts_hand = True
        self.player_starts_round = True
    
    def update_score(self, winner, points):
        """
        Update the score for the winning player.
        
        Args:
            winner (str): 'Jogador' or 'Oponente'
            points (int): Points to add to the winner's score
        """
        if winner == "Jogador":
            self.pontos_jogador += points
        elif winner == "Oponente":
            self.pontos_oponente += points
    
    def get_game_winner(self):
        """
        Check if there's a game winner (first to 12 points).
        
        Returns:
            str: 'Jogador', 'Oponente', or None if game should continue
        """
        if self.pontos_jogador >= 12:
            return "Jogador"
        elif self.pontos_oponente >= 12:
            return "Oponente"
        return None
