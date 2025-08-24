"""
Display and Layout Module for Truco 2000

This module handles all screen display and layout management:
- Screen clearing and layout coordination
- Two-column layout system (main area + sidebar)
- Battle zone rendering and management
- Game state visualization
- Card hand display

This module coordinates visual elements but delegates ASCII art generation
to the ascii_art module.
"""

import os
import time


class UIDisplay:
    """
    Manages all display operations and screen layout.
    
    This class handles the visual presentation of the game state,
    coordinating between different UI components to create a cohesive
    user experience.
    """
    
    def __init__(self, ascii_art, screen_width=120):
        """
        Initialize the display manager.
        
        Args:
            ascii_art (ASCIIArt): ASCII art generator instance
            screen_width (int): Total screen width for layout calculations
        """
        self.ascii_art = ascii_art
        self.screen_width = screen_width
        self.cards_database = ascii_art.fill_cards_database()
    
    def clear_screen(self):
        """Clear the console screen."""
        os.system('cls')
    
    def show_quit_message(self):
        """Display the quit message with bear mascot."""
        self.clear_screen()
        print(self.ascii_art.get_farewell_bear())
        print("\nObrigado por jogar Truco 2000!")
        print("Até a próxima! ♠♥♦♣")
    
    def show_game_intro(self):
        """Display the complete game introduction sequence."""
        self.ascii_art.display_intro_sequence()
    
    def get_battle_zone_lines(self, main_width, carta_jogador=None, carta_oponente=None, 
                            round_result=None, show_result=False):
        """
        Generate battle zone display lines - always open and visible.
        
        Args:
            main_width (int): Width available for the battle zone
            carta_jogador (str, optional): Player's card to display
            carta_oponente (str, optional): Opponent's card to display  
            round_result (str, optional): Result message to show
            show_result (bool): Whether to show the result
        
        Returns:
            list: List of strings representing the battle zone lines
        """
        lines = []
        lines.append(self.ascii_art.create_separator(main_width))
        lines.append(self.ascii_art.center_text("MESA", main_width))
        lines.append(self.ascii_art.create_separator(main_width))
        
        # Always assign fixed positions: [player, opponent]
        battle_cards = [None, None]
        labels = ["SUA CARTA", "CARTA DO OPONENTE"]

        if carta_jogador:
            battle_cards[0] = carta_jogador
        if carta_oponente:
            battle_cards[1] = carta_oponente
        
        
        if battle_cards:
            # Display labels
            if len(battle_cards) == 1:
                # Single card - center the label
                lines.append(f"{labels[0]}") # self.ascii_art.center_text(labels[0], main_width)
            else:
                # Two cards - distribute labels
                label_spacing = main_width // 2
                left_label = f"{labels[0]:^{label_spacing}}"
                right_label = f"{labels[1]:^{label_spacing}}"
                lines.append(left_label + right_label)
            
            # Display cards always player card left and opponent right
            card_displays = []
            for card in battle_cards:
                if card:
                    card_displays.append(self.cards_database[card].split('\n'))
                else:
                    # Fill with empty card lines for alignment
                    card_displays.append([" " * 9] * 7)  # 7 = card height

            max_card_lines = max(len(card) for card in card_displays)
            for i in range(max_card_lines):
                left_card = card_displays[0][i] if i < len(card_displays[0]) else " " * 9
                right_card = card_displays[1][i] if i < len(card_displays[1]) else " " * 9
                row = left_card.center(label_spacing) + right_card.center(main_width - label_spacing)
                lines.append(row)
            
            
            # Show round result if requested
            if show_result and round_result:
                lines.append("")
                lines.append(self.ascii_art.center_text(f"*** {round_result} ***", main_width))
            else:
                lines.append("")  # Empty line for spacing
                lines.append("")  # Second empty line for consistent height
        else:
            # No cards to display - show placeholder
            lines.append(self.ascii_art.center_text("(aguardando cartas...)", main_width))
            default_card_height = 7  # Set this to match your card ASCII art height
            for _ in range(default_card_height):
                lines.append("")
            lines.append("")  # Empty lines for consistent height
            lines.append("")
        
        lines.append(self.ascii_art.create_separator(main_width))
        return lines
    
    def build_sidebar_lines(self, game_core, truco_logic, rodada, resultados_rodadas, 
                          carta_virada, manilha, player_starts, primeira_vitoria):
        """
        Build the sidebar content lines.
        
        Args:
            game_core (GameCore): Game core instance for scores
            truco_logic (TrucoLogic): Truco logic for hand value
            rodada (int): Current round number
            resultados_rodadas (list): Results of completed rounds
            carta_virada (str): The vira card
            manilha (str): Current manilha rank
            player_starts (bool): Whether player starts this round
            primeira_vitoria (str): Who won first non-tie round
        
        Returns:
            list: List of strings representing sidebar content
        """
        sidebar_lines = []
        sidebar_width = 38  # Sidebar width
        
        # Score and round info
        sidebar_lines.append(f"PLACAR: Você {game_core.pontos_jogador} x {game_core.pontos_oponente} Oponente")
        sidebar_lines.append("")
        sidebar_lines.append(f"RODADA {rodada + 1}")
        starter = "Você" if player_starts else "Oponente"
        sidebar_lines.append(f"{starter} começa esta rodada.")
        sidebar_lines.append("")
        
        # Hand status
        if rodada > 0:
            sidebar_lines.append("STATUS DA MÃO:")
            for i, resultado in enumerate(resultados_rodadas):
                if resultado == "Jogador":
                    sidebar_lines.append(f"  Rodada {i + 1}: Você venceu")
                elif resultado == "Oponente":
                    sidebar_lines.append(f"  Rodada {i + 1}: Oponente venceu")
                else:
                    sidebar_lines.append(f"  Rodada {i + 1}: Empate")
            
            if primeira_vitoria:
                sidebar_lines.append(f"Primeira vitória: {primeira_vitoria}")
            sidebar_lines.append("")
        else:
            sidebar_lines.append("")
        
        # Current hand value
        if truco_logic.current_hand_value > 1:
            truco_name = truco_logic.get_truco_name(truco_logic.current_hand_value)
            sidebar_lines.append(f"MÃO ATUAL: {truco_name}")
            sidebar_lines.append(f"Vale: {truco_logic.current_hand_value} pontos")
            sidebar_lines.append("")
        
        # Vira card display
        sidebar_lines.append("CARTA VIRADA:")
        vira_lines = self.cards_database[carta_virada].split('\n')
        sidebar_lines.extend(vira_lines)
        sidebar_lines.append("")
        sidebar_lines.append(f"Manilhas: {manilha}♣, {manilha}♥, {manilha}♠, {manilha}♦")
        sidebar_lines.append("")
        
        # Pad sidebar to minimum height for consistent layout
        min_sidebar_height = 28
        while len(sidebar_lines) < min_sidebar_height:
            sidebar_lines.append("")
        
        return sidebar_lines
    
    def display_player_hand(self, mao_do_jogador, main_width):
        """
        Generate lines for displaying the player's hand.
        
        Args:
            mao_do_jogador (list): Player's current hand
            main_width (int): Width available for display
        
        Returns:
            list: List of strings representing the hand display
        """
        lines = []
        lines.append("SUAS CARTAS:")
        
        if not mao_do_jogador:
            lines.append("(sem cartas)")
            return lines
        
        # Display card numbers and cards
        hand_displays = [self.cards_database[c].split('\n') for c in mao_do_jogador]
        max_hand_lines = max(len(card) for card in hand_displays) if hand_displays else 0
        
        # Add card numbers above cards
        number_line = ""
        for idx in range(len(mao_do_jogador)):
            number_label = f"({idx + 1})"
            number_line += f"  {number_label:^9}"  # 9 is card width
        lines.append(number_line.strip())
        
        # Add card ASCII art lines
        for i in range(max_hand_lines):
            row = ""
            for idx, card_lines in enumerate(hand_displays):
                if i < len(card_lines):
                    card_line = card_lines[i]
                else:
                    card_line = " " * 9  # Empty card line
                
                row += f"  {card_line}"  # Add spacing between cards
            
            lines.append(row.rstrip().ljust(main_width))
        
        return lines
    
    def display_game_layout(self, game_core, truco_logic, rodada, mao_do_jogador, 
                          manilha, resultados_rodadas, carta_virada, player_starts, 
                          primeira_vitoria, battle_zone=None):
        """
        Display the complete game layout with sidebar and main area.
        
        Args:
            game_core (GameCore): Game core instance
            truco_logic (TrucoLogic): Truco logic instance  
            rodada (int): Current round number
            mao_do_jogador (list): Player's hand
            manilha (str): Current manilha rank
            resultados_rodadas (list): Round results
            carta_virada (str): Vira card
            player_starts (bool): Whether player starts this round
            primeira_vitoria (str): First round winner
            battle_zone (dict, optional): Battle zone display data
        """
        self.clear_screen()
        
        # Calculate layout dimensions
        sidebar_width = 38
        main_width = self.screen_width - sidebar_width - 3  # 3 for spacing and separator
        
        # Build sidebar content
        sidebar_lines = self.build_sidebar_lines(
            game_core, truco_logic, rodada, resultados_rodadas, 
            carta_virada, manilha, player_starts, primeira_vitoria
        )
        
        # Build main area content
        main_lines = []
        
        # Battle zone (always visible)
        if battle_zone:
            bz_lines = self.get_battle_zone_lines(
                main_width,
                battle_zone.get("carta_jogador"),
                battle_zone.get("carta_oponente"), 
                battle_zone.get("round_result"),
                battle_zone.get("show_result", False)
            )
        else:
            bz_lines = self.get_battle_zone_lines(main_width)
        
        main_lines.extend(bz_lines)
        main_lines.append("")
        
        # Player's hand
        hand_lines = self.display_player_hand(mao_do_jogador, main_width)
        main_lines.extend(hand_lines)
        
        # Pad main area to match sidebar height
        while len(main_lines) < len(sidebar_lines):
            main_lines.append("")
        
        # Print both columns side by side
        for left, right in zip(main_lines, sidebar_lines):
            print(f"{left.ljust(main_width)} | {right}")
        
        print()  # Extra space at the end
    
    def show_message(self, message, pause_time=2):
        """
        Show a message to the user with optional pause.
        
        Args:
            message (str): Message to display
            pause_time (float): Time to pause after showing message
        """
        print(f"\n{message}")
        if pause_time > 0:
            time.sleep(pause_time)
    
    def show_truco_call(self, caller, value, truco_names):
        """
        Display a truco call announcement.
        
        Args:
            caller (str): Who called truco ("Jogador" or "Oponente")
            value (int): Truco value
            truco_names (dict): Names for truco values
        """
        truco_name = truco_names.get(value, f"Vale {value}")
        caller_name = "Você" if caller == "Jogador" else "Oponente"
        self.show_message(f"*** {caller_name} pediu {truco_name} (vale {value} pontos)! ***", 3)
    
    def show_truco_acceptance(self, accepter, value, truco_names):
        """
        Display truco acceptance message.
        
        Args:
            accepter (str): Who accepted ("Jogador" or "Oponente") 
            value (int): Accepted value
            truco_names (dict): Names for truco values
        """
        accepter_name = "Você" if accepter == "Jogador" else "Oponente"
        truco_name = truco_names.get(value, f"Vale {value}")
        self.show_message(f"{accepter_name} aceitou o {truco_name}!", 3)
    
    def show_opponent_runs(self, value, truco_names):
        """
        Display message when opponent runs from truco.
        
        Args:
            value (int): Value opponent ran from
            truco_names (dict): Names for truco values
        """
        truco_name = truco_names.get(value, f"Vale {value}")
        self.show_message(f"Oponente fugiu do {truco_name}!", 3)
    
    def show_round_winner(self, winner, carta_jogador, carta_oponente):
        """
        Show the winner of a round with cards.
        
        Args:
            winner (str): Round winner
            carta_jogador (str): Player's card
            carta_oponente (str): Opponent's card
        """
        winner_text = "Você venceu" if winner == "Jogador" else "Oponente venceu" if winner == "Oponente" else "Empate"
        self.show_message(f"\n*** {winner_text} a rodada! ***")
    
    def show_hand_result(self, winner, points, game_core):
        """
        Show the result of a completed hand.
        
        Args:
            winner (str): Hand winner
            points (int): Points awarded
            game_core (GameCore): Game core for current scores
        """
        winner_text = "Você" if winner == "Jogador" else "Oponente"
        if points == 1:
            self.show_message(f"\n*** {winner_text} venceu a mão e ganhou {points} ponto! ***")
        else:
            self.show_message(f"\n*** {winner_text} venceu a mão e ganhou {points} pontos! ***")
        self.show_message(f"Placar: Você {game_core.pontos_jogador} x {game_core.pontos_oponente} Oponente")
    
    def show_game_winner(self, winner):
        """
        Show the final game winner.
        
        Args:
            winner (str): Game winner ("Jogador" or "Oponente")
        """
        if winner == "Jogador":
            self.show_message("\n*** PARABÉNS! VOCÊ VENCEU O JOGO! ***", 5)
        else:
            self.show_message("\n*** OPONENTE VENCEU O JOGO! ***", 5)
        
        print("\nObrigado por jogar!")
        print(self.ascii_art.get_bear_mascot())
