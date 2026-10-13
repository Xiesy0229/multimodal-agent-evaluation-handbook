Warning: fs was declared with const; use let for reassignable variables.
#!/usr/bin/env python3
"""Offline mechanical checks; not a substitute for image or semantic review."""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import unicodedata


DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "assets" / "default_config.json"
WORD_RE = re.compile(r"[A-Za-z]+(?:['\u2019][A-Za-z]+)*")
SHA_RE = re.compile(r"[0-9a-fA-F]{64}")
REWRITE_METHODS = {"product_skill", "public_template", "custom_skill"}
REVIEW_MODES = {"independent_agent", "independent_human", "single_agent"}


def integer(value, minimum=0):
    return isinstance(value, int) and not isinstance(value, bool) and value >= minimum


def number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def han_count(value):
    return sum(
        0x3400 <= ord(char) <= 0x4DBF
        or 0x4E00 <= ord(char) <= 0x9FFF
        or 0xF900 <= ord(char) <= 0xFAFF
        or 0x20000 <= ord(char) <= 0x2FFFF
        or 0x30000 <= ord(char) <= 0x323AF
        for char in value
    )


def normalized_prompt(value):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value)).casefold()


def load_cases(path):
    content = Path(path).read_text(encoding="utf-8-sig")
    if content.lstrip().startswith("["):
        data = json.loads(content)
        if not isinstance(data, list):
            raise ValueError("The input must be an array or JSONL objects.")
        return data
    records = []
    for line_no, line in enumerate(content.splitlines(), 1):
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError("Invalid JSONL at line %s: %s" % (line_no, exc.msg)) from exc
    return records


def config_errors(config):
    errors = []
    if not isinstance(config, dict):
        return ["Configuration must be an object."]
    total = config.get("total_cases")
    if not integer(total, 1):
        return ["total_cases must be a positive integer."]
    for name in ("languages", "shot_modes", "styles", "reference_counts"):
        counts = config.get(name)
        if not isinstance(counts, dict) or not counts:
            errors.append("%s must be a nonempty object." % name)
            continue
        if not all(isinstance(key, str) and integer(value) for key, value in counts.items()):
            errors.append("%s must contain string keys and nonnegative integer counts." % name)
            continue
        if sum(counts.values()) != total:
            errors.append("%s must sum to total_cases." % name)
    permitted = {
        "languages": {"zh", "en"},
        "shot_modes": {"single", "multi"},
        "styles": {"user_casual", "natural_detailed", "structured", "ultra_long"},
    }
    for key, allowed in permitted.items():
        values = config.get(key)
        if isinstance(values, dict) and set(values) != allowed:
            errors.append("%s must use exactly: %s." % (key, sorted(allowed)))
    for key in (
        "pilot_cases", "boundary_threshold", "boundary_cases",
        "distinct_boundary_types", "rewrite_cases", "daily_human_minimum", "max_shots",
    ):
        if not integer(config.get(key)):
            errors.append("%s must be a nonnegative integer." % key)
    for key in ("pilot_cases", "boundary_cases", "rewrite_cases", "daily_human_minimum"):
        if integer(config.get(key)) and config[key] > total:
            errors.append("%s cannot exceed total_cases." % key)
    if config.get("pilot_cases") == 0 or config.get("max_shots") == 0:
        errors.append("pilot_cases and max_shots must be positive.")
    if not number(config.get("duration_s")) or config["duration_s"] <= 0:
        errors.append("duration_s must be a positive finite number.")
    for key in ("subject_minimums", "capability_minimums"):
        values = config.get(key)
        if not isinstance(values, dict) or not values:
            errors.append("%s must be a nonempty object." % key)
        elif not all(text(k) and integer(v) and v <= total for k, v in values.items()):
            errors.append("%s contains invalid minima." % key)
    for key in ("source_types", "review_dimensions", "allowed_image_extensions"):
        values = config.get(key)
        if not isinstance(values, list) or not values or not all(text(v) for v in values):
            errors.append("%s must be a nonempty string list." % key)
        elif len(set(values)) != len(values):
            errors.append("%s contains duplicate values." % key)
    if not isinstance(config.get("upload_required"), bool):
        errors.append("upload_required must be boolean.")
    ultra = config.get("ultra_long")
    if not isinstance(ultra, dict):
        errors.append("ultra_long must be an object.")
    elif (
        ultra.get("language") != "zh"
        or not integer(ultra.get("min_han"), 1)
        or not integer(ultra.get("max_han"), 1)
        or ultra["min_han"] > ultra["max_han"]
    ):
        errors.append("ultra_long needs zh and a valid positive Han-character range.")
    refs = config.get("reference_counts")
    threshold = config.get("boundary_threshold")
    if isinstance(refs, dict) and integer(threshold):
        if not all(isinstance(k, str) and k.isdigit() and int(k) > 0 for k in refs):
            errors.append("reference_counts keys must be positive integer strings.")
        elif all(integer(v) for v in refs.values()):
            boundary = sum(v for k, v in refs.items() if int(k) > threshold)
            if boundary != config.get("boundary_cases"):
                errors.append("boundary_cases disagrees with reference_counts.")
    if integer(config.get("distinct_boundary_types")) and integer(config.get("boundary_cases")):
        if config["distinct_boundary_types"] > config["boundary_cases"]:
            errors.append("distinct_boundary_types cannot exceed boundary_cases.")
    return errors


def image_signature(header, suffix):
    if suffix in {".jpg", ".jpeg"}:
        return header.startswith(b"\xff\xd8\xff")
    if suffix == ".png":
        return header.startswith(b"\x89PNG\r\n\x1a\n")
    if suffix == ".webp":
        return header.startswith(b"RIFF") and header[8:12] == b"WEBP"
    return False


class Checker:
    def __init__(self, config, root, stage, require_uploaded):
        self.config = config
        self.root = Path(root).resolve()
        self.stage = stage
        self.require_uploaded = require_uploaded or config["upload_required"]
        self.errors = []
        self.warnings = []
        self.counts = {key: Counter() for key in (
            "languages", "shot_modes", "styles", "reference_counts",
            "subjects", "capabilities", "boundary_types",
        )}
        self.ids = set()
        self.prompts = {}
        self.asset_hashes = {}
        self.zh_methods = set()
        self.rewrites = 0
        self.daily = 0
        self.handwriting = 0
        self.single_agent_reviews = 0
        self.uploaded = 0
        self.prompt_metrics = []

    def error(self, at, message):
        self.errors.append("%s: %s" % (at, message))

    def object(self, value, at):
        if not isinstance(value, dict):
            self.error(at, "must be an object")
            return {}
        return value

    def string(self, value, at):
        if not text(value):
            self.error(at, "must be a nonempty string")
            return ""
        return value

    def strings(self, value, at, nonempty=False):
        if not isinstance(value, list) or not all(text(item) for item in value):
            self.error(at, "must be a list of nonempty strings")
            return []
        if nonempty and not value:
            self.error(at, "must not be empty")
        if len(value) != len(set(value)):
            self.error(at, "contains duplicates")
        return value

    def enum(self, value, allowed, at):
        if not isinstance(value, str) or value not in allowed:
            self.error(at, "invalid value")
            return None
        return value

    def timeline(self, value, shots, at):
        if not isinstance(value, list) or not value:
            self.error(at, "must be a nonempty timeline")
            return
        previous_end = 0.0
        previous_shot = 1
        seen_shots = set()
        for index, segment in enumerate(value, 1):
            label = "%s[%s]" % (at, index)
            segment = self.object(segment, label)
            start, end = segment.get("start_s"), segment.get("end_s")
            self.string(segment.get("event"), label + ".event")
            shot = segment.get("shot")
            if not integer(shot, 1) or shot > shots:
                self.error(label, "shot is outside declared shot range")
            else:
                seen_shots.add(shot)
                if shot < previous_shot or shot > previous_shot + 1:
                    self.error(label, "shot order must be contiguous and nondecreasing")
                previous_shot = shot
            if not number(start) or not number(end):
                self.error(label, "times must be finite numbers")
                continue
            if abs(start - previous_end) > 1e-6 or end <= start:
                self.error(label, "time intervals must be positive and continuous from zero")
            previous_end = end
        if abs(previous_end - self.config["duration_s"]) > 1e-6:
            self.error(at, "timeline must end at the configured duration")
        if seen_shots != set(range(1, shots + 1)):
            self.error(at, "timeline does not contain every declared shot")

    def references(self, value, at):
        if not isinstance(value, list) or not value:
            self.error(at, "requires actual image references")
            return []
        same_case_hashes = set()
        same_case_ids = set()
        checked = []
        for index, raw in enumerate(value, 1):
            label = "%s[%s]" % (at, index)
            ref = self.object(raw, label)
            checked.append(ref)
            if not integer(ref.get("index"), 1) or ref["index"] != index:
                self.error(label, "reference index must match ordered position")
            asset_id = self.string(ref.get("asset_id"), label + ".asset_id")
            if asset_id in same_case_ids:
                self.error(label, "duplicate asset_id within the case")
            same_case_ids.add(asset_id)
            for field in ("source_url", "role", "license_note"):
                self.string(ref.get(field), label + "." + field)
            if not isinstance(ref.get("source_repo"), str):
                self.error(label + ".source_repo", "must be a string")
            rights = self.enum(ref.get("rights_status"), {"cleared", "pending"}, label + ".rights_status")
            visual = self.enum(ref.get("visual_check"), {"passed", "pending"}, label + ".visual_check")
            if self.stage != "draft" and (rights != "cleared" or visual != "passed"):
                self.error(label, "rights and visual review must be completed")
            path_text = self.string(ref.get("path"), label + ".path")
            if not path_text:
                continue
            try:
                path = Path(path_text)
                if path.is_absolute() or "\\" in path_text:
                    raise ValueError("use a portable relative path")
                path = (self.root / path).resolve()
                if not path.is_relative_to(self.root):
                    raise ValueError("path escapes the asset root")
                suffix = path.suffix.lower()
                if suffix not in self.config["allowed_image_extensions"]:
                    raise ValueError("not an allowed static image extension")
                digest = hashlib.sha256()
                with path.open("rb") as handle:
                    header = handle.read(32)
                    digest.update(header)
                    while True:
                        chunk = handle.read(1024 * 1024)
                        if not chunk:
                            break
                        digest.update(chunk)
                if not image_signature(header, suffix):
                    raise ValueError("image header does not match its extension")
                actual_hash = digest.hexdigest()
            except (OSError, ValueError) as exc:
                self.error(label + ".path", str(exc))
                continue
            declared = ref.get("sha256")
            if not isinstance(declared, str) or not SHA_RE.fullmatch(declared) or declared.lower() != actual_hash:
                self.error(label + ".sha256", "does not match the actual file")
            if actual_hash in same_case_hashes:
                self.error(label, "duplicate image bytes cannot count as a new reference")
            same_case_hashes.add(actual_hash)
            if asset_id in self.asset_hashes and self.asset_hashes[asset_id] != actual_hash:
                self.error(label, "asset_id resolves to different image bytes")
            self.asset_hashes[asset_id] = actual_hash
        return checked

    def rewrite(self, value, prompt, at):
        value = self.object(value, at)
        used = value.get("used")
        if not isinstance(used, bool):
            self.error(at + ".used", "must be boolean")
            return
        if not used:
            return
        self.rewrites += 1
        self.enum(value.get("method"), REWRITE_METHODS, at + ".method")
        for field in ("source", "version", "before", "after", "evidence"):
            self.string(value.get(field), at + "." + field)
        if value.get("after") != prompt:
            self.error(at, "after must equal the final prompt")
        if value.get("before") == value.get("after"):
            self.error(at, "before and after must differ")

    def review(self, value, at):
        value = self.object(value, at)
        mode = self.enum(value.get("mode"), REVIEW_MODES, at + ".mode")
        if mode == "single_agent":
            self.single_agent_reviews += 1
        self.string(value.get("reviewer"), at + ".reviewer")
        self.string(value.get("notes"), at + ".notes")
        for dimension in ["status"] + self.config["review_dimensions"]:
            state = self.enum(value.get(dimension), {"passed", "pending", "failed"}, at + "." + dimension)
            if self.stage != "draft" and state != "passed":
                self.error(at + "." + dimension, "review has not passed")

    def upload(self, value, refs, at):
        value = self.object(value, at)
        state = self.enum(
            value.get("status"), {"not_requested", "pending", "blocked", "verified"}, at + ".status"
        )
        if self.require_uploaded and state != "verified":
            self.error(at, "verified upload is required")
        if state != "verified":
            return
        self.uploaded += 1
        self.string(value.get("target"), at + ".target")
        self.string(value.get("verified_by"), at + ".verified_by")
        remotes = value.get("remote_images")
        if not isinstance(remotes, list) or len(remotes) != len(refs):
            self.error(at, "remote image count must equal reference count")
            return
        for index, (remote, ref) in enumerate(zip(remotes, refs), 1):
            label = "%s.remote_images[%s]" % (at, index)
            remote = self.object(remote, label)
            if remote.get("index") != index or remote.get("asset_id") != ref.get("asset_id"):
                self.error(label, "remote order or asset_id does not match the input")
            location = self.string(remote.get("location"), label + ".location")
            if location.startswith(("/", "\\", "file:")) or re.match(r"^[A-Za-z]:[\\/]", location):
                self.error(label, "remote location must not be a local filesystem path")

    def case(self, raw, row):
        case = self.object(raw, "row %s" % row)
        case_id = self.string(case.get("id"), "row %s.id" % row)
        at = case_id or "row %s" % row
        if case_id in self.ids:
            self.error(at, "duplicate case id")
        self.ids.add(case_id)
        for key in ("title", "task_type", "main_test"):
            self.string(case.get(key), at + "." + key)
        self.strings(case.get("pass_criteria"), at + ".pass_criteria", nonempty=True)
        self.strings(case.get("failure_signals"), at + ".failure_signals", nonempty=True)
        modalities = case.get("input_modalities")
        if modalities != ["text", "image"]:
            self.error(at, "input_modalities must be exactly ['text', 'image']")
        prompt = self.string(case.get("prompt"), at + ".prompt")
        norm = normalized_prompt(prompt)
        if norm in self.prompts:
            self.error(at, "duplicate normalized prompt of %s" % self.prompts[norm])
        self.prompts[norm] = at
        language = self.enum(case.get("language"), self.config["languages"], at + ".language")
        style = self.enum(case.get("style"), self.config["styles"], at + ".style")
        if language:
            self.counts["languages"][language] += 1
        if style:
            self.counts["styles"][style] += 1
        duration = case.get("duration_s")
        if not number(duration) or duration != self.config["duration_s"]:
            self.error(at + ".duration_s", "must equal the configured duration")
        shots = case.get("shots")
        if not integer(shots, 1) or shots > self.config["max_shots"]:
            self.error(at + ".shots", "invalid shot count")
            shots = 1
        self.counts["shot_modes"]["single" if shots == 1 else "multi"] += 1
        self.timeline(case.get("timeline"), shots, at + ".timeline")
        subjects = self.strings(case.get("subject_tags"), at + ".subject_tags", nonempty=True)
        for subject in set(subjects):
            if self.enum(subject, self.config["subject_minimums"], at + ".subject_tags"):
                self.counts["subjects"][subject] += 1
        primary = self.enum(
            case.get("primary_capability"), self.config["capability_minimums"], at + ".primary_capability"
        )
        secondary = self.strings(case.get("secondary_capabilities"), at + ".secondary_capabilities")
        if len(secondary) > 2 or primary in secondary:
            self.error(at, "use one primary and at most two distinct secondary capabilities")
        caps = ([primary] if primary else []) + secondary
        evidence = self.object(case.get("capability_evidence"), at + ".capability_evidence")
        for cap in set(caps):
            if self.enum(cap, self.config["capability_minimums"], at + ".capabilities"):
                self.counts["capabilities"][cap] += 1
            quote = self.string(evidence.get(cap), at + ".capability_evidence." + cap)
            if quote and quote not in prompt:
                self.error(at, "capability evidence must appear verbatim in prompt")
        if set(evidence) != set(caps):
            self.error(at, "evidence keys must equal assigned capabilities")
        complexity = "simple" if len(set(caps)) == 1 else "medium" if len(set(caps)) == 2 else "hard"
        if case.get("complexity") != complexity:
            self.error(at + ".complexity", "does not match the explicit capability count")
        word_count = case.get("word_count")
        method = self.string(case.get("word_count_method"), at + ".word_count_method")
        if not integer(word_count):
            self.error(at + ".word_count", "must be a nonnegative integer")
        else:
            expected = "tiny" if word_count < 10 else "short" if word_count <= 30 else "long"
            if case.get("length_label") != expected:
                self.error(at + ".length_label", "does not match word_count")
            if language == "en" and word_count != len(WORD_RE.findall(prompt)):
                self.error(at + ".word_count", "does not match the packaged English word-count rule")
        if language == "zh":
            self.zh_methods.add(method)
        metric = {"id": case_id, "han": han_count(prompt), "non_whitespace_chars": len(re.sub(r"\s", "", prompt))}
        self.prompt_metrics.append(metric)
        if style == "ultra_long":
            bounds = self.config["ultra_long"]
            if language != bounds["language"] or not bounds["min_han"] <= metric["han"] <= bounds["max_han"]:
                self.error(at, "ultra_long must satisfy the configured language and Han-character range")
            if case.get("length_label") != "long":
                self.error(at, "ultra_long still needs the long length label")
        for key in ("daily_human", "handwriting"):
            if not isinstance(case.get(key), bool):
                self.error(at + "." + key, "must be boolean")
        if case.get("daily_human") is True:
            self.daily += 1
            if "human" not in subjects:
                self.error(at, "daily_human needs the human subject tag")
        if case.get("handwriting") is True:
            self.handwriting += 1
            if "text_layout" not in caps:
                self.error(at, "handwriting needs the text_layout capability")
        refs = self.references(case.get("refs"), at + ".refs")
        self.counts["reference_counts"][str(len(refs))] += 1
        if str(len(refs)) not in self.config["reference_counts"]:
            self.error(at, "reference count is outside configured bins")
        boundary = self.object(case.get("boundary"), at + ".boundary")
        is_boundary = len(refs) > self.config["boundary_threshold"]
        if not isinstance(boundary.get("is_boundary"), bool) or boundary["is_boundary"] != is_boundary:
            self.error(at, "boundary flag does not match actual reference count")
        if is_boundary:
            boundary_type = self.string(boundary.get("type"), at + ".boundary.type")
            self.counts["boundary_types"][boundary_type] += 1
        source = self.object(case.get("source"), at + ".source")
        source_type = self.enum(source.get("type"), self.config["source_types"], at + ".source.type")
        self.string(source.get("adaptation"), at + ".source.adaptation")
        if source_type != "handwritten":
            self.string(source.get("origin_url"), at + ".source.origin_url")
        self.rewrite(case.get("rewrite"), prompt, at + ".rewrite")
        self.review(case.get("review"), at + ".review")
        self.upload(case.get("upload"), refs, at + ".upload")

    def finish(self, total):
        config = self.config
        if self.stage == "full":
            if total != config["total_cases"]:
                self.error("dataset", "case count differs from total_cases")
            for key in ("languages", "shot_modes", "styles", "reference_counts"):
                for label in set(config[key]) | set(self.counts[key]):
                    if self.counts[key][label] != config[key].get(label, 0):
                        self.error(key, "quota mismatch for %s" % label)
            for category, minima in (
                ("subjects", config["subject_minimums"]),
                ("capabilities", config["capability_minimums"]),
            ):
                for label, minimum in minima.items():
                    if self.counts[category][label] < minimum:
                        self.error(category, "coverage below minimum for %s" % label)
            if self.rewrites != config["rewrite_cases"]:
                self.error("dataset", "rewrite count differs from rewrite_cases")
            if self.daily < config["daily_human_minimum"]:
                self.error("dataset", "not enough daily human cases")
            if sum(self.counts["boundary_types"].values()) != config["boundary_cases"]:
                self.error("dataset", "boundary case count differs from configuration")
            if len(self.counts["boundary_types"]) < config["distinct_boundary_types"]:
                self.error("dataset", "not enough distinct boundary type labels; semantic diversity still needs review")
        elif self.stage == "pilot":
            if total != config["pilot_cases"]:
                self.error("pilot", "case count differs from pilot_cases")
            for language in ("zh", "en"):
                if self.counts["languages"][language] == 0:
                    self.error("pilot", "both languages are required")
            if not self.counts["styles"]["ultra_long"] or not self.handwriting:
                self.error("pilot", "include an ultra-long case and a handwriting case")
            counts = [int(key) for key in self.counts["reference_counts"]]
            for low, high in ((1, 3), (4, 6), (7, 10), (11, 18), (19, math.inf)):
                if not any(low <= count <= high for count in counts):
                    self.error("pilot", "missing reference-count band %s-%s" % (low, high))
        if len(self.zh_methods) > 1:
            self.error("dataset", "Chinese word-count method must be consistent")
        if self.single_agent_reviews:
            self.warnings.append(
                "%s cases declare single-agent review, not independent review." % self.single_agent_reviews
            )
        if self.uploaded != total:
            self.warnings.append("Not every case has a verified upload; local validation does not prove online delivery.")
        return {
            "ok": not self.errors,
            "mechanical_only": True,
            "stage": self.stage,
            "require_uploaded": self.require_uploaded,
            "case_count": total,
            "counts": {key: dict(value) for key, value in self.counts.items()},
            "rewrite_cases": self.rewrites,
            "daily_human_cases": self.daily,
            "verified_upload_cases": self.uploaded,
            "prompt_metrics": self.prompt_metrics,
            "errors": self.errors,
            "warnings": self.warnings,
            "not_verified": [
                "Semantic image alignment, full decoding, animation and perceptual duplicates",
                "Authenticity of licenses, sources, rewrite use and reviewer declarations",
                "Physical timing, language naturalness, semantic diversity and remote accessibility",
                "Chinese tokenization and target model input limits",
            ],
        }


def validate(cases, config, asset_root, stage="full", require_uploaded=False):
    errors = config_errors(config)
    if errors:
        return {"ok": False, "mechanical_only": True, "errors": errors, "warnings": []}
    if not isinstance(cases, list):
        return {"ok": False, "mechanical_only": True, "errors": ["Cases must be a list."], "warnings": []}
    if stage not in {"draft", "pilot", "full"}:
        return {"ok": False, "mechanical_only": True, "errors": ["Unknown stage."], "warnings": []}
    checker = Checker(config, asset_root, stage, require_uploaded)
    for row, case in enumerate(cases, 1):
        checker.case(case, row)
    return checker.finish(len(cases))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases", nargs="?", type=Path)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--asset-root", type=Path)
    parser.add_argument("--stage", choices=("draft", "pilot", "full"), default="full")
    parser.add_argument("--require-uploaded", action="store_true")
    parser.add_argument("--check-config", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args(argv)
    try:
        config = json.loads(args.config.read_text(encoding="utf-8-sig"))
        if args.check_config:
            errors = config_errors(config)
            report = {"ok": not errors, "mechanical_only": True, "errors": errors, "warnings": []}
        else:
            if args.cases is None:
                parser.error("provide cases or use --check-config")
            root = args.asset_root if args.asset_root is not None else args.cases.parent
            report = validate(load_cases(args.cases), config, root, args.stage, args.require_uploaded)
        if args.report:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("PASS (mechanical checks only)" if report["ok"] else "FAIL")
        if "case_count" in report:
            print("Cases: %s | Stage: %s | Verified uploads: %s" % (
                report["case_count"], report["stage"], report["verified_upload_cases"]
            ))
        for error in report["errors"][:30]:
            print("ERROR:", error)
        if len(report["errors"]) > 30:
            print("Additional errors:", len(report["errors"]) - 30)
        for warning in report["warnings"]:
            print("WARNING:", warning)
        return 0 if report["ok"] else 1
    except (OSError, ValueError, TypeError) as exc:
        print("Input/report error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
