"""
Adapter Module for Pygame UI.

Translates game-state dictionaries into structured snapshots for rendering.
Provides functions to bridge GameController/GameCore state with the UI layer.
"""

from typing import Dict, List, Optional, Tuple

def render_card(code: str) -> List[str]:
    """Return a small ASCII block for a card code like 'A♠' or '10♥'."""
    if not code:
        return ["(sem carta)"]
    rank = code[:-1]
    suit = code[-1]
    # Keep fixed width for simplicity
    top = "┌─────┐"
    line1 = f"│{rank:<2} {suit} │"
    line2 = "│     │"
    line3 = f"│ {suit} {rank:>2}│"
    bottom = "└─────┘"
    return [top, line1, line2, line3, bottom]


def demo_game_state() -> Dict:
    """Return a small demo game state we can use for UI testing."""
    return {
        "scores": {"player": 5, "opponent": 3},
        "carta_vira": "4♦",
        "manilha": "7♣",
        "round_results": ["Você", "Oponente", "Você"],
        # player hand: list of card codes
        "player_hand": ["A♠", "7♥", "3♦"],
        # played cards (None if not played yet)
        "played": {"player": "A♠", "opponent": "K♣"},
        "current_hand_value": 1,
    }


def sidebar_from_state(state: Dict) -> Dict:
    # Sidebar widget expects a snapshot dict with specific keys; keep it simple
    return {
        "scores": state.get("scores", {}),
        "carta_vira": state.get("carta_vira", "-"),
        "manilha": state.get("manilha", "-"),
        "round_results": state.get("round_results", []),
        "message": state.get("message"),
        "current_hand_value": state.get("current_hand_value", 1),
    }


def hand_from_state(state: Dict) -> List[List[str]]:
    hand_codes = state.get("player_hand", [])
    return [render_card(code) for code in hand_codes]


def battle_from_state(state: Dict) -> Tuple[Optional[List[str]], Optional[List[str]]]:
    played = state.get("played", {})
    p = played.get("player")
    o = played.get("opponent")
    player_card = render_card(p) if p else None
    opponent_card = render_card(o) if o else None
    return player_card, opponent_card


def snapshot_from_gamecore() -> Dict:
    """Create a demo snapshot using a fresh GameCore instance.

    This avoids mutating any running GameCore used elsewhere in the program.
    """
    try:
        from game_core import GameCore
    except Exception:
        # If GameCore isn't importable for some reason, fall back to demo_game_state
        return demo_game_state()

    core = GameCore()
    core.reiniciar_baralho()
    carta_vira, manilha = core.determinar_manilha()
    # deal three cards each
    player_hand = core.distribuir_cartas(3)
    opponent_hand = core.distribuir_cartas(3)

    state = {
        "scores": {"player": core.pontos_jogador, "opponent": core.pontos_oponente},
        "carta_vira": carta_vira,
        "manilha": manilha,
        "round_results": [],
        "player_hand": player_hand,
        "played": {"player": None, "opponent": None},
        "current_hand_value": 1,  # Default hand value at start
    }
    return state


def snapshot_from_controller(controller) -> Dict:
    """
    Build a comprehensive snapshot from a GameController instance for Pygame rendering.
    
    Returns a structured dictionary with all data needed for the renderer:
    - opponent_name: Name of the opponent
    - opponent_card_count: Number of cards in opponent's hand
    - hand: List of card codes in player's hand
    - battle: Dict with player_card and opponent_card (cards currently played)
    - current_round: Round number (1-3)
    - sidebar: Dict with player_score, opponent_score, truco_value, truco_name, manilha
    - player_starts_round: Whether player starts this round
    - player_starts_hand: Whether player started this hand
    - pending_truco: Any pending truco negotiation state
    """
    try:
        # Try to get snapshot from controller
        try:
            snap = controller.get_snapshot()
        except Exception:
            # Fall back to building from GameCore
            core = getattr(controller, "core", None)
            scores = {
                "player": getattr(core, "pontos_jogador", 0),
                "opponent": getattr(core, "pontos_oponente", 0)
            }
            snap = snapshot_from_gamecore()
            snap["scores"] = scores
            
            # Get truco value from truco logic
            truco = getattr(controller, "truco", None)
            if truco:
                snap["current_hand_value"] = getattr(truco, "current_hand_value", 1)

        # Build enhanced snapshot for Pygame renderer
        enhanced_snap = {
            # Opponent info
            "opponent_name": snap.get("opponent_name", "INIT-RAM"),
            "opponent_card_count": len(snap.get("opponent_hand", [])),
            
            # Player hand
            "hand": snap.get("player_hand", []),
            
            # Battle zone (played cards)
            "battle": {
                "player_card": snap.get("played", {}).get("player"),
                "opponent_card": snap.get("played", {}).get("opponent")
            },
            
            # Round info
            "current_round": len(snap.get("round_results", [])) + 1,
            
            # Sidebar data
            "sidebar": {
                "player_score": snap.get("scores", {}).get("player", 0),
                "opponent_score": snap.get("scores", {}).get("opponent", 0),
                "opponent_name": snap.get("opponent_name", "INIT-RAM"),
                "truco_value": snap.get("current_hand_value", 1),
                "truco_name": _get_truco_name(snap.get("current_hand_value", 1), controller),
                "vira": snap.get("carta_vira", "?"),
                "manilha": snap.get("manilha", "?")
            },
            
            # Game flow flags
            "player_starts_round": snap.get("player_starts_round", True),
            "player_starts_hand": snap.get("player_starts_hand", True),
            "pending_truco": snap.get("pending_truco"),
            "round_results": snap.get("round_results", [])
        }

        return enhanced_snap
        
    except Exception:
        # Ultimate fallback
        return {
            "opponent_name": "Oponente",
            "opponent_card_count": 0,
            "hand": [],
            "battle": {"player_card": None, "opponent_card": None},
            "current_round": 1,
            "sidebar": {
                "player_score": 0,
                "opponent_score": 0,
                "opponent_name": "INIT-RAM",
                "truco_value": 1,
                "truco_name": "Normal",
                "vira": "?",
                "manilha": "?"
            },
            "player_starts_round": True,
            "player_starts_hand": True,
            "pending_truco": None,
            "round_results": []
        }


def _get_truco_name(value: int, controller) -> str:
    """Get the human-readable name for a truco value."""
    try:
        truco = getattr(controller, "truco", None)
        if truco and hasattr(truco, "get_truco_name"):
            return truco.get_truco_name(value)
    except Exception:
        pass
    
    # Fallback names
    names = {1: "Normal", 3: "Truco", 6: "Seis", 9: "Nove", 12: "Doze"}
    return names.get(value, f"Valor {value}")


def play_card(controller, index: int) -> Dict:
    """Adapter wrapper for playing a player's card via the controller.

    Returns the controller snapshot after the play.
    """
    try:
        # Use controller's play_player_card (non-blocking controller step)
        snap = controller.play_player_card(index)
        return snap
    except Exception:
        try:
            return controller.get_snapshot()
        except Exception:
            return demo_game_state()


def opponent_play(controller) -> Dict:
    """Adapter wrapper for opponent playing a card."""
    try:
        return controller.opponent_play()
    except Exception:
        try:
            return controller.get_snapshot()
        except Exception:
            return demo_game_state()


def opponent_preplay(controller) -> Dict:
    """Adapter wrapper used when the UI wants the opponent to pre-play for the
    upcoming round. This clears any lingering player's played card so the table
    shows only the opponent's preview card.
    """
    try:
        # Clear player's played slot if present to avoid showing an old card
        try:
            if hasattr(controller, "played") and isinstance(controller.played, dict):
                controller.played["player"] = None
        except Exception:
            pass

        return controller.opponent_play()
    except Exception:
        try:
            return controller.get_snapshot()
        except Exception:
            return demo_game_state()


def resolve_round(controller) -> Dict:
    """Adapter wrapper to resolve the currently played round."""
    try:
        return controller.resolve_round()
    except Exception:
        try:
            return controller.get_snapshot()
        except Exception:
            return demo_game_state()


def call_truco(controller) -> Dict:
    """Adapter wrapper for initiating a truco from the player."""
    try:
        return controller.call_truco()
    except Exception:
        try:
            return controller.get_snapshot()
        except Exception:
            return demo_game_state()


def respond_truco(controller, action: str) -> Dict:
    """Adapter wrapper for responding to a pending truco (accept/run/reraise)."""
    try:
        return controller.respond_to_truco(action)
    except Exception:
        try:
            return controller.get_snapshot()
        except Exception:
            return demo_game_state()


def flee(controller) -> Dict:
    """Adapter wrapper for fleeing/run from truco (player runs)."""
    try:
        return controller.run()
    except Exception:
        try:
            return controller.get_snapshot()
        except Exception:
            return demo_game_state()


def reset_hand(controller) -> Dict:
    """Adapter wrapper to reset the current hand on the controller and
    return the resulting snapshot."""
    try:
        controller.reset_hand()
        return snapshot_from_controller(controller)
    except Exception:
        try:
            return controller.get_snapshot()
        except Exception:
            return demo_game_state()


def reset_match(controller) -> Dict:
    """Adapter wrapper to reset the whole match (scores) and start a fresh hand."""
    try:
        controller.reset_match()
        return snapshot_from_controller(controller)
    except Exception:
        try:
            return controller.get_snapshot()
        except Exception:
            return demo_game_state()
