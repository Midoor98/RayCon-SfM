# RayCon-SfM · v0.1 companion tools: inputs and outputs

The companion tools included in v0.1 organize pairwise feature matches into tracks across images, reject conflicts and export a visibility table. This release does not include camera pose estimation, 3D point estimation or the RayCon optimization backend. The full image reconstruction pipeline is outside the scope of these tools; system trial-run code is planned for the next version.

## Run

Requires Python 3.10 or later, with no third-party dependencies. Run from the repository root:

```bash
bash run.sh
python3 -B -m unittest discover -s tests -v
```

To specify an input file:

```bash
python3 -B src/tracks.py --input data/pair_matches.csv --min-views 3 --output result/custom-run
```

The directory specified by `--output` must not already exist. If omitted, a new timestamped directory is created under `result/`. The minimum view count defaults to 2; the custom example above sets it to 3.

## Data and rules

`data/pair_matches.csv` contains hand-authored synthetic correspondences with columns `image_a,feature_a,image_b,feature_b`. Image IDs and feature IDs are nonnegative integers and need not be consecutive. Within an image, a feature ID must refer to the same feature across all match rows. The input contains no pixel coordinates, camera parameters or 3D coordinates, and the program does not read actual images.

Each image-ID/feature-ID pair is a node, and each match is an undirected edge. The tools compute connected components of this graph, counting duplicate edges only once. If a component contains multiple distinct features from the same image, the entire component is rejected and recorded without attempting a repair. The remaining components are filtered by the minimum view count.

Connectivity represents match associations and does not establish geometric correctness. The tools do not perform geometric verification, outlier estimation or triangulation. Nodes and components are sorted before export, so reordering the input rows does not change track IDs.

## Workflow and files

1. Validate IDs and cross-image match relationships.
2. Remove duplicate edges, construct the undirected graph and find connected components.
3. Reject conflicting or short tracks, then export associations and statistics.

| File | Purpose |
| --- | --- |
| `src/tracks.py` | Generic graph association, track organization and command-line entry point |
| `run.sh` | Shortcut for the synthetic example; forwards command-line arguments |
| `tests/test_tracks.py` | Checks for transitive associations, conflicts, deduplication and stable output |
| `result/<run-directory>/tracks.json` | Image and feature IDs for each accepted track |
| `result/<run-directory>/visibility.csv` | Visibility records in `track_id,image_id,feature_id` format |
| `result/<run-directory>/rejected.json` | Rejection reasons and the complete corresponding components |
| `result/<run-directory>/summary.json` | Match counts, duplicate counts, track counts and track-length distribution |

The default example contains 10 match rows, including one duplicate edge. It retains 3 tracks spanning 3, 4 and 2 views, and rejects one component with a same-image conflict. If all components are rejected, the tools still export empty tracks and statistics showing zero accepted tracks. These counts describe correspondence processing; they are not camera registration counts, reconstruction success rates or research accuracy results.

The C++ entry point uses the same data format and requires the header order shown in the example, with unquoted fields. Integer IDs must consist of decimal digits only. Run the default C++ example with `bash run_cpp.sh`.
