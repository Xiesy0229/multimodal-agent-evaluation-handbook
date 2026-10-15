Warning: fs was declared with const; use let for reassignable variables.
#!/usr/bin/env python3
"""Synthetic fixtures test the checker, not the quality of evaluation prompts."""

import copy
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

import validate_cases as checker


def png_bytes(color):
    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(b"\0" + bytes((color, 100, 120))))
        + chunk(b"IEND", b"")
    )


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.config = json.loads(checker.DEFAULT_CONFIG.read_text(encoding="utf-8"))
        self.refs = []
        for index in range(20):
            content = png_bytes(index)
            path = self.root / ("ref%02d.png" % index)
            path.write_bytes(content)
            self.refs.append({
                "index": index + 1, "asset_id": "fixture-%s" % index,
                "path": path.name, "sha256": hashlib.sha256(content).hexdigest(),
                "source_url": "https://example.org/synthetic-fixture",
                "source_repo": "", "role": "Synthetic test only",
                "license_note": "Self-created one-pixel test fixture, not an evaluation asset.",
                "rights_status": "cleared", "visual_check": "passed",
            })

    def one(self, index=0, nrefs=1, language="en", style="user_casual", shots=1):
        cap = "expression_physiology"
        prompt = "Fixture %s. A person smiles slowly while facing the camera." % index
        if style == "ultra_long":
            prompt += "\u5b57" * 2100
        words = len(checker.WORD_RE.findall(prompt)) if language == "en" else 100
        timeline = [
            {"start_s": part * 10 / shots, "end_s": (part + 1) * 10 / shots,
             "shot": part + 1, "event": "Synthetic event"}
            for part in range(shots)
        ]
        return {
            "id": "R2V-%03d" % (index + 1), "title": "Synthetic fixture",
            "input_modalities": ["text", "image"], "prompt": prompt,
            "language": language, "duration_s": 10, "task_type": "Synthetic fixture",
            "style": style, "shots": shots, "subject_tags": ["human"],
            "primary_capability": cap, "secondary_capabilities": [],
            "capability_evidence": {cap: "smiles slowly"}, "complexity": "simple",
            "word_count": words, "word_count_method": "synthetic-test-only" if language == "zh" else "english-regex",
            "length_label": "tiny" if words < 10 else "short" if words <= 30 else "long",
            "main_test": "Fixture only", "pass_criteria": ["Fixture passes"],
            "failure_signals": ["Fixture fails"], "daily_human": True, "handwriting": False,
            "timeline": timeline, "refs": copy.deepcopy(self.refs[:nrefs]),
            "boundary": {"is_boundary": nrefs > 10, "type": "type-%s" % nrefs if nrefs > 10 else ""},
            "source": {"type": "handwritten", "origin_url": "", "adaptation": "Self-created fixture"},
            "rewrite": {"used": False},
            "review": {
                "status": "passed", "reviewer": "synthetic-test", "mode": "single_agent",
                "notes": "Synthetic fixture; no actual human semantic review.",
                **{key: "passed" for key in self.config["review_dimensions"]},
            },
            "upload": {"status": "not_requested"},
        }

    def single_config(self, row):
        config = copy.deepcopy(self.config)
        config.update({
            "total_cases": 1, "pilot_cases": 1, "rewrite_cases": 0,
            "daily_human_minimum": 1,
            "boundary_cases": int(row["boundary"]["is_boundary"]),
            "distinct_boundary_types": int(row["boundary"]["is_boundary"]),
        })
        config["languages"] = {key: int(key == row["language"]) for key in config["languages"]}
        config["styles"] = {key: int(key == row["style"]) for key in config["styles"]}
        mode = "single" if row["shots"] == 1 else "multi"
        config["shot_modes"] = {key: int(key == mode) for key in config["shot_modes"]}
        config["reference_counts"] = {str(len(row["refs"])): 1}
        config["subject_minimums"] = {key: int(key in row["subject_tags"]) for key in config["subject_minimums"]}
        config["capability_minimums"] = {key: int(key == row["primary_capability"]) for key in config["capability_minimums"]}
        return config

    def result(self, row, require_uploaded=False):
        return checker.validate([row], self.single_config(row), self.root, require_uploaded=require_uploaded)

    def assert_bad(self, row, fragment, require_uploaded=False):
        result = self.result(row, require_uploaded)
        self.assertFalse(result["ok"], result)
        self.assertTrue(any(fragment in error for error in result["errors"]), result["errors"])

    def test_default_configuration(self):
        self.assertEqual(checker.config_errors(self.config), [])

    def test_valid_local_case_is_mechanical_only(self):
        result = self.result(self.one())
        self.assertTrue(result["ok"], result["errors"])
        self.assertTrue(result["mechanical_only"])
        self.assertEqual(result["verified_upload_cases"], 0)
        self.assertTrue(result["warnings"])

    def test_quota_mismatch(self):
        config = copy.deepcopy(self.config)
        config["reference_counts"]["1"] += 1
        self.assertTrue(any("sum" in e for e in checker.config_errors(config)))

    def test_duplicate_image_bytes(self):
        row = self.one(nrefs=2)
        row["refs"][1].update({
            "path": row["refs"][0]["path"], "sha256": row["refs"][0]["sha256"]
        })
        self.assert_bad(row, "duplicate image bytes")

    def test_missing_image(self):
        row = self.one()
        row["refs"][0]["path"] = "missing.png"
        self.assert_bad(row, ".path")

    def test_wrong_hash(self):
        row = self.one()
        row["refs"][0]["sha256"] = "0" * 64
        self.assert_bad(row, "does not match the actual file")

    def test_path_escape(self):
        row = self.one()
        row["refs"][0]["path"] = "../outside.png"
        self.assert_bad(row, "escapes")

    def test_video_disguised_as_image(self):
        row = self.one()
        (self.root / "video.png").write_bytes(b"\0\0\0 ftypmp42")
        row["refs"][0]["path"] = "video.png"
        self.assert_bad(row, "image header")

    def test_excluded_input_modality(self):
        row = self.one()
        row["input_modalities"].append("audio")
        self.assert_bad(row, "input_modalities")

    def test_unsupported_rights_status(self):
        row = self.one()
        row["refs"][0]["rights_status"] = "pending"
        self.assert_bad(row, "rights and visual review")

    def test_timeline_gap(self):
        row = self.one()
        row["timeline"][0]["start_s"] = 2
        self.assert_bad(row, "continuous")

    def test_nonfinite_timeline(self):
        row = self.one()
        row["timeline"][0]["end_s"] = float("nan")
        self.assert_bad(row, "finite")

    def test_ultra_length_valid_and_invalid(self):
        row = self.one(language="zh", style="ultra_long")
        self.assertTrue(self.result(row)["ok"])
        row["prompt"] = "smiles slowly" + "\u5b57" * 50
        self.assert_bad(row, "Han-character range")

    def test_evidence_missing_from_prompt(self):
        row = self.one()
        row["capability_evidence"]["expression_physiology"] = "not in this prompt"
        self.assert_bad(row, "verbatim")

    def test_duplicate_prompts(self):
        rows = [self.one(0), self.one(1)]
        rows[1]["prompt"] = " \n" + rows[0]["prompt"] + "  "
        result = checker.validate(rows, self.config, self.root, stage="draft")
        self.assertTrue(any("duplicate normalized prompt" in e for e in result["errors"]))

    def test_pilot_bands(self):
        rows = [
            self.one(index, nrefs, "zh" if index % 2 == 0 else "en",
                     "ultra_long" if index == 0 else "user_casual", 1 if index < 6 else 2)
            for index, nrefs in enumerate([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 20])
        ]
        rows[1]["handwriting"] = True
        rows[1]["primary_capability"] = "text_layout"
        rows[1]["capability_evidence"] = {"text_layout": "smiles slowly"}
        result = checker.validate(rows, self.config, self.root, stage="pilot")
        self.assertTrue(result["ok"], result["errors"])
        rows[-1]["refs"] = copy.deepcopy(self.refs[:18])
        result = checker.validate(rows, self.config, self.root, stage="pilot")
        self.assertTrue(any("missing reference-count band" in e for e in result["errors"]))

    def test_pending_review(self):
        row = self.one()
        row["review"]["ten_second_feasibility"] = "pending"
        self.assert_bad(row, "has not passed")

    def test_unverified_upload(self):
        self.assert_bad(self.one(), "verified upload is required", require_uploaded=True)

    def test_fake_complete_upload(self):
        row = self.one(nrefs=2)
        row["upload"] = {"status": "verified", "target": "Sheet", "verified_by": "tester", "remote_images": []}
        self.assert_bad(row, "remote image count")

    def test_valid_remote_mapping(self):
        row = self.one(nrefs=2)
        row["upload"] = {
            "status": "verified", "target": "Sheet", "verified_by": "tester",
            "remote_images": [
                {"index": ref["index"], "asset_id": ref["asset_id"], "location": "Sheet!image-%s" % ref["index"]}
                for ref in row["refs"]
            ],
        }
        self.assertTrue(self.result(row, require_uploaded=True)["ok"])
        row["upload"]["remote_images"].reverse()
        self.assert_bad(row, "remote order", require_uploaded=True)

    def test_malformed_nested_values_do_not_crash(self):
        row = self.one()
        for key in ("review", "rewrite", "source", "upload", "boundary"):
            bad = copy.deepcopy(row)
            bad[key] = []
            result = checker.validate([bad], self.single_config(row), self.root)
            self.assertFalse(result["ok"])
        result = checker.validate([None, {"refs": [None]}], self.config, self.root)
        self.assertFalse(result["ok"])

    def test_real_default_150_quota_matrix(self):
        ref_counts = [int(n) for n, count in self.config["reference_counts"].items() for _ in range(count)]
        styles = [style for style, count in self.config["styles"].items() for _ in range(count)]
        subjects = list(self.config["subject_minimums"])
        caps = list(self.config["capability_minimums"])
        rows = []
        for index in range(150):
            language = "en" if index < 75 else "zh"
            row = self.one(index, ref_counts[index], language, styles[index], 1 if index < 75 else 2)
            cap = caps[index % len(caps)]
            row["primary_capability"] = cap
            row["capability_evidence"] = {cap: "smiles slowly"}
            row["subject_tags"] = list(dict.fromkeys(["human", subjects[index % len(subjects)]]))
            if index < 6:
                row["rewrite"] = {
                    "used": True, "method": "custom_skill", "source": "synthetic-test",
                    "version": "1", "before": "Before fixture", "after": row["prompt"],
                    "evidence": "Synthetic code-path test only",
                }
            rows.append(row)
        result = checker.validate(rows, self.config, self.root)
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["case_count"], 150)
        self.assertEqual(sum(result["counts"]["boundary_types"].values()), 9)
        self.assertEqual(sum(int(k) * v for k, v in result["counts"]["reference_counts"].items()), 686)
        rows[-1]["refs"] = rows[-1]["refs"][:-1]
        result = checker.validate(rows, self.config, self.root)
        self.assertFalse(result["ok"])

    def test_loader_jsonl_and_invalid_input(self):
        path = self.root / "cases.jsonl"
        path.write_text(json.dumps(self.one()) + "\n\n", encoding="utf-8")
        self.assertEqual(len(checker.load_cases(path)), 1)
        path.write_text("{broken}\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            checker.load_cases(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
