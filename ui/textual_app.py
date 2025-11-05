from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button
from textual.screen import Screen
import asyncio

# timing and game config
from config import GameConfig

# Adapter to translate (demo) game state into widget payloads
from ui import adapter

# Import our widgets
from ui.widgets.battle_zone_widget import BattleZoneWidget
from ui.widgets.hand_widget import HandWidget
from ui.widgets.sidebar_widget import SidebarWidget
from ui.widgets.prompt_widget import PromptWidget
from ui.ui_controller import UIController

# Simple skeleton app for Truco 2000 using Textual
class TrucoModal(Screen):
    """Modal screen shown when the opponent raises truco and the player must respond.

    Uses controller.pending_truco to render the options. Keys: A (Aceitar), T (Truco/Aumentar), F (Fugir).
    """
    def compose(self) -> ComposeResult:
        # We'll render a centered message and three action buttons
        with Vertical():
            yield Static("Decisão de Truco", classes="title")
            yield Static("Aguardando sua resposta...", classes="subtitle")
            with Horizontal():
                yield Button("Aceitar", id="accept")
                yield Button("Aumentar", id="reraise")
                yield Button("Fugir", id="run")

    def on_mount(self) -> None:
        # Update the subtitle with the pending truco value from controller
        try:
            pending = self.app.controller.pending_truco
            msg = f"Oponente pediu {self.app.controller.truco.get_truco_name(pending['value'])}"
        except Exception:
            msg = "Pedido de truco"
        # Update the second Static (subtitle)
        try:
            subs = self.query("Static")
            # second Static is subtitle
            if len(subs) > 1:
                subs[1].update(msg)
        except Exception:
            pass

    async def on_button_pressed(self, event) -> None:
        action = getattr(event.button, "id", None)
        if not action:
            return
        # Map button ids to controller actions
        act_map = {"accept": "accept", "reraise": "reraise", "run": "run"}
        chosen = act_map.get(action)
        if not chosen:
            await self.app.pop_screen()
            return

        # Respond via controller and update main UI
        try:
            snapshot = self.app.controller.respond_to_truco(chosen)
        except Exception:
            snapshot = self.app.controller.get_snapshot()

        try:
            sidebar = self.app.query_one(SidebarWidget)
            hand = self.app.query_one(HandWidget)
            battle = self.app.query_one(BattleZoneWidget)
            prompt = self.app.query_one(PromptWidget)
        except Exception:
            sidebar = hand = battle = prompt = None

        if sidebar:
            sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
        if hand:
            self.app.current_hand_codes = snapshot.get("player_hand", [])
            self.app.current_hand_payload = adapter.hand_from_state(snapshot)
            self.app.selected_index = None
            hand.update_hand(self.app.current_hand_payload, self.app.selected_index)
        if battle:
            player_card, opponent_card = adapter.battle_from_state(snapshot)
            battle.update_zone(player_card, opponent_card)

        # Reset prompt buttons to defaults
        if prompt:
            try:
                prompt.update_actions([
                    ("play", "Jogar"),
                    ("truco", "Truco"),
                    ("run", "Fugir"),
                    ("restart", "Reiniciar"),
                ])
            except Exception:
                pass

        await self.app.pop_screen()

    async def on_key(self, event) -> None:
        try:
            k = event.key.lower()
        except Exception:
            return
        if k == "a":
            await self.on_button_pressed(type("E", (), {"button": type("B", (), {"id": "accept"})()}))
        elif k == "t":
            await self.on_button_pressed(type("E", (), {"button": type("B", (), {"id": "reraise"})()}))
        elif k == "f":
            await self.on_button_pressed(type("E", (), {"button": type("B", (), {"id": "run"})()}))

class TrucoTextualApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    # simple styling placeholders
    .main-area {
        background: $background;
        border: round $primary;
    }
    /* Battle zone (top) and Hand area (bottom) as separate boxed panels */
    .battle-area {
        height: 40%;
        border: round #3b82f6; /* blue border */
        background: #071033;   /* dark-blue panel background */
        padding: 1 1;
        margin-bottom: 1;
    }
    .hand-area {
        height: 60%;
        border: round #3b82f6;
        background: #071033; 
        padding: 1 1;
    }
    .sidebar {
        width: 36;
        border: round $secondary;
        padding: 1 1;
        background: $panel;
    }
    """

    def compose(self) -> ComposeResult:
        # Top header
        yield Header(show_clock=False)

        # Main content area: horizontal split (main + sidebar)
        with Horizontal():
            # Left: main area split vertically into Battle (top) and Hand (bottom)
            with Vertical(classes="main-area"):
                with Vertical(classes="battle-area"):
                    yield BattleZoneWidget()
                with Vertical(classes="hand-area"):
                    # Hand area: player's hand (side-by-side) and action prompt
                    yield HandWidget()
                    yield PromptWidget()

            # Right: sidebar
            with Vertical(classes="sidebar"):
                yield SidebarWidget()

        # Footer with hints
        yield Footer()

    # --- Runtime UI state (hand, selection) ---
    current_hand_codes: list = []
    current_hand_payload: list = []
    selected_index: int | None = None

    async def on_mount(self) -> None:
        # Show the main menu on start
        # instantiate controller used by UI for interactive play
        self.controller = UIController()
        await self.push_screen(MainMenu())

    async def start_game(self) -> None:
        """Reset controller and populate UI with a fresh game snapshot.

        This is called when the player presses Start in the main menu or when
        the Restart action is chosen.
        """
        try:
            # Reset controller state for a new hand/game
            self.controller.reset_hand()
            snapshot = self.controller.get_snapshot()

            sidebar = self.query_one(SidebarWidget)
            hand = self.query_one(HandWidget)
            battle = self.query_one(BattleZoneWidget)
        except Exception:
            return

        # Update runtime state
        self.current_hand_codes = snapshot.get("player_hand", [])
        self.current_hand_payload = adapter.hand_from_state(snapshot)
        self.selected_index = None

        # Update widgets
        sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
        hand.update_hand(self.current_hand_payload, self.selected_index)
        player_card, opponent_card = adapter.battle_from_state(snapshot)
        battle.update_zone(player_card, opponent_card)
        # Ensure prompt shows default actions (Portuguese labels)
        try:
            prompt = self.query_one(PromptWidget)
            prompt.update_actions([
                ("play", "Jogar"),
                ("truco", "Truco"),
                ("run", "Fugir"),
                ("restart", "Reiniciar"),
            ])
        except Exception:
            pass
    
    # (on_key is implemented later to include digit handling)

    async def load_demo(self) -> None:
        """Load a demo snapshot via the adapter and populate widgets."""
        state = adapter.demo_game_state()

        # Find widgets in the app
        try:
            sidebar = self.query_one(SidebarWidget)
            hand = self.query_one(HandWidget)
            battle = self.query_one(BattleZoneWidget)
        except Exception:
            # If widgets aren't present, do nothing
            return

        # Build payloads
        sidebar_payload = adapter.sidebar_from_state(state)
        hand_payload = adapter.hand_from_state(state)
        player_card, opponent_card = adapter.battle_from_state(state)

        # store runtime hand state for interactive actions
        self.current_hand_codes = state.get("player_hand", [])
        self.current_hand_payload = hand_payload
        self.selected_index = None

        # Update widgets (these are synchronous calls but safe on the main loop)
        sidebar.update_snapshot(sidebar_payload)
        hand.update_hand(hand_payload, self.selected_index)
        battle.update_zone(player_card, opponent_card)

    async def load_gamecore_snapshot(self) -> None:
        """Create a snapshot from a fresh GameCore via the adapter and populate widgets."""
        state = adapter.snapshot_from_gamecore()

        try:
            sidebar = self.query_one(SidebarWidget)
            hand = self.query_one(HandWidget)
            battle = self.query_one(BattleZoneWidget)
        except Exception:
            return

        sidebar_payload = adapter.sidebar_from_state(state)
        hand_payload = adapter.hand_from_state(state)
        player_card, opponent_card = adapter.battle_from_state(state)

        # store runtime hand state
        self.current_hand_codes = state.get("player_hand", [])
        self.current_hand_payload = hand_payload
        self.selected_index = None

        sidebar.update_snapshot(sidebar_payload)
        hand.update_hand(hand_payload, self.selected_index)
        battle.update_zone(player_card, opponent_card)

        # If opponent should start the first round, pre-play their card so the player
        # can see it before choosing (matches original CLI behavior).
        try:
            if not getattr(self.controller.core, "player_starts_round", True):
                snapshot = self.controller.opponent_play()
                sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
                # update hand payload (player hand unchanged)
                self.current_hand_payload = adapter.hand_from_state(snapshot)
                hand.update_hand(self.current_hand_payload, self.selected_index)
                player_card, opponent_card = adapter.battle_from_state(snapshot)
                battle.update_zone(player_card, opponent_card, status_text="Oponente jogou")
        except Exception:
            pass

    async def play_card(self, index: int) -> None:
        """Play a card from current_hand_codes at 1-based index.

        Updates hand widget and battle zone with the played card.
        """
        # Orchestrate a smooth turn: player plays -> opponent thinks -> opponent plays -> reveal -> resolve
        THINK_DELAY = 0.6
        REVEAL_DELAY = 0.8

        # Decide who starts this round (controller/core tracks it)
        starter_is_player = True
        try:
            starter_is_player = getattr(self.controller.core, "player_starts_round", True)
        except Exception:
            starter_is_player = True

        sidebar = hand = battle = None
        try:
            sidebar = self.query_one(SidebarWidget)
            hand = self.query_one(HandWidget)
            battle = self.query_one(BattleZoneWidget)
        except Exception:
            pass

        if starter_is_player:
            # Player starts: player plays first, then opponent
            try:
                snapshot = self.controller.play_player_card(index)
            except Exception:
                snapshot = self.controller.get_snapshot()

            # Update runtime UI to show player's played card
            self.current_hand_codes = snapshot.get("player_hand", [])
            self.current_hand_payload = adapter.hand_from_state(snapshot)
            self.selected_index = None

            if sidebar:
                sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
            if hand:
                hand.update_hand(self.current_hand_payload, self.selected_index)

            player_card, opponent_card = adapter.battle_from_state(snapshot)
            # show only player's card for now
            if battle:
                battle.update_zone(player_card, None, status_text=f"Você jogou")

            # Opponent thinking delay
            await asyncio.sleep(THINK_DELAY)

            # Opponent plays
            try:
                snapshot = self.controller.opponent_play()
            except Exception:
                snapshot = self.controller.get_snapshot()

            if sidebar:
                sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
            player_card, opponent_card = adapter.battle_from_state(snapshot)
            if battle:
                battle.update_zone(player_card, opponent_card, status_text=f"Oponente jogou")

            # Reveal pause
            await asyncio.sleep(REVEAL_DELAY)

            # Resolve round
            try:
                snapshot = self.controller.resolve_round()
            except Exception:
                snapshot = self.controller.get_snapshot()

        else:
            # Opponent starts: opponent plays first, then player
            # 1) Opponent plays (unless they already played and we pre-rendered their card)
            try:
                if not getattr(self.controller, "played", {}).get("opponent"):
                    snapshot = self.controller.opponent_play()
                else:
                    snapshot = self.controller.get_snapshot()
            except Exception:
                snapshot = self.controller.get_snapshot()

            # Update UI to show opponent only
            self.current_hand_payload = adapter.hand_from_state(snapshot)
            if sidebar:
                sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
            if hand:
                # don't change selection yet
                hand.update_hand(adapter.hand_from_state(snapshot), self.selected_index)
            player_card, opponent_card = adapter.battle_from_state(snapshot)
            if battle:
                # show only opponent for now
                battle.update_zone(None, opponent_card, status_text=f"Oponente jogou")

            # Short pause so player sees opponent card
            await asyncio.sleep(THINK_DELAY)

            # 2) Now player plays (we were triggered by player's key)
            try:
                snapshot = self.controller.play_player_card(index)
            except Exception:
                snapshot = self.controller.get_snapshot()

            # Update runtime UI to show player's played card
            self.current_hand_codes = snapshot.get("player_hand", [])
            self.current_hand_payload = adapter.hand_from_state(snapshot)
            self.selected_index = None
            if sidebar:
                sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
            if hand:
                hand.update_hand(self.current_hand_payload, self.selected_index)
            player_card, opponent_card = adapter.battle_from_state(snapshot)
            if battle:
                battle.update_zone(player_card, opponent_card, status_text=f"Você jogou")

            # Reveal pause before resolving
            await asyncio.sleep(REVEAL_DELAY)

            # Resolve round
            try:
                snapshot = self.controller.resolve_round()
            except Exception:
                snapshot = self.controller.get_snapshot()

        sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
        self.current_hand_codes = snapshot.get("player_hand", [])
        self.current_hand_payload = adapter.hand_from_state(snapshot)
        hand.update_hand(self.current_hand_payload, self.selected_index)
        player_card, opponent_card = adapter.battle_from_state(snapshot)
        battle.update_zone(player_card, opponent_card, status_text=f"{snapshot.get('message', '')}")

        # If the hand continues and the next round starter is the opponent,
        # have the opponent play immediately so the player sees the opponent's card
        # before making their selection (matches original CLI behavior).
        try:
            if not snapshot.get("hand_ended", False) and not getattr(self.controller.core, "player_starts_round", True):
                # Opponent plays for the upcoming round
                next_snapshot = self.controller.opponent_play()
                sidebar.update_snapshot(adapter.sidebar_from_state(next_snapshot))
                self.current_hand_payload = adapter.hand_from_state(next_snapshot)
                hand.update_hand(self.current_hand_payload, None)
                player_card, opponent_card = adapter.battle_from_state(next_snapshot)
                battle.update_zone(player_card, opponent_card, status_text="Oponente jogou")
        except Exception:
            pass

        # If the hand is complete (controller signals via hand_ended), show a short banner and auto-deal next hand
        try:
            if snapshot.get("hand_ended", False):
                # show end-of-hand message in sidebar (already set in snapshot['message'])
                await asyncio.sleep(1.0)
                p_score = snapshot.get("scores", {}).get("player", 0)
                o_score = snapshot.get("scores", {}).get("opponent", 0)
                if p_score >= GameConfig.WINNING_SCORE or o_score >= GameConfig.WINNING_SCORE:
                    # game over - show final message but do not auto-deal
                    try:
                        sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
                    except Exception:
                        pass
                else:
                    # auto-deal next hand
                    self.controller.reset_hand()
                    snapshot = self.controller.get_snapshot()
                    sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
                    self.current_hand_codes = snapshot.get("player_hand", [])
                    self.current_hand_payload = adapter.hand_from_state(snapshot)
                    hand.update_hand(self.current_hand_payload, None)
                    player_card, opponent_card = adapter.battle_from_state(snapshot)
                    battle.update_zone(player_card, opponent_card)
                    # If the opponent starts the new hand, pre-play their card so the player
                    # sees it before selecting their card (matches original CLI behavior).
                    try:
                        if not getattr(self.controller.core, "player_starts_round", True):
                            snapshot = self.controller.opponent_play()
                            sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
                            self.current_hand_payload = adapter.hand_from_state(snapshot)
                            hand.update_hand(self.current_hand_payload, None)
                            player_card, opponent_card = adapter.battle_from_state(snapshot)
                            battle.update_zone(player_card, opponent_card, status_text="Oponente jogou")
                    except Exception:
                        pass
        except Exception:
            pass

    async def on_button_pressed(self, event) -> None:
        # Handle PromptWidget button presses at the App level
        btn_id = getattr(event.button, "id", None)
        if btn_id == "play":
            # If a selection exists, play it; otherwise instruct user
            if self.selected_index:
                await self.play_card(self.selected_index)
            else:
                try:
                    sidebar = self.query_one(SidebarWidget)
                    sidebar.update_snapshot({"scores": {"player": 0, "opponent": 0}, "carta_vira": "-", "manilha": "-", "round_results": [], "message": "Pressione 1/2/3 para selecionar carta"})
                except Exception:
                    pass
        elif btn_id == "truco":
            try:
                # call controller.truco and update
                snapshot = self.controller.call_truco()
                sidebar = self.query_one(SidebarWidget)
                hand = self.query_one(HandWidget)
                battle = self.query_one(BattleZoneWidget)
                prompt = self.query_one(PromptWidget)

                sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
                # update hand/battle state
                self.current_hand_codes = snapshot.get("player_hand", [])
                self.current_hand_payload = adapter.hand_from_state(snapshot)
                self.selected_index = None
                hand.update_hand(self.current_hand_payload, self.selected_index)
                player_card, opponent_card = adapter.battle_from_state(snapshot)
                battle.update_zone(player_card, opponent_card)

                # If snapshot indicates a pending truco, either show modal or switch the prompt buttons inline
                if snapshot.get("pending_truco"):
                    try:
                        if GameConfig.USE_MODAL_TRUCO:
                            # Push the modal screen to ask the player
                            await self.push_screen(TrucoModal())
                        elif prompt:
                            prompt.update_actions([
                                ("accept", "Aceitar"),
                                ("reraise", "Aumentar"),
                                ("run", "Fugir"),
                                ("restart", "Reiniciar"),
                            ])
                    except Exception:
                        pass
            except Exception:
                pass

        elif btn_id in ("accept", "reraise"):
            # Inline handling for responding to a pending truco (from PromptWidget)
            try:
                action = "accept" if btn_id == "accept" else "reraise"
                snapshot = self.controller.respond_to_truco(action)
            except Exception:
                snapshot = self.controller.get_snapshot()

            try:
                sidebar = self.query_one(SidebarWidget)
                hand = self.query_one(HandWidget)
                battle = self.query_one(BattleZoneWidget)
                prompt = self.query_one(PromptWidget)
            except Exception:
                sidebar = hand = battle = prompt = None

            if sidebar:
                sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
            if hand:
                self.current_hand_codes = snapshot.get("player_hand", [])
                self.current_hand_payload = adapter.hand_from_state(snapshot)
                self.selected_index = None
                hand.update_hand(self.current_hand_payload, self.selected_index)
            if battle:
                player_card, opponent_card = adapter.battle_from_state(snapshot)
                battle.update_zone(player_card, opponent_card)

            # If still pending (opponent re-raised), leave inline buttons showing new pending options
            if prompt:
                try:
                    if snapshot.get("pending_truco"):
                        prompt.update_actions([
                            ("accept", "Aceitar"),
                            ("reraise", "Aumentar"),
                            ("run", "Fugir"),
                            ("restart", "Reiniciar"),
                        ])
                    else:
                        # restore default prompt
                        prompt.update_actions([
                            ("play", "Jogar"),
                            ("truco", "Truco"),
                            ("run", "Fugir"),
                            ("restart", "Reiniciar"),
                        ])
                except Exception:
                    pass
        elif btn_id == "run":
            try:
                snapshot = self.controller.run()
                sidebar = self.query_one(SidebarWidget)
                sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
            except Exception:
                pass
        elif btn_id == "restart":
            # Restart the game (reset controller and UI)
            try:
                # reset full match scores then start
                try:
                    self.controller.reset_match()
                except Exception:
                    pass
                await self.start_game()
                # If menu is visible, remove it
                try:
                    # close menu if present
                    self.pop_screen()
                except Exception:
                    pass
            except Exception:
                pass

    async def on_key(self, event) -> None:
        # Quick keys: m -> open menu, q -> quit, d -> demo snapshot
        try:
            key = event.key
        except Exception:
            return

        if key == "m":
            await self.push_screen(MainMenu())
        elif key == "q":
            self.exit()
        # note: demo (d) and gamecore (g) shortcuts removed; start the game via menu
        elif key in ("left", "arrow_left"):
            # move selection left (wrap)
            if self.current_hand_codes:
                if self.selected_index is None:
                    self.selected_index = 1
                else:
                    self.selected_index = (self.selected_index - 2) % len(self.current_hand_codes) + 1
                try:
                    hand = self.query_one(HandWidget)
                    hand.update_hand(self.current_hand_payload, self.selected_index)
                except Exception:
                    pass
        elif key in ("right", "arrow_right"):
            # move selection right (wrap)
            if self.current_hand_codes:
                if self.selected_index is None:
                    self.selected_index = 1
                else:
                    self.selected_index = (self.selected_index) % len(self.current_hand_codes) + 1
                try:
                    hand = self.query_one(HandWidget)
                    hand.update_hand(self.current_hand_payload, self.selected_index)
                except Exception:
                    pass
        elif key == "enter":
            # play selected card immediately
            if self.selected_index is not None:
                await self.play_card(self.selected_index)
        elif key.isdigit():
            idx = int(key)
            # If the digit corresponds to a card, select and play it
            if self.current_hand_codes and 1 <= idx <= len(self.current_hand_codes):
                self.selected_index = idx
                # immediate play on digit press
                await self.play_card(idx)

class MainMenu(Screen):
    """A minimal main menu screen with Start/Quit actions."""
    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("Truco 2000", classes="title")
            yield Static("Press Start to enter the game (or press 'q' to quit)", classes="subtitle")
            yield Button("Start Game", id="start")
            yield Button("Quit", id="quit")

    async def on_button_pressed(self, event) -> None:
        btn_id = getattr(event.button, "id", None)
        if btn_id == "start":
            # Start the game and dismiss the menu
            await self.app.start_game()
            try:
                self.app.pop_screen()
            except Exception:
                pass
        elif btn_id == "quit":
            self.app.exit()

    async def on_key(self, event) -> None:
        # Allow Enter to start and 'q' to quit
        try:
            key = event.key
        except Exception:
            return
        if key == "enter":
            await self.app.start_game()
            try:
                self.app.pop_screen()
            except Exception:
                pass
        elif key == "q":
            self.app.exit()


    # TrucoModal moved earlier to be defined before use


if __name__ == "__main__":
    app = TrucoTextualApp()
    app.run()
