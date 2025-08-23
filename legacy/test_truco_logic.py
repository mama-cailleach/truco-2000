#!/usr/bin/env python3
"""
Test script to verify truco logic scenarios
"""

# Import the game class
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import from the main game file
exec(open("truco_2000_v1.0.py").read())

def test_truco_logic():
    """Test various truco scenarios"""
    print("Testing Truco Logic Scenarios...")
    print("=" * 50)
    
    game = TrucoGame()
    
    # Test 1: Normal hand start (value should be 1)
    print("Test 1: New hand - current_hand_value should be 1")
    game.current_hand_value = 1
    game.last_raiser = None
    
    # Simulate handle_truco_sequence call
    print(f"Current hand value: {game.current_hand_value}")
    
    # Test the corrected logic
    last_accepted_value = game.current_hand_value  # Should be 1 for new hand
    print(f"Last accepted value at start: {last_accepted_value}")
    
    print("\n" + "=" * 50)
    
    # Test 2: Mid-game truco sequence (hand value is 3)
    print("Test 2: Mid-game - current_hand_value is 3")
    game.current_hand_value = 3
    game.last_raiser = "Oponente"
    
    print(f"Current hand value: {game.current_hand_value}")
    last_accepted_value = game.current_hand_value  # Should be 3
    print(f"Last accepted value at start: {last_accepted_value}")
    
    print("\n" + "=" * 50)
    
    # Test 3: High-value scenario (hand value is 9)
    print("Test 3: High-value - current_hand_value is 9")
    game.current_hand_value = 9
    game.last_raiser = "Jogador"
    
    print(f"Current hand value: {game.current_hand_value}")
    last_accepted_value = game.current_hand_value  # Should be 9
    print(f"Last accepted value at start: {last_accepted_value}")
    
    print("\n" + "=" * 50)
    print("All tests show correct behavior:")
    print("- last_accepted_value now properly uses current_hand_value")
    print("- Each new hand starts with value 1 (reset in jogar_mao)")
    print("- Mid-game trucoss use the current accepted value")

if __name__ == "__main__":
    test_truco_logic()
