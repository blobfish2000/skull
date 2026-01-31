from random import randint, choice
import os
from time import sleep
import mcts

class TicTacToeState:
    def __init__(self, players = 2, starting_cards = 4):
        self.to_play = 0
        self.board = [['.','.','.'],['.','.','.'],['.','.','.']]
        self.winner = -2

    def valid_plays(self) -> list[int]:
        """
        0-9, grid
        """
        if self.winner >= -1:
            return []
        rowjoin = self.board[0] + self.board[1] + self.board[2]
        plays = [i for i, p in enumerate(rowjoin) if p == '.']
        return plays

    def render(self) -> str:
        ps  = "Player: " + str(self.to_play) + "\n\n"
        for row in self.board:
            ps += " ".join([str(r) for r in row])
            ps += "\n"
        ps += "Winner:" + str(self.winner) + "\n"
        return ps

    def _next_player(self) -> int:
        return (self.to_play + 1) % self.players

    def _winner(self) -> int:
        for player in [0,1]:
            for column in range(3):
                good = True
                for row in range(3):
                    if self.board[column][row] != player:
                        good = False
                if good:
                    return player

            for row in range(3):
                good = True
                for column in range(3):
                    if self.board[column][row] != player:
                        good = False
                if good:
                    return player

            good = True
            for d in range(3):
                if self.board[d][d] != player:
                    good = False
            if good:
                return player

            good = True
            for d in range(3):
                if self.board[2-d][d] != player:
                    good = False
            if good:
                return player
        if len(self.valid_plays()) == 0:
            return -1
        else:
            return -2


    def advance(self, play) -> None:
        player = self.to_play
        row = play % 3
        column = int((play - row) / 3.0)
        self.board[column][row] = player
        self.to_play = 1 - self.to_play
        self.winner = self._winner()
        return f"Player {player} plays {play}"




game = TicTacToeState()
plays = []
while game.winner == -2:
    os.system("clear")
    print(game.render())
    print("-"*30)
    print("\n".join(plays))
    valid = sorted(game.valid_plays())
    play = -3
    if game.to_play == 0:
        s = mcts.Searcher(game)
        play = s.find(1000)
        #print("Valid plays: " + ", ".join([str(x) for x in valid]))
        #while play not in valid:
        #    play = int(input("Play? "))
        #print() 
    else:
        s = mcts.Searcher(game)
        play = s.find(1000)
    plays.append(game.advance(play))

os.system("clear")
print(game.render())
print("-"*30)
print("\n".join(plays))

#game.advance(4)
#game.advance(8)
#game.advance(2)
#print(game.render())
#
#s = mcts.Searcher(game)
#print(s.find())

