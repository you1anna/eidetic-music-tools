from __future__ import annotations

from pathlib import Path

from librarytools import config, sort


def _make(root: Path, rel: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("audio")
    return path


def test_build_plan_targets_flat_role_dest(tmp_path: Path):
    root = tmp_path / "SAMPLES"
    _make(root, "DRUM-KITS/Pack/Kicks/Kick Big 909.wav")

    plan = sort.build_plan(root=root)

    assert len(plan) == 1
    move = plan[0]
    # Flat: file lands directly under the role folder, not in a pack subfolder.
    assert move.dest.parent == root / "KICKS"
    assert move.dest.name.endswith(".wav")
    assert move.tag.startswith("KICKS|")


def test_review_files_are_left_unsorted_by_default(tmp_path: Path):
    root = tmp_path / "SAMPLES"
    _make(root, "_PACKS/Sean/Sean 80s/o.wav")  # cryptic -> _REVIEW

    assert sort.build_plan(root=root) == []


def test_destination_and_staging_dirs_are_not_sources(tmp_path: Path):
    root = tmp_path / "SAMPLES"
    _make(root, "KICKS/already-sorted.wav")     # a destination role folder
    _make(root, "_TO-DELETE/dupe.wav")          # dedupe staging
    _make(root, "_REVIEW/leftover.wav")         # review staging

    assert sort.build_plan(root=root) == []


def test_top_level_vendor_folders_are_in_scope(tmp_path: Path):
    root = tmp_path / "SAMPLES"
    _make(root, "Goldbaby.Super.Analog.909/SA909_HH/HH_909D2_AC_R6.wav")

    plan = sort.build_plan(root=root)

    assert len(plan) == 1
    assert plan[0].dest.parent == root / "HATS-CYM"


def test_include_review_flag_gathers_review_files(tmp_path: Path):
    root = tmp_path / "SAMPLES"
    _make(root, "_PACKS/Sean/Sean 80s/o.wav")

    plan = sort.build_plan(root=root, include_review=True)

    assert len(plan) == 1
    assert plan[0].dest.parent == root / "_REVIEW"


def test_apply_moves_file_and_writes_undo(tmp_path: Path, monkeypatch):
    root = tmp_path / "SAMPLES"
    src = _make(root, "DRUM-KITS/Pack/Kicks/Kick Big 909.wav")
    monkeypatch.setattr(config, "MANIFEST_DIR", tmp_path / "manifests")

    code = sort.main(["--root", str(root), "--apply"])

    assert code == 0
    assert not src.exists()
    moved = list((root / "KICKS").glob("*.wav"))
    assert len(moved) == 1


def test_dry_run_leaves_files_in_place(tmp_path: Path, monkeypatch):
    root = tmp_path / "SAMPLES"
    src = _make(root, "DRUM-KITS/Pack/Kicks/Kick 909.wav")
    monkeypatch.setattr(config, "MANIFEST_DIR", tmp_path / "manifests")

    code = sort.main(["--root", str(root)])

    assert code == 0
    assert src.exists()
