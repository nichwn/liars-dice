from unittest import TestCase
from liars_dice.server.game import Hand, Die


class TestHand(TestCase):

    def setUp(self):
        self.hand = Hand()

    def test_have_die(self):
        self.assertEqual(self.hand.have_die(), True,
                         "failed to recognise multiple dice in hand")
        self.hand.hand = [Die()]
        self.assertEqual(self.hand.have_die(), True,
                         "failed to recognise single die in hand")
        self.hand.hand = []
        self.assertEqual(self.hand.have_die(), False,
                         "failed to recognise empty hand")

    def test_reroll(self):
        for die in self.hand.hand:
            self.assertGreaterEqual(die.value, 1, "value less than 1")
            self.assertLessEqual(die.value, 6, "value greater than 6")
