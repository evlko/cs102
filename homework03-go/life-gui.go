package main

import (
	"github.com/gonutz/prototype/draw"
	"time"
)

func (game *Game) createCells() []cell {
	var cells []cell
	for row := 0; row < len(game.Grid); row++ {
		for col := 0; col < len(game.Grid[row]); col++ {
			cells = append(cells, cell{
				x: row,
				y: col,
				color: draw.White,
			})
		}
	}
	return cells
}

func (c *cell) changeColor(grid [][]int)  {
	if grid[c.x][c.y] == 1 {
		c.color = draw.LightGreen
	} else{
		c.color = draw.White
	}
}

type cell struct {
	x, y  int
	color draw.Color
}

func (game *Game) runWindow(size int) {
	var (
		cells []cell
	)

	cells = game.createCells()

	draw.RunWindow("Life Game", len(game.Grid)*size, len(game.Grid[0])*size, func(window draw.Window) {
		if window.WasKeyPressed(draw.KeyEscape) {
			window.Close()
		}
		for i := range cells{
			cells[i].changeColor(game.Grid)
		}

		for _, cell := range cells {
			window.FillRect(cell.x * size, cell.y * size, size, size, cell.color)
		}

		time.Sleep(200 * time.Millisecond)
		game.Step()
	})
}

