import unittest

import numpy as np

from access import allowed_mask, masked_top_k, visible_chunks
from bm25_search import BM25Index

CHUNKS = [
    {"id": "a#00", "access": "public", "text": "queue basics"},
    {"id": "b#00", "access": "internal", "text": "dead-letter runbook"},
    {"id": "c#00", "access": "restricted", "text": "secret retention policy"},
    {"id": "d#00", "access": "weird-label", "text": "unknown label"},
    {"id": "e#00", "text": "missing label"},
]


def ids(chunks):
    return [c["id"] for c in chunks]


class VisibilityTests(unittest.TestCase):
    def test_public_sees_only_public(self):
        self.assertEqual(ids(visible_chunks(CHUNKS, "public")), ["a#00"])

    def test_internal_sees_public_and_internal(self):
        self.assertEqual(ids(visible_chunks(CHUNKS, "internal")), ["a#00", "b#00"])

    def test_restricted_sees_everything(self):
        self.assertEqual(len(visible_chunks(CHUNKS, "restricted")), 5)

    def test_unknown_or_missing_labels_fail_closed(self):
        hidden = ids(visible_chunks(CHUNKS, "internal"))
        self.assertNotIn("d#00", hidden)
        self.assertNotIn("e#00", hidden)

    def test_unknown_user_level_gets_least_access(self):
        self.assertEqual(ids(visible_chunks(CHUNKS, "admin?")), ["a#00"])


class RankingTests(unittest.TestCase):
    def test_masked_item_is_never_returned_even_if_best(self):
        scores = np.array([0.1, 0.9, 0.5])
        mask = np.array([True, False, True])
        self.assertEqual(masked_top_k(scores, mask, 3), [2, 0])

    def test_nothing_allowed_returns_nothing(self):
        scores = np.array([0.4, 0.8])
        self.assertEqual(masked_top_k(scores, np.array([False, False]), 2), [])

    def test_bm25_built_from_visible_chunks_never_returns_restricted(self):
        index = BM25Index(visible_chunks(CHUNKS, "public"))
        results = ids(c for _s, c in index.search("secret retention policy", k=5))
        self.assertNotIn("c#00", results)


if __name__ == "__main__":
    unittest.main()