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
from twisted.internet import reactor
from liars_dice.client.player import Player, PlayerFactory


class SimpleBot(Player):
    pass


if __name__ == "__main__":
    PORT = 9637
    host = raw_input("Host: ")
    reactor.connectTCP(host, PORT, PlayerFactory(SimpleBot()))
    reactor.run()
