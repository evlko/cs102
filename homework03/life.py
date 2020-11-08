import pathlib
import random
import typing as tp

import pygame
from pygame.locals import *

Cell = tp.Tuple[int, int]
Cells = tp.List[int]
Grid = tp.List[Cells]

class GameOfLife:
    def __init__(
        self,
        size: tp.Tuple[int, int],
        randomize: bool = True,
        max_generations: tp.Optional[float] = float("inf"),
    ) -> None:
        # Размер клеточного поля
        self.rows, self.cols = size
        # Предыдущее поколение клеток
        self.prev_generation = self.create_grid()
        # Текущее поколение клеток
        self.curr_generation = self.create_grid(randomize=randomize)
        # Максимальное число поколений
        self.max_generations = max_generations
        # Текущее число поколений
        self.generations = 1

    def create_grid(self, randomize: bool = False) -> Grid:
        return [
            [random.randint(0, 1 if randomize else 0) for w in range(self.cols)]
            for h in range(self.rows)
        ]

    def get_neighbours(self, cell: Cell) -> Cells:
        x, y = cell[0], cell[1]
        neighbours = []
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if (0 <= i < self.rows and 0 <= j < self.cols) and (
                    (x, y) != (i, j)
                ):
                    neighbours.append(self.prev_generation[i][j])
        return neighbours

    def get_next_generation(self) -> Grid:
        new_cells = self.create_grid(False)
        for i in range(self.rows):
            for j in range(self.cols):
                count = sum(self.get_neighbours((j, i)))
                if count == 3 or (count == 2 and self.prev_generation[j][i] == 1):
                    new_cells[j][i] = 1
                else:
                    new_cells[j][i] = 0
        return new_cells

    def step(self) -> None:
        """
        Выполнить один шаг игры.
        """
        self.prev_generation = self.curr_generation
        self.curr_generation = self.get_next_generation()
        self.generations += 1

    @property
    def is_max_generations_exceeded(self) -> bool:
        """
        Не превысило ли текущее число поколений максимально допустимое.
        """
        return False if self.generations < self.max_generations else True

    @property
    def is_changing(self) -> bool:
        """
        Изменилось ли состояние клеток с предыдущего шага.
        """
        return True if self.prev_generation != self.curr_generation else False

    @staticmethod
    def from_file(filename: pathlib.Path) -> "GameOfLife":
        """
        Прочитать состояние клеток из указанного файла.
        """
        f = open(filename, 'r')
        grid = [[int(num) for num in line.strip()] for line in f]
        f.close()
        game_of_life = GameOfLife((len(grid),len(grid[0])))
        game_of_life.curr_generation = grid
        return game_of_life

    def save(self, filename: pathlib.Path) -> None:
        """
        Сохранить текущее состояние клеток в указанный файл.
        """
        f = open(filename, 'w')
        f.write('\n'.join([''.join(str(line).strip(']').strip('[').replace(' ','').replace(',','')) for line in self.curr_generation]))
        f.close()

life = GameOfLife.from_file('glider.txt')
for i in range(4):
    life.step()
life.save('glider-4-steps.txt')
