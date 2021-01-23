package main

import (
	"fmt"
	"math/rand"
	"os"
	"os/exec"
	"time"
)

type Game struct {
	gridOriginal [][]int
	Grid         [][]int
}

func New(rows, cols int) *Game {
	game := &Game{}
	game.Grid = make([][]int, rows)
	for i := range game.Grid {
		game.Grid[i] = make([]int, cols)
	}
	return game
}

func (game *Game) copyGrid() {
	game.gridOriginal = make([][]int, len(game.Grid))
	for i, row := range game.Grid {
		game.gridOriginal[i] = make([]int, len(row))
		copy(game.gridOriginal[i], row)
	}
}

func (game *Game) Step() {
	game.copyGrid()

	for row := 0; row < len(game.Grid); row++ {
		for col := 0; col < len(game.Grid[row]); col++ {
			neighbours := game.getNeighbours(row, col)
			if neighbours == 3 || (neighbours == 2 && game.gridOriginal[row][col] == 1){
				game.Grid[row][col] = 1
			} else {
				game.Grid[row][col] = 0
			}
		}
	}
}

func (game *Game) getNeighbours(row, col int) int {
	x := row
	y := col
	neighbours := 0
	for row := x - 1; row < x + 2; row++ {
		for col := y - 1; col < y + 2; col++ {
			if (row >= 0 && row < len(game.gridOriginal)) && (col >= 0 && col < len(game.gridOriginal[row])) {
				neighbours += game.gridOriginal[row][col]
			}
		}
	}
	neighbours -= game.gridOriginal[x][y]
	return neighbours
}

func (game *Game) CreateGrid(random bool) {
	rand.Seed(time.Now().UTC().UnixNano())
	max := 1
	if random{max = 2}
	for i := 0; i < len(game.Grid); i++ {
		for j := 0; j < len(game.Grid[i]); j++ {
			if rand.Intn(max) == 1 {
				game.Grid[i][j] = 1
			} else {
				game.Grid[i][j] = 0
			}
		}
	}
}

func CallClear() {
	cmd := exec.Command("cmd", "/c", "cls")
	cmd.Stdout = os.Stdout
	cmd.Run()
}

func main() {
	var(
		rows int
		cols int
		mode int
		size int
	)

	fmt.Print("Enter the number of rows: ")
	fmt.Scanf("%d\n", &rows)

	fmt.Print("Enter the number of columns: ")
	fmt.Scanf("%d\n", &cols)

	fmt.Print("Choose the mode [1 - console, 2 - GUI]: ")
	fmt.Scanf("%d\n", &mode)


	game := New(rows, cols)
	game.CreateGrid(true)

	if mode == 1 {
		for {
			CallClear()
			game.Step()
			print(game.ToString())
			time.Sleep(200 * time.Millisecond)
		}
	} else if mode == 2 {
		fmt.Print("Cell size: ")
		fmt.Scanf("%d\n", &size)
		game.runWindow(size)
	}
}
