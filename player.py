"""
By Zufeng Wang
"""

BOARD_SIZE = 8
# board constants
BLACK = "@"
WHITE = "O"
TEAMS = (WHITE, BLACK)
EMPTY = "-"
CORNER = 'X'
# phases: 0: placing phase, 1: moving phase begin
#   2: after shrink 1, 3: after shrink 2
PLACING_PHASE = 0
MOVING_PHASE = 1
SHRINK1_PHASE = 2
SHRINK2_PHASE = 3


class Player(object):
    """
    An agent that can play Watch Your Back.
    This agent makes random valid actions on its turn
    """

    def __init__(self, colour):
        """
        :param colour: either 'white' or 'black'
        """
        # set up a new board
        self.board = Board()
        self.phase = PLACING_PHASE  # First phase: Placing phase
        if colour == 'white':
            self.team = WHITE
        else:
            self.team = BLACK

    def action(self, turns):
        """
        called by the referee to request an action from the player

        :param turns: number of turns that have taken place
            since start of current game phase
        :return: next action
        """
        # gets list of all actions
        # moves = get_all_actions(self.team)
        # chooses a random one and returns it

        pass

    def update(self, action):
        """
        Inform player about opponent's most recent move

        :param action: opponent's action
        :return: Nothing
        """
        # Update our board


class Board(object):
    def __init__(self):
        # initialise empty board
        self.positions = {
            WHITE: [],
            BLACK: []
        }
        # start in placing phase
        self.phase = PLACING_PHASE

    def place_piece(self, team, position):
        """
        Suitable for placing phase.
        Doesn't check if move is valid

        :param team: WHITE or BLACK
        :param position: (x, y)
        :return:
        """
        # TODO: consider adding validation of this move
        self.positions[team].append(position)
        # TODO: now check if any pieces were taken

    def move_piece(self, start, end):
        """
        Moves the piece from start to end. For moving phase.

        :param start:
        :param end:
        :return:
        """
        # TODO: consider adding validation of this move, and phase
        # e.g. check if there is a piece there, and target is empty
        pass

    def get_all_actions(self, team):
        """
        Returns a list of all possible moves for a team.
        Form of actions returned depends on board's phase.

        :param team: WHITE or BLACK
        :return: list of placing positions (c, r), or moves ((a, b), (c, d))
        """
        # set some bounds
        if self.phase == PLACING_PHASE:
            # the valid places are all empty squares within team zone
            pass
        else:
            # moving phase. Return all valid moves of the team's pieces
            pass

    def advance_phase(self):
        """advance the phase of this board"""
        self.phase += 1
        # TODO: apply shrinking and remove relevant pieces
        # first remove any pieces due to edges reducing
        # then apply new corners one at a time and check if any more removed

    def update_pieces_removed(self, mid_pos):
        """
        Removes pieces from the board due to a
            new piece entering this position

        :param mid_pos: position of this piece
        :return:
        """
        # due to a piece being added to mid_pos, it is possible for pieces
        # in 4 adjacent squares, as well as the start piece itself,
        # to be removed
        # So we record the existence of any pieces at these positions
        # column offset, row offset from centre position
        offsets = ((0, 0), (0, 2), (0, 1), (0, -2), (0, -1),
                   (2, 0), (1, 0), (-2, 0), (-1, 0))
        # mid, uu, u, dd, d, rr, r, ll, l
        pieces = [None] * 9
        for team in TEAMS:
            for col, row in self.positions[team]:
                c_diff = col - mid_pos[0]
                r_diff = row - mid_pos[0]
                for index, offset in enumerate(offsets):
                    if (c_diff, r_diff) == offset:
                        pieces[index] = team
        # Also add corners to the list
        for col, row in self.get_corners():
            c_diff = col - mid_pos[0]
            r_diff = row - mid_pos[0]
            for index, offset in enumerate(offsets):
                if (c_diff, r_diff) == offset:
                    pieces[index] = CORNER
        # NOTE: after shrinkage, corners are applied one at a time instead
        mid = pieces[0]  # this is the piece that just moved in
        assert mid is not None
        # Cross is complete. Check if enemy pieces are removed (u, r, d, l)
        for i in range(2, len(pieces), step=2):
            enemy = pieces[i]
            if enemy and enemy != mid:
                # check if flanked on other side by corner or mid's ally
                if pieces[i-1] == mid or pieces[i-1] == CORNER:
                    # this enemy is removed from the board
                    pieces[i] = None
                    # TODO set this piece to be removed
        # now check if mid is itself removed
        enemy = Board.get_opponent_team(mid)
        if pieces[2] == enemy and pieces[4] == enemy:
            pieces[0] = None
            # TODO set this piece to be removed


        # TODO: find a function to remove elements from a list
        # preferably multiple in one go to avoid errors in iteration

    def get_corners(self):
        """
        returns the positions of the current corners of the board
        in CCW order starting from top-left

        :return: list of positions of corners
        """
        if self.phase == PLACING_PHASE or self.phase == MOVING_PHASE:
            return (0, 0), (0, 7), (7, 7), (7, 0)
        elif self.phase == SHRINK1_PHASE:
            return (1, 1), (1, 6), (6, 6), (6, 1)
        else:
            # self.phase == SHRINK2_PHASE:
            return (2, 2), (2, 5), (5, 5), (5, 2)

    @staticmethod
    def get_opponent_team(team):
        """ given a team (WHITE or BLACK), returns the opposing team"""
        if team == WHITE:
            return BLACK
        elif team == BLACK:
            return WHITE
        raise ValueError("team should either be BLACK or WHITE")

    # need:
    # way to check which pieces where taken (and update board)
