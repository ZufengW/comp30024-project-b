import board as b
from random import randrange
from copy import deepcopy


class Board2(b.Board):
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
                if self.phase == b.PLACING_PHASE and self.placing_pos_threatened(piece['pos'], enemy_of_piece):
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
                if self.__pos_can_be_placed_in(other_side, enemy):
                    return True
        return False
        # TODO consider edge case of final place

    def __pos_can_be_placed_in(self, pos, team):
        """ :return whether or not pos is within team's placing boundary during
        Placing Phase and is available to be placed in"""
        if self.pos_empty(pos):  # is the position in bounds and empty?
            if team == b.WHITE:  # is the position within team's starting zone?
                return pos[1] < 6
            elif team == b.BLACK:
                return pos[1] > 1
        return False

    def get_best_value_from_state(self, team):
        """ If this board is current state and it's team's turn,
        return the best value they can get.

        :param team: to move
        :return: highest value for this team
        """
        # calculate all possible actions
        actions = self.get_all_actions(team)
        next_values = [0] * len(actions)
        best_value = -999
        for i in range(len(next_values)):
            board = deepcopy(self)
            board.do_action(actions[i], team)
            # calculate how favourable the next state is
            next_values[i] = board.value_board(team)
            # and keep track of the best value
            best_value = max(best_value, next_values[i])
        return best_value


class Player(object):
    """
    An agent that can play Watch Your Back.
    This agent looks at the next state caused by each action to pick an action
    TODO Like greedy-agent-3 but does minimax
    """

    def __init__(self, colour):
        """
        :param colour: either 'white' or 'black'
        """
        # set up a new board
        self.board = Board2()
        # set up team allegiances
        self.team = b.BLACK
        if colour == 'white':
            self.team = b.WHITE
        elif colour == 'black':
            self.team = b.BLACK
        else:
            raise ValueError("colour must be 'white' or 'black'")
        self.enemy_team = b.Board.get_opponent_team(self.team)

    def action(self, turns):
        """
        called by the referee to request an action from the player

        :param turns: number of turns that have taken place
            since start of current game phase
        :return: next action
        """
        # assert turns == self.board.turn_count
        # gets list of all actions
        actions = self.board.get_all_actions(self.team)

        # calculate how favourable the state is after applying each action
        next_values = [0] * len(actions)
        best_value = 999
        for i in range(len(next_values)):
            board = deepcopy(self.board)
            board.do_action(actions[i], self.team)
            # Do opponent's turn to calculate the value of their best response
            # calculate how favourable the next state is based on opponent
            next_values[i] = board.get_best_value_from_state(self.enemy_team)
            # and keep track of the best value (lowest enemy value)
            best_value = min(best_value, next_values[i])

        # filter out less-favourable states
        best_actions = []
        for i in range(len(next_values)):
            if next_values[i] == best_value:
                best_actions.append(actions[i])

        print("{}: best {}, len-best {}, len-all {}".format(self.team, best_value, len(best_actions), len(actions)))
        our_action = None  # will forfeit turn if no actions
        if len(best_actions) > 0:
            # choose random action
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
