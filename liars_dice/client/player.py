"""

Functionality common to all players.

"""

from twisted.internet.protocol import connectionDone
from twisted.protocols.basic import LineReceiver


class Player(LineReceiver):
    """A player instance.

    This class is intended to be subclassed by more specific player
    instances, such as humans or an AI instance.
    """

    def __init__(self):
        pass

    def lineReceived(self, line):
        # Interpret messages received from the server, and delegate to the
        # appropriate functionality.
        #
        # Overrides LineReceiver, and is not intended to be overridden itself.
        pass

    def send_name(self, username):
        """Send a username (string) to attempt to register with to the
        server.
        """
        pass

    def send_liar(self):
        """Send the server a "Liar" action."""
        pass

    def send_spot_on(self):
        """Send the server a "Spot On" action."""
        pass

    def send_bet(self, face, number):
        """Send the server the player's bet,where face (int) is the die face
        and number (int) is the number of dice predicted.
        """
        pass

    def _received_hand(self, hand):
        # Update a player's hand based on server information.
        #
        # hand is a string of comma-separated face values.
        pass

    def _received_player_status(self, data):
        # Updates player information with that from the server.
        #
        # hand is a string of comma-separated values. The format of each of
        # the values is <player name>=<number of dice> in the order of play.
        pass

    def _received_next_turn(self):
        # Update the active player's turn
        pass

    def _received_player_left(self, player):
        # Update player information when a player (string) leaves the game.
        pass

    def _received_player_joined(self, player):
        # Update player information for when a player (string) joins the game.
        pass

    def notification_name_request(self):
        """Respond to a server's request for a username.

        Intended to be overridden by subclasses.
        """
        pass

    def notification_play_request(self):
        """Respond to a server's request to make a play.

        Intended to be overridden by subclasses.
        """
        pass

    def notification_next_turn(self):
        """Respond to the next turn being declared.

        Intended to be overridden by subclasses.
        """
        pass

    def notification_hand(self):
        """Respond to receiving a new hand.

        Intended to be overridden by subclasses.
        """
        pass

    def notification_bet(self, face, number):
        """Respond to the current turn player making a standard bet.

        face (int) is the face of the die value, and number (int) is the
        number of dice predicted.

        Intended to be overridden by subclasses.
        """
        pass

    def notification_spot_on(self):
        """Respond to the current player making a "Spot On" bet.

        Intended to be overridden by subclasses.
        """
        pass

    def notification_liar(self):
        """Respond to the current player making a "Liar" bet.

        Intended to be overridden by subclasses.
        """
        pass

    def notification_player_lost_die(self, string):
        """Respond to a player (string) losing a die.

        Intended to be overridden by subclasses.
        """
        pass

    def notification_player_left(self, player):
        """Respond to a player (string) leaving the game.

        Intended to be overridden by subclasses.
        """
        pass

    def notification_player_joined(self, player):
        """Respond to a player (string) joining the game.

        Intended to be overridden by subclasses.
        """
        pass

    def notification_new_round(self):
        """Respond to a new round commencing.

        Intended to be overridden by subclasses.
        """
        pass

    def notification_winner(self, player):
        """Respond to a player (string) winning the game.

        Intended to be overridden by subclasses.
        """
        pass
