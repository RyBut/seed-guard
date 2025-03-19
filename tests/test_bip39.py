import pytest
from seed_guard._bip39 import BIP39
from seed_guard._mnenomic_length import MnemonicLength

@pytest.fixture
def bip39():
    """Create a fresh BIP39 instance for each test"""
    return BIP39()

def test_valid_word(bip39):
    assert bip39.is_valid_word("abandon")
    assert bip39.is_valid_word("ABANDON")
    assert bip39.is_valid_word("zoo")
    assert not bip39.is_valid_word("notaword")

def test_valid_mnemonic_lengths(bip39):
    words_12 = ["abandon"] * 12
    words_24 = ["abandon"] * 24
    words_15 = ["abandon"] * 15
    
    assert bip39.is_valid_mnemonic(words_12)
    assert bip39.is_valid_mnemonic(words_24)
    assert not bip39.is_valid_mnemonic(words_15)

def test_validate_mnemonic(bip39):
    valid_words = ["abandon"] * 12
    
    # Should not raise
    bip39.validate_mnemonic(valid_words)
    
    # Test invalid length
    with pytest.raises(ValueError) as exc_info:
        bip39.validate_mnemonic(["abandon"] * 15)
    assert "Invalid mnemonic length" in str(exc_info.value)
    
    # Test invalid word
    invalid_words = ["notaword"] + ["abandon"] * 11
    with pytest.raises(ValueError) as exc_info:
        bip39.validate_mnemonic(invalid_words)
    assert "Invalid word at position 1" in str(exc_info.value)

def test_word_to_index_conversion(bip39):
    assert bip39.word_to_index("abandon") == 0
    assert bip39.word_to_index("zoo") == 2047
    assert bip39.word_to_index("ABANDON") == 0  # test case insensitivity
    assert bip39.word_to_index("notaword") is None

def test_index_to_word_conversion(bip39):
    assert bip39.index_to_word(0) == "abandon"
    assert bip39.index_to_word(2047) == "zoo"
    assert bip39.index_to_word(-1) is None
    assert bip39.index_to_word(2048) is None

def test_words_to_indices_conversion(bip39):
    words = ["abandon", "ability", "able"] + ["abandon"] * 9  # 12 words
    indices = bip39.words_to_indices(words)
    assert indices == [0, 1, 2] + [0] * 9

    with pytest.raises(ValueError):
        bip39.words_to_indices(["notaword"] + ["abandon"] * 11)

def test_indices_to_words_conversion(bip39):
    indices = [0, 1, 2] + [0] * 9  # 12 indices
    words = bip39.indices_to_words(indices)
    assert words == ["abandon", "ability", "able"] + ["abandon"] * 9

    with pytest.raises(ValueError):
        bip39.indices_to_words([2048] + [0] * 11)  # invalid index

def test_get_word_length(bip39):
    assert bip39.get_word_length(["abandon"] * 12) == MnemonicLength.WORDS_12
    assert bip39.get_word_length(["abandon"] * 24) == MnemonicLength.WORDS_24
    assert bip39.get_word_length(["abandon"] * 15) is None

import random

def test_generate_random_phrases(bip39):
    # Generate 12-word phrase
    indices_12 = [random.randint(0, 2047) for _ in range(12)]
    words_12 = bip39.indices_to_words(indices_12)
    assert len(words_12) == 12
    assert bip39.is_valid_mnemonic(words_12)
    # Verify conversion back to indices
    assert bip39.words_to_indices(words_12) == indices_12
    
    # Generate 24-word phrase
    indices_24 = [random.randint(0, 2047) for _ in range(24)]
    words_24 = bip39.indices_to_words(indices_24)
    assert len(words_24) == 24
    assert bip39.is_valid_mnemonic(words_24)
    # Verify conversion back to indices
    assert bip39.words_to_indices(words_24) == indices_24