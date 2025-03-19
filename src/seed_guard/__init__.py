# src/seed_guard/__init__.py
from .seed_guard import SeedGuard as _SeedGuard

class SeedGuard(_SeedGuard):
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
    pass

__all__ = ['SeedGuard']