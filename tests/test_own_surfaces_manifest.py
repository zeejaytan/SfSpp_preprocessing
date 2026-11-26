"""Ticket 09: the own-surface manifest must describe exactly the regenerated run.

Stdlib unittest only, so the check runs anywhere the repo is checked out.  The manifest
lives at sfs_axes/own_surfaces.json and is the one record of which directories the frozen
Ticket 03 extraction had to draw on for the 157 own-surface pieces.
"""
import json
import os
import re
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, os.pardir, "sfs_axes", "own_surfaces.json")

POTS = list("ABCDEFGHIJ")
VESSEL_KEYS = POTS + ["JUGLET_DEF3X"]
POT_COUNTS = {"A": 8, "B": 9, "C": 4, "D": 29, "E": 31, "F": 7, "G": 7,
              "H": 11, "I": 30, "J": 12}
JUG_COUNT = 9
COMMIT = "a50f8cc0ebe17621e2ce32424808c7414c2d7bbf"
STALE = ("t305-lane", "t66-admitsign", "t80-default-on", "out_poth")
RUN_TAG = "_t09-own-surfaces"


def load():
    with open(MANIFEST) as fh:
        return json.load(fh)


class ManifestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load()

    def test_top_level_keys(self):
        for k in ("run_id", "run_root", "preprocessing_commit", "binaries_sha256",
                  "sfs_dedupe", "sfs_wall_pair_filter", "total_pieces",
                  "total_walls", "duplicate_xyz", "vessels",
                  "axes_own_regen", "axes_juglet_def3x_regen"):
            self.assertIn(k, self.m)

    def test_commit_is_full_sha1(self):
        self.assertEqual(self.m["preprocessing_commit"], COMMIT)
        self.assertRegex(self.m["preprocessing_commit"], r"^[0-9a-f]{40}$")

    def test_binary_hashes_are_sha256(self):
        hashes = self.m["binaries_sha256"]
        self.assertEqual(sorted(hashes), ["EdgeLineExtractionHeadless",
                                          "MeshPreprocessingHeadless"])
        for name, h in hashes.items():
            self.assertRegex(str(h), r"^[0-9a-f]{64}$", name)

    def test_switches(self):
        self.assertEqual(self.m["sfs_dedupe"], "off")
        self.assertEqual(self.m["sfs_wall_pair_filter"], "default_on")

    def test_vessel_keys(self):
        self.assertEqual(sorted(self.m["vessels"]), sorted(VESSEL_KEYS))

    def test_piece_counts(self):
        v = self.m["vessels"]
        for P in POTS:
            self.assertEqual(int(v[P]["pieces"]), POT_COUNTS[P], P)
        self.assertEqual(int(v["JUGLET_DEF3X"]["pieces"]), JUG_COUNT)
        total = sum(int(x["pieces"]) for x in v.values())
        self.assertEqual(total, 157)
        self.assertEqual(int(self.m["total_pieces"]), 157)

    def test_walls_and_duplicates(self):
        self.assertEqual(int(self.m["total_walls"]), 314)
        self.assertEqual(int(self.m["duplicate_xyz"]), 0)

    def test_units_per_mm(self):
        v = self.m["vessels"]
        for P in POTS:
            self.assertEqual(float(v[P]["units_per_mm"]), 1.0, P)
        self.assertEqual(float(v["JUGLET_DEF3X"]["units_per_mm"]), 3.0)

    def test_paths_under_run_root(self):
        root = self.m["run_root"]
        paths = [self.m["axes_own_regen"], self.m["axes_juglet_def3x_regen"]]
        paths += [v["geom_dir"] for v in self.m["vessels"].values()]
        self.assertEqual(len(paths), 13)  # 2 axes dirs + 11 vessel geom dirs
        for p in paths:
            self.assertTrue(p.startswith(root), p)
            self.assertIn(RUN_TAG, p, p)

    def test_axes_dirs_named(self):
        self.assertTrue(self.m["axes_own_regen"].endswith("/out/axes09_own_regen"))
        self.assertTrue(self.m["axes_juglet_def3x_regen"]
                        .endswith("/out/axes09_juglet_def3x_regen"))

    def test_no_stale_run_references(self):
        blob = json.dumps(self.m)
        for s in STALE:
            self.assertNotIn(s, blob)

    def test_run_id_matches_root(self):
        self.assertEqual(self.m["run_id"],
                         os.path.basename(self.m["run_root"].rstrip("/")))
        self.assertRegex(self.m["run_id"], r"^\d{8}-\d{4}_[0-9a-f]{7}_t09-own-surfaces$")


if __name__ == "__main__":
    unittest.main()
