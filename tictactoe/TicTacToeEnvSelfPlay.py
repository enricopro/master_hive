import numpy as np

class TicTacToeEnvSelfPlay:
    def __init__(self, num_games=1):
        self.num_games = num_games
        self.board_size = 3
        self.boards = np.zeros((num_games, self.board_size, self.board_size), dtype=int)
        #self.boards = np.random.choice([0, 1, -1], size=(num_games, self.board_size, self.board_size))
        self.current_player = 1  # Player 1 starts

    def reset(self, game_idx=None):
        self.boards[game_idx] = np.zeros((self.board_size, self.board_size), dtype=int)

    def step(self, moves, model):
        rewards_total = []
        rewards1 = []
        rewards2 = []
        for i in range(len(moves)): # for each game
            row = moves[i][0]
            col = moves[i][1]
            if self.boards[i, row, col] != 0:
                raise ValueError("Invalid move")
            self.boards[i, row, col] = self.current_player
            reward1, done = self.check_game_over(i)
            rewards1.append(reward1)
            if done:
                self.reset(i)

        state = self.to_state() * (-1)
        mask = np.zeros(state.shape) 
        for i in range(len(state)):
            for j in range(len(state[i])):
                if state[i][j] != 0:
                    mask[i][j] = -1000 
        q_values = model.predict(state)
        actions = [[np.argmax(q_values[i] + mask[i])] for i in range(len(mask))]

        actions_adapted = [[action[0] // 3, action[0] % 3] for action in actions]
        for i in range(len(actions_adapted)):
            row = actions_adapted[i][0]
            col = actions_adapted[i][1]
            if self.boards[i, row, col] != 0:
                raise ValueError("Invalid move")
            self.boards[i, row, col] = -self.current_player
            reward2, done = self.check_game_over(i)
            rewards2.append(reward2)
            if done:
                self.reset(i)
        for k in range(len(rewards1)):
            rewards_total.append(rewards1[k] + rewards2[k])
        return rewards_total

    def check_game_over(self, game_idx):
        board = self.boards[game_idx]
        lines = [
            board[0, :], board[1, :], board[2, :],
            board[:, 0], board[:, 1], board[:, 2],
            board.diagonal(), np.fliplr(board).diagonal()
        ]
        player = self.current_player
        for line in lines:
            if np.all(line == player):
                return 1, True  # Current player wins
            if np.all(line == -player):
                return -1, True  # Current player loses
        if np.all(board != 0):
            return 0, True  # Tie game
        return 0, False  # Game continues

    def to_state(self):
        # Returns a flattened version of the board states suitable for NN input
        states = []
        for i in range(self.num_games):
            state = np.array([])
            state = np.concatenate((state, self.boards[i].flatten()))
            states.append(state)
        return np.stack(states)

    def render(self, game_idx):
        board = self.boards[game_idx]
        symbols = {0: ' ', 1: 'X', -1: 'O'}
        for row in board:
            print(' | '.join(symbols[x] for x in row))
            print('-' * 9)

    def get_available_moves(self):
        available_moves = np.zeros((self.boars.shape[0], self.board_size*self.board_size))
        for i in range(self.boards.shape[0]):
            board = self.boards[i].flatten()
            for j in range(len(board)):
                if board[j] == 0:
                    available_moves[i, j] = 1
        return available_moves