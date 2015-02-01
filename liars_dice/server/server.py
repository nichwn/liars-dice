"""

Server to run the game.

"""

import sys
from twisted.internet import reactor
from twisted.internet.protocol import connectionDone, Factory
from twisted.protocols.basic import LineReceiver
from twisted.python import log
from liars_dice import network_command
from liars_dice.server.game import GameStatus


class LiarsGame(LineReceiver):
    """Handle client communication and game running."""

    def __init__(self):
        self.username = None

    def lineReceived(self, line):
        """Handle receiving messages from clients."""
        message = line.split(network_command.DELIMINATOR)
        command = message[0]
        if len(message) == 1:
            extra = None
        else:
            extra = message[1]

        if command == network_command.USERNAME:
            self._received_username(extra)

        elif command == network_command.START:
            self._received_start()

        # These commands can only be performed by the turn player
        elif self.factory.game.turn_player() == self.username:
            if command == network_command.LIAR:
                self.send_message(line)
                log.msg("Turn player made a 'Liar' accusation.")
                losing_player = self.factory.game.handle_liar()
                self.send_message(network_command.PLAYER_LOST_DIE +
                                  network_command.DELIMINATOR + losing_player)
                self.next_turn()

            elif command == network_command.SPOT_ON:
                self.send_message(line)
                log.msg("Turn player predicted 'spot_on'.")
                losing_player = self.factory.game.handle_spot_on()
                self.send_message(network_command.PLAYER_LOST_DIE +
                                  network_command.DELIMINATOR + losing_player)
                self.next_turn()

            elif command == network_command.BET:
                self.send_message(line)
                log.msg("Turn player made the prediction: " + line)
                face, number = extra.split(",")
                self.factory.game.handle_bet(face, number)
                self.next_turn()

    def connectionMade(self):
        """Handle making a connection to a client, and requesting a username."""
        if not self.factory.game_started:
            self.sendLine(network_command.USERNAME)

    def connectionLost(self, reason=connectionDone):
        """Handle connection failures."""
        if self.username is not None:
            self.factory.game.remove_player(self.username)
            del self.factory.clients[self.username]
            log.msg(self.username + " disconnected from the server.")
            self.send_message(network_command.PLAYER_LEFT +
                              network_command.DELIMINATOR + self.username)
            self.roll_new_round()

    def _received_username(self, username):
        """Set the client's username."""
        if username not in self.factory.clients and self.username is None:
            self.factory.clients[username] = self
            self.factory.game.add_player(username)
            log.msg(username + " joined the game.")
            self.send_message(network_command.PLAYER_JOINED +
                              network_command.DELIMINATOR + username)
            self.username = username
            self.send_player_status()
        elif username in self.factory.clients:
            log.msg("A client attempted to join as '" + username +
                    "' but the username had already been taken.")
            self.sendLine(network_command.USERNAME)

    def _received_start(self):
        """Start the game."""
        i = self.factory.game.player_order.index(self.username)

        # Only the first, still active, player can start the game
        # There must be at least 2 players
        if i == 0 and len(self.factory.game.player_order) >= 2:
            log.msg("Game started on the request of: " + self.username)
            self.factory.game_started = True
            self.roll_new_round()
        else:
            log.msg(
                self.username + " attempted to start the game, but they "
                                "either did not have permission to do so, "
                                "or there were not enough players to start "
                                "the game.")

    def send_message(self, message, client_usernames=None):
        """Send a message to all connected clients.

        message (string) is the message to send, and client_usernames is a
        list of all of the usernames of all clients to whom the messages are to
        be sent. To send the message to all clients, pass None instead.
        """
        for username, client in self.factory.clients.items():
            if client_usernames is None or username in client_usernames:
                client.sendLine(message)

    def roll_new_round(self):
        """Roll a new round of the game."""
        self.factory.game.next_round()
        next_player = self.factory.game.turn_player()
        log.msg("New round")
        self.send_message(network_command.NEXT_ROUND)
        log.msg("Start of Round Player: " + next_player)
        self.send_player_status()
        self.send_message(
            network_command.NEXT_TURN + network_command.DELIMINATOR +
            next_player)
        self.send_message(network_command.PLAY, next_player)

    def next_turn(self):
        """Inform clients of the next player's turn, where next_player
        (string) is the player whose turn it is.
        """
        self.factory.game.next_turn()
        next_player = self.factory.game.turn_player()
        log.msg("Next Turn: " + next_player)
        self.send_message(self,
                          network_command.NEXT_TURN +
                          network_command.DELIMINATOR + next_player)
        self.send_message(network_command.PLAY, next_player)

    def send_player_status(self):
        """Inform all clients of the game status (player names with
        the number of remaining dice).
        """
        player_data = self.factory.game.get_player_status()
        message = (network_command.PLAYER_STATUS + network_command.DELIMINATOR +
                   ",".join(p + "=" + str(dice) for p, dice in player_data))

        # Send the message
        self.send_message(message)
        log.msg("Sent player status: " + message)


class LiarGameFactory(Factory):
    """Handle client connections and store the game status."""
    protocol = LiarsGame

    def __init__(self):
        self.clients = {}
        self.game = GameStatus()
        self.game_started = False


log.startLogging(sys.stdout)
reactor.listenTCP(9637, LiarGameFactory())
reactor.run()
