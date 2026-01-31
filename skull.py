from random import randint, choice
import os
from time import sleep
import mcts

class SkullState:
    def __init__(self, players = 2, starting_cards = 4):
        self.to_play = 0
        self.players = players
        self.player_cards = [starting_cards for _ in range(players)]
        self.player_base_hand = [starting_cards for _ in range(players)]
        self.has_skull = [True for _ in range(players)]
        self.plays = [[] for _ in range(players)] # -1 = flower, -2 = skull
        self.bids = [0 for _ in range(players)]
        self.phase = 0 # 0: playing, 1: bidding, 2: flipping
        self.flips = [False for _ in range(players)]
        self.winner = -2

    def visible_str(self, player):
        s = ""
        s += str(self.to_play)
        s += str(self.players)
        s += str(self.player_cards)
        s += str(self.player_base_hand)
        s += str(self.has_skull[player])
        s += str([len(p) for p in self.plays])
        s += str(self.plays[player])
        s += str(self.bids)
        s += str(self.phase)
        s += str(self.flips)
        s += str(self.winner)
        return s

    def valid_plays(self) -> list[int]:
        """
        -2: Skull
        -1: Flower
        0 : Pass
        1+: Bid N
        0+: Flip Nth players top card
        """
        player = self.to_play
        plays = []
        # If there's a winner
        if self.winner != -2:
            # We can't play
            return []
        # If we're out
        if self.player_base_hand[player] == 0:
            # We must pass
            return [0]
        # If we're in the playing phase
        if self.phase == 0:
            #If we've played a card
            if len(self.plays[player]) > 0:
                #We can bid anything up to the number of cards
                num_cards_played = sum([len(plays) for plays in self.plays])
                plays = list(range(1, num_cards_played+1))

            #if we have any cards
            if self.player_cards[player] > 0:
                #if we still have our skull and haven't played it
                if self.has_skull[player] and -2 not in self.plays[player]:
                    #we can play our skull
                    plays.append(-2)
                    #if we have more cards
                    if len(self.player_cards) > 1:
                        #we can also play a flower
                        plays.append(-1)

                #if we only have a flower
                else:
                    #we can play a flower
                    plays.append(-1)

        # If we're in the bidding phase
        elif self.phase == 1:
            #we can always pass
            plays = [0]

            current_bid = max(self.bids)
            num_cards_played = sum([len(plays) for plays in self.plays])
            #if the big isn't maxed
            if current_bid < num_cards_played:
                #we can bid at anything above current bid up to the number of cards
                plays = [0] + list(range(current_bid + 1, num_cards_played+1))

        # If we're flipping
        elif self.phase == 2:
            # If we have any cards on our stack
            if len(self.plays[player]) > 0:
                # We have to flip our own
                plays = [player]
            else:
                # Otherwise we can flip any player who has cards unflipped
                plays = [player for player,plays in enumerate(self.plays) if len(plays) > 0]

        return plays

    def render(self) -> str:
        out_string = ""
        for p in range(self.players):
            ps  = " Player " + str(p) + " - "
            if self.flips[p]:
                ps  = " PLAYER " + str(p) + " - "
            if self.to_play == p:
                ps = "*" + ps[1:]
            if self.phase == 0:
                ps += "Hand: " + str(self.player_cards[p]) + "/" + str(self.player_base_hand[p]) + " "
                ps += "| Played: " + str(len(self.plays[p]))
            if self.phase == 1:
                ps += "Hand: " + str(self.player_cards[p]) + "/" + str(self.player_base_hand[p]) + " "
                ps += "| Played: " + str(len(self.plays[p])) + " "
                ps += "| Bid: " + str(self.bids[p])
            if self.phase == 2:
                ps += "Hand: " + str(self.player_cards[p]) + "/" + str(self.player_base_hand[p]) + " "
                if -2 in self.plays[p]:
                    ps += "|*Down: " + str(len(self.plays[p])) + " "
                else:
                    ps += "| Down: " + str(len(self.plays[p])) + " "
                if self.to_play == p:
                    ps += "| Bid: " + str(self.bids[p])
            ps += "\n"
            out_string += ps
        return out_string

    def _next_player(self) -> int:
        return (self.to_play + 1) % self.players

    def _reset(self) -> None:
        #reset the board
        self.player_cards = self.player_base_hand[:]
        self.plays = [[] for _ in range(self.players)] # -1 = flower, -2 = skull
        self.bids = [0 for _ in range(self.players)]
        self.phase = 0 # 0: playing, 1: bidding, 2: flipping

    def advance(self, play) -> None:
        player = self.to_play
        #if we're in the playing phase
        if self.phase == 0:
            #and we play a card
            if play < 0:
                #play the card
                self.plays[player].append(play)
                #decrement hand
                self.player_cards[player] -= 1
                #advance play
                self.to_play = self._next_player()
                return f"Player {player} plays {'Skull' if play == -2 else 'Flower'}"
            #if we start bidding
            else:
                #log the bid
                self.bids[player] = play
                #change the phase
                self.phase = 1
                #advance play
                self.to_play = self._next_player()
                return f"Player {player} bids {play}"
             
        #if we're bidding
        elif self.phase == 1:
            #if we bid
            if play > 0:
                #log the bid
                self.bids[player] = play
                #advance play
                self.to_play = self._next_player()
                return f"Player {player} bids {play}"
            #if we pass
            else:
                #advance play
                self.to_play = self._next_player()
                #if the next player has the max bid
                if self.bids[self.to_play] == max(self.bids):
                    #advance phase
                    self.phase = 2
                return f"Player {player} passes"
        #if we're flipping
        elif self.phase == 2:
            #reveal the top card from the playth player
            card = self.plays[play].pop()
            #if it's a skull
            if card == -2:
                #see if we lose our skull
                if randint(1,self.player_base_hand[player]) == 1:
                    self.has_skull[player] = False
                #lose a card
                self.player_base_hand[player] -= 1
                #if we have no cards
                if self.player_base_hand[player] == 0:
                    still_in = [p for p, h in enumerate(self.player_base_hand) if h > 0]
                    if len(still_in) == 1:
                        self.winner = still_in[0]
                        return f"Player {self.winner} wins by exhaustion"
                #reset
                self._reset()
                #and stay on the play
                return f"Player {player} flips a skull and loses a card, skull: {self.has_skull[player]}"
            #if it's a flower
            #decrement our bid
            self.bids[player] -= 1
            #if we've exhausted our bid (won)
            if self.bids[player] == 0:
                #if we've flipped
                if self.flips[player]:
                    #win
                    self.winner = player
                    return f"Player {player} meets their bid and has won!"
                #otherwise
                else:
                    #flip
                    self.flips[player] = True
                    #and reset the board
                    self._reset()
                    #keeping us on play
                    return f"Player {player} meets their bid and has gotten a point!"
            #otherwise
            else:
                #continue with us in play
                return f"Player {player} flips {play}'s card and continues"


game = SkullState(starting_cards=2)

game.advance(-1)
game.advance(-1)

game.flips = [True, True]
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
        play = s.find(10000)
        #print("Valid plays: " + ", ".join([str(x) for x in valid]))
        #while play not in valid:
        #    play = int(input("Play? "))
        #print() 
    else:
        s = mcts.Searcher(game)
        play = s.find(10000)
    plays.append(game.advance(play))

os.system("clear")
print(game.render())
print("-"*30)
print("\n".join(plays))

