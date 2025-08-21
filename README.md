# Truco 2000

## Introduction

**Truco 2000** is a feature-rich command-line implementation of the popular Brazilian card game "Truco" developed by mama. This game showcases advanced Python programming skills with object-oriented design, sophisticated game logic, and an immersive ASCII-based user interface with a retro Y2K aesthetic. Currently available in Brazilian Portuguese.

---

### What is Truco?

Truco is a popular card game in Brazil and parts of Latin America. It's a trick-taking game with unique rules:

- Players compete to win rounds ("rodadas") using a reduced deck of 40 cards
- Features a special "manilha" (trump) card system that changes each hand
- Includes strategic elements like bluffing and calling "truco" to raise the stakes
- Players can call truco at strategic moments to increase point values
- The first player to reach 12 points wins the game

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

## 🎮 How to Play

### **Starting the Game**
1. Run the script: `python truco_2000_v1.0.py`
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

## 🏗️ Technical Excellence

This project demonstrates advanced programming concepts:

### **Object-Oriented Design**
- Clean class structure with separated concerns
- Encapsulated game state and behavior
- Modular methods for different game phases

### **Advanced Game Logic**
- Complex truco sequence handling
- Proper state management across rounds and hands
- Accurate implementation of Brazilian Truco rules

### **User Interface Innovation**
- Dynamic ASCII art generation
- Screen clearing and layout management
- Progressive visual reveals with timing
- Battle zone system for card display
- Two-column layout with persistent sidebar
- Consistent battle zone height (no shifting cards)

### **Code Quality**
- Comprehensive input validation
- Error handling and edge case management
- Clean, readable, and maintainable code structure
- Deprecated/removed unused display functions for clarity

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

## 🚀 Recent Improvements (August 2025)

### **Major UI and Logic Enhancements**
- 🖥️ **Two-column layout**: Sidebar with score, round info, vira, and manilha; main area for cards and battle zone
- 🃏 **Battle zone always open**: Never shifts, always shows header and placeholder if empty
- 🏷️ **Dynamic label and card spacing**: Card labels and cards always aligned, with adjustable spacing
- 🛑 **Global quit command**: Type 'quit' at any prompt to exit instantly
- 🧹 **Removed unused display functions**: Cleaned up legacy code for maintainability
- 🐞 **Bug fixes**: No more shifting cards or missing card lines when round result is shown
- ⏱️ **Strategic pauses**: Ensured all important messages (like truco acceptance) are visible before screen clears

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
3. **Run**: `python truco_2000_v1.0.py`
4. **Enjoy**: Experience authentic Brazilian Truco with modern enhancements!

---

**Note:** This project was created as a programming showcase and for entertainment purposes. Truco 2000 celebrates Brazilian gaming culture while demonstrating advanced software development techniques.

**Boa sorte e que vença o melhor!** 🃏✨