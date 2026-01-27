# Textual Legacy Archive

This directory contains archived Textual UI code from the Truco 2000 project. These files are preserved for reference only during the migration from Textual to Pygame.

## Contents

- **textual_app.py** - Original Textual app implementation with screen management and modal logic
- **widgets/** - Textual-specific widget implementations:
  - `battle_zone_widget.py` - Battle zone rendering
  - `card_widget.py` - Individual card display
  - `game_banner.py` - Banner/overlay base class
  - `hand_widget.py` - Player hand rendering
  - `prompt_widget.py` - Truco/action prompts
  - `sidebar_widget.py` - Game info sidebar
  - `truco_response_widget.py` - Truco negotiation modal
  - `welcome_screen.py` - Welcome/sizing screen
  - `win_banner_widget.py` - Win/results banner
- **debug_main.py** - Debug version of game controller with manual opponent card selection
- **test.py** - Rich library layout demonstration
- **test2.py** - Textual app test entry point

## Why This Exists

During January 2026, the Truco 2000 project was refactored from Textual (CLI/TUI framework) to Pygame (graphical game framework) to gain more control over rendering, input, and animations.

## Usage

**Do not use this code in active development.** This archive serves as:

1. **Reference**: If you need to understand how certain features (like truco negotiation modals or widget hierarchy) were implemented in Textual, check these files.
2. **Migration guide**: When porting features to Pygame, compare the Textual implementation here with the new Pygame implementation in `ui/`.
3. **Historical record**: Preserves the UI implementation state before the refactor.

## Migration Notes

- **Game logic** (`game_core.py`, `game_controller.py`, `truco_logic.py`, `ai/`) was untouched during refactor.
- **Adapter layer** (`ui/adapter.py`) was kept and refactored, removing Textual dependencies while preserving state mapping.
- **New Pygame structure** is in:
  - `ui/pygame_app.py` - Main Pygame app
  - `ui/scenes/` - Scene management (replaces Textual screens)
  - `ui/input_handler.py` - Input handling (replaces Textual events)
  - `ui/renderer.py` - Rendering pipeline
  - `ui/widgets/` - Pygame widgets (new, not from Textual)

## Cleanup Plan

Once the Pygame refactor is confirmed stable and all features are ported:

1. This directory can be archived to a git tag or separate branch for historical reference.
2. Eventually, it can be deleted from the main codebase to reduce clutter.
3. For now, it serves as an incremental migration checkpoint.

---

*Archive created: January 27, 2026 | Refactor status: Phase 0*
