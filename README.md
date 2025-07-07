# Truco 2000

## Introduction

**Truco 2000** is a command-line implementation of the popular Brazilian card game "Truco" developed by mama. This game showcases Python programming skills with a focus on object-oriented design, game logic implementation, and command-line user interface development. At moment only available in Brazilian Portuguese.

---

### What is Truco?

Truco is a popular card game in Brazil and parts of Latin America. It's a trick-taking game with unique rules:

- Players compete to win rounds ("tricks") using a reduced deck of 40 cards
- Features a special "manilha" (trump) card system that changes each hand
- Includes strategic elements like bluffing and calling "truco" to raise the stakes
- The first player to reach 12 points wins the game

---

## Features

- Complete implementation of Truco card game rules
- Text-based card visualization with ASCII art
- Strategic gameplay with truco calling and accepting/running mechanics
- Player vs computer opponent gameplay
- Turn-based mechanics that respect traditional Truco rules where winner starts next round
- Visual representation of the "vira" card and manilhas (trump cards)
- Clean object-oriented programming structure
- Robust input validation

---

## Code Structure

This project demonstrates several programming concepts:

- **Object-Oriented Design:** Utilizes classes to encapsulate game state and behavior
- **ASCII Art Generation:** Creates visually appealing card representations in the terminal
- **Input Validation:** Handles and validates user input with clear feedback
- **Game Logic:** Implements complex card game rules and state management
- **Randomization:** Uses Python's random library for card shuffling and CPU decisions

---

## How to Play

1. Run the script using Python:  
   `python truco_2000_v1.0.py`
2. Follow the on-screen prompts to play the game
3. On your turn, select a card to play by entering its number
4. Call "truco" by entering 'T' when available to raise the stakes from 1 to 3 points
5. Run away from a truco call by entering 'F' if you don't like your chances
6. The first player to reach 12 points wins

---

## Card Ranking

Cards are ranked as follows (lowest to highest):

**4, 5, 6, 7, Q, J, K, A, 2, 3**

Manilhas (trump cards) are the highest-ranked cards, determined by the "vira" card drawn at the beginning of each hand. The manilha is the card of the next rank after the "vira" card.

---

## Planned Improvements

This is an active project with several planned enhancements:

### 1. UI Improvements

- Clear screen functionality between rounds to reduce visual clutter
- Better visual presentation of game state and results
- Improved layout and use of color when possible

### 2. Game Rules Tutorial

- Add an in-game tutorial explaining Truco rules
- Help section for new players
- Optional rule variations

### 3. AI Opponent Enhancement

- Develop strategic AI opponents with different playstyles
- Multiple difficulty levels
- AI that can call truco strategically

### 4. Extended Truco Logic

- Implement the full betting sequence of 6, 9, and 12 points
- Support for "Seis" (6 points), "Nove" (9 points), and "Doze" (12 points) calls
- Ability for AI to initiate truco calls

### 5. Translation

- Translation to English

---

## About the Developer

This game is part of mama-cailleach's Python portfolio, showcasing skills in:

- Python programming
- Game development
- Object-oriented design
- User interface creation
- Complex logic implementation

---

**Note:** This project was created as a programming exercise and for entertainment purposes. Truco 2000 is not affiliated with any commercial card game products.
