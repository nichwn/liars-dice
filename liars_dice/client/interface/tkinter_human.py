"""

An interface for a human player to play the game via a GUI.

"""
from Tkinter import *
import tkFont
import functools
from twisted.internet import tksupport, reactor
from liars_dice import config_parse, network_command
from liars_dice.client.player import Player, PlayerFactory


class ConsoleFrame(Frame):
    """A frame containing a console for message output.

    Attributes:
        master: Tkinter master frame.
    """

    def __init__(self, master, **kwargs):
        """
        Args:
            master: Tkinter master frame.
        """

        Frame.__init__(self, master, **kwargs)

        scrollbar = Scrollbar(self)
        scrollbar.pack(side=RIGHT, fill=Y)

        self._console = Text(self, height=10, state=DISABLED)
        self._console.pack()

        self._console.configure(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self._console.yview)

    def emit_line(self, line):
        """Appends a line to the console.

        Args:
            line: A string to append to the console. Does not need to have
                a newline at the end of it.
        """
        # Prevent an empty line on the first line
        # Need to also prevent user writes
        self._console.config(state=NORMAL)
        if self._console.get("1.0", "end-1c") != "":
            self._console.insert(END, "\n" + line)
        else:
            self._console.insert(END, line)
        self._console.config(state=DISABLED)

        # Automatic textbox scrolling
        self._console.see(END)


class TurnLabelFrame(LabelFrame):
    """A label frame indicating whose turn it is."""

    def __init__(self, master, **kwargs):
        """
        Args:
            master: Tkinter master frame.
        """
        LabelFrame.__init__(self, master, **kwargs)
        self.configure(text="Player Order")

        # Player usernames
        self._previous_player_username = Label(self)
        self._previous_player_username.grid(row=1, column=0)
        self._current_player_username = Label(self)
        self._current_player_username.grid(row=1, column=1)
        self._next_player_username = Label(self)
        self._next_player_username.grid(row=1, column=2)

        # Player dice
        self._previous_player_dice = Label(self)
        self._previous_player_dice.grid(row=2, column=0)
        self._current_player_dice = Label(self)
        self._current_player_dice.grid(row=2, column=1)
        self._next_player_dice = Label(self)
        self._next_player_dice.grid(row=2, column=2)

        # Highlight the current turn player
        font = tkFont.Font(font=self._current_player_username["font"])
        font.config(weight="bold")
        self._current_player_username["font"] = font
        self._current_player_dice["font"] = font

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
        self._previous_player_username.configure(text=previous_player[0])
        self._current_player_username.configure(text=current_player[0])
        self._next_player_username.configure(text=next_player[0])

        self._previous_player_dice.configure(text=previous_player[1])
        self._current_player_dice.configure(text=current_player[1])
        self._next_player_dice.configure(text=next_player[1])


class PlayWindow(Toplevel):
    """A window allowing users to select their actions.

    Attributes:
        submitted: A Boolean indicating whether an action has been sent to the
            server.
    """

    def __init__(self, master, client, **kwargs):
        """
        Args:
            master: Tkinter master frame.
            client: A connection to the server, A subclass of twisted's
                Protocol.
        """
        Toplevel.__init__(self, master, **kwargs)
        self._client = client

        # Numbers
        number_frame = LabelFrame(self, text="Number of Dice")
        number_frame.pack(side=LEFT)
        self._number_buttons = self.generate_text_buttons(number_frame,
                                                          self.number_click,
                                                          [str(x) for x in
                                                           xrange(1, 11)])
        # Die faces
        dice_frame = LabelFrame(self, text="Die Face")
        dice_frame.pack(side=LEFT)
        self._dice_buttons = self.generate_image_buttons(dice_frame,
                                                         self.face_click,
                                                         ["resources/die_"
                                                          "{}.gif".format(x)
                                                          for x in
                                                          xrange(1, 7)])

        # Action buttons
        liar = Button(self, text="Liar!", command=self.pressed_liar)
        liar.pack(side=TOP)
        spot_on = Button(self, text="Spot On!",
                         command=self.pressed_spot_on)
        spot_on.pack(side=TOP)
        self._bid_button = Button(self, text="Bid!", state=DISABLED,
                                  command=self.pressed_bid)
        self._bid_button.pack(side=TOP)

        # Colour to change buttons to when clicked
        self._selectedbg = "#00ffff"

        # Default colour so background colour changes can be reverted
        self._defaultbg = dice_frame.cget('bg')

        # Face and number of dice selected by the user
        self._face_selected = None
        self._number_selected = None

        # Whether the user has submitted an action
        self.submitted = False

        # Take focus
        self.transient(master)
        self.grab_set()

    def background_click(self, buttons, selected_index):
        """Changes the colours of pressed buttons.

        Args:
            buttons: A list of associated buttons (only one should register as
                'pressed' at a time).
            selected_index: An integer with the index in buttons corresponding
                to the clicked button.
        """
        for die in buttons:
            die.configure(bg=self._defaultbg)
        buttons[selected_index].configure(bg=self._selectedbg)

    def check_bid_possible(self):
        """Enables the 'Bid!' button if the player has selected what bid
        they'd like to send.
        """
        if (self._face_selected is not None and
                self._number_selected is not None):
            self._bid_button.configure(state=NORMAL)

    def face_click(self, selected_index):
        """Stores the face value when a dice face button is pressed, and
        changes its background colour.

        Args:
            selected_index: An integer consisting of the order the face button
                was generated in (from 0).
        """
        self._face_selected = selected_index + 1
        self.background_click(self._dice_buttons, selected_index)
        self.check_bid_possible()

    def number_click(self, selected_index):
        """Stores the face value when a dice face button is pressed, and
        changes its background colour.

        Args:
            selected_index: An integer consisting of the order the face button
                was generated in (from 0).
        """
        self._number_selected = selected_index + 1
        self.background_click(self._number_buttons, selected_index)
        self.check_bid_possible()

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
            master: The tkinter frame to display the buttons in.
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
            master: The tkinter frame to display the buttons in.
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
        self._client.send_liar()
        self.post_action()

    def pressed_spot_on(self):
        """Submit a 'Spot On' action."""
        self._client.send_spot_on()
        self.post_action()

    def pressed_bid(self):
        """Submit a 'Bid' action."""
        self._client.send_bid(self._face_selected, self._number_selected)
        self.post_action()

    def post_action(self):
        """Cleanup to be performed after a submitted action."""
        self.submitted = True
        self.destroy()


class PreviousBidLabelFrame(LabelFrame):
    """A label frame displaying the latest bid played."""

    def __init__(self, master, **kwargs):
        """
        Args:
            master: Tkinter master frame.
        """
        LabelFrame.__init__(self, master, **kwargs)
        self.configure(text="Previous Bid")

        self._dice = []

    def display_previous_bid(self, face, number):
        """Displays the bid.

        Args:
            face: An integer with the face of the die, or None if there is no
                previous bid.
            number: An inteer with number of the die, or None if there is no
                previous bid.
        """
        if face is not None and number is not None:
            self._dice = display_dice(self, self._dice,
                                      [face for _ in xrange(number)])


class HandLabelFrame(LabelFrame):
    """A label frame consisting of the player's hand."""

    def __init__(self, master, **kwargs):
        """
        Args:
            master: Tkinter master frame.
        """
        LabelFrame.__init__(self, master, **kwargs)
        self.configure(text="Your Hand")

        self._dice = []

    def generate_hand_display(self, hand):
        """Displays the dice in the player's hand.

        Args:
            hand: An iterator of integers from 1 - 6 corresponding to die faces.
        """
        self._dice = display_dice(self, self._dice, hand)


class UsernameWindow(Toplevel):
    """Prompts the player for their username.

    Attributes:
        submitted: A Boolean indicating whether an action has been sent to the
            server.
    """

    def __init__(self, master, client, **kwargs):
        """
        Args:
            master: Tkinter master frame.
            client: A connection to the server, A subclass of twisted's
                Protocol.
        """
        Toplevel.__init__(self, master, **kwargs)
        self._client = client

        self._prompt = Label(self, text="Username:")
        self._prompt.pack()
        self._username_entry = Entry(self)
        self._username_entry.pack()
        self._username_entry.focus_set()
        self._submit = Button(self, text="Submit", command=self.send_username)
        self._submit.pack()
        self.bind("<Return>", self.send_username)

        # Whether the user has submitted their action
        self.submitted = False

        # Take focus
        self.transient(master)
        self.grab_set()

    def send_username(self, event=None):
        """Send the username entered to the server."""
        username = self._username_entry.get().replace(network_command.DELIMITER,
                                                      "")
        self._client.send_username(username)
        self.submitted = True
        self.destroy()


class App(Player):
    """Tkinter GUI and server connection."""

    def __init__(self, master):
        """
        Args:
            master: Tkinter master frame.
        """
        Player.__init__(self)
        self._master = master

        # Generate the UI elements
        self._turn_frame = TurnLabelFrame(master)
        self._turn_frame.grid(row=0, column=0)
        self._hand_frame = HandLabelFrame(master)
        self._hand_frame.grid(row=1, column=0)
        self._previous_bid_frame = PreviousBidLabelFrame(master)
        self._previous_bid_frame.grid(row=2, column=0)
        self._console_frame = ConsoleFrame(master)
        self._console_frame.grid(row=3, column=0)
        self._console_frame.columnconfigure(0, weight=1)
        self._chat_entry = Entry(master)
        self._chat_entry.grid(row=4, column=0)
        self._chat_entry.columnconfigure(0, weight=1)
        self._chat_entry.focus_set()
        master.bind("<Return>", self.send_chat_message)
        self._start_button = Button(master, text="Start Game!", state=DISABLED,
                                    command=self.send_start)
        self._start_button.grid(row=5, column=0)

        # Hide the game related elements until needed
        self._turn_frame.grid_remove()
        self._hand_frame.grid_remove()
        self._previous_bid_frame.grid_remove()

        # Game status
        self._game_started = False
        self._player_data = []
        self._turn_username = None
        self._can_start = False

    def send_chat_message(self, event):
        """Sends the chat message in the chat window to the server.

        Args:
            event: The event sent by tkinter's frame.bind().
        """
        message = self._chat_entry.get()
        self.send_chat(message)
        self._chat_entry.delete(0, END)

    def notification_player_status(self, player_data):
        self._player_data = player_data

        # Allow the client to start the game if the game conditions allow for it
        if not self._game_started and self._can_start and len(player_data) >= 2:
            self._start_button.configure(state=NORMAL)

        # Display player status information to the console
        elif self._game_started:
            self._console_frame.emit_line("Players with their remaining dice:")
            for player in player_data:
                self._console_frame.emit_line(
                    player[0] + " - " + str(player[1]))

    def notification_username_request(self):
        window = UsernameWindow(self._master, self)
        self._master.wait_window(window)

        # Prevent user from shutting down the window without submitting their
        # username
        if not window.submitted:
            self.notification_username_request()

    def notification_play_request(self):
        window = PlayWindow(self._master, self)
        self._master.wait_window(window)

        # Prevent user from shutting down the window without submitting their
        # username
        if not window.submitted:
            self.notification_play_request()

    def notification_next_turn(self, player):
        self._turn_username = player

        # Update the player order display
        i = [p[0] for p in self._player_data].index(player)
        length = len(self._player_data)
        previous_player = self._player_data[(i - 1) % length]
        current_player = self._player_data[i]
        next_player = self._player_data[(i + 1) % length]
        self._turn_frame.display_turn_order(previous_player, current_player,
                                            next_player)

        if player[-1].lower() == "s":
            player += "'"
        else:
            player += "'s"
        self._console_frame.emit_line(player + " turn!")

    def notification_hand(self, hand):
        self._hand_frame.generate_hand_display(hand)

    def notification_bid(self, face, number):
        self._previous_bid_frame.display_previous_bid(face, number)

        out_face = str(face)
        if number != 1:
            out_face = str(face) + "s"
        out_number = str(number)
        self._console_frame.emit_line(
            "{} bid {} {}.".format(self._turn_username,
                                   out_number,
                                   out_face))

    def notification_spot_on(self):
        self._console_frame.emit_line(self._turn_username + " announced "
                                                            "'Spot On!'")

    def notification_liar(self):
        self._console_frame.emit_line(self._turn_username + " announced "
                                                            "'Liar!'")

    def notification_player_lost_die(self, player):
        self._console_frame.emit_line(player + " lost a die.")

    def notification_eliminated(self, player):
        self._console_frame.emit_line(player + " has run out of dice and been "
                                               "eliminated!")

        if player == self.username:
            self._hand_frame.destroy()

    def notification_player_left(self, player):
        self._console_frame.emit_line(player + " has disconnected from the "
                                               "game.")

    def notification_player_joined(self, player):
        self._console_frame.emit_line(player + " has joined the game.")

    def notification_can_start(self):
        self._can_start = True

    def notification_new_round(self):

        # Display the UI elements relevant for the game, and remove those
        # no longer necessary.
        if not self._game_started:
            self._game_started = True
            self._turn_frame.grid()
            self._hand_frame.grid()
            self._previous_bid_frame.grid()
            self._start_button.destroy()

        self._previous_bid_frame.display_previous_bid(1, 0)

        self._console_frame.emit_line("New round!")

    def notification_winner(self, player):
        self._console_frame.emit_line(player + " has won the game!")

    def notification_chat(self, username, message):
        self._console_frame.emit_line("{}: {}".format(username, message))


def display_dice(master, dice_old, face_new):
    """Displays dice in a frame horizontally.

    Args:
        master: Tkinter master frame.
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


def run():
    """Run the client."""
    # GUI Settings
    root = Tk()
    root.title("Liar's Dice Client")
    root.resizable(width=False, height=False)

    # Create the GUI
    player_factory = PlayerFactory(App(root))

    # tkinter + twisted support
    tksupport.install(root)

    # Connection
    host = config_parse.host
    port = config_parse.port
    reactor.connectTCP(host, port, player_factory)
    reactor.run()


if __name__ == "__main__":
    run()
