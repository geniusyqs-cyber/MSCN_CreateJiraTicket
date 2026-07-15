import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import create_mscn_ticket


def test_parse_args_accepts_description_file(tmp_path, monkeypatch):
    description_file = tmp_path / "description.txt"
    description_file.write_text("hello from file", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "create_mscn_ticket.py",
            "--summary",
            "Test",
            "--description-file",
            str(description_file),
        ],
    )

    args = create_mscn_ticket.parse_args()

    assert args.description_file == str(description_file)
