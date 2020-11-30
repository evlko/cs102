import argparse
import curses

from life import GameOfLife
from ui import UI


class Console(UI):
    def __init__(self, life: GameOfLife) -> None:
        super().__init__(life)

    def draw_borders(self, screen) -> None:
        """ Отобразить рамку. """
        screen.border("|", "|", "-", "-", "+", "+", "+", "+")

    def draw_grid(self, screen) -> None:
        """ Отобразить состояние клеток. """
        for i in range(1, self.life.rows + 1):
            for j in range(1, self.life.cols + 1):
                symbol = str(self.life.curr_generation[i - 1][j - 1])
                screen.addstr(i, j, "*") if symbol == "1" else screen.addstr(i, j, " ")

    def run(self) -> None:
        screen = curses.initscr()
        screen = curses.newwin(self.life.rows + 2, self.life.cols + 2)
        while self.life.is_changing and not self.life.is_max_generations_exceeded:
            self.draw_borders(screen)
            self.draw_grid(screen)
            self.life.step()
            screen.refresh()
        curses.endwin()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--rows",
        action="store",
        dest="rows",
        type=int,
        default=20,
        help="Number of rows",
    )
    parser.add_argument(
        "--cols",
        action="store",
        dest="cols",
        type=int,
        default=50,
        help="Number of cols",
    )
    parser.add_argument(
        "--max-generations",
        action="store",
        dest="max_generations",
        type=int,
        default=100,
        help="Number of max generations",
    )
    args = parser.parse_args()
    life = GameOfLife((args.rows, args.cols), max_generations=args.max_generations)
    ui = Console(life)
    ui.run()
