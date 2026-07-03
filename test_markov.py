#!/usr/bin/env python3
"""Tests for the Markov captain's log generator."""

import random
import unittest

from markov_captains_log import MarkovChain


class MarkovChainGenerationTests(unittest.TestCase):
    def test_generate_returns_sentence_when_max_length_hits_mid_sentence(self):
        chain = MarkovChain(order=1)
        chain.train([
            "Captain reports anomaly near the neutral zone with no immediate resolution",
        ])

        random.seed(7)
        generated = chain.generate(max_length=8, min_length=3)

        self.assertEqual(generated[0], generated[0].upper())
        self.assertTrue(generated.endswith("."), generated)
        self.assertLessEqual(len(generated.split()), 8)

    def test_generate_trims_to_last_complete_sentence_when_available(self):
        chain = MarkovChain(order=1)
        chain.train([
            "Captain log complete. This continuation should be trimmed before max length expires",
        ])

        random.seed(7)
        generated = chain.generate(max_length=7, min_length=2)

        self.assertEqual(generated, "Captain log complete.")


if __name__ == "__main__":
    unittest.main()
