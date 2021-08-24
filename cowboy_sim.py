import gametheory
import numpy as np

root, lu = gametheory.solution(talk = False)

# Computer probabilities
reload = [[0 for _ in range(5)] for _ in range(5)]
shield = [[0 for _ in range(5)] for _ in range(5)]
shoot = [[0 for _ in range(5)] for _ in range(5)]

for key in lu:
    if key[0] == 'R':
        reload[int(key[2])][int(key[3])] = root[lu[key]]
    elif key[0] == 'X':
        shield[int(key[2])][int(key[3])] = root[lu[key]]
    elif key[0] == 'S':
        shoot[int(key[2])][int(key[3])] = root[lu[key]]

# Computer plays move given game state with cpu count second
def cpu_play(player, cpu):
    choice = np.random.choice(["R", "X", "S"], p=[reload[cpu][player], shield[cpu][player], shoot[cpu][player]])
    return choice

# Interactive play vs. CPU
# Returns 0 if player wins, 1 if CPU wins
# double_cpu is not None if two cpus are playing each other (takes function like cpu_play)
def play_game(quiet=False, double_cpu=None):
    player = 0
    cpu = 0
    while True:
        if not double_cpu:
            move = input("(R)eload, Shield (X), or (S)hoot?: ").upper()
        else:
            move = double_cpu(cpu, player)

        if move not in ["R", "S", "X"]:
            if not quiet:
                print("Move not recognized.")
            continue
        cpu_move = cpu_play(player, cpu)
        if not quiet:
            print("CPU plays " + cpu_move)
        if cpu_move == "S" and move == 'R':
            if not quiet:
                print("CPU wins!")
            return 1
        elif move == "S" and cpu_move == "S":
            if not quiet:
                print("Player wins!")
            return 0

        if cpu_move == "R":
            cpu += 1
        elif cpu_move == 'S':
            cpu -= 1

        if move == 'R':
            player += 1
        elif move == 'S':
            player -= 1
        
        if cpu == 5 and player == 5:
            cpu = 0
            player = 0
        elif cpu == 5:
            if not quiet:
                print("CPU wins!")
            return 1
        elif player == 5:
            if not quiet:
                print("Player wins!")
            return 0
        elif player == 0 and cpu == 4:
            if not quiet:
                print("CPU wins!")
            return 1
        elif player == 4 and cpu == 0:
            if not quiet:
                print("Player wins!")
            return 0

        if not quiet:
            print("Count: " + str(player) + "-" + str(cpu))

def only_reload_cpu(player, cpu):
    return "R"

# Always reloads unless it can shoot, in which case it shoots
def reload_shoot_cpu(player, cpu):
    if cpu > 0:
        return "S"
    return "R"

# Plays legal moves at random
def random_cpu(player, cpu):
    if cpu > 0:
        return np.random.choice(['R', 'X', 'S'])
    else:
        return np.random.choice(['R', 'X'])

# Returns win rate of optimal CPU
def double_cpu(cpu_function, games=10000, quiet=False):
    records = []
    for _ in range(games):
        result = play_game(quiet=True, double_cpu=cpu_function)
        records.append(result)
    
    optimal = sum(records)/games
    if not quiet:
        print("Optimal CPU W%: " + str(optimal))
    return optimal

if __name__ == "__main__":
    print("vs. Only Reload: ")
    print(double_cpu(only_reload_cpu, quiet=True))

    print("vs. Reload-Shoot: ")
    print(double_cpu(reload_shoot_cpu, quiet=True))

    print("vs. Random: ")
    print(double_cpu(random_cpu, quiet=True))