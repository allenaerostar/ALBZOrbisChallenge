from PythonClientAPI.Game import PointUtils
from PythonClientAPI.Game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.Game.Enums import Direction, MoveType, MoveResult
from PythonClientAPI.Game.World import World


class PlayerAI:
    class UnitMemory:
        UNIT = None;
        WASCHECKED = False;

        def __init__(self):
            self.WASCHECKED = True;
            pass

    NESTCHANGES_ENEMY = list();
    NESTCHANGES_FRIENDLY = list();
    TURNCOUNT = 1;
    EXPANSIONLIST = [];
    POTENTIALNESTS = [];
    UNITMEMORIES = [];

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

        Update Average Nest spawning speed
        """
        self.UpdateNestChanges(world, True);
        self.UpdateNestChanges(world, False);
        self.UpdateExpansionList(world, enemy_units);
        POTENTIALNESTS = self.GetListOfPossibleNests(world, enemy_units, friendly_units);
        self.RemoveEmptyMemories();

        # Fly away to freedom, daring fireflies
        # Build thou nests
        # Grow, become stronger
        # Take over the world
        for unit in friendly_units:
            #check for persistent memory or create a new one
            memory = self.GetMemory(unit);
            if memory is None:
                self.NewMemory(unit);
            path = world.get_shortest_path(unit.position,
                                           world.get_closest_capturable_tile_from(unit.position, None).position,
                                           None)
            if path: world.move(unit, path[0])

        #print("Average:" + str(self.GetAverageNestGrowth(0, self.TURNCOUNT, True)))
        self.TURNCOUNT += 1;

    def RemoveEmptyMemories(self):
        toRemove = [];
        for mem in self.UNITMEMORIES:
            if mem.WASCHECKED:
                mem.WASCHECKED = False;
            else:
                toRemove.append(mem);
        for mem in toRemove:
            self.UNITMEMORIES.remove(mem);

    def GetMemory(self, unit):
        for mem in self.UNITMEMORIES:
            if mem.UNIT == unit:
                return mem;
        return None;

    def NewMemory(self, unit):
        newMem = self.UnitMemory();
        newMem.UNIT = unit;
        self.UNITMEMORIES.append(newMem);
        return newMem;

    """
    Push the number of nests that have been created this turn for a specified player
    """

    def UpdateNestChanges(self, world, isFriendly):
        if (isFriendly):
            self.NESTCHANGES_FRIENDLY.append(len(world.get_friendly_nest_positions()))
        else:
            self.NESTCHANGES_ENEMY.append(len(world.get_enemy_nest_positions()))

    """
    Calculate the average number of nests [Inclusive, exclusive)
    """

    def GetAverageNestGrowth(self, referenceStartTurn, referenceEndTurn, isFriendly):
        nests = None;
        changeList = [];
        total = 0;
        if (isFriendly):
            nests = self.NESTCHANGES_FRIENDLY[referenceStartTurn:referenceEndTurn]
        else:
            nests = self.NESTCHANGES_ENEMY[referenceStartTurn:referenceEndTurn]

        if(self.TURNCOUNT == 1):
            return 0;
        else:
            for i in range(1, len(nests)):
                changeVal = nests[i] - nests[i - 1];
                changeList.append(changeVal);
                total += changeVal;

            return total / len(changeList);

    def TotalArmyValue(self, units):
        totalArmyValue = 0
        for unit in units:
            totalArmyValue += unit.health
        return totalArmyValue

    def StrongestUnits(self, units):
        strongestUnits = units
        strongestUnits.sort(key=lambda unit: unit.health);

        return strongestUnits

    def UpdateExpansionList(self, world, enemy_units):
        friendNestPositions = world.get_friendly_nest_positions()
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
    @staticmethod
    def IsNestable(self, world, nestPoint):
        if world.get_tile_at(nestPoint).is_neutral():
            return False;

        tilesAround = nestPoint.world.get_tiles_around();
        for key in tilesAround:
            if tilesAround[key].is_permanently_owned():
                return False;
        return True;

    def GetListOfPossibleNests(self, world, enemy_units, friendly_units):
        RANGE_ENEMY = 6;
        RANGE_PLAYER = 7;
        neutralTiles = world.get_neutral_tiles();
        #neutralTiles.sort(key=lambda x: world.get_shortest_path(x.position, world.get_closest_friendly_nest_from(x.position, None), None), reverse=True);
        neutralTiles.sort(key=lambda x: self.SortBySafestNestPriority(x, world, enemy_units, friendly_units, RANGE_ENEMY, RANGE_PLAYER), reverse=True);
        return neutralTiles;

    def SortBySafestNestPriority(self, x, world, enemy_units, friendly_units, rangeEnemy, rangePlayer):
        enemies = self.CheckEnemiesWithinRange(world, enemy_units, x.position, rangeEnemy);
        friends = self.CheckAlliesWithinRange(world, friendly_units, x.position, rangePlayer);

        if(len(friends) == 0):
            return -999;
        if(len(enemies) > 0):
            return self.CheckContestRange(world, self.SumUnitValue(enemies), friendly_units, enemies[0].position, x.position);
        else:
            return 999;

    """
    Contest Range
    """
    def CheckContestRange(self, world, subset_army_value, friendly_units, enemy_position, nest_position):
        defendingUnitsTAV = 0
        for unit in friendly_units:
            if world.get_shortest_path_distance(nest_position, unit.position)  < world.get_shortest_path_distance(nest_position, enemy_position):
                defendingUnitsTAV+= unit.health;

        return defendingUnitsTAV - subset_army_value

    def CheckEnemiesWithinRange(self, world, enemy_units, nest_position, range):
        enemies = []
        for enemy in enemy_units:
            if world.get_shortest_path_distance(nest_position, enemy.position) < range:
                enemies.append(enemy);
        return enemies

    def CheckAlliesWithinRange(self, world, friendly_units, nest_position, range):
        friendly = []
        for friend in friendly_units:
            if world.get_shortest_path_distance(nest_position, friend.position) < range:
                friendly.append(friend);
        return friendly

    def SumUnitValue(self, units):
        sum = 0;
        for unit in units:
            sum += unit.health;
        return sum;

    class UnitMemory:
        UNIT = None

        def __init__(self, unit):
            """
            Any instantiation code goes here
            """
            self.UNIT = unit

        def ConstructNest(self, world, position):
            if(PlayerAI.IsNestable(self, world, position)):
                closestAdj = None;
                shortestDistance = 0;
                adjTiles = world.get_tiles_around(position)
                for adj in adjTiles:
                    distance = world.get_shortest_path_distance(self.UNIT.position, adjTiles[adj].position)
                    if distance != 0 and distance < shortestDistance and not(adjTiles[adj].is_friendly()) and not(adjTiles[adj].is_permanently_owned()):
                        shortestDistance = distance
                        closestAdj = adjTiles[adj].position
                path = world.get_shortest_path(self.UNIT.position, closestAdj.position)
                world.move(self.UNIT, path[0])



        def AttackEnemyNest(self, world):
            closestAdj = None;
            shortestDistance = 0;
            adjTiles = world.get_tiles_around(self.UNIT.position)
            for adj in adjTiles:
                distance = world.get_shortest_path_distance(self.UNIT.position, adjTiles[adj].position)
                if distance != 0 and distance < shortestDistance:
                    shortestDistance = distance
                    closestAdj = adjTiles[adj].position
            path = world.get_shortest_path(self.UNIT.position, closestAdj.position)
            world.move(self.UNIT, path[0])