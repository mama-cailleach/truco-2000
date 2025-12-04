"""
Truco Logic Module for Truco 2000

This module handles all Truco-specific logic:
- Truco sequence handling (truco, retruco, vale 9, vale 12)
- Player and AI responses to truco calls
- Truco state management and escalation
- Point calculations for truco scenarios

This module is separate from core game logic to allow for different
AI difficulty levels and truco strategies.
"""

import random


class TrucoLogic:
    """
    Manages all Truco-related game mechanics and decision-making.
    
    This class handles the complex negotiations and escalations that make
    Truco unique among card games.
    """
    
    def __init__(self):
        """Initialize truco state tracking."""
        # Truco state tracking
        self.current_hand_value = 1  # Current value of the hand (1, 3, 6, 9, 12)
        self.last_accepted_value = 1  # Last value that was explicitly accepted (for defensive tracking)
        self.last_raiser = None  # Who made the last raise ("Jogador" or "Oponente")
        self.truco_names = {1: "Normal", 3: "Truco", 6: "Retruco", 9: "Vale 9", 12: "Vale 12"}
    
    def reset_truco_state(self):
        """
        Reset truco state for a new hand.
        
        Should be called at the beginning of each new hand.
        """
        self.current_hand_value = 1
        self.last_accepted_value = 1
        self.last_raiser = None
    
    def can_raise_truco(self, player, current_value=None):
        """
        Check if a player can raise the truco stakes.
        
        Args:
            player (str): "Jogador" or "Oponente"
            current_value (int, optional): Current hand value, uses self.current_hand_value if None
            
        Returns:
            bool: True if the player can raise truco
            
        Rules:
            - Cannot raise above 12 points
            - Cannot raise twice in a row (must wait for opponent's turn)
            - Can always raise if current value is 1 (no active truco)
        """
        if current_value is None:
            current_value = self.current_hand_value
            
        # Cannot raise above maximum
        if current_value >= 12:
            return False
            
        # If no active truco, anyone can start
        if current_value == 1:
            return True
            
        # If there's an active truco, can only raise if you weren't the last raiser
        return self.last_raiser != player
    
    def get_next_truco_value(self, current_value=None):
        """
        Get the next truco value in the escalation sequence.
        
        Args:
            current_value (int, optional): Current value, uses self.current_hand_value if None
            
        Returns:
            int: Next value in sequence (3, 6, 9, 12), or None if at maximum
        """
        if current_value is None:
            current_value = self.current_hand_value
            
        if current_value == 1:
            return 3
        elif current_value < 12:
            return current_value + 3
        else:
            return None  # Already at maximum
    
    def get_truco_name(self, value):
        """
        Get the name for a truco value.
        
        Args:
            value (int): Truco value (1, 3, 6, 9, 12)
            
        Returns:
            str: Name of the truco level
        """
        return self.truco_names.get(value, f"Vale {value}")
    
    def handle_truco_sequence(self, initiator, current_value=3, input_handler=None, ui_handler=None):
        """
        Handle a complete truco sequence until someone accepts or runs.
        
        This is the core truco negotiation logic that handles back-and-forth
        escalation between players.
        
        Args:
            initiator (str): Who started the truco ("Jogador" or "Oponente")
            current_value (int): Starting value of the truco (default: 3)
            ui_handler (object): UI handler for getting responses (must have get_truco_response methods)
            
        Returns:
            tuple: (accepted, final_value, who_ran, final_raiser, last_accepted_value)
                - accepted (bool): True if truco was accepted, False if someone ran
                - final_value (int): Final truco value
                - who_ran (str): Who ran away, or None
                - final_raiser (str): Who made the final raise
                - last_accepted_value (int): Last value that was accepted
        """
        if ui_handler is None:
            # Cannot handle truco sequence without UI
            return False, current_value, initiator, None, self.current_hand_value
        
        raiser = initiator
        value = current_value
        last_accepted_value = self.current_hand_value
        
        while value <= 12:
            if raiser == "Oponente":
                # Get player's response to opponent's truco
                response = input_handler.get_truco_response(value, raiser, self.truco_names)
                
                if response == 'run':
                    # Player ran away
                    return False, value, "Jogador", raiser, last_accepted_value
                elif response == 'accept':
                    # Player accepted
                    return True, value, None, raiser, value
                elif response == 'reraise':
                    # Player wants to reraise
                    last_accepted_value = value
                    next_value = self.get_next_truco_value(value)
                    if next_value is None or next_value > 12:
                        # Cannot reraise further, must accept
                        return True, value, None, raiser, value
                    
                    # Show player's reraise
                    ui_handler.show_truco_call("Jogador", next_value, self.truco_names)
                    
                    # Update state for next iteration
                    raiser = "Jogador"
                    value = next_value
            else:
                # Get opponent's response to player's truco
                response = self.get_opponent_truco_response(value)
                
                if response == 'run':
                    # Opponent ran away
                    ui_handler.show_opponent_runs(value, self.truco_names)
                    return False, value, "Oponente", raiser, last_accepted_value
                elif response == 'accept':
                    # Opponent accepted
                    ui_handler.show_truco_acceptance("Oponente", value, self.truco_names)
                    return True, value, None, raiser, value
                elif response == 'reraise':
                    # Opponent wants to reraise
                    last_accepted_value = value
                    next_value = self.get_next_truco_value(value)
                    if next_value is None or next_value > 12:
                        # Cannot reraise further, must accept
                        ui_handler.show_truco_acceptance("Oponente", value, self.truco_names)
                        return True, value, None, raiser, value
                    
                    # Show opponent's reraise
                    ui_handler.show_truco_call("Oponente", next_value, self.truco_names)
                    
                    # Update state for next iteration
                    raiser = "Oponente"
                    value = next_value
        
        # Should never reach here, but safety fallback
        return True, value, None, raiser, last_accepted_value
    
    def get_opponent_truco_response(self, current_value):
        """
        Get the opponent's response to a truco call.
        
        This is a simple AI that makes random decisions. In the future,
        this can be replaced with more sophisticated AI strategies.
        
        Args:
            current_value (int): Current value being proposed
            
        Returns:
            str: 'run', 'accept', or 'reraise'
        """
        next_value = self.get_next_truco_value(current_value)
        can_reraise = next_value is not None and next_value <= 12
        
        if can_reraise:
            # Random choice between all three options
            # Weighted slightly toward acceptance for better gameplay
            choices = ['run', 'accept', 'accept', 'reraise']  # Accept has higher probability
            return random.choice(choices)
        else:
            # Can only run or accept at max value
            return random.choice(['run', 'accept'])
    
    def should_opponent_initiate_truco(self, current_value, difficulty='medium'):
        """
        Determine if opponent should initiate a truco call.
        
        Args:
            current_value (int): Current hand value
            difficulty (str): AI difficulty level ('easy', 'medium', 'hard')
            
        Returns:
            bool: True if opponent should call truco
        """
        if not self.can_raise_truco("Oponente", current_value):
            return False
        
        # Different probabilities based on difficulty
        if difficulty == 'easy':
            probability = 0.15  # 15% chance
        elif difficulty == 'medium':
            probability = 0.25  # 25% chance
        else:  # hard
            probability = 0.35  # 35% chance
        
        return random.random() < probability
    
    def update_truco_state(self, new_value, raiser):
        """
        Update the internal truco state when a raise is ACCEPTED.
        
        This is called after a re-raise is accepted or when initial raise is accepted.
        It updates current_hand_value and marks new_value as the last_accepted_value.
        
        Args:
            new_value (int): New hand value (the accepted value)
            raiser (str): Who made the raise that resulted in this value
        """
        self.current_hand_value = new_value
        self.last_accepted_value = new_value  # When accepted, it becomes the new baseline for next run
        self.last_raiser = raiser
    
    def calculate_points_for_runner(self, who_ran, final_value, last_accepted_value):
        """
        Calculate points when someone runs from truco.
        
        When someone runs from a raise, the other player wins the last ACCEPTED value,
        not the proposed value. For example:
          - Player calls Truco(3) -> opponent accepts (3 is now accepted)
          - Opponent re-raises to Retruco(6) -> player RUNS
          - Player GIVES 3 points to opponent (the last accepted), not 6
        
        Args:
            who_ran (str): "Jogador" or "Oponente" (who refused the raise)
            final_value (int): Value that was proposed (caused the run) [used for validation only]
            last_accepted_value (int): Last value that was accepted before the raise
            
        Returns:
            tuple: (winner, points_awarded)
                - winner (str): Who gets the points (the other player from who_ran)
                - points_awarded (int): Points = last_accepted_value
        """
        if who_ran == "Jogador":
            winner = "Oponente"
        else:
            winner = "Jogador"
        
        # Award the last accepted value (the value that was accepted before the raise that caused the run)
        points_awarded = last_accepted_value
        
        return winner, points_awarded
