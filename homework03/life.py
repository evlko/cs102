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
        """
        Создание списка клеток.

        Клетка считается живой, если ее значение равно 1, в противном случае клетка
        считается мертвой, то есть, ее значение равно 0.

        Parameters
        ----------
        randomize : bool
            Если значение истина, то создается матрица, где каждая клетка может
            быть равновероятно живой или мертвой, иначе все клетки создаются мертвыми.

        Returns
        ----------
        out : Grid
            Матрица клеток размером `rows` х `cols`.
        """
        return [
            [random.randint(0, 1 if randomize else 0) for w in range(self.cols)]
            for h in range(self.rows)
        ]

    def get_neighbours(self, cell: Cell) -> Cells:
        """
        Вернуть список соседних клеток для клетки `cell`.

        Соседними считаются клетки по горизонтали, вертикали и диагоналям,
        то есть, во всех направлениях.

        Parameters
        ----------
        cell : Cell
            Клетка, для которой необходимо получить список соседей. Клетка
            представлена кортежем, содержащим ее координаты на игровом поле.

        Returns
        ----------
        out : Cells
            Список соседних клеток.
        """
        x, y = cell[0], cell[1]
        neighbours = []
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                if (0 <= i < self.rows and 0 <= j < self.cols) and ((x, y) != (i, j)):
                    neighbours.append(self.curr_generation[i][j])
        return neighbours

    def get_next_generation(self) -> Grid:
        """
        Получить следующее поколение клеток.
        Returns
        ----------
        out : Grid
            Новое поколение клеток.
        """
        new_grid = self.create_grid()
        for i in range(self.rows):
            for j in range(self.cols):
                count = sum(self.get_neighbours((i, j)))
                if count == 3 or (count == 2 and self.curr_generation[i][j] == 1):
                    new_grid[i][j] = 1
                else:
                    new_grid[i][j] = 0
        return new_grid

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
        return self.generations >= self.max_generations  # type: ignore

    @property
    def is_changing(self) -> bool:
        """
        Изменилось ли состояние клеток с предыдущего шага.
        """
        return self.prev_generation != self.curr_generation

    @staticmethod
    def from_file(filename: pathlib.Path) -> "GameOfLife":
        """
        Прочитать состояние клеток из указанного файла.
        """
        f = open(filename, "r")
        grid = [[int(num) for num in line.strip()] for line in f]
        f.close()
        game_of_life = GameOfLife((len(grid), len(grid[0])))
        game_of_life.curr_generation = grid
        return game_of_life

    def save(self, filename: pathlib.Path) -> None:
        """
        Сохранить текущее состояние клеток в указанный файл.
        """
        f = open(filename, "w")
        f.write(
            "\n".join(
                [
                    "".join(
                        str(line)
                        .strip("]")
                        .strip("[")
                        .replace(" ", "")
                        .replace(",", "")
                    )
                    for line in self.curr_generation
                ]
            )
        )
        f.close()
