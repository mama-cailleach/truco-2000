"""
Utility Functions Module for Truco 2000

This module contains common utility functions used across the game:
- Helper functions
- Common operations
- Cross-module utilities

These functions don't belong to any specific module but are used
by multiple parts of the game.
"""

import sys
import time


def safe_exit(message="Saindo do jogo..."):
    """
    Safely exit the game with a message.
    
    Args:
        message (str): Message to show before exiting
    """
    print(f"\n{message}")
    sys.exit(0)


def pause_with_message(message, pause_time=2):
    """
    Display a message and pause for the specified time.
    
    Args:
        message (str): Message to display
        pause_time (float): Time to pause in seconds
    """
    print(f"\n{message}")
    if pause_time > 0:
        time.sleep(pause_time)


def format_card_list(cards, separator=", "):
    """
    Format a list of cards for display.
    
    Args:
        cards (list): List of card strings
        separator (str): Separator between cards
        
    Returns:
        str: Formatted card list
    """
    return separator.join(cards)


def clamp(value, min_value, max_value):
    """
    Clamp a value between minimum and maximum bounds.
    
    Args:
        value: Value to clamp
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Clamped value
    """
    return max(min_value, min(value, max_value))


def get_plural_suffix(count, singular="", plural="s"):
    """
    Get the appropriate suffix for singular/plural forms.
    
    Args:
        count (int): Number to check
        singular (str): Singular suffix
        plural (str): Plural suffix
        
    Returns:
        str: Appropriate suffix
    """
    return singular if count == 1 else plural


def format_score(player_score, opponent_score):
    """
    Format a score display string.
    
    Args:
        player_score (int): Player's score
        opponent_score (int): Opponent's score
        
    Returns:
        str: Formatted score string
    """
    return f"Você {player_score} x {opponent_score} Oponente"


def validate_card_index(index, hand_size):
    """
    Validate if a card index is valid for the given hand size.
    
    Args:
        index (int): Card index (1-based)
        hand_size (int): Size of the hand
        
    Returns:
        bool: True if index is valid
    """
    return 1 <= index <= hand_size


def convert_to_zero_based_index(one_based_index):
    """
    Convert 1-based index to 0-based index.
    
    Args:
        one_based_index (int): 1-based index
        
    Returns:
        int: 0-based index
    """
    return one_based_index - 1
