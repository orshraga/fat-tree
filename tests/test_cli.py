import json

import pytest

from cli import main


def test_basic_run_prints_expected_lines(capsys):
    assert main(["--k", "4", "--failure-rate", "0", "--seed", "1"]) == 0
    out = capsys.readouterr().out
    assert "k = 4" in out
    assert "hosts: 16" in out
    assert "reachable host pairs: 120 of 120 (100.0%)" in out


def test_config_file_is_used(tmp_path, capsys):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"k": 6, "failure_rate": 0.0, "seed": 3}), encoding="utf-8")
    assert main(["--config", str(cfg)]) == 0
    assert "k = 6" in capsys.readouterr().out


def test_cli_flag_overrides_config(tmp_path, capsys):
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"k": 6}), encoding="utf-8")
    assert main(["--config", str(cfg), "--k", "4"]) == 0
    assert "k = 4" in capsys.readouterr().out


def test_missing_k_is_an_error():
    with pytest.raises(SystemExit):
        main(["--failure-rate", "0.1"])


def test_invalid_rate_is_an_error():
    with pytest.raises(SystemExit):
        main(["--k", "4", "--failure-rate", "1.5"])


def test_unknown_config_key_is_an_error(tmp_path):
    cfg = tmp_path / "bad.json"
    cfg.write_text(json.dumps({"k": 4, "colour": "red"}), encoding="utf-8")
    with pytest.raises(SystemExit):
        main(["--config", str(cfg)])
