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
    }


def sidebar_from_state(state: Dict) -> Dict:
    # Sidebar widget expects a snapshot dict with specific keys; keep it simple
    return {
        "scores": state.get("scores", {}),
        "carta_vira": state.get("carta_vira", "-"),
        "manilha": state.get("manilha", "-"),
        "round_results": state.get("round_results", []),
        "message": state.get("message"),
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
    }
    return state


def snapshot_from_controller(controller) -> Dict:
    """Attempt to build a snapshot from a GameController instance.

    If controller doesn't expose the current hand state (common), fall back to
    creating a fresh GameCore snapshot so the UI can still show something.
    """
    try:
        # controller.core has scores at least
        core = getattr(controller, "core", None)
        scores = {"player": getattr(core, "pontos_jogador", 0), "opponent": getattr(core, "pontos_oponente", 0)}
        # We don't assume controller keeps the current dealt hands in attributes, so fall back
        # to snapshot_from_gamecore for hands/manilha
        base = snapshot_from_gamecore()
        base["scores"] = scores
        return base
    except Exception:
        return demo_game_state()
