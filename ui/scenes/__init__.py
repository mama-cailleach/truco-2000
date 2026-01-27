"""
Scene management module for Pygame Truco 2000.

All scenes inherit from BaseScene and are registered here.
"""

from ui.scenes.base_scene import BaseScene
from ui.scenes.welcome_scene import WelcomeScene
from ui.scenes.menu_scene import MenuScene
from ui.scenes.game_scene import GameScene

__all__ = [
    "BaseScene",
    "WelcomeScene",
    "MenuScene",
    "GameScene",
]
