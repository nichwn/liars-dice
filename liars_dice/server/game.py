"""

Handle the actual game components.

"""


class Die:
    """Manage a single die."""

    def __init__(self):
        pass

    def roll(self):
        """Roll the die."""
        pass


class Hand:
    """Manage a player's hand."""

    def __init__(self):
        pass

    def have_die(self):
        """Return True if there is at least one die in the hand, else False."""
        pass

    def reroll(self):
        """Reroll the hand."""
        pass

    def die_face(self, hand):
        """Return a sequence of all the die values in a hand."""
        pass


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