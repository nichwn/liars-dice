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
        self._username = None

    def lineReceived(self, line):

        # Parse the received message
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
        elif self.factory.game.turn_player() == self._username:
            if command in (network_command.SPOT_ON, network_command.LIAR):
                self.handle_non_bet(command)

            elif command == network_command.BET:
                self.send_message(line)
                log.msg("Turn player made the prediction: " + line)
                face, number = [int(x) for x in extra.split(",")]
                self.factory.game.handle_bet(face, number)
                self.next_turn()

    def connectionMade(self):

        # Request username
        if not self.factory.game_started:
            self.sendLine(network_command.USERNAME)
        else:
            self.transport.loseConnection()

    def connectionLost(self, reason=connectionDone):
        if self._username is not None:
            self.factory.game.remove_player(self._username)
            del self.factory.clients[self._username]
            log.msg(self._username + " disconnected from the server.")
            self.send_message(network_command.PLAYER_LEFT +
                              network_command.DELIMINATOR + self._username)
            self.roll_new_round()

    def _received_username(self, username):
        """Set the client's username. Usernames cannot be changed once set.

        Args:
            username: A string with the username of the client.
        """
        if username not in self.factory.clients and self._username is None:
            self.factory.clients[username] = self
            self.factory.game.add_player(username)
            log.msg(username + " joined the game.")
            self.send_message(network_command.PLAYER_JOINED +
                              network_command.DELIMINATOR + username)
            self._username = username
            self.send_player_status()
        elif username in self.factory.clients:
            log.msg("A client attempted to join as '" + username +
                    "' but the username had already been taken.")
            self.sendLine(network_command.USERNAME)

    def _received_start(self):
        """Start the game."""
        i = self.factory.game.player_order.index(self._username)

        # Only the first, still active, player can start the game
        # There must be at least 2 players
        if i == 0 and len(self.factory.game.player_order) >= 2:
            log.msg("Game started on the request of: " + self._username)
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

        Args:
            message: A string with the message to be sent.
            client_usernames: A list of all the usernames of the clients to
                whom the messages should be sent to, or None if the message
                should be sent to all clients.
        """
        for username, client in self.factory.clients.items():
            if client_usernames is None or username in client_usernames:
                client.sendLine(message)

    def handle_non_bet(self, command):
        """Manage player actions that do not involve betting.

        Args:
            command: network_command.SPOT_ON or network_command.LIAR
                indicating whether the action is a 'Spot On' action, or a
                'Liar' one.
        """
        try:
            if command == network_command.SPOT_ON:
                losing_player = self.factory.game.handle_spot_on()
            else:
                losing_player = self.factory.game.handle_liar()

            self.send_message(command)
            log.msg("Turn player made accusation: " + command)

            self.send_message(network_command.PLAYER_LOST_DIE +
                              network_command.DELIMINATOR + losing_player)
            self.next_turn()

        except RuntimeError:
            # No previous bet
            self.send_message(network_command.PLAY,
                              self.factory.game.turn_player())

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
        """Inform clients of the next player's turn."""
        self.factory.game.next_turn()
        next_player = self.factory.game.turn_player()
        log.msg("Next Turn: " + next_player)
        self.send_message(network_command.NEXT_TURN +
                          network_command.DELIMINATOR + next_player)
        self.send_message(network_command.PLAY, next_player)

    def send_player_status(self):
        """Inform all clients of the game status."""
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
