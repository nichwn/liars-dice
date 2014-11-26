"""

Handle the actual game components.

"""
from random import randint
import collections


class Die:
    """Manage a single die."""

    def __init__(self):
        self.face = None  # properly assigned in roll
        self.roll()

    def roll(self):
        """Roll the die."""
        self.face = randint(1, 6)


class Hand:
    """Manage a player's hand."""
    INITIAL_HAND_SIZE = 6

    def __init__(self):
        self.hand = []
        for i in xrange(self.INITIAL_HAND_SIZE):
            self.hand.append(Die())

    def have_die(self):
        """Return True if there is at least one die in the hand, else False."""
        return len(self.hand) != 0

    def reroll(self):
        """Reroll the hand."""
        for die in self.hand:
            die.roll()

    def die_face(self):
        """Return a sequence of all the die values in a hand."""
        return (die.face for die in self.hand)


class GameStatus:
    """Provide functionality for manipulating the game's status."""

    def __init__(self):
        self.players = {}
        self.dice_count = collections.Counter()

    def remove_die(self, player):
        """Remove a die from the player's hand.

        Return True if the player's hand becomes empty and removes them from
        the game, else False.
        """
        removed = self.players[player].hand.pop()
        self.dice_count -= collections.Counter((removed.face,))
        die_remains = self.players[player].have_die()

        # Remove eliminated players
        if not die_remains:
            self.remove_player(player)

        return die_remains

    def add_player(self, player):
        """Add a player to the game."""
        self.players[player] = Hand()
        self.dice_count += collections.Counter(self.players[player].die_face())

    def remove_player(self, player):
        """Remove a player from the game."""
        self.dice_count -= collections.Counter(self.players[player].die_face())
        del self.players[player]

    def reroll_all(self):
        """Reroll the hands of all players."""
        self.dice_count = collections.Counter()
        for hand in self.players.itervalues():
            hand.reroll()
            self.dice_count += collections.Counter(hand.die_face())

    def get_winner(self):
        """Return the player who has won the game, if any, else None."""
        remaining = self.players.keys()
        if len(remaining) == 1:
            return remaining[0]
        else:
            return None
