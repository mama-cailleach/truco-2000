from typing import Dict, List, Optional, Tuple

# Adapter functions that translate a game-state dict into widget payloads.
# For now we provide a demo snapshot generator and pure functions that
# return structures consumable by the widgets in ui/widgets/.

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
    """Attempt to build a snapshot from a GameController instance.

    If controller doesn't expose the current hand state (common), fall back to
    creating a fresh GameCore snapshot so the UI can still show something.
    """
    try:
        # Prefer controller.get_snapshot() when available so we reflect live state
        try:
            snap = controller.get_snapshot()
        except Exception:
            # fall back to building a snapshot from a fresh GameCore
            core = getattr(controller, "core", None)
            scores = {"player": getattr(core, "pontos_jogador", 0), "opponent": getattr(core, "pontos_oponente", 0)}
            snap = snapshot_from_gamecore()
            snap["scores"] = scores
            # Try to get current_hand_value from controller's truco logic
            truco = getattr(controller, "truco", None)
            if truco:
                snap["current_hand_value"] = getattr(truco, "current_hand_value", 1)

        # Include starter flags from controller.core when available so UI can
        # decide who should play next without reaching into controller internals.
        core = getattr(controller, "core", None)
        try:
            snap["player_starts_round"] = getattr(core, "player_starts_round", True)
            snap["player_starts_hand"] = getattr(core, "player_starts_hand", True)
        except Exception:
            snap["player_starts_round"] = snap.get("player_starts_round", True)
            snap["player_starts_hand"] = snap.get("player_starts_hand", True)

        # If there's a pending truco, include a human-friendly name for display
        try:
            pending = snap.get("pending_truco")
            if pending and hasattr(controller, "truco"):
                try:
                    snap["pending_truco_name"] = controller.truco.get_truco_name(pending.get("value"))
                except Exception:
                    snap["pending_truco_name"] = None
        except Exception:
            pass

        return snap
    except Exception:
        return demo_game_state()


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
