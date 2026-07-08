"""Torch-free tests for the classifier's pure logic (taxonomy, banding, audit shaping)."""

from __future__ import annotations

from pathlib import Path

from librarytools import classifier, config, review


def test_int2class_is_30_and_kick_index_consistent() -> None:
    assert len(classifier.INT2CLASS) == 30
    assert classifier.INT2CLASS[classifier.KICK_INDEX] == "kick"


def test_class_to_role_targets_are_real_curated_roles() -> None:
    valid = set(review.ROLE_FOLDERS)
    for cls, role in classifier.CLASS_TO_ROLE.items():
        assert cls in classifier.INT2CLASS
        assert role in valid, f"{cls} -> {role} is not a CURATED role"


def test_drum_roles_are_covered_by_the_mapping() -> None:
    mapped_roles = set(classifier.CLASS_TO_ROLE.values())
    assert classifier.DRUM_ROLES - {"DRUM-KITS"} <= mapped_roles


def test_band_thresholds() -> None:
    assert classifier._band(0.80) == "trust"
    assert classifier._band(0.79) == "review"
    assert classifier._band(0.50) == "review"
    assert classifier._band(0.49) == "low"


def test_available_false_when_weights_missing(monkeypatch) -> None:
    monkeypatch.setattr(config, "DRUM_MODEL_PATH", Path("/nonexistent/weights.model"))
    assert classifier.available() is False


def test_write_role_audit_roundtrip(tmp_path: Path) -> None:
    rows = [
        classifier.RoleAuditRow(
            path="CURATED/KICKS/a.wav", current_role="KICKS", authoritative=True,
            top_class="cym", top_prob=0.91, kick_prob=0.0, suggested_role="HATS-CYM",
            agree="no", band="trust", note="",
        ),
        classifier.RoleAuditRow(
            path="CURATED/DRONE-ATMOS/b.wav", current_role="DRONE-ATMOS", authoritative=False,
            top_class="fx", top_prob=0.42, kick_prob=0.01, suggested_role="REVIEW",
            agree="", band="", note="",
        ),
    ]
    out = tmp_path / "role-audit.tsv"
    classifier.write_role_audit(out, rows)
    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[0].split("\t")[:3] == ["path", "current_role", "authoritative"]
    assert lines[1].split("\t")[7] == "no"  # agree column for the mismatched authoritative row

    summary = classifier.summarise_role_audit(rows)
    assert any("KICKS" in line and "high-confidence" in line for line in summary)
    assert any("DRONE-ATMOS" in line and "possible-drum-oneshot" in line for line in summary)
