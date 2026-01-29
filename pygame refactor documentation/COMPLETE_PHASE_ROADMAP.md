# Complete Pygame Refactor Phase Sequence

## Full Roadmap (9 Phases Total)

### ✅ Phase 0 — Prep & Setup
**Status**: COMPLETED
- Archive legacy Textual code to `textual_legacy/`
- Update requirements (remove Textual, add Pygame)
- Add Pygame settings to config.py
- Update copilot instructions

### ✅ Phase 1 — Pygame App Skeleton & Window Management
**Status**: COMPLETED  
- Create main Pygame app (`ui/pygame_app.py`)
- Create scene framework (`ui/scenes/base_scene.py`)
- Create placeholder scenes (Welcome, Menu, Game)
- Update `main.py` entry point
- **Result**: Runnable Pygame window with basic scene navigation

### ⏭️ Phase 1.5 — Internationalization (i18n) & Text Separation
**Status**: DESIGNED (Ready to implement)
- Create `ui/text/` with TextManager class
- Create language files: `pt_br.py` (Portuguese - PRIMARY), `en_us.py` (English - template)
- Extract all hardcoded strings from Phase 1
- Update all scenes to use TextManager
- Add language config settings
- Document all string keys in STRINGS_REFERENCE.md
- **Result**: All UI text separated from code, Portuguese fully supported, ready for multi-language

### Phase 2 — Input Handling & Scene Navigation
- Create `ui/input_handler.py` for Pygame input system
- Implement scene transitions (Welcome → Menu → Game)
- Create `ui/widgets/button.py` with TextManager integration
- Update MenuScene with buttons pulling text from TextManager
- **Result**: Clickable buttons, working navigation, text from TextManager

### Phase 3 — Game State Rendering (ASCII Cards → Pygame)
- Refactor `ui/adapter.py` (remove Textual refs)
- Create `ui/renderer.py` with rendering pipeline
- Create `ui/widgets/card_display.py`
- Create `ui/assets/` directory structure
- Update GameScene to display dealt hand
- **Result**: Game state rendering working, hand visible

### ✅ Phase 4 — Interactive Card Play & Truco Negotiation
**Status**: COMPLETED
- Wire card click events to play cards
- Implement card selection and highlighting
- Create truco negotiation UI (Accept/Raise/Flee)
- Integrate opponent AI via adapter
- **Result**: Full hand gameplay working

### ✅ Phase 4.5 — Full Truco Escalation & State Management
**Status**: COMPLETED
- Separate player-initiated vs opponent-initiated truco calls
- Implement opponent random truco (15% before playing card)
- Support full escalation chain: Truco(3) → Seis(6) → Nove(9) → Doze(12)
- Fix state management (truco value resets correctly on new hands)
- All truco flows tested and working
- **Result**: Complete bidirectional truco negotiation with proper state reset

### ✅ Phase 5 — Match Flow & Results Screens
**Status**: COMPLETED
- Create `ui/scenes/results_scene.py` with hand & match results display
- Implement match win condition (first to 12 points)
- Auto-deal new hands when hand ends
- Track cumulative scores across hands
- Implement "Play Again" / "Back to Menu" transitions
- Ensure proper hand state reset (truco, cards, player_starts flags)
- **Deliverables**: 
  - Results screen showing hand winner and points awarded
  - Match completion detection and game over screen
  - Smooth hand-to-hand flow with automatic dealing
- **Result**: Complete matches playable start to finish

### Phase 6 — Visual Polish & Animations (Optional)
- Add card play animations
- Add hover/selection effects
- Add message overlays
- Optional: Sound effects and music
- **Result**: Smooth, polished gameplay feel

### Phase 7 — Menu & Settings (Optional)
- Create `ui/scenes/settings_scene.py` (difficulty, volume, themes)
- Create `ui/scenes/tutorial_scene.py` (rules, walkthrough)
- Wire menu buttons to new scenes
- **Result**: Settings and tutorial accessible

### Phase 9 — Testing & Cleanup
- Full smoke test (accounting for TextManager)
- Test AI opponent (INIT-RAM)
- Test edge cases and keyboard shortcuts
- Remove build artifacts
- Update README with setup instructions
- Final documentation review
- **Result**: Clean, working Pygame build ready for release

---

## Key Architectural Improvements

1. **Text Separation (Phase 1.5)**
   - All text in `ui/text/locales/` files
   - Easy to support multiple languages
   - Translators can work independently
   - Consistent terminology across UI

2. **Scene-Based Architecture**
   - Clean scene stack management
   - Independent scenes with clear interfaces
   - Easy to add new screens (settings, tutorial, etc.)

3. **Adapter Pattern**
   - Game logic completely separate from UI
   - Scenes request data via adapter snapshots
   - No game logic in rendering code

4. **TextManager Integration**
   - Scenes injected with TextManager
   - All text loaded from config-selected language
   - Runtime language switching possible

---

## File Structure After All Phases

```
truco-2000/
├── config.py                    # Pygame + language settings
├── game_controller.py           # UNCHANGED - core logic
├── game_core.py                 # UNCHANGED - game rules
├── main.py                      # Pygame launcher
├── truco_logic.py              # UNCHANGED - truco rules
├── utils.py                     # UNCHANGED - helpers
├── ai/                          # UNCHANGED - AI opponents
├── ui/
│   ├── pygame_app.py           # Main Pygame app
│   ├── adapter.py              # Game state bridge
│   ├── ui_controller.py        # Game controller
│   ├── display.py              # Layout helpers
│   ├── input.py                # Input utilities
│   ├── ascii_art.py            # ASCII rendering
│   ├── input_handler.py        # Pygame input system
│   ├── renderer.py             # Rendering pipeline
│   ├── text/                   # i18n system
│   │   ├── __init__.py         # TextManager
│   │   ├── locales/
│   │   │   ├── pt_br.py        # Portuguese (PRIMARY)
│   │   │   └── en_us.py        # English (template)
│   │   └── STRINGS_REFERENCE.md
│   ├── scenes/
│   │   ├── __init__.py
│   │   ├── base_scene.py       # Scene base class
│   │   ├── welcome_scene.py
│   │   ├── menu_scene.py
│   │   ├── game_scene.py
│   │   ├── results_scene.py
│   │   ├── settings_scene.py   # Optional
│   │   └── tutorial_scene.py   # Optional
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── button.py           # Button widget
│   │   ├── card_display.py     # Card rendering
│   │   ├── text_overlay.py     # Message overlays
│   │   └── hud.py              # HUD components
│   ├── assets/
│   │   ├── cards/              # Card data/images
│   │   ├── fonts/              # Font files
│   │   ├── images/             # UI images
│   │   └── sounds/             # Optional audio
│   └── utils.py                # Pygame helpers
├── textual_legacy/             # Archived Textual code
│   ├── README.md
│   ├── textual_app.py
│   ├── widgets/
│   ├── debug_main.py
│   ├── test.py
│   └── test2.py
├── .github/
│   ├── pygame_plan.md          # Complete refactor plan
│   └── copilot-instructions.md # Updated documentation
├── requirements-dev.txt        # Pygame dependency
├── README.md                   # Updated with setup
└── (other files)
```

---

## Quick Reference: Implementation Order

| Order | Phase | Focus | Deliverable |
|-------|-------|-------|-------------|
| 1 | 0 | Prep | Clean structure, deps updated |
| 2 | 1 | Window | Pygame app + scenes working |
| 3 | **1.5** | **i18n** | **TextManager + Portuguese** |
| 4 | 2 | Input | Buttons + navigation |
| 5 | 3 | Rendering | Game state display |
| 6 | 4 | Gameplay | Card play + truco |
| 7 | 5 | Flow | Full matches |
| 8 | 6 | Polish | Animations (optional) |
| 9 | 7 | Settings | Menus (optional) |
| 10 | 9 | Cleanup | Testing + finalization |

---

## Success Metrics

After each phase:
- ✅ Window opens correctly
- ✅ Scenes navigate as expected
- ✅ **All text from TextManager** (Phase 1.5+)
- ✅ Game state renders
- ✅ Input handled properly
- ✅ Full match playable
- ✅ Opponent AI works
- ✅ No hardcoded strings in code
- ✅ Portuguese fully functional
- ✅ Ready for English translation

---

**Last Updated**: January 27, 2026  
**Status**: Ready to proceed with Phase 1.5
**Primary Language**: Portuguese (pt_br)  
**Secondary Language**: English (en_us - template for future)
