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
        self.players = []
        self.current_player_index = None
        self.current_player = None
        self.username = None
        self.hand = None

    def lineReceived(self, line):
        # Interpret messages received from the server, and delegate to the
        # appropriate functionality.
        #
        # Overrides LineReceiver, and is not intended to be overridden itself.

        # Parse message
        message = line.split(":")
        command = message[0]
        if len(message) == 1:
            extra = None
        else:
            extra = message[1]

        # Delegate to the appropriate method
        if command == "hand":
            self._received_hand(extra)
            self.notification_hand()
        elif command == "player_status":
            self._received_player_status(extra)
        elif command == "next_turn":
            self._received_next_turn()
            self.notification_next_turn()
        elif command == "left":
            self._received_player_left(extra)
            self.notification_player_left(extra)
        elif command == "joined":
            self._received_player_joined()
            self.notification_player_joined()
        elif command == "username":
            self.notification_name_request()
        elif command == "play":
            self.notification_play_request()
        elif command == "bet":
            face, number = [int(n) for n in extra.split(",")]
            self.notification_bet(face, number)
        elif command == "spot_on":
            self.notification_spot_on()
        elif command == "liar":
            self.notification_spot_on()
        elif command == "player_lost_die":
            self.notification_player_lost_die(extra)
        elif command == "new_round":
            self.notification_new_round()
        elif command == "winner":
            self.notification_winner(extra)

    def send_name(self, username):
        """Send a username (string) to attempt to register with to the
        server.

        The following characters will be removed from the username if present:
            :
        """
        self.sendLine("username:" + username.replace(":", ""))
        self.username = username

    def send_liar(self):
        """Send the server a "Liar" action."""
        self.sendLine("liar")

    def send_spot_on(self):
        """Send the server a "Spot On" action."""
        self.sendLine("spot_on")

    def send_bet(self, face, number):
        """Send the server the player's bet,where face (int) is the die face
        and number (int) is the number of dice predicted.
        """
        self.sendLine("bet:" + str(face) + "," + str(number))

    def _received_hand(self, hand):
        # Update a player's hand based on server information.
        #
        # hand is a string of comma-separated face values.
        self.hand = sorted([int(die) for die in hand.split(",")])

    def _received_player_status(self, data):
        # Updates player information with that from the server.
        #
        # hand is a string of comma-separated values. The format of each of
        # the values is <player name>=<number of dice> in the order of play.
        # Players are space delimited.
        player_data = [player.split("=") for player in data.split(",")]
        self.players = [(username, int(face)) for username, face in player_data]
        self.current_player_index = 0
        self.current_player = self.players[self.current_player_index][0]

    def _received_next_turn(self):
        # Update the active player's turn
        self.current_player_index = ((self.current_player_index + 1) %
                                     len(self.players))
        self.current_player = self.players[self.current_player_index][0]

    def _received_player_left(self, player):
        # Update player information when a player (string) leaves the game.
        usernames = [p[0] for p in self.players]
        i = usernames.index(player)
        self.players = self.players[:i] + self.players[i + 1:]

    def _received_player_joined(self, player):
        # Update player information for when a player (string) joins the game.
        self.players.append((player, None))

    def notification_name_request(self):
        """Respond to a server's request for a username.

        Intended to be overridden by subclasses.
        """
        raise NotImplementedError

    def notification_play_request(self):
        """Respond to a server's request to make a play.

        Intended to be overridden by subclasses.
        """
        raise NotImplementedError

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
