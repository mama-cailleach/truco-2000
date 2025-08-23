# Truco 2000: How the Code Works (Beginner-Friendly Guide)

Welcome! This guide explains how the Truco 2000 game code is organized and how it works, using simple language. If you are learning Python and want to understand a real project, this is for you!

---

## What is Truco 2000?
Truco 2000 is a command-line game that lets you play the Brazilian card game "Truco" against the computer. The game uses text and ASCII art to show cards and the game board in your terminal.

---

## How is the Code Organized?
The code is split into different files (called "modules"). Each file has a special job. This makes the code easier to read, fix, and add new features to.

### Main Parts:
- **main.py**: This is where the game starts. It sets everything up and launches the game.
- **game_controller.py**: This is the "conductor". It controls the flow of the game: who plays, when rounds start, and when the game ends.
- **game_core.py**: This file has the main game rules, like how to shuffle cards, who wins a round, and how points are counted. It does NOT handle any user input or output.
- **truco_logic.py**: This file handles the special "truco" part of the game, where players can raise the stakes. It also has the computer's (AI) decisions for truco.
- **ui/display.py**: This file is in charge of showing things on the screen, like cards, scores, and banners.
- **ui/input.py**: This file asks the player for input (like which card to play) and checks if the input is valid.
- **ui/ascii_art.py**: This file creates the fancy ASCII art for cards and banners.
- **config.py**: This file stores settings, like screen width and card names.
- **utils.py**: This file has small helper functions used in different places.

---

## How Does the Game Work?

1. **Start the Game**
   - You run `python main.py` in your terminal.
   - The game shows an intro and sets up everything.

2. **Game Flow**
   - The `game_controller.py` file runs the main loop:
     - Deals cards to you and the computer.
     - Shows your hand and the "battle zone" (where played cards go).
     - Asks you to pick a card or call "truco" (raise the stakes).
     - Handles the computer's moves and truco decisions.
     - Decides who wins each round and hand.
     - Updates the score and shows results.
     - Repeats until someone wins the game.

3. **User Interface**
   - All messages, cards, and banners are shown using `ui/display.py` and `ui/ascii_art.py`.
   - All input (your choices) are handled by `ui/input.py`.
   - You can type `quit` at any time to exit the game.

4. **Game Logic**
   - The rules for who wins a round, how cards are ranked, and how truco works are in `game_core.py` and `truco_logic.py`.
   - The computer opponent uses simple AI to decide when to call or accept truco.

---

## Why is the Code Split Like This?
- **Easier to Understand**: Each file does one job. You don't have to read everything at once.
- **Easier to Fix**: If there's a bug in how cards are shown, you only look in the UI files.
- **Easier to Add Features**: Want to add sound or a tutorial? You can do it without breaking the game rules.

---

## Most Important Features (Explained Simply)

- **Battle Zone**: The place on the screen where you see your card and the computer's card side by side. This helps you see who is winning each round.
- **Truco System**: You can "call truco" to raise the points for a hand. The computer can accept, raise back, or run away. This makes the game more exciting!
- **Manilha (Trump Card)**: Each hand, a special card is chosen as the "manilha" (trump). Manilhas beat all other cards. The code figures this out automatically.
- **Global Quit**: You can type `quit` at any prompt to exit the game safely.
- **Input Validation**: The game checks your input and asks again if you type something wrong, so you don't get stuck.
- **ASCII Art**: Cards and banners are drawn with text, making the game look cool in your terminal.

---

## Tips for Reading the Code
- Start with `main.py` to see how the game starts.
- Look at `game_controller.py` to understand the game flow.
- Check `ui/display.py` and `ui/input.py` to see how the game talks to you.
- Explore `game_core.py` and `truco_logic.py` for the rules and special moves.

---

## Summary
- The code is organized so each part has a clear job.
- The game is easy to play, and the code is ready for new features.
- If you are learning Python, this is a great example of how to build a real project!

Happy coding and boa sorte! 🃏
