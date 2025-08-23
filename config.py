"""
Configuration Module for Truco 2000

This module contains all game configuration settings:
- Screen and layout settings
- Timing constants
- Game rules and values
- Default settings

Centralizing configuration makes it easy to adjust game behavior
and prepare for future features like settings files.
"""


class GameConfig:
    """
    Central configuration class for all game settings.
    
    This class holds all configurable values that affect game behavior,
    making it easy to adjust settings or load them from files in the future.
    """
    
    # Display settings
    SCREEN_WIDTH = 120
    SIDEBAR_WIDTH = 38
    
    # Timing settings (in seconds)
    INTRO_LINE_DELAY = 0.1
    MESSAGE_PAUSE_SHORT = 2
    MESSAGE_PAUSE_MEDIUM = 3
    MESSAGE_PAUSE_LONG = 5
    CARD_REVEAL_PAUSE = 5
    ROUND_RESULT_PAUSE = 3
    
    # Game rules
    WINNING_SCORE = 12
    CARDS_PER_HAND = 3
    DECK_SIZE = 40
    
    # Truco values and names
    TRUCO_VALUES = [1, 3, 6, 9, 12]
    TRUCO_NAMES = {
        1: "Normal",
        3: "Truco", 
        6: "Retruco",
        9: "Vale 9",
        12: "Vale 12"
    }
    
    # Card values (for sorting and comparison)
    CARD_RANKS = ['4', '5', '6', '7', 'Q', 'J', 'K', 'A', '2', '3']
    CARD_VALUES = {rank: idx + 1 for idx, rank in enumerate(CARD_RANKS)}
    
    # Suits and their hierarchy for manilha tie-breaking
    SUITS = ['♦', '♠', '♥', '♣']
    SUIT_HIERARCHY = {'♣': 4, '♥': 3, '♠': 2, '♦': 1}
    
    # AI difficulty settings
    AI_DIFFICULTIES = {
        'easy': {
            'truco_probability': 0.15,
            'accept_probability': 0.6,
            'reraise_probability': 0.1
        },
        'medium': {
            'truco_probability': 0.25,
            'accept_probability': 0.5,
            'reraise_probability': 0.2
        },
        'hard': {
            'truco_probability': 0.35,
            'accept_probability': 0.4,
            'reraise_probability': 0.3
        }
    }
    
    # Input validation
    VALID_YES_RESPONSES = ['s', 'sim', 'y', 'yes']
    VALID_NO_RESPONSES = ['n', 'nao', 'não', 'no']
    
    # Special commands
    QUIT_COMMAND = 'quit'
    TRUCO_COMMAND = 't'
    FUGIR_COMMAND = 'f'
    
    # Messages
    MESSAGES = {
        'welcome': "E aí... Que tal jogar um truquinho? (s/n): ",
        'play_again': "Deseja jogar novamente? (s/n): ",
        'thanks': "Obrigado por jogar Truco 2000! Até a próxima!",
        'quit': "Ok! Então tchau!",
        'invalid_input': "Escolha inválida. Por favor, escolha uma dessas opções: ",
        'empty_input': "Entrada vazia. Por favor, digite uma opção válida.",
        'yes_no_help': "Por favor, responda com 's' (sim) ou 'n' (não)."
    }
    
    @classmethod
    def get_main_width(cls):
        """Get the main area width (total minus sidebar and separator)."""
        return cls.SCREEN_WIDTH - cls.SIDEBAR_WIDTH - 3
    
    @classmethod
    def get_next_truco_value(cls, current_value):
        """Get the next truco value in sequence."""
        if current_value == 1:
            return 3
        elif current_value < 12:
            return current_value + 3
        else:
            return None
    
    @classmethod
    def is_max_truco(cls, value):
        """Check if the value is the maximum truco."""
        return value >= 12
