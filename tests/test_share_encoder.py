import pytest
from seed_guard.share_encoder import ShareEncoder 

class TestShareEncoder:
    @pytest.fixture
    def encoder(self):
        return ShareEncoder()
    
    def test_empty_input(self, encoder):
        with pytest.raises(ValueError, match="Empty input"):
            encoder.encode_share(b'')
        
        with pytest.raises(ValueError, match="Empty input"):
            encoder.decode_share('')
    
    def test_basic_encoding_decoding(self, encoder):
        test_data = b'Hello, World!'
        encoded = encoder.encode_share(test_data)
        decoded = encoder.decode_share(encoded)
        assert decoded == test_data
    
    def test_binary_data(self, encoder):
        test_data = bytes([0, 1, 2, 3, 255, 254, 253])
        encoded = encoder.encode_share(test_data)
        decoded = encoder.decode_share(encoded)
        assert decoded == test_data
    
    def test_leading_zeros(self, encoder):
        test_data = bytes([0, 0, 1, 2, 3])
        encoded = encoder.encode_share(test_data)
        decoded = encoder.decode_share(encoded)
        assert decoded == test_data
        assert len(decoded) == 5  # Ensure leading zeros are preserved
    
    def test_invalid_characters(self, encoder):
        with pytest.raises(ValueError, match="Invalid character in share"):
            encoder.decode_share('Invalid{}Characters')
    
    def test_whitespace_handling(self, encoder):
        test_data = b'Test Data'
        encoded = encoder.encode_share(test_data)
        # Add random whitespace
        encoded_with_whitespace = ' '.join(encoded)
        decoded = encoder.decode_share(encoded_with_whitespace)
        assert decoded == test_data
    
    def test_format_share(self, encoder):
        test_data = b'TestFormatting'
        encoded = encoder.encode_share(test_data)
        formatted = encoder.format_share(encoded, group_size=4)
        # Check that formatting doesn't affect decoding
        decoded = encoder.decode_share(formatted)
        assert decoded == test_data
        # Check grouping
        assert all(len(group) <= 4 for group in formatted.split())
    
    def test_large_data(self, encoder):
        test_data = bytes(range(256))  # Create 256 bytes of sequential data
        encoded = encoder.encode_share(test_data)
        decoded = encoder.decode_share(encoded)
        assert decoded == test_data
    
    def test_backward_compatibility(self, encoder):
        # Test decoding without length prefix
        test_data = "ABC123"  # Direct share without length prefix
        decoded = encoder.decode_share(test_data)
        assert len(decoded) == 2  # Should use default length of 2
    
    def test_charset_uniqueness(self, encoder):
        # Verify all characters in charset are unique
        assert len(encoder.CHARSET) == len(set(encoder.CHARSET))
    
    @pytest.mark.parametrize("group_size", [2, 3, 4, 5])
    def test_different_group_sizes(self, encoder, group_size):
        test_data = b'TestGroupSizes'
        encoded = encoder.encode_share(test_data)
        formatted = encoder.format_share(encoded, group_size=group_size)
        # Verify most groups are of the specified size
        groups = formatted.split()
        # Last group might be shorter, so we check all but the last
        assert all(len(group) == group_size for group in groups[:-1])
        # Check that the formatted string still decodes correctly
        assert encoder.decode_share(formatted) == test_data

    def test_edge_cases(self, encoder):
        # Test single byte
        assert encoder.decode_share(encoder.encode_share(b'\x00')) == b'\x00'
        # Test max value byte
        assert encoder.decode_share(encoder.encode_share(b'\xff')) == b'\xff'
        # Test repeated bytes
        assert encoder.decode_share(encoder.encode_share(b'AAAA')) == b'AAAA'