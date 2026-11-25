import unittest

from tinynotes import config, storage


class StorageTest(unittest.TestCase):
    def setUp(self):
        self.conn = storage.connect(":memory:")

    def tearDown(self):
        self.conn.close()

    def test_add_and_get(self):
        note_id = storage.add_note(self.conn, "标题", "正文")
        note = storage.get_note(self.conn, note_id)
        self.assertEqual(note["title"], "标题")
        self.assertEqual(note["body"], "正文")

    def test_get_missing(self):
        self.assertIsNone(storage.get_note(self.conn, 999))

    def test_list_is_newest_first_and_paged(self):
        for i in range(config.PAGE_SIZE + 3):
            storage.add_note(self.conn, f"t{i}", f"b{i}")
        first = storage.list_notes(self.conn, page=1)
        second = storage.list_notes(self.conn, page=2)
        self.assertEqual(len(first), config.PAGE_SIZE)
        self.assertEqual(len(second), 3)
        self.assertEqual(first[0]["title"], f"t{config.PAGE_SIZE + 2}")

    def test_delete(self):
        note_id = storage.add_note(self.conn, "t", "b")
        self.assertTrue(storage.delete_note(self.conn, note_id))
        self.assertFalse(storage.delete_note(self.conn, note_id))

    def test_search_matches_title_and_body(self):
        storage.add_note(self.conn, "买菜", "西红柿和鸡蛋")
        storage.add_note(self.conn, "读书", "《人月神话》")
        self.assertEqual(len(storage.search_notes(self.conn, "鸡蛋")), 1)
        self.assertEqual(len(storage.search_notes(self.conn, "读书")), 1)
        self.assertEqual(len(storage.search_notes(self.conn, "不存在")), 0)


if __name__ == "__main__":
    unittest.main()
