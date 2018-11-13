import random
import math


class Chip(object):
    '''
    x: -1 : 1
    y: -1 : 1
    efficiency: 0.018 : 1.1
    '''

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def fix_value_overflows(self):
        if self.x > 1: self.x = 1
        if self.y > 1: self.y = 1
        if self.x < -1: self.x = -1
        if self.y < -1: self.y = -1

    def calculate_efficiency(self):
        self.efficiency = (self.x ** 2 + 3 * self.y ** 2) * math.exp(-self.x ** 2 - self.y ** 2)


def populate():
    population = []
    for individual in range(30):
        x = random.uniform(-1.0, 1.0)
        y = random.uniform(-1.0, 1.0)
        a_chip = Chip(x, y)
        a_chip.calculate_efficiency()
        population.append(a_chip)
    return population


def get_max(population):
    maximum_efficiency = max(gene.efficiency for gene in population)
    return maximum_efficiency


def evolve(population):
    for generation in range(200):
        for individual in range(len(population)):
            for previous_individual in range(individual):
                distance = 0
                if population[previous_individual].efficiency > population[individual].efficiency:
                    distance = math.sqrt((population[individual].x - population[previous_individual].x) ** 2 + (
                        population[individual].y - population[previous_individual].y) ** 2)

                    attractiveness = (population[previous_individual].efficiency - population[
                        individual].efficiency) * math.exp(-4 * distance ** 2)

                    population[individual].x += (
                        attractiveness * (population[previous_individual].x - population[individual].x) + 0.15 * (
                            random.uniform(0.0, 1.0) - 0.5))

                    population[individual].y += (
                        attractiveness * (population[previous_individual].x - population[individual].x) + 0.15 * (
                            random.uniform(0.0, 1.0) - 0.5))

                    population[individual].fix_value_overflows()

                    population[individual].calculate_efficiency()
    return population


if __name__ == "__main__":
    population = populate()
    final_population = evolve(population)
    max_efficiency = get_max(final_population)
    print(max_efficiency)
