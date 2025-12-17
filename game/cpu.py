"""
CPUプレイヤークラス

ルールベースのAIロジックとオプションのOpenAI連携を提供します。
CPUは以下の優先順位で手を決定します：
1. 勝てる手があれば勝つ
2. 相手の勝ちを阻止する
3. 中心を取る
4. 角を取る
5. 辺を取る
"""

import os
import random
import re
from typing import Optional
from .board import Board
from .judge import Judge


class CPU:
    """
    CPUプレイヤークラス
    
    ルールベースのAIでゲームをプレイします。
    オプションでOpenAI APIを使用した手の提案も可能です。
    """
    
    # 盤面の位置定数
    CENTER = 4           # 中心のインデックス
    CORNERS = [0, 2, 6, 8]  # 四隅のインデックス
    EDGES = [1, 3, 5, 7]    # 辺（中心以外の外周）のインデックス
    
    def __init__(self, mark: str, opponent_mark: str, use_openai: bool = False):
        """
        CPUプレイヤーを初期化する
        
        Args:
            mark: CPUのマーク（"X" または "O"）
            opponent_mark: 対戦相手のマーク
            use_openai: OpenAI APIを使用するかどうか
        """
        self.mark = mark
        self.opponent_mark = opponent_mark
        self.use_openai = use_openai
        self._openai_client = None
        self._openai_available = False
        
        # OpenAI使用が指定されていれば初期化を試みる
        if use_openai:
            self._init_openai()
    
    def _init_openai(self) -> None:
        """
        OpenAIクライアントを初期化する
        
        .envファイルからAPIキーを読み込み、OpenAIクライアントを作成します。
        キーがない場合やライブラリがない場合は何もしません。
        """
        try:
            # .envファイルから環境変数を読み込む
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=api_key)
                self._openai_available = True
        except ImportError:
            # python-dotenvまたはopenaiライブラリがない場合
            pass
        except Exception:
            # その他のエラー（ネットワークエラーなど）
            pass
    
    def get_move(self, board: Board) -> int:
        """
        CPUの次の手を決定する
        
        OpenAIが有効な場合はまずOpenAIに問い合わせ、
        失敗した場合はルールベースのロジックにフォールバックします。
        
        Args:
            board: 現在のゲーム盤面
            
        Returns:
            配置するマスのインデックス（0-8）
        """
        # OpenAIが使用可能な場合、まずOpenAIに問い合わせる
        if self.use_openai and self._openai_available:
            openai_move = self._get_openai_move(board)
            if openai_move is not None:
                return openai_move
        
        # OpenAIが使えない場合やOpenAIが失敗した場合はルールベースで決定
        return self._get_rule_based_move(board)
    
    def _get_rule_based_move(self, board: Board) -> int:
        """
        ルールベースのロジックで手を決定する
        
        優先順位：
        1. 勝てる手があれば勝つ
        2. 相手の勝ちを阻止する
        3. 中心を取る
        4. 角を取る
        5. 辺を取る
        
        Args:
            board: 現在のゲーム盤面
            
        Returns:
            配置するマスのインデックス（0-8）
            
        Raises:
            ValueError: 空きマスがない場合
        """
        empty_cells = board.get_empty_cells()
        
        if not empty_cells:
            raise ValueError("空きマスがありません")
        
        # 優先度1: 自分が勝てる手があれば即座に勝つ
        winning_move = self._find_winning_move(board, self.mark)
        if winning_move is not None:
            return winning_move
        
        # 優先度2: 相手の勝ちを阻止する
        blocking_move = self._find_winning_move(board, self.opponent_mark)
        if blocking_move is not None:
            return blocking_move
        
        # 優先度3: 中心が空いていれば中心を取る
        if self.CENTER in empty_cells:
            return self.CENTER
        
        # 優先度4: 空いている角からランダムに選ぶ
        available_corners = [c for c in self.CORNERS if c in empty_cells]
        if available_corners:
            return random.choice(available_corners)
        
        # 優先度5: 空いている辺からランダムに選ぶ
        available_edges = [e for e in self.EDGES if e in empty_cells]
        if available_edges:
            return random.choice(available_edges)
        
        # フォールバック: 空いているマスからランダムに選ぶ
        return random.choice(empty_cells)
    
    def _find_winning_move(self, board: Board, player: str) -> Optional[int]:
        """
        指定したプレイヤーが勝てる手を探す
        
        勝利パターンの中で、2マスが埋まっていて1マスが空いているものを探します。
        
        Args:
            board: 現在のゲーム盤面
            player: チェックするプレイヤーのマーク
            
        Returns:
            勝てるマスのインデックス、なければNone
        """
        cells = board.get_board_state()
        
        # 全ての勝利パターンをチェック
        for pattern in Judge.WIN_PATTERNS:
            values = [cells[i] for i in pattern]
            
            # 2マスが同じプレイヤーで埋まっていて、1マスが空いている場合
            if values.count(player) == 2 and values.count(Board.EMPTY) == 1:
                # 空いているマスのインデックスを返す
                empty_idx = values.index(Board.EMPTY)
                return pattern[empty_idx]
        
        return None
    
    def _get_openai_move(self, board: Board) -> Optional[int]:
        """
        OpenAI APIを使用して手を取得する
        
        現在の盤面状態をプロンプトとして送信し、
        AIが提案する手を取得します。
        
        Args:
            board: 現在のゲーム盤面
            
        Returns:
            提案されたマスのインデックス、失敗した場合はNone
        """
        if not self._openai_client:
            return None
        
        try:
            # 盤面を文字列形式に変換（空きマスは数字で表示）
            cells = board.get_board_state()
            board_str = ""
            for i in range(3):
                row = cells[i*3:(i+1)*3]
                row_str = " | ".join(c if c else str(i*3 + j) for j, c in enumerate(row))
                board_str += f"{row_str}\n"
                if i < 2:
                    board_str += "---------\n"
            
            empty_cells = board.get_empty_cells()
            
            # OpenAIへのプロンプトを作成
            prompt = f"""You are playing Tic-Tac-Toe as '{self.mark}'. 
Current board (numbers show empty cell indices):
{board_str}
Available moves: {empty_cells}
Reply with ONLY a single number (the cell index) for your best move."""

            # OpenAI APIを呼び出す
            response = self._openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=10,
                temperature=0.3
            )
            
            move_str = response.choices[0].message.content.strip()
            
            # 応答から数字を抽出（「I choose 4」のような応答にも対応）
            match = re.search(r'\d+', move_str)
            if match:
                move = int(match.group())
                # 有効な手かどうかを確認
                if move in empty_cells:
                    return move
            
        except Exception:
            # エラーが発生した場合はNoneを返してフォールバック
            pass
        
        return None
    
    @staticmethod
    def get_game_reflection(moves: list[dict], winner: str) -> Optional[str]:
        """
        ゲーム終了後の反省コメントをOpenAIから取得する
        
        対戦の手順と結果を送信し、AIによる短い反省コメントを取得します。
        この機能はオプションで、APIキーがない場合は何も返しません。
        
        Args:
            moves: ゲーム中の手順リスト（各要素は player, mark, position を含む辞書）
            winner: 勝者（"CPU", "Human", または "Draw"）
            
        Returns:
            反省コメント（日本語）、取得できない場合はNone
        """
        try:
            # .envファイルから環境変数を読み込む
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return None
            
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            
            # 手順を文字列形式に変換
            moves_str = "\n".join([f"{m['player']}: position {m['position']}" for m in moves])
            
            # 反省コメント取得用のプロンプト
            prompt = f"""A Tic-Tac-Toe game just ended.
Moves:
{moves_str}
Result: {winner}

Give a brief, fun reflection on this game in 1-2 sentences (in Japanese)."""

            # OpenAI APIを呼び出す
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception:
            # エラーが発生した場合はNoneを返す
            return None
