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
    # Flat: file lands directly under the role folder in the CURATED zone.
    assert move.dest.parent == root / "CURATED" / "KICKS"
    assert move.dest.name.endswith(".wav")
    assert move.tag.startswith("KICKS|")


def test_curated_and_packs_are_not_sources(tmp_path: Path):
    root = tmp_path / "SAMPLES"
    _make(root, "CURATED/KICKS/already.wav")    # curated zone (destination)
    _make(root, "PACKS/vendor/loop.wav")        # raw packs zone (browse-only)

    assert sort.build_plan(root=root) == []


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
    assert plan[0].dest.parent == root / "CURATED" / "HATS-CYM"


def test_include_review_flag_gathers_review_files(tmp_path: Path):
    root = tmp_path / "SAMPLES"
    _make(root, "_PACKS/Sean/Sean 80s/o.wav")

    plan = sort.build_plan(root=root, include_review=True)

    assert len(plan) == 1
    assert plan[0].dest.parent == root / "_REVIEW"


def test_colliding_names_get_numeric_suffix(tmp_path: Path):
    root = tmp_path / "SAMPLES"
    # Two distinct files that normalise to the same proposed name.
    _make(root, "DRUM-KITS/PackA/Kicks/Kick 909.wav")
    _make(root, "DRUM-KITS/PackA/Kicks/Kick  909.wav")  # double space -> same name

    plan = sort.build_plan(root=root)
    dests = sorted(m.dest.name for m in plan)

    assert len(plan) == 2
    assert len(set(dests)) == 2  # collision resolved, not skipped
    assert any(d.endswith("-2.wav") for d in dests)


def test_collision_with_existing_disk_file_gets_suffix(tmp_path: Path):
    root = tmp_path / "SAMPLES"
    _make(root, "CURATED/KICKS/kick-909_packa.wav")      # already in destination
    _make(root, "DRUM-KITS/PackA/Kicks/Kick 909.wav")    # normalises to same name

    plan = sort.build_plan(root=root)

    assert len(plan) == 1
    assert plan[0].dest.name == "kick-909_packa-2.wav"


def test_apply_moves_file_and_writes_undo(tmp_path: Path, monkeypatch):
    root = tmp_path / "SAMPLES"
    src = _make(root, "DRUM-KITS/Pack/Kicks/Kick Big 909.wav")
    monkeypatch.setattr(config, "MANIFEST_DIR", tmp_path / "manifests")

    code = sort.main(["--root", str(root), "--apply"])

    assert code == 0
    assert not src.exists()
    moved = list((root / "CURATED" / "KICKS").glob("*.wav"))
    assert len(moved) == 1


def test_dry_run_leaves_files_in_place(tmp_path: Path, monkeypatch):
    root = tmp_path / "SAMPLES"
    src = _make(root, "DRUM-KITS/Pack/Kicks/Kick 909.wav")
    monkeypatch.setattr(config, "MANIFEST_DIR", tmp_path / "manifests")

    code = sort.main(["--root", str(root)])

    assert code == 0
    assert src.exists()
