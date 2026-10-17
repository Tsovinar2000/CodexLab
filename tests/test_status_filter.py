import unittest
from unittest.mock import patch

from app.schemas import TaskStatus
from app.service import list_tasks


class StatusFilterTests(unittest.TestCase):
    def test_status_filter(self):
        tasks = [
            {"id": 1, "status": "open"},
            {"id": 2, "status": "done"},
            {"id": 3, "status": "open"},
        ]
        cases = [
            (None, tasks),
            (TaskStatus.open, [tasks[0], tasks[2]]),
            (TaskStatus.done, [tasks[1]]),
        ]
        with patch("app.service.load_tasks", return_value=tasks):
            for status, expected in cases:
                with self.subTest(status=status):
                    self.assertEqual(list_tasks(status=status), expected)

    def test_status_filter_without_matches(self):
        with patch("app.service.load_tasks", return_value=[{"id": 1, "status": "open"}]):
            self.assertEqual(list_tasks(status=TaskStatus.done), [])

    def test_status_filter_with_empty_store(self):
        with patch("app.service.load_tasks", return_value=[]):
            self.assertEqual(list_tasks(status=TaskStatus.open), [])
