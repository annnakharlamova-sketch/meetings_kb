from pathlib import Path

from parsers.meeting_parser import parse_meeting


BASE_DIR = Path(__file__).resolve().parent.parent

file = BASE_DIR / "data" / "meeting_01.txt"

print(file)

text = file.read_text(
    encoding="utf-8"
)

meeting = parse_meeting(text)

print(meeting)