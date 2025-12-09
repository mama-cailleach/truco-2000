from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
from truco_logic import TrucoLogic


@dataclass
class AIOpponentContext:
    """Lightweight snapshot of state exposed to AI opponents.

    This avoids leaking controller internals but provides enough signal for
    decision making and debugging.
    """

    opponent_hand: List[str]
    player_hand: List[str]
    played: Dict[str, Optional[str]]
    manilha: str
    carta_vira: str
    scores: Dict[str, int]
    current_hand_value: int
    last_accepted_value: int
    pending_truco: Optional[Dict]
    round_results: List[str]
    player_starts_round: bool
    player_starts_hand: bool


class BaseAIOpponent:
    """Base class for all AI opponents.

    Subclasses implement card selection and truco behaviour. All methods are
    synchronous and deterministic by default; add randomness inside overrides
    as needed.
    """

    name: str = "Base"
    description: str = "Placeholder opponent; override in subclasses."

    def on_new_hand(self, context: AIOpponentContext) -> None:
        """Hook called at the start of each hand. Override to reset per-hand state."""
        return

    def choose_card(self, context: AIOpponentContext) -> int:
        """Return the index of the card to play from opponent_hand (0-based).

        The controller will pop the card at this index. Must be within bounds.
        Default: play the first card (index 0) to preserve legacy behaviour.
        """
        return 0

    def decide_truco_response(self, proposed_value: int, truco: TrucoLogic, context: AIOpponentContext) -> str:
        """Decide how to respond when the player raises to proposed_value.

        Return one of: 'accept', 'run', or 'reraise'. Default delegates to
        TrucoLogic's legacy random/threshold response to preserve current behaviour.
        """
        try:
            return truco.get_opponent_truco_response(proposed_value)
        except Exception:
            return "accept"


class BaselineOpponent(BaseAIOpponent):
    """Baseline opponent mirroring the current random/simple behaviour.

    This keeps the game playable while we build bespoke opponents.
    """

    name = "Baseline"
    description = "Plays first card; truco responses match legacy logic."

    # Inherit BaseAIOpponent defaults
    pass
