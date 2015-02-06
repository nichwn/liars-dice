"""

Constants for distinguishing message types passed and received by servers and
clients.

"""

DELIMITER = ":"  # delimiter between the command and the content

USERNAME = "username"
PLAYER_LEFT = "left"
PLAYER_JOINED = "joined"
CAN_START = "can_start"

START = "start"
NEXT_ROUND = "next_round"
NEXT_TURN = "next_turn"
PLAY = "play"
WINNER = "winner"

PLAYER_LOST_DIE = "player_lost_die"
PLAYER_ELIMINATED = "eliminated"
PLAYER_HAND = "hand"
PLAYER_STATUS = "player_status"

BET = "bet"
LIAR = "liar"
SPOT_ON = "spot_on"

CHAT = "chat"
