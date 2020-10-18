package caesar

func EncryptCaesar(plaintext string, shift int) string {
	var ciphertext string

	for i := 0; i < len(plaintext); i++ {
		symbolNumber := int(plaintext[i])
		if (int('A') <= symbolNumber) && (symbolNumber <= int('Z')) {
			symbolNumber = (int(symbolNumber)+shift-int('A'))%26 + int('A')
		} else if (int('a') <= symbolNumber) && (symbolNumber <= int('z')) {
			symbolNumber = (int(symbolNumber)+shift-int('a'))%26 + int('a')
		}
		ciphertext += string(rune(symbolNumber))
	}
	return ciphertext
}

func DecryptCaesar(ciphertext string, shift int) string {
	var plaintext string

	for i := 0; i < len(ciphertext); i++ {
		symbolNumber := int(ciphertext[i])
		if (int('A') <= symbolNumber) && (symbolNumber <= int('Z')) {
			symbolNumber = (symbolNumber-shift-int('A')+26)%26 + int('A')
		} else if (int('a') <= symbolNumber) && (symbolNumber <= int('z')) {
			symbolNumber = (symbolNumber-shift-int('a')+26)%26 + int('a')
		}
		plaintext += string(rune(symbolNumber))
	}
	return plaintext
}
