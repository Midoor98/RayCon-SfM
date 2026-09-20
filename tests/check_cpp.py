"""Cross-check the standalone C++ public preview against its Python utility."""
import csv
import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BINARY = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT / "src"))

def call(source, output, *extra):
    return subprocess.run([str(BINARY), "--input", str(source), "--output", str(output), *extra],
                          text=True, capture_output=True)

with tempfile.TemporaryDirectory(prefix="raycon-cpp-check-") as directory:
    temporary = Path(directory)
    version = subprocess.run([str(BINARY), "--version"], text=True, capture_output=True, check=True)
    assert "0.1.0" in version.stdout
    from tracks import build_tracks
    source = ROOT / "data/pair_matches.csv"
    output = temporary / "default"
    result = call(source, output)
    assert result.returncode == 0, result.stderr
    with source.open() as stream:
        expected, rejected, summary = build_tracks(csv.DictReader(stream))
    assert json.loads((output / "tracks.json").read_text()) == expected
    assert json.loads((output / "rejected.json").read_text()) == rejected
    actual = json.loads((output / "summary.json").read_text())
    for key in summary:
        if key != "backend":
            assert actual[key] == summary[key], key
    empty = temporary / "filtered"
    assert call(source, empty, "--min-views", "10").returncode == 0
    assert json.loads((empty / "tracks.json").read_text()) == []
    invalid_samples = [
        "image_a,feature_a,image_b,feature_b\n",
        "image_a,feature_a,image_b,feature_b\n0,0,0,1\n",
        "image_a,feature_a,image_b,feature_b\n-1,0,1,1\n",
        "image_a,feature_a,image_b,feature_b\n0.5,0,1,1\n",
        "image_a,feature_a,image_b,feature_b\n0,nan,1,1\n",
    ]
    before = {p.name: p.read_bytes() for p in output.iterdir()}
    assert call(source, output).returncode != 0
    assert before == {p.name: p.read_bytes() for p in output.iterdir()}
    for i, content in enumerate(invalid_samples + ["wrong,header\n1,2\n"]):
        bad = temporary / f"bad-{i}.csv"
        bad.write_text(content)
        destination = temporary / f"bad-output-{i}"
        assert call(bad, destination).returncode != 0
        assert not destination.exists()
print("PASS: C++/Python agreement, custom input, invalid input, output preservation, version")
