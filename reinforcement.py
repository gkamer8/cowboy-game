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
    def reinforce(self, win, delta=.005):
        move_dicts = {'R': self.reload, 'X': self.shield, 'S': self.shoot}
        inverse_dicts = {'R': [self.shield, self.shoot], 'X': [self.reload, self.shoot], 'S': [self.reload, self.shield]}
        for cpu, player, move in self.move_history:
            # Note: Never increase or decrease a zero
            if not win:
                delta *= -1
            if move_dicts[move][cpu][player] >= 1:
                continue

            move_dicts[move][cpu][player] += delta
            if move_dicts[move][cpu][player] >= 1:
                move_dicts[move][cpu][player] = 1
                inverse_dicts[move][0][cpu][player] = 0
                inverse_dicts[move][1][cpu][player] = 0
            elif move_dicts[move][cpu][player] <= 0:
                move_dicts[move][cpu][player] = 0
                inverse_dicts[move][0][cpu][player] = inverse_dicts[move][0][cpu][player] / (inverse_dicts[move][0][cpu][player] + inverse_dicts[move][1][cpu][player])
                inverse_dicts[move][1][cpu][player] = 1 - inverse_dicts[move][0][cpu][player]
            else:
                inverse_dicts[move][0][cpu][player] = (1 - move_dicts[move][cpu][player]) * (inverse_dicts[move][0][cpu][player] / (inverse_dicts[move][0][cpu][player] + inverse_dicts[move][1][cpu][player]))
                inverse_dicts[move][1][cpu][player] = 1 - move_dicts[move][cpu][player] - inverse_dicts[move][0][cpu][player]
            """
            adjustment = delta / 2  # Change for other two choices
            for inv in inverse_dicts[move]:
                if inv[cpu][player] - adjustment <= 0:
                    adjustment = delta
                else:
                    inv[cpu][player] -= adjustment

            move_dicts[move][cpu][player] = 1 - inverse_dicts[move][0][cpu][player] - inverse_dicts[move][1][cpu][player]  # Can't go above one
            """

if __name__ == '__main__':
    CPU1 = Reinforced()
    CPU2 = Reinforced()
    rounds = 500
    speak = 200
    results = 0
    for x in range(rounds):
        if x % speak == 0:
            print("Round: " + str(x))
        result = faceoff(CPU1, CPU2)
        results += result
        CPU2.reinforce(result)
        CPU1.reinforce(not result)
    CPU1.show_probs()
    print("Win % of CPU2: " + str(round(results / rounds)))
        