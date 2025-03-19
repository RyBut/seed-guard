from typing import List, Optional
from ._bip39_wordlist import WORDLIST
from ._mnenomic_length import MnemonicLength

class BIP39:
    """
    Class to handle BIP39 seed word operations including validation and conversion
    """
    
    VALID_LENGTHS = {MnemonicLength.WORDS_12.value, MnemonicLength.WORDS_24.value}
    
    def __init__(self):
        self._word_to_index = {word: index for index, word in enumerate(WORDLIST)}
    
    @property
    def valid_lengths(self) -> List[int]:
        """Get valid mnemonic lengths"""
        return sorted(list(self.VALID_LENGTHS))
    
    def is_valid_word(self, word: str) -> bool:
        """
        Check if a word is a valid BIP39 word
        
        Args:
            word: Word to check
            
        Returns:
            bool: True if word is valid, False otherwise
        """
        return word.lower() in self._word_to_index
    
    def is_valid_mnemonic(self, mnemonic: List[str]) -> bool:
        """
        Check if a mnemonic phrase is valid (all words exist and length is correct)
        
        Args:
            mnemonic: List of words to verify
            
        Returns:
            bool: True if mnemonic is valid, False otherwise
        """
        if len(mnemonic) not in self.VALID_LENGTHS:
            return False
        return all(self.is_valid_word(word) for word in mnemonic)
    
    def validate_mnemonic(self, mnemonic: List[str]) -> None:
        """
        Validate a mnemonic phrase and raise descriptive errors if invalid
        
        Args:
            mnemonic: List of words to verify
            
        Raises:
            ValueError: If mnemonic is invalid with specific reason
        """
        if not mnemonic:
            raise ValueError("Mnemonic cannot be empty")
            
        length = len(mnemonic)
        if length not in self.VALID_LENGTHS:
            raise ValueError(
                f"Invalid mnemonic length: {length}. "
                f"Must be one of {self.valid_lengths}"
            )
            
        for i, word in enumerate(mnemonic):
            if not self.is_valid_word(word):
                raise ValueError(
                    f"Invalid word at position {i + 1}: '{word}'"
                )
    
    def word_to_index(self, word: str) -> Optional[int]:
        """
        Convert a BIP39 word to its index
        
        Args:
            word: BIP39 word
            
        Returns:
            int: Index of the word (0-2047) or None if word is invalid
        """
        return self._word_to_index.get(word.lower())
    
    def index_to_word(self, index: int) -> Optional[str]:
        """
        Convert an index to its corresponding BIP39 word
        
        Args:
            index: Index (0-2047)
            
        Returns:
            str: BIP39 word or None if index is out of range
        """
        if 0 <= index < len(WORDLIST):
            return WORDLIST[index]
        return None
    
    def words_to_indices(self, words: List[str]) -> List[int]:
        """
        Convert a list of BIP39 words to their indices
        
        Args:
            words: List of BIP39 words
            
        Returns:
            List[int]: List of indices
            
        Raises:
            ValueError: If any word is invalid
        """
        # Validate the mnemonic first
        self.validate_mnemonic(words)
        
        return [self._word_to_index[word.lower()] for word in words]
    
    def indices_to_words(self, indices: List[int]) -> List[str]:
        """
        Convert a list of indices to their corresponding BIP39 words
        
        Args:
            indices: List of indices (0-2047)
            
        Returns:
            List[str]: List of BIP39 words
            
        Raises:
            ValueError: If any index is out of range or invalid length
        """
        if len(indices) not in self.VALID_LENGTHS:
            raise ValueError(
                f"Invalid number of indices: {len(indices)}. "
                f"Must be one of {self.valid_lengths}"
            )
            
        words = []
        for i, index in enumerate(indices):
            word = self.index_to_word(index)
            if word is None:
                raise ValueError(f"Invalid index at position {i + 1}: {index}")
            words.append(word)
        return words
    
    def get_word_length(self, mnemonic: List[str]) -> Optional[MnemonicLength]:
        """
        Get the MnemonicLength enum for a given mnemonic
        
        Args:
            mnemonic: List of words
            
        Returns:
            MnemonicLength or None if invalid length
        """
        length = len(mnemonic)
        return next(
            (ml for ml in MnemonicLength if ml.value == length),
            None
        )