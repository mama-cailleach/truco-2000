from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button
from textual.screen import Screen
import asyncio

# timing and game config
from config import GameConfig

# How long the opponent 'thinks' before playing (seconds)
OPPONENT_THINK_DELAY = 0.6

# Adapter to translate (demo) game state into widget payloads
from ui import adapter

# Import our widgets
from ui.widgets.battle_zone_widget import BattleZoneWidget
from ui.widgets.hand_widget import HandWidget
from ui.widgets.sidebar_widget import SidebarWidget
from ui.widgets.prompt_widget import PromptWidget
from ui.widgets.truco_response_widget import TrucoResponseWidget
from ui.widgets.win_banner_widget import WinBannerWidget
from ui.ui_controller import UIController
from ui.ascii_art import ASCIIArt

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
            snap = adapter.snapshot_from_controller(self.app.controller)
            pending_name = snap.get("pending_truco_name")
            if pending_name:
                msg = f"Oponente pediu {pending_name}"
            else:
                msg = "Pedido de truco"
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

        # Respond via adapter (controller wrapper) and update main UI
        try:
            snapshot = adapter.respond_truco(self.app.controller, chosen)
        except Exception:
            snapshot = adapter.snapshot_from_controller(self.app.controller)

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
                disabled = self.get_disabled_button_ids(snapshot)
                prompt.update_actions([
                    ("play", "Jogar"),
                    ("truco", "Truco"),
                    ("run", "Fugir"),
                    ("restart", "Reiniciar"),
                ], disabled_ids=disabled)
            except Exception:
                pass

        # If this response ended the match, refresh snapshot and navigate to main menu
        try:
            snapshot = adapter.snapshot_from_controller(self.app.controller)
            game_over = await self.app.handle_game_over(snapshot)
            if game_over:
                # still pop modal so UI returns to main screen flow
                await self.app.pop_screen()
                return
        except Exception:
            pass

        # If hand ended (but match not over), auto-deal next hand and have opponent start if appropriate
        try:
            if snapshot.get("hand_ended", False):
                try:
                    # auto-deal next hand via adapter.reset_hand()
                    snapshot = adapter.reset_hand(self.app.controller)
                    try:
                        sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
                    except Exception:
                        pass
                    self.current_hand_codes = snapshot.get("player_hand", [])
                    self.current_hand_payload = adapter.hand_from_state(snapshot)
                    try:
                        hand.update_hand(self.current_hand_payload, None)
                    except Exception:
                        pass
                    try:
                        player_card, opponent_card = adapter.battle_from_state(snapshot)
                        battle.update_zone(player_card, opponent_card)
                    except Exception:
                        pass

                    # If opponent should start the new hand, pre-play their card
                    try:
                        if not snapshot.get("player_starts_round", True):
                            try:
                                await asyncio.sleep(OPPONENT_THINK_DELAY)
                            except Exception:
                                pass
                            next_snap = adapter.opponent_preplay(self.controller)
                            try:
                                sidebar.update_snapshot(adapter.sidebar_from_state(next_snap))
                            except Exception:
                                pass
                            self.current_hand_payload = adapter.hand_from_state(next_snap)
                            try:
                                hand.update_hand(self.current_hand_payload, None)
                            except Exception:
                                pass
                            try:
                                player_card, opponent_card = adapter.battle_from_state(next_snap)
                                battle.update_zone(player_card, opponent_card, status_text="Oponente jogou")
                            except Exception:
                                pass
                    except Exception:
                        pass
                except Exception:
                    pass
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
        color: #008F11;
        align: center middle;
    }
    # simple styling placeholders
    .main-area {
        background: #0D0208;
        border: round #00FF41;
    }
    /* Battle zone (top) and Hand area (bottom) as separate boxed panels */
    .battle-area {
        height: 40%;
        border: round #003B00; 
        background: #0D0208;   
        padding: 1 1;
        margin-bottom: 1;
    }
    .hand-area {
        height: 60%;
        border: round #003B00;
        background: #0D0208; 
        padding: 1 1;
    }
    #hand_container {
        height: auto;
        width: 100%;
    }
    #card_display {
        height: auto;
        width: 100%;
    }
    #action_buttons {
        height: auto;
        width: 100%;
    }
    #card_button_row {
        height: auto;
        width: 100%;
    }
    #card_button_row Button {
    padding: 0 0;      # Reduce horizontal padding (left/right)
    width: 7;          # Fixed small width
    min-width: 3;      # Override minimum
    margin: 0 2;  # Add 1 space on left and right of each button

    }
    .sidebar {
        width: 36;
        border: round #00FF41;
        background: #0D0208; 
        padding: 1 1;
    }
    PromptWidget {
        height: auto;
        width: 100%;
        margin-top: 1;
    }
    
    /* Base GameBanner styles */
    GameBanner {
        layer: overlay;
        dock: none;
        border: round #00FF41;
        background: #0D0208;
        padding: 1 2;
    }
    
    /* GameBanner container and content defaults */
    GameBanner > Vertical {
        width: 100%;
        height: auto;
        align: center middle;
        row-span: 1;
    }
    
    GameBanner Static {
        width: 100%;
        text-align: center;
    }
    
    GameBanner Horizontal {
        width: 100%;
        height: auto;
        align: center middle;
        column-span: 2;
    }
    
    /* Specific banner overrides */
    TrucoResponseWidget {
        width: 60;
        height: 10;
        border: round $error;
        background: $surface;
        offset: 0% 50%;
    }
    
    WinBannerWidget {
        width: 60;
        height: auto;
        offset: 0% 0%;
    }
    
    #win_banner_buttons Button {
        min-width: 14;
        margin: 0 2;
    }
    
    #truco_response_message {
        margin-bottom: 1;
    }
    
    /* Main Menu styles */
    MainMenu {
        background: #0D0208;
        align: center middle;
    }
    
    #menu_container {
        width: 80%;
        height: auto;
        align: center middle;
    }
    
    #menu_banner {
        color: #00FF41;
        text-align: left;
        width: 100%;
        margin-bottom: 0;
    }

    #menu_card_banner {
        color: #00FF41;
        text-align: left;
        width: 100%;
        margin-bottom: 0;
    }
    
    #menu_subtitle {
        color: #008F11;
        text-align: left;
        width: 100%;
        margin-bottom: 0;
    }
    
    #menu_buttons {
        width: 20;
        align: center middle;
        margin-left: 21;
    }
    
    #menu_buttons Button {
        width: 100%;
        margin: 1 2;
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
    game_over_active: bool = False

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
        # Clear any lingering game-over banner/state
        self.game_over_active = False
        self.remove_win_banner()
        try:
            prompt = self.query_one(PromptWidget)
            prompt.truco_btn.disabled = False
            prompt.run_btn.disabled = False
        except Exception:
            pass
        try:
            hand_widget = self.query_one(HandWidget)
            hand_widget.set_card_buttons_disabled(False)
        except Exception:
            pass
        try:
            # Reset controller state for a new hand/game via adapter
            snapshot = adapter.reset_hand(self.controller)

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
        # Update prompt button states (Truco/Run)
        try:
            prompt = self.query_one(PromptWidget)
            # Disable truco if player cannot raise
            if not snapshot.get("can_player_raise_truco", True):
                prompt.truco_btn.disabled = True
            else:
                prompt.truco_btn.disabled = False
        except Exception:
            pass

    async def handle_game_over(self, snapshot: dict) -> bool:
        """If either player reached the winning score, show the win banner overlay.

        Returns True if the game was over (banner shown), False otherwise.
        """
        try:
            p_score = snapshot.get("scores", {}).get("player", 0)
            o_score = snapshot.get("scores", {}).get("opponent", 0)
        except Exception:
            p_score = o_score = 0

        if p_score < GameConfig.WINNING_SCORE and o_score < GameConfig.WINNING_SCORE:
            # No winner yet; ensure flag is clear
            self.game_over_active = False
            return False

        # Already showing banner; keep it alive
        if self.game_over_active:
            return True

        self.game_over_active = True

        # Ensure final snapshot is visible in sidebar
        try:
            sidebar = self.query_one(SidebarWidget)
            sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
        except Exception:
            pass

        # Disable primary interactions
        try:
            hand_widget = self.query_one(HandWidget)
            hand_widget.set_card_buttons_disabled(True)
        except Exception:
            pass
        try:
            prompt = self.query_one(PromptWidget)
            prompt.truco_btn.disabled = True
            prompt.run_btn.disabled = True
        except Exception:
            pass
        # Remove any truco overlay that might still be present
        try:
            truco_overlay = self.query_one(TrucoResponseWidget)
            truco_overlay.remove()
        except Exception:
            pass

        # Mount the win banner over the battle area
        try:
            battle_area = self.query_one(".battle-area")
            try:
                existing_banner = self.query_one(WinBannerWidget)
                existing_banner.remove()
            except Exception:
                pass
            winner_text = "Você venceu o jogo!" if p_score >= GameConfig.WINNING_SCORE else "Oponente venceu o jogo!"
            banner = WinBannerWidget(winner_text=winner_text)
            await battle_area.mount(banner)
        except Exception:
            pass

        return True
    
    def get_disabled_button_ids(self, snapshot: dict) -> list:
        """Determine which buttons should be disabled based on game state.
        
        Returns a list of button ids that should be disabled.
        """
        disabled = []
        
        # Disable truco button if player cannot raise
        if not snapshot.get("can_player_raise_truco", True):
            disabled.append("truco")
        
        return disabled

    def remove_win_banner(self) -> None:
        """Remove the win banner overlay if it is mounted."""
        try:
            banner = self.query_one(WinBannerWidget)
            banner.remove()
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
        # can see it before choosing (matches original CLI behavior). Use adapter snapshot
        # so we avoid reaching into controller.core directly.
        try:
            ctrl_snap = adapter.snapshot_from_controller(self.controller)
            if not ctrl_snap.get("player_starts_round", True):
                # small thinking pause before opponent pre-plays
                try:
                    await asyncio.sleep(OPPONENT_THINK_DELAY)
                except Exception:
                    pass
                snapshot = adapter.opponent_preplay(self.controller)
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

        # Disable card buttons during this entire sequence
        try:
            hand = self.query_one(HandWidget)
            hand.set_card_buttons_disabled(True)
        except Exception:
            hand = None

        # Main play orchestration
        try:
            # Decide who starts this round (use adapter snapshot so UI doesn't access controller.core)
            starter_is_player = True
            try:
                ctrl_snap = adapter.snapshot_from_controller(self.controller)
                starter_is_player = ctrl_snap.get("player_starts_round", True)
            except Exception:
                starter_is_player = True

            sidebar = battle = None
            try:
                sidebar = self.query_one(SidebarWidget)
                battle = self.query_one(BattleZoneWidget)
            except Exception:
                pass

            if starter_is_player:
                # Player starts: player plays first, then opponent
                try:
                    snapshot = adapter.play_card(self.controller, index)
                except Exception:
                    snapshot = adapter.snapshot_from_controller(self.controller)

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
                    # opponent thinking pause
                    try:
                        await asyncio.sleep(OPPONENT_THINK_DELAY)
                    except Exception:
                        pass
                    snapshot = adapter.opponent_play(self.controller)
                except Exception:
                    snapshot = adapter.snapshot_from_controller(self.controller)

                if sidebar:
                    sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
                player_card, opponent_card = adapter.battle_from_state(snapshot)
                if battle:
                    battle.update_zone(player_card, opponent_card, status_text=f"Oponente jogou")

                # Reveal pause
                await asyncio.sleep(REVEAL_DELAY)

                # Resolve round
                try:
                    snapshot = adapter.resolve_round(self.controller)
                except Exception:
                    snapshot = adapter.snapshot_from_controller(self.controller)

            else:
                # Opponent starts: opponent plays first, then player
                # 1) Opponent plays (unless they already played and we pre-rendered their card)
                try:
                    if not getattr(self.controller, "played", {}).get("opponent"):
                        # opponent thinking pause before initial opponent play
                        try:
                            await asyncio.sleep(OPPONENT_THINK_DELAY)
                        except Exception:
                            pass
                        snapshot = adapter.opponent_play(self.controller)
                    else:
                        snapshot = adapter.snapshot_from_controller(self.controller)
                except Exception:
                    snapshot = adapter.snapshot_from_controller(self.controller)

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
                    snapshot = adapter.play_card(self.controller, index)
                except Exception:
                    snapshot = adapter.snapshot_from_controller(self.controller)

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
                    snapshot = adapter.resolve_round(self.controller)
                except Exception:
                    snapshot = adapter.snapshot_from_controller(self.controller)

            sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
            self.current_hand_codes = snapshot.get("player_hand", [])
            self.current_hand_payload = adapter.hand_from_state(snapshot)
            hand.update_hand(self.current_hand_payload, self.selected_index)
            player_card, opponent_card = adapter.battle_from_state(snapshot)
            battle.update_zone(player_card, opponent_card, status_text=f"{snapshot.get('message', '')}")

            # If the match just ended, show banner and stop further flow
            try:
                game_over = await self.handle_game_over(snapshot)
                if game_over:
                    return
            except Exception:
                pass

            # Pause so players can see the played cards, then clear the battle zone
            try:
                CLEAR_DELAY = 1.0
                await asyncio.sleep(CLEAR_DELAY)
                # Clear the table for the upcoming card placements
                try:
                    battle.update_zone(None, None, status_text="")
                except Exception:
                    pass
            except Exception:
                pass

            # If the hand continues and the next round starter is the opponent,
            # have the opponent play immediately so the player sees the opponent's card
            # before making their selection (matches original CLI behavior).
            try:
                ctrl_snap = adapter.snapshot_from_controller(self.controller)
                if not snapshot.get("hand_ended", False) and not ctrl_snap.get("player_starts_round", True):
                    # Opponent thinking pause then pre-play for the upcoming round (clear player's old card first)
                    try:
                        await asyncio.sleep(OPPONENT_THINK_DELAY)
                    except Exception:
                        pass
                    next_snapshot = adapter.opponent_preplay(self.controller)
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
                    try:
                        await asyncio.sleep(1.0)
                    except Exception:
                        pass

                    # Refresh snapshot from controller (scores may have changed during resolve)
                    try:
                        snapshot = adapter.snapshot_from_controller(self.controller)
                    except Exception:
                        pass

                    # Not game-over: proceed to auto-deal next hand
                    # auto-deal next hand (reset via adapter)
                    snapshot = adapter.reset_hand(self.controller)
                    sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
                    self.current_hand_codes = snapshot.get("player_hand", [])
                    self.current_hand_payload = adapter.hand_from_state(snapshot)
                    hand.update_hand(self.current_hand_payload, None)
                    player_card, opponent_card = adapter.battle_from_state(snapshot)
                    battle.update_zone(player_card, opponent_card)
                    
                    # Update prompt buttons with new disabled state
                    try:
                        prompt = self.query_one(PromptWidget)
                        # Update truco button state
                        if not snapshot.get("can_player_raise_truco", True):
                            prompt.truco_btn.disabled = True
                        else:
                            prompt.truco_btn.disabled = False
                    except Exception:
                        pass
                    
                    # Re-enable card buttons for next hand
                    try:
                        hand.set_card_buttons_disabled(False)
                    except Exception:
                        pass
                    
                    # If the opponent starts the new hand, pre-play their card so the player
                        # sees it before selecting their card (matches original CLI behavior).
                    try:
                        if not snapshot.get("player_starts_round", True):
                            try:
                                await asyncio.sleep(OPPONENT_THINK_DELAY)
                            except Exception:
                                pass
                            snapshot = adapter.opponent_preplay(self.controller)
                            sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
                            self.current_hand_payload = adapter.hand_from_state(snapshot)
                            hand.update_hand(self.current_hand_payload, None)
                            player_card, opponent_card = adapter.battle_from_state(snapshot)
                            battle.update_zone(player_card, opponent_card, status_text="Oponente jogou")
                    except Exception:
                        pass
            except Exception:
                pass
        except Exception:
            pass
        finally:
            # Ensure card buttons are re-enabled when play_card completes
            try:
                hand = self.query_one(HandWidget)
                hand.set_card_buttons_disabled(self.game_over_active)
            except Exception:
                pass

    async def on_button_pressed(self, event) -> None:
        # Handle button presses from HandWidget (card buttons) and PromptWidget (truco/run)
        btn_id = getattr(event.button, "id", None)
        if not btn_id:
            return

        # If game is over, only allow win-banner actions
        if self.game_over_active and btn_id not in ("win_play_again", "win_menu", "win_quit"):
            return

        # Win banner actions
        if btn_id == "win_play_again":
            try:
                adapter.reset_match(self.controller)
            except Exception:
                pass
            self.game_over_active = False
            self.remove_win_banner()
            await self.start_game()
            return
        elif btn_id == "win_menu":
            self.game_over_active = False
            self.remove_win_banner()
            try:
                await self.push_screen(MainMenu())
            except Exception:
                pass
            return
        elif btn_id == "win_quit":
            self.exit()
            return
        
        # Card button clicks: card_1, card_2, card_3
        if btn_id.startswith("card_"):
            try:
                card_num = int(btn_id.split("_")[1])
                if 1 <= card_num <= len(self.current_hand_codes):
                    await self.play_card(card_num)
            except Exception:
                pass
            return
        
        # Main action buttons
        elif btn_id == "truco":
            try:
                # call controller.truco and update via adapter
                snapshot = adapter.call_truco(self.controller)
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

                # If snapshot indicates a pending truco, show truco response banner
                if snapshot.get("pending_truco"):
                    try:
                        pending_name = snapshot.get("pending_truco_name", "Truco")
                        # Show truco response widget inside hand-area container
                        hand_area = self.query_one(".hand-area")
                        truco_response = TrucoResponseWidget(pending_name)
                        # Mount it inside hand-area as overlay
                        await hand_area.mount(truco_response)
                        # Disable card buttons during truco negotiation
                        try:
                            hand.set_card_buttons_disabled(True)
                        except Exception:
                            pass
                        # Disable truco button during pending truco
                        try:
                            prompt.truco_btn.disabled = True
                        except Exception:
                            pass
                    except Exception:
                        pass
                # After call_truco, refresh snapshot and check for game over in case points were awarded
                try:
                    snapshot = adapter.snapshot_from_controller(self.controller)
                    game_over = await self.handle_game_over(snapshot)
                    if game_over:
                        return
                except Exception:
                    pass
                # If call_truco resulted in the hand ending (but not game-over), auto-deal next hand
                try:
                    if snapshot.get("hand_ended", False):
                        # auto-deal next hand via adapter.reset_hand()
                        try:
                            snapshot = adapter.reset_hand(self.controller)
                            sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
                        except Exception:
                            pass
                        try:
                            self.current_hand_codes = snapshot.get("player_hand", [])
                            self.current_hand_payload = adapter.hand_from_state(snapshot)
                            hand.update_hand(self.current_hand_payload, None)
                        except Exception:
                            pass
                        try:
                            player_card, opponent_card = adapter.battle_from_state(snapshot)
                            battle.update_zone(player_card, opponent_card)
                        except Exception:
                            pass
                        
                        # Update prompt buttons with new disabled state
                        try:
                            disabled = self.get_disabled_button_ids(snapshot)
                            prompt.update_actions([
                                ("play", "Jogar"),
                                ("truco", "Truco"),
                                ("run", "Fugir"),
                                ("restart", "Reiniciar"),
                            ], disabled_ids=disabled)
                        except Exception:
                            pass
                        
                        try:
                            if not snapshot.get("player_starts_round", True):
                                try:
                                    await asyncio.sleep(OPPONENT_THINK_DELAY)
                                except Exception:
                                    pass
                                next_snap = adapter.opponent_preplay(self.controller)
                                try:
                                    sidebar.update_snapshot(adapter.sidebar_from_state(next_snap))
                                except Exception:
                                    pass
                                self.current_hand_payload = adapter.hand_from_state(next_snap)
                                try:
                                    hand.update_hand(self.current_hand_payload, None)
                                except Exception:
                                    pass
                                try:
                                    player_card, opponent_card = adapter.battle_from_state(next_snap)
                                    battle.update_zone(player_card, opponent_card, status_text="Oponente jogou")
                                except Exception:
                                    pass
                        except Exception:
                            pass
                except Exception:
                    pass
            except Exception:
                pass

        elif btn_id in ("truco_accept", "truco_reraise", "truco_run"):
            # Handle truco response buttons from TrucoResponseWidget
            try:
                action_map = {
                    "truco_accept": "accept",
                    "truco_run": "run",
                    "truco_reraise": "reraise"
                }
                action = action_map.get(btn_id)
                if action:
                    snapshot = adapter.respond_truco(self.controller, action)
                else:
                    snapshot = adapter.snapshot_from_controller(self.controller)
            except Exception:
                snapshot = adapter.snapshot_from_controller(self.controller)

            try:
                sidebar = self.query_one(SidebarWidget)
                hand = self.query_one(HandWidget)
                battle = self.query_one(BattleZoneWidget)
            except Exception:
                sidebar = hand = battle = None

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

            # If still pending (opponent re-raised), update truco response widget
            try:
                if snapshot.get("pending_truco"):
                    pending_name = snapshot.get("pending_truco_name", "Truco")
                    try:
                        truco_response = self.query_one(TrucoResponseWidget)
                        truco_response.update_message(pending_name)
                    except Exception:
                        # Widget doesn't exist yet, create it
                        try:
                            hand_area = self.query_one(".hand-area")
                            truco_response = TrucoResponseWidget(pending_name)
                            await hand_area.mount(truco_response)
                        except Exception:
                            pass
                else:
                    # Hand ended or no pending truco, remove overlay and re-enable buttons
                    try:
                        truco_response = self.query_one(TrucoResponseWidget)
                        truco_response.remove()
                    except Exception:
                        pass
                    # Re-enable card buttons
                    try:
                        hand = self.query_one(HandWidget)
                        hand.set_card_buttons_disabled(False)
                    except Exception:
                        pass
                    # Re-enable truco button
                    try:
                        prompt = self.query_one(PromptWidget)
                        if snapshot.get("can_player_raise_truco", True):
                            prompt.truco_btn.disabled = False
                    except Exception:
                        pass
            except Exception:
                pass
            
            # If the response awarded points and ended the match, navigate to main menu
            try:
                # Refresh snapshot to ensure any score changes are visible
                snapshot = adapter.snapshot_from_controller(self.controller)
                game_over = await self.handle_game_over(snapshot)
                if game_over:
                    return
            except Exception:
                pass
            # If inline response ended hand (but not game over), auto-deal next hand
            try:
                if snapshot.get("hand_ended", False):
                    try:
                        snapshot = adapter.reset_hand(self.controller)
                        sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
                    except Exception:
                        pass
                    try:
                        self.current_hand_codes = snapshot.get("player_hand", [])
                        self.current_hand_payload = adapter.hand_from_state(snapshot)
                        hand.update_hand(self.current_hand_payload, None)
                    except Exception:
                        pass
                    try:
                        player_card, opponent_card = adapter.battle_from_state(snapshot)
                        battle.update_zone(player_card, opponent_card)
                    except Exception:
                        pass
                    try:
                        if not snapshot.get("player_starts_round", True):
                            try:
                                await asyncio.sleep(OPPONENT_THINK_DELAY)
                            except Exception:
                                pass
                            next_snap = adapter.opponent_preplay(self.controller)
                            try:
                                sidebar.update_snapshot(adapter.sidebar_from_state(next_snap))
                            except Exception:
                                pass
                            self.current_hand_payload = adapter.hand_from_state(next_snap)
                            try:
                                hand.update_hand(self.current_hand_payload, None)
                            except Exception:
                                pass
                            try:
                                player_card, opponent_card = adapter.battle_from_state(next_snap)
                                battle.update_zone(player_card, opponent_card, status_text="Oponente jogou")
                            except Exception:
                                pass
                    except Exception:
                        pass
            except Exception:
                pass
        elif btn_id == "run":
            try:
                # Player flees: perform flee via adapter which returns a snapshot
                snapshot = adapter.flee(self.controller)
                try:
                    sidebar = self.query_one(SidebarWidget)
                    sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
                except Exception:
                    pass

                # Immediately refresh snapshot so UI shows updated hand/table state
                try:
                    snapshot = adapter.snapshot_from_controller(self.controller)
                except Exception:
                    pass

                # Update all widgets with the freshest snapshot so the UI reflects the score update
                try:
                    sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
                except Exception:
                    pass
                try:
                    self.current_hand_codes = snapshot.get("player_hand", [])
                    self.current_hand_payload = adapter.hand_from_state(snapshot)
                    hand = self.query_one(HandWidget)
                    hand.update_hand(self.current_hand_payload, None)
                except Exception:
                    pass
                try:
                    battle = self.query_one(BattleZoneWidget)
                    player_card, opponent_card = adapter.battle_from_state(snapshot)
                    battle.update_zone(player_card, opponent_card)
                except Exception:
                    pass

                # If the match is over, navigate to main menu immediately (no banner/auto-deal)
                try:
                    game_over = await self.handle_game_over(snapshot)
                    if game_over:
                        return
                except Exception:
                    pass

                # Immediately clear the battle zone so the table appears reset
                try:
                    battle = self.query_one(BattleZoneWidget)
                    try:
                        battle.update_zone(None, None, status_text="")
                    except Exception:
                        pass
                except Exception:
                    pass

                # Not game-over: reset the hand immediately so opponent will start the new hand
                try:
                    snapshot = adapter.reset_hand(self.controller)
                    try:
                        sidebar.update_snapshot(adapter.sidebar_from_state(snapshot))
                    except Exception:
                        pass
                    self.current_hand_codes = snapshot.get("player_hand", [])
                    self.current_hand_payload = adapter.hand_from_state(snapshot)
                    try:
                        hand = self.query_one(HandWidget)
                        hand.update_hand(self.current_hand_payload, None)
                    except Exception:
                        pass
                    try:
                        player_card, opponent_card = adapter.battle_from_state(snapshot)
                        battle.update_zone(player_card, opponent_card)
                    except Exception:
                        pass

                    # If opponent should start the new hand, pre-play their card so the player sees it before selecting
                    try:
                        if not snapshot.get("player_starts_round", True):
                            try:
                                await asyncio.sleep(OPPONENT_THINK_DELAY)
                            except Exception:
                                pass
                            next_snap = adapter.opponent_preplay(self.controller)
                            try:
                                sidebar.update_snapshot(adapter.sidebar_from_state(next_snap))
                            except Exception:
                                pass
                            self.current_hand_payload = adapter.hand_from_state(next_snap)
                            try:
                                hand.update_hand(self.current_hand_payload, None)
                            except Exception:
                                pass
                            try:
                                player_card, opponent_card = adapter.battle_from_state(next_snap)
                                battle.update_zone(player_card, opponent_card, status_text="Oponente jogou")
                            except Exception:
                                pass
                    except Exception:
                        pass
                except Exception:
                    pass

                # Show an end-of-hand banner for a short delay so the player sees the result
                try:
                    await asyncio.sleep(1.0)
                except Exception:
                    pass
            except Exception:
                pass

    async def on_key(self, event) -> None:
        # Quick keys: m -> menu, q -> quit, w -> restart, 1/2/3 -> play card
        try:
            key = event.key
        except Exception:
            return

        # If game is over, only allow restart/menu/quit shortcuts
        if self.game_over_active and key not in ("m", "q", "w"):
            return

        if key == "m":
            self.game_over_active = False
            self.remove_win_banner()
            await self.push_screen(MainMenu())
        elif key == "q":
            self.exit()
        elif key == "w":
            # Restart the match
            try:
                adapter.reset_match(self.controller)
            except Exception:
                pass
            self.game_over_active = False
            self.remove_win_banner()
            await self.start_game()
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
    """Main menu screen with ASCII art banner and game options."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ascii_art = ASCIIArt()
    
    def compose(self) -> ComposeResult:
        with Vertical(id="menu_container"):
            # ASCII art banner
            yield Static(self.ascii_art.get_intro_banner(), id="menu_banner", classes="banner_art")
            # Card banner
            yield Static(self.ascii_art.get_card_decoration(), id="menu_card_banner", classes="card_banner_art")
            # Game subtitle
            yield Static(self.ascii_art.get_game_subtitle(), id="menu_subtitle", classes="subtitle_art")
            # Button container
            with Vertical(id="menu_buttons"):
                yield Button("Jogar", id="start", variant="success")
                yield Button("Configurações", id="settings", variant="primary")
                yield Button("Tutorial", id="tutorial", variant="default")
                #yield Button("Sair", id="quit", variant="error")

    async def on_button_pressed(self, event) -> None:
        btn_id = getattr(event.button, "id", None)
        if btn_id == "start":
            # Reset match (clear scores) then start the game and dismiss the menu
            try:
                adapter.reset_match(self.app.controller)
            except Exception:
                pass
            await self.app.start_game()
            try:
                self.app.pop_screen()
            except Exception:
                pass
        elif btn_id == "settings":
            # Placeholder for settings screen
            pass
        elif btn_id == "tutorial":
            # Placeholder for tutorial screen
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
            try:
                adapter.reset_match(self.app.controller)
            except Exception:
                pass
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
