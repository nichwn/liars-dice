from unittest import TestCase
from liars_dice.server.game import Die


class TestDie(TestCase):

    def setUp(self):
        self.die = Die()

    def test_roll(self):
        # Appropriate roll values
        self.die.roll()
        self.assertGreaterEqual(self.die.face, 1, "value less than 1")
        self.assertLessEqual(self.die.face, 6, "value greater than 6")
