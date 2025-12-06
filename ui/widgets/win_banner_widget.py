from ui.widgets.game_banner import GameBanner


class WinBannerWidget(GameBanner):
    """Overlay banner shown when the match ends.

    Displays the winner message and provides primary next-step actions.
    """

    def __init__(self, winner_text: str, **kwargs):
        buttons = [
            ("Jogar Novamente", "win_play_again", "success"),
            ("Menu", "win_menu", "primary"),
            ("Sair", "win_quit", "error"),
        ]
        super().__init__(
            message=winner_text,
            buttons=buttons,
            banner_id="win_banner",
            message_classes="win_title",
            **kwargs
        )
