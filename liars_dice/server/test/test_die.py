from unittest import TestCase
from liars_dice.server.game import Die


class TestDie(TestCase):

    def setUp(self):
        self.die = Die()

    def test_roll(self):
        self.die.roll()
        self.assertGreaterEqual(self.die.value, 1, "value less than 1")
        self.assertLessEqual(self.die.value, 6, "value greater than 6")
