# Watch Your Back
A repo containing AI agents that can play the game "Watch Your Back".
Also contains the referee to run the game.

## Set up
Clone this repo.
```bash
git clone git@github.com:ZufengW/comp30024-project-b.git
```
From its root directory, run a game:
```bash
python referee.py white_module black_module
```
Where `python` is the name of your Python 3.6 interpreter,
`white_module` and `black_module` are the full names of the modules
containing the `Player` classes playing as White player and Black player. For example:
```bash
python3 referee.py greedy-agent-5 mirror-agent
```

## How to extend
You can add more agents. (See `random-agent.py` for example.)

## Rules of the game
*Watch Your Back!* is a two player turn-based board game. Each player controls a team of twelve rogues who fight to the death. The easiest way to cut down an enemy is to stab them in the back. Control your lawless warriors to jump and slash their way around the board surrounding and silencing your enemies until none remain. And, of course, *watch your back!*

### Board
*Watch Your Back!* plays on an 8x8 **board** made of 64 **squares**. Squares are labelled by their *column* and *row* numbers, starting with square (0,0) in the top-left corner of the board. Column indices increase to the right, and row indices increase down the board.
In addition, the special squares (0,0), (7,0), (0,7) and (7,7) are called **corner** squares.

### Gameplay
Two players (**Black** and **White**) play the game. Each player controls 12 **pieces** (each piece represents one ‘fighter’ on a player’s ‘team’). Initially, there are no pieces on the board. In the first part of the game, the players take turns placing their pieces onto the board during a **placing phase**. Then the players take turns moving their pieces around the board during a **moving phase**. In both phases, players can **eliminate** opponent pieces by **surrounding** them with two of their own pieces (the surrounded ‘fighter’ will be ‘stabbed in the back’). The aim of the game is to eliminate all of the opponent’s pieces.

### Placing Phase

The game starts with a **placing phase**. In the placing phase, players take turns putting their pieces on the board. White has the first turn in the placing phase.

On each turn, one player places one piece in any **unoccupied square** within their **starting zone**. (An unoccupied square is any non-corner square without a piece.) White’s starting zone includes all squares in the top 6 rows of the board except for the top corners (0,0) and (7,0). Black’s starting zone includes all squares in the bottom 6 rows except for the bottom corners (0,7) and (7,7).

When a player places a piece, zero or more pieces may be **eliminated**. A piece is eliminated if it is **surrounded** on two sides (horizontally or vertically) by enemy pieces or *corners*.
A piece is not eliminated if it is surrounded diagonally or on two sides that are not vertically or horizontally opposite. A piece is not eliminated if it is surrounded by non-enemy pieces.
Placing a single piece may eliminate multiple enemy pieces if it causes them all to become surrounded as per the above description.

Placing a piece may lead to the piece itself being eliminated if it is placed on a square that is already surrounded. However, a piece always gets to surround and eliminate nearby pieces before it is eliminated itself. For example, if Black places a piece in the square marked 3 in the configuration `BW3W`, this piece is not eliminated because it will surround and eliminate the White piece on its left first.

Once each player has placed 12 pieces on the board (regardless of how many of their pieces remain on the board), the placing phase ends and the game continues to the **moving phase**.

### Moving Phase
In the **moving phase**, players take turns moving their pieces around the board. Like in the placing phase, White has the first turn in the moving phase.

On each turn, one player moves one of their own pieces into a nearby unoccupied square. During the moving phase, players can move their pieces to squares outside of their **starting zone**.

A player can move their piece to the square above, below, or to the right or left of its current square (as long as these squares are unoccupied). They cannot move a piece diagonally.

A player may make their piece **jump** over a horizontally or vertically adjacent piece into the square opposite that piece (as long as the opposite square is unoccupied). For example, in `7WWB3`, the White player can make their middle piece jump over the leftmost White piece into the square marked 7, or jump over the Black piece to its right into the square marked 3.

It is possible that none of a player’s pieces will have any available squares to move to on the player’s turn. If this is the case, the player must **forfeit** their move and play continues with the other player’s next turn. In all other cases, a player must make exactly one move (one regular move or one jump) on each of their turns in the movement phase.

Each time a player moves a piece, zero or more pieces may be **eliminated** according to the same rules as for elimination in the **placing phase**.

After 128 moves take place in the movement phase including any forfeited moves (after 64 moves for each player) the board **shrinks**: The squares in the outermost rows and columns are removed from the board and the squares (1,1), (6,1), (1,6) and (6,6) become corner squares. Any pieces located on any of these squares are eliminated.

After a further 64 moves take place (so after a total of 192 moves, or 96 moves each), the board shrinks again: The outermost remaining squares are removed from the board and the squares (2,2), (2,5), (5,2) and (5,5) become corner squares. Again, any pieces located on any of these squares are eliminated.

The transformation of squares into corner squares during this shrinking process may result in zero or more pieces being eliminated. The rules for these new corner squares eliminating pieces are the same as the rules for placing enemy pieces during the placing phase. That is, a piece next to a new corner square is eliminated if there is an enemy piece on its opposite side (the side opposite the new corner piece). New corner squares eliminate nearby pieces in order starting with the top-left new corner square and proceeding *counter-clockwise* around the board. That is, the new corner squares eliminate nearby squares in the order: top-left, bottom-left, bottom-right, top-right.

### End of the game
The game ends if either player has fewer than 2 pieces remaining. In this case, the player with 2 or more pieces remaining **wins the game**. If both players have fewer than 2 pieces remaining as a result of the same turn (for example, due to multiple pieces being eliminated during the shrinking of the board), then the game ends in a **tie**.
