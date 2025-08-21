# Truco 2000 - AI Coding Instructions

## Project Overview
Truco 2000 is a Brazilian card game implementation in Python with a retro Y2K aesthetic. The project prioritizes clean game logic over complex UI dependencies, following a "CLI-first, enhance later" approach.

## Architecture & Design Patterns

### Core Game State Management
- **Single class design**: `TrucoGame` handles all game logic, UI, and state
- **Stateful gameplay**: Multi-level state tracking across games → hands → rounds → truco sequences
- **Turn-based flow**: Uses `player_starts_hand` and `player_starts_round` flags to manage initiative
- **Critical state variables**:
  - `current_hand_value`: Truco escalation (1→3→6→9→12)
  - `last_raiser`: Prevents same player from re-raising truco
  - `primeira_vitoria`: Implements "caminhão" rule for hand resolution

### Game Logic Hierarchy
```
Game (to 12 points) 
  └── Hand (best 2/3 rounds, worth current_hand_value points)
      └── Round (single card play + battle resolution)
          └── Truco Sequence (escalating stakes negotiation)
```

### Complex Rules Implementation
- **Manilha system**: Dynamic trump cards based on `vira` card using circular rank progression
- **Hand resolution**: Complex victory conditions in `check_hand_winner()` - handles 2/3 wins, draws, and "primeira_vitoria" tiebreaker
- **Truco escalation**: `handle_truco_sequence()` manages bidirectional raise/accept/run sequences with proper point calculation
- **Power move timing**: Players can call truco after seeing opponent's card (strategic advantage)

## UI Architecture & Patterns

### Retro CLI Aesthetic
- **Screen management**: `clear_screen()` + structured layout sections
- **ASCII card system**: `generate_card_ascii()` creates Unicode-bordered cards, `cards_database` stores all 40 cards
- **Battle Zone**: Progressive card revelation with `display_battle_zone()` - central visual focus
- **Side-by-side display**: `display_cards_side_by_side()` handles multi-card horizontal layouts

### Layout Structure (70-char width)
```
[Header with score and truco value]
[Round info and status]
[Opponent area (hidden cards)]
[BATTLE ZONE - played cards side-by-side]
[Vira card + Manilha info]
[Player's remaining cards with numbers]
```

### Input Validation Pattern
- `get_valid_input()`: Universal input handler with option validation
- Context-aware choices: Truco/run availability based on `current_hand_value` and `last_raiser`
- Special inputs: 'T' (truco), 'F' (fugir/run), numbers for card selection

## Development Workflow

### Testing & Running
```bash
python truco_2000_v1.0.py  # Main game
# Safe copy exists: truco_2000_v1.0_safe_copy_DONOTTOUCH.py
```

### File Structure
- `truco_2000_v1.0.py`: Main game file (working version)
- `truco_2000_v1.0_safe_copy_DONOTTOUCH.py`: Backup reference
- `future_plans.txt`: Architecture roadmap and enhancement plans
- `README.md`: Comprehensive feature documentation

## Key Development Principles

### State Management
- Return tuples from `jogar_rodada()`: `(winner, hands, game_state, special_results)`
- Immediate hand termination on truco runs: Check `special_result` before processing round results
- Proper turn management: Update `player_starts_round` based on round winners

### UI Enhancement Strategy
1. **Current**: Pure `print()` + ASCII art (no dependencies)
2. **Planned**: `rich` library for colors/tables (maintains print compatibility)
3. **Future**: `curses` for full-screen terminal UI
4. **Architecture**: Game logic separated from display for easy UI migration

### Brazilian Truco Authenticity
- **Card hierarchy**: 4,5,6,7,Q,J,K,A,2,3 (ascending)
- **Manilha precedence**: ♣ > ♥ > ♠ > ♦ (when both cards are manilhas)
- **Truco names**: Normal(1) → Truco(3) → Retruco(6) → Vale 9 → Vale 12
- **Escape mechanics**: Players can "fugir" (run) from unfavorable truco situations

### Code Quality Patterns
- Descriptive method names in Portuguese for game concepts (`jogar_mao`, `vencedor_rodada`)
- Comprehensive docstrings with parameter descriptions
- State validation before major operations (check `can_truco` conditions)
- Time delays (`time.sleep()`) for dramatic effect and user comprehension

## Common Pitfalls
- Don't modify `player_starts_hand` mid-hand (only between hands)
- Always check for truco `special_result` before processing normal round outcomes
- Maintain 70-character line width for consistent CLI layout
- Remember manilha comparison requires both suit hierarchy AND rank matching
