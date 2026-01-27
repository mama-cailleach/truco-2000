from textual.widgets import Static
from textual.containers import Vertical
from textual.app import ComposeResult


class WelcomeSizingWidget(Static):
    """Widget displaying a fixed-size box to help users verify terminal dimensions."""
    
    def __init__(self, **kwargs):
        # Recommended dimensions for the game (width x height in cells)
        self.recommended_width = 102
        self.recommended_height = 44
        super().__init__(**kwargs)
    
    def compose(self) -> ComposeResult:
        # Create the border box and message
        instructions = (
            "Para uma melhor visualização, certifique-se de que você pode ver\n"
            "todos os cantos deste quadrado verde.\n\n"
            f"Tamanho recomendado: {self.recommended_width} × {self.recommended_height}\n\n"
            "Pressione ENTER para começar..."
        )
        
        # Build the visual box
        border_top = "┌" + "─" * (self.recommended_width - 2) + "┐"
        border_bottom = "└" + "─" * (self.recommended_width - 2) + "┘"
        
        # Calculate middle position for message
        message_lines = instructions.split('\n')
        vertical_padding = (self.recommended_height - len(message_lines) - 2) // 2
        
        # Build the complete visual
        lines = [border_top]
        
        # Add padding before message
        for _ in range(vertical_padding):
            lines.append("│" + " " * (self.recommended_width - 2) + "│")
        
        # Add message lines (centered)
        for line in message_lines:
            padding = (self.recommended_width - 2 - len(line)) // 2
            content = " " * padding + line + " " * (self.recommended_width - 2 - padding - len(line))
            lines.append("│" + content + "│")
        
        # Add padding after message
        remaining = self.recommended_height - len(lines) - 1
        for _ in range(remaining):
            lines.append("│" + " " * (self.recommended_width - 2) + "│")
        
        lines.append(border_bottom)
        
        yield Static("\n".join(lines), id="sizing_box")
