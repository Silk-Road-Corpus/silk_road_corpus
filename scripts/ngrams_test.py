import unittest
from collections import Counter
from ngrams import extract_ngrams


class TestExtractNgrams(unittest.TestCase):
    """Unit tests for the extract_ngrams function."""

    def test_simple_string(self):
        """Tests a simple string with no punctuation."""
        text = "你好世界"
        expected_counts = Counter({
            # Unigrams
            '你': 1, '好': 1, '世': 1, '界': 1,
            # Bigrams
            '你好': 1, '好世': 1, '世界': 1,
            # Trigrams
            '你好世': 1, '好世界': 1,
            # 4-gram
            '你好世界': 1
        })
        self.assertEqual(extract_ngrams(text), expected_counts)

    def test_string_with_punctuation(self):
        """Tests that Chinese punctuation and whitespace are correctly stripped."""
        text = "你好，世界。　歡迎！"
        # Cleaned text should be "你好世界歡迎"
        expected_counts = Counter({
            # Unigrams
            '你': 1, '好': 1, '世': 1, '界': 1, '歡': 1, '迎': 1,
            # Bigrams
            '你好': 1, '好世': 1, '世界': 1, '界歡': 1, '歡迎': 1,
            # Trigrams
            '你好世': 1, '好世界': 1, '世界歡': 1, '界歡迎': 1,
            # 4-grams
            '你好世界': 1, '好世界歡': 1, '世界歡迎': 1,
            # 5-grams
            '你好世界歡': 1, '好世界歡迎': 1,
            # 6-grams
            '你好世界歡迎': 1
        })
        self.assertEqual(extract_ngrams(text), expected_counts)

    def test_string_with_repetitions(self):
        """Tests a string with repeated characters and sequences."""
        text = "吃葡萄不吐葡萄皮"
        expected_counts = Counter({
            # Unigrams
            '吃': 1, '葡': 2, '萄': 2, '不': 1, '吐': 1, '皮': 1,
            # Bigrams
            '吃葡': 1, '葡萄': 2, '萄不': 1, '不吐': 1, '吐葡': 1, '萄皮': 1,
            # Trigrams
            '吃葡萄': 1, '葡萄不': 1, '萄不吐': 1, '不吐葡': 1, '吐葡萄': 1, '萄皮': 1,
            # 4-grams
            '吃葡萄不': 1, '葡萄不吐': 1, '萄不吐葡': 1, '不吐葡萄': 1, '吐葡萄皮': 1
        })
        # The trigram '葡萄皮' is missing from the expected because the last '萄' is followed by '皮'
        # Let's correct the expected trigrams
        expected_counts_corrected = Counter({
            # Unigrams
            '吃': 1, '葡': 2, '萄': 2, '不': 1, '吐': 1, '皮': 1,
            # Bigrams
            '吃葡': 1, '葡萄': 2, '萄不': 1, '不吐': 1, '吐葡': 1, '萄皮': 1,
            # Trigrams
            '吃葡萄': 1, '葡萄不': 1, '萄不吐': 1, '不吐葡': 1, '吐葡萄': 1, '葡萄皮': 1,
            # 4-grams
            '吃葡萄不': 1, '葡萄不吐': 1, '萄不吐葡': 1, '不吐葡萄': 1, '吐葡萄皮': 1,
            # 5-grams
            '吃葡萄不吐': 1, '葡萄不吐葡': 1, '萄不吐葡萄': 1, '不吐葡萄皮': 1,
            # 6-grams
            '吃葡萄不吐葡': 1, '葡萄不吐葡萄': 1, '萄不吐葡萄皮': 1,
            # 7-grams
            '吃葡萄不吐葡萄': 1, '葡萄不吐葡萄皮': 1,
            # 8-grams
            '吃葡萄不吐葡萄皮': 1
        })
        self.assertEqual(extract_ngrams(text), expected_counts_corrected)

    def test_empty_string(self):
        """Tests an empty string input."""
        text = ""
        expected_counts = Counter()
        self.assertEqual(extract_ngrams(text), expected_counts)

    def test_short_string(self):
        """Tests a string shorter than the max n-gram size."""
        text = "佛"
        expected_counts = Counter({'佛': 1})
        self.assertEqual(extract_ngrams(text), expected_counts)

        text_two = "佛教"
        expected_counts_two = Counter({'佛': 1, '教': 1, '佛教': 1})
        self.assertEqual(extract_ngrams(text_two), expected_counts_two)

    def test_punctuation_only_string(self):
        """Tests a string that only contains punctuation."""
        text = "，。？！"
        expected_counts = Counter()
        self.assertEqual(extract_ngrams(text), expected_counts)


if __name__ == '__main__':
    unittest.main()
