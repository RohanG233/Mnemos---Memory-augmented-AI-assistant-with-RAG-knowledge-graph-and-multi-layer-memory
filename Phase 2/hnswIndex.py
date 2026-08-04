import numpy as np

def set_default_probas(M, m_L):
    nn = 0
    cum_nneighbor_per_level = []
    level = 0
    assign_probas = []

    while True:
        proba = np.exp(-level / m_L) * (1 - np.exp(-1 / m_L))
        if proba < 1e-9:
            break

        assign_probas.append(proba)
        nn += M * 2 if level == 0 else M
        cum_nneighbor_per_level.append(nn)
        level += 1

    return assign_probas, cum_nneighbor_per_level


def random_level(assign_probas, rng):
    f = rng.uniform()

    for level in range(len(assign_probas)):
        if f < assign_probas[level]:
            return level
        f -= assign_probas[level]

    return len(assign_probas) - 1


# ---------------- Main ----------------

M = 32
m_L = 1 / np.log(M)

assign_probas, _ = set_default_probas(M, m_L)

rng = np.random.default_rng()

level = random_level(assign_probas, rng)

print("Assigned Level:", level)