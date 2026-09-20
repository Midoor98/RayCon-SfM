"""Plot a visibility matrix from actual public-demo track output."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--input", type=Path, required=True, help="tracks.json from the demo")
parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "docs/assets/demo-preview.png")
args = parser.parse_args()
tracks = json.loads(args.input.read_text())
if not tracks:
    parser.error("preview needs at least one accepted track")
images = sorted({o["image_id"] for track in tracks for o in track["observations"]})
matrix = [[int(image in {o["image_id"] for o in track["observations"]}) for image in images] for track in tracks]
plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": "#e6efff", "axes.labelcolor": "#a3b5d3",
                     "xtick.color": "#91a5c7", "ytick.color": "#91a5c7", "axes.edgecolor": "#34415b"})
fig = plt.figure(figsize=(14, 6), facecolor="#0b1222")
ax = fig.add_axes([0.09, 0.23, 0.54, 0.53], facecolor="#0b1222")
ax.imshow(matrix, aspect="auto", cmap=ListedColormap(["#172339", "#ae86ff"]), vmin=0, vmax=1, interpolation="nearest")
ax.set_xticks(range(len(images)), images)
ax.set_yticks(range(len(tracks)), [t["track_id"] for t in tracks], fontsize=8)
ax.set_xlabel("Image identifier")
ax.set_ylabel("Accepted feature track")
fig.text(0.055, 0.90, "RayCon-SfM  /  Track inspection", fontsize=21, weight="bold")
fig.text(0.055, 0.835, "Synthetic correspondences. Colored cells indicate an associated observation.", fontsize=11, color="#91a5c7")
fig.text(0.73, 0.65, str(len(tracks)), fontsize=46, color="#bc9cff", weight="bold")
fig.text(0.73, 0.59, "ACCEPTED TRACKS", fontsize=10, color="#91a5c7")
fig.text(0.73, 0.43, str(len(images)), fontsize=30, color="#77e6cf")
fig.text(0.73, 0.37, "INPUT IMAGE IDS", fontsize=10, color="#91a5c7")
fig.text(0.055, 0.055, "PUBLIC PREVIEW v0.1.0     /     GRAPH ASSOCIATION UTILITIES     /     NO 3D RECONSTRUCTION", fontsize=10, color="#77e6cf")
args.output.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(args.output, dpi=140, facecolor=fig.get_facecolor())
plt.close(fig)
print(args.output)
