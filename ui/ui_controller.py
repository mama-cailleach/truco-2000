from typing import Dict, Optional, List
from game_core import GameCore
from config import GameConfig
from truco_logic import TrucoLogic
from ai.opponents import BaseAIOpponent, BaselineOpponent, AIOpponentContext, _get_default_opponent

class UIController:
    """Lightweight controller used by the Textual UI for prototyping interactions.

    This intentionally keeps logic simple and does not implement full Truco
    negotiation. It uses GameCore for card dealing, scoring, and winner determination.
    """
    def __init__(self, opponent_ai: Optional[BaseAIOpponent] = None):
        self.core = GameCore()
        self.config = GameConfig
        self.truco = TrucoLogic()
        self.opponent_ai: BaseAIOpponent = opponent_ai or _get_default_opponent()
        self.message: Optional[str] = None
        self.reset_hand()

    def reset_hand(self):
        self.core.reiniciar_baralho()
        carta_vira, manilha = self.core.determinar_manilha()
        self.carta_vira = carta_vira
        self.manilha = manilha
        # deal hands
        self.player_hand = self.core.distribuir_cartas(self.config.CARDS_PER_HAND)
        self.opponent_hand = self.core.distribuir_cartas(self.config.CARDS_PER_HAND)
        self.played = {"player": None, "opponent": None}
        self.round_results = []
        # reset truco state for new hand
        self.truco.reset_truco_state()
        self.message = None
        # pending_truco holds a dict when the UI must respond to an opponent raise
        # Example: {"value": 6, "raiser": "Oponente", "last_accepted": 3}
        self.pending_truco = None
        # per-hand tracking
        self.vitorias_jogador = 0
        self.vitorias_oponente = 0
        self.primeira_vitoria = None
        self.current_round = 0
        # Flag used by UI to indicate the current hand has finished
        self.hand_ended = False
        # Ensure round-starter follows the hand starter for a fresh hand
        try:
            self.core.player_starts_round = getattr(self.core, "player_starts_hand", True)
        except Exception:
            pass

        # Notify opponent AI of new hand
        try:
            self.opponent_ai.on_new_hand(self._build_ai_context())
        except Exception:
            pass

    def set_opponent_ai(self, opponent_ai: Optional[BaseAIOpponent]):
        """Swap the active opponent AI (useful for debugging/testing different profiles)."""
        self.opponent_ai = opponent_ai or BaselineOpponent()

    def reset_match(self):
        """Reset match-level scores and start a fresh hand.

        Use this when the user requests a full restart of the match.
        """
        # Reset core scores
        try:
            self.core.pontos_jogador = 0
            self.core.pontos_oponente = 0
        except Exception:
            pass
        # Start a fresh hand as well
        self.reset_hand()

    def get_snapshot(self) -> Dict:
        # Get pending truco name if one exists
        pending_truco_name = None
        if self.pending_truco:
            try:
                pending_truco_name = self.truco.get_truco_name(self.pending_truco.get("value"))
            except Exception:
                pending_truco_name = "Truco"
        
        return {
            "scores": {"player": self.core.pontos_jogador, "opponent": self.core.pontos_oponente},
            "carta_vira": self.carta_vira,
            "manilha": self.manilha,
            "round_results": self.round_results.copy(),
            "player_hand": self.player_hand.copy(),
            "played": self.played.copy(),
            "message": self.message,
            "pending_truco": self.pending_truco,
            "pending_truco_name": pending_truco_name,
            "hand_ended": getattr(self, "hand_ended", False),
            "can_player_raise_truco": self.truco.can_raise_truco("Jogador"),
            "current_hand_value": self.truco.current_hand_value,
        }

    # --- Split play flow into explicit steps so UI can animate/delay ---
    def play_player_card(self, index: int) -> Dict:
        """Remove the player's card from hand and set it as played (no opponent action)."""
        if index < 1 or index > len(self.player_hand):
            return self.get_snapshot()
        card = self.player_hand.pop(index - 1)
        self.played["player"] = card
        # clear any transient message
        self.message = None
        return self.get_snapshot()

    def opponent_play(self) -> Dict:
        """Choose an opponent card and set it as played. Returns snapshot."""
        opp_card = None
        if self.opponent_hand:
            try:
                context = self._build_ai_context()
                idx = self.opponent_ai.choose_card(context)
                if idx is None:
                    idx = 0
                if idx < 0 or idx >= len(self.opponent_hand):
                    idx = 0
                opp_card = self.opponent_hand.pop(idx)
            except Exception:
                opp_card = self.opponent_hand.pop(0)
            self.played["opponent"] = opp_card
        return self.get_snapshot()

    def resolve_round(self) -> Dict:
        """Resolve the currently played cards: determine winner, update scores and round_results."""
        p = self.played.get("player")
        o = self.played.get("opponent")
        winner = None
        try:
            winner = self.core.vencedor_rodada(p, o, self.manilha)
        except Exception:
            winner = None
        # Update per-round counters and messages, but DO NOT award hand points yet
        if winner == "Jogador":
            self.vitorias_jogador += 1
            if self.primeira_vitoria is None:
                self.primeira_vitoria = "Jogador"
            self.round_results.append("Você")
            self.message = "Você ganhou a rodada"
            # Player won this round and will start the next round
            try:
                self.core.player_starts_round = True
            except Exception:
                pass
        elif winner == "Oponente":
            self.vitorias_oponente += 1
            if self.primeira_vitoria is None:
                self.primeira_vitoria = "Oponente"
            self.round_results.append("Oponente")
            self.message = "Oponente ganhou a rodada"
            # Opponent won this round and will start the next round
            try:
                self.core.player_starts_round = False
            except Exception:
                pass
        else:
            self.round_results.append("Empate")
            self.message = "Empate"

        # Check if hand should end using core rules
        end_hand, winner_msg = self.core.check_hand_winner(self.current_round, self.round_results, self.vitorias_jogador, self.vitorias_oponente, self.primeira_vitoria)

        if end_hand:
            # Determine hand winner and award hand-level points (truco multiplier)
            if self.vitorias_jogador > self.vitorias_oponente:
                hand_winner = "Jogador"
            elif self.vitorias_oponente > self.vitorias_jogador:
                hand_winner = "Oponente"
            else:
                # tie-breaker by primeira_vitoria
                if self.primeira_vitoria == "Jogador":
                    hand_winner = "Jogador"
                elif self.primeira_vitoria == "Oponente":
                    hand_winner = "Oponente"
                else:
                    hand_winner = None

            if hand_winner:
                # Points for the hand are the current truco value
                points = self.truco.current_hand_value
                self.core.update_score(hand_winner, points)
                # set message to hand-level winner message
                self.message = winner_msg or f"{hand_winner} venceu a mão ({points} pontos)"

                # Winner of the hand starts the next hand
                try:
                    self.core.player_starts_hand = (hand_winner == "Jogador")
                    # Also set next round start to the same player for the new hand
                    self.core.player_starts_round = (hand_winner == "Jogador")
                except Exception:
                    pass

            # mark hand complete; played cards remain until UI resets for next hand
            self.hand_ended = True
            # Clear table state so future snapshots don't show stale cards
            try:
                self.played["player"] = None
                self.played["opponent"] = None
            except Exception:
                pass
            # increment current_round for completeness
            self.current_round += 1
            return self.get_snapshot()

        # Hand continues; advance round counter
        self.current_round += 1
        # Clear table state for the next round so snapshots don't show old cards
        try:
            self.played["player"] = None
            self.played["opponent"] = None
        except Exception:
            pass
        return self.get_snapshot()

    def play_card(self, index: int) -> Dict:
        """Play a card from player's hand (1-based index). Returns new snapshot."""
        if index < 1 or index > len(self.player_hand):
            return self.get_snapshot()
        card = self.player_hand.pop(index-1)
        self.played["player"] = card
        # opponent plays a simple card (first available)
        opp_card = None
        if self.opponent_hand:
            opp_card = self.opponent_hand.pop(0)
            self.played["opponent"] = opp_card
        # determine winner for this round
        winner = None
        try:
            winner = self.core.vencedor_rodada(card, opp_card, self.manilha)
        except Exception:
            winner = None
        if winner == "Jogador":
            self.core.update_score("Jogador", 1)
            self.round_results.append("Você")
        elif winner == "Oponente":
            self.core.update_score("Oponente", 1)
            self.round_results.append("Oponente")
        else:
            self.round_results.append("Empate")
        # clear transient message after play
        self.message = None
        return self.get_snapshot()

    def call_truco(self) -> Dict:
        # Player initiates a truco request. We drive a single step of negotiation
        # and return either a completed result or a pending request for the UI.
        
        # First, check if player can raise truco (not the last raiser, and not at max value)
        if not self.truco.can_raise_truco("Jogador"):
            self.message = "Você não pode aumentar agora (você aumentou por último)"
            return self.get_snapshot()
        
        next_value = self.truco.get_next_truco_value()
        if next_value is None:
            self.message = "Já no valor máximo de truco"
            return self.get_snapshot()

        # Opponent decides reactively via AI hook
        try:
            response = self.opponent_ai.decide_truco_response(next_value, self.truco, self._build_ai_context())
        except Exception:
            response = self.truco.get_opponent_truco_response(next_value)
        if response == 'accept':
            # Opponent accepted player's truco
            self.truco.update_truco_state(next_value, 'Jogador')
            self.message = f"Oponente aceitou {self.truco.get_truco_name(next_value)}"
            return self.get_snapshot()
        elif response == 'run':
            # Opponent fled — award last accepted points (before this raise proposal)
            last_accepted = self.truco.last_accepted_value
            winner, points = self.truco.calculate_points_for_runner('Oponente', next_value, last_accepted)
            self.core.update_score(winner, points)
            self.message = f"{winner} ganha {points} ponto(s) (fugiu)"
            # Mark the hand ended and set next-hand/round starter based on winner
            try:
                self.core.player_starts_hand = (winner == "Jogador")
                self.core.player_starts_round = (winner == "Jogador")
            except Exception:
                pass
            self.hand_ended = True
            return self.get_snapshot()
        else:
            # Opponent re-raised — compute the new value and create a pending request
            opp_new = self.truco.get_next_truco_value(next_value)
            if opp_new is None:
                # cannot reraise further; treat as acceptance
                self.truco.update_truco_state(next_value, 'Jogador')
                self.message = f"Oponente aceitou {self.truco.get_truco_name(next_value)}"
                return self.get_snapshot()

            # Create pending truco for the UI to respond to
            # By re-raising, opponent implicitly accepted next_value, so it becomes last_accepted
            self.pending_truco = {
                "value": opp_new,
                "raiser": "Oponente",
                "last_accepted": next_value,
            }
            self.message = f"Oponente pediu {self.truco.get_truco_name(opp_new)} - Aceitar / Fugir / Aumentar?"
            return self.get_snapshot()

    def run(self) -> Dict:
        # Player runs from truco: calculate points based on current truco state
        # Use last_accepted_value (not current_hand_value) as the points to award
        last_accepted = self.truco.last_accepted_value
        winner, points = self.truco.calculate_points_for_runner("Jogador", self.truco.current_hand_value, last_accepted)
        self.core.update_score(winner, points)
        self.message = f"{winner} ganha {points} ponto(s) (fugiu)"
        # Mark the hand as ended and set the next hand/round starter to opponent
        try:
            # When the player flees, opponent will start the next hand/round
            self.core.player_starts_hand = False
            self.core.player_starts_round = False
        except Exception:
            pass

        # Let the UI show an end-of-hand banner; UI will call adapter.reset_hand()
        self.hand_ended = True
        return self.get_snapshot()

    def _build_ai_context(self) -> AIOpponentContext:
        """Build a sanitized context snapshot for AI decision making."""
        return AIOpponentContext(
            opponent_hand=self.opponent_hand.copy(),
            player_hand=self.player_hand.copy(),
            played=self.played.copy(),
            manilha=self.manilha,
            carta_vira=self.carta_vira,
            scores={"player": self.core.pontos_jogador, "opponent": self.core.pontos_oponente},
            current_hand_value=self.truco.current_hand_value,
            last_accepted_value=self.truco.last_accepted_value,
            pending_truco=self.pending_truco.copy() if isinstance(self.pending_truco, dict) else self.pending_truco,
            round_results=self.round_results.copy(),
            player_starts_round=getattr(self.core, "player_starts_round", True),
            player_starts_hand=getattr(self.core, "player_starts_hand", True),
        )

    def respond_to_truco(self, action: str) -> Dict:
        """Handle a player response to a pending opponent truco.

        action: one of 'accept', 'run', 'reraise'
        """
        if not self.pending_truco:
            self.message = "Nenhum truco pendente"
            return self.get_snapshot()

        pending = self.pending_truco
        value = pending["value"]
        last_accepted = pending.get("last_accepted", self.truco.current_hand_value)

        if action == 'accept':
            # Player accepts the opponent's raise
            self.truco.update_truco_state(value, 'Oponente')
            self.message = f"Você aceitou {self.truco.get_truco_name(value)}"
            self.pending_truco = None
            return self.get_snapshot()

        if action == 'run':
            # Player runs — opponent wins last accepted points
            winner, points = self.truco.calculate_points_for_runner('Jogador', value, last_accepted)
            self.core.update_score(winner, points)
            self.message = f"{winner} ganha {points} ponto(s) (fugiu)"
            # Clear pending and mark hand completed; set starter based on winner
            self.pending_truco = None
            try:
                self.core.player_starts_hand = (winner == "Jogador")
                self.core.player_starts_round = (winner == "Jogador")
            except Exception:
                pass
            self.hand_ended = True
            return self.get_snapshot()

        if action == 'reraise':
            # Player increases the raise further
            next_val = self.truco.get_next_truco_value(value)
            if next_val is None:
                # cannot reraise further; treat as accept
                self.truco.update_truco_state(value, 'Oponente')
                self.message = f"Valor máximo atingido. Aceito {self.truco.get_truco_name(value)}"
                self.pending_truco = None
                return self.get_snapshot()

            # Now opponent must respond to the player's reraise
            opp_resp = self.truco.get_opponent_truco_response(next_val)
            if opp_resp == 'accept':
                self.truco.update_truco_state(next_val, 'Jogador')
                self.message = f"Oponente aceitou {self.truco.get_truco_name(next_val)}"
                self.pending_truco = None
                return self.get_snapshot()
            elif opp_resp == 'run':
                # Opponent runs from player's re-raise; player wins value (what was implicitly accepted)
                winner, points = self.truco.calculate_points_for_runner('Oponente', next_val, value)
                self.core.update_score(winner, points)
                self.message = f"{winner} ganha {points} ponto(s) (fugiu)"
                self.pending_truco = None
                return self.get_snapshot()
            else:
                # Opponent reraise again — create new pending request
                opp_new = self.truco.get_next_truco_value(next_val)
                if opp_new is None:
                    self.truco.update_truco_state(next_val, 'Jogador')
                    self.message = f"Oponente aceitou {self.truco.get_truco_name(next_val)}"
                    self.pending_truco = None
                    return self.get_snapshot()
                self.pending_truco = {"value": opp_new, "raiser": "Oponente", "last_accepted": next_val}
                self.message = f"Oponente pediu {self.truco.get_truco_name(opp_new)} - Aceitar / Fugir / Aumentar?"
                return self.get_snapshot()

        # Unknown action
        self.message = "Ação desconhecida"
        return self.get_snapshot()

    # --- Methods used by TrucoLogic for callbacks/input ---
    def get_truco_response(self, value: int, raiser: str, truco_names: Dict) -> str:
        """Called when opponent raised truco and we must respond.

        For now, automatically accept (UI can be extended later to prompt user).
        """
        # In future, this should pause and wait for UI input; for now accept.
        self.message = f"Oponente pediu {truco_names.get(value, value)}"
        return 'accept'

    def show_truco_call(self, who: str, value: int, truco_names: Dict):
        self.message = f"{who} pediu {truco_names.get(value, value)}"

    def show_truco_acceptance(self, who: str, value: int, truco_names: Dict):
        self.message = f"{who} aceitou {truco_names.get(value, value)}"

    def show_opponent_runs(self, value: int, truco_names: Dict):
        self.message = f"Oponente fugiu de {truco_names.get(value, value)}"
