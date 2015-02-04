"""

An interface for a human player to play the game via a GUI.

"""
from Tkinter import *
from twisted.internet import tksupport, reactor
from liars_dice import config_parse, network_command
from liars_dice.client.player import Player, PlayerFactory


class PreviousBetLabelFrame:
    """A label frame displaying the latest bet played."""

    def __init__(self, master):
        self.frame = LabelFrame(master, text="Dice")
        self.frame.pack()

        self._dice = []

    def display_previous_bet(self, face, number):
        """Displays the bet.

        Args:
            face: An integer with the face of the die, or None if there is no
                previous bet.
            number: An inteer with number of the die, or None if there is no
                previous bet.
        """
        if face is not None and number is not None:

            self._dice = display_dice(self.frame, self._dice,
                                      [face for _ in xrange(number)])


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
        self._dice = display_dice(self.frame, self._dice, hand)


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


def display_dice(master, dice_old, face_new):
    """Displays dice in a frame horizontally.

    Args:
        master: The frame to display the dice.
        dice_old: A list with the previous dice returned by this function, or
            [] if there aren't any.
        face_new: A list of integers of dice faces to display.

    Returns:
        A list of the dice generated.
    """
    # Destroy the old collection
    for die in dice_old:
        die.destroy()

    # Generate new hand
    dice = []
    for die in face_new:
        die_image = PhotoImage(file="resources/die_{}.gif".format(die))
        die_label = Label(master, image=die_image)
        die_label.image = die_image
        die_label.pack(side=LEFT)
        dice.append(die_label)

    return dice



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
