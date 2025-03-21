from typing import List, Optional, Tuple
from ._bip39 import BIP39
from ._bip39_compression import BIP39Compression
from ._bip39_encryptor import BIP39Encryptor
from ._bip39_shamir import BIP39Shamir
from ._share_encoder import ShareEncoder
from ._secret_splitter import SecretSplitter

class SeedGuard:
    def __init__(self):
        self._bip39 = BIP39()
        self._compressor = BIP39Compression()
        self._encryptor = BIP39Encryptor()
        self._shamir = BIP39Shamir()
        self._encoder = ShareEncoder()
        self._splitter = SecretSplitter(split_ratio=0.9)

    def encode_seed_phrase(
        self, 
        seed_words: List[str], 
        shares_required: int, 
        shares_total: int,
        password: Optional[str] = None
    ) -> Tuple[str, List[str]]:
        """
        Convert a seed phrase into an encoded primary piece and encoded shares.

        Args:
            seed_words: List of 12 or 24 BIP39 words
            shares_required: Number of shares required to reconstruct (threshold)
            shares_total: Total number of shares to generate
            password: Optional encryption password

        Returns:
            Tuple containing:
                - Primary piece as encoded string
                - List of encoded shares as strings

        Raises:
            ValueError: If inputs are invalid
        """
        # Validate and convert seed phrase to indices
        indices = self._bip39.words_to_indices(seed_words)

        # Compress the indices
        compressed = self._compressor.compress(indices)

        # Encrypt
        encrypted = self._encryptor.encrypt(compressed, password)

        # Split into primary and secondary pieces
        primary, secondary = self._splitter.split(encrypted)

        # Encode primary piece
        encoded_primary = self._encoder.encode_share(primary)

        # Split secondary piece into shares
        shares = self._shamir.split(secondary, shares_total, shares_required)

        # Encode shares
        encoded_shares = [self._encoder.encode_share(share) for share in shares]

        return encoded_primary, encoded_shares

    def decode_shares(
        self, 
        encoded_primary: str,
        shares: List[str],
        password: Optional[str] = None
    ) -> List[str]:
        """
        Reconstruct seed phrase from encoded primary piece and shares.

        Args:
            encoded_primary: Primary piece as encoded string
            shares: List of encoded shares
            password: Optional decryption password (must match encoding password)

        Returns:
            List of BIP39 words

        Raises:
            ValueError: If shares are invalid or insufficient
        """
        # Decode primary piece
        primary = self._encoder.decode_share(encoded_primary)

        # Decode shares from string format
        decoded_shares = [self._encoder.decode_share(share) for share in shares]

        # Combine shares to get secondary piece
        secondary = self._shamir.combine(decoded_shares)

        # Combine primary and secondary pieces
        combined = self._splitter.combine(primary, secondary)

        # Decrypt if password provided
        decrypted = self._encryptor.decrypt(combined, password)

        # Decompress to indices
        indices = self._compressor.decompress(decrypted)

        # Convert indices back to words
        return self._bip39.indices_to_words(indices)