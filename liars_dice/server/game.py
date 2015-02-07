"""

Handle the actual game components.

"""
from random import randint
import collections


class Die:
    """Manage a single die.

    Attributes:
        face: An integer between 1 - 6 (inclusive) with the die's value.
    """

    def __init__(self):
        self.face = None  # properly assigned in roll
        self.roll()

    def roll(self):
        """Roll the die. Changes the value of the face attribute."""
        self.face = randint(1, 6)


class Hand:
    """Manage a player's hand.

    Attributes:
        hand: A list containing the dice in a player's hand.
    """
    INITIAL_HAND_SIZE = 5

    def __init__(self):
        self.hand = []
        for i in xrange(self.INITIAL_HAND_SIZE):
            self.hand.append(Die())

    def have_die(self):
        """Determine whether the player has at least 1 die in their hand.

        Returns:
            A Boolean indicating whether the player has at least 1 die or not.
        """
        return len(self.hand) != 0

    def roll(self):
        """Roll all the dice in the hand."""
        for die in self.hand:
            die.roll()

    def die_face(self):
        """Return a sequence of all the die values in a hand.

        Returns:
            A list of integers with the face value of all the dice.
        """
        return [die.face for die in self.hand]


class GameStatus:
    """Provide functionality for manipulating the game's status.

    Args:
        players: A dictionary of strings of players mapping to their
            corresponding Hand object.
        player_order: A list of players in turn order. However, the turn player
            is not necessarily the first element.
        previous_bid: A tuple of 2 integers, indicating the die face and
            number of the previous bid.
        game_running: A Boolean indicating whether the game is still
            running.
    """

    def __init__(self):
        self.players = {}
        self.player_order = []
        self._round_player_index = -1  # used in round-related methods
        self._turn_player_index = -1  # used in round and turn-related methods
        self._dice_count = collections.Counter()
        self.previous_bid = None  # after bids are made, will be (face, number)
        self.game_running = True

    def remove_die(self, player):
        """Remove a die from the player's hand.

        Args:
            player: A string with the username of the player to be removed.

        Returns:
            A Boolean indicating whether the player lost their last die and
            has been removed from the game.
        """
        removed = self.players[player].hand.pop()
        self._dice_count -= collections.Counter((removed.face,))
        die_remains = self.players[player].have_die()

        # Remove eliminated players
        if not die_remains:
            self.remove_player(player)
            return True
        return False

    def add_player(self, player):
        """Add a player to the game.

        Args:
            player: A string with the username of the player to be added.
        """
        self.players[player] = Hand()
        self.player_order += (player,)
        self._dice_count += collections.Counter(self.players[player].die_face())

    def remove_player(self, player):
        """Remove a player from the game.

        Args:
            player: A string with the username of the player to be removed.
        """
        self._dice_count -= collections.Counter(self.players[player].die_face())

        # Adjust to handle turn being removed
        if self.turn_player() == player:
            self._turn_player_index -= 1

        # Round players
        round_index = self._round_player_index % len(self.player_order)
        if self.player_order[round_index] == player:
            self._round_player_index -= 1

        del self.players[player]
        order_index = self.player_order.index(player)
        self.player_order = (self.player_order[:order_index] +
                             self.player_order[order_index + 1:])

    def roll_all(self):
        """Roll the hands of all players."""
        self._dice_count = collections.Counter()
        for hand in self.players.itervalues():
            hand.roll()
            self._dice_count += collections.Counter(hand.die_face())

    def get_winner(self):
        """Determine the winner of the game, if any.

        Returns:
            A string with the username of the winning player, or None if there
            is no such player.
        """
        remaining = self.players.keys()
        if len(remaining) == 1:
            return remaining[0]
        else:
            return None

    def turn_player(self):
        """Determine the player whose turn it is.

        Returns:
            A string with the username of the current turn player.
        """
        i = self._turn_player_index % len(self.player_order)
        return self.player_order[i]

    def turn_player_previous(self):
        """Determine the player whose turn it was last turn.

        Calling this immediately after a new round has begun will give an
        incorrect result.

        Returns:
            A string with the username of the previous turn player.
        """
        i = (self._turn_player_index - 1) % len(self.player_order)
        return self.player_order[i]

    def get_player_hands(self):
        """Provide information on player hands.

        Returns:
            A sequence of (string, list of integers) tuples, of player
            usernames and the face value of the dice in their hand.
        """
        return ((player, self.players[player].die_face())
                for player in self.player_order)

    def get_player_status(self):
        """Provide information on the current game state.

        Returns:
            A list of tuples, where the tuple is a player's username
            followed by the number of dice they have.

            The order is in turn order, but the first player does not
            necessarily correspond with the turn player.
        """
        return [(player, len(self.players[player].hand))
                for player in self.player_order]

    def handle_bid(self, face, number):
        """Resolve bids made by the turn player.

        Args:
            face: An integer with the die value bid.
            number: An integer with the number of dice bid.

        Returns:
            A Boolean indicating whether the bid was valid.
        """
        # Grab previous bid
        if self.previous_bid is not None:
            old_face, old_number = self.previous_bid
        else:
            # allows any combination of face and number that are in the
            # valid range
            old_face, old_number = (-1, -1)

        # Handle the current bid
        valid_range = number >= 1 and 1 <= face <= 6
        allowed_bid = (number > old_number or
                       (face > old_face and number == old_number))
        if valid_range and allowed_bid:
            self.previous_bid = (face, number)
            return True
        else:
            return False

    def handle_liar(self):
        """Resolve liar declarations made by the turn player.

        Returns:
            A tuple composed of a string with the username of the player who
            lost a die, and a Boolean indicating whether the player lost their
            last die and has hence been eliminated.

        Raises:
            RuntimeError: No previous bid has been made.
        """
        if self.previous_bid is None:
            raise RuntimeError("No previous bid has been made.")
        face, number = self.previous_bid

        if number <= self._dice_count[face]:
            player = self.turn_player()
        else:
            player = self.turn_player_previous()

        eliminated = self.remove_die(player)
        return player, eliminated

    def handle_spot_on(self):
        """Handle spot on declarations made by the turn player.

        Returns:
            A tuple composed of a string with the username of the player who
            lost a die, and a Boolean indicating whether the player lost their
            last die and has hence been eliminated.

        Raises:
            RuntimeError: No previous bid has been made.
        """
        if self.previous_bid is None:
            raise RuntimeError("No previous bid has been made.")
        face, number = self.previous_bid

        if number != self._dice_count[face]:
            player = self.turn_player()
        else:
            player = self.turn_player_previous()

        eliminated = self.remove_die(player)
        return player, eliminated

    def next_round(self):
        """Move play to the next round."""
        self._round_player_index += 1
        self._turn_player_index = self._round_player_index
        self.roll_all()

    def next_turn(self):
        """Move play to the next turn."""
        self._turn_player_index += 1

    def stop(self):
        """Stops the game."""
        self.game_running = False
