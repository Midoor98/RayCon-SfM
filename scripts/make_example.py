"""Generate a deterministic synthetic feature-association fixture."""
import csv
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "data/showcase_matches.csv"
rows = []
for track in range(16):
    views = [image for image in range(8) if (image + track) % 5 != 0]
    for first, second in zip(views, views[1:]):
        rows.append((first, track * 10 + first, second, track * 10 + second))
rows.append(rows[0])
rows.extend([(0, 900, 1, 901), (1, 901, 0, 902)])
with path.open("w", newline="", encoding="utf-8") as stream:
    writer = csv.writer(stream)
    writer.writerow(["image_a", "feature_a", "image_b", "feature_b"])
    writer.writerows(rows)
print(path.name, "written; synthetic fixture only")
