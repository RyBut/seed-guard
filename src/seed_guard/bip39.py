from .bip39_wordlist import WORDLIST

class BIP39:
    _word_to_index = {word: index for index, word in enumerate(WORDLIST)}
    _index_to_word = {index: word for index, word in enumerate(WORDLIST)}
    _index_to_binary = {index: format(index, '011b') for index in range(2048)}
    _binary_to_index = {format(index, '011b'): index for index in range(2048)}

    @classmethod
    def get_word(cls, index: int) -> str:
        """Get word from index (0-2047)"""
        if not 0 <= index <= 2047:
            raise ValueError("Index must be between 0 and 2047")
        return cls._index_to_word[index]

    @classmethod
    def get_index(cls, word: str) -> int:
        """Get index (0-2047) from word"""
        if word not in cls._word_to_index:
            raise ValueError(f"'{word}' is not a valid BIP39 word")
        return cls._word_to_index[word]

    @classmethod
    def get_binary(cls, word: str) -> str:
        """Get binary representation (11 bits) from word"""
        index = cls.get_index(word)
        return cls._index_to_binary[index]

    @classmethod
    def get_word_from_binary(cls, binary: str) -> str:
        """Get word from binary representation"""
        if not isinstance(binary, str) or not all(bit in '01' for bit in binary) or len(binary) != 11:
            raise ValueError("Binary must be an 11-bit string")
        return cls.get_word(cls._binary_to_index[binary])

    @classmethod
    def is_valid_word(cls, word: str) -> bool:
        """Check if word is in BIP39 wordlist"""
        return word in cls._word_to_index

    @classmethod
    def total_words(cls) -> int:
        """Get total number of words in wordlist"""
        return len(WORDLIST)