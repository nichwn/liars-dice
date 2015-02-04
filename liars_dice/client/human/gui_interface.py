"""

An interface for a human player to play the game via a GUI.

"""
from Tkinter import *
from twisted.internet import tksupport, reactor
from liars_dice import config_parse, network_command
from liars_dice.client.player import Player, PlayerFactory


class HandLabelFrame:
    """A label frame consisting of the player's hand."""

    def __init__(self, master, hand):
        self.frame = LabelFrame(master, text="Your Hand")
        self.frame.pack()

        self._dice = []
        self.generate_hand_display(hand)

    def generate_hand_display(self, hand):
        """Displays the dice in the player's hand.

        Args:
            hand: An iterator of integers from 1 - 6 corresponding to die faces.
        """
        # Destroy the old hand
        for die in self._dice:
            die.destroy()

        # Generate new hand
        self._dice = []
        for die in hand:
            die_image = PhotoImage(file="resources/die_{}.gif".format(die))
            die_label = Label(self.frame, image=die_image)
            die_label.image = die_image
            die_label.pack(side=LEFT)
            self._dice.append(die_label)


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


class App(Player):
    """Tkinter GUI and server connection."""

    def __init__(self, master):
        Player.__init__(self)
        self.master = master

    def notification_username_request(self):
        window = UsernameWindow(self.master, self)
        self.master.wait_window(window.top)


if __name__ == "__main__":

    # GUI Settings
    root = Tk()
    root.title("Liar's Dice Client")
    root.resizable(width=False, height=False)

    # Create the GUI
    player_factory = PlayerFactory(App(root))

    # tkinter + twisted support
    tksupport.install(root)

    # Connection
    HOST = config_parse.host
    PORT = config_parse.port
    reactor.connectTCP(HOST, PORT, player_factory)
    reactor.run()
