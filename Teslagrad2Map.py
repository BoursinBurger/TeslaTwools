from typing import List
from Teslagrad2Scene import Scene
from Teslagrad2Exit import Exit
from Teslagrad2Scroll import Scroll
from Teslagrad2Equipment import Equipment
from Teslagrad2Data import scenes


class Map:
    def __init__(self):
        """
        Define a graph of nodes.
        """
        self.scenes: List[Scene] = list()

    def add_scene(self, scene_obj: Scene):
        """
        Add a node to the graph.
        :param scene_obj: Scene object
        """
        self.scenes.append(scene_obj)

    @staticmethod
    def traverse_to_scene(source_scene, destination_scene, user_equipment):
        """
        Attempt to find a path from one scene to another using the given equipment.
        :param source_scene: Scene beginning the traversal.
        :param destination_scene: Scene ending the traversal.
        :param user_equipment: A bitwise combination of Equipment flags for items possessed.
               Example: Equipment.BLINK | Equipment.CLOAK means Lumina has Blink and Cloak.
        :return: A list of linked scenes from source to destination.
        """
        path_list = [[source_scene]]
        path_index = 0
        # To keep track of previously visited nodes
        previous_nodes = {source_scene}
        if source_scene == destination_scene:
            return path_list[0]

        while path_index < len(path_list):
            current_path = path_list[path_index]
            last_node = current_path[-1]
            # Eligible next-nodes are those that satisfy the equipment requirements of their respective exits.
            next_nodes = [e.scene for e in last_node.exits if e.is_usable(user_equipment)]
            # Search goal node
            if destination_scene in next_nodes:
                current_path.append(destination_scene)
                return current_path
            # Add new paths
            for next_node in next_nodes:
                if next_node not in previous_nodes:
                    new_path = current_path[:]
                    new_path.append(next_node)
                    path_list.append(new_path)
                    # To avoid backtracking
                    previous_nodes.add(next_node)
            # Continue to next path in list
            path_index += 1
        # No path is found
        return []

    def traverse_to_scroll(self, source_scene, scroll_index, user_equipment):
        """
        Attempt to find a path from a given scene to a given scroll using the given equipment.
        :param source_scene: Scene beginning the traversal.
        :param scroll_index: Scroll number to be reached.
        :param user_equipment: A bitwise combination of Equipment flags for items possessed.
               Example: Equipment.BLINK | Equipment.CLOAK means Lumina has Blink and Cloak.
        :return: A list of linked scenes from source to destination.
        """

        # First, find the scene containing the scroll index.
        destination_scene = None
        destination_scroll = None
        for scene in self.scenes:
            for scroll in scene.scrolls:
                if scroll_index == scroll.number:
                    destination_scene = scene
                    destination_scroll = scroll
                    break
        # Return empty list if scroll not found.
        if destination_scene is None:
            return []
        # Return empty list if scroll not collectible.
        if not destination_scroll.is_collectible(user_equipment):
            return []
        # Otherwise, traverse the map to reach the destination scene
        scene_path = self.traverse_to_scene(source_scene, destination_scene, user_equipment)
        if len(scene_path) == 0:
            return scene_path
        else:
            scene_path.append(destination_scroll)
            return scene_path


teslagrad2map = Map()

lumina_landed = Scene(name="Lumina Landed", respawn_point=scenes.get("Lumina Landed"))
viking_hilltop = Scene(name="Viking Hilltop", respawn_point=scenes.get("Viking Hilltop"))

lumina_landed.add_exit(Exit(scene=viking_hilltop, exit_requirements=None))
viking_hilltop.add_exit(Exit(scene=lumina_landed, exit_requirements=None))

teslagrad2map.add_scene(lumina_landed)
teslagrad2map.add_scene(viking_hilltop)

my_equipment = Equipment.BLINK | Equipment.CLOAK

path = teslagrad2map.traverse_to_scene(lumina_landed, viking_hilltop, my_equipment)
print(', '.join([(obj.name if type(obj) is Scene else obj.number) for obj in path]))
