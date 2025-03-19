import pytest
from itertools import combinations
from seed_guard._bip39_shamir import BIP39Shamir

@pytest.fixture
def shamir():
    return BIP39Shamir()

def test_split_and_combine(shamir):
    secret = b"Hello, World!"
    shares = 5
    threshold = 3
    
    # Split the secret
    share_pieces = shamir.split(secret, shares, threshold)
    
    # Verify we got the right number of shares
    assert len(share_pieces) == shares
    
    # Test combining with exact threshold
    recovered = shamir.combine(share_pieces[:threshold])
    assert recovered == secret
    
    # Test combining with more than threshold
    recovered = shamir.combine(share_pieces[:threshold+1])
    assert recovered == secret

def test_insufficient_shares(shamir):
    secret = b"Test Secret"
    shares = 5
    threshold = 3
    
    share_pieces = shamir.split(secret, shares, threshold)
    
    with pytest.raises(ValueError, match="Insufficient shares"):
        shamir.combine(share_pieces[:threshold-1])

def test_different_secret_sizes(shamir):
    test_secrets = [
        b"x",                    # 1 byte
        b"hello",               # 5 bytes
        b"x" * 16,             # 16 bytes
        b"x" * 32,             # 32 bytes
        b"x" * 128             # 128 bytes
    ]
    
    for secret in test_secrets:
        shares = shamir.split(secret, 5, 3)
        recovered = shamir.combine(shares[:3])
        assert recovered == secret

def test_all_share_combinations(shamir):
    secret = b"combination test"
    total_shares = 4
    threshold = 2
    
    shares = shamir.split(secret, total_shares, threshold)
    
    # Test all possible combinations of threshold shares
    for share_combination in combinations(shares, threshold):
        recovered = shamir.combine(list(share_combination))
        assert recovered == secret

def test_invalid_parameters(shamir):
    secret = b"test"
    
    # Test threshold > shares
    with pytest.raises(ValueError, match="Threshold cannot be greater than total shares"):
        shamir.split(secret, 2, 3)
    
    # Test threshold < 2
    with pytest.raises(ValueError, match="Threshold must be at least 2"):
        shamir.split(secret, 3, 1)

def test_different_field_shares(shamir):
    # Generate shares from different secrets (thus different field sizes)
    shares1 = shamir.split(b"small secret", 3, 2)
    shares2 = shamir.split(b"x" * 32, 3, 2)
    
    # Try to combine shares from different fields
    with pytest.raises(ValueError, match="Shares from different field sizes"):
        shamir.combine([shares1[0], shares2[0]])

def test_different_threshold_shares(shamir):
    secret = b"test secret"
    
    # Generate shares with different thresholds
    shares1 = shamir.split(secret, 3, 2)
    shares2 = shamir.split(secret, 3, 3)
    
    # Try to combine shares from different threshold schemes
    with pytest.raises(ValueError, match="Shares from different threshold schemes"):
        shamir.combine([shares1[0], shares2[0]])