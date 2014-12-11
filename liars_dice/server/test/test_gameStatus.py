from unittest import TestCase
import collections
from liars_dice.server.game import GameStatus, Hand, Die


class TestGameStatus(TestCase):
    def setUp(self):
        self.status = GameStatus()
        self.status.players["test"] = Hand()
        self.status.player_order = ("test",)
        self.status.dice_count = collections.Counter(
            self.status.players["test"].die_face())

    def test_remove_die(self):
        old_len = len(self.status.players["test"].hand)
        self.status.remove_die("test")
        new_len = len(self.status.players["test"].hand)
        self.assertEqual(new_len, old_len - 1,
                         "did not remove a single die from the hand only")
        self.assertEqual(self.status.dice_count, collections.Counter(
            self.status.players["test"].die_face()), "incorrect dice tally")

        self.status = GameStatus()
        self.status.players["singledie"] = Hand()
        self.status.players["singledie"].hand = [Die()]
        self.status.player_order = ["singledie", ]
        self.status.remove_die("singledie")
        self.assertEqual(len(self.status.players), 0,
                         "did not remove the player")
        self.assertEqual(len(self.status.player_order), 0,
                         "did not adjust the player_order")

    def test_add_player(self):
        old_count = len(self.status.players)
        self.status.add_player("test2")
        new_count = len(self.status.players)
        self.assertEqual(new_count, old_count + 1,
                         "did not add a single player")
        self.assertEqual(len(self.status.player_order), new_count,
                         "did not add the player to the turn order")
        self.assertIsInstance(self.status.players["test2"], Hand,
                              "failed to create a hand")
        self.assertEqual(self.status.dice_count, collections.Counter(
            self.status.players["test"].die_face()) + collections.Counter(
            self.status.players["test2"].die_face()), "failed to tally dice")

    def test_remove_player(self):
        self.status.add_player("test2")
        self.assertEqual(len(self.status.players), 2,
                         "test case setup does not have the expected two "
                         "players")
        self.assertEqual(len(self.status.player_order), 2,
                         "test case setup does not have the expected two "
                         "player turn order")
        self.status.remove_player("test2")
        self.assertEqual(self.status.dice_count, collections.Counter(
            self.status.players["test"].die_face()), "incorrect dice tally "
                                                     "for multiple players")
        self.assertEqual(len(self.status.players), 1,
                         "did not exclusively remove a single player from "
                         "multiple")
        self.assertEqual(len(self.status.player_order), 1,
                         "did not remove the player from the turn order (2 -> "
                         "1)")
        self.assertTrue("test2" not in self.status.players,
                        "did not remove the correct player")
        self.assertTrue("test2" not in self.status.player_order,
                        "did not remove the correct player from turn order")
        self.assertEqual(self.status.dice_count, collections.Counter(
            self.status.players["test"].die_face()), "incorrect dice tally "
                                                     "for single player")
        self.status.remove_player("test")
        self.assertEqual(len(self.status.players), 0,
                         "did not exclusively remove a single player when "
                         "alone")
        self.assertEqual(len(self.status.player_order), 0,
                         "did not remove the player from the turn order (1 -> "
                         "0)")
        self.assertEqual(self.status.dice_count, collections.Counter(),
                         "incorrect dice tally for no players")

    def test_reroll_all(self):
        old_count = len(self.status.players["test"].hand)
        self.status.reroll_all()
        self.assertIsInstance(self.status.players["test"], Hand,
                              "no hand found")
        new_count = len(self.status.players["test"].hand)
        self.assertEqual(new_count, old_count, "hand size changed")
        self.assertEqual(self.status.dice_count, collections.Counter(
            self.status.players["test"].die_face()), "incorrect dice tally "
                                                     "for single player")

    def test_get_winner(self):
        self.status.players["test2"] = Hand()
        self.assertIs(self.status.get_winner(), None,
                      "provided winner when there is no winner")
        del self.status.players["test2"]
        self.assertEqual(self.status.get_winner(), "test",
                         "did not provide the correct winner, when there is a "
                         "winner")

    def test_turn_player(self):
        self.status.add_player("test2")
        self.status.turn_player_index = 0
        self.assertEqual(self.status.turn_player(), "test",
                         "incorrect turn player (original player)")
        self.status.turn_player_index = 1
        self.assertEqual(self.status.turn_player(), "test2",
                         "incorrect turn player added player)")

    def test_handle_bet(self):
        self.status.handle_bet(2, 4)
        self.assertEqual(self.status.previous_bet, (2, 4),
                         "incorrect previous bet")

    def test_handle_liar(self):
        self.status.turn_player_index = 0
        self.status.add_player("test2")
        self.status.handle_bet(2, 4)
        self.status.dice_count = collections.Counter([2, 2, 2, 2, 1, 1, 3, 5])
        self.assertEqual(self.status.handle_liar(), "test",
                         "Wrong player (incorrect guess)")

        self.status.handle_bet(2, 5)
        self.status.dice_count = collections.Counter([2, 2, 2, 2, 1, 1, 3, 5])
        self.assertEqual(self.status.handle_liar(), "test2",
                         "Wrong player (correct guess)")

    def test_handle_spot_on(self):
        self.status.turn_player_index = 0
        self.status.add_player("test2")
        self.status.handle_bet(2, 4)
        self.status.dice_count = collections.Counter([2, 2, 2, 2, 1, 1, 3, 5])
        self.assertEqual(self.status.handle_spot_on(), "test2",
                         "Wrong player (correct guess)")

        self.status.handle_bet(2, 5)
        self.status.dice_count = collections.Counter([2, 2, 2, 2, 1, 1, 3, 5])
        self.assertEqual(self.status.handle_spot_on(), "test",
                         "Wrong player (incorrect guess)")

