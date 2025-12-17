#!/usr/bin/env python3
"""Entry point for the Tic-Tac-Toe game."""

import tkinter as tk
from ui import TicTacToeApp


def main():
    """Main function to start the application."""
    root = tk.Tk()
    app = TicTacToeApp(root)
    app.run()


if __name__ == "__main__":
    main()
