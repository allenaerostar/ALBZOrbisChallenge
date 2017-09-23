from PythonClientAPI.Game import PointUtils
from PythonClientAPI.Game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.Game.Enums import Direction, MoveType, MoveResult
from PythonClientAPI.Game.World import World


class PlayerAI:
    EXPANSIONLIST = []

    def __init__(self):
        """
        Any instantiation code goes here
        """
        pass

    def do_move(self, world, friendly_units, enemy_units):
        """
        This method will get called every turn.

        :param world: World object reflecting current game state
        :param friendly_units: list of FriendlyUnit objects
        :param enemy_units: list of EnemyUnit objects
        """
        # Fly away to freedom, daring fireflies
        # Build thou nests
        # Grow, become stronger
        # Take over the world
        for unit in friendly_units:
            path = world.get_shortest_path(unit.position,
                                           world.get_closest_capturable_tile_from(unit.position, None).position,
                                           None)
            if path: world.move(unit, path[0])

    def TotalArmyValue(self, units):
        totalArmyValue = 0
        for unit in units:
            totalArmyValue += unit.health
        return totalArmyValue

    def StrongestUnits(self, units):
        strongestUnits = units
        strongestUnits.sort(key=lambda unit: unit.health, reverse=True);

        return strongestUnits

    def UpdateExpansionList(self, world, enemy_units):
        friendNestPositions = World.get_friendly_nest_positions()
        nestEnemyPairs =[]
        for position in friendNestPositions:
            shortestDistance = -1
            closestEnemies = []
            for enemy in enemy_units:
                enemy_distance = world.get_shortest_path_distance(position, enemy.position);
                if enemy_distance != -1 and enemy_distance < shortestDistance:
                    closestEnemies.clear()
                    closestEnemies.append(enemy)
            nestEnemyPairs.append((position, closestEnemies))
        self.EXPANSIONLIST.append(nestEnemyPairs)


