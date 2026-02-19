import unittest
import cszjj

class TestPhraseCount(unittest.TestCase):
    """Unit tests for the phrase_count function."""

    def test_single_char(self):
        """Test counting a single character."""
        content = "觀自在菩薩"
        self.assertEqual(cszjj.phrase_count(content, "觀"), 1)
        self.assertEqual(cszjj.phrase_count(content, "薩"), 1)
        self.assertEqual(cszjj.phrase_count(content, "無"), 0)

    def test_multi_char_phrase(self):
        """Test counting a multi-character phrase."""
        content = "色不異空，空不異色"
        self.assertEqual(cszjj.phrase_count(content, "不異"), 2)
        self.assertEqual(cszjj.phrase_count(content, "色不"), 1)
        self.assertEqual(cszjj.phrase_count(content, "受想"), 0)

    def test_repeated_phrase(self):
        """Test counting repeated phrases."""
        content = "善哉善哉"
        self.assertEqual(cszjj.phrase_count(content, "善哉"), 2)
        self.assertEqual(cszjj.phrase_count(content, "善"), 2)

    def test_empty_content(self):
        """Test counting in empty content."""
        self.assertEqual(cszjj.phrase_count("", "佛"), 0)

    def test_multiline_content1(self):
        """Test counting phrases in multi-line content."""
        content = "觀自在菩薩\n行深般若波羅蜜多時\n觀自在菩薩"
        self.assertEqual(cszjj.phrase_count(content, "觀自在"), 2)

    def test_multiline_content(self):
        """Test counting phrases in multi-line content."""
        content = """
[0723a11] 佛言：「夫為道者，譬如持炬火入冥室中，其冥 即滅而明猶在，學道見諦，愚癡都滅，得無 不見。」

[0723a14] 佛言：「吾何念念道？吾何行行道？吾何言言道？ 吾念諦道，不忽須臾也。」

[0723a16] 佛言：「覩天地念非常，覩山川念非常，覩万 物形體豐熾念非常；執心如此，得道疾矣。」

[0723a18] 佛言：「一日行，常念道、行道，遂得信根，其福無 量。」

[0723a20] 佛言：「熟自念身中四大，名自有名都為無，吾 我者寄生，生亦不久，其事如幻耳。」
"""
        self.assertEqual(cszjj.phrase_count(content, "吾"), 5)

if __name__ == '__main__':
    unittest.main()