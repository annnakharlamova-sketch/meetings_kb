import sys
import os

repo_root = os.path.abspath(os.path.dirname(__file__))
src_path = os.path.join(repo_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from parsers.filters import parse_query

failed = 0

# Test 1
catalog = {
    "projects": ["CRM2026 Migration"],
    "participants": ["Иванов А."],
    "statuses": ["open"],
    "topics": ["budget"]
}
q = "CRM after 10.06.2026 with Ivanov"
out = parse_query(q, catalog)
print('TEST1 output:', out)
if out["filters"]["project"] is None:
    print('TEST1 FAIL: project not matched')
    failed += 1
if out["filters"]["date_from"] != "2026-06-10":
    print('TEST1 FAIL: date_from expected 2026-06-10 got', out["filters"]["date_from"])
    failed += 1

# Test 2
catalog2 = {"projects": ["X"], "participants": ["Y"], "statuses": ["Z"], "topics": ["T"]}
q2 = "Unrelated query that matches nothing"
out2 = parse_query(q2, catalog2)
print('TEST2 output:', out2)
expected_filters = {"project": None, "participants": None, "date_from": None, "date_to": None, "status": None, "topics": None}
if out2["filters"] != expected_filters:
    print('TEST2 FAIL: filters differ')
    failed += 1

if failed:
    print(f"FAILED {failed} test(s)")
    sys.exit(1)
print('ALL TESTS PASSED')
sys.exit(0)
