"""

An interface for a human player to play the game via a GUI.

"""
from Tkinter import *
import tkFont
import functools
from twisted.internet import tksupport, reactor
from liars_dice import config_parse, network_command
from liars_dice.client.player import Player, PlayerFactory


class ConsoleFrame:
    """A frame containing a textbox for message output."""
    def __init__(self, master):
        frame = Frame(master)
        frame.pack()

        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.console = Text(frame, height=10, state=DISABLED)
        self.console.pack()

        self.console.configure(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.console.yview)

    def emit_line(self, line):
        # Prevent an empty line on the first line
        self.console.config(state=NORMAL)
        if self.console.get("1.0", "end-1c") != "":
            self.console.insert(END, "\n" + line)
        else:
            self.console.insert(END, line)
        self.console.config(state=DISABLED)

        # Automatic textbox scrolling
        self.console.see(END)


class TurnLabelFrame:
    """A label frame indicating whose turn it is."""

    def __init__(self, master):
        frame = LabelFrame(master, text="Player Order")
        frame.pack()

        # Player names
        self.previous_player_username = Label(frame)
        self.previous_player_username.grid(row=1, column=0)
        self.current_player_username = Label(frame)
        self.current_player_username.grid(row=1, column=1)
        self.next_player_username = Label(frame)
        self.next_player_username.grid(row=1, column=2)

        # Player dice
        self.previous_player_dice = Label(frame)
        self.previous_player_dice.grid(row=2, column=0)
        self.current_player_dice = Label(frame)
        self.current_player_dice.grid(row=2, column=1)
        self.next_player_dice = Label(frame)
        self.next_player_dice.grid(row=2, column=2)

        # Highlight the current turn player
        font = tkFont.Font(font=self.current_player_username["font"])
        font.config(weight="bold")
        self.current_player_username["font"] = font
        self.current_player_dice["font"] = font

    def display_turn_order(self, previous_player, current_player,
                           next_player):
        """Displays the previous, current, and next player in turn order, along
        with the number of dice they have remaining.

        Args:
            previous_player: A tuple consisting of a string with the player who
                plays right before the current turn player, along with an
                integer of the number of dice they have remaining.
            current_player: A tuple consisting of a string with the player whose
                turn it is, along with an integer of the number of dice they
                have remaining.
            next_player: A tuple consisting of a string with the player whose
                turn is next, along with an integer of the number of dice they
                have remaining.
        """
        self.previous_player_username.configure(text=previous_player[0])
        self.current_player_username.configure(text=current_player[0])
        self.next_player_username.configure(text=next_player[0])

        self.previous_player_dice.configure(text=previous_player[1])
        self.current_player_dice.configure(text=current_player[1])
        self.next_player_dice.configure(text=next_player[1])


class PlayLabelFrame:
    """A label frame allowing users to select their actions."""

    def __init__(self, master, client):
        self.client = client

        play_frame = LabelFrame(master)
        play_frame.pack()

        # Numbers
        number_frame = LabelFrame(play_frame, text="Number of Dice")
        number_frame.pack(side=LEFT)
        self.number_buttons = self.generate_text_buttons(number_frame,
                                                         self.number_click,
                                                         [str(x) for x in
                                                          xrange(1, 11)])
        # Die faces
        dice_frame = LabelFrame(play_frame, text="Die Face")
        dice_frame.pack(side=LEFT)
        self.dice_buttons = self.generate_image_buttons(dice_frame,
                                                        self.face_click,
                                                        ["resources/die_"
                                                         "{}.gif".format(x)
                                                         for x in
                                                         xrange(1, 7)])

        # Action buttons
        liar = Button(play_frame, text="Liar!", command=self.pressed_liar)
        liar.pack(side=TOP)
        spot_on = Button(play_frame, text="Spot On!",
                         command=self.pressed_spot_on)
        spot_on.pack(side=TOP)
        self.bet_button = Button(play_frame, text="Bet!", state=DISABLED,
                                 command=self.pressed_bet)
        self.bet_button.pack(side=TOP)

        # Colour to change buttons to when clicked
        self.selectedbg = "#00ffff"

        # Default colour so background colour changes can be reverted
        self.defaultbg = dice_frame.cget('bg')

        # Face and number of dice selected by the user
        self.face_selected = None
        self.number_selected = None

    def background_click(self, buttons, selected_index):
        """Changes the colours of pressed buttons.

        Args:
            buttons: A list of associated buttons (only one should register as
                'pressed' at a time).
            selected_index: An integer with the index in buttons corresponding
                to the clicked button.
        """
        for die in buttons:
            die.configure(bg=self.defaultbg)
        buttons[selected_index].configure(bg=self.selectedbg)

    def check_bet_possible(self):
        """Enables the 'Bet!' button if the player has selected what bet
        they'd like to send.
        """
        if (self.face_selected is not None and
                self.number_selected is not None):
            self.bet_button.configure(state=NORMAL)

    def face_click(self, selected_index):
        """Stores the face value when a dice face button is pressed, and
        changes its background colour.

        Args:
            selected_index: An integer consisting of the order the face button
                was generated in (from 0).
        """
        self.face_selected = selected_index + 1
        self.background_click(self.dice_buttons, selected_index)
        self.check_bet_possible()

    def number_click(self, selected_index):
        """Stores the face value when a dice face button is pressed, and
        changes its background colour.

        Args:
            selected_index: An integer consisting of the order the face button
                was generated in (from 0).
        """
        self.number_selected = selected_index + 1
        self.background_click(self.number_buttons, selected_index)
        self.check_bet_possible()

    def position_widget(self, widget):
        """Return the row and column position of a widget in a multi-row, two
        column grid in order from left-right, up-down.

        Args:
            widget: An integer consisting of widget placement order (starting
                from 0).

        Returns:
            A two element tuple of integers with the row and the column position
            values of the widget on a grid.
        """
        BUTTONS_PER_ROW = 2
        row = widget / BUTTONS_PER_ROW
        column = widget % BUTTONS_PER_ROW
        return row, column

    def generate_text_buttons(self, master, reaction, text):
        """Generates buttons in two columns, in order of left-right, top-down.

        Args:
            master: The frame to display the buttons in.
            reaction: The command which the buttons should perform when clicked.
                It should accept an integer parameter that will correspond
                with the order the button was created (0-initial).
            text: A list of strings consisting of the text display of the
                buttons, in the order to be displayed, or None if no text is to
                be used.
        """
        generated = []
        for i in xrange(len(text)):
            # Generate the button
            command = functools.partial(reaction, i)
            button = Button(master, text=text[i], command=command)

            # Place the button
            row, column = self.position_widget(i)
            button.grid(row=row, column=column)

            generated.append(button)
        return generated

    def generate_image_buttons(self, master, reaction, image_location):
        """Generates buttons in two columns, in order of left-right, top-down.

        Args:
            master: The frame to display the buttons in.
            reaction: The command which the buttons should perform when clicked.
                It should accept an integer parameter that will correspond
                with the order the button was created (0-initial).
            image_location: A list of strings consisting of the file location
                of the source image files for the buttons, in the order to be
                displayed, or None if no images are to be used.
        """
        generated = []
        for i in xrange(len(image_location)):
            # Generate the button
            image = PhotoImage(file=image_location[i])
            command = functools.partial(reaction, i)
            button = Button(master, image=image, command=command)
            button.image = image

            # Place the button
            row, column = self.position_widget(i)
            button.grid(row=row, column=column)

            generated.append(button)
        return generated

    def pressed_liar(self):
        """Submit a 'Liar' action."""
        self.client.send_liar()

    def pressed_spot_on(self):
        """Submit a 'Spot On' action."""
        self.client.send_spot_on()

    def pressed_bet(self):
        """Submit a 'Bet' action."""
        self.client.send_bet(self.face_selected, self.number_selected)


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
