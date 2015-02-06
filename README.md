Liar's Dice
===========

This project consists of a server and multiple clients for playing a simple dice game, 'Liar's Dice'. 

It is compatible with Python 2.7 only.

How to Play
-----------

Players are initially given 5 dice each. Each round, all players privately roll all their dice such that they can see the faces, but nobody else can. Players then take it in turns to perform one of three actions:

* They pick a die face and a number of dice, and make a bid. In this version, all bids must either have a higher number of dice, or the same number with a higher die face.
* They challenge the previous bid ('Liar!'), and if the there are less dice pooled amongst the players than the number predicted for the predicted face, the player who made the bet loses a die. If incorrect, the challenger loses a die instead. Then the game proceeds to the next round.
* They predict that the previous bid is correct ("Spot On!"). In this version, if the number of dice with that face amongst all the player's dice match the previous bid, then the player who made the big loses a die. If incorrect, the declarer loses a die instead. Then the game proceeds to the next round.

The last player with dice remaining wins the game.

Usage
-----

To run any of the scripts, the project root directory must be in the PYTHONPATH. The easiest way to ensure this is to run the Python console in the root directory by entering the following in the terminal while in the root directory:

    python
    
And then caling the appropriate method to run the script with:

    from liars_dice.XXX import <server/client>
    <server/client>.run()

### Server

To run the server, just call liars_dice.server.server.run(). This will run a server at the port number given by liars_dice/config.ini (9637 default). The server can only run one game at a time, though multiple games can be run on a single computer as long as the port numbers are different. There are no restrictions on the number of players who can join, though be warned that a large number of players can be very cumbersome to play with, and the GUI client may not suitable for such games.

### Client

There are three different clients included, though it is pretty simple to create your own if you'd prefer (see: 'How to Make Your Own Client'). All clients will connect to the host (localhost default) and port number (9637 default) provided in liars_dice/config.ini. They are:

#### Tkinter GUI (liars_dice.client.interface.tkinter_human.run())

This is a client intended for a human player. It is the most feature rich of the human clients, and is the only one which supports in-game chat. This is the suggested human client to use unless there are huge number of players, as the client is only capable of betting a maximum of 10 dice.

#### Console (liars_dice.client.interface.console_human.run())

This is a client intended for a human player. Although it doesn't contain all the features and niceties of the GUI version, for those who prefer a simple text interface, it serves very well.

#### Simple Bot (liars_dice.client.interface.simple_bot.run())

This is the only included client that allows the computer to participate, and is a great way to add more players to the game. The only restriction is that the bot does not support starting the game, and will automatically disconnect from the server before the game has started if it is client the server is awaiting such a message from. This typically shouldn't be a problem as long as a player joins the server before the bot does.


Configuration File
------------------

The configuration file at liars_dice/config.ini provides various server and client set-up values. To change the host or the port number, just edit this file with any text editor and substitute the desired value.

By default, all connections by the clients and server are via localhost. As such, if you'd like clients to connect to the server from different computers, you must change the host location to that corresponding with your server. If you'd like to play using only one computer for the server and all the clients, the host can be left as localhost.

How to Make Your Own Client
---------------------------

Making your own client is pretty simple. All you need to do is inherit liars_dice.client.player.Player and override the notification_XXX() methods corresponding to the events you'd like to respond to. By default, all event calls are ignored except notification_username_notification_request(), notification_play_request() and notification_can_start() which must be overriden, or else they will raise an exception.

A skeleton at liars_dice/client/interface/client_skeleton.py has been provided to make writing a client more convenient. Feel free to copy the file and extend it with your changes.

Both human and bots creation use the same process. The only difference is that

Note that if you intend to create a GUI, ensure that you integrate it with the Twisted networking library. Instructions on how to do this for your GUI of choice can be found at <http://twistedmatrix.com/documents/current/core/howto/choosing-reactor.html>.

