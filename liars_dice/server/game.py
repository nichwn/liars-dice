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

    def turn_player(self):
        """Return the current turn player (string, or None if the game has
        ended).
        """
        pass

    def get_player_status(self):
        """Return a list of tuples, where the tuple is a player's name
        followed by the number of dice they have.

        The order is in turn order, but the first player does not
        necessarily correspond with the next player to play.
        """
        pass

    def handle_bet(self, face, number):
        """Resolve bets made by the turn player."""
        pass

    def handle_liar(self):
        """Resolve liar declarations made by the turn player.

        Return the name of the losing player.
        """
        pass

    def handle_spot_on(self):
        """Handle spot on declarations made by the turn player.

        Return the name of the losing player.
        """
        pass

    def next_round(self):
        """Moves play to the next round."""
        pass

    def next_turn(self):
        """Move play to the next turn."""
        pass
