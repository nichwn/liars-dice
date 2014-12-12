"""

An interface for a human player to play the game.

"""
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
from liars_dice.client.player import Player


class ConsoleHuman(Player):
    """A player instance."""

    def notification_player_status(self, player_data):
        pass

    def notification_name_request(self):
        raise NotImplementedError

    def notification_play_request(self):
        raise NotImplementedError

    def notification_next_turn(self, player):
        pass

    def notification_hand(self):
        pass

    def notification_bet(self, face, number):
        pass

    def notification_spot_on(self):
        pass

    def notification_liar(self):
        pass

    def notification_player_lost_die(self, string):
        pass

    def notification_player_left(self, player):
        pass

    def notification_player_joined(self, player):
        pass

    def notification_new_round(self):
        pass

    def notification_winner(self, player):
        pass


class ConsoleHumanFactory(ClientFactory):
    """Handle client connections and store the game status."""

    def startedConnecting(self, connector):
        pass

    def buildProtocol(self, addr):
        pass

    def clientConnectionLost(self, connector, reason):
        pass

    def clientConnectionFailed(self, connector, reason):
        pass


if __name__ == "__main__":
    PORT = 9637
    host = raw_input("Host: ")
    reactor.connectTCP(host, 9637, ConsoleHumanFactory())
    reactor.run()
