import pytest
from seed_guard import SeedGuard

class TestSeedGuard:
    @pytest.fixture
    def seed_guard(self):
        return SeedGuard()
    
    @pytest.fixture
    def valid_seed_12(self):
        return [
            "abandon", "ability", "able", "about", "above", "absent",
            "absorb", "abstract", "absurd", "abuse", "access", "accident"
        ]
    
    @pytest.fixture
    def valid_seed_24(self):
        return [
            "abandon", "ability", "able", "about", "above", "absent",
            "absorb", "abstract", "absurd", "abuse", "access", "accident",
            "account", "accuse", "achieve", "acid", "acoustic", "acquire",
            "across", "act", "action", "actor", "actress", "actual"
        ]

    def test_basic_encoding_decoding_no_password(self, seed_guard, valid_seed_12):
        """Test basic encoding and decoding without password"""
        primary, shares = seed_guard.encode_seed_phrase(
            seed_words=valid_seed_12,
            shares_required=3,
            shares_total=5
        )
        
        # Verify number of shares and primary piece
        assert len(shares) == 5
        assert isinstance(primary, str)
        assert len(primary) > 0
        
        # Test reconstruction with exact number of required shares
        recovered = seed_guard.decode_shares(primary, shares[:3])
        assert recovered == valid_seed_12
        
        # Test reconstruction with more than required shares
        recovered = seed_guard.decode_shares(primary, shares[:4])
        assert recovered == valid_seed_12

    def test_encoding_decoding_with_password(self, seed_guard, valid_seed_24):
        """Test encoding and decoding with password"""
        password = "test_password123"
        primary, shares = seed_guard.encode_seed_phrase(
            seed_words=valid_seed_24,
            shares_required=2,
            shares_total=3,
            password=password
        )
        
        # Test successful decoding with correct password
        recovered = seed_guard.decode_shares(primary, shares[:2], password=password)
        assert recovered == valid_seed_24
        
        # Test failed decoding with wrong password
        with pytest.raises(Exception):
            seed_guard.decode_shares(primary, shares[:2], password="wrong_password")

    def test_insufficient_shares(self, seed_guard, valid_seed_12):
        """Test error handling when providing insufficient shares"""
        primary, shares = seed_guard.encode_seed_phrase(
            seed_words=valid_seed_12,
            shares_required=3,
            shares_total=5
        )
        
        with pytest.raises(ValueError, match="Insufficient shares"):
            seed_guard.decode_shares(primary, shares[:2])  # Only 2 shares when 3 required

    def test_invalid_share_combinations(self, seed_guard, valid_seed_12):
        """Test mixing shares from different encodings"""
        primary1, shares1 = seed_guard.encode_seed_phrase(
            seed_words=valid_seed_12,
            shares_required=2,
            shares_total=3
        )
        
        primary2, shares2 = seed_guard.encode_seed_phrase(
            seed_words=valid_seed_12,
            shares_required=2,
            shares_total=3
        )
        
        # Try to combine shares from different encodings
        # Should fail during decryption with InvalidTag
        from cryptography.exceptions import InvalidTag
        with pytest.raises(InvalidTag):
            seed_guard.decode_shares(primary1, [shares1[0], shares2[0]])

    def test_invalid_parameters(self, seed_guard, valid_seed_12):
        """Test invalid input parameters"""
        # Test threshold > total shares
        with pytest.raises(ValueError):
            seed_guard.encode_seed_phrase(
                seed_words=valid_seed_12,
                shares_required=4,
                shares_total=3
            )
        
        # Test threshold < 2
        with pytest.raises(ValueError):
            seed_guard.encode_seed_phrase(
                seed_words=valid_seed_12,
                shares_required=1,
                shares_total=3
            )

    def test_invalid_seed_phrase(self, seed_guard):
        """Test invalid seed phrases"""
        # Test wrong length
        invalid_seed = ["abandon"] * 15  # Invalid length
        with pytest.raises(ValueError):
            seed_guard.encode_seed_phrase(
                seed_words=invalid_seed,
                shares_required=2,
                shares_total=3
            )
        
        # Test invalid words
        invalid_seed = ["notaword"] + ["abandon"] * 11
        with pytest.raises(ValueError):
            seed_guard.encode_seed_phrase(
                seed_words=invalid_seed,
                shares_required=2,
                shares_total=3
            )

    def test_empty_inputs(self, seed_guard):
        """Test empty inputs"""
        # Test empty seed phrase
        with pytest.raises(ValueError):
            seed_guard.encode_seed_phrase(
                seed_words=[],
                shares_required=2,
                shares_total=3
            )
        
        # Test empty shares list
        with pytest.raises(ValueError):
            seed_guard.decode_shares("", [])

    def test_mixed_password_scenarios(self, seed_guard, valid_seed_12):
        """Test mixing password and no-password scenarios"""
        # Encode with custom password
        primary, shares = seed_guard.encode_seed_phrase(
            seed_words=valid_seed_12,
            shares_required=2,
            shares_total=3,
            password="test_password"
        )
        
        # Should fail when trying to decode with default password
        with pytest.raises(Exception):
            seed_guard.decode_shares(primary, shares[:2])  # Will use default password
        
        # Should succeed when using correct password
        recovered = seed_guard.decode_shares(primary, shares[:2], password="test_password")
        assert recovered == valid_seed_12

        # Encode with default password
        primary, shares = seed_guard.encode_seed_phrase(
            seed_words=valid_seed_12,
            shares_required=2,
            shares_total=3
        )
        
        # Should succeed when decoding with default password
        recovered = seed_guard.decode_shares(primary, shares[:2])  # Will use default password
        assert recovered == valid_seed_12

        # Should fail when trying to decode with different password
        with pytest.raises(Exception):
            seed_guard.decode_shares(primary, shares[:2], password="test_password")

    def test_invalid_primary_piece(self, seed_guard, valid_seed_12):
        """Test invalid primary piece scenarios"""
        primary, shares = seed_guard.encode_seed_phrase(
            seed_words=valid_seed_12,
            shares_required=2,
            shares_total=3
        )

        # Test with empty primary piece
        with pytest.raises(ValueError):
            seed_guard.decode_shares("", shares[:2])

        # Test with invalid format primary piece
        with pytest.raises(ValueError):
            seed_guard.decode_shares("invalid_format", shares[:2])

        # Test with wrong primary piece
        other_primary, _ = seed_guard.encode_seed_phrase(
            seed_words=valid_seed_12,
            shares_required=2,
            shares_total=3
        )
        with pytest.raises(Exception):
            seed_guard.decode_shares(other_primary, shares[:2])