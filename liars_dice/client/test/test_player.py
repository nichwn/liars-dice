from liars_dice.client.player import Player
from unittest import TestCase


class TestPlayer(TestCase):
    def setUp(self):
        self.player = Player()

    def test__received_hand(self):
        self.player._received_hand("6,5,6,4,1,3")
        self.assertEqual(self.player.hand, [1, 3, 4, 5, 6, 6],
                         "hand does not correspond with expected hand")
