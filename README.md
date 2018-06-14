# Watch Your Back
A repo containing AI agents that can play the game "Watch Your Back".
Also contains the referee to run the game.

## Set up
`cd` to the directory where you want to clone this repo
```bash
git clone git@github.com:ZufengW/comp30024-project-b.git
```

Run a game:
```bash
python referee.py white_module black_module
```
Where `python` is the name of the Python 3.6 interpreter,
`white_module` and `black_module` are the full names of the modules
containing the `Player` classes playing as White player and Black player.

## How to extend
You can add more agents. (See `random-agent.py` for example.)
