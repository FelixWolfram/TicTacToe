class Computer:
    def __init__(self, check_for_winner_func):
        self.check_for_winner_func = check_for_winner_func
        

    # player1 ("X") is max, player2 ("O") is min
    def computer_move(self, board, player1):
        results = []
        for i in range(3):
            for j in range(3):
                if board[i][j] == '':
                    board[i][j] = ('X' if player1 else "O")
                    winner, _ = self.check_for_winner_func(board)
                    if winner is not None:
                        board[i][j] = ''
                        return winner, (i, j)   # computer wins
                    result, (_, _) = self.computer_move(board, not player1)
                    results.append((result, (i, j)))
                    board[i][j] = ''
        if not results:
            return 0, (None, None)  # draw
        return max(results) if player1 else min(results)