package vigenere

import "strings"

func EncryptVigenere(plaintext string, keyword string) string {
	var ciphertext string

	diff := len(plaintext) - len(keyword)
	save := len(keyword)
	for i := 0; i < diff; i++ {
		keyword = keyword + string(keyword[i%save])
	}
	keyword = strings.ToLower(keyword)

	for i := 0; i < len(plaintext); i++ {
		shift := int(keyword[0]) - int('a')
		keyword = keyword[1:]
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

func DecryptVigenere(ciphertext string, keyword string) string {
	var plaintext string

	diff := len(ciphertext) - len(keyword)
	save := len(keyword)
	for i := 0; i < diff; i++ {
		keyword = keyword + string(keyword[i%save])
	}
	keyword = strings.ToLower(keyword)

	for i := 0; i < len(ciphertext); i++ {
		shift := int(keyword[0]) - int('a')
		keyword = keyword[1:]
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
