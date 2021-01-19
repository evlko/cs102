package main

import (
	"fmt"
	"io/ioutil"
	"math/rand"
	"path/filepath"
	"reflect"
)

func readSudoku(filename string) ([][]byte, error) {
	data, err := ioutil.ReadFile(filename)
	if err != nil {
		return nil, err
	}
	grid := group(filter(data), 9)
	return grid, nil
}

func filter(values []byte) []byte {
	filteredValues := make([]byte, 0)
	for _, v := range values {
		if (v >= '1' && v <= '9') || v == '.' {
			filteredValues = append(filteredValues, v)
		}
	}
	return filteredValues
}

func display(grid [][]byte) {
	for i := 0; i < len(grid); i++ {
		for j := 0; j < len(grid); j++ {
			fmt.Print(string(grid[i][j]))
		}
		fmt.Println()
	}
}

func group(values []byte, n int) [][]byte {
	var result [][]byte

	for i := 0; i < len(values); i += n {
		result = append(result, values[i:i+n])
	}

	return result
}

func getRow(grid [][]byte, row int) []byte {
	return grid[row]
}

func getCol(grid [][]byte, col int) []byte {
	var result []byte

	for _, row := range grid {
		result = append(result, row[col])
	}

	return result
}

func getBlock(grid [][]byte, row int, col int) []byte {
	var result []byte

	for r := row / 3 * 3; r < 3 * (row / 3 + 1); r++ {
		for c := col / 3 * 3; c < 3 * (col / 3 + 1); c++ {
			result = append(result, grid[r][c])
		}
	}

	return result
}

func findEmptyPosition(grid [][]byte) (int, int) {
	for x, row := range grid {
		for y, digit := range row {
			if digit == '.' {
				return x, y
			}
		}
	}

	return -1, -1
}

// function that returns union of arrays without duplicates
func Union(a, b []byte) (uni []byte) {
	check := make(map[byte]bool)
	sum := append(a, b...)

	for _, item := range sum {
		check[item] = true
	}

	for item := range check {
		uni = append(uni, item)
	}

	return
}

// function that returns an array the difference between two other arrays
func Difference(a, b []byte) (diff []byte) {
	check := make(map[byte]bool)

	for _, item := range b {
		check[item] = true
	}

	for _, item := range a {
		if _, ok := check[item]; !ok {
			diff = append(diff, item)
		}
	}

	return
}

func findPossibleValues(grid [][]byte, row int, col int) []byte {
	digits := make([]byte, 0, 9)

	for i := '1'; i <= '9'; i++ {
		digits = append(digits, byte(i))
	}

	var rowValues []byte
	rowValues = append(rowValues, getRow(grid, row)...)


	var colValues []byte
	colValues = append(colValues, getCol(grid, col)...)

	var blockValues []byte
	blockValues = append(blockValues, getBlock(grid, row, col)...)

	var possibleValues []byte
	possibleValues = append(possibleValues, Union(Union(rowValues, colValues), blockValues)...)

	var result []byte
	result = append(result, Difference(digits, possibleValues)...)

	return result
}

func solve(grid [][]byte) ([][]byte, bool) {
	row, col := findEmptyPosition(grid)

	// -1, -1 - returns only if everything is solved
	if row == -1 && col == -1 {
		return grid, true
	}

	values := findPossibleValues(grid, row, col)
	if len(values) == 0 {
		return grid, false
	}

	for _, value := range values {
		grid[row][col] = value
		newResult, solution := solve(grid)
		if solution {
			return newResult, true
		}
		grid[row][col] = byte('.')
	}
	return grid, false
}

func checkSolution(grid [][]byte) bool {
	digits := make([]byte, 0, 9)
	for i := '1'; i <= '9'; i++ {
		digits = append(digits, byte(i))
	}

	for i := 0; i < 9; i++ {
		numbersInRow := getRow(grid, i)
		if !reflect.DeepEqual(numbersInRow, digits) {
			return false
		}
	}

	for i := 0; i < 9; i++ {
		numbersInCol := getCol(grid, i)
		if !reflect.DeepEqual(numbersInCol, digits) {
			return false
		}
	}

	for i := 0; i < 3; i++ {
		for j := 0; j < 3; j++ {
			numbersInBlock := getBlock(grid, i + 3 * i, j + 3 * j)
			if !reflect.DeepEqual(numbersInBlock, digits) {
				return false
			}
		}
	}

	return true
}

// struct for positions
type Position struct {
	x int
	y int
}

func generateSudoku(N int) [][]byte {
	if N > 81 {
		N = 81
	}

	grid := make([][]byte, 9, 9)
	for i := 0; i < 9; i++ {
		grid[i] = make([]byte, 9, 9)
		for j := 0; j < 9; j++ {
			grid[i][j] = byte('.')
		}
	}

	solvedGrid, _ := solve(grid)

	var positions []Position
	for i := 1; i <= 9; i++ {
		for j := 1; j <= 9; j++ {
			positions = append(positions, Position{i, j})
		}
	}

	for i := 0; i < 81 - N; i++{
		cell := rand.Intn(len(positions)-1)
		solvedGrid[positions[cell].x][positions[cell].y] = byte('.')
		positions = append(positions[:cell], positions[cell+1:]...)
	}

	return solvedGrid
}

func main() {
	puzzles, err := filepath.Glob("puzzle*.txt")
	if err != nil {
		fmt.Printf("Could not find any puzzles")
		return
	}
	for _, fname := range puzzles {
		go func(fname string) {
			grid, _ := readSudoku(fname)
			solution, _ := solve(grid)
			fmt.Println("Solution for", fname)
			display(solution)
		}(fname)
	}
	var input string
	fmt.Scanln(&input)
}
