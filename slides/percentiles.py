import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

rng = np.random.default_rng(7)
N = 100
# latency-like distribution: most fast, long tail
data = np.clip(rng.lognormal(mean=3.6, sigma=0.55, size=N), 8, None)
data[-3:] = [150, 185, 230]  # a few outliers to make the tail obvious
rng.shuffle(data)
data = np.round(data).astype(int)
srt = np.sort(data)
mean = data.mean()

def pct(p):  # nearest-rank
    k = int(np.ceil(p / 100 * N))
    return k, srt[k - 1]

BG, STICK, DIM = "#0f172a", "#60a5fa", "#334155"
COLORS = {"p50": "#34d399", "p90": "#fbbf24", "p95": "#fb923c", "p99": "#f87171"}
YMAX = srt.max() * 1.15

frames, durations = [], []

def draw(vals, title, colors=None, mean_line=False, marks=(), subtitle=""):
    fig, ax = plt.subplots(figsize=(9, 4.6), dpi=90)
    fig.patch.set_facecolor(BG); ax.set_facecolor(BG)
    ax.bar(range(N), vals, width=0.8, color=colors if colors is not None else STICK)
    if mean_line:
        ax.axhline(mean, color="white", ls="--", lw=1.5)
        ax.text(1, mean + 4, f"mean = {mean:.1f} ms", color="white", fontsize=11, fontweight="bold")
    ypos = {"p50": 0.97, "p90": 0.97, "p95": 0.80, "p99": 0.63}
    for name, p in marks:
        k, v = pct(p)
        ax.axvline(k - 0.5, color=COLORS[name], lw=2)
        ax.axhline(v, color=COLORS[name], lw=1, ls=":")
        ax.text(k - 1.5, YMAX * ypos[name], f"{name}\n{v} ms", color=COLORS[name],
                ha="right", va="top", fontsize=11, fontweight="bold",
                bbox=dict(facecolor=BG, edgecolor="none", pad=1.5))
    ax.set_xlim(-1, N); ax.set_ylim(0, YMAX)
    ax.set_title(title, color="white", fontsize=14, loc="left", fontweight="bold")
    if subtitle:
        ax.text(0, -0.1, subtitle, transform=ax.transAxes, color="#94a3b8", fontsize=10)
    ax.set_xticks([]); ax.tick_params(colors="#94a3b8"); ax.set_ylabel("latency (ms)", color="#94a3b8")
    for s in ax.spines.values(): s.set_visible(False)
    fig.tight_layout()
    fig.canvas.draw()
    img = Image.fromarray(np.asarray(fig.canvas.buffer_rgba())[..., :3].copy())
    plt.close(fig)
    return img

def add(img, ms): frames.append(img); durations.append(ms)

# 1. unsorted
add(draw(data, "100 requests, in arrival order"), 1500)

# 2. sorting (bubble-sort snapshots, sped up)
arr = data.copy(); snaps = []
step = 0
for i in range(N):
    swapped = False
    for j in range(N - 1 - i):
        if arr[j] > arr[j + 1]:
            arr[j], arr[j + 1] = arr[j + 1], arr[j]; swapped = True
            step += 1
            if step % 90 == 0: snaps.append(arr.copy())
    if not swapped: break
for s in snaps:
    add(draw(s, "Sorting by latency..."), 70)
add(draw(srt, "Sorted"), 1200)

# 3. mean
add(draw(srt, "Mean = sum / N", mean_line=True,
         subtitle="Dragged up by the tail: most requests are faster than the mean."), 2500)

# 4. percentiles, cumulative
cols_base = [STICK] * N
shown = []
for name, p in [("p50", 50), ("p90", 90), ("p95", 95), ("p99", 99)]:
    shown.append((name, p))
    k, v = pct(p)
    cols = [COLORS[name] if i < k else DIM for i in range(N)]
    label = {"p50": "p50 (median): half of requests are at or below this",
             "p90": "p90: 90% of requests are at or below this",
             "p95": "p95: 95% of requests are at or below this",
             "p99": "p99: only 1 request in 100 is slower"}[name]
    add(draw(srt, label, colors=cols, mean_line=True, marks=shown,
             subtitle=f"{name} = {v} ms  (mean = {mean:.1f} ms)"), 2500)

# final summary
add(draw(srt, "Mean hides the tail; percentiles show it", mean_line=True, marks=shown), 3500)

frames[0].save("percentiles.gif", save_all=True, append_images=frames[1:],
               duration=durations, loop=0, optimize=True)
print(len(frames), "frames")
