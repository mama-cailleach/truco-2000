"""
Base Scene class for all Pygame scenes.

All scenes inherit from this class and implement:
- on_enter(): Called when scene becomes active
- on_exit(): Called when scene is deactivated
- handle_event(event): Handle Pygame events
- update(delta_time): Update scene state
- render(surface): Draw scene to surface
"""

from abc import ABC, abstractmethod
import pygame


class BaseScene(ABC):
    """
    Abstract base class for all game scenes.
    
    Defines the interface that all scenes must implement.
    """
    
    def __init__(self, app):
        """
        Initialize the scene.
        
        Args:
            app: The PygameApp instance
        """
        self.app = app
        
    @abstractmethod
    def on_enter(self) -> None:
        """
        Called when this scene becomes the active scene.
        
        Use this to initialize scene-specific resources.
        """
        pass
    
    @abstractmethod
    def on_exit(self) -> None:
        """
        Called when this scene is no longer active.
        
        Use this to clean up resources.
        """
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle a Pygame event.
        
        Args:
            event: A pygame event
        """
        pass
    
    @abstractmethod
    def update(self, delta_time: float) -> None:
        """
        Update scene state.
        
        Args:
            delta_time: Time elapsed since last frame (seconds)
        """
        pass
    
    @abstractmethod
    def render(self, surface: pygame.Surface) -> None:
        """
        Render the scene to the given surface.
        
        Args:
            surface: The pygame surface to draw to
        """
        pass
