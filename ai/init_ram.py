"""INIT-RAM: The Bluff-Master AI Opponent.

First opponent encountered by the player. Designed to teach aggressive bluffing,
recognizing bluffs, and making decisions on when to fold or accept.

Strategy:
- Aggressive Truco calls (30-40% bluffs)
- Concedes to player Truco ~60% of the time (rewards player bluff attempts)
- Predictable card strength thresholds
- Impatient, fast dialogue tone
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai.opponents import AIOpponentContext
    from truco_logic import TrucoLogic


class InitRam:
    """INIT-RAM: The Bluff-Master.
    
    Aries sign, aggressive bluffer, forces the player to learn truco psychology.
    """

    name = "INIT-RAM"
    description = "The Bluff-Master. Aggressive caller but weak follow-through. Learn when to fold or counter."
    
    # Per-hand state for bluff tracking
    hand_strength: str = ""  # "high", "medium", or "low"
    bluff_committed: bool = False
    
    def on_new_hand(self, context: AIOpponentContext) -> None:
        """Evaluate hand strength and decide bluff strategy for this hand."""
        # Classify opponent hand strength
        self.hand_strength = self._evaluate_hand_strength(context.opponent_hand, context.manilha)
        self.bluff_committed = False
    
    def _evaluate_hand_strength(self, hand: list[str], manilha: str) -> str:
        """Classify hand as 'high', 'medium', or 'low' based on card strength.
        
        High: Has manilha or multiple 3s, 2s, As
        Medium: Has some strong cards but not dominantly
        Low: Mostly weak cards (4s, 5s, 6s, 7s)
        """
        strong_cards = {manilha}  # Manilha is always strong
        strong_cards.update(["3", "2", "A"])  # Highest non-manilha cards
        
        strong_count = sum(1 for card in hand if any(rank in card for rank in ["3", "2", "A", manilha]))
        weak_count = sum(1 for card in hand if any(rank in card for rank in ["4", "5", "6", "7"]))
        
        if strong_count >= 2 or manilha in "".join(hand):
            return "high"
        elif strong_count >= 1 and weak_count <= 1:
            return "medium"
        else:
            return "low"
    
    def choose_card(self, context: AIOpponentContext) -> int:
        """Select a card to play.
        
        High hand: Play strongly (manilha first, or high cards)
        Medium hand: Play normally, set up for bluff potential
        Low hand: Play to minimize losses
        """
        hand = context.opponent_hand
        if not hand:
            return 0
        
        manilha = context.manilha
        
        if self.hand_strength == "high":
            # Play high cards aggressively
            return self._pick_strongest_card(hand, manilha)
        elif self.hand_strength == "medium":
            # Play a medium card to set up bluff potential
            return self._pick_medium_card(hand, manilha)
        else:  # low
            # Play the weakest card to preserve stronger options
            return self._pick_weakest_card(hand)
    
    def _pick_strongest_card(self, hand: list[str], manilha: str) -> int:
        """Return index of the manilha if present, else highest ranked card."""
        for i, card in enumerate(hand):
            if manilha in card:
                return i
        
        # Fallback to highest rank
        rank_order = {"3": 10, "2": 9, "A": 8, "K": 7, "J": 6, "Q": 5}
        return max(range(len(hand)), key=lambda i: rank_order.get(hand[i][0], 0))
    
    def _pick_medium_card(self, hand: list[str], manilha: str) -> int:
        """Pick a card that's moderately strong but not the best."""
        strong_cards = []
        weak_cards = []
        
        for i, card in enumerate(hand):
            if any(rank in card for rank in ["3", "2", "A"]):
                strong_cards.append(i)
            else:
                weak_cards.append(i)
        
        # Prefer a strong card if available, but not the manilha
        if strong_cards:
            return strong_cards[0]
        # Otherwise play first available
        return 0
    
    def _pick_weakest_card(self, hand: list[str]) -> int:
        """Return index of the weakest card."""
        rank_order = {"3": 10, "2": 9, "A": 8, "K": 7, "J": 6, "Q": 5, "7": 4, "6": 3, "5": 2, "4": 1}
        return min(range(len(hand)), key=lambda i: rank_order.get(hand[i][0], 0))
    
    def decide_truco_response(self, proposed_value: int, truco: TrucoLogic, context: AIOpponentContext) -> str:
        """Respond to player's truco call.
        
        Strategy:
        - High hand: Accept challenges (back up the bluff threat)
        - Medium hand: Concede ~60% of the time (reward player bluffs)
        - Low hand: Almost always concede (avoid losses)
        """
        if self.hand_strength == "high":
            # Strong hand: accept more often (75% accept, 25% run/reraise)
            if random.random() < 0.75:
                return "accept"
            else:
                return "run"
        
        elif self.hand_strength == "medium":
            # Medium hand: concede ~60% (reward bluff attempts)
            if random.random() < 0.60:
                return "run"
            else:
                return "accept"
        
        else:  # low hand
            # Low hand: almost always concede (~85%)
            if random.random() < 0.85:
                return "run"
            else:
                return "accept"
