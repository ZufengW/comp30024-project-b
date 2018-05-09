import board as b
import re


class Player(object):
    """
    An agent that can play Watch Your Back.
    Gets moves from human user
    """

    def __init__(self, colour):
        """
        :param colour: either 'white' or 'black'
        """
        # set up a new board
        self.board = b.Board()
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
        assert turns == self.board.turn_count
        # gets list of all actions
        actions = self.board.get_all_actions(self.team)

        if len(actions) == 0:
            return None   # will forfeit turn if no actions
        # get action from user input. Keep looping until valid input
        while True:
            line = input('Enter an action: col row\n').strip()
            parts = re.split(r'\D+', line)  # split by anything not digit
            if parts[0] == '':
                parts.remove('')
            if len(parts) < 2:
                print('Enter two integers. (Less than two found)')
                continue
            try:
                input_action = (int(parts[0]), int(parts[1]))
            except ValueError:
                print('Enter two integers. (Found non-integers)')
                continue
            if input_action in actions:
                # this is valid action
                # Update the board with our action
                self.board.do_action(input_action, self.team)
                return input_action
            else:
                print('Action not in list of valid actions')

    def update(self, action):
        """
        Inform player about opponent's most recent move

        :param action: opponent's action
        :return: Nothing
        """
        # Update our board with the opponent's action
        self.board.do_action(action, self.enemy_team)
