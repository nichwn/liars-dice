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

    def test_roll(self):
        for die in self.hand.hand:
            self.assertGreaterEqual(die.face, 1, "value less than 1")
            self.assertLessEqual(die.face, 6, "value greater than 6")

    def test_die_face(self):
        for i in xrange(len(self.hand.hand)):
            self.hand.hand[i].face = min(i + 1, 6)

        test_result = self.hand.die_face()

        # The mucking about with len is to changing the default hand size
        # in affecting this test
        unsized_hand = ([1, 2, 3, 4, 5] + (len(self.hand.hand) - 5) * [6])
        expected_result = unsized_hand[:len(self.hand.hand)]

        self.assertEqual(test_result, expected_result,
                         "incorrect hand compostion")
