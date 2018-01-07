#!/usr/bin/env python3

# https://burakkanber.com/blog/machine-learning-genetic-algorithms-part-1-javascript/

from optparse import OptionParser
import sys
import string
import random
# from time import sleep

parser = OptionParser()
parser.add_option("-g", action="store", type="string", dest="goal", help="goal to achive")
parser.add_option("-s", action="store", type="int", dest="size", default=10, help="population size")
parser.add_option("-m", action="store", type="float", dest="mutation", default=0.5, help="random mutation chance")
(options, args) = parser.parse_args()

# alphabet = string.printable
alphabet = string.ascii_letters + string.digits + " ?!,.:;"

class Chromosome:

	def __init__(self, code):
		self.code = code
		self.cost = sys.maxsize

	def __str__(self):
		return "{} {}".format(self.code, self.cost)

	def __repr__(self):
		return self.__str__()

	@classmethod
	def random(cls, len):
		code = ""
		for i in range(0, len):
			code += random.choice(alphabet)
		return Chromosome(code)

	def calc_cost(self, goal):
		total = 0
		for i in range(0, len(self.code)):
			# distance between two ascii characters
			value = alphabet.index(self.code[i]) - alphabet.index(goal[i])
			# square that distance so it couldn't be negative
			total += value * value
		self.cost = total

	def mate(self, chromosome):
		# mate two chromosomes to produce childs:
		# 	test + abcd ->
		# 	tecd, abst
		child1_code = self.code[:len(self.code) // 2] + chromosome.code[len(chromosome.code) // 2:]
		child2_code = chromosome.code[:len(chromosome.code) // 2] + self.code[len(self.code) // 2:]
		return list(map(lambda x : Chromosome(x), [child1_code, child2_code]))

	def mutate(self, chance, goal):
		if random.random() > chance: return

		costly_idx = -1
		costly_value = 0
		for i in range(0, len(self.code)):
			value = alphabet.index(self.code[i]) - alphabet.index(goal[i])
			if value * value > costly_value:
				costly_value = value * value
				costly_idx = i

		if costly_idx == -1: return

		self.code = self.code[:costly_idx] + random.choice(alphabet) + self.code[costly_idx + 1:]

class Population:

	def __init__(self, goal, size, mutation_chance):
		self.members = []
		self.goal = goal
		self.mutation_chance = mutation_chance
		self.generation_num = 0
		self.goal_reached = False
		self._size = size
		self._keep_best = True
		self._best_offset = 1 if self._keep_best else 0

		for i in range(0, self._size):
			self.members.append(Chromosome.random(len(goal)))

	def next_gen(self):
		# calculate cost of each chromosome
		for chromosome in self.members:
			chromosome.calc_cost(self.goal)

		# sort chromosomes by cost (lowest cost first)
		self.members.sort(key=lambda x: x.cost)

		# print generation
		print("gen {}".format(self.generation_num))
		print(self.members)

		# check if goal is reached
		for chromosome in self.members:
			if chromosome.code == self.goal:
				self.goal_reached = True
				return

		# mate two best childs
		childs = self.members[0].mate(self.members[1])

		# replace two worst childs with new best ones
		self.members = self.members[:len(self.members) - len(childs)] + childs

		# mate each chromosome with best one
		upd_members = []
		if self._keep_best: upd_members.append(self.members[0])
		for chromosome in self.members[1:len(self.members) // 2 + 1]:
			childs = self.members[0].mate(chromosome)
			upd_members += childs
		self.members = upd_members

		# mutate some chromosomes with a given chanse (0.0 to 1.0) and calculate cost
		for chromosome in self.members[self._best_offset:]:
			chromosome.mutate(self.mutation_chance, self.goal)
			chromosome.calc_cost(self.goal)

		self.generation_num += 1
		# sleep(1)

def main():
	goal = options.goal
	population_size = options.size
	mutation_chance = options.mutation

	if not goal:
		parser.error('Goal is not set')
	p = Population(goal, population_size, mutation_chance)
	print("goal: {}, population size: {}, mutation chance: {}".format(goal, population_size, mutation_chance))
	while p.goal_reached == False: 
		p.next_gen()

if __name__ == "__main__":
	main()