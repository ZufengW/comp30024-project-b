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
        self.board = []
        for i in range(BOARD_SIZE):
            self.board.append([None] * BOARD_SIZE)

        self.pieces = []
        # start in placing phase
        self.phase = PLACING_PHASE
        # number of turns taken place since start of current game phase
        self.turn_count = 0

    def do_action(self, action, team):
        """
        Direct way to do the action

        :param action: action to make (same format as for referee)
        :param team: team doing the action
        :return:
        """
        # TODO consider validation
        # Placing phase: (x, y)
        if self.phase == PLACING_PHASE:
            self.place_piece(action, team)
        else:
            # Move phase:    ((a, b), (c, d))
            start_pos, end_pos = action
            self.move_piece(start_pos, end_pos)
        self.turn_count += 1
        # advance to next phase if enough moves have happened
        if self.phase == PLACING_PHASE and self.turn_count == 24:
            self.advance_phase()
        elif self.phase == MOVING_PHASE and self.turn_count == 128:
            self.advance_phase()
        elif self.phase == SHRINK1_PHASE and self.turn_count == 64:
            self.advance_phase()

    def place_piece(self, position, team):
        """
        Suitable for placing phase.
        This is the only way to add a new piece to the board.
        Doesn't check if move is valid

        :param position: (c, r)
        :param team: WHITE or BLACK
        :return:
        """
        c, r = position
        # TODO: consider adding/removing validation of this move e.g. in bounds
        assert self.in_bounds(position)
        assert self.get_piece_at_pos(position) is None
        self.board[c][r] = len(self.pieces)  # store the index
        new_piece = {
            "pos": position,
            "team": team
        }
        self.pieces.append(new_piece)
        # check if any pieces were taken
        self.update_pieces_removed(position)

    def move_piece(self, start_pos, end_pos):
        """
        Moves the piece from start to end. For moving phase.

        :param start_pos: starting position, which must have piece
        :param end_pos: destination of this move
        :return:
        """
        # TODO: consider adding/removing validation of the positions and phase
        # Some validation of move
        assert self.phase != PLACING_PHASE  # cannot move in placing phase
        assert self.in_bounds(start_pos) and self.in_bounds(end_pos)
        assert self.get_piece_at_pos(end_pos) is None  # destination is empty
        assert end_pos not in self.get_corners()
        piece = self.get_piece_at_pos(start_pos)
        assert piece is not None  # make sure there is a piece to move
        # TODO: consider adding validation of the move itself
        piece.pos = end_pos  # update position in pieces list
        assert self.pieces[self.board[start_pos[0]][start_pos[1]]].pos == piece.pos # TODO just testing if my logic is correct
        # update positions on board
        self.board[end_pos[0]][end_pos[1]] = self.board[start_pos[0]][start_pos[1]]
        self.board[start_pos[0]][start_pos[1]] = None

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
        self.turn_count = 0
        # TODO: shrink borders and remove outside pieces
        pieces_to_remove = []
        for index, piece in enumerate(self.pieces):
            if not self.in_bounds(piece.pos):
                pieces_to_remove.append(index)
                self.board[piece.pos[0]][piece.pos[1]] = None
        self.pieces = [x for i, x in enumerate(self.pieces)
                       if i not in pieces_to_remove]
        # TODO apply corners and remove more pieces
        corners = self.get_corners()  # new corners
        # top-left corner
        col, row = corners[0]
        self.update_pieces_removed((col + 1, row), attack=False)
        self.update_pieces_removed((col, row + 1), attack=False)
        # bottom-left corner L
        col, row = corners[0]
        self.update_pieces_removed((col + 1, row), attack=False)
        self.update_pieces_removed((col, row - 1), attack=False)
        # bottom-right corner _|
        col, row = corners[0]
        self.update_pieces_removed((col - 1, row), attack=False)
        self.update_pieces_removed((col, row - 1), attack=False)
        # top-right corner -.
        col, row = corners[0]
        self.update_pieces_removed((col - 1, row), attack=False)
        self.update_pieces_removed((col, row + 1), attack=False)

    def get_piece_at_pos(self, position):
        """
        Returns the piece at a position (c, r),
        or None if out of bounds or no piece.

        :param position: tuple (column, row)
        :return: piece, or None if there isn't one or out of bounds
        """
        # also check if position is in bounds
        if self.in_bounds(position):
            index = self.board[position[0]][position[1]]
            if index is not None:
                return self.pieces[index]
        return None

    def has_piece_of_team(self, position, team):
        """
        :return: whether or not the square contains a piece
            belonging to team
        """
        piece = self.get_piece_at_pos(position)
        if piece:
            return piece.team == team
        return False

    def remove_piece_at_pos(self, position):
        """ removes a piece from the game """
        index = self.board[position[0]][position[1]]
        # delete the piece from the board and the piece list
        self.board[position[0]][position[1]] = None
        self.pieces.pop(index)

    def in_bounds(self, position):
        """:return: whether or not a position is on the board. Depends on phase
        """
        # but in-bounds also depends on the game state
        if self.phase == PLACING_PHASE or self.phase == MOVING_PHASE:
            return 0 <= position[0] < BOARD_SIZE \
                    and 0 <= position[1] < BOARD_SIZE
        elif self.phase == SHRINK1_PHASE:
            return 1 <= position[0] < BOARD_SIZE - 1 \
                    and 1 <= position[1] < BOARD_SIZE - 1
        else:
            return 2 <= position[0] < BOARD_SIZE - 2 \
                   and 2 <= position[1] < BOARD_SIZE - 2

    def update_pieces_removed(self, mid_pos, attack=True):
        """
        Removes pieces from the board due to a
            new piece entering this position

        :param mid_pos: position of this piece (c, r)
        :param attack: whether or not this piece moved here itself
            (if not, it's just defending against corners shrinking)
        :return:
        """
        mid_team = self.get_piece_at_pos(mid_pos).team
        enemy_team = Board.get_opponent_team(mid_team)
        c_mid, r_mid = mid_pos

        # check if any 4 surrounding squares have an opponent to take
        if attack:
            offsets = (-1, 0), (0, 1), (1, 0), (0, -1)
            for c_off, r_off in offsets:
                adj_pos = (c_mid + c_off, r_mid + r_off)
                if self.has_piece_of_team(adj_pos, enemy_team):
                    # enemy piece here, check other side
                    opp_pos = (c_mid + 2 * c_off, r_mid + 2 * r_off)
                    if self.has_piece_of_team(opp_pos, mid_team):
                        # adj piece is surrounded. Remove it
                        self.remove_piece_at_pos(adj_pos)
                    elif opp_pos in self.get_corners():
                        # also gets removed if corner...
                        self.remove_piece_at_pos(adj_pos)
        # Check if the mid piece is itself removed by opponents (and corners)
        # either by up/down or L/R
        u_pos = (c_mid, r_mid - 1)
        d_pos = (c_mid, r_mid + 1)
        l_pos = (c_mid - 1, r_mid)
        r_pos = (c_mid + 1, r_mid)
        corners = self.get_corners()
        if ((self.has_piece_of_team(u_pos, enemy_team) or u_pos in corners) and
            (self.has_piece_of_team(d_pos, enemy_team) or d_pos in corners)) or\
            ((self.has_piece_of_team(l_pos, enemy_team) or l_pos in corners) and
             (self.has_piece_of_team(r_pos, enemy_team) or r_pos in corners)):
            self.remove_piece_at_pos(mid_pos)

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
        else:  # self.phase == SHRINK2_PHASE:
            return (2, 2), (2, 5), (5, 5), (5, 2)

    @staticmethod
    def get_opponent_team(team):
        """ given a team (WHITE or BLACK), returns the opposing team"""
        if team == WHITE:
            return BLACK
        elif team == BLACK:
            return WHITE
        raise ValueError("team should either be BLACK or WHITE")
