import numpy as np

rng = np.random.default_rng(42)
t = np.sort(rng.uniform(0, 100, 1000))  # 1000 événements sur 100 s -> moyenne = 10/s


import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5), sharex=True)

ax1.eventplot(t, linelengths=0.8)
ax1.set_yticks([])
ax1.set_title("1000 événements uniformes sur 100 s")

ax2.hist(t, bins=100)  # fenêtres de 1 s
ax2.axhline(10, color="r", ls="--", label="moyenne (10/s)")
ax2.set_xlabel("temps (s)")
ax2.set_ylabel("événements / s")
ax2.legend()

plt.tight_layout()
plt.show()
