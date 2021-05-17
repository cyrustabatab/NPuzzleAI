import heapq
import math
from copy import copy




class State:


    def __init__(self,board,distance=0,move=None,predecessor=None):

        self.board = board
        self.move = move
        self.distance = distance
        self.predecessor = predecessor

    
    @property
    def heuristic(self):
        return self.board.heuristic
    

    def __lt__(self,state):

        if isinstance(state,State):

            return self.distance + self.heuristic <= state.distance + state.heuristic

class Board:


    def __init__(self,tiles):

        self.n= int(math.sqrt(len(tiles)))
        self.tiles = tiles 
        self.empty_index = self.tiles.index(None)
        self._calculate_heuristic()
    

    def _manhattan_distance(self,a,b):


        a_row,b_row = a//self.n,b//self.n
        a_col,b_col = a % self.n,b % self.n

        return abs(a_row - b_row) + abs(a_col - b_col)
    def _calculate_heuristic(self):

        

        total = 0
        for i,number in enumerate(self.tiles):
            if number is None:
                continue
            total += self._manhattan_distance(i,number -1)
        self.heuristic = total
    

    def _swap(self,i,j):


        tiles = copy(self.tiles)

        tiles[i],tiles[j] = tiles[j],tiles[i]
        return tiles
    
    def get_successors(self):

        empty = self.empty_index
        
        empty_row,empty_col = empty // self.n,empty % self.n
        successors = []

        if empty_row > 0: #above first row
            successor = Board(self._swap(empty,empty-self.n))
            successors.append((successor,'D'))


        if empty_row < self.n - 1:
            successor = Board(self._swap(empty,empty +self.n))
            successors.append((successor,'U'))


        if empty_col > 0:
            successor = Board(self._swap(empty,empty -1))
            successors.append((successor,'R'))


        if empty_col < self.n - 1:
            successor = Board(self._swap(empty,empty +1))
            successors.append((successor,'L'))



        return successors

    

    def __repr__(self):


        board = ''
    
        tiles_copy = self.tiles.copy()
        tiles_copy[tiles_copy.index(None)] = 0
        for i in range(0,len(self.tiles),self.n):
            board += ' '.join(map(lambda value: f"{value:>2}",tiles_copy[i:i+self.n])) +'\n'


        return board









class NPuzzleSolver:


    def __init__(self,board):

        assert len(board) == len(board[0]),"rows and cols must be equal"
            

        n = len(board)

        self.goal_state = list(range(1,n**2))
        self.goal_state.append(None)

        tiles = []

        for row in board:
            tiles.extend(row)

        print(tiles) 
        self._solve(tiles)


    def _solve(self,tiles):

        start_board = Board(tiles)
        start_state = State(start_board)



        states = []
        heapq.heappush(states,start_state)
        visited = set()

        visited.add(tuple(start_board.tiles))


        print(self.goal_state)
        while states:


            current_state = heapq.heappop(states)
            if current_state.board.tiles == self.goal_state:
                break



            for successor,action in current_state.board.get_successors():
                if tuple(successor.tiles) not in visited:
                    visited.add(tuple(successor.tiles))
                    next_state = State(successor,current_state.distance + 1,action,current_state)
                    heapq.heappush(states,next_state)

        
        print(current_state.distance)
        states = []
        while current_state:
            states.append(current_state)

            current_state = current_state.predecessor
        
        
        while states:
            current_state = states.pop()
            print(current_state.move)
            print(current_state.board)




if __name__ == "__main__":
    

    board = [[10,5,9,6],[7,1,2,11],[15,8,4,12],[14,13,3,None]]


    NPuzzleSolver(board)


