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
    """A frame containing a console for message output."""

    def __init__(self, master, **kwargs):
        Frame.__init__(self, master, **kwargs)

        scrollbar = Scrollbar(self)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.console = Text(self, height=10, state=DISABLED)
        self.console.pack()

        self.console.configure(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.console.yview)

    def emit_line(self, line):
        # Prevent an empty line on the first line
        # Need to also prevent user writes
        self.console.config(state=NORMAL)
        if self.console.get("1.0", "end-1c") != "":
            self.console.insert(END, "\n" + line)
        else:
            self.console.insert(END, line)
        self.console.config(state=DISABLED)

        # Automatic textbox scrolling
        self.console.see(END)


class TurnLabelFrame(LabelFrame):
    """A label frame indicating whose turn it is."""

    def __init__(self, master, **kwargs):
        LabelFrame.__init__(self, master, **kwargs)
        self.configure(text="Player Order")

        # Player names
        self.previous_player_username = Label(self)
        self.previous_player_username.grid(row=1, column=0)
        self.current_player_username = Label(self)
        self.current_player_username.grid(row=1, column=1)
        self.next_player_username = Label(self)
        self.next_player_username.grid(row=1, column=2)

        # Player dice
        self.previous_player_dice = Label(self)
        self.previous_player_dice.grid(row=2, column=0)
        self.current_player_dice = Label(self)
        self.current_player_dice.grid(row=2, column=1)
        self.next_player_dice = Label(self)
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


class PlayWindow(Toplevel):
    """A window allowing users to select their actions."""

    def __init__(self, master, client, **kwargs):
        Toplevel.__init__(self, master, **kwargs)
        self.client = client

        # Numbers
        number_frame = LabelFrame(self, text="Number of Dice")
        number_frame.pack(side=LEFT)
        self.number_buttons = self.generate_text_buttons(number_frame,
                                                         self.number_click,
                                                         [str(x) for x in
                                                          xrange(1, 11)])
        # Die faces
        dice_frame = LabelFrame(self, text="Die Face")
        dice_frame.pack(side=LEFT)
        self.dice_buttons = self.generate_image_buttons(dice_frame,
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
        self.bet_button = Button(self, text="Bet!", state=DISABLED,
                                 command=self.pressed_bet)
        self.bet_button.pack(side=TOP)

        # Colour to change buttons to when clicked
        self.selectedbg = "#00ffff"

        # Default colour so background colour changes can be reverted
        self.defaultbg = dice_frame.cget('bg')

        # Face and number of dice selected by the user
        self.face_selected = None
        self.number_selected = None

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
        self.post_action()

    def pressed_spot_on(self):
        """Submit a 'Spot On' action."""
        self.client.send_spot_on()
        self.post_action()

    def pressed_bet(self):
        """Submit a 'Bet' action."""
        self.client.send_bet(self.face_selected, self.number_selected)
        self.post_action()

    def post_action(self):
        """Cleanup to be performed after a submitted action."""
        self.submitted = True
        self.destroy()


class PreviousBetLabelFrame(LabelFrame):
    """A label frame displaying the latest bet played."""

    def __init__(self, master, **kwargs):
        LabelFrame.__init__(self, master, **kwargs)
        self.configure(text="Previous Bet")

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

            self._dice = display_dice(self, self._dice,
                                      [face for _ in xrange(number)])


class HandLabelFrame(LabelFrame):
    """A label frame consisting of the player's hand."""

    def __init__(self, master, **kwargs):
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
    """Prompts the player for their username."""

    def __init__(self, master, client, **kwargs):
        Toplevel.__init__(self, master, **kwargs)
        self.client = client

        self.prompt = Label(self, text="Username:")
        self.prompt.pack()
        self.username_entry = Entry(self)
        self.username_entry.pack()
        self.username_entry.focus_set()
        self.submit = Button(self, text="Submit", command=self.send_username)
        self.submit.pack()
        self.bind("<Return>", self.send_username)

        # Whether the user has submitted their action
        self.submitted = False

        # Take focus
        self.transient(master)
        self.grab_set()

    def send_username(self, event=None):
        username = self.username_entry.get().replace(network_command.DELIMITER,
                                                     "")
        self.client.send_name(username)
        self.submitted = True
        self.destroy()


class App(Player):
    """Tkinter GUI and server connection."""

    def __init__(self, master):
        Player.__init__(self)
        self.master = master

        # Generate the UI elements
        self.turn_frame = TurnLabelFrame(root)
        self.turn_frame.grid(row=0, column=0)
        self.hand_frame = HandLabelFrame(root)
        self.hand_frame.grid(row=1, column=0)
        self.previous_bet_frame = PreviousBetLabelFrame(root)
        self.previous_bet_frame.grid(row=2, column=0)
        self.console_frame = ConsoleFrame(master)
        self.console_frame.grid(row=3, column=0)
        self.console_frame.columnconfigure(0, weight=1)
        self.chat_entry = Entry(master)
        self.chat_entry.grid(row=4, column=0)
        self.chat_entry.columnconfigure(0, weight=1)
        self.chat_entry.focus_set()
        master.bind("<Return>", self.send_chat_message)
        self.start_button = Button(master, text="Start Game!", state=DISABLED,
                                   command=self.send_start)
        self.start_button.grid(row=5, column=0)

        # Hide the game related elements until needed
        self.turn_frame.grid_remove()
        self.hand_frame.grid_remove()
        self.previous_bet_frame.grid_remove()

        # Game status
        self.game_started = False
        self.player_data = []
        self.turn_username = None
        self.can_start = False

    def send_chat_message(self, event):
        """Sends the chat message in the chat window to the server.

        Args:
            event: The event sent by tkinter's frame.bind()"""
        message = self.chat_entry.get()
        self.send_chat(message)
        self.chat_entry.delete(0, END)

    def notification_player_status(self, player_data):
        self.player_data = player_data

        # Allow the client to start the game if the game conditions allow for it
        if not self.game_started and self.can_start and len(player_data) >= 2:
            self.start_button.configure(state=NORMAL)

        # Display player status information to the console
        elif self.game_started:
            self.console_frame.emit_line("Players with their remaining dice:")
            for player in player_data:
                self.console_frame.emit_line(player[0] + " - " + str(player[1]))

    def notification_username_request(self):
        window = UsernameWindow(self.master, self)
        self.master.wait_window(window)

        # Prevent user from shutting down the window without submitting their
        # username
        if not window.submitted:
            self.notification_username_request()

    def notification_play_request(self):
        window = PlayWindow(self.master, self)
        self.master.wait_window(window)

        # Prevent user from shutting down the window without submitting their
        # username
        if not window.submitted:
            self.notification_play_request()

    def notification_next_turn(self, player):
        self.turn_username = player

        # Update the player order display
        i = [p[0] for p in self.player_data].index(player)
        length = len(self.player_data)
        previous_player = self.player_data[(i - 1) % length]
        current_player = self.player_data[i]
        next_player = self.player_data[(i + 1) % length]
        self.turn_frame.display_turn_order(previous_player, current_player,
                                           next_player)

        if player[-1].lower() == "s":
            player += "'"
        else:
            player += "'s"
        self.console_frame.emit_line(player + " turn!")

    def notification_hand(self, hand):
        self.hand_frame.generate_hand_display(hand)

    def notification_bet(self, face, number):
        self.previous_bet_frame.display_previous_bet(face, number)

        out_face = str(face)
        if number != 1:
            out_face = str(face) + "s"
        out_number = str(number)
        self.console_frame.emit_line("{} bet {} {}.".format(self.turn_username,
                                                            out_number,
                                                            out_face))

    def notification_spot_on(self):
        self.console_frame.emit_line(self.turn_username + " announced "
                                                          "'Spot On!'")

    def notification_liar(self):
        self.console_frame.emit_line(self.turn_username + " announced "
                                                          "'Liar!'")

    def notification_player_lost_die(self, player):
        self.console_frame.emit_line(player + " lost a die.")

    def notification_eliminated(self, player):
        self.console_frame.emit_line(player + " has run out of dice and been "
                                              "eliminated!")

        if player == self.username:
            self.hand_frame.destroy()

    def notification_player_left(self, player):
        self.console_frame.emit_line(player + " has disconnected from the "
                                              "game.")

    def notification_player_joined(self, player):
        self.console_frame.emit_line(player + " has joined the game.")

    def notification_can_start(self):
        self.can_start = True

    def notification_new_round(self):

        # Display the UI elements relevant for the game, and remove those
        # no longer necessary.
        if not self.game_started:
            self.game_started = True
            self.turn_frame.grid()
            self.hand_frame.grid()
            self.previous_bet_frame.grid()
            self.start_button.destroy()

        self.previous_bet_frame.display_previous_bet(1, 0)

        self.console_frame.emit_line("New round!")

    def notification_winner(self, player):
        self.console_frame.emit_line(player + " has won the game!")

    def notification_chat(self, username, message):
        self.console_frame.emit_line("{}: {}".format(username, message))


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
