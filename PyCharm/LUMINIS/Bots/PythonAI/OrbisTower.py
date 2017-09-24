from PythonClientAPI.Game import PointUtils
from PythonClientAPI.Game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.Game.Enums import Direction, MoveType, MoveResult
from PythonClientAPI.Game.World import World

class PlayerAI:

    NESTCHANGES_ENEMY = list();
    NESTCHANGES_FRIENDLY = list();
    TURNCOUNT = 1;

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

        print("Turn:" + self.TURNCOUNT)
        self.TURNCOUNT += 1;


    """
    Push the number of nests that have been created this turn for a specified player
    """
    def UpdateNestChanges(self, isFriendly):

        nestPositions = None;
        if(isFriendly):
            nestPositions = get_friendly_nest_positions();
            self.NESTCHANGES_FRIENDLY.append(len(nestPositions));
        else:
            nestPositions = get_enemy_nest_positions();
            self.NESTCHANGES_ENEMY.append(len(nestPositions));

    """
    Calculate the average number of nests [Inclusive, exclusive)
    """
    def GetAverageNestGrowth(self, referenceStartTurn,referenceEndTurn, isFriendly):
        nests = None;
        changeList = [];
        total = 0;
        if(isFriendly):
            nests = self.NESTCHANGES_FRIENDLY[referenceStartTurn:referenceEndTurn]
        else:
            nests = self.NESTCHANGES_ENEMY[referenceStartTurn:referenceEndTurn]

        for i in range(1, len(nests)):
            changeVal = nests[i] - nests[i - 1];
            changeList.append(changeVal);
            total += changeVal;

        return total/len(changeList);

