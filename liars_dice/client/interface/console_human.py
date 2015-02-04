"""

An interface for a human player to play the game via a console.

"""
import re
from twisted.internet import reactor
from liars_dice import config_parse
from liars_dice.client.player import Player, PlayerFactory


class ConsoleHuman(Player):
    """A player instance."""

    def __init__(self):
        Player.__init__(self)

        self._display_instructions = True  # display command instructions

    def notification_player_status(self, player_data):

        # Display message
        print "Players\tDice"
        for player, number in player_data:
            print player + "\t" + str(number)

    def notification_username_request(self):
        print "Username requested."
        username = raw_input("Username: ")
        self.send_name(username)
        print

    def notification_play_request(self):
        if self._display_instructions:
            print "It's your turn. Choose a play to make."
            print ("Type 'Liar!' to make a liar declaration, or 'Spot On!' "
                   "for a spot on declaration.")
            print ("Otherwise, provide two space delimited numbers, where the "
                   "first is the die face, and the second the number "
                   "predicted.")
            print "Your hand: ", self.hand
            self._display_instructions = False

        invalid = True
        while invalid:
            play = raw_input("Command: ")
            if re.match('liar!?', play, re.IGNORECASE):
                self.send_liar()
                invalid = False
            elif re.match('spot on!?', play, re.IGNORECASE):
                self.send_spot_on()
                invalid = False
            elif len(play.split()) == 2:
                try:
                    face, number = [int(n) for n in play.split()]
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

        self._display_instructions = True

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

    def notification_eliminated(self, player):
        print
        if player == self.username:
            print ("You have run out of dice and been eliminated from the "
                   "game. Better luck next time!")
        else:
            print (player + " lost their last die, and has been eliminated "
                            "from the game.")

    def start_prompt(self):
        """Prompt the player as to whether they would like to start the
        game.
        """
        invalid = True
        while invalid:
            response = (raw_input("Would you like to start the game "
                                  "[Y/n]?").lower())

            if response == "y" or response == "yes":
                self.sendLine("start")
                invalid = False
            elif response == "n" or response == "no":
                invalid = False
            else:
                print "Please type 'Y' or 'n'."

    def notification_player_left(self, player):
        print player + " left the game."

    def notification_player_joined(self, player):
        print player + " has joined the game."
        if self.can_start:
            self.start_prompt()

    def notification_new_round(self):
        print "\nA new round has begun."

        self._display_instructions = True

    def notification_winner(self, player):
        print
        if player != self.username:
            print player + " has won the game."
        else:
            print "You've won the game! Congratulations!"


if __name__ == "__main__":
    HOST = config_parse.host
    PORT = config_parse.port
    reactor.connectTCP(HOST, PORT, PlayerFactory(ConsoleHuman()))
    reactor.run()
