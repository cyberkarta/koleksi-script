from collections import namedtuple
from random import choices, randint, randrange, random
from typing import List, Callable, Tuple
import time
from functools import partial

Genome = List[int]
Population = List[Genome]
FitnessFunc = Callable[[Genome], int]
PopulateFunc = Callable[[], Population]
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
MutationFunc = Callable[[Genome], Genome]

Risk = namedtuple('Risk', ['name', 'val_mitigation', 'cost_mitigation'])
risks = [
          Risk('SQL injection in login panel', 9.8,6),
          Risk('DOM based XSS with CSP configured',	5.2,7),
          Risk('Admin email exposure', 3.8,2),
          Risk('SSRF in upload page', 7.2, 5),
          Risk('SameSite policy not enforced',6.8,6),
          Risk('No CSRF token',8.5,8),
          Risk('XSS in search box with CSP configured',7.3,6),
          Risk('Outdated framework',8.1,7),
          Risk('Vulnerability in Angular JS',7.5,7),
]

def generate_genome(length: int) -> Genome:
  return choices([0, 1], k=length)

def generate_population(size: int, genome_length: int) -> Population:
  return [generate_genome(genome_length) for g in range(size)]

def fitness(genome: Genome, risks: [Risk], cost_limit: int) -> int:
  if len(genome) != len(risks):
    raise ValueError("genome must be the same length")

  cost = 0
  value = 0

  for i, risk in enumerate(risks):
    if genome[i] == 1:
      cost += risk.cost_mitigation
      value += risk.val_mitigation
      
      if cost > cost_limit :
        return 0

    return value

def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
  return choices(
      population=population,
      weights=[fitness_func(genome) for genome in population],
      k=2
  )

def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
  if len(a) != len(b):
    raise ValueError("Genomes a and b must be the same length")

  length = len(a)
  if length < 2:
    return a, b

  p = randint(1, length -1)
  return a[0:p] + b[p:], b[0:p] + a[p:]

def mutation(genome: Genome, num: int = 1, probability: float = 0.5) -> Genome:
  for i in range(num):
    index = randrange(len(genome))
    genome[index] = genome[index] if random() > probability else abs(genome[index] - 1)
  return genome

def run_evolution(
    populate_func: PopulateFunc,
    fitness_func: FitnessFunc,
    selection_func: SelectionFunc = selection_pair,
    crossover_func: CrossoverFunc = single_point_crossover,
    mutation_func: MutationFunc = mutation,
    generation_limit: int = 100,
    fitness_limit: int = 100
) -> Tuple[Population, int]:
  population = populate_func()

  for i in range(generation_limit):
    population = sorted(
        population,
        key=lambda genome: fitness_func(genome),
        reverse=True
    )

    if fitness_func(population[0]) >= fitness_limit:
      break

    next_generation = population[0:2]

    for j in range(int(len(population) / 2) - 1):
      parents = selection_func(population, fitness_func)
      offspring_a, offspring_b = crossover_func(parents[0], parents[1])
      offspring_a = mutation_func(offspring_a)
      offspring_b = mutation_func(offspring_b)
      next_generation += [offspring_a, offspring_b]
    
    population = next_generation

  population = sorted(
      population,
      key=lambda genome: fitness_func(genome),
      reverse=True
  )

  return population, i

start = time.time()
population, generations = run_evolution(
    populate_func=partial(
        generate_population, size = 10, genome_length=len(risks)
    ),
    fitness_func=partial(
        fitness, risks=risks, cost_limit=15
    ),
    fitness_limit=100,
    generation_limit=100
)
end = time.time()

def genome_to_risks(genome: Genome, risks: [Risk]) -> [Risk]:
  result = []
  for i, risk in enumerate(risks):
    if genome[i] > 0:
      result += [risk.name]

  return result

print (f"number of generations: {generations}")
print (f"time: {end - start} s")
print (f"best solution: {genome_to_risks(population[0], risks)}")
