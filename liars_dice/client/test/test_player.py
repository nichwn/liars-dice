from liars_dice.client.player import Player
from unittest import TestCase


class TestPlayer(TestCase):
    def setUp(self):
        self.player = Player()

    def test__received_hand(self):
        self.player._received_hand("6,5,6,4,1,3")
        self.assertEqual(self.player.hand, [1, 3, 4, 5, 6, 6],
                         "hand does not correspond with expected hand")

    def test__received_player_status(self):
        self.player._received_player_status("c=6,a=3,b=2")
        self.assertEqual(self.player.players, [("c", 6), ("a", 3),
                                               ("b", 2)],
                         "player status incorrect")
        self.assertEqual(self.player.current_player, "c",
                         "turn player's name incorrect")

    def test__received_next_turn(self):
        self.player.players = [("a", 5), ("b", 6)]
        self.player.current_player_index = 0
        self.player._received_next_turn()
        self.assertEqual(self.player.current_player, "b",
                         "incorrect turn player when simply going to the next "
                         "player")
        self.player._received_next_turn()
        self.assertEqual(self.player.current_player, "a",
                         "incorrect turn player when wrapping")

    def test__received_player_left(self):
        self.player.players = [("a", 5), ("b", 6)]
        self.player._received_player_left("a")
        self.assertEqual(self.player.players, [("b", 6)],
                         "failed to remove from multiple players correctly")
        self.player._received_player_left("b")
        self.assertEqual(self.player.players, [],
                         "failed to remove from single player correctly")

    def test__received_player_joined(self):
        self.player.players = [("a", None), ("b", None)]
        self.player._received_player_joined("c")
        self.assertEqual(self.player.players, [("a", None), ("b", None),
                                               ("c", None)],
                         "failed to add a player")
