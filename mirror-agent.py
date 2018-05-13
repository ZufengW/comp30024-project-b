import board as bm
from random import randrange
from copy import deepcopy
import math


class Board2(bm.Board):
    # additional methods
    def value_board(self, team):
        """ determines how favourable this board state is

        :param team: the team who last moved
        :return: integer value
            (Higher is better for team. Lower is better for enemy)
        """
        enemy = Board2.get_opponent_team(team)  # enemy of team
        counts = {team: 0, enemy: 0}
        for piece in self.pieces:
            if piece is not None:
                # live pieces are worth points
                # also gives weight to distance of piece from middle
                piece_value = 30 - Board2.distance_of_pos_to_mid(piece['pos'])
                counts[piece['team']] += piece_value

                # During placing phase, consider if this piece is threatened
                # to be removed on its enemy's next action
                enemy_of_piece = Board2.get_opponent_team(piece['team'])
                if self.phase == bm.PLACING_PHASE \
                        and self.placing_pos_threatened(piece['pos'], enemy_of_piece):
                    # is worse if your own piece is threatened after your action
                    if piece['team'] == team:
                        # can subtract less here if want to play aggressive
                        counts[team] -= piece_value
                    else:  # enemy piece threatened. They could move it though
                        counts[enemy] -= piece_value // 3

        # symmetry in calculation
        return counts[team] - counts[enemy]

    @staticmethod
    def distance_of_pos_to_mid(pos):
        """ :returns Manhattan distance of pos to middle four squares """
        # middle indexes are: 3, 4
        x_diff = min(abs(3 - pos[0]), abs(4 - pos[0]))
        y_diff = min(abs(3 - pos[1]), abs(4 - pos[1]))
        return x_diff + y_diff

    def placing_pos_threatened(self, pos, enemy):
        """ Checks whether or not a pos is threatened during placing phase
        A piece is threatened by placing if there exists a square such that if
        an enemy is placed there, it causes the piece to be removed.

        :param pos: containing a piece
        :param enemy: enemy team of piece
        :return: whether or not piece is threatened
        """
        corners = self.get_corners()
        for x_off, y_off in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            side = (pos[0] - x_off, pos[1] - y_off)
            if self.has_piece_of_team(side, enemy) or side in corners:
                # one side is threatened. What about other?
                other_side = (pos[0] + x_off, pos[1] + y_off)
                if self.pos_can_be_placed_in(other_side, enemy):
                    return True
        return False
        # TODO consider edge case of final place

    def pos_can_be_placed_in(self, pos, team):
        """ :return whether or not pos is within team's placing boundary during
        Placing Phase and is available to be placed in"""
        if self.pos_empty(pos):  # is the position in bounds and empty?
            if team == bm.WHITE:  # is the position within team's starting zone?
                return pos[1] < 6
            elif team == bm.BLACK:
                return pos[1] > 1
        return False

    def get_best_value_for_state(self, team, enemy, depth, a, b):
        """ If this board is current state and it's team's turn,
        return the best value they can get.
        Does Minimax with alpha beta pruning.

        :param team: to move
        :param enemy: other team
        :param depth: depth of recursion
        :param a: Alpha
        :param b: Beta
        :return: highest value for this team
        """
        if depth == 0:  # base case: Go no deeper. Return valuation of board
            return self.value_board(enemy)

        # calculate all possible actions for team in this board state
        actions = self.get_all_actions(team)
        # Edge case: no possible actions. Need to pass turn
        if len(actions) == 0:
            board = deepcopy(self)
            board.do_action(None, team)  # pass turn
            if depth > 1:
                return board.get_best_value_for_state(enemy, team, depth - 1, a, b)
            else:
                return board.value_board(team)

        if depth % 2 == 1:  # maximising
            best_value = -math.inf
            for action in actions:
                board = deepcopy(self)
                board.do_action(action, team)
                best_value = max(best_value, board.get_best_value_for_state(
                        enemy, team, depth - 1, a, b))
                a = max(a, best_value)
                if b < a:
                    # print(b, "<", a, "D cut off: depth", depth)
                    break  # beta cut-off
            return best_value
        else:  # minimising
            best_value = math.inf
            for action in actions:
                board = deepcopy(self)
                board.do_action(action, team)
                best_value = min(best_value, board.get_best_value_for_state(
                        enemy, team, depth - 1, a, b))
                b = min(b, best_value)
                if b < a:
                    # print(b, "<", a, "C cut off: depth", depth)
                    break  # alpha cut-off
            return best_value

    def get_best_actions_from_state(self, team, enemy, depth=1, a=-math.inf, b=math.inf):
        """ Does minimax to get list of good actions for team

        :param team: to move
        :param enemy: other team
        :param depth: depth of recursion
        :param a: Alpha
        :param b: Beta
        :return: list of actions giving best value for team, and the best value
        """
        assert depth > 0  # only the other function should deal with base case
        actions = self.get_all_actions(team)
        # Edge case: no possible actions
        if len(actions) == 0:
            return [], self.value_board(team)

        # calculate how favourable the state is after applying each action
        next_values = [0] * len(actions)
        if depth % 2 == 1:  # maximising
            # sort actions (order by best actions first) to optimise pruning
            if self.phase == bm.PLACING_PHASE:
                actions.sort(key=lambda x: Board2.distance_of_pos_to_mid(x))
            best_value = -math.inf
            for i in range(len(next_values)):
                board = deepcopy(self)
                board.do_action(actions[i], team)
                next_values[i] = \
                    board.get_best_value_for_state(enemy, team, depth - 1, a, b)
                best_value = max(best_value, next_values[i])
                a = max(a, best_value)
                if b < a:
                    break  # beta cut-off (shouldn't happen because top depth)
        else:  # minimising
            best_value = math.inf
            for i in range(len(next_values)):
                board = deepcopy(self)
                board.do_action(actions[i], team)
                next_values[i] = \
                    board.get_best_value_for_state(enemy, team, depth - 1, a, b)
                best_value = min(best_value, next_values[i])
                b = min(b, best_value)
                if b < a:
                    break  # alpha cut-off (shouldn't happen because top depth)

        # filter out less-favourable states
        best_actions = []
        for i in range(len(next_values)):
            if next_values[i] == best_value:
                best_actions.append(actions[i])
        # TODO remove test printing
        print("    {} best_value {}, best_actions {}".format(
                team, best_value, best_actions))
        return best_actions, best_value

    @staticmethod
    def mirror_pos(pos):
        """
        :param pos: position to mirror
        :return: pos mirrored diagonally across the board
        """
        result = []
        for d in pos:
            if d < 4:
                d += (((4 - d) * 2) - 1)
            else:
                d -= (((d - 3) * 2) - 1)
            result.append(d)
        return result[0], result[1]


class Player(object):
    """
    An agent that can play Watch Your Back.
    This agent looks at the next state caused by each action to pick an action
    Like greedy-agent-5 but does mirroring if playing as black
    """

    def __init__(self, colour):
        """
        :param colour: either 'white' or 'black'
        """
        # set up a new board
        self.board = Board2()
        # set up team allegiances
        self.team = bm.BLACK
        if colour == 'white':
            self.team = bm.WHITE
        elif colour == 'black':
            self.team = bm.BLACK
        else:
            raise ValueError("colour must be 'white' or 'black'")
        self.enemy_team = bm.Board.get_opponent_team(self.team)

        # extra variables for mirror strategy
        self.mirroring = True  # whether or not still mirroring
        self.enemy_action = None  # enemy team's last action

    def action(self, turns):
        """
        called by the referee to request an action from the player

        :param turns: number of turns that have taken place
            since start of current game phase
        :return: next action
        """
        best_value = 99
        # Opening Book
        if self.board.phase == bm.PLACING_PHASE and turns == 0:
            # These are good first moves for WHITE
            best_actions = [(3, 4), (4, 4)]
        else:
            # different Minimax search depth depending on game phase
            depth = 2 + max(0, self.board.phase - 1)
            if self.board.phase == bm.PLACING_PHASE:
                depth = 3  # otherwise mirror doesn't work properly
            best_actions, best_value = self.board.get_best_actions_from_state(
                    self.team, self.enemy_team, depth)
            print("    {} Minimax depth: {}".format(self.team, depth))

        # Mirror strategy during Placing Phase
        if self.mirroring and self.team == bm.BLACK \
                and self.board.phase == bm.PLACING_PHASE and best_value < 2:
            # continue mirroring strategy
            mirror_action = Board2.mirror_pos(self.enemy_action)
            print("    {} Mirror. best_value {}, action {}".format(
                    self.team, best_value, mirror_action))
            if self.board.pos_can_be_placed_in(mirror_action, self.team):
                # Update the board with our action
                self.board.do_action(mirror_action, self.team)
                return mirror_action
            else:
                # should not happen because there should always be space
                print('M ASSERTION INCORRECT')
                self.mirroring = False
        else:
            # stop mirroring either because white did bad move
            # or Placing Phase ended
            self.mirroring = False

        our_action = None  # will forfeit turn if no actions
        if len(best_actions) > 0:
            # choose random action among our best actions
            our_action = best_actions[randrange(0, len(best_actions))]

        # Update the board with our action
        self.board.do_action(our_action, self.team)
        return our_action

    def update(self, action):
        """
        Inform player about opponent's most recent move

        :param action: opponent's action
        :return: Nothing
        """
        # Update our board with the opponent's action
        self.board.do_action(action, self.enemy_team)
        self.enemy_action = action
