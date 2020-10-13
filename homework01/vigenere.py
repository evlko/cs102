def encrypt_vigenere(plaintext: str, keyword: str) -> str:
    """
    Encrypts plaintext using a Vigenere cipher.

    >>> encrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> encrypt_vigenere("python", "a")
    'python'
    >>> encrypt_vigenere("ATTACKATDAWN", "LEMON")
    'LXFOPVEFRNHR'
    """
    ciphertext = ""
    keyword *= len(plaintext) // len(keyword) + 1
    for letter in plaintext:
        symbol_number = ord(letter)
        shift = ord(keyword[0].lower())-ord("a")
        keyword = keyword[1:]
        if letter.isupper():
            symbol_number = (symbol_number + shift - ord("A")) % 26 + ord("A")
        elif letter.islower():
            symbol_number = (symbol_number + shift - ord("a")) % 26 + ord("a")
        ciphertext += chr(symbol_number)
    return ciphertext


def decrypt_vigenere(ciphertext: str, keyword: str) -> str:
    """
    Decrypts a ciphertext using a Vigenere cipher.

    >>> decrypt_vigenere("PYTHON", "A")
    'PYTHON'
    >>> decrypt_vigenere("python", "a")
    'python'
    >>> decrypt_vigenere("LXFOPVEFRNHR", "LEMON")
    'ATTACKATDAWN'
    """
    plaintext = ""
    keyword *= len(ciphertext) // len(keyword) + 1
    for letter in ciphertext:
        symbol_number=ord(letter)
        shift=ord(keyword[0].lower())-ord("a")
        keyword=keyword[1:]
        if letter.isupper():
            symbol_number=(symbol_number - shift - ord("A")) % 26 + ord("A")
        elif letter.islower():
            symbol_number=(symbol_number - shift - ord("a")) % 26 + ord("a")
        plaintext += chr(symbol_number)
    return plaintext
