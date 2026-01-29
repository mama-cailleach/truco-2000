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
    
    # Pygame Window Settings
    WINDOW_WIDTH = 1024
    WINDOW_HEIGHT = 768
    WINDOW_TITLE = "Truco 2000"
    FPS = 60
    
    # Pygame Colors (RGB)
    COLOR_BACKGROUND = (13, 2, 8)  # Dark purple
    COLOR_BACKGROUND_DARK = (8, 1, 5)  # Even darker purple
    COLOR_PRIMARY = (0, 255, 65)  # Bright green
    COLOR_SECONDARY = (0, 143, 17)  # Dark green
    COLOR_ACCENT = (0, 59, 0)  # Very dark green
    COLOR_TEXT = (0, 255, 65)  # Bright green
    COLOR_TEXT_MUTED = (0, 180, 45)  # Dimmer green
    COLOR_TEXT_SECONDARY = (200, 200, 200)  # Light gray
    COLOR_BUTTON_HOVER = (0, 200, 50)  # Dim green
    COLOR_BUTTON_PRESSED = (0, 150, 30)  # Darker green
    COLOR_ERROR = (255, 50, 50)  # Red
    COLOR_DANGER = (255, 80, 80)  # Light red
    COLOR_WARNING = (255, 200, 0)  # Yellow/orange
    COLOR_SUCCESS = (50, 255, 50)  # Bright green
    
    # Font Settings
    FONT_NAME = "Arial"  # System default; can be overridden by asset
    FONT_SIZE_TITLE = 36
    FONT_SIZE_LARGE = 24
    FONT_SIZE_NORMAL = 18
    FONT_SIZE_SMALL = 14
    
    # Display settings (legacy CLI compatibility)
    SCREEN_WIDTH = 120
    SIDEBAR_WIDTH = 38
    
    # Timing settings (in seconds)
    INTRO_LINE_DELAY = 0.1
    MESSAGE_PAUSE_SHORT = 2
    MESSAGE_PAUSE_MEDIUM = 3
    MESSAGE_PAUSE_LONG = 5
    CARD_REVEAL_PAUSE = 5
    ROUND_RESULT_PAUSE = 3
    OPPONENT_THINK_DELAY = 0.6  # How long opponent 'thinks' before playing
    
    # Game rules
    WINNING_SCORE = 12
    CARDS_PER_HAND = 3
    DECK_SIZE = 40
    
    # Truco values and names
    TRUCO_VALUES = [1, 3, 6, 9, 12]
    TRUCO_NAMES = {
        1: "Normal",
        3: "Truco", 
        6: "Seis",
        9: "Nove",
        12: "Doze"
    }
    
    # Internationalization (i18n)
    DEFAULT_LANGUAGE = "pt_br"
    SUPPORTED_LANGUAGES = ["pt_br", "en_us"]
    AUTO_DETECT_LANGUAGE = False

    
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

    # UI options
    # If True, use a modal dialog for pending truco responses; if False, change buttons inline
    USE_MODAL_TRUCO = False
    
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
