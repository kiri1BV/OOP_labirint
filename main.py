#!/usr/bin/env python3

from src.core.game import Game


def main():
    game = Game(maze_width=21, maze_height=15)
    game.run()


if __name__ == "__main__":
    main()
