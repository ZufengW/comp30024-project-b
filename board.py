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


class Board(object):
    def __init__(self):
        # initialise empty board
        self.board = []
        for i in range(BOARD_SIZE):
            self.board.append([None] * BOARD_SIZE)

        self.pieces = [None] * 24
        # start in placing phase
        self.phase = PLACING_PHASE
        # number of turns taken place since start of current game phase
        self.turn_count = 0

    def do_action(self, action, team):
        """
        Updates the board with a team's action

        :param action: action to make (same format as for referee)
        :param team: team doing the action
        :return:
        """
        # TODO consider validation
        if action is None:  # forfeit turn. Turn count still increases
            pass
        # Placing phase: (x, y)
        elif self.phase == PLACING_PHASE:
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
        elif self.phase == SHRINK1_PHASE and self.turn_count == 192:
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

        new_piece = {
            "pos": position,
            "team": team
        }
        # find an empty position in the list to place the piece
        new_piece_index = self.pieces.index(None)
        self.pieces[new_piece_index] = new_piece
        self.board[c][r] = new_piece_index  # store the index on the board
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
        piece['pos'] = end_pos  # update position in pieces list
        # update positions on board
        self.board[end_pos[0]][end_pos[1]] = self.board[start_pos[0]][start_pos[1]]
        self.board[start_pos[0]][start_pos[1]] = None
        # update pieces removed due to this piece moving
        self.update_pieces_removed(piece['pos'])

    def get_all_actions(self, team):
        """
        Returns a list of all possible moves for a team.
        Form of actions returned depends on board's phase.

        :param team: WHITE or BLACK
        :return: list of placing positions (c, r), or moves ((a, b), (c, d))
        """
        possible_moves = []
        if self.phase == PLACING_PHASE:
            # the valid places are all empty squares within team zone
            # if team == WHITE
            rows_start = 0
            rows_end = 6
            if team == BLACK:
                rows_start = 2
                rows_end = BOARD_SIZE
            corners = self.get_corners()
            for c in range(BOARD_SIZE):
                for r in range(rows_start, rows_end):
                    if self.get_piece_at_pos((c, r)) is None \
                            and (c, r) not in corners:
                        possible_moves.append((c, r))
            return possible_moves

        # moving phase. Return all valid moves of the team's pieces
        for piece in self.pieces:
            if piece is not None and piece['team'] == team:
                piece_moves = self.get_all_moves_for_piece_at_pos(piece['pos'])
                # add this piece's moves to the list
                possible_moves += piece_moves
        return possible_moves

    def get_all_moves_for_piece_at_pos(self, position):
        """
        Returns a list of all moves that can be made by the piece at position

        :param position: position of this piece
        :return: list of possible moves: ((a, b), (c, d))
        """
        possible_moves = []
        # represents four cardinal directions that each piece can move in
        offsets = ((1, 0), (0, 1), (-1, 0), (0, -1))
        corners = self.get_corners()
        for c_off, r_off in offsets:
            adj_pos = (position[0] + c_off, position[1] + r_off)
            if self.in_bounds(adj_pos):
                piece_index = self.board[adj_pos[0]][adj_pos[1]]
                if piece_index is None:
                    if adj_pos not in corners:
                        # position has no pieces or corners. Can move here
                        possible_moves.append((position, adj_pos))
                else:
                    # there is a piece here. Can we jump over?
                    opp_pos = (adj_pos[0] + c_off, adj_pos[1] + r_off)
                    if self.pos_empty(opp_pos):
                        possible_moves.append((position, opp_pos))
        return possible_moves

    def advance_phase(self):
        """advance the phase of this board"""
        if self.phase == PLACING_PHASE:
            # turn count doesn't reset if board shrinks
            self.turn_count = 0
        self.phase += 1

        corners = self.get_corners()  # new corners
        # Remove pieces outside the new bounds or overlapping with new corners
        for index, piece in enumerate(self.pieces):
            if piece is not None:
                if not self.in_bounds(piece['pos']) or piece['pos'] in corners:
                    self.remove_piece_at_pos(piece['pos'])

        # apply corners and remove more pieces if needed
        # top-left corner
        col, row = corners[0]
        self.update_pieces_removed((col + 1, row), attack=False)
        self.update_pieces_removed((col, row + 1), attack=False)
        # bottom-left corner L
        col, row = corners[1]
        self.update_pieces_removed((col + 1, row), attack=False)
        self.update_pieces_removed((col, row - 1), attack=False)
        # bottom-right corner _|
        col, row = corners[2]
        self.update_pieces_removed((col - 1, row), attack=False)
        self.update_pieces_removed((col, row - 1), attack=False)
        # top-right corner -.
        col, row = corners[3]
        self.update_pieces_removed((col - 1, row), attack=False)
        self.update_pieces_removed((col, row + 1), attack=False)

    def get_piece_at_pos(self, position):
        """
        Returns the piece at a position (c, r),
        or None if out of bounds or no piece.
            First checks if position is within bounds

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
            return piece['team'] == team
        return False

    def pos_empty(self, pos):
        """
        Returns whether or not position is in bounds and free of pieces
        and corners. (i.e. available for other pieces to move there)

        :param pos: position on board
        :return: whether or not position is in bounds
            and free of pieces and corners
        """
        return self.in_bounds(pos) and self.board[pos[0]][pos[1]] is None \
            and pos not in self.get_corners()

    def remove_piece_at_pos(self, position):
        """ removes a piece from the game """
        index = self.board[position[0]][position[1]]
        # delete the piece from the board and the piece list
        self.board[position[0]][position[1]] = None
        # results in an empty spot in the piece list
        self.pieces[index] = None

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
        Removes pieces from the board due to a new piece entering this position

        If attack=False, then the piece here (if there is one)
        is not the aggressor.

        If there is no piece in mid_pos, nothing happens.

        :param mid_pos: position of this piece (c, r)
        :param attack: whether or not this piece moved here itself
            (if not, it's just defending against corners shrinking)
        :return:
        """
        # TODO fix this
        mid_piece = self.get_piece_at_pos(mid_pos)
        if mid_piece is None:
            return  # no piece in the middle, so nothing to remove
        mid_team = mid_piece['team']
        enemy_team = Board.get_opponent_team(mid_team)
        c_mid, r_mid = mid_pos

        # check if any 4 surrounding squares have an opponent to take
        if attack:
            offsets = (-1, 0), (0, 1), (1, 0), (0, -1)
            for c_off, r_off in offsets:
                adj_pos = (c_mid + c_off, r_mid + r_off)
                if self.has_piece_of_team(adj_pos, enemy_team):
                    # enemy piece here, check other side
                    opp_pos = (adj_pos[0] + c_off, adj_pos[1] + r_off)
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

    def distance_to_nearest_of_team(self, pos, team):
        """ returns distance to nearest piece belonging to team

        :param pos: (c, r)
        :param team: team of piece search for
        :return: Manhattan distance between pos and piece
        """
        best_dist = 999
        for piece in self.pieces:
            if piece is not None and piece['team'] == team:
                dist = abs(pos[0] - piece['pos'][0]) \
                        + abs(pos[1] - piece['pos'][1])
                best_dist = min(dist, best_dist)
        if best_dist == 999:
            return -1  # did not find any pieces
        return best_dist

    def get_piece_nearest_to_pos_of_team(self, pos, team):
        """ returns piece nearest to pos and belonging to team

        :param pos: (c, r)
        :param team: team of piece search for
        :return: piece object, or None if couldn't find
        """
        best_dist = 999
        nearest_piece = None
        for piece in self.pieces:
            if piece is not None and piece['team'] == team:
                dist = abs(pos[0] - piece['pos'][0]) \
                        + abs(pos[1] - piece['pos'][1])
                if dist < best_dist:
                    best_dist = dist
                    nearest_piece = piece
        return nearest_piece

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

    def check_winner(self):
        """
        Checks if game is over and returns winner
            T for tie. None for game not yet finished

        :return: BLACK or WHITE or 'T' or None
        """
        black_count = 0
        white_count = 0
        for piece in self.pieces:
            if piece is not None:
                if piece['team'] == WHITE:
                    white_count += 1
                elif piece['team'] == BLACK:
                    black_count += 1
                else:
                    raise ValueError("team should be BLACK or WHITE")
        if black_count < 2 and white_count < 2:
            # tie because both teams have fewer than 2 pieces on same turn
            return 'T'
        elif black_count < 2:
            return WHITE
        elif white_count < 2:
            return BLACK
        return None

    @staticmethod
    def get_opponent_team(team):
        """ given a team (WHITE or BLACK), returns the opposing team"""
        if team == WHITE:
            return BLACK
        elif team == BLACK:
            return WHITE
        raise ValueError("team should either be BLACK or WHITE")

    def print_board(self):
        """ prints the current layout of the board """
        corners = self.get_corners()
        print('=== BOARD: phase {}, turn {} ==='
              .format(self.phase, self.turn_count))
        print('0 1 2 3 4 5 6 7')
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                char_to_print = ' '
                piece_index = self.board[col][row]
                if piece_index is not None:
                    char_to_print = self.pieces[piece_index]['team']
                elif (col, row) in corners:
                    char_to_print = CORNER
                print(char_to_print, end=' ')
            print("")

    # TODO def tostring
