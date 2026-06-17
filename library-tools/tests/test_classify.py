from __future__ import annotations

from pathlib import Path

from librarytools.classify import classify_path


def test_loop_keyword_wins():
    b, r = classify_path(Path("_PACKS/Riemann/drum loop 132.wav"))
    assert b == "LOOPS"
    assert "loop" in r


def test_bpm_token_is_a_loop():
    b, _ = classify_path(Path("_PACKS/Pack/rumble_132bpm.wav"))
    assert b == "LOOPS"


def test_pad_keyword():
    b, _ = classify_path(Path("_PACKS/Pack/warm pad C.wav"))
    assert b == "PADS-DRONES"


def test_drone_keyword():
    b, _ = classify_path(Path("DRUM-KITS/Vendor/dark drone.wav"))
    assert b == "PADS-DRONES"


def test_oneshot_keyword():
    b, _ = classify_path(Path("DRUM-KITS/Vendor/kick hit 01.wav"))
    assert b == "ONE-SHOTS"


def test_loop_beats_pad_when_both_present():
    b, _ = classify_path(Path("_PACKS/Pack/pad loop.wav"))
    assert b == "LOOPS"


def test_short_duration_oneshot_when_no_keyword():
    b, r = classify_path(Path("_PACKS/Pack/zap.wav"), duration=0.4)
    assert b == "ONE-SHOTS"
    assert "duration" in r


def test_long_duration_loop_when_no_keyword():
    b, _ = classify_path(Path("_PACKS/Pack/zap.wav"), duration=4.0)
    assert b == "LOOPS"


def test_unmatched_no_duration_is_other():
    b, r = classify_path(Path("_PACKS/Pack/mystery.wav"))
    assert b == "OTHER"
    assert r == "unmatched"


def test_folder_keyword_counts():
    b, _ = classify_path(Path("_PACKS/Techno Loops/bd.wav"))
    assert b == "LOOPS"
