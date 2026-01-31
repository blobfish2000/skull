from random import choice
from copy import deepcopy as copy
import math
import jsonpickle
import json

EXPLORE = math.sqrt(2)
BIG = 9999999

class Node:
    def __init__(self, move: int | None, parent, to_play: int):
        self.move = move #the move played to get here.
        self.parent = parent
        self.children = []
        self.to_play = to_play
        self.total_wins = 0.0 #wins from the move; the PARENT's to_play determines the arity
        self.visits = 0.0
        self.vis_string = ""
        if self.parent:
            self.parent.children.append(self)

    def score(self) -> float:
        if self.visits == 0:
            return BIG
        if self.parent.visits == 0:
            return -BIG
        average_wins = self.total_wins / self.visits
        return average_wins + EXPLORE * math.sqrt(math.log(self.parent.visits) / self.visits)

class Searcher:
    def __init__(self, state):
        self.root_state = copy(state)
        self.state = copy(self.root_state)

        self.root_node = Node(move = None, parent = None, to_play = self.state.to_play)
        self.node = self.root_node

        self.vis_dict = {"":[self.root_node]}


    def select(self):
        self.node = self.root_node
        self.state = copy(self.root_state)
        while len(self.node.children) > 0:
            scores = [n.score() for n in self.node.children]
            max_i = scores.index(max(scores))
            self.node = self.node.children[max_i]
            self.state.advance(self.node.move)

    def expand(self):
        moves = self.state.valid_plays()
        if len(moves) == 0:
            return
        for move in moves:
            parent_to_play = self.state.to_play
            state = copy(self.state)
            state.advance(move)
            vis_string = state.visible_str(parent_to_play)
            new_node = Node(move = move, parent = self.node, to_play = state.to_play)
            new_node.vis_string = vis_string
            if vis_string not in self.vis_dict.keys():
                self.vis_dict[vis_string] = []
            self.vis_dict[vis_string].append(new_node)
        next_node = choice(self.node.children)
        move = next_node.move
        self.state.advance(move)
        self.node = next_node

    def simulate_backprop(self):
        while self.state.winner < -1:
            moves = self.state.valid_plays()
            move = choice(moves)
            self.state.advance(move)

        winner = self.state.winner

        while self.node.parent:

            shared_pool = self.vis_dict[self.node.vis_string]

            for s_node in shared_pool:
                parent_play = s_node.parent.to_play
                if parent_play == winner:
                    s_node.total_wins += 1
                if winner == -1:
                    s_node.total_wins += 0.5
                s_node.visits += 1
            self.node = self.node.parent
        self.node.visits += 1

    def run(self):
        self.select()
        self.expand()
        self.simulate_backprop()

    def best_move(self):
        if len(self.root_node.children) == 0:
            return None

        visits = [n.visits for n in self.root_node.children]
        wins = [n.total_wins for n in self.root_node.children]
        v_i = visits.index(max(visits))
        return self.root_node.children[v_i].move

    def find(self, n = 1000):
        print("running search...")
        for _ in range(n):
            self.run()
            #input()
            #print(json.dumps(json.loads(jsonpickle.encode(self.root_node)), indent = 4))

        return self.best_move()
