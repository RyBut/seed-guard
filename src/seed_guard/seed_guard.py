from typing import List, Optional
from .bip39 import BIP39
from .bip39_compression import BIP39Compression
from .bip39_encryptor import BIP39Encryptor
from .bip39_shamir import BIP39Shamir
from .share_encoder import ShareEncoder

class SeedGuard:
    def __init__(self):
        self.bip39 = BIP39()
        self.compressor = BIP39Compression()
        self.encryptor = BIP39Encryptor()
        self.shamir = BIP39Shamir()
        self.encoder = ShareEncoder()

    def encode_seed_phrase(
        self, 
        seed_words: List[str], 
        shares_required: int, 
        shares_total: int,
        password: Optional[str] = None
    ) -> List[str]:
        """
        Convert a seed phrase into encoded shares.

        Args:
            seed_words: List of 12 or 24 BIP39 words
            shares_required: Number of shares required to reconstruct (threshold)
            shares_total: Total number of shares to generate
            password: Optional encryption password

        Returns:
            List of encoded shares as strings

        Raises:
            ValueError: If inputs are invalid
        """
        # Validate and convert seed phrase to indices
        indices = self.bip39.words_to_indices(seed_words)

        # Compress the indices
        compressed = self.compressor.compress(indices)

        # Encrypt if password provided
        data_to_split = self.encryptor.encrypt(compressed, password)

        # Split into shares
        shares = self.shamir.split(data_to_split, shares_total, shares_required)

        # Encode shares
        return [self.encoder.encode_share(share) for share in shares]

    def decode_shares(
        self, 
        shares: List[str],
        password: Optional[str] = None
    ) -> List[str]:
        """
        Reconstruct seed phrase from shares.

        Args:
            shares: List of encoded shares
            password: Optional decryption password (must match encoding password)

        Returns:
            List of BIP39 words

        Raises:
            ValueError: If shares are invalid or insufficient
        """
        # Decode shares from string format
        decoded_shares = [self.encoder.decode_share(share) for share in shares]

        # Combine shares
        combined = self.shamir.combine(decoded_shares)

        # Decrypt if password provided
        data_to_decompress = self.encryptor.decrypt(combined, password)

        # Decompress to indices
        indices = self.compressor.decompress(data_to_decompress)

        # Convert indices back to words
        return self.bip39.indices_to_words(indices)