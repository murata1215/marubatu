"""CPU AI for Tic-Tac-Toe with rule-based logic and optional OpenAI integration."""

import os
import random
from typing import Optional
from .board import Board
from .judge import Judge


class CPU:
    """CPU player with rule-based AI and optional OpenAI integration."""
    
    CENTER = 4
    CORNERS = [0, 2, 6, 8]
    EDGES = [1, 3, 5, 7]
    
    def __init__(self, mark: str, opponent_mark: str, use_openai: bool = False):
        """
        Initialize CPU player.
        
        Args:
            mark: CPU's mark (X or O)
            opponent_mark: Opponent's mark
            use_openai: Whether to try OpenAI for move suggestions
        """
        self.mark = mark
        self.opponent_mark = opponent_mark
        self.use_openai = use_openai
        self._openai_client = None
        self._openai_available = False
        
        if use_openai:
            self._init_openai()
    
    def _init_openai(self) -> None:
        """Initialize OpenAI client if API key is available."""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=api_key)
                self._openai_available = True
        except ImportError:
            pass
        except Exception:
            pass
    
    def get_move(self, board: Board) -> int:
        """
        Get the best move for CPU.
        
        Args:
            board: Current game board
            
        Returns:
            Cell index for the move
        """
        if self.use_openai and self._openai_available:
            openai_move = self._get_openai_move(board)
            if openai_move is not None:
                return openai_move
        
        return self._get_rule_based_move(board)
    
    def _get_rule_based_move(self, board: Board) -> int:
        """
        Get move using rule-based logic.
        
        Priority:
        1. Win if possible
        2. Block opponent's winning move
        3. Take center
        4. Take corner
        5. Take edge
        """
        empty_cells = board.get_empty_cells()
        
        if not empty_cells:
            raise ValueError("No empty cells available")
        
        winning_move = self._find_winning_move(board, self.mark)
        if winning_move is not None:
            return winning_move
        
        blocking_move = self._find_winning_move(board, self.opponent_mark)
        if blocking_move is not None:
            return blocking_move
        
        if self.CENTER in empty_cells:
            return self.CENTER
        
        available_corners = [c for c in self.CORNERS if c in empty_cells]
        if available_corners:
            return random.choice(available_corners)
        
        available_edges = [e for e in self.EDGES if e in empty_cells]
        if available_edges:
            return random.choice(available_edges)
        
        return random.choice(empty_cells)
    
    def _find_winning_move(self, board: Board, player: str) -> Optional[int]:
        """
        Find a move that would win for the given player.
        
        Args:
            board: Current game board
            player: Player mark to check for
            
        Returns:
            Winning cell index, or None if no winning move
        """
        cells = board.get_board_state()
        
        for pattern in Judge.WIN_PATTERNS:
            values = [cells[i] for i in pattern]
            
            if values.count(player) == 2 and values.count(Board.EMPTY) == 1:
                empty_idx = values.index(Board.EMPTY)
                return pattern[empty_idx]
        
        return None
    
    def _get_openai_move(self, board: Board) -> Optional[int]:
        """
        Get move suggestion from OpenAI.
        
        Args:
            board: Current game board
            
        Returns:
            Suggested cell index, or None if failed
        """
        if not self._openai_client:
            return None
        
        try:
            cells = board.get_board_state()
            board_str = ""
            for i in range(3):
                row = cells[i*3:(i+1)*3]
                row_str = " | ".join(c if c else str(i*3 + j) for j, c in enumerate(row))
                board_str += f"{row_str}\n"
                if i < 2:
                    board_str += "---------\n"
            
            empty_cells = board.get_empty_cells()
            
            prompt = f"""You are playing Tic-Tac-Toe as '{self.mark}'. 
Current board (numbers show empty cell indices):
{board_str}
Available moves: {empty_cells}
Reply with ONLY a single number (the cell index) for your best move."""

            response = self._openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.3
            )
            
            move_str = response.choices[0].message.content.strip()
            move = int(move_str)
            
            if move in empty_cells:
                return move
            
        except Exception:
            pass
        
        return None
    
    @staticmethod
    def get_game_reflection(moves: list[dict], winner: str) -> Optional[str]:
        """
        Get a reflection on the game from OpenAI.
        
        Args:
            moves: List of moves made during the game
            winner: Winner of the game (CPU/Human/Draw)
            
        Returns:
            Reflection text, or None if unavailable
        """
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return None
            
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            moves_str = "\n".join([f"{m['player']}: position {m['position']}" for m in moves])
            
            prompt = f"""A Tic-Tac-Toe game just ended.
Moves:
{moves_str}
Result: {winner}

Give a brief, fun reflection on this game in 1-2 sentences (in Japanese)."""

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception:
            return None
