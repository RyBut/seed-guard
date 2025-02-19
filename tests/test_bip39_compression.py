import random
import pytest
from seed_guard.bip39_compression import BIP39Compression

@pytest.fixture
def compressor():
    return BIP39Compression()

def test_random_12_word(compressor):
    for _ in range(10000):  # Run 10000 random tests
        indices = [random.randint(0, 2047) for _ in range(12)]
        compressed = compressor.compress(indices)
        decompressed = compressor.decompress(compressed)
        assert indices == decompressed
        assert len(compressed) == 17  # 12 words should compress to 17 bytes

def test_random_24_word(compressor):
    for _ in range(10000):  # Run 10000 random tests
        indices = [random.randint(0, 2047) for _ in range(24)]
        compressed = compressor.compress(indices)
        decompressed = compressor.decompress(compressed)
        assert indices == decompressed
        assert len(compressed) == 33  # 24 words should compress to 33 bytes

def test_invalid_indices(compressor):
    with pytest.raises(ValueError):
        compressor.compress([2048])  # Index too large
    with pytest.raises(ValueError):
        compressor.compress([-1])    # Negative index

def test_empty_input(compressor):
    with pytest.raises(ValueError):
        compressor.decompress(b'')