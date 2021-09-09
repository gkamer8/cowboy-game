from genetic import CPU
import numpy as np

class Reinforced(CPU):

    def __init__(self, probs=None):
        super().__init__(props=probs)
        move_history = []  # List of tuples with (my_bullet_count, opponent_bullet_count, move)
    
    def get_move(self, player, cpu):
        choice = np.random.choice(['R', 'X', 'S'], p=[self.reload[cpu][player], self.shield[cpu][player], self.shoot[cpu][player]])
        self.move_history.append((cpu, player, choice))

    # Win is boolean set to true if it's reinforcing a win
    # Delta = change in choice probability (absolute percentage points)
    def reinforce(self, win, delta=.02):
        move_dicts = {'R': self.reload, 'X': self.shield, 'S': self.shoot}
        inverse_dicts = {'R': [self.shield, self.shoot], 'X': [self.reload, self.shoot], 'S': [self.reload, self.shield]}
        for cpu, player, move in self.move_history:
            # Note: Never increase or decrease a zero
            if not win:
                delta *= -1

            adjustment = delta  # Change for other two choices
            for inv in inverse_dicts[move]:
                if inv[cpu, player] == 0:
                    adjustment *= 2
                else:
                    inv[cpu, player] -= adjustment / 2
            move_dicts[move] = min(move_dicts[move] + delta, 1)  # Can't go above one
