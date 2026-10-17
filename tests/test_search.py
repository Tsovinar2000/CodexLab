import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from app import store
from app.schemas import TaskStatus
from app.service import list_tasks


class SearchTests(unittest.TestCase):
    def test_search_with_temporary_storage(self):
        tasks = [
            {"id": 1, "title": "Launch recap", "description": "Draft summary", "status": "open"},
            {"id": 2, "title": "Archive notes", "description": "Final launch report", "status": "done"},
            {"id": 3, "title": "Plan agenda", "description": "Workshop outline", "status": "open"},
        ]
        cases = [
            ("title substring", {"q": "aunc"}, [1, 2]),
            ("description", {"q": "report"}, [2]),
            ("uppercase title", {"q": "RECAP"}, [1]),
            ("uppercase description", {"q": "FINAL"}, [2]),
            ("combined open", {"q": "launch", "status": TaskStatus.open}, [1]),
            ("combined done", {"q": "launch", "status": TaskStatus.done}, [2]),
            ("combined no matches", {"q": "agenda", "status": TaskStatus.done}, []),
            ("no matches", {"q": "missing"}, []),
            ("omitted q", {}, [1, 2, 3]),
            ("omitted q with status", {"status": TaskStatus.open}, [1, 3]),
        ]
        with TemporaryDirectory() as directory:
            data_file = Path(directory) / "tasks.json"
            data_file.write_text(json.dumps(tasks), encoding="utf-8")
            before = data_file.read_bytes()
            with patch.object(store, "DATA_FILE", data_file):
                for name, parameters, expected in cases:
                    with self.subTest(name=name):
                        self.assertEqual(
                            [task["id"] for task in list_tasks(**parameters)], expected
                        )
            self.assertEqual(data_file.read_bytes(), before)
