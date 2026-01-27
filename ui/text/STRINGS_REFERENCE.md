# Strings Reference (i18n)

All UI strings are defined in `ui/text/locales/*.py` files.
Use hierarchical keys and `TextManager.get_text(key, **params)` to retrieve them.

## Keys

- welcome.title — App title
- welcome.prompt — Prompt to continue from welcome screen

- menu.play — Play button label
- menu.settings — Settings button label
- menu.tutorial — Tutorial button label
- menu.quit — Quit button label

- game.title — Game scene title
- game.placeholder — Placeholder message (until Phase 3+ rendering)
- game.esc_hint — ESC hint to return to menu

- common.opponent — "Opponent" label
- common.you — "You" label
- common.battle_zone — "Table"/"Mesa" label
- common.your_hand — "Your Hand"/"Sua Mão" label

- truco.call — "Truco" action
- truco.accept — Accept truco
- truco.raise — Raise truco
- truco.flee — Flee/run action

- results.winner — Winner message with {winner}
- results.score — Score line with {player_score} and {opponent_score}
- results.play_again — Play again button
- results.menu — Menu button

- error.invalid — Invalid input message
- prompt.confirm — Generic confirm prompt

## Usage

```python
from ui.text import TextManager

tm = TextManager("pt_br")
label = tm.get_text("menu.play")
message = tm.get_text("results.score", player_score=5, opponent_score=3)
```

## Adding New Languages

- Create a new file `ui/text/locales/<lang>.py`
- Define a `STRINGS = { ... }` dictionary
- Add the language code to `GameConfig.SUPPORTED_LANGUAGES`
- Set `GameConfig.DEFAULT_LANGUAGE` or call `TextManager.set_locale()` at runtime
