#!/usr/bin/env python3
"""
〇×ゲーム（Tic-Tac-Toe）エントリーポイント

このファイルがアプリケーションの起動ポイントです。
実行方法: python main.py
"""

import tkinter as tk
from ui import TicTacToeApp


def main():
    """
    アプリケーションを起動する
    
    tkinterのルートウィンドウを作成し、〇×ゲームアプリケーションを起動します。
    """
    # tkinterのルートウィンドウを作成
    root = tk.Tk()
    # アプリケーションを初期化
    app = TicTacToeApp(root)
    # メインループを開始（ウィンドウを表示）
    app.run()


if __name__ == "__main__":
    # スクリプトとして直接実行された場合にmain()を呼び出す
    main()
