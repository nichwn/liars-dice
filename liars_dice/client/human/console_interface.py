"""

An interface for a human player to play the game.

"""
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from liars_dice.client.player import Player


class ConsoleHuman(Player):
    """A player instance."""

    def notification_player_status(self, player_data):
        print "Players\tDice"
        for player, number in player_data:
            print player + "\t" + str(number)

    def notification_name_request(self):
        print "Username requested."
        username = raw_input("Username: ")
        self.send_name(username)

    def notification_play_request(self):
        print "It's your turn. Choose a play to make."
        print ("Type 'Liar!' to make a liar declaration, or 'Spot On!' for a "
               "spot on declaration.")
        print ("Otherwise, provide two space-delimited numbers, where the "
               "first is the die face, and the second the number predicted.")

        invalid = True
        while invalid:
            play = raw_input("Command: ").lower()
            if play.startswith("liar"):
                self.send_liar()
                invalid = False
            elif play.startswith("spot on"):
                self.send_spot_on()
                invalid = False
            elif len(play.split()) == 2:
                try:
                    face, number = ((int(face), int(number))
                                    for face, number in play.split())
                    self.send_bet(face, number)
                    invalid = False
                except ValueError:
                    pass

            if invalid:
                "Could not parse the command. Did you type it in correctly?"

    def notification_next_turn(self, player):
        msg = "\n" + player
        if player[-1] == "s":
            msg += "'"
        else:
            msg += "'s"
        msg += " turn."
        print msg

    def notification_hand(self):
        print "New hand received:\t", self.hand

    def notification_bet(self, face, number):
        print "Bet made."
        print "Face:\t" + str(face)
        print "Number:\t" + str(number)

    def notification_spot_on(self):
        print "'Spot On!' declared."

    def notification_liar(self):
        print "'Liar!' declared."

    def notification_player_lost_die(self, player):
        print player + " lost a die."

    def notification_player_left(self, player):
        print player + " left the game."

    def notification_player_joined(self, player):
        print player + " has joined the game."

    def notification_new_round(self):
        print "\nA new round has begun."

    def notification_winner(self, player):
        print "\n" + player + " has won the game."
        if self.username == player:
            print "Congratulations " + player


class ConsoleHumanFactory(ClientFactory):
    """Handle client connections and store the game status."""

    def startedConnecting(self, connector):
        print "Attempting to connect to the server..."

    def buildProtocol(self, addr):
        print "Connection established.\n"
        return ConsoleHuman()

    def clientConnectionLost(self, connector, reason):
        print "Connection to the server lost. Reason:", reason

    def clientConnectionFailed(self, connector, reason):
        print "Failed to connect. Reason:", reason


if __name__ == "__main__":
    PORT = 9637
    host = raw_input("Host: ")
    reactor.connectTCP(host, 9637, ConsoleHumanFactory())
    reactor.run()
