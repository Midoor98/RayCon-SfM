import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from tracks import build_tracks


def match(ia, fa, ib, fb):
    return dict(image_a=str(ia), feature_a=str(fa), image_b=str(ib), feature_b=str(fb))


class TrackTests(unittest.TestCase):
    def test_demo_components_and_conflict(self):
        with (ROOT / "data/pair_matches.csv").open(newline="", encoding="utf-8") as stream:
            tracks, rejected, summary = build_tracks(csv.DictReader(stream))
        self.assertEqual(len(tracks), 3)
        self.assertEqual(summary["duplicate_match_count"], 1)
        self.assertEqual(summary["track_length_histogram"], {"2": 1, "3": 1, "4": 1})
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0]["reason"], "multiple_features_in_one_image")
        self.assertEqual(len(rejected[0]["observations"]), 3)

    def test_transitive_association(self):
        tracks, rejected, _ = build_tracks([match(0, 7, 1, 8), match(1, 8, 2, 9)])
        self.assertEqual(rejected, [])
        self.assertEqual(tracks[0]["observations"], [dict(image_id=0, feature_id=7),
                                                     dict(image_id=1, feature_id=8),
                                                     dict(image_id=2, feature_id=9)])

    def test_deterministic_row_order(self):
        rows = [match(0, 7, 1, 8), match(1, 8, 2, 9), match(3, 0, 4, 0)]
        self.assertEqual(build_tracks(rows), build_tracks(list(reversed(rows))))

    def test_conflicts_reject_entire_component(self):
        tracks, rejected, _ = build_tracks([match(0, 0, 1, 0), match(1, 0, 0, 1)])
        self.assertEqual(tracks, [])
        self.assertEqual(len(rejected), 1)

    def test_min_views(self):
        tracks, rejected, _ = build_tracks([match(0, 0, 1, 0)], min_views=3)
        self.assertEqual(tracks, [])
        self.assertEqual(rejected[0]["reason"], "too_few_views")

    def test_invalid_input(self):
        for rows in ([], [match(0, 0, 0, 1)], [match(-1, 0, 1, 0)], [match(0.5, 0, 1, 0)]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                build_tracks(rows)
        with self.assertRaises(ValueError):
            build_tracks([match(0, 0, 1, 0)], min_views=1)


if __name__ == "__main__":
    unittest.main()
