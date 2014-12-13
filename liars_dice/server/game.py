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
        self.player_order = []
        self.round_player_index = -1  # handled in round-related methods
        self.turn_player_index = -1  # handled in round and turn-related methods
        self.dice_count = collections.Counter()
        self.previous_bet = None  # after bets are made, will be (face, number)

    def remove_die(self, player):
        """Remove a die from the player's hand."""
        removed = self.players[player].hand.pop()
        self.dice_count -= collections.Counter((removed.face,))
        die_remains = self.players[player].have_die()

        # Remove eliminated players
        if not die_remains:
            self.remove_player(player)

    def add_player(self, player):
        """Add a player to the game."""
        self.players[player] = Hand()
        self.player_order += (player,)
        self.dice_count += collections.Counter(self.players[player].die_face())

    def remove_player(self, player):
        """Remove a player from the game."""
        self.dice_count -= collections.Counter(self.players[player].die_face())

        # Adjust to handle turn being removed
        if self.turn_player() == player:
            self.turn_player_index -= 1

        # Round players
        round_index = self.round_player_index % len(self.player_order)
        if self.player_order[round_index] == player:
            self.round_player_index -= 1

        del self.players[player]
        order_index = self.player_order.index(player)
        self.player_order = (self.player_order[:order_index] +
                             self.player_order[order_index + 1:])

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
        i = self.turn_player_index % len(self.player_order)
        return self.player_order[i]

    def turn_player_previous(self):
        """Return the previous turn player (string, or None if the game has
        ended).
        """
        i = (self.turn_player_index - 1) % len(self.player_order)
        return self.player_order[i]

    def get_player_status(self):
        """Return a list of tuples, where the tuple is a player's name
        followed by the number of dice they have.

        The order is in turn order, but the first player does not
        necessarily correspond with the next player to play.
        """
        return [(player, len(self.players[player].hand))
                for player in self.player_order]

    def handle_bet(self, face, number):
        """Resolve bets made by the turn player.

        Return True if the bet is valid, else False.
        """
        # Grab previous bet
        if self.previous_bet is not None:
            old_face, old_number = self.previous_bet
        else:
            old_face, old_number = (1, 0)

        # Handle the current bet
        correct_range = number >= 1 and 1 <= face <= 6
        allowed_bet = (number > old_number or
                       (face > old_face and number == old_number))
        if correct_range and allowed_bet:
            self.previous_bet = (face, number)
            return True
        else:
            return False

    def handle_liar(self):
        """Resolve liar declarations made by the turn player.

        Return the name of the losing player.
        """
        face, number = self.previous_bet
        if number <= self.dice_count[face]:
            player = self.turn_player()
        else:
            player = self.turn_player_previous()

        self.remove_die(player)
        return player

    def handle_spot_on(self):
        """Handle spot on declarations made by the turn player.

        Return the name of the losing player.
        """
        face, number = self.previous_bet
        if number != self.dice_count[face]:
            player = self.turn_player()
        else:
            player = self.turn_player_previous()

        self.remove_die(player)
        return player

    def next_round(self):
        """Moves play to the next round."""
        self.round_player_index += 1
        self.turn_player_index = self.round_player_index

    def next_turn(self):
        """Move play to the next turn."""
        self.turn_player_index += 1
