from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button

# 1. Define the main App class
class CardGameApp(App[None]):
    
    # 2. Define the 'compose' method to lay out the UI
    def compose(self) -> ComposeResult:
        yield Header()  # Top bar with title
        yield Footer()  # Bottom bar with keys
        
        # Example: A Button for the player action
        yield Button("Hit Me!", id="hit_button", variant="primary")
        yield Button("Stand", id="stand_button", variant="error")

# 3. Run the App
if __name__ == "__main__":
    app = CardGameApp()
    app.run()