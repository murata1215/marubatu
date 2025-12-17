"""Board class for managing the Tic-Tac-Toe game state."""


class Board:
    """Manages the 3x3 Tic-Tac-Toe board state."""
    
    EMPTY = ""
    PLAYER_X = "X"
    PLAYER_O = "O"
    
    def __init__(self):
        """Initialize an empty 3x3 board."""
        self.cells: list[str] = [self.EMPTY] * 9
    
    def reset(self) -> None:
        """Reset the board to empty state."""
        self.cells = [self.EMPTY] * 9
    
    def get_cell(self, index: int) -> str:
        """Get the value at a specific cell index (0-8)."""
        if 0 <= index < 9:
            return self.cells[index]
        return self.EMPTY
    
    def set_cell(self, index: int, player: str) -> bool:
        """
        Set a cell to a player's mark.
        
        Args:
            index: Cell index (0-8)
            player: Player mark (X or O)
            
        Returns:
            True if successful, False if cell is occupied or invalid
        """
        if 0 <= index < 9 and self.cells[index] == self.EMPTY:
            self.cells[index] = player
            return True
        return False
    
    def get_empty_cells(self) -> list[int]:
        """Get list of empty cell indices."""
        return [i for i, cell in enumerate(self.cells) if cell == self.EMPTY]
    
    def is_full(self) -> bool:
        """Check if the board is completely filled."""
        return self.EMPTY not in self.cells
    
    def get_board_state(self) -> list[str]:
        """Get a copy of the current board state."""
        return self.cells.copy()
    
    def get_cell_position(self, index: int) -> tuple[int, int]:
        """Convert cell index to (row, col) position."""
        return (index // 3, index % 3)
    
    def get_cell_index(self, row: int, col: int) -> int:
        """Convert (row, col) position to cell index."""
        return row * 3 + col
