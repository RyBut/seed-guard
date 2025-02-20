import pytest
from seed_guard.share_encoder import ShareEncoder

@pytest.fixture
def encoder():
    return ShareEncoder()

def test_basic_encoding_decoding(encoder):
    test_bytes = b'\x00\x03\x00\x00\x00\x01\x7f'
    encoded = encoder.encode_share(test_bytes)
    decoded = encoder.decode_share(encoded)
    assert test_bytes == decoded

def test_zero_bytes(encoder):
    test_bytes = b'\x00\x00\x00\x00'
    encoded = encoder.encode_share(test_bytes)
    decoded = encoder.decode_share(encoded)
    assert test_bytes == decoded

def test_formatting(encoder):
    test_bytes = b'\x01\x02\x03\x04\x05'
    encoded = encoder.encode_share(test_bytes)
    formatted = encoder.format_share(encoded, group_size=4)
    
    print(f"Encoded: {encoded}")
    print(f"Formatted: {formatted}")
    
    # Split into prefix and data parts
    prefix, data = formatted.split(':')
    # Only check the groups in the data part
    groups = data.split()
    
    print("Groups and their lengths:")
    for group in groups:
        print(f"{group}: {len(group)}")

    # Check that formatting doesn't affect decoding
    decoded_plain = encoder.decode_share(encoded)
    decoded_formatted = encoder.decode_share(formatted)
    assert decoded_plain == decoded_formatted
    
    # Verify group size
    assert all(len(group) <= 4 for group in groups)

def test_charset_validity(encoder):
    # Test that all characters in charset are unique
    assert len(encoder.CHARSET) == len(set(encoder.CHARSET))
    
    # Test that reverse lookup matches charset
    for idx, char in enumerate(encoder.CHARSET):
        assert encoder.REVERSE_LOOKUP[char] == idx

def test_large_input(encoder):
    test_bytes = bytes(range(32))  # 32 bytes of sequential data
    encoded = encoder.encode_share(test_bytes)
    decoded = encoder.decode_share(encoded)
    assert test_bytes == decoded

def test_invalid_input(encoder):
    with pytest.raises(ValueError):
        encoder.decode_share("Invalid&Characters")

def test_empty_input(encoder):
    with pytest.raises(ValueError):
        encoder.encode_share(b'')
    
    with pytest.raises(ValueError):
        encoder.decode_share('')