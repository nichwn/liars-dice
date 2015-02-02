"""

A simple bot that can connect to the server and play the game. It cannot start
the game, and will automatically disconnect from the server if given that
power.

Bot strategy:
    if there is no previous bet
        bets -> face 1 - 6 randomly, number 1
    if the number of previous dice bet == total / 6
        30% -> Spot On
        70% -> Play as normal
    if the number of previous dice bet == total / 6 + 1
        60% -> Liar
        40% -> Play as normal
    if the number of previous dice bet >= toal / 6 + 2
        80% -> Liar
        20% -> Play as normal
    else (this is 'Play as normal')
        if face == 6
            increase number of dice by 1
        else
            30% -> increase number of dice by 1

        pick random valid face
"""
from twisted.internet import reactor
from liars_dice.client.player import Player, PlayerFactory


class SimpleBot(Player):
    """A bot instance as given by the module header."""

    def __init__(self):
        Player.__init__(self)
        self.previous_face = None
        self.previous_number = None
        self.desired_username = "Simple Bot"
        self.total_dice = None  # this value is unused - set later

    def notification_player_status(self, player_data):
        self.total_dice = sum(n for _, n in player_data)

    def notification_username_request(self):
        self.sendLine(self.desired_username)

        # Add an underscore in case the username is taken and a new username
        # has to be resent
        self.desired_username += "_"

    def notification_play_request(self):
        pass

    def notification_bet(self, face, number):
        self.previous_face = face
        self.previous_number = number

    def notification_new_round(self):
        self.previous_face = None
        self.previous_number = None

    def notification_can_start(self):
        self.transport.loseConnection()


if __name__ == "__main__":
    PORT = 9637
    host = raw_input("Host: ")
    reactor.connectTCP(host, PORT, PlayerFactory(SimpleBot()))
    reactor.run()
