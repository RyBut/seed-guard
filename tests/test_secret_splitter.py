import pytest
from seed_guard.secret_splitter import SecretSplitter

class TestSecretSplitter:
    def test_init_valid_ratio(self):
        splitter = SecretSplitter(0.8)
        assert splitter.split_ratio == 0.8

    def test_init_invalid_ratio(self):
        with pytest.raises(ValueError):
            SecretSplitter(0)
        with pytest.raises(ValueError):
            SecretSplitter(1)
        with pytest.raises(ValueError):
            SecretSplitter(-0.5)
        with pytest.raises(ValueError):
            SecretSplitter(1.5)

    def test_split_empty_input(self):
        splitter = SecretSplitter()
        with pytest.raises(ValueError):
            splitter.split(b'')

    def test_split_and_combine(self):
        test_data = [
            b'Hello World',
            b'\x00\x01\x02\x03\x04\x05',
            b'\x86c\x1d\x8c\xfc\xe1|XnaE',
            b'a' * 1000  # Test with larger data
        ]
        
        splitter = SecretSplitter(0.8)
        for data in test_data:
            primary, secondary = splitter.split(data)
            # Test pieces are not empty
            assert len(primary) > 0
            assert len(secondary) > 0
            # Test combined data matches original
            combined = splitter.combine(primary, secondary)
            assert combined == data
            # Test lengths match expected
            p_len, s_len = splitter.get_split_lengths(len(data))
            assert len(primary) == p_len
            assert len(secondary) == s_len

    def test_split_ratio_boundaries(self):
        small_data = b'ab'  # Minimum size to split
        splitter = SecretSplitter(0.8)
        primary, secondary = splitter.split(small_data)
        assert len(primary) == 1
        assert len(secondary) == 1

    def test_combine_empty_pieces(self):
        splitter = SecretSplitter()
        with pytest.raises(ValueError):
            splitter.combine(b'', b'data')
        with pytest.raises(ValueError):
            splitter.combine(b'data', b'')
        with pytest.raises(ValueError):
            splitter.combine(b'', b'')

    def test_get_split_lengths(self):
        splitter = SecretSplitter(0.8)
        test_lengths = [2, 5, 10, 100]
        
        for length in test_lengths:
            p_len, s_len = splitter.get_split_lengths(length)
            # Test lengths add up to total
            assert p_len + s_len == length
            # Test primary is larger (for 0.8 ratio), except for length=2
            if length > 2:
                assert p_len > s_len
            else:
                assert p_len == s_len == 1
            # Test both pieces have at least 1 byte
            assert p_len >= 1
            assert s_len >= 1