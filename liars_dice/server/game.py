"""

Handle the actual game components.

"""
from random import randint


class Die:
    """Manage a single die."""

    def __init__(self):
        self.value = None  # properly assigned in roll
        self.roll()

    def roll(self):
        """Roll the die."""
        self.value = randint(1, 6)


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
        return (die.value for die in self.hand)


class GameStatus:
    """Provide functionality for manipulating the game's status."""

    def __init__(self):
        pass

    def remove_die(self, player):
        """Remove a die from the player's hand.

        Return True if the player's hand becomes empty, else False.
        """
        pass

    def add_player(self, player):
        """Add a player to the game."""
        pass

    def remove_player(self, player):
        """Remove a player from the game."""
        pass

    def reroll_all(self):
        """Reroll the hands of all players."""
        pass

    def get_winner(self):
        """Return the player who has won the game, if any, else None."""
        pass