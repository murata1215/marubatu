"""
〇×ゲーム GUIアプリケーション

tkinterを使用した〇×ゲーム（Tic-Tac-Toe）のGUIアプリケーションです。
人間 vs CPU の対戦が可能で、ゲーム履歴の保存・表示機能も備えています。
"""

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
    """
    〇×ゲームのメインGUIアプリケーションクラス
    
    tkinterを使用してゲームUIを構築し、ゲームの進行を管理します。
    """
    
    # プレイヤー識別用の定数
    HUMAN = "Human"
    CPU_PLAYER = "CPU"
    
    def __init__(self, root: tk.Tk):
        """
        アプリケーションを初期化する
        
        Args:
            root: tkinterのルートウィンドウ
        """
        self.root = root
        self.root.title("Tic-Tac-Toe (〇×ゲーム)")
        self.root.resizable(False, False)
        
        # ゲーム状態の初期化
        self.board = Board()                    # ゲーム盤面
        self.cpu: Optional[CPU] = None          # CPUプレイヤー
        self.game_active = False                # ゲーム進行中フラグ
        self.human_mark = ""                    # 人間のマーク（X or O）
        self.cpu_mark = ""                      # CPUのマーク（X or O）
        self.current_player = ""                # 現在の手番
        self.first_player = ""                  # 先手プレイヤー
        self.moves: list[dict] = []             # 現在のゲームの手順記録
        self.game_start_time: Optional[datetime] = None  # ゲーム開始時刻
        self.session_start_time = datetime.now()         # セッション開始時刻
        self.session_log_file = self._create_session_log_file()  # ログファイルパス
        self.game_history: list[dict] = []      # セッション内のゲーム履歴
        self.game_id = 0                        # ゲームID（OpenAI反省コメントの競合防止用）
        
        # UIの構築と初期状態の設定
        self._setup_ui()
        self._disable_board()
        self._update_status("「開始」ボタンを押してゲームを始めてください")
    
    def _create_session_log_file(self) -> str:
        """
        セッションログファイルのパスを作成する
        
        logs/session_YYYYMMDD_HHMMSS.jsonl 形式のファイルパスを生成します。
        logsディレクトリが存在しない場合は作成します。
        
        Returns:
            ログファイルの絶対パス
        """
        # スクリプトの親ディレクトリを基準にlogsディレクトリを作成
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logs_dir = os.path.join(script_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        # タイムスタンプ付きのファイル名を生成
        timestamp = self.session_start_time.strftime("%Y%m%d_%H%M%S")
        return os.path.join(logs_dir, f"session_{timestamp}.jsonl")
    
    def _setup_ui(self) -> None:
        """
        ユーザーインターフェースを構築する
        
        左側にゲーム盤面と操作ボタン、右側に履歴表示エリアを配置します。
        """
        # メインフレーム（全体のコンテナ）
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # 左側フレーム（ゲーム盤面と操作ボタン）
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, padx=(0, 10))
        
        # ステータス表示ラベル（ゲームの状態やメッセージを表示）
        self.status_label = ttk.Label(
            left_frame, 
            text="", 
            font=("Arial", 12),
            wraplength=250
        )
        self.status_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # 3x3のゲーム盤面ボタンを作成
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
        
        # 操作ボタンフレーム（開始・リセットボタン）
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        # 開始ボタン
        self.start_button = ttk.Button(
            button_frame,
            text="開始",
            command=self._start_game
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # リセットボタン（初期状態では無効）
        self.reset_button = ttk.Button(
            button_frame,
            text="リセット",
            command=self._reset_game,
            state=tk.DISABLED
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # 右側フレーム（履歴表示エリア）
        right_frame = ttk.LabelFrame(main_frame, text="履歴", padding="5")
        right_frame.grid(row=0, column=1, sticky="nsew")
        
        # 履歴表示用テキストエリア（読み取り専用）
        self.history_text = tk.Text(
            right_frame,
            width=30,
            height=20,
            font=("Arial", 9),
            state=tk.DISABLED
        )
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(right_frame, command=self.history_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_text.config(yscrollcommand=scrollbar.set)
    
    def _update_status(self, message: str) -> None:
        """
        ステータスラベルを更新する
        
        Args:
            message: 表示するメッセージ
        """
        self.status_label.config(text=message)
    
    def _disable_board(self) -> None:
        """
        全てのボードボタンを無効化する
        
        ゲーム開始前やゲーム終了後に呼び出されます。
        """
        for btn in self.buttons:
            btn.config(state=tk.DISABLED)
    
    def _start_game(self) -> None:
        """
        新しいゲームを開始する
        
        盤面をリセットし、先手をランダムに決定してゲームを開始します。
        CPUが先手の場合は、500ms後にCPUの手を実行します。
        """
        # 盤面と手順記録をリセット
        self.board.reset()
        self.moves = []
        self.game_start_time = datetime.now()
        self.game_id += 1  # ゲームIDをインクリメント（OpenAI反省コメントの競合防止用）
        
        # 全てのボタンを有効化してテキストをクリア
        for btn in self.buttons:
            btn.config(text="", state=tk.NORMAL, bg="SystemButtonFace")
        
        # 先手をランダムに決定
        if random.choice([True, False]):
            # 人間が先手の場合
            self.first_player = self.HUMAN
            self.human_mark = Board.PLAYER_X
            self.cpu_mark = Board.PLAYER_O
            self.current_player = self.HUMAN
            self._update_status(f"あなたが先手（{self.human_mark}）です。マスをクリックしてください")
        else:
            # CPUが先手の場合
            self.first_player = self.CPU_PLAYER
            self.cpu_mark = Board.PLAYER_X
            self.human_mark = Board.PLAYER_O
            self.current_player = self.CPU_PLAYER
            self._update_status(f"CPUが先手（{self.cpu_mark}）です")
        
        # CPUプレイヤーを初期化（OpenAI使用可否をチェック）
        use_openai = self._check_openai_available()
        self.cpu = CPU(self.cpu_mark, self.human_mark, use_openai=use_openai)
        
        # ゲーム状態を更新
        self.game_active = True
        self.start_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.NORMAL)
        
        # CPUが先手の場合は500ms後にCPUの手を実行
        if self.current_player == self.CPU_PLAYER:
            self.root.after(500, self._cpu_move)
    
    def _check_openai_available(self) -> bool:
        """
        OpenAI APIが利用可能かどうかを確認する
        
        .envファイルにOPENAI_API_KEYが設定されているかをチェックします。
        
        Returns:
            APIキーが設定されていればTrue、そうでなければFalse
        """
        try:
            from dotenv import load_dotenv
            load_dotenv()
            return bool(os.getenv("OPENAI_API_KEY"))
        except ImportError:
            return False
    
    def _reset_game(self) -> None:
        """
        ゲームを初期状態にリセットする
        
        盤面をクリアし、ボタンを無効化して開始待ち状態に戻します。
        """
        self.game_active = False
        self.board.reset()
        self.moves = []
        
        # 全てのボタンを無効化してテキストをクリア
        for btn in self.buttons:
            btn.config(text="", state=tk.DISABLED, bg="SystemButtonFace")
        
        # ボタン状態を更新
        self.start_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.DISABLED)
        self._update_status("「開始」ボタンを押してゲームを始めてください")
    
    def _on_cell_click(self, index: int) -> None:
        """
        マスがクリックされた時の処理
        
        人間の手番でゲームが進行中の場合のみ、マスにマークを配置します。
        配置後、ゲーム終了判定を行い、終了していなければCPUの手番に移ります。
        
        Args:
            index: クリックされたマスのインデックス（0-8）
        """
        # ゲームが進行中でない、または人間の手番でない場合は何もしない
        if not self.game_active or self.current_player != self.HUMAN:
            return
        
        # マスにマークを配置（既に埋まっている場合は失敗）
        if self.board.set_cell(index, self.human_mark):
            self.buttons[index].config(text=self.human_mark)
            # 手順を記録
            self.moves.append({
                "player": self.HUMAN,
                "mark": self.human_mark,
                "position": index
            })
            
            # ゲーム終了判定
            if self._check_game_end():
                return
            
            # CPUの手番に移行
            self.current_player = self.CPU_PLAYER
            self._update_status("CPUが考えています...")
            self.root.after(500, self._cpu_move)
    
    def _cpu_move(self) -> None:
        """
        CPUの手を実行する
        
        CPUのAIロジックで次の手を決定し、盤面に配置します。
        エラーが発生した場合はゲームを停止してエラーメッセージを表示します。
        """
        if not self.game_active:
            return
        
        # CPUの手を取得（エラー時はゲームを停止）
        try:
            move = self.cpu.get_move(self.board)
        except Exception as e:
            self._update_status(f"CPUエラー: {e}\nリセットしてください")
            self.game_active = False
            self._disable_board()
            self.start_button.config(state=tk.NORMAL)
            return
        
        # マスにマークを配置
        self.board.set_cell(move, self.cpu_mark)
        self.buttons[move].config(text=self.cpu_mark)
        # 手順を記録
        self.moves.append({
            "player": self.CPU_PLAYER,
            "mark": self.cpu_mark,
            "position": move
        })
        
        # ゲーム終了判定
        if self._check_game_end():
            return
        
        # 人間の手番に移行
        self.current_player = self.HUMAN
        self._update_status(f"あなたの番（{self.human_mark}）です。マスをクリックしてください")
    
    def _check_game_end(self) -> bool:
        """
        ゲーム終了判定を行う
        
        勝者がいるか、引き分けかをチェックし、終了していれば終了処理を呼び出します。
        
        Returns:
            ゲームが終了していればTrue、続行中ならFalse
        """
        winner = Judge.check_winner(self.board)
        
        # 勝者がいる場合
        if winner:
            self._end_game(winner)
            return True
        
        # 引き分けの場合
        if Judge.check_draw(self.board):
            self._end_game(None)
            return True
        
        return False
    
    def _end_game(self, winner_mark: Optional[str]) -> None:
        """
        ゲーム終了処理を行う
        
        勝利ラインのハイライト、結果メッセージの表示、ログの保存、
        OpenAIによる反省コメントの取得（バックグラウンド）を行います。
        
        Args:
            winner_mark: 勝者のマーク（"X" または "O"）、引き分けの場合はNone
        """
        self.game_active = False
        
        # 全てのボタンを無効化
        for btn in self.buttons:
            btn.config(state=tk.DISABLED)
        
        # 勝利ラインがあればハイライト表示
        winning_line = Judge.get_winning_line(self.board)
        if winning_line:
            for idx in winning_line:
                self.buttons[idx].config(bg="lightgreen")
        
        # 結果に応じたメッセージを設定
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
        
        # ゲームログを保存
        self._save_game_log(result)
        
        # 開始ボタンを有効化（次のゲームを開始可能に）
        self.start_button.config(state=tk.NORMAL)
        
        # OpenAI反省コメントをバックグラウンドで取得
        # game_idを使用して、新しいゲームが始まった場合は古い反省コメントを無視
        current_game_id = self.game_id
        moves_copy = self.moves.copy()
        
        def fetch_reflection():
            """バックグラウンドでOpenAI反省コメントを取得する"""
            reflection = CPU.get_game_reflection(moves_copy, result)
            # 同じゲームIDの場合のみ反省コメントを表示（競合防止）
            if reflection and self.game_id == current_game_id:
                self.root.after(0, lambda: self._update_status(f"{message}\n\n{reflection}"))
        
        # デーモンスレッドとして実行（アプリ終了時に自動終了）
        thread = threading.Thread(target=fetch_reflection, daemon=True)
        thread.start()
    
    def _save_game_log(self, winner: str) -> None:
        """
        ゲームログをファイルに保存する
        
        JSONL形式（1行1ゲーム）でログファイルに追記します。
        
        Args:
            winner: 勝者（"Human", "CPU", または "Draw"）
        """
        # ゲーム記録を作成
        game_record = {
            "start_time": self.game_start_time.isoformat() if self.game_start_time else None,
            "end_time": datetime.now().isoformat(),
            "first_player": self.first_player,
            "human_mark": self.human_mark,
            "cpu_mark": self.cpu_mark,
            "moves": self.moves,
            "winner": winner
        }
        
        # ファイルに追記
        try:
            with open(self.session_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(game_record, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"ログ保存エラー: {e}")
        
        # 履歴に追加して表示を更新
        self.game_history.append(game_record)
        self._update_history_display()
    
    def _get_japanese_result(self, winner: str) -> str:
        """
        勝者文字列を日本語表示用テキストに変換する
        
        Args:
            winner: 勝者（"Human", "CPU", または "Draw"）
            
        Returns:
            日本語の結果テキスト
        """
        if winner == "Draw":
            return "引き分け"
        elif winner == self.HUMAN:
            return "あなたの勝ち"
        elif winner == self.CPU_PLAYER:
            return "CPUの勝ち"
        return winner
    
    def _get_japanese_first_player(self, first_player: str) -> str:
        """
        先手プレイヤー文字列を日本語表示用テキストに変換する
        
        Args:
            first_player: 先手プレイヤー（"Human" または "CPU"）
            
        Returns:
            日本語の先手プレイヤーテキスト
        """
        if first_player == self.HUMAN:
            return "あなた"
        elif first_player == self.CPU_PLAYER:
            return "CPU"
        return first_player
    
    def _update_history_display(self) -> None:
        """
        履歴表示エリアを更新する
        
        直近10ゲームの履歴を新しい順に表示します。
        """
        # テキストエリアを編集可能にしてクリア
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        
        # 直近10ゲームを新しい順に表示
        for i, game in enumerate(reversed(self.game_history[-10:]), 1):
            game_num = len(self.game_history) - i + 1
            first = "先手: " + self._get_japanese_first_player(game["first_player"])
            result = "結果: " + self._get_japanese_result(game["winner"])
            moves_count = f"手数: {len(game['moves'])}"
            
            self.history_text.insert(tk.END, f"--- ゲーム {game_num} ---\n")
            self.history_text.insert(tk.END, f"{first}\n")
            self.history_text.insert(tk.END, f"{result}\n")
            self.history_text.insert(tk.END, f"{moves_count}\n\n")
        
        # テキストエリアを読み取り専用に戻す
        self.history_text.config(state=tk.DISABLED)
    
    def run(self) -> None:
        """
        アプリケーションのメインループを開始する
        
        tkinterのイベントループを開始し、ウィンドウを表示します。
        """
        self.root.mainloop()
