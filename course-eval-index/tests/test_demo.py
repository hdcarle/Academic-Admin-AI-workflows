"""Smoke test: the bundled demo reports parse and build without errors.  Run: python -m pytest tests"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(cmd):
    return subprocess.run([sys.executable, "-m", "course_eval", cmd, "--config", "examples/config.yaml"],
                          cwd=ROOT, capture_output=True, text=True)


def test_demo_parse_and_build():
    assert run("parse").returncode == 0
    sections = json.load(open(os.path.join(ROOT, "examples", "demo_data", "sections.json")))
    assert len(sections) == 4
    assert sum(s["enrolled"] for s in sections) == 110
    assert {s["format"] for s in sections} == {"Online", "In-person"}
    assert run("build").returncode == 0
    assert os.path.exists(os.path.join(ROOT, "examples", "demo_output", "Teaching_Evaluation_Index.xlsx"))
    assert run("verify").returncode == 0
