from PythonClientAPI.Game import PointUtils
from PythonClientAPI.Game.Entities import FriendlyUnit, EnemyUnit, Tile
from PythonClientAPI.Game.Enums import Direction, MoveType, MoveResult
from PythonClientAPI.Game.World import World
from enum import Enum

class PlayerAI:
    NESTCHANGES_ENEMY = list();
    NESTCHANGES_FRIENDLY = list();
    TURNCOUNT = 1;
    EXPANSIONLIST = [];
    POTENTIALNESTS = [];
    UNITMEMORIES = [];
    TOAVOID = [];

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
        self.POTENTIALNESTS = self.GetListOfPossibleNests(world, enemy_units, friendly_units);
        self.RemoveEmptyMemories();

        # Fly away to freedom, daring fireflies
        # Build thou nests
        # Grow, become stronger
        # Take over the world
        for unit in friendly_units:
            #check for persistent memory or create a new one
            memory = self.GetMemory(unit);
            if memory is None:
                #determine here
                memory = self.NewMemory(unit, 'Farm');
                if(len(self.POTENTIALNESTS) > 0):
                    memory.POTENTIAL_NEST = self.POTENTIALNESTS[0];
                    self.TOAVOID.append(self.POTENTIALNESTS[0]);

            #path = world.get_shortest_path(unit.position,
            #                               world.get_closest_capturable_tile_from(unit.position, None).position,
            #                               None)
            #if path: world.move(unit, path[0])

            memory.Move(world, enemy_units, friendly_units, self.TileListToPositions(self.TOAVOID));

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

    def NewMemory(self, unit, type):
        newMem = self.UnitMemory(unit, type);
        self.UNITMEMORIES.append(newMem);
        return newMem;

    def TileListToPositions(self, tileList):
        positions = [];
        for tile in tileList:
            positions.append(tile.position);

        return positions;

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

        tilesAround = world.get_tiles_around(nestPoint);
        for key in tilesAround:
            if tilesAround[key].is_permanently_owned():
                return False;
        return True;

    def GetListOfPossibleNests(self, world, enemy_units, friendly_units):
        RANGE_ENEMY = 6;
        RANGE_PLAYER = 6;
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


    #Memory Class
    class UnitMemory:
        UNIT = None;
        POSITION = None;
        WASCHECKED = False;
        MYTYPE = None;
        TARGET_NEST = None;

        class TASKTYPE:
            ATTACK, DEFEND, FARM, FREE = range(4)

        def __init__(self, world, unit, type):
            self.UNIT = unit;
            self.POSITION = unit.position;
            self.WASCHECKED = True;
            closestNest = None;
            closestDistance = 999;
            for nest in world.get_enemy_nest_positions():
                nestDistance = world.get_shortest_path_distance(self.POSITION, nest)
                if nestDistance < closestDistance:
                    closestDistance = nestDistance
                    closestNest = nest
            self.TARGET_NEST = world.get_tile_at(closestNest)


            if type == 'Attack':
                self.MYTYPE = self.TASKTYPE.ATTACK;
            elif type == 'Defend':
                self.MYTYPE = self.TASKTYPE.DEFEND;
            elif type == 'Farm':
                self.MYTYPE = self.TASKTYPE.FARM;
            pass

        def IsNestable(self, world, nestPoint):
            if world.get_tile_at(nestPoint).is_neutral():
                return False;

            tilesAround = world.get_tiles_around(nestPoint);
            for key in tilesAround:
                if tilesAround[key].is_permanently_owned():
                    return False;
            return True;

        def Move(self, world, enemy_units, friendly_units, toAvoid):
            if self.MYTYPE == self.TASKTYPE.FARM:
                print(self.POTENTIAL_NEST);
                if self.IsNestable(world, self.POTENTIAL_NEST.position):
                    self.MYTYPE = self.TASKTYPE.FREE;
                else:
                    self.ConstructNest(world, friendly_units, toAvoid);
            elif self.MYTYPE == self.TASKTYPE.ATTACK:
                if not (self.TARGET_NEST.is_friendly()) and not (self.TARGET_NEST.is_permanently_owned()):
                    self.AttackEnemyNest(world)
                else:
                    self.MYTYPE = self.TASKTYPE.FREE;

        #FARM specific parameters
        POTENTIAL_NEST = None;
        def ConstructNest(self, world, friendly_units, toAvoid):
            #print(tile);
            adjTiles = world.get_tiles_around(self.POTENTIAL_NEST.position);
            filteredTiles = [];
            for adj in adjTiles:
                distance = world.get_shortest_path_distance(self.POSITION, adjTiles[adj].position);
                if distance != 0 and not (adjTiles[adj].is_friendly()) and not (
                    adjTiles[adj].is_permanently_owned()):
                    filteredTiles.append(adjTiles[adj]);

            if len(filteredTiles) == 0:
                return False;

            avoid = set();
            avoid.add(self.POTENTIAL_NEST.position);
            for friend in friendly_units:
                avoid.add(friend.position);
            for av in toAvoid:
                avoid.add(av);

            #BUG: self.UNIT.position WAS NOT PASSED BY REFERENCE !!!!
            path = world.get_shortest_path(self.POSITION, filteredTiles[0].position, avoid)
            if path is not None:
                if len(path) > 0:
                    if world.move(self.UNIT, path[0]) != MoveType.REST:
                        self.POSITION = path[0];
            return True;

        def AttackEnemyNest(self, world):

            path = world.get_shortest_path(self.position, self.TARGET_NEST.position)
            world.move(self.UNIT, path[0])

