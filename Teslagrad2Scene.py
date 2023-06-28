from typing import List, Dict
from Teslagrad2Exit import Exit
from Teslagrad2Scroll import Scroll


class Scene:
    def __init__(self, name: str, respawn_point: Dict[str, float]):
        """
        Define a node / vertex within the graph
        :param name: The name of the scene
        :param respawn_point: The respawnPoint of the scene following the format: {"x": 0.12345, "y", 0.12345}
        """
        self.name: str = name
        self.respawn_point: Dict[str, float] = respawn_point
        self.exits: List[Exit] = list()
        self.scrolls: List[Scroll] = list()

    def add_exit(self, exit_obj: Exit):
        """
        Add an Exit to the Scene
        :param exit_obj: Exit object
        """
        self.exits.append(exit_obj)

    def add_scroll(self, scroll_obj: Scroll):
        """
        Add a Scroll to the Scene
        :param scroll_obj: Scroll object
        """
        self.scrolls.append(scroll_obj)
