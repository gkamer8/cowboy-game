from scipy.optimize import fsolve

# https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fsolve.html#scipy.optimize.fsolve

# Create lookup table to keep track of variables
lu = {} 
for i in range(5):
    for k in range(5):
        # No variables in a 4, 0 or 0, 4 count
        if not(i == 0 and k == 4 or i == 4 and k == 0):
            lu['EV_' + str(i) + str(k)] = len(lu)
            lu['R_' + str(i) + str(k)] = len(lu)
            # Only include shield when opponent has > 0
            if k > 0:
                lu['X_' + str(i) + str(k)] = len(lu)
            # Only include shoot when you have > 0
            if i > 0:
                lu['S_' + str(i) + str(k)] = len(lu)

def func(x):
    # xcp[k] refers to an element of x or a constant in {0, 1, -1}, including all combos ([0-6), [0-6))
    xcp = {}  # "x copy"
    for i in range(-1, 6):
        for k in range(-1, 6):
            if 'EV_' + str(i) + str(k) in lu:
                xcp['EV_' + str(i) + str(k)] = x[lu['EV_' + str(i) + str(k)]]
            elif i == 5 and k == 5:
                xcp['EV_' + str(i) + str(k)] = x[lu['EV_00']]
            elif i == 5:
                xcp['EV_' + str(i) + str(k)] = 1
            elif k == 5:
                xcp['EV_' + str(i) + str(k)] = -1
            elif i == 4 and k == 0:
                xcp['EV_' + str(i) + str(k)] = 1
            elif i == 0 and k == 4:
                xcp['EV_' + str(i) + str(k)] = -1
            else:
                xcp['EV_' + str(i) + str(k)] = 0

            # Note: the following code creates some unused variables in counts containing 5
            
            for move in ['R_', 'X_', 'S_']:
                if move + str(i) + str(k) in lu:
                    xcp[move + str(i) + str(k)] = x[lu[move + str(i) + str(k)]]
                else:
                    xcp[move + str(i) + str(k)] = 0

    m = []

    for i in range(5):
        for k in range(5):
            if i == 0 and k == 4 or i == 4 and k == 0:
                continue

            # Reload
            m.append(
                # Reload
                xcp['EV_' + str(i+1) + str(k+1)] * xcp['R_' + str(k) + str(i)] +
                # Shield
                xcp['EV_' + str(i+1) + str(k)] * xcp['X_' + str(k) + str(i)] +
                # Shoot
                (-1) * xcp['S_' + str(k) + str(i)] +
                # Minus EV
                (-1) * xcp['EV_' + str(i) + str(k)]
            )

            # Shield
            if k > 0:
                m.append(
                    # Reload
                    xcp['EV_' + str(i) + str(k+1)] * xcp['R_' + str(k) + str(i)] +
                    # Shield
                    xcp['EV_' + str(i) + str(k)] * xcp['X_' + str(k) + str(i)] +
                    # Shoot
                    xcp['EV_' + str(i) + str(k-1)] * xcp['S_' + str(k) + str(i)] +
                    # Minus EV
                    (-1) * xcp['EV_' + str(i) + str(k)]
                )
            # Shoot
            if i > 0:
                m.append(
                    # Reload
                    (1) * xcp['R_' + str(k) + str(i)] +
                    # Shield
                    xcp['EV_' + str(i-1) + str(k)] * xcp['X_' + str(k) + str(i)] +
                    # Shoot
                    xcp['EV_' + str(i-1) + str(k-1)] * xcp['S_' + str(k) + str(i)] +
                    # Minus EV
                    (-1) * xcp['EV_' + str(i) + str(k)]
                )

            # All equal to one
            eq = -1
            if i != 0:
                eq += xcp['S_' + str(i) + str(k)]
            if k != 0:
                eq += xcp['X_' + str(i) + str(k)]
            eq += xcp['R_' + str(i) + str(k)]
            m.append(eq)

    return m

guesses = [1/3 for _ in range(len(lu))]
for i in range(5):
    guesses[lu['EV_' + str(i) * 2]] = 0
root = fsolve(func, guesses, factor=.01)

for key in lu:
    print(key + '\t' + ': ' + str(round(root[lu[key]], 3)))
