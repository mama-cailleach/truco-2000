# Truco 2000

## Introduction


**Truco 2000** is a feature-rich, modular command-line implementation of the popular Brazilian card game "Truco" developed by mama. The codebase has been fully refactored for maintainability, extensibility, and future enhancements, with a clean separation of concerns across multiple modules. The game features advanced Python programming, object-oriented design, and an immersive ASCII-based user interface with a retro Y2K aesthetic. Currently available in Brazilian Portuguese.

---

### What is Truco?

Truco is a popular card game in Brazil and parts of Latin America. It's a trick-taking game with unique rules:

- Players compete to win rounds ("rodadas") using a reduced deck of 40 cards
- Features a special "manilha" (trump) card system that changes each hand
- Includes strategic elements like bluffing and calling "truco" to raise the stakes
- Players can call truco at strategic moments to increase point values
- The first player to reach 12 points wins the game

---


---

## 🏗️ Project Architecture & Refactor Overview

### Modular Structure (2025 Refactor)

The codebase is now organized into the following modules:

- **`main.py`**: Entry point. Initializes and launches the game.
- **`game_controller.py`**: Orchestrates the main game loop, hand/round flow, and coordinates all modules.
- **`game_core.py`**: Pure game logic (deck, rules, scoring, round/hand winner logic). No UI dependencies.
- **`truco_logic.py`**: Handles truco escalation, negotiation, and AI responses. All truco-specific state and logic lives here.
- **`ui/`**: UI system split into:
	- `ui/display.py`: Layout, battle zone, and all output rendering.
	- `ui/input.py`: All user input, validation, and global quit handling.
	- `ui/ascii_art.py`: Card and banner ASCII art generation.
- **`config.py`**: Centralized settings (screen width, truco names, etc).
- **`utils.py`**: Shared helpers (safe_exit, formatting, etc).

#### Key Design Principles
- **Separation of Concerns**: Game logic, UI, and controller are strictly separated.
- **Extensibility**: Easy to add new features (AI, tutorial, sound, etc) without breaking core logic.
- **Testability**: Pure logic modules can be tested independently of UI.
- **Future-Proofing**: Structure supports future GUI/web, AI, and tutorial systems.

#### Major Changes in the Refactor
- All core logic, truco negotiation, and UI code split into dedicated modules.
- Controller orchestrates game flow, hands, and rounds.
- UI rendering and input are fully decoupled from game logic.
- Truco escalation and AI logic isolated for easy extension.
- Card/label centering and battle zone layout improved for clarity.
- Global quit command and robust input validation.
- Legacy monolithic script archived; new entry point is `main.py`.

---

## ✨ Features

### **Core Gameplay**
- ✅ Complete implementation of authentic Brazilian Truco rules
- ✅ Strategic truco calling system (1 → 3 → 6 → 9 → 12 points)
- ✅ Player vs intelligent computer opponent
- ✅ Proper turn-based mechanics respecting traditional Truco rules
- ✅ Authentic "manilha" (trump card) system with card hierarchy

### **Advanced Visual Experience**
- 🎨 Beautiful ASCII art card representations
- 🖥️ Clean screen-clearing interface for organized gameplay
- ⚔️ **Battle Zone**: Dedicated area always visible, showing played cards side-by-side or placeholders
- 📊 Real-time game status with scores and hand values
- 🎯 Progressive card revelation with dramatic timing
- 📱 Organized two-column layout optimized for wide terminals
- 🧩 Sidebar always shows score, round info, vira, and manilha

### **Strategic Gameplay Elements**
- 🧠 **Power Move Truco**: Call truco after seeing opponent's card
- 🏃 **Strategic Running**: Escape from unfavorable truco situations
- 🎲 **Intelligent AI**: Opponent makes strategic decisions about truco calls
- 🔄 **Complete Truco Sequence**: Support for all escalation levels
- ⚖️ **Correct Point Calculation**: Proper scoring when players run from truco
- 🛑 **Global Quit Command**: Type 'quit' at any prompt to exit instantly

### **Enhanced User Experience**
- ✅ Robust input validation with clear error messages
- ⏱️ Smooth game flow with strategic pauses for dramatic effect
- 🎮 Intuitive controls with numbered card selection
- 📋 Clear game state display showing round results and standings
- 🎯 Visual feedback for all game actions
- 🖥️ Consistent, non-shifting layout: battle zone and hand always aligned

---


---

## 🗂️ File & Module Overview

| Module/File            | Responsibility                                                      |
|------------------------|---------------------------------------------------------------------|
| `main.py`              | Entry point, initializes game controller                            |
| `game_controller.py`   | Main game loop, hand/round management, module coordination          |
| `game_core.py`         | Deck, rules, scoring, round/hand winner logic (no UI dependencies)  |
| `truco_logic.py`       | Truco escalation, negotiation, AI responses                         |
| `ui/display.py`        | Output rendering, layout, battle zone, banners                      |
| `ui/input.py`          | User input, validation, global quit                                 |
| `ui/ascii_art.py`      | Card and banner ASCII art generation                                |
| `config.py`            | Centralized settings (screen width, truco names, etc)               |
| `utils.py`             | Shared helpers (safe_exit, formatting, etc)                         |

---

## 🎮 How to Play

### **Starting the Game**
1. Run the game: `python main.py`
2. Follow the ASCII art intro and choose to play
3. The game displays your cards side-by-side with clear numbering

### **During Each Round**
- **Select cards**: Enter the number (1, 2, or 3) of the card you want to play
- **Call Truco**: Enter 'T' to raise the stakes (available when strategic)
- **Strategic Truco**: You can call truco after seeing your opponent's card!
- **Escape**: Enter 'F' to run away from unfavorable situations
- **Quit**: Enter 'quit' at any prompt to exit the game immediately
- **Watch the Battle Zone**: See both cards displayed clearly with results

### **Truco Escalation System**
- **Normal Hand**: 1 point
- **Truco**: 3 points (first escalation)
- **Retruco**: 6 points (counter-raise)
- **Vale 9**: 9 points (further escalation)
- **Vale 12**: 12 points (maximum stakes)

### **Winning Strategy**
- Win 2 out of 3 rounds to win the hand
- Use truco strategically to maximize points
- Call truco after seeing opponent's card for maximum advantage
- Know when to run to minimize losses

---

## 🃏 Card Ranking & Rules

### **Standard Card Hierarchy** (lowest to highest)
**4, 5, 6, 7, Q, J, K, A, 2, 3**

### **Manilha System**
- The "vira" card is revealed at the start of each hand
- The next card in sequence becomes the manilha (trump)
- Manilhas beat all other cards
- When both players have manilhas, suit order determines winner: ♣ > ♥ > ♠ > ♦

### **Hand Resolution**
- Best 2 out of 3 rounds wins the hand
- Winner of each round starts the next round
- Strategic timing of truco calls can dramatically change point values

---


## 🛠️ Technical Excellence & Refactor Benefits

### **Modern Modular Architecture**
- Strict separation of game logic, UI, and controller for maintainability
- Each module has a single responsibility and clear interface
- Easy to extend: add new UI, AI, tutorial, or sound modules without breaking core logic

### **Advanced Game Logic**
- All rules, deck, and scoring logic isolated in `game_core.py`
- Truco negotiation and escalation handled in `truco_logic.py`
- Controller manages game state and flow, not UI or rules

### **User Interface Innovation**
- All output rendering and input handling in `ui/` submodules
- Battle zone and card display always aligned and centered
- ASCII art and banners generated in dedicated module
- Global quit command and robust input validation

### **Code Quality**
- Fully decoupled modules for easier testing and future upgrades
- Legacy monolithic script archived for reference
- Clean, readable, and maintainable code structure

### **Extensibility**
- Ready for new features: AI difficulties, tutorial, sound, GUI/web UI, and more


---

## 🎨 Visual Design

### **Retro Y2K Aesthetic**
- ASCII art banner with "TRUCO 2000" branding
- Organized sections with visual separators
- Clean typography and spacing
- Terminal-optimized layout for various screen sizes

### **Battle Zone Innovation**
- Dedicated area for displaying played cards
- Side-by-side view of user and opponent cards
- Clear indication of round winner in the battle zone
- Battle zone always visible, even when no cards are played

---


## 🚀 Major Changes in the 2025 Refactor

- 🗂️ **Full modularization**: All logic, UI, and controller code split into dedicated modules
- 🧠 **Pure logic modules**: Game rules and truco negotiation are UI-independent
- 🖥️ **UI system overhaul**: All display and input code in `ui/` submodules
- ⚔️ **Battle zone and card alignment**: Always centered and visually clear
- 🏃 **Global quit command**: Type 'quit' at any prompt to exit instantly
- 🐞 **Bug fixes**: Round starter logic, UI card alignment, handler argument errors all addressed
- 🧹 **Legacy script archived**: `truco_2000_v1.0.py` is now for reference only; use `main.py` to play


---

## 🎯 Planned Improvements

### **Phase 4: Enhanced Polish**
- 🔜 Fine-tuned retro Windows 98/2000 aesthetic
- 🔜 Color support where available
- 🔜 Enhanced spacing and visual hierarchy
- 🔜 Sound effects simulation with ASCII

### **Gameplay Enhancements**
- 🔜 Multiple AI difficulty levels with different strategies
- 🔜 Statistics tracking across games
- 🔜 Tournament mode
- 🔜 Replay system

### **Educational Features**
- 🔜 Interactive tutorial for new players
- 🔜 Rule explanations and strategy tips
- 🔜 Practice mode against different AI personalities

### **Platform Expansion**
- 🔜 Executable (.exe) compilation for easy distribution
- 🔜 English translation
- 🔜 Cross-platform compatibility improvements

---

## 👨‍💻 About the Developer

This game showcases mama-cailleach's expertise in:

- **Advanced Python Programming**: Complex game logic and state management
- **User Experience Design**: Intuitive interfaces and visual feedback
- **Game Development**: Authentic rule implementation and strategic AI
- **Software Architecture**: Clean, maintainable, and extensible code
- **Cultural Gaming**: Authentic Brazilian card game experience

---

## 🎲 Getting Started

1. **Requirements**: Python 3.x
2. **Installation**: Download `truco_2000_v1.0.py`
3. **Run**: `python main.py`
4. **Enjoy**: Experience authentic Brazilian Truco with modern enhancements!

---

**Note:** This project was created as a programming showcase and for entertainment purposes. Truco 2000 celebrates Brazilian gaming culture while demonstrating advanced software development techniques.

**Boa sorte e que vença o melhor!** 🃏✨