"""
Input Handling Module for Truco 2000

This module handles all user input operations:
- Input validation and sanitization
- Card choice prompts
- Yes/No confirmations
- Truco response handling
- Global quit command processing

All input functions include the global 'quit' command functionality.
"""

import sys


class InputHandler:
    """
    Handles all user input with validation and global quit functionality.
    
    This class centralizes input handling to ensure consistent behavior
    across the entire game, including the global quit command.
    """
    
    def __init__(self, ui_display=None):
        """
        Initialize the input handler.
        
        Args:
            ui_display (UIDisplay, optional): Reference to UI display for showing quit messages
        """
        self.ui_display = ui_display
    
    def handle_quit(self):
        """
        Handle the global quit command.
        
        This method is called whenever the user types 'quit' at any input prompt.
        It shows a farewell message and exits the game.
        """
        if self.ui_display:
            self.ui_display.show_quit_message()
        else:
            print("\nObrigado por jogar Truco 2000! Até a próxima!")
        
        sys.exit(0)
    
    def get_valid_input(self, prompt, valid_options):
        """
        Get and validate user input against a list of valid options.
        
        Args:
            prompt (str): The prompt to display to the user
            valid_options (list): List of valid options (can include numbers as strings,
                                and special options like 't', 'f', etc.)
        
        Returns:
            str: The validated user input
            
        Features:
            - Global quit command ('quit')
            - Case-insensitive matching
            - Number validation
            - Clear error messages
        """
        while True:
            user_input = input(prompt).strip().lower()
            
            # Handle global quit command
            if user_input == "quit":
                self.handle_quit()
            
            # Check if the input is empty
            if user_input == "":
                print("Entrada vazia. Por favor, digite uma opção válida.")
                continue
            
            # Check if the input is a valid special command
            valid_options_lower = [str(option).lower() for option in valid_options]
            if user_input in valid_options_lower:
                # Return the original case from valid_options
                for original_option in valid_options:
                    if str(original_option).lower() == user_input:
                        return str(original_option)
            
            # Check if the input is a valid number within range
            if user_input.isdigit():
                number = int(user_input)
                # Check if this number (as string) is in valid options
                if str(number) in [str(opt) for opt in valid_options]:
                    return str(number)
            
            # If we get here, the input is not valid
            options_display = ", ".join(str(opt) for opt in valid_options)
            print(f"Escolha inválida. Por favor, escolha uma dessas opções: {options_display}")
    
    def get_yes_no_input(self, prompt):
        """
        Get a yes/no input from the user.
        
        Args:
            prompt (str): The prompt to display to the user
        
        Returns:
            bool: True if yes, False if no
            
        Accepts:
            - Yes: 's', 'sim', 'y', 'yes'
            - No: 'n', 'nao', 'não', 'no'
        """
        valid_yes = ['s', 'sim', 'y', 'yes']
        valid_no = ['n', 'nao', 'não', 'no']
        valid_options = valid_yes + valid_no
        
        while True:
            user_input = input(prompt).strip().lower()
            
            # Handle global quit command
            if user_input == "quit":
                self.handle_quit()
            
            if user_input in valid_yes:
                return True
            elif user_input in valid_no:
                return False
            else:
                print("Por favor, responda com 's' (sim) ou 'n' (não).")
    
    def get_truco_response(self, current_value, raiser, truco_names):
        """
        Get the player's response to a truco call: run, accept, or reraise.
        
        Args:
            current_value (int): Current value being proposed (3, 6, 9, 12)
            raiser (str): Who made the truco call ("Oponente")
            truco_names (dict): Dictionary mapping values to truco names
        
        Returns:
            str: 'run', 'accept', or 'reraise'
        """
        next_value = current_value + 3
        can_reraise = next_value <= 12
        
        print(f"Oponente pediu {truco_names[current_value]} (vale {current_value} pontos)")
        
        valid_options = ['f', 'a']  # fugir, aceitar
        prompt = "F: Fugir, A: Aceitar"
        
        if can_reraise:
            valid_options.append('r')
            prompt += f", R: {truco_names[next_value]} (vale {next_value})"
        
        prompt += ": "
        
        choice = self.get_valid_input(prompt, valid_options)
        
        if choice.lower() == 'f':
            return 'run'
        elif choice.lower() == 'a':
            return 'accept'
        elif choice.lower() == 'r':
            return 'reraise'
    
    def get_card_choice(self, mao, truco_logic, allow_truco=True, allow_fugir=True):
        """
        Get a valid card choice from the player.
        
        Args:
            mao (list): The player's hand
            truco_logic (TrucoLogic): Truco logic instance for checking valid moves
            allow_truco (bool): Whether to allow the "truco" option
            allow_fugir (bool): Whether to allow the "fugir" option
        
        Returns:
            str: The validated choice (number as string, 't', or 'f')
        """
        valid_options = [str(i + 1) for i in range(len(mao))]
        
        # Check if player can call truco/reraise
        can_truco = (allow_truco and truco_logic.can_raise_truco("Jogador"))
        
        if can_truco:
            valid_options.append('t')
            next_value = truco_logic.get_next_truco_value()
            truco_name = truco_logic.get_truco_name(next_value)
            print(f"T: {truco_name}")
        elif allow_truco and not truco_logic.can_raise_truco("Jogador"):
            print("(Você já pediu o último truco/reraise desta mão)")
        
        if allow_fugir:
            valid_options.append('f')
            print("F: Fugir")
        
        # Build prompt
        prompt_options = ""
        if can_truco:
            next_value = truco_logic.get_next_truco_value()
            truco_name = truco_logic.get_truco_name(next_value)
            prompt_options += f", T ({truco_name})"
        if allow_fugir:
            prompt_options += ", F (Fugir)"
        
        prompt = f"Escolha o número da carta que deseja jogar{prompt_options}: "
        
        return self.get_valid_input(prompt, valid_options)
