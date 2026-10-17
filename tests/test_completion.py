import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from app import store
from app.service import complete_task, get_task


class CompletionPersistenceTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.data_file = Path(directory.name) / "tasks.json"
        self.tasks = [
            {"id": 1, "status": "open", "completed_at": None},
            {"id": 2, "status": "open", "completed_at": None},
        ]
        self.data_file.write_text(json.dumps(self.tasks), encoding="utf-8")
        patcher = patch.object(store, "DATA_FILE", self.data_file)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_completion_persists_to_json_and_subsequent_reads(self):
        completed = complete_task(1)
        persisted = json.loads(self.data_file.read_text(encoding="utf-8"))
        self.assertEqual(persisted[0]["status"], "done")
        self.assertIsNotNone(persisted[0]["completed_at"])
        self.assertEqual(persisted[0], completed)
        self.assertEqual(get_task(1), completed)
        self.assertEqual(persisted[1], self.tasks[1])

    def test_missing_task_does_not_change_storage(self):
        before = self.data_file.read_bytes()
        self.assertIsNone(complete_task(999))
        self.assertEqual(self.data_file.read_bytes(), before)
