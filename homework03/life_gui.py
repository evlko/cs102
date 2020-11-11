import argparse

import pygame  # type: ignore
from pygame.locals import *  # type: ignore

from life import GameOfLife
from ui import UI


class GUI(UI):
    def __init__(self, life: GameOfLife, cell_size: int = 10, speed: int = 10) -> None:
        super().__init__(life)
        self.width = cell_size * self.life.cols
        self.height = cell_size * self.life.rows
        self.cell_size = cell_size

        # Устанавливаем размер окна
        self.screen_size = self.width, self.height

        # Создание нового окна
        self.screen = pygame.display.set_mode(self.screen_size)

        # Скорость протекания игры
        self.speed = speed

    def draw_lines(self) -> None:
        """ Отрисовать сетку """
        for x in range(0, self.width, self.cell_size):
            pygame.draw.line(
                self.screen, pygame.Color("black"), (x, 0), (x, self.height)
            )
        for y in range(0, self.height, self.cell_size):
            pygame.draw.line(
                self.screen, pygame.Color("black"), (0, y), (self.width, y)
            )

    def draw_grid(self) -> None:
        """
        Отрисовка списка клеток с закрашиванием их в соответствующе цвета.
        """
        for x in range(0, self.width, self.cell_size):
            for y in range(0, self.height, self.cell_size):
                color = (255, 255, 255)  # white color
                if (
                    self.life.curr_generation[y // self.cell_size][x // self.cell_size]
                    == 1
                ):
                    color = (127, 242, 26)  # green color
                pygame.draw.rect(
                    self.screen,
                    pygame.Color(color),
                    (x, y, self.cell_size, self.cell_size),
                )

    def run(self) -> None:
        """ Запустить игру """
        pygame.init()
        clock = pygame.time.Clock()
        pygame.display.set_caption("Game of Life")
        self.screen.fill(pygame.Color("white"))

        running = True
        paused = False
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:  # type: ignore
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == K_SPACE:  # type: ignore
                        paused = not paused
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    self.life.curr_generation[pos[1] // self.cell_size][
                        pos[0] // self.cell_size
                    ] ^= 1
            # Отрисовка списка клеток
            self.draw_grid()
            self.draw_lines()
            # Выполнение одного шага игры (обновление состояния ячеек), если нет паузы
            if not paused:
                self.life.step()
            pygame.display.flip()
            clock.tick(self.speed)
        pygame.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--width",
        action="store",
        dest="width",
        type=int,
        default=50,
        help="Width",
    )
    parser.add_argument(
        "--height",
        action="store",
        dest="height",
        type=int,
        default=20,
        help="Height",
    )
    parser.add_argument(
        "--max-generations",
        action="store",
        dest="max_generations",
        type=int,
        default=100,
        help="Number of max generations",
    )
    parser.add_argument(
        "--cell-size",
        action="store",
        dest="cell_size",
        type=int,
        default=10,
        help="Size of a cell",
    )
    args = parser.parse_args()
    life = GameOfLife((args.height, args.width), max_generations=args.max_generations)
    gui = GUI(life, cell_size=args.cell_size)
    gui.run()
