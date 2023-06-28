from Teslagrad2Equipment import Equipment


class Exit:
    def __init__(self, scene, exit_requirements):
        """
        Define an edge to a graph node.
        :param scene: The scene this exit connects to.
               A pair of bidirectional scenes must each have an exit that points to the other.
        :param exit_requirements: Equipment required to use this exit. Valid values are:
               * None, for no requirements.
               * A bitwise combination of Equipment flags for all equipment required.
                 Example: Equipment.BLINK | Equipment.SLIDE, for something requiring blink AND slide.
               * A collection of optional scenarios, with each scenario being a bitwise combination described above.
                 Example: (Equipment.DIRECTIONAL_BLINK, Equipment.DOUBLE_JUMP, Equipment.CLOAK | Equipment.AXE),
                 for a scenario where you could use Omni-blink OR Double-jump OR the Axe + Cloak.
        """
        self.scene = scene
        self.requirements = exit_requirements

    def is_usable(self, user_equipment) -> bool:
        """
        Compare a user's equipment against the object's requirements.
        :param user_equipment: A bitwise combination of Equipment flags for items possessed.
               Example: Equipment.BLINK | Equipment.CLOAK means Lumina has Blink and Cloak.
        :return: A boolean indicating satisfaction of the requirements.
        """
        # If there are no requirements, they are always fulfilled.
        if self.requirements is None:
            return True
        # Otherwise we do have requirements. If the user has no equipment, the requirements are not fulfilled.
        elif user_equipment is None:
            return False
        # If the requirements are a bitwise flag, check if the requirements are a subset of the user's equipment.
        elif type(self.requirements) is Equipment:
            return self.requirements in user_equipment
        # If the requirements are in an iterable, check if any item in the iterable is a subset of the user's equipment.
        elif type(self.requirements) in (list, tuple, set):
            return any(item in user_equipment for item in self.requirements)
        else:
            raise ValueError("Unexpected requirements scenario")
