"""

A client skeleton intended to make developing a client easier.

For details on the conditions for notification_XXX() being called, see the
corresponding docstrings of liars_dice/client/player.py.

"""
from twisted.internet import reactor
from liars_dice import config_parse
from liars_dice.client.player import Player, PlayerFactory


class YourClientName(Player):

    def notification_player_status(self, player_data):
        pass

    def notification_username_request(self):
        # To submit your username, call self.username(username)
        # Do not attempt to store the username yourself. Instead,
        # self.username will store the username you've given to the server.
        #
        # Do not modify self.username.
        raise NotImplementedError

    def notification_play_request(self):
        # To submit your action choose one of the following:
        #   liar --> self.send_liar()
        #   spot on --> self.send_spot_on()
        #   bet --> self.send_bet(face, number)
        raise NotImplementedError

    def notification_next_turn(self, player):
        pass

    def notification_hand(self, hand):
        pass

    def notification_bet(self, face, number):
        pass

    def notification_spot_on(self):
        pass

    def notification_liar(self):
        pass

    def notification_player_lost_die(self, player):
        pass

    def notification_eliminated(self, player):
        pass

    def notification_player_left(self, player):
        pass

    def notification_player_joined(self, player):
        pass

    def notification_can_start(self):
        # A player who receives this notification can start the game. To start
        # the game, call self.send_start() at any time after receiving this
        # event call.
        raise NotImplementedError

    def notification_new_round(self):
        pass

    def notification_winner(self, player):
        pass

    def notification_chat(self, username, message):
        # To pass your own chat messages, call self.send_chat(message). There's
        # no need to store chat messages that you've sent, as the server will
        # send them back to you via this event.
        pass


def run():
    # Grab the host and client from liars_dice/config.ini
    host = config_parse.host
    port = config_parse.port

    # Run Twisted's reactor. This should be the last thing in your program.
    # If you intend to use a GUI, see the following on how to integrate
    # it with Twisted:
    #
    # http://twistedmatrix.com/documents/current/core/howto/choosing-reactor.html
    #
    # If you are familiar with Twisted's ClientFactory, you may of course feel
    # free to override/replace PlayerFactory with a factory of your choice.
    # However, this is not necessary.
    reactor.connectTCP(host, port, PlayerFactory(YourClientName()))
    reactor.run()

if __name__ == "__main__":
    run()
