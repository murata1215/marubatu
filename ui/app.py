"""Tkinter GUI application for Tic-Tac-Toe."""

import tkinter as tk
from tkinter import ttk
import random
import json
import os
import threading
import re
from datetime import datetime
from typing import Optional

from game import Board, Judge, CPU


class TicTacToeApp:
    """Main GUI application for Tic-Tac-Toe game."""
    
    HUMAN = "Human"
    CPU_PLAYER = "CPU"
    
    def __init__(self, root: tk.Tk):
        """Initialize the application."""
        self.root = root
        self.root.title("Tic-Tac-Toe (〇×ゲーム)")
        self.root.resizable(False, False)
        
        self.board = Board()
        self.cpu: Optional[CPU] = None
        self.game_active = False
        self.human_mark = ""
        self.cpu_mark = ""
        self.current_player = ""
        self.first_player = ""
        self.moves: list[dict] = []
        self.game_start_time: Optional[datetime] = None
        self.session_start_time = datetime.now()
        self.session_log_file = self._create_session_log_file()
        self.game_history: list[dict] = []
        self.game_id = 0
        
        self._setup_ui()
        self._disable_board()
        self._update_status("「開始」ボタンを押してゲームを始めてください")
    
    def _create_session_log_file(self) -> str:
        """Create session log file path."""
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logs_dir = os.path.join(script_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        timestamp = self.session_start_time.strftime("%Y%m%d_%H%M%S")
        return os.path.join(logs_dir, f"session_{timestamp}.jsonl")
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, padx=(0, 10))
        
        self.status_label = ttk.Label(
            left_frame, 
            text="", 
            font=("Arial", 12),
            wraplength=250
        )
        self.status_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        self.buttons: list[tk.Button] = []
        for i in range(9):
            row, col = i // 3, i % 3
            btn = tk.Button(
                left_frame,
                text="",
                font=("Arial", 24, "bold"),
                width=4,
                height=2,
                command=lambda idx=i: self._on_cell_click(idx)
            )
            btn.grid(row=row + 1, column=col, padx=2, pady=2)
            self.buttons.append(btn)
        
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        self.start_button = ttk.Button(
            button_frame,
            text="開始",
            command=self._start_game
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = ttk.Button(
            button_frame,
            text="リセット",
            command=self._reset_game,
            state=tk.DISABLED
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        right_frame = ttk.LabelFrame(main_frame, text="履歴", padding="5")
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        self.history_text = tk.Text(
            right_frame,
            width=30,
            height=20,
            font=("Arial", 9),
            state=tk.DISABLED
        )
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(right_frame, command=self.history_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text.config(yscrollcommand=scrollbar.set)
    
    def _update_status(self, message: str) -> None:
        """Update the status label."""
        self.status_label.config(text=message)
    
    def _disable_board(self) -> None:
        """Disable all board buttons."""
        for btn in self.buttons:
            btn.config(state=tk.DISABLED)
    
    def _start_game(self) -> None:
        """Start a new game."""
        self.board.reset()
        self.moves = []
        self.game_start_time = datetime.now()
        self.game_id += 1
        
        for btn in self.buttons:
            btn.config(text="", state=tk.NORMAL, bg="SystemButtonFace")
        
        if random.choice([True, False]):
            self.first_player = self.HUMAN
            self.human_mark = Board.PLAYER_X
            self.cpu_mark = Board.PLAYER_O
            self.current_player = self.HUMAN
            self._update_status(f"あなたが先手（{self.human_mark}）です。マスをクリックしてください")
        else:
            self.first_player = self.CPU_PLAYER
            self.cpu_mark = Board.PLAYER_X
            self.human_mark = Board.PLAYER_O
            self.current_player = self.CPU_PLAYER
            self._update_status(f"CPUが先手（{self.cpu_mark}）です")
        
        use_openai = self._check_openai_available()
        self.cpu = CPU(self.cpu_mark, self.human_mark, use_openai=use_openai)
        
        self.game_active = True
        self.start_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.NORMAL)
        
        if self.current_player == self.CPU_PLAYER:
            self.root.after(500, self._cpu_move)
    
    def _check_openai_available(self) -> bool:
        """Check if OpenAI API is available."""
        try:
            from dotenv import load_dotenv
            load_dotenv()
            return bool(os.getenv("OPENAI_API_KEY"))
        except ImportError:
            return False
    
    def _reset_game(self) -> None:
        """Reset the game to initial state."""
        self.game_active = False
        self.board.reset()
        self.moves = []
        
        for btn in self.buttons:
            btn.config(text="", state=tk.DISABLED, bg="SystemButtonFace")
        
        self.start_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.DISABLED)
        self._update_status("「開始」ボタンを押してゲームを始めてください")
    
    def _on_cell_click(self, index: int) -> None:
        """Handle cell button click."""
        if not self.game_active or self.current_player != self.HUMAN:
            return
        
        if self.board.set_cell(index, self.human_mark):
            self.buttons[index].config(text=self.human_mark)
            self.moves.append({
                "player": self.HUMAN,
                "mark": self.human_mark,
                "position": index
            })
            
            if self._check_game_end():
                return
            
            self.current_player = self.CPU_PLAYER
            self._update_status("CPUが考えています...")
            self.root.after(500, self._cpu_move)
    
    def _cpu_move(self) -> None:
        """Execute CPU's move."""
        if not self.game_active:
            return
        
        try:
            move = self.cpu.get_move(self.board)
        except Exception as e:
            self._update_status(f"CPUエラー: {e}\nリセットしてください")
            self.game_active = False
            self._disable_board()
            self.start_button.config(state=tk.NORMAL)
            return
        
        self.board.set_cell(move, self.cpu_mark)
        self.buttons[move].config(text=self.cpu_mark)
        self.moves.append({
            "player": self.CPU_PLAYER,
            "mark": self.cpu_mark,
            "position": move
        })
        
        if self._check_game_end():
            return
        
        self.current_player = self.HUMAN
        self._update_status(f"あなたの番（{self.human_mark}）です。マスをクリックしてください")
    
    def _check_game_end(self) -> bool:
        """Check if the game has ended and handle accordingly."""
        winner = Judge.check_winner(self.board)
        
        if winner:
            self._end_game(winner)
            return True
        
        if Judge.check_draw(self.board):
            self._end_game(None)
            return True
        
        return False
    
    def _end_game(self, winner_mark: Optional[str]) -> None:
        """Handle game end."""
        self.game_active = False
        
        for btn in self.buttons:
            btn.config(state=tk.DISABLED)
        
        winning_line = Judge.get_winning_line(self.board)
        if winning_line:
            for idx in winning_line:
                self.buttons[idx].config(bg="lightgreen")
        
        if winner_mark is None:
            result = "Draw"
            message = "引き分けです！"
        elif winner_mark == self.human_mark:
            result = self.HUMAN
            message = "あなたの勝ちです！おめでとうございます！"
        else:
            result = self.CPU_PLAYER
            message = "CPUの勝ちです。次は頑張りましょう！"
        
        self._update_status(message)
        
        self._save_game_log(result)
        
        self.start_button.config(state=tk.NORMAL)
        
        current_game_id = self.game_id
        moves_copy = self.moves.copy()
        
        def fetch_reflection():
            reflection = CPU.get_game_reflection(moves_copy, result)
            if reflection and self.game_id == current_game_id:
                self.root.after(0, lambda: self._update_status(f"{message}\n\n{reflection}"))
        
        thread = threading.Thread(target=fetch_reflection, daemon=True)
        thread.start()
    
    def _save_game_log(self, winner: str) -> None:
        """Save game log to file."""
        game_record = {
            "start_time": self.game_start_time.isoformat() if self.game_start_time else None,
            "end_time": datetime.now().isoformat(),
            "first_player": self.first_player,
            "human_mark": self.human_mark,
            "cpu_mark": self.cpu_mark,
            "moves": self.moves,
            "winner": winner
        }
        
        try:
            with open(self.session_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(game_record, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Failed to save game log: {e}")
        
        self.game_history.append(game_record)
        self._update_history_display()
    
    def _get_japanese_result(self, winner: str) -> str:
        """Convert winner string to Japanese display text."""
        if winner == "Draw":
            return "引き分け"
        elif winner == self.HUMAN:
            return "あなたの勝ち"
        elif winner == self.CPU_PLAYER:
            return "CPUの勝ち"
        return winner
    
    def _get_japanese_first_player(self, first_player: str) -> str:
        """Convert first player string to Japanese display text."""
        if first_player == self.HUMAN:
            return "あなた"
        elif first_player == self.CPU_PLAYER:
            return "CPU"
        return first_player
    
    def _update_history_display(self) -> None:
        """Update the history text display."""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        
        for i, game in enumerate(reversed(self.game_history[-10:]), 1):
            game_num = len(self.game_history) - i + 1
            first = "先手: " + self._get_japanese_first_player(game["first_player"])
            result = "結果: " + self._get_japanese_result(game["winner"])
            moves_count = f"手数: {len(game['moves'])}"
            
            self.history_text.insert(tk.END, f"--- ゲーム {game_num} ---\n")
            self.history_text.insert(tk.END, f"{first}\n")
            self.history_text.insert(tk.END, f"{result}\n")
            self.history_text.insert(tk.END, f"{moves_count}\n\n")
        
        self.history_text.config(state=tk.DISABLED)
    
    def run(self) -> None:
        """Run the application main loop."""
        self.root.mainloop()
