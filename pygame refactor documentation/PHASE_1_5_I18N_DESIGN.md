# Phase 1.5 Addition: Internationalization (i18n) & Text Separation

## Summary of Changes

A new phase has been inserted into the refactor plan to ensure all UI text is separated from code, enabling future multi-language support (Portuguese + English).

## Phase Placement

**Phase 1.5** is now positioned logically between:
- **Phase 1**: Pygame app skeleton & window management (creates the basic UI structure)
- **Phase 1.5** ← **NEW**: i18n & text separation (extracts and organizes all strings)
- **Phase 2**: Input handling & scene navigation (refactored to reference TextManager for all text)

All subsequent phases have been renumbered:
- Old Phase 2 → Phase 2 (Input Handling)
- Old Phase 3 → Phase 3 (Game State Rendering)
- Old Phase 4 → Phase 4 (Card Play & Truco)
- Old Phase 5 → Phase 5 (Match Flow)
- Old Phase 6 → Phase 6 (Animations)
- Old Phase 7 → Phase 7 (Settings/Menu)
- Old Phase 8 → Phase 9 (Testing & Cleanup)

## What Phase 1.5 Includes

### Structure
```
ui/text/
├── __init__.py              # TextManager class (loads/manages language strings)
├── locales/                 # Language-specific files
│   ├── pt_br.py            # Brazilian Portuguese (PRIMARY - fully populated)
│   └── en_us.py            # English (template for future)
└── STRINGS_REFERENCE.md     # Documentation of all string keys
```

### Key Tasks

1. **TextManager Implementation**
   - Load language files dynamically
   - `get_text(key)` method for simple strings
   - `get_text(key, **params)` for parameterized strings
   - Support runtime language switching
   - Store current locale in `config.py`

2. **Language Files (Python Dictionaries)**
   - Portuguese: `ui/text/locales/pt_br.py`
   - English template: `ui/text/locales/en_us.py`
   - Hierarchical keys (e.g., `welcome.title`, `menu.play`, `truco.accept`)

3. **String Extraction** from:
   - `ui/scenes/*.py` - scene titles, button labels, prompts
   - `config.py` - any UI messages
   - Phase 1 placeholder text

4. **Scene Updates**
   - Inject TextManager into scenes
   - Replace all hardcoded strings with `text_manager.get_text('key')`
   - Ensure all text renders correctly in Portuguese

5. **Configuration Updates**
   - Add `DEFAULT_LANGUAGE = "pt_br"` to config.py
   - Add `SUPPORTED_LANGUAGES = ["pt_br", "en_us"]`
   - Optional: `AUTO_DETECT_LANGUAGE = False`

6. **Documentation**
   - Create `ui/text/STRINGS_REFERENCE.md`
   - List all string keys and their purposes
   - Guide for translators

### Example String Keys Structure

```python
# ui/text/locales/pt_br.py
STRINGS = {
    # Welcome Scene
    "welcome.title": "TRUCO 2000",
    "welcome.prompt": "Pressione qualquer tecla para continuar...",
    
    # Menu Scene
    "menu.play": "JOGAR",
    "menu.settings": "CONFIGURAÇÕES",
    "menu.tutorial": "TUTORIAL",
    "menu.quit": "SAIR",
    
    # Game Scene
    "game.opponent": "Oponente",
    "game.player": "Você",
    "game.battle_zone": "Mesa",
    "game.your_hand": "Sua Mão",
    
    # Truco Actions
    "truco.call": "TRUCO",
    "truco.accept": "ACEITAR",
    "truco.raise": "AUMENTAR",
    "truco.flee": "FUGIR",
    
    # Results
    "results.winner": "Vencedor: {winner}",
    "results.score": "Placar - Você: {player_score} | Oponente: {opponent_score}",
    "results.play_again": "JOGAR NOVAMENTE",
    "results.menu": "MENU",
    
    # Common
    "common.cancel": "CANCELAR",
    "common.confirm": "CONFIRMAR",
    "common.close": "FECHAR",
}
```

## Benefits

✅ **Easy multi-language support** - Add new language by creating `ui/text/locales/new_lang.py`
✅ **Translator-friendly** - Non-programmers can work on translations independently
✅ **Maintainability** - Centralized terminology control ensures consistency
✅ **CSV export ready** - Can easily export STRINGS dict for professional translation workflows
✅ **Version control** - Language files tracked separately for translation updates
✅ **Clean separation** - Code logic completely decoupled from UI text

## Optional Enhancements

- Export strings to CSV for translation management tools
- Add string versioning to track translation status
- Create CLI tool to verify all keys are used (no orphans)
- Auto-detect system locale for language selection
- Add string validation (check for missing keys at startup)

## Phase 2+ Adjustments

All subsequent phases have been updated to account for TextManager:
- Scene constructors now receive TextManager instance
- Button widget pulls labels from TextManager
- Phase 2 tasks note: "Pull button text from TextManager"
- All scenes use `text_manager.get_text('key')` instead of hardcoded strings

## Configuration Changes Needed

In `config.py`:
```python
# Add to GameConfig class:
DEFAULT_LANGUAGE = "pt_br"
SUPPORTED_LANGUAGES = ["pt_br", "en_us"]
AUTO_DETECT_LANGUAGE = False  # Optional
```

## Execution Order

This phase should be executed **after Phase 1** is complete because:
1. We need the scene structure (Phase 1) to know what strings to extract
2. We can then systematically replace all hardcoded strings
3. Phase 2 input handling can reference TextManager from the start
4. This prevents string duplication and ensures consistency across all phases

## Next Steps

Once Phase 1.5 is complete:
1. All UI scenes use TextManager for text retrieval
2. Portuguese language file is fully populated
3. English template ready for translation
4. Future language additions require only creating a new locale file
5. Ready to proceed with Phase 2 (Input Handling)

---

**Status**: Phase 1.5 design complete. Ready to implement after Phase 1.
**Language**: Primary = Portuguese (pt_br), Secondary = English (en_us - template)
