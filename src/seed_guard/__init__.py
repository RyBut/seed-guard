from ._seed_guard_impl import SeedGuard as _SeedGuard

class SeedGuard:
    """
    SeedGuard provides secure splitting and sharing of cryptocurrency seed phrases.
    
    This class securely encodes a BIP39 seed phrase into a primary piece and multiple
    shares, where a specified threshold of shares is needed for reconstruction.
    
    Example:
        ```python
        from seed_guard import SeedGuard
        
        sg = SeedGuard()
        primary, shares = sg.encode_seed_phrase(
            seed_words=["abandon", "ability", ...],  # 12 or 24 BIP39 words
            shares_required=3,
            shares_total=5,
            password="optional-password"
        )
        
        # To recover the seed phrase
        recovered = sg.decode_shares(
            encoded_primary=primary,
            shares=shares[:3],  # Only 3 required as specified
            password="optional-password"  # Must match if used during encoding
        )
        ```
    """
    def __init__(self):
        self._impl = _SeedGuard()
        
    def encode_seed_phrase(self, seed_words, shares_required, shares_total, password=None):
        """
        Encodes a seed phrase into a primary piece and multiple shares.
        
        Args:
            seed_words (list): List of BIP39 seed words
            shares_required (int): Number of shares required for reconstruction
            shares_total (int): Total number of shares to generate
            password (str, optional): Optional password for additional encryption
            
        Returns:
            tuple: (encoded_primary, list_of_shares)
        """
        return self._impl.encode_seed_phrase(seed_words, shares_required, shares_total, password)
        
    def decode_shares(self, encoded_primary, shares, password=None):
        """
        Reconstructs the original seed phrase from the primary piece and shares.
        
        Args:
            encoded_primary (str): The encoded primary piece
            shares (list): List of shares (at least as many as required during encoding)
            password (str, optional): Password used during encoding if any
            
        Returns:
            list: The original seed words
        """
        return self._impl.decode_shares(encoded_primary, shares, password)

__all__ = ['SeedGuard']