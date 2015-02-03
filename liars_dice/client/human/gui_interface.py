"""

An interface for a human player to play the game via a GUI.

"""
from Tkinter import *
from twisted.internet import tksupport, reactor
from liars_dice import config_parse, network_command
from liars_dice.client.player import Player, PlayerFactory


class GUIHuman(Player):
    """Client protocol instance."""

    def notification_player_status(self, player_data):
        pass

    def notification_username_request(self):
        app.username_prompt()

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


class UsernameWindow:
    """Prompts the player for their username."""

    def __init__(self, master, client):
        self.client = client

        self.top = Toplevel(master)
        self.prompt = Label(self.top, text="Username:")
        self.prompt.pack()
        self.username_entry = Entry(self.top)
        self.username_entry.pack()
        self.username_entry.focus_set()
        self.submit = Button(self.top, text="Submit",
                             command=self.send_username)
        self.submit.pack()

        # Take focus
        self.top.transient(master)
        self.top.grab_set()

    def send_username(self):
        username = self.username_entry.get().replace(network_command.DELIMITER,
                                                     "")
        self.client.send_name(username)
        self.cleanup()

    def cleanup(self):
        """Destroy the window."""
        self.top.destroy()


class App:
    """Tkinter GUI."""

    def __init__(self, master, factory):
        self.master = master
        self.client = factory.client

    def username_prompt(self):
        window = UsernameWindow(self.master, self.client)
        self.master.wait_window(window.top)


if __name__ == "__main__":

    # Protocol factory
    player_factory = PlayerFactory(GUIHuman())

    # Create the GUI
    root = Tk()
    root.title("Liar's Dice Client")
    root.resizable(width=False, height=False)
    app = App(root, player_factory)
    tksupport.install(root)

    # Reactor
    HOST = config_parse.host
    PORT = config_parse.port
    reactor.connectTCP(HOST, PORT, player_factory)
    reactor.run()
