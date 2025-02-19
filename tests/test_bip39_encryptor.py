import random
import pytest
import os
from seed_guard.bip39_compression import BIP39Compression
from seed_guard.bip39_encryptor import BIP39Encryptor

@pytest.fixture
def compressor():
    return BIP39Compression()

@pytest.fixture
def encryptor():
    return BIP39Encryptor()

def test_basic_encryption_decryption(encryptor):
    data = b"test data"
    password = "test_password"
    
    encrypted = encryptor.encrypt(data, password)
    decrypted = encryptor.decrypt(encrypted, password)
    
    assert decrypted == data
    assert len(encrypted) == len(data) + encryptor.SALT_SIZE + encryptor.NONCE_SIZE + 16  # +16 for auth tag

def test_wrong_password(encryptor):
    data = b"test data"
    encrypted = encryptor.encrypt(data, "correct_password")
    
    with pytest.raises(Exception):  # Should fail to decrypt
        encryptor.decrypt(encrypted, "wrong_password")

def test_data_tampering(encryptor):
    data = b"test data"
    password = "test_password"
    encrypted = encryptor.encrypt(data, password)
    
    # Tamper with the ciphertext
    tampered = encrypted[:-1] + bytes([encrypted[-1] ^ 1])
    
    with pytest.raises(Exception):
        encryptor.decrypt(tampered, password)

def test_compression_encryption_flow(compressor, encryptor):
    # Test with 12-word seed
    indices_12 = [i for i in range(12)]
    password = "test_password"
    
    compressed = compressor.compress(indices_12)
    encrypted = encryptor.encrypt(compressed, password)
    decrypted = encryptor.decrypt(encrypted, password)
    decompressed = compressor.decompress(decrypted)
    
    assert decompressed == indices_12
    assert len(encrypted) == len(compressed) + encryptor.SALT_SIZE + encryptor.NONCE_SIZE + 16

def test_random_seeds_encryption(compressor, encryptor):
    passwords = ["simple", "complex!@#$%^&*()", "unicode♠♣♥♦", ""]
    
    for password in passwords:
        for _ in range(10):  # Test 10 random seeds for each password
            # Generate random seed phrases (both 12 and 24 words)
            indices_12 = [random.randint(0, 2047) for _ in range(12)]
            indices_24 = [random.randint(0, 2047) for _ in range(24)]
            
            for indices in [indices_12, indices_24]:
                compressed = compressor.compress(indices)
                encrypted = encryptor.encrypt(compressed, password)
                decrypted = encryptor.decrypt(encrypted, password)
                decompressed = compressor.decompress(decrypted)
                
                assert decompressed == indices

def test_empty_data(encryptor):
    password = "test_password"
    data = b""
    
    encrypted = encryptor.encrypt(data, password)
    decrypted = encryptor.decrypt(encrypted, password)
    
    assert decrypted == data

def test_large_data(encryptor):
    password = "test_password"
    data = os.urandom(1000)  # 1KB of random data
    
    encrypted = encryptor.encrypt(data, password)
    decrypted = encryptor.decrypt(encrypted, password)
    
    assert decrypted == data

def test_same_data_different_ciphertext(encryptor):
    data = b"test data"
    password = "test_password"
    
    encrypted1 = encryptor.encrypt(data, password)
    encrypted2 = encryptor.encrypt(data, password)
    
    # Should be different due to random salt and nonce
    assert encrypted1 != encrypted2
    
    # But both should decrypt to the same data
    assert encryptor.decrypt(encrypted1, password) == encryptor.decrypt(encrypted2, password)