"""
盤面管理クラス

3x3の〇×ゲーム（Tic-Tac-Toe）の盤面状態を管理するクラスを提供します。
盤面は0-8のインデックスで表現され、以下のように配置されます：
    0 | 1 | 2
    ---------
    3 | 4 | 5
    ---------
    6 | 7 | 8
"""


class Board:
    """
    3x3の〇×ゲーム盤面を管理するクラス
    
    盤面の状態管理、マスへの配置、空きマスの取得などの機能を提供します。
    """
    
    # 定数: 空のマス、プレイヤーXとOのマーク
    EMPTY = ""
    PLAYER_X = "X"
    PLAYER_O = "O"
    
    def __init__(self):
        """
        盤面を初期化する
        
        9マス全てを空の状態で初期化します。
        """
        self.cells: list[str] = [self.EMPTY] * 9
    
    def reset(self) -> None:
        """
        盤面をリセットする
        
        全てのマスを空の状態に戻します。
        """
        self.cells = [self.EMPTY] * 9
    
    def get_cell(self, index: int) -> str:
        """
        指定したマスの状態を取得する
        
        Args:
            index: マスのインデックス（0-8）
            
        Returns:
            マスの状態（"X", "O", または空文字列）
        """
        if 0 <= index < 9:
            return self.cells[index]
        return self.EMPTY
    
    def set_cell(self, index: int, player: str) -> bool:
        """
        指定したマスにプレイヤーのマークを配置する
        
        Args:
            index: マスのインデックス（0-8）
            player: プレイヤーのマーク（"X" または "O"）
            
        Returns:
            配置成功ならTrue、マスが埋まっているか無効なインデックスならFalse
        """
        # インデックスが有効範囲内かつマスが空の場合のみ配置可能
        if 0 <= index < 9 and self.cells[index] == self.EMPTY:
            self.cells[index] = player
            return True
        return False
    
    def get_empty_cells(self) -> list[int]:
        """
        空いているマスのインデックス一覧を取得する
        
        Returns:
            空きマスのインデックスのリスト
        """
        return [i for i, cell in enumerate(self.cells) if cell == self.EMPTY]
    
    def is_full(self) -> bool:
        """
        盤面が全て埋まっているか確認する
        
        Returns:
            全マスが埋まっていればTrue、空きがあればFalse
        """
        return self.EMPTY not in self.cells
    
    def get_board_state(self) -> list[str]:
        """
        現在の盤面状態のコピーを取得する
        
        Returns:
            盤面状態のリスト（9要素）
        """
        return self.cells.copy()
    
    def get_cell_position(self, index: int) -> tuple[int, int]:
        """
        マスのインデックスを行・列の座標に変換する
        
        Args:
            index: マスのインデックス（0-8）
            
        Returns:
            (行, 列) のタプル（各0-2）
        """
        return (index // 3, index % 3)
    
    def get_cell_index(self, row: int, col: int) -> int:
        """
        行・列の座標をマスのインデックスに変換する
        
        Args:
            row: 行番号（0-2）
            col: 列番号（0-2）
            
        Returns:
            マスのインデックス（0-8）
        """
        return row * 3 + col
