import psycopg2
from configparser import ConfigParser
import random
import copy

database = []
objTeams = []
objGroups = []
objPots = [None] * 4
groupsAvailable = [None] * 8

# function that gets the config parameters for the connection to database
def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    db= {}

    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return db


def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        # create a cursor
        cur = conn.cursor()

        # execute a statement
        print('PostgreSQL database version:')
        cur.execute("SELECT * FROM champions.sorteio ORDER BY \"pote\"")

        # display the PostgreSQL database version
        database = cur.fetchall()
        objectConvTeams(database)
        objectConvPots(objTeams)

        # close the communication with the PostgreSQL
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


# function that updates the database after the draw, changing the group field of each team
def update(groups):
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    for i in range(8):
        cur.execute("UPDATE champions.sorteio SET \"group\" = %s WHERE equipa = %s OR equipa = %s OR equipa = %s OR equipa = %s", (groups[i].name, groups[i].group[0].name, groups[i].group[1].name, groups[i].group[2].name, groups[i].group[3].name))
    conn.commit()


# function that clears the groups after draw
def clear_groups(groups):
    groups.clear()


# function that returns a random element from a given list
def random_from_list(lista):
    picked = random.choice(lista)
    return picked


# class containing every data from the team object
class Team:
    def __init__(self, name, country, pot):
        self.name = name
        self.country = country
        self.pot = pot

    def __str__(self):
        return self.name


# class containing every data from the group object, and a method to add a team to a given group
class Group:
    def __init__(self, name):
        self.name = name
        self.group = [None] * 4

    def add_team(self, team, aux, pot):
        aux.group[pot] = team


# assigns the database values returned from the connection to a list of team objects
def objectConvTeams(database):
    for i in range(32):
        obj = Team(database[i][0], database[i][1], database[i][2])
        objTeams.append(obj)


# function that divides all 32 teams according to their pots
def objectConvPots(Teams_pot):
    temp = []

    for j in range(4):
        for i in range(32):
            if Teams_pot[i].pot == (j + 1):
                temp.append(Teams_pot[i])
        objPots[j] = temp
        temp = []


# function that creates a list of group objects
def objectConvGroups():
    for ch in "ABCDEFGH":
        group = Group(ch)
        objGroups.append(group)
    return objGroups


# function responsible for ordering the teams left to draw based on the number of groups they can be drawn into
def sorter(pTeams, pAvailable):
    pAvailableLocal = sorted(pAvailable, key=lambda k: k['size'])
    for i in range(len(pAvailableLocal)):
        pTeams[i] = (pAvailableLocal[i]["Equipa"])
    return [pTeams, pAvailableLocal]


# main class, is responsible for:
# 1) building the list of available groups for a given team
# 2) draw all the teams of a pot
# 3) being the "engine" through the body method
class Draw:
    def build_groups_list_potX(self, team, groups_lst, pot, repeat):
        result = []
        if pot == 0:
            if repeat != 0:
                if repeat % 2 == 0:
                    for i in range(4, 8):
                        if groups_lst[i].group[pot] is None:
                                result.append(groups_lst[i])
                else:
                    for i in range(4):
                        if groups_lst[i].group[pot] is None:
                                result.append(groups_lst[i])
            else:
                for i in range(8):
                    if groups_lst[i].group[pot] is None:
                            result.append(groups_lst[i])

        else:
            if repeat != 0:
                if repeat % 2 != 0:
                    for i in range(4):
                        countries = []
                        for j in range(pot):
                            countries.append(groups_lst[i].group[j].country)
                        if groups_lst[i].group[pot] is None:
                            if team.country not in countries:
                                result.append(groups_lst[i])

                else:
                    for i in range(4, 8):
                        countries1 = []
                        for j in range(pot):
                            countries1.append(groups_lst[i].group[j].country)
                        if groups_lst[i].group[pot] is None:
                            if team.country not in countries1:
                                result.append(groups_lst[i])

            else:
                for i in range(8):
                    countries2 = []
                    for j in range(pot):
                        countries2.append(groups_lst[i].group[j].country)
                    if groups_lst[i].group[pot] is None:
                        if team.country not in countries2:
                            result.append(groups_lst[i])
        return result

    def draw_potX(self, pot_lst, groups_lst, pot):
        teams = []
        countries = []
        times = []
        multiples = []
        multiples_int = []
        groups_drawn = []
        pTeams = [None] * 8
        to_delete_teams = []
        to_delete_groups = []

        for i in range(8):
            team_1 = random_from_list(pot_lst)
            teams.append(team_1)
            countries.append(team_1.country)
            pot_lst.remove(team_1)

        for i in range(8):
            times.append(countries.count(teams[i].country))

        for i in range(8):
            if times[i] > 1:
                if teams[i].country not in multiples:
                    multiples.append(teams[i].country)
                    multiples_int.append(1)

        for i in range(8):
            if teams[i].country in multiples:
                index = multiples.index(teams[i].country)
                groupsAvailable_lst = self.build_groups_list_potX(teams[i], groups_lst, pot, multiples_int[index])
                groupsAvailable[i] = ({"Equipa": teams[i], "Grupos": groupsAvailable_lst, "size": len(groupsAvailable_lst)})
                multiples_int[index] += 1
            else:
                groupsAvailable_lst = self.build_groups_list_potX(teams[i], groups_lst, pot, 0)
                groupsAvailable[i] = ({"Equipa": teams[i], "Grupos": groupsAvailable_lst, "size": len(groupsAvailable_lst)})

        pAvailable = groupsAvailable
        aux = sorter(pTeams, pAvailable)
        pTeams = aux[0]
        pAvailable = aux[1]

        for i in range(8):
            if pTeams[i] is not None:
                if pTeams[i].country in multiples:
                    group_1 = random_from_list(pAvailable[i]["Grupos"])
                    if group_1 in groups_drawn:
                        count_rep = 0
                        while group_1 in groups_drawn:
                            group_1 = random_from_list(pAvailable[i]["Grupos"])
                            if count_rep == 100:
                                return False
                            count_rep += 1
                    groups_drawn.append(group_1)
                    index_group_1 = groups_lst.index(group_1)
                    Group(groups_lst[index_group_1]).add_team(pTeams[i], groups_lst[index_group_1], pot)
                    multiples_int[index] += 1
                    to_delete_teams.append(i)
                    to_delete_groups.append(i)
                    pTeams[i] = None

                    for j in range(len(pAvailable)):
                        if pAvailable[j] is not None:
                            if group_1 in pAvailable[j]["Grupos"]:
                                pAvailable[j]["Grupos"].remove(group_1)

                aux = sorter(pTeams, pAvailable)
                pTeams = aux[0]
                pAvailable = aux[1]

        pTeams = [q for r, q in enumerate(pTeams) if r not in to_delete_teams]
        pAvailable = [w for e, w in enumerate(pAvailable) if e not in to_delete_groups]

        for k in range(len(pAvailable)):
            if pTeams[k] is not None:
                group_2 = random_from_list(pAvailable[k]["Grupos"])
                if group_2 in groups_drawn:
                    count = 0
                    while group_2 in groups_drawn:
                        group_2 = random_from_list(pAvailable[k]["Grupos"])
                        if count == 100:
                            return False
                        count += 1
                groups_drawn.append(group_2)
                index_group_2 = groups_lst.index(group_2)
                Group(groups_lst[index_group_2]).add_team(pTeams[k], groups_lst[index_group_2], pot)
                pTeams[k] = None

                for c in range(len(pAvailable)):
                    if pAvailable[c] is not None:
                        if group_2 in pAvailable[c]:
                            pAvailable[c]["Grupos"].remove(group_2)

            aux = sorter(pTeams, pAvailable)
            pTeams = aux[0]
            pAvailable = aux[1]
        return True

    def body(self, pots, groups):
        i = 0
        aux = [None] * 4
        count = 0

        for j in range(4):
            aux[j] = copy.deepcopy(pots)

        while i < 4:
            test = self.draw_potX(pots[i], groups, i)
            if test is False:
                while test is False:
                    for k in range(8):
                        groups[k].group[i] = None
                    if_fail = copy.deepcopy(aux[count][i])
                    test = self.draw_potX(if_fail, groups, i)
                    count += 1
            i += 1
        objectConvPots(objTeams)
        update(objGroups)

