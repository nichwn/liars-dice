"""

A simple bot that can connect to the server and play the game. It cannot start
the game, and will automatically disconnect from the server if given that
power.

Bot strategy:
    if there is no previous bet
        bets -> face 1 - 6 randomly, number 1
    if the number of previous dice bet == total / 6
        30% -> Spot On
        70% -> Play as normal
    if the number of previous dice bet == total / 6 + 1
        60% -> Liar
        40% -> Play as normal
    if the number of previous dice bet >= toal / 6 + 2
        80% -> Liar
        20% -> Play as normal
    else (this is 'Play as normal')
        if face == 6
            increase number of dice by 1
        else
            30% -> increase number of dice by 1

        pick random valid face
"""
from random import randint, random
from twisted.internet import reactor
from liars_dice import config_parse
from liars_dice.client.player import Player, PlayerFactory


class SimpleBot(Player):
    """A bot instance as given by the module header.

    Attributes:
        previous_face: An integer with the face the previous bet made.
        previous_number: An inteer with the number of dice the previous bet
            made.
        desired_username: The name the bot will be referred to by the server.
            If taken, will append underscores until accepted.
    """
    MIN_FACE = 1
    MAX_FACE = 6
    FACES_PER_DIE = 6

    def __init__(self):
        Player.__init__(self)
        self.previous_face = None
        self.previous_number = None
        self.desired_username = "Simple Bot"
        self._total_dice = None  # this value is unused - set later

    def notification_player_status(self, player_data):
        self._total_dice = sum(n for _, n in player_data)

    def notification_username_request(self):
        self.send_name(self.desired_username)

        # Add an underscore in case the username is taken and a new username
        # has to be resent
        self.desired_username += "_"

    def notification_play_request(self):
        # See the module header for the explanation of the bot's strategy.

        if self.previous_number is not None:
            expected_dice_per_face = self.previous_number / self.FACES_PER_DIE
        else:
            expected_dice_per_face = None  # not used - suppressing IDE warnings

        if self.previous_number is None or self.previous_face is None:
            number = 1
            face = randint(self.MIN_FACE, self.MAX_FACE)

        elif (self.previous_number == expected_dice_per_face and
                random_boolean(0.3)):
            self.send_spot_on()
            return

        elif (self.previous_number == expected_dice_per_face + 1 and
                random_boolean(0.6)):
            self.send_liar()
            return

        elif (self.previous_number >= expected_dice_per_face + 2 and
                random_boolean(0.8)):
            self.send_liar()
            return

        else:
            if self.previous_face == self.MAX_FACE or random_boolean(0.3):
                number = self.previous_number + 1
                must_increase_face = False
            else:
                number = self.previous_number
                must_increase_face = True

            if must_increase_face:
                face = randint(self.previous_number + 1, self.MAX_FACE)
            else:
                face = randint(self.previous_number, self.MAX_FACE)

        self.send_bet(face, number)

    def notification_bet(self, face, number):
        self.previous_face = face
        self.previous_number = number

    def notification_new_round(self):
        self.previous_face = None
        self.previous_number = None

    def notification_can_start(self):
        self.transport.loseConnection()


def random_boolean(true_chance):
    """Generate a Boolean with probability based on true_chance.

    Args:
        true_chance: A floating point number in the range [0.0, 1.0),
            indicating the probabiliy of a True result.

    Returns:
        A Boolean base don true_chance.

    Raises:
        ValueError: true_chance is not in the range [0.0, 1.0).
    """
    if true_chance < 0.0 or true_chance >= 1.0:
        raise ValueError("true_chance is not in the range [0.0, 1.0)")
    return true_chance > random()


if __name__ == "__main__":
    HOST = config_parse.host
    PORT = config_parse.port
    reactor.connectTCP(HOST, PORT, PlayerFactory(SimpleBot()))
    reactor.run()
