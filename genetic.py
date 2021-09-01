import numpy as np
import random
from cowboy_sim import double_cpu

"""
Flow:

Generate n random CPUs

Play random games between them

Take the top p percent of CPUs

Randomly mate some together (take averages)??
---> actually, no, take draws from normal distribution centered around each probability

"""

def faceoff(cpu1, cpu2):
    cpu1_count = 0
    cpu2_count = 0
    turns = 0
    while True:
        turns += 1
        # After 100 turns, the game ends with a random victor
        if turns >= 100:
            return np.random.choice([0, 1])

        cpu1_move = cpu1.get_move(cpu2_count, cpu1_count)
        cpu2_move = cpu2.get_move(cpu1_count, cpu2_count)

        # Death
        if cpu1_move == 'R' and cpu2_move == 'S':
            return 1
        if cpu2_move == 'R' and cpu1_move == 'S':
            return 0
        
        # Reloads
        if cpu2_move == 'R':
            cpu2_count += 1
        if cpu1_move == 'R':
            cpu1_count += 1
        
        # Shoots
        if cpu1_move == 'S':
            cpu1_count -= 1
        if cpu2_move == 'S':
            cpu2_count -= 1
        
        # 0, 4s
        if cpu1_count == 4 and cpu2_count == 0:
            return 0
        if cpu2_count == 4 and cpu1_count == 0:
            return 1
        
        # 5s
        if cpu1_count == 5 and cpu2_count == 5:
            cpu2_count = 0
            cpu1_count = 0
            continue
        elif cpu1_count == 5:
            return 0
        elif cpu2_count == 5:
            return 1

class CPU:

    # probs = list of reload, shield, and shoot
    def __init__(self, probs=None):

        if not probs:
            self.reload = [[0 for _ in range(5)] for _ in range(5)]
            self.shield = [[0 for _ in range(5)] for _ in range(5)]
            self.shoot = [[0 for _ in range(5)] for _ in range(5)]

            for x in range(5):
                for y in range(5):
                    self.reload[x][y] = random.random()
                    self.shoot[x][y] = random.random()
                    self.shield[x][y] = random.random()

                    total = self.reload[x][y] + self.shield[x][y] + self.shoot[x][y]
                    self.reload[x][y] /= total
                    self.shoot[x][y] /= total
                    self.shield[x][y] /= total

            for x in range(5):
                # Edge cases

                # C > 0, p = 0
                self.shield[x][0] = 0
                self.reload[x][0] = random.random()
                self.shoot[x][0] = 1 - self.reload[x][0]
            
                # C = 0, p > 0
                self.shoot[0][x] = 0
                self.reload[0][x] = random.random()
                self.shield[0][x] = 1 - self.reload[0][x]

                self.reload[0][0] = 1
                self.shield[0][0] = 0
                self.shoot[0][0] = 0
        else:
            self.reload = probs[0]
            self.shield = probs[1]
            self.shoot = probs[2]

    def get_move(self, player, cpu):
        return np.random.choice(['R', 'X', 'S'], p=[self.reload[cpu][player], self.shield[cpu][player], self.shoot[cpu][player]])

    # get n cpus representing the next generation
    def next_gen(self, n, std=.05):
        reloads = [[[0 for _ in range(5)] for _ in range(5)] for _ in range(n)]
        shields = [[[0 for _ in range(5)] for _ in range(5)] for _ in range(n)]
        shoots = [[[0 for _ in range(5)] for _ in range(5)] for _ in range(n)]

        for x in range(5):
            for y in range(5):
                
                if not (x == 0 and y == 0):
                    r_draws = np.random.normal(self.reload[x][y], std, n)
                else:
                    r_draws = [1 for _ in range(n)]

                if y > 0:
                    x_draws = np.random.normal(self.shield[x][y], std, n)
                else:
                    x_draws = [0 for _ in range(n)]

                if x > 0:
                    s_draws = np.random.normal(self.shoot[x][y], std, n)
                else:
                    s_draws = [0 for _ in range(n)]

                for i in range(n):
                    if r_draws[i] < 0:
                        r_draws[i] = 0
                    if x_draws[i] < 0:
                        x_draws[i] = 0
                    if s_draws[i] < 0:
                        s_draws[i] = 0

                    total = r_draws[i] + x_draws[i] + s_draws[i]
                    reloads[i][x][y] = r_draws[i] / total
                    shields[i][x][y] = x_draws[i] / total
                    shoots[i][x][y] = s_draws[i] / total

        return [CPU(probs=[reloads[i], shields[i], shoots[i]]) for i in range(n)]

# Returns unordered list of top x cpus
def tournament(cpus, x, rounds=100):

    # Bracket tournament
    round = list(cpus)
    while len(round) >= x * 2:
        # If round isn't even, double the first cpu
        if len(round) % 2 != 0:
            round.append(round[0])
        # Group up teams
        games = [[round[i], round[i + 1]] for i in range(0, len(round)-1, 2)]
        round = []
        for game in games:
            results = 0
            for _ in range(rounds):
                results += faceoff(game[0], game[1])
            if results/rounds > .5:
                round.append(game[1])
            else:
                round.append(game[0])
    return [round[i] for i in range(x)]

    """
    Old tournament:
    results = [0 for _ in range(len(cpus))]
    for i in range(len(cpus)):
        cpu = cpus[i]
        for _ in range(rounds):
            # note: it's possible for a cpu to play itself and to play other opponents many times
            oppo = random.randrange(len(cpus))
            res = faceoff(cpus[oppo], cpu)
            results[i] += res
            results[oppo] += 1 if res == 0 else 0


    combined = [[cpus[i], results[i]] for i in range(len(results))]
    combined_sorted = sorted(combined, key=lambda x: x[1], reverse=True)
    return [combined_sorted[i][0] for i in range(x)]
    """


# Returns list of n random CPU objects
def get_random_cpus(n):
    return [CPU() for _ in range(n)]


if __name__ == '__main__':

    # Generation size
    n = 256
    # Top x breed
    x = 16
    # Top x each have y offspring
    y = 16
    # Iterations
    iters = 1000

    cpus = get_random_cpus(n)
    for i in range(iters):
        print(f"Iter: {i + 1}")
        tops = tournament(cpus, x)
        # Generate next generation
        cpus = []
        for top in tops:
            cpus.extend(top.next_gen(y))

    # Test CPU from last generation against random CPUs
    results = []
    rand_cpus = get_random_cpus(10)
    for c in rand_cpus:
        for _ in range(1000):
            results.append(faceoff(c, cpus[0]))
    print("Win %: " + str(sum(results) / len(results)))

    print("Reload: " + str(cpus[0].reload))
    print("Shield: " + str(cpus[0].shield))
    print("Shoot: " + str(cpus[0].shoot))

    print("Win Rate of Optimal vs. CPU: ")
    print(double_cpu(cpus[0].get_move, quiet=True))