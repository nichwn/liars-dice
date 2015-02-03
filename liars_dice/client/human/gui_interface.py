"""

An interface for a human player to play the game via a GUI.

"""
from Tkinter import *
from twisted.internet import tksupport, reactor
from liars_dice import config_parse
from liars_dice.client.player import Player, PlayerFactory


class GUIHuman(Player):
    """Client protocol instance."""

    def notification_player_status(self, player_data):
        pass

    def notification_username_request(self):
        pass

    def notification_play_request(self):
        pass

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

    def notification_player_lost_die(self, player):
        pass

    def notification_eliminated(self, player):
        pass

    def notification_player_left(self, player):
        pass

    def notification_player_joined(self, player):
        pass

    def notification_can_start(self):
        pass

    def notification_new_round(self):
        pass

    def notification_winner(self, player):
        pass


class App:
    """Tkinter GUI."""

    def __init__(self, master, factory):
        pass


if __name__ == "__main__":

    # Protocol factory
    factory = PlayerFactory(GUIHuman())

    # Create the GUI
    root = Tk()
    root.title("Liar's Dice Client")
    root.resizable(width=False, height=False)
    app = App(root, factory)
    tksupport.install(root)

    # Reactor
    HOST = config_parse.host
    PORT = config_parse.port
    reactor.connectTCP(HOST, PORT, factory)
    reactor.run()
