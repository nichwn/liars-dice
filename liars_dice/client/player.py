"""

Functionality common to all players.

"""

from twisted.protocols.basic import LineReceiver
from liars_dice import network_command


class Player(LineReceiver):
    """A player instance.

    This class is intended to be subclassed by more specific player
    instances, such as humans or an AI instance.
    """

    def __init__(self):
        self.username = None
        self.hand = None
        self.allow_username_change = True

    def lineReceived(self, line):

        # Parse message
        message = line.split(network_command.DELIMINATOR)
        command = message[0]
        if len(message) == 1:
            extra = None
        else:
            extra = message[1]

        # Delegate to the appropriate method
        if command == network_command.PLAYER_HAND:
            self._received_hand(extra)
            self.notification_hand()
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
        elif command == network_command.USERNAME:
            self.allow_username_change = True
            self.notification_name_request()
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
        elif command == network_command.NEXT_ROUND:
            self.notification_new_round()
        elif command == network_command.WINNER:
            self.notification_winner(extra)

    def send_name(self, username):
        """Send a username (string) to attempt to register with to the
        server.

        The following characters will be removed from the username if present:
            :
        """
        if self.allow_username_change:
            self.sendLine(
                network_command.USERNAME + network_command.DELIMINATOR +
                username.replace(
                    network_command.DELIMINATOR, ""))
            self.username = username
            self.allow_username_change = False

    def send_liar(self):
        """Send the server a "Liar" action."""
        self.sendLine(network_command.LIAR)

    def send_spot_on(self):
        """Send the server a "Spot On" action."""
        self.sendLine(network_command.SPOT_ON)

    def send_bet(self, face, number):
        """Send the server the player's bet,where face (int) is the die face
        and number (int) is the number of dice predicted.
        """
        self.sendLine(network_command.BET + network_command.DELIMINATOR + str(
            face) + "," + str(number))

    def send_start(self):
        """Send a message to the server to start the game.

        Will only work if the player is the lead player, and there are at least
        two players who have joined the game.
        """
        # Checking the conditions for starting the game is done server-side
        self.sendLine(network_command.START)

    def _received_hand(self, hand):
        # Update a player's hand based on server information.
        #
        # hand is a string of comma-separated face values.
        self.hand = sorted([int(die) for die in hand.split(",")])

    def notification_player_status(self, player_data):
        """Respond to being provided with game status.

        player_data is a list of tuples composed of player names and the number
        of dice they possess.

        The players are in turn order, but the first entry does not
        necessarily correspond to the next player to play (see
        notification_next_turn instead).
        """
        pass

    def notification_name_request(self):
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

        player (string) is the name of the next player to act.

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

    def notification_player_lost_die(self, player):
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
