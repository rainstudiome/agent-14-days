import unittest

from tinynotes.utils import make_title, truncate


class TruncateTest(unittest.TestCase):
    def test_short_text_unchanged(self):
        self.assertEqual(truncate("hello", 10), "hello")

    def test_exact_length_unchanged(self):
        self.assertEqual(truncate("hello", 5), "hello")

    def test_long_text_fits_limit(self):
        # 截断以后，连同省略号一共不能超过 limit 个字符
        result = truncate("abcdefghijk", 5)
        self.assertEqual(result, "abcd…")
        self.assertEqual(len(result), 5)


class MakeTitleTest(unittest.TestCase):
    def test_first_line(self):
        self.assertEqual(make_title("第一行\n第二行"), "第一行")

    def test_empty_body(self):
        self.assertEqual(make_title("   "), "无标题")


if __name__ == "__main__":
    unittest.main()
