import unittest

from bm25_search import BM25, tokenize


class TokenizeTests(unittest.TestCase):
    def test_codes_kept_whole_and_in_parts(self):
        tokens = tokenize("Error ERR-4291 happened")
        self.assertIn("err-4291", tokens)
        self.assertIn("4291", tokens)

    def test_stopwords_removed(self):
        self.assertEqual(tokenize("the queue"), ["queue"])


class BM25Tests(unittest.TestCase):
    def setUp(self):
        docs = [
            "ERR-4291 means rate limit exceeded",
            "ERR-4001 means invalid json",
            "messages are kept for 14 days",
        ]
        self.bm25 = BM25([tokenize(d) for d in docs])

    def test_exact_code_ranks_first(self):
        scores = self.bm25.scores(tokenize("ERR-4291"))
        self.assertEqual(scores.index(max(scores)), 0)

    def test_no_overlap_scores_zero(self):
        self.assertEqual(self.bm25.scores(tokenize("banana")), [0.0, 0.0, 0.0])


if __name__ == "__main__":
    unittest.main()