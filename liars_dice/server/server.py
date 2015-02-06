"""

Server to run the game.

"""

import sys
from twisted.internet import reactor
from twisted.internet.protocol import connectionDone, Factory
from twisted.protocols.basic import LineReceiver
from twisted.python import log
from liars_dice import network_command, config_parse
from liars_dice.server.game import GameStatus


class LiarsGame(LineReceiver):
    """Handle client communication and game running."""

    def __init__(self):
        self._username = None

    def lineReceived(self, line):

        # Parse the received message
        message = line.split(network_command.DELIMITER)
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
                face, number = [int(x) for x in extra.split(",")]

                if self.factory.game.handle_bet(face, number):
                    log.msg("Turn player made the prediction: " + line)
                    self.send_message(line)
                    self.next_turn()
                else:
                    log.msg("Turn player attempted to predict: " + line +
                            " - but it was invalid")
                    self.send_message(network_command.PLAY,
                                      [self.factory.game.turn_player()])

    def connectionMade(self):

        # Request username
        if not self.factory.game_started:
            self.sendLine(network_command.USERNAME)
        else:
            self.transport.loseConnection()

    def connectionLost(self, reason=connectionDone):
        if self._username is not None:

            # No need to do anything if the player has already been
            # eliminated or the game is over
            if (self._username in self.factory.game.players and
                    self.factory.game.game_running):
                self.factory.game.remove_player(self._username)
                del self.factory.clients[self._username]
                log.msg(self._username + " disconnected from the server.")
                self.send_message(network_command.PLAYER_LEFT +
                                  network_command.DELIMITER + self._username)

            if self.factory.game_started:
                winner = self.check_winner()

                if not winner:
                    self.next_round()

            elif len(self.factory.game.players) > 0:
                self.send_can_start()

    def _received_username(self, username):
        """Set the client's username. Usernames cannot be changed once set.

        Args:
            username: A string with the username of the client.
        """
        if (username not in self.factory.clients and username and
                self._username is None):
            self.factory.clients[username] = self
            self.factory.game.add_player(username)
            log.msg(username + " joined the game.")
            self.send_message(network_command.PLAYER_JOINED +
                              network_command.DELIMITER + username)
            self._username = username
            self.send_player_status()

            # First player to join can start the game
            if len(self.factory.game.players) == 1:
                self.send_can_start()

        elif username in self.factory.clients:
            log.msg("A client attempted to join as '" + username +
                    "' but the username had already been taken.")
            self.sendLine(network_command.USERNAME)
        elif not username:
            log.msg("A client attempted to join with an empty username.")
            self.sendLine(network_command.USERNAME)

    def _received_start(self):
        """Start the game."""
        i = self.factory.game.player_order.index(self._username)

        # Only the first, still active, player can start the game
        # There must be at least 2 players
        # Game must not have started
        if (i == 0 and len(self.factory.game.player_order) >= 2 and
                not self.factory.game_started):
            log.msg("Game started on the request of: " + self._username)
            self.factory.game_started = True
            self.next_round()
        else:
            log.msg(
                self._username + " attempted to start the game, but they "
                                 "either did not have permission to do so, "
                                 "there were not enough players to start "
                                 "the game, or the game had already begun.")

    def send_message(self, message, client_usernames=None):
        """Send a message to all connected clients.

        Args:
            message: A string with the message to be sent.
            client_usernames: A list of all the usernames of the clients to
                whom the messages should be sent to, or None if the message
                should be sent to all clients.
        """
        if client_usernames is None:
            for username, client in self.factory.clients.iteritems():
                client.sendLine(message)

        else:
            for username in client_usernames:
                self.factory.clients[username].sendLine(message)

    def send_can_start(self):
        """Send a message informing the client who can start the game that they
        can start it.
        """
        can_start_player = self.factory.game.player_order[0]
        log.msg("Informing " + can_start_player +
                " that they can start the game...")
        self.send_message(network_command.CAN_START,
                          [self.factory.game.player_order[0]])

    def handle_non_bet(self, command):
        """Manage player actions that do not involve betting.

        Args:
            command: network_command.SPOT_ON or network_command.LIAR
                indicating whether the action is a 'Spot On' action, or a
                'Liar' one.
        """
        try:
            if command == network_command.SPOT_ON:
                losing_player, eliminated = self.factory.game.handle_spot_on()
            else:
                losing_player, eliminated = self.factory.game.handle_liar()

            # Announce action
            self.send_message(command)
            log.msg("Turn player made accusation: " + command)

            # Resolve die loss
            self.send_message(network_command.PLAYER_LOST_DIE +
                              network_command.DELIMITER + losing_player)

            winner = False
            if eliminated:
                self.send_message(network_command.PLAYER_ELIMINATED +
                                  network_command.DELIMITER + losing_player)

                # Determine if the game has been won
                winner = self.check_winner()

            if not winner:
                self.next_round()

        except RuntimeError:
            # No previous bet
            self.send_message(network_command.PLAY,
                              [self.factory.game.turn_player()])

    def next_round(self):
        """Roll a new round of the game."""
        # Announce new round
        self.factory.game.next_round()
        log.msg("New round")
        self.send_message(network_command.NEXT_ROUND)

        # Update the board situation
        self.send_player_status()
        self.send_player_hand()

        # Reset the previous bet
        self.factory.game.previous_bet = None

        # Announce the player whose turn it is
        next_player = self.factory.game.turn_player()
        log.msg("Start of Round Player: " + next_player)
        self.send_message(
            network_command.NEXT_TURN + network_command.DELIMITER +
            next_player)
        self.send_message(network_command.PLAY, [next_player])

    def next_turn(self):
        """Inform clients of the next player's turn."""
        self.factory.game.next_turn()
        next_player = self.factory.game.turn_player()
        log.msg("Next Turn: " + next_player)
        self.send_message(network_command.NEXT_TURN +
                          network_command.DELIMITER + next_player)
        self.send_message(network_command.PLAY, [next_player])

    def check_winner(self):
        """Checks if a player has won the game.

        If a player has won, informs all clients of their victory,
        disconnects them, and stops the reactor.

        Returns:
            A Boolean indicating whether a player has won the game.
        """
        winner = self.factory.game.get_winner()

        # Winner found
        if winner is not None:
            log.msg("Winner: " + winner)
            self.send_message(network_command.WINNER +
                              network_command.DELIMITER + winner)

            log.msg("Ending the game...")
            self.factory.game.stop()

            log.msg("Dropping client connections...")
            for _, client in self.factory.clients.iteritems():
                client.transport.loseConnection()

            log.msg("Starting a new game...")
            self.factory.__init__()

            return True
        return False

    def send_player_hand(self):
        """Inform all clients of their hand."""
        for player, hand in self.factory.game.get_player_hands():
            self.send_message(network_command.PLAYER_HAND +
                              network_command.DELIMITER +
                              ",".join([str(x) for x in hand]), [player])

    def send_player_status(self):
        """Inform all clients of the game status."""
        player_data = self.factory.game.get_player_status()
        message = (network_command.PLAYER_STATUS + network_command.DELIMITER +
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
reactor.listenTCP(config_parse.port, LiarGameFactory())
reactor.run()
