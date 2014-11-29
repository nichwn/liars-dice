"""

Server to run the game.

"""
from twisted.internet.protocol import connectionDone, Factory
from twisted.protocols.basic import LineReceiver
from liars_dice.server.game import GameStatus


class LiarsGame(LineReceiver):
    """Handle client communication and game running."""

    def __init__(self):
        self.username = None

    def lineReceived(self, line):
        """Handle receiving messages from clients."""
        pass

    def connectionMade(self):
        """Handle making a connection to a client, and requesting a username."""
        pass

    def connectionLost(self, reason = connectionDone):
        """Handle connection failures."""
        pass

    def _received_username(self, username):
        """Set the client's username."""
        pass

    def send_message(self, message, client_usernames=None):
        """Send a message to all connected clients.

        message (string) is the message to send, and client_usernames is a
        list of all of the clients whose username are contained in it to whom
        the messages are sent. To send the message to all clients, it should
        be None instead.
        """
        pass

    def roll_new_round(self):
        """Roll a new round of the game."""
        pass

    def next_turn(self, next_player):
        """Inform clients of the next player's turn, where next_player
        (string) is the player whose turn it is.
        """
        pass

    def send_player_status(self):
        """Inform all clients of the game status (player names with
        the number of remaining dice).
        """
        pass


class LiarGameFactory(Factory):
    """Handle client connections and store the game status."""
    protocol = LiarsGame

    def __init__(self):
        self.clients = {}
        self.game = GameStatus()
        self.accept_connections = True
