"""
勝敗判定クラス

〇×ゲームの勝敗判定ロジックを提供します。
縦・横・斜めの3つ揃いによる勝利判定と、引き分け判定を行います。
"""

from typing import Optional
from .board import Board


class Judge:
    """
    〇×ゲームの勝敗判定を行うクラス
    
    勝利パターン（縦3列、横3行、斜め2本の計8パターン）をチェックし、
    勝者の判定、引き分けの判定、ゲーム終了の判定を行います。
    """
    
    # 勝利パターン: 3つ揃えば勝ちとなるマスの組み合わせ（8パターン）
    WIN_PATTERNS = [
        [0, 1, 2],  # 上段（横）
        [3, 4, 5],  # 中段（横）
        [6, 7, 8],  # 下段（横）
        [0, 3, 6],  # 左列（縦）
        [1, 4, 7],  # 中列（縦）
        [2, 5, 8],  # 右列（縦）
        [0, 4, 8],  # 左上から右下への斜め
        [2, 4, 6],  # 右上から左下への斜め
    ]
    
    @classmethod
    def get_winning_line(cls, board: Board) -> Optional[list[int]]:
        """
        勝利ラインを取得する
        
        3つ揃っているラインがあれば、そのマスのインデックスを返します。
        
        Args:
            board: ゲーム盤面
            
        Returns:
            勝利ラインのインデックスリスト（3要素）、なければNone
        """
        cells = board.get_board_state()
        
        # 全ての勝利パターンをチェック
        for pattern in cls.WIN_PATTERNS:
            a, b, c = pattern
            # 3マスが全て同じマークで埋まっていれば勝利
            if cells[a] != Board.EMPTY and cells[a] == cells[b] == cells[c]:
                return pattern
        
        return None
    
    @classmethod
    def check_winner(cls, board: Board) -> Optional[str]:
        """
        勝者を判定する
        
        Args:
            board: ゲーム盤面
            
        Returns:
            勝者のマーク（"X" または "O"）、勝者がいなければNone
        """
        # 勝利ラインがあれば、そのラインの最初のマスのマークが勝者
        winning_line = cls.get_winning_line(board)
        if winning_line:
            return board.get_cell(winning_line[0])
        return None
    
    @classmethod
    def check_draw(cls, board: Board) -> bool:
        """
        引き分けかどうかを判定する
        
        盤面が全て埋まっていて、かつ勝者がいない場合は引き分けです。
        
        Args:
            board: ゲーム盤面
            
        Returns:
            引き分けならTrue、そうでなければFalse
        """
        return board.is_full() and cls.get_winning_line(board) is None
    
    @classmethod
    def is_game_over(cls, board: Board) -> bool:
        """
        ゲームが終了したかどうかを判定する
        
        勝者がいるか、盤面が全て埋まっていればゲーム終了です。
        
        Args:
            board: ゲーム盤面
            
        Returns:
            ゲーム終了ならTrue、続行中ならFalse
        """
        return cls.get_winning_line(board) is not None or board.is_full()
