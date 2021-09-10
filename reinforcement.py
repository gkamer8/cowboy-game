from genetic import CPU, faceoff
import numpy as np

class Reinforced(CPU):

    def __init__(self, probs=None):
        super().__init__(probs=probs)
        self.move_history = []  # List of tuples with (my_bullet_count, opponent_bullet_count, move)
    
    def get_move(self, player, cpu):
        choice = np.random.choice(['R', 'X', 'S'], p=[self.reload[cpu][player], self.shield[cpu][player], self.shoot[cpu][player]])
        self.move_history.append((cpu, player, choice))
        return choice

    # Win is boolean set to true if it's reinforcing a win
    # Delta = change in choice probability (absolute percentage points)
    def reinforce(self, win, delta=.02):
        move_dicts = {'R': self.reload, 'X': self.shield, 'S': self.shoot}
        inverse_moves = {'R': [self.shield, self.shoot], 'X': [self.reload, self.shoot], 'S': [self.reload, self.shield]}
        if not win:
            delta *= -1
        for cpu, player, move in self.move_history:
            inverse_moves[move][0][cpu][player] -= delta
            inverse_moves[move][1][cpu][player] -= delta
            # print(f"Mv: {move}, CPU: {cpu}, Play: {player}, Del: {delta}, P: {move_dicts[move][cpu][player]}")
            continue

        # Make zero all that should be zero (and all that is negative)
        for x in range(5):
            for y in range(5):
                for mv in move_dicts:
                    move_dicts[mv][x][y] = max(0, move_dicts[mv][x][y])
            self.shoot[0][x] = 0
            self.shield[x][0] = 0

        # Normalize to 1
        for x in range(5):
            for y in range(5):
                new_r = self.reload[x][y] / (self.reload[x][y] + self.shoot[x][y] + self.shield[x][y])
                new_x = self.shield[x][y] / (self.reload[x][y] + self.shoot[x][y] + self.shield[x][y])
                self.reload[x][y] = new_r
                self.shield[x][y] = new_x
                self.shoot[x][y] = max(0, 1 - new_r - new_x)
        self.move_history = []

if __name__ == '__main__':
    CPU1 = Reinforced()
    CPU2 = Reinforced()
    rounds = 20_000
    speak = 1000
    results = 0
    CPU1.show_probs()
    for x in range(rounds):
        if x % speak == 0:
            print("Round: " + str(x))
        result = faceoff(CPU1, CPU2)
        results += result
        CPU2.reinforce(result)
        CPU1.reinforce(not result)
    CPU1.show_probs()
    CPU2.show_probs()
    print("Win % of CPU2: " + str(results / rounds))
        