"""Public feature-track organization only; no camera or structure solver."""

import argparse
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def nonnegative_int(value):
    number = int(value)
    if number < 0:
        raise ValueError("image and feature identifiers must be nonnegative integers")
    return number


def build_tracks(rows, min_views=2):
    """Build connected components; discard entire components with image conflicts."""
    if not isinstance(min_views, int) or min_views < 2:
        raise ValueError("min_views must be an integer of at least two")
    adjacency = {}
    edges = set()
    count = duplicates = 0
    for row in rows:
        a = (nonnegative_int(row["image_a"]), nonnegative_int(row["feature_a"]))
        b = (nonnegative_int(row["image_b"]), nonnegative_int(row["feature_b"]))
        if a[0] == b[0]:
            raise ValueError("a correspondence must connect different images")
        count += 1
        edge = tuple(sorted((a, b)))
        if edge in edges:
            duplicates += 1
            continue
        edges.add(edge)
        adjacency.setdefault(a, set()).add(b)
        adjacency.setdefault(b, set()).add(a)
    if not count:
        raise ValueError("input contains no correspondences")
    visited, accepted, rejected = set(), [], []
    for seed in sorted(adjacency):
        if seed in visited:
            continue
        stack, component = [seed], []
        visited.add(seed)
        while stack:
            node = stack.pop()
            component.append(node)
            for neighbor in sorted(adjacency[node]):
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)
        component.sort()
        observations = [{"image_id": image, "feature_id": feature}
                        for image, feature in component]
        image_ids = [node[0] for node in component]
        if len(image_ids) != len(set(image_ids)):
            rejected.append({"reason": "multiple_features_in_one_image", "observations": observations})
        elif len(component) < min_views:
            rejected.append({"reason": "too_few_views", "observations": observations})
        else:
            accepted.append({"track_id": len(accepted), "observations": observations})
    histogram = Counter(len(track["observations"]) for track in accepted)
    summary = {"mode": "public-demo", "backend": "feature_graph_connected_components",
               "input_match_count": count, "unique_match_count": len(edges),
               "duplicate_match_count": duplicates, "input_image_count": len({p[0] for p in adjacency}),
               "accepted_track_count": len(accepted), "rejected_component_count": len(rejected),
               "track_length_histogram": {str(k): histogram[k] for k in sorted(histogram)},
               "min_views": min_views, "camera_estimation": False, "point_triangulation": False}
    return accepted, rejected, summary


def main():
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    version = (root / "VERSION").read_text(encoding="utf-8").strip()
    parser.add_argument("--version", action="version", version=f"RayCon-SfM public preview {version}")
    parser.add_argument("--input", type=Path, default=root / "data/pair_matches.csv")
    parser.add_argument("--min-views", type=int, default=2)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        with args.input.open(newline="", encoding="utf-8") as stream:
            rows = list(csv.DictReader(stream))
        tracks, rejected, summary = build_tracks(rows, args.min_views)
        summary["version"] = version
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        output = args.output or root / "result" / stamp
        output.mkdir(parents=True, exist_ok=False)
        for filename, data in (("tracks.json", tracks), ("rejected.json", rejected), ("summary.json", summary)):
            (output / filename).write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        with (output / "visibility.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=["track_id", "image_id", "feature_id"])
            writer.writeheader()
            for track in tracks:
                for observation in track["observations"]:
                    writer.writerow({"track_id": track["track_id"], **observation})
        print(json.dumps(summary, ensure_ascii=False))
        print(f"Output: {output}")
    except (OSError, ValueError, KeyError, TypeError, csv.Error) as exc:
        parser.exit(2, f"Input/output error: {exc}\n")


if __name__ == "__main__":
    main()
