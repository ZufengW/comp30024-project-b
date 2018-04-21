import board as b


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
        self.board = b.Board()
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
        assert turns == self.board.turn_count
        # gets list of all actions
        actions = self.board.get_all_actions(self.team)
        # print(self.team, "can choose one of ", actions)
        # TODO chooses a random one and returns it
        our_action = None
        if len(actions) > 0:
            our_action = actions[0]
        # Update the board with our action
        self.board.do_action(our_action, self.team, test=True)

        return our_action

    def update(self, action):
        """
        Inform player about opponent's most recent move

        :param action: opponent's action
        :return: Nothing
        """
        # Update our board
        self.board.do_action(action, self.enemy_team)