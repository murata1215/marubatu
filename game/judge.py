"""Judge class for determining game outcomes."""

from typing import Optional
from .board import Board


class Judge:
    """Handles win/draw detection for Tic-Tac-Toe."""
    
    WIN_PATTERNS = [
        [0, 1, 2],  # Top row
        [3, 4, 5],  # Middle row
        [6, 7, 8],  # Bottom row
        [0, 3, 6],  # Left column
        [1, 4, 7],  # Middle column
        [2, 5, 8],  # Right column
        [0, 4, 8],  # Diagonal top-left to bottom-right
        [2, 4, 6],  # Diagonal top-right to bottom-left
    ]
    
    @classmethod
    def get_winning_line(cls, board: Board) -> Optional[list[int]]:
        """
        Get the winning line indices if there's a winner.
        
        Args:
            board: The game board
            
        Returns:
            List of 3 cell indices forming the winning line, or None
        """
        cells = board.get_board_state()
        
        for pattern in cls.WIN_PATTERNS:
            a, b, c = pattern
            if cells[a] != Board.EMPTY and cells[a] == cells[b] == cells[c]:
                return pattern
        
        return None
    
    @classmethod
    def check_winner(cls, board: Board) -> Optional[str]:
        """
        Check if there's a winner.
        
        Args:
            board: The game board
            
        Returns:
            The winning player's mark (X or O), or None if no winner
        """
        winning_line = cls.get_winning_line(board)
        if winning_line:
            return board.get_cell(winning_line[0])
        return None
    
    @classmethod
    def check_draw(cls, board: Board) -> bool:
        """
        Check if the game is a draw.
        
        Args:
            board: The game board
            
        Returns:
            True if draw (board full and no winner), False otherwise
        """
        return board.is_full() and cls.get_winning_line(board) is None
    
    @classmethod
    def is_game_over(cls, board: Board) -> bool:
        """
        Check if the game has ended.
        
        Args:
            board: The game board
            
        Returns:
            True if game is over (winner or draw), False otherwise
        """
        return cls.get_winning_line(board) is not None or board.is_full()
