"""
ASCII Art and Visual Elements Module for Truco 2000

This module handles all ASCII art generation and visual elements:
- Card ASCII art generation and database
- Game banners and intro sequences
- Decorative elements (bears, separators)
- Visual effects and animations

This module is focused purely on visual content generation.
"""

import time


class ASCIIArt:
    """
    Generates and manages ASCII art elements for the game.
    
    This class handles all visual content that doesn't involve game layout,
    focusing on static art elements and visual effects.
    """
    
    def __init__(self):
        """Initialize ASCII art elements."""
        # Cute bear mascot
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
        
        # Farewell bear
        self.ursinho_tchau = r'''
  (c).-.(c)   ___________________
   / ._. \   | Ok! Então tchau!  |
   \( Y )/   |___________________|
    /'-'\    

                        '''
    
    def generate_card_ascii(self, rank, suit):
        """
        Generate ASCII art for a card with given rank and suit.
        
        Args:
            rank (str): Card rank ('4', '5', '6', '7', 'Q', 'J', 'K', 'A', '2', '3')
            suit (str): Card suit ('♠', '♥', '♦', '♣')
        
        Returns:
            str: ASCII art representation of the card
        """
        # Define the card template
        top_line = "┌───────┐"
        rank_line = f"│ {rank:<2}    │"
        suit_line = f"│   {suit}   │"
        middle_line = "│       │"
        bottom_rank_line = f"│     {rank} │"
        bottom_line = "└───────┘"
        
        # Concatenate all lines to form the ASCII art
        card_ascii = '\n'.join([
            top_line,
            rank_line,
            suit_line,
            middle_line,
            suit_line,
            bottom_rank_line,
            bottom_line
        ])
        
        return card_ascii
    
    def fill_cards_database(self):
        """
        Fill the cards database with ASCII art for all cards.
        
        Returns:
            dict: Dictionary mapping card strings to their ASCII art
        """
        cards_database = {}
        ranks = ['4', '5', '6', '7', 'Q', 'J', 'K', 'A', '2', '3']
        suits = ['♠', '♥', '♦', '♣']  # Unicode suits
        
        for rank in ranks:
            for suit in suits:
                card_key = rank + suit
                cards_database[card_key] = self.generate_card_ascii(rank, suit)
        
        return cards_database
    
    def get_intro_banner(self):
        """
        Get the main game banner.
        
        Returns:
            str: ASCII art banner for the game intro
        """
        banner = '''
         ______   ______     __  __     ______     ______    
        /\\__  _\\ /\\  == \\   /\\ \\/\\ \\   /\\  ___\\   /\\  __ \\   
        \\/_/\\ \\/ \\ \\  __<   \\ \\ \\_\\ \\  \\ \\ \\____  \\ \\ \\/\\ \\  
           \\ \\_\\  \\ \\_\\ \\_\\  \\ \\_____\\  \\ \\_____\\  \\ \\_____\\ 
            \\/_/   \\/_/ /_/   \\/_____/   \\/_____/   \\/_____/ 
        '''
        return banner
    
    def get_card_decoration(self):
        """
        Get decorative card elements for the intro.
        
        Returns:
            str: ASCII art showing decorative cards
        """
        decoration = r'''
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
        return decoration
    
    def get_game_subtitle(self):
        """
        Get the game subtitle and credits.
        
        Returns:
            str: Subtitle text with game information
        """
        return ("                             ♠♥♦♣\n"
                "                          Truco 2000\n"
                "                       Um jogo em python\n"
                "                           por mama\n"
                "                             ♠♥♦♣")
    
    def display_intro_sequence(self):
        """
        Display the complete intro sequence with timing effects.
        
        This method shows the full intro with dramatic timing for better
        user experience.
        """
        # Display banner with line-by-line animation
        banner_lines = self.get_intro_banner().split('\n')
        for line in banner_lines:
            print(line)
            time.sleep(0.1)
        
        # Display card decoration
        print(self.get_card_decoration())
        
        # Display subtitle
        print(self.get_game_subtitle())
    
    def get_bear_mascot(self):
        """
        Get the main bear mascot.
        
        Returns:
            str: ASCII art of the game mascot
        """
        return self.ursinho
    
    def get_farewell_bear(self):
        """
        Get the farewell bear with speech bubble.
        
        Returns:
            str: ASCII art of bear saying goodbye
        """
        return self.ursinho_tchau
    
    def create_separator(self, width, char='='):
        """
        Create a separator line of specified width.
        
        Args:
            width (int): Width of the separator
            char (str): Character to use for the separator
        
        Returns:
            str: Separator string
        """
        return char * width
    
    def center_text(self, text, width):
        """
        Center text within a specified width.
        
        Args:
            text (str): Text to center
            width (int): Width to center within
        
        Returns:
            str: Centered text
        """
        return f"{text:^{width}}"
    
    def create_bordered_text(self, text, width, border_char='*'):
        """
        Create text with borders around it.
        
        Args:
            text (str): Text to border
            width (int): Total width including borders
            border_char (str): Character to use for borders
        
        Returns:
            list: List of lines forming the bordered text
        """
        lines = []
        
        # Top border
        lines.append(border_char * width)
        
        # Text line with side borders
        text_width = width - 4  # Account for borders and spaces
        centered_text = f"{text:^{text_width}}"
        lines.append(f"{border_char} {centered_text} {border_char}")
        
        # Bottom border
        lines.append(border_char * width)
        
        return lines
