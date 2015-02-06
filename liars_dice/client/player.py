"""

Functionality common to all players.

"""
from twisted.internet.protocol import ClientFactory

from twisted.protocols.basic import LineReceiver
from liars_dice import network_command, config_parse


class Player(LineReceiver):
    """A player instance.

    This class is intended to be subclassed by more specific player
    instances, such as humans or an AI instance.

    Attributes:
        username: A string with the player's username, or None if the player
            does not have one.
    """

    def __init__(self):
        self.username = None
        self._allow_username_change = True

    def lineReceived(self, line):

        # Parse message
        message = line.split(network_command.DELIMITER)
        command = message[0]
        if len(message) == 1:
            extra = None
        else:
            extra = message[1]

        # Delegate to the appropriate method
        if command == network_command.PLAYER_HAND:
            hand = sorted([int(die) for die in extra.split(",")])
            self.notification_hand(hand)

        elif command == network_command.PLAYER_STATUS:
            player_data = [(username, int(amount)) for username, amount in
                           (player.split("=") for player in extra.split(","))]
            self.notification_player_status(player_data)

        elif command == network_command.NEXT_TURN:
            self.notification_next_turn(extra)

        elif command == network_command.PLAYER_LEFT:
            self.notification_player_left(extra)

        elif command == network_command.PLAYER_JOINED:
            self.notification_player_joined(extra)

        elif command == network_command.CAN_START:
            self.notification_can_start()

        elif command == network_command.USERNAME:
            self._allow_username_change = True
            self.notification_username_request()

        elif command == network_command.PLAY:
            self.notification_play_request()

        elif command == network_command.BET:
            face, number = [int(n) for n in extra.split(",")]
            self.notification_bet(face, number)

        elif command == network_command.SPOT_ON:
            self.notification_spot_on()

        elif command == network_command.LIAR:
            self.notification_liar()

        elif command == network_command.PLAYER_LOST_DIE:
            self.notification_player_lost_die(extra)

        elif command == network_command.PLAYER_ELIMINATED:
            self.notification_eliminated(extra)

        elif command == network_command.NEXT_ROUND:
            self.notification_new_round()

        elif command == network_command.WINNER:
            self.notification_winner(extra)

        elif command == network_command.CHAT:
            delim = extra.index(",")
            username = extra[:delim]
            message = extra[delim + 1:]
            self.notification_chat(username, message)

    def send_username(self, username):
        """Register the player's username with the server.

        Args:
            username: A string with the player's username. Colons are not
                permitted in the username and will be automatically removed.
        """
        if self._allow_username_change:
            self.sendLine(
                network_command.USERNAME + network_command.DELIMITER +
                username.replace(
                    network_command.DELIMITER, ""))
            self.username = username
            self._allow_username_change = False

    def send_liar(self):
        """Send the server a "Liar" action."""
        self.sendLine(network_command.LIAR)

    def send_spot_on(self):
        """Send the server a "Spot On" action."""
        self.sendLine(network_command.SPOT_ON)

    def send_bet(self, face, number):
        """Send the server the player's bet.

        Args:
            face: An integer with the die value bet.
            number: An integer with the number of dice bet.
        """
        self.sendLine(network_command.BET + network_command.DELIMITER + str(
            face) + "," + str(number))

    def send_start(self):
        """Send a message to the server to start the game.

        This will have no effect if the player is not the lead player, or
        if there are not at least two players participating in the game.
        """
        # Checking the conditions for starting the game is done server-side
        self.sendLine(network_command.START)

    def send_chat(self, message):
        """Send a chat message to the server."""
        self.sendLine(network_command.CHAT + network_command.DELIMITER +
                      message)

    def notification_player_status(self, player_data):
        """Respond to being provided with game status.

        Intended to be overridden by subclasses (optional).

        Args:
            player_data: A list of tuples composed of player usernames with the
                number of dice they possess. The players are in turn order,
                but the first entry does not necessarily correspond to the
                whose turn it is (see notification_next_turn instead).
        """
        pass

    def notification_username_request(self):
        """Respond to a server's request for a username.

        Must be overridden by subclasses.
        """
        raise NotImplementedError

    def notification_play_request(self):
        """Respond to a server's request to make a play.

        Must be overridden by subclasses.
        """
        raise NotImplementedError

    def notification_next_turn(self, player):
        """Respond to the next turn being declared.

        Args:
            player: A string with the player's username whose turn it is.
        """
        pass

    def notification_hand(self, hand):
        """Respond to receiving a new hand."""
        pass

    def notification_bet(self, face, number):
        """Respond to the current turn player making a standard bet.

        Args:
            face: An integer with the die value bet.
            number: An integer with the number of dice bet.
        """
        pass

    def notification_spot_on(self):
        """Respond to the current turn player making a "Spot On" bet."""
        pass

    def notification_liar(self):
        """Respond to the current turn player making a "Liar" bet."""
        pass

    def notification_player_lost_die(self, player):
        """Respond to a player losing a die.

        Args:
            player: A string with the player's username whose turn it is.
        """
        pass

    def notification_eliminated(self, player):
        """Respond to a player being eliminated from the game.

        Args:
            player: A string with the player's username whose turn it is.
        """
        pass

    def notification_player_left(self, player):
        """Respond to a player leaving the game.

        Args:
            player: A string with the player's username whose turn it is.
        """
        pass

    def notification_player_joined(self, player):
        """Respond to a player joining the game.

        Args:
            player: A string with the player's username whose turn it is.
        """
        pass

    def notification_can_start(self):
        """Respond to being informed that one can start the game.

        Must be overridden by subclasses.
        """
        raise NotImplementedError

    def notification_new_round(self):
        """Respond to a new round commencing."""
        pass

    def notification_winner(self, player):
        """Respond to a player (string) winning the game.

        Args:
            player: A string with the player's username whose turn it is.
        """
        pass

    def notification_chat(self, username, message):
        """Respond to receiving a chat message.

        Args:
            username: A string with the username of the sender.
            message: A string containing the message.
        """
        pass


class PlayerFactory(ClientFactory):
    """Handle client connections."""

    def __init__(self, client):
        self.client = client

    def startedConnecting(self, connector):
        print ("Attempting to connect to the server at "
               "[{}]...".format(config_parse.host))

    def buildProtocol(self, addr):
        print "Connection established.\n"
        return self.client

    def clientConnectionLost(self, connector, reason):
        print "Connection to the server lost. Reason:", reason

    def clientConnectionFailed(self, connector, reason):
        print "Failed to connect. Reason:", reason

