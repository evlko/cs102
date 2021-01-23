package main

func DrawHorizontalBorders(len int) string{
	output := "+"
	for col := 0; col < len; col++{
		output += "-"
	}
	output += "+\n"
	return output
}

func (game *Game) ToString() string {
	output := ""
	output += DrawHorizontalBorders(len(game.Grid))
	for row := 0; row < len(game.Grid[0]); row++ {
		output += "|"
		for col := 0; col < len(game.Grid[row]); col++ {
			if game.Grid[row][col] == 1{
				output += "*"
			} else{
				output += " "
			}
		}
		output += "|\n"
	}
	output += DrawHorizontalBorders(len(game.Grid))
	return output
}