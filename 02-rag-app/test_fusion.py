import unittest

from fusion import rrf


def chunk(i):
    return {"id": i}


class FusionTests(unittest.TestCase):
    def test_agreement_beats_a_single_list_win(self):
        a = [chunk("x"), chunk("y"), chunk("z")]
        b = [chunk("y"), chunk("w")]
        fused = rrf([a, b])
        # y is rank 2 + rank 1, x is rank 1 in one list only
        self.assertEqual(fused[0][1]["id"], "y")

    def test_item_in_only_one_list_still_appears(self):
        fused = rrf([[chunk("x")], [chunk("w")]])
        self.assertEqual({c["id"] for _s, c in fused}, {"x", "w"})

    def test_top_n_limits_results(self):
        ranking = [chunk(str(i)) for i in range(10)]
        self.assertEqual(len(rrf([ranking], top_n=3)), 3)


if __name__ == "__main__":
    unittest.main()