from unittest import TestCase
import collections
from liars_dice.server.game import GameStatus, Hand


class TestGameStatus(TestCase):
    def setUp(self):
        self.status = GameStatus()
        self.status.players["test"] = Hand()
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

    def test_add_player(self):
        old_count = len(self.status.players)
        self.status.add_player("test2")
        new_count = len(self.status.players)
        self.assertEqual(new_count, old_count + 1,
                         "did not add a single player")
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
        self.status.remove_player("test2")
        self.assertEqual(self.status.dice_count, collections.Counter(
            self.status.players["test"].die_face()), "incorrect dice tally "
                                                     "for multiple players")
        self.assertEqual(len(self.status.players), 1,
                         "did not exclusively remove a single player from "
                         "multiple")
        self.assertTrue("test2" not in self.status.players,
                        "did not remove the correct player")
        self.assertEqual(self.status.dice_count, collections.Counter(
            self.status.players["test"].die_face()), "incorrect dice tally "
                                                     "for single player")
        self.status.remove_player("test")
        self.assertEqual(len(self.status.players), 0,
                         "did not exclusively remove a single player when "
                         "alone")
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
