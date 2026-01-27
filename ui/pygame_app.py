"""
Main Pygame Application for Truco 2000

This module contains the core Pygame app class that manages:
- Window creation and rendering
- Game loop (event handling, update, render)
- Scene management (scene stack)
- FPS control and timing
"""

import pygame
import sys
from typing import List, Optional
from config import GameConfig
from ui.text import TextManager
from ui.input_handler import InputHandler


class PygameApp:
    """
    Main Pygame application class.
    
    Manages the game window, event loop, and scene stack.
    """
    
    def __init__(self):
        """Initialize Pygame and create the main app."""
        pygame.init()
        
        self.width = GameConfig.WINDOW_WIDTH
        self.height = GameConfig.WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(GameConfig.WINDOW_TITLE)
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.scene_stack: List = []  # Stack of scenes
        self.controller = None  # Will be set by caller
        # Text manager for localization
        self.text_manager = TextManager(GameConfig.DEFAULT_LANGUAGE)
        # Input handler
        self.input_handler = InputHandler(self)
        # Register global shortcuts
        self.input_handler.register_global_key(pygame.K_q, self._quit)
        self.input_handler.register_global_key(pygame.K_ESCAPE, self._go_back)
        
    def push_scene(self, scene) -> None:
        """Push a new scene onto the stack."""
        if self.scene_stack:
            self.scene_stack[-1].on_exit()
        self.scene_stack.append(scene)
        scene.on_enter()
        
    def pop_scene(self) -> None:
        """Pop the current scene from the stack."""
        if self.scene_stack:
            current_scene = self.scene_stack.pop()
            current_scene.on_exit()
            if self.scene_stack:
                self.scene_stack[-1].on_enter()
        else:
            self.running = False
            
    def replace_scene(self, scene) -> None:
        """Replace the current scene with a new one."""
        if self.scene_stack:
            current_scene = self.scene_stack.pop()
            current_scene.on_exit()
        self.scene_stack.append(scene)
        scene.on_enter()
        
    def get_current_scene(self):
        """Get the currently active scene."""
        return self.scene_stack[-1] if self.scene_stack else None
    
    def handle_events(self) -> None:
        """Handle Pygame events."""
        for event in pygame.event.get():
            self.input_handler.process_event(event)

    def _quit(self) -> None:
        """Quit the application."""
        self.running = False

    def _go_back(self) -> None:
        """Global ESC: go back to previous scene or menu."""
        if len(self.scene_stack) > 1:
            self.pop_scene()
        else:
            # If only one scene, try to go to menu
            from ui.scenes.menu_scene import MenuScene
            self.replace_scene(MenuScene(self))
    
    def update(self, delta_time: float) -> None:
        """Update game state."""
        current_scene = self.get_current_scene()
        if current_scene:
            current_scene.update(delta_time)
    
    def render(self) -> None:
        """Render the current frame."""
        # Clear screen
        self.screen.fill(GameConfig.COLOR_BACKGROUND)
        
        # Render current scene
        current_scene = self.get_current_scene()
        if current_scene:
            current_scene.render(self.screen)
        
        # Update display
        pygame.display.flip()
    
    def run(self) -> None:
        """Main game loop."""
        try:
            while self.running and self.scene_stack:
                delta_time = self.clock.tick(GameConfig.FPS) / 1000.0
                
                self.handle_events()
                self.update(delta_time)
                self.render()
        finally:
            self.cleanup()
    
    def cleanup(self) -> None:
        """Clean up and quit Pygame."""
        pygame.quit()
        sys.exit()


def main():
    """Entry point for the Pygame app."""
    from ui.scenes.welcome_scene import WelcomeScene
    from game_controller import GameController
    
    app = PygameApp()
    app.controller = GameController()
    
    # Start with welcome scene
    app.push_scene(WelcomeScene(app))
    
    # Run the game loop
    app.run()


if __name__ == "__main__":
    main()
