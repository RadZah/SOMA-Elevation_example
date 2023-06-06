import sys

import numpy as np
import requests


class OpenTopoData:
    API_REQUESTS_COUNT = 0  # Class variable
    OPEN_TOPO_DATA_BASE_URL = "https://api.opentopodata.org/v1/etopo1"  # Class variable

    @classmethod
    def get_coordinates_elevation(cls, latt, long):
        # API Call to get the position values
        # url = f"https://api.open-elevation.com/api/v1/lookup?locations={lat},{lng}"
        url = f"{cls.OPEN_TOPO_DATA_BASE_URL}?locations={latt},{long}"
        try:
            OpenTopoData.API_REQUESTS_COUNT += 1
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)

        data = response.json()
        elevation = data["results"][0]["elevation"]
        return elevation


class GoogleMapInstance:
    API_REQUESTS_COUNT = 0  # Class variable
    BASE_URL = "https://maps.googleapis.com/maps/api/elevation/json"
    API_KEY = "Your-Private-Key-for-Google-Maps-Elevation-API"  # https://console.cloud.google.com/

    @classmethod
    def get_coordinates_elevation(cls, latt, long):
        # API Call to get the position values
        # url = f"https://maps.googleapis.com/maps/api/elevation/json?locations={lat},{lng}&key={API_KEY}"
        url = f"{cls.BASE_URL}?locations={latt},{long}&key={cls.API_KEY}"
        try:
            GoogleMapInstance.API_REQUESTS_COUNT += 1
            response = requests.get(url)
        except requests.exceptions.RequestException as e:
            print(e)
            sys.exit(1)
        data = response.json()
        elevation = data["results"][0]["elevation"]
        return elevation


class Individual:

    def __init__(self, latt=None, long=None):
        self.latt = latt
        self.long = long
        self.fitness = None

    def update_fitness_values(self, map_api):
        # API Call to get the position values
        if map_api == "GoogleElevationMap":
            self.fitness = GoogleMapInstance.get_coordinates_elevation(self.latt, self.long)
        elif map_api == "OpenTopoData":
            self.fitness = OpenTopoData.get_coordinates_elevation(self.latt, self.long)
        else:
            sys.exit("Invalid map_api value")

    def get_fitness(self, map_api):
        if self.fitness is None:
            self.update_fitness_values(map_api)
        return self.fitness

    def set_coordinates(self, latt=0, long=0):
        self.latt = latt
        self.long = long


class Soma:

    def __init__(self,
                 path_length=3,
                 step=0.4,  # step=0.11,
                 population_size=15,
                 migrations=3,
                 accepted_error=10
                 # prt=1,
                 # dimensions=1,
                 ):

        self.PATH_LENGTH = path_length
        self.STEP = step
        self.POPULATION_SIZE = population_size
        self.MIGRATIONS = migrations
        self.ACCEPTED_ERROR = accepted_error

        # self.MAP_API = "GoogleElevationMap"
        self.MAP_API = "OpenTopoData"

        # self.PRT = None
        # self.DIMENSIONS = None

        self.POPULATION = []

        self.LATT_MIN = None
        self.LATT_MAX = None
        self.LONG_MIN = None
        self.LONG_MAX = None

        self.BEST_FITNESS_INDEX = None
        self.BEST_FITNESS = None

        self.DEBUG_MODE = False

    def set_google_map_api(self):
        self.MAP_API = "GoogleElevationMap"

    def set_open_topo_data_api(self):
        self.MAP_API = "OpenTopoData"

    def objective_function(self, individual):
        fittness = individual.get_fitness(self.MAP_API)
        return fittness

    def get_distnace_to_leader(self, i):
        """ Calculate the distance to the Leader """

        distance_latt = self.POPULATION[self.BEST_FITNESS_INDEX].latt - self.POPULATION[i].latt
        distance_long = self.POPULATION[self.BEST_FITNESS_INDEX].long - self.POPULATION[i].long

        return distance_latt, distance_long

    def update_leader_if_better_founded(self, random_individual, i):
        """ Check if the new individual is better than the current leader if so update the leader """

        elevation = random_individual.get_fitness(self.MAP_API)
        if self.BEST_FITNESS is None or elevation > self.BEST_FITNESS:
            self.BEST_FITNESS = elevation
            self.BEST_FITNESS_INDEX = i

        return

    def create_random_individual(self, i):
        """ Create individual with random position """
        lattitude_x = np.random.uniform(self.LATT_MIN, self.LATT_MAX)
        longitude_y = np.random.uniform(self.LONG_MIN, self.LONG_MAX)

        random_individual = Individual(latt=lattitude_x, long=longitude_y)
        self.update_leader_if_better_founded(random_individual, i)

        return random_individual

    def initialize_population(self):
        """ Initialize randomly distributed population  """

        for i in range(self.POPULATION_SIZE):
            new_individual = self.create_random_individual(i)
            self.POPULATION.append(new_individual)

    @staticmethod
    def compare_fittness(migrating_fitness, best_fitness):
        """
        :param migrating_fitness:
        :param best_fitness:
        :return: True if migratting_fitness better, False if not
        """
        if migrating_fitness > best_fitness:
            ret = True
        else:
            ret = False
        return ret

    def migrate_if_better(self, migrating_individual, updated_individual, best_fitness):

        migrating_fitness = migrating_individual.get_fitness(self.MAP_API)

        if self.compare_fittness(migrating_fitness, best_fitness):
            updated_individual["fitness"] = migrating_fitness
            updated_individual["latt"] = migrating_individual.latt
            updated_individual["long"] = migrating_individual.long
            updated_individual["updated"] = True
            best_fitness = migrating_fitness

        return updated_individual, best_fitness

    def migrate(self, initial_individual, updated_individual, best_fitness,
                distance_towards_leader_latt, distance_towards_leader_long, step_towards_leader):

        move_latt_val = initial_individual.get("latt") + (distance_towards_leader_latt * self.PATH_LENGTH) * (
                step_towards_leader / (self.PATH_LENGTH / self.STEP))

        move_long_val = initial_individual.get("long") + (distance_towards_leader_long * self.PATH_LENGTH) * (
                step_towards_leader / (self.PATH_LENGTH / self.STEP))

        # check if the new position is out of bounds
        if move_latt_val > self.LATT_MAX or move_latt_val < self.LATT_MIN \
                or move_long_val > self.LONG_MAX or move_long_val < self.LONG_MIN:
            pass
        else:

            migrating_individual = Individual()
            migrating_individual.set_coordinates(latt=move_latt_val, long=move_long_val)
            updated_individual, best_fitness = self.migrate_if_better(
                migrating_individual, updated_individual, best_fitness)

        return updated_individual, best_fitness

    def check_all_the_path(self, i):

        if self.DEBUG_MODE:
            print("\tOLD fittnes for i: ", i, " fittness", self.POPULATION[i].get_fitness(self.MAP_API))

        leader_adept = {"fitness": self.BEST_FITNESS, "index": self.BEST_FITNESS_INDEX}

        distance_towards_leader_latt, distance_towards_leader_long = self.get_distnace_to_leader(i)

        best_fitness = self.POPULATION[i].get_fitness(self.MAP_API)

        initial_individual = {"fitness": self.POPULATION[i].get_fitness(self.MAP_API), "latt": self.POPULATION[i].latt,
                              "long": self.POPULATION[i].long}

        updated_individual = {"fitness": None, "latt": None, "long": None, "updated": False, "index": i}

        # check all the path
        for step_thought_path in range(int(self.PATH_LENGTH / self.STEP)):
            updated_individual, best_fitness = self.migrate(initial_individual,
                                                            updated_individual,
                                                            best_fitness,
                                                            distance_towards_leader_latt,
                                                            distance_towards_leader_long,
                                                            step_thought_path + 1)

        if updated_individual.get("updated") is True:
            self.POPULATION[i].set_coordinates(latt=updated_individual.get("latt"), long=updated_individual.get("long"))
            self.POPULATION[i].fitness = updated_individual.get("fitness")

            if updated_individual.get("fitness") > leader_adept.get("fitness"):
                self.BEST_FITNESS = updated_individual.get("fitness")
                self.BEST_FITNESS_INDEX = updated_individual.get("index")

        if self.DEBUG_MODE:
            print("\tNEW fittnes for i: ", i, " fittness", self.POPULATION[i].get_fitness(self.MAP_API), "\n")

    def create_return_dict(self, msg, migrations):
        ret = {
            "best_elevation": self.POPULATION[self.BEST_FITNESS_INDEX].get_fitness(self.MAP_API),
            "best_latt": self.POPULATION[self.BEST_FITNESS_INDEX].latt,
            "best_long": self.POPULATION[self.BEST_FITNESS_INDEX].long,
            "message": msg,
            "no_of_migrations": migrations,
            "Open_Topo_Data_API_requests": OpenTopoData.API_REQUESTS_COUNT,
            "Google_Map_API_requests": GoogleMapInstance.API_REQUESTS_COUNT
        }
        return ret

    def run(self):
        """ Run the SOMA algorithm and try to find the best solution """

        self.initialize_population()

        for each_migration in range(self.MIGRATIONS):  # loop through all migrations

            if self.DEBUG_MODE:
                print("Migration start : ", each_migration, " best is ", self.BEST_FITNESS)

            best_on_migration_start = self.BEST_FITNESS

            for i in range(self.POPULATION_SIZE):  # loop through all individuals
                if i != self.BEST_FITNESS_INDEX:
                    self.check_all_the_path(i)

            if self.DEBUG_MODE:
                print("Migration end best is ", self.BEST_FITNESS, ", index ", self.BEST_FITNESS_INDEX, "\n\n")

            if best_on_migration_start == self.BEST_FITNESS:
                return self.create_return_dict(msg="No change of postion during last migration",
                                               migrations=each_migration + 1)
            elif (abs(best_on_migration_start - self.BEST_FITNESS) < self.ACCEPTED_ERROR):
                msg_val = "Last migration change is less than accepted change. Exactly: ", abs(
                    best_on_migration_start - self.BEST_FITNESS)
                return self.create_return_dict(msg=msg_val, migrations=each_migration + 1)

        return self.create_return_dict(msg="Number of migrations reached, ", migrations=each_migration + 1)

    def set_area(self, coordinates):
        """ Set the area of the search """

        self.LATT_MIN = coordinates["latt_min"]
        self.LATT_MAX = coordinates["latt_max"]
        self.LONG_MIN = coordinates["long_min"]
        self.LONG_MAX = coordinates["long_max"]
