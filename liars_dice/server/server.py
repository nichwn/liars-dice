"""

Server to run the game.

"""

import sys
from twisted.internet.protocol import connectionDone, Factory
from twisted.protocols.basic import LineReceiver
from twisted.python import log
from liars_dice.server.game import GameStatus


class LiarsGame(LineReceiver):
    """Handle client communication and game running."""

    def __init__(self):
        self.username = None

    def lineReceived(self, line):
        """Handle receiving messages from clients."""
        message = line.split(":")
        command = message[0]
        if len(message) == 1:
            extra = None
        else:
            extra = message[1]

        # Anyone can send these messages, as long as the server is accepting
        # new connections
        if command == "username" and self.factory.accept_connections:
            self._received_username(extra)

        # These commands can only be performed by the turn player
        elif self.factory.game.turn_player() == self.username:
            if command == "liar":
                self.send_message(line)
                log.msg("Turn player made a 'Liar' accusation.")
                losing_player = self.game.handle_liar()
                self.send_message("player_lost_die:" + losing_player)
                self.next_turn()

            elif command == "spot_on":
                self.send_message(line)
                log.msg("Turn player predicted 'spot_on'.")
                losing_player = self.game.handle_spot_on()
                self.send_message("player_lost_die:" + losing_player)
                self.next_turn()

            elif command == "bet":
                self.send_message(line)
                log.msg("Turn player made the prediction: " + line)
                face, number = extra.split(",")
                self.game.handle_bet(face, number)
                self.next_turn()

    def connectionMade(self):
        """Handle making a connection to a client, and requesting a username."""
        if self.factory.accept_connections:
            self.sendLine("username")

    def connectionLost(self, reason=connectionDone):
        """Handle connection failures."""
        if self.username is not None:
            self.factory.game.remove_player(self.username)
            del self.factory.clients[self.username]
            self.send_message("left:" + self.username)
            log.msg(self.username + " disconnected from the server.")
            self.roll_new_round()

    def _received_username(self, username):
        """Set the client's username."""
        if username not in self.factory.clients and self.username is not None:
            self.factory.clients[username] = self
            self.factory.game.add_player(username)
            log.msg(username + " joined the game.")
            self.username = username
        elif username in self.factory.clients:
            log.msg("A client attempted to join as '" + username +
                    "' but the username had already been taken.")
            self.sendLine("username")

    def send_message(self, message, client_usernames=None):
        """Send a message to all connected clients.

        message (string) is the message to send, and client_usernames is a
        list of all of the clients whose username are contained in it to whom
        the messages are sent. To send the message to all clients, it should
        be None instead.
        """
        for username, client in self.factory.clients:
            if client_usernames is None or username in client_usernames:
                client.sendLine(message)

    def roll_new_round(self):
        """Roll a new round of the game."""
        self.game.next_round()
        next_player = self.game.turn_player()
        log.msg("New round")
        self.send_message("new_round")
        self.send_player_status()
        self.send_message("next_turn:" + next_player)
        log.msg("Start of Round Player: " + next_player)

    def next_turn(self):
        """Inform clients of the next player's turn, where next_player
        (string) is the player whose turn it is.
        """
        self.game.next_turn()
        next_player = self.game.turn_player()
        log.msg("Next Turn: " + next_player)
        self.send_message(self, "next_turn:" + next_player)

    def send_player_status(self):
        """Inform all clients of the game status (player names with
        the number of remaining dice).
        """
        player_data = self.factory.game.get_player_status()
        message = "player_status:" + ",".join(["=".join(status) for status in
                                               player_data])

        # Send the message
        self.send_message(message)
        log.msg("Sent player status: " + message)


class LiarGameFactory(Factory):
    """Handle client connections and store the game status."""
    protocol = LiarsGame

    def __init__(self):
        self.clients = {}
        self.game = GameStatus()
        self.accept_connections = True


log.startLogging(sys.stdout)
