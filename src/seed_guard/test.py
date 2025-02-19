import hashlib
import os
import zlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from typing import List, Tuple

class PasswordProtectedSeedObfuscator:
    PRIME = 2**192 - 4595
    
    # Base91 alphabet - efficiently encodes binary data to printable ASCII
    BASE91_CHARS = ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
                   "0123456789!#$%&()*+,./:;<=>?@[]^_`{|}~'\"")
    
    def _to_base91(self, data: bytes) -> str:
        """Convert bytes to base91 string"""
        value = int.from_bytes(data, 'big')
        result = ""
        while value:
            value, rem = divmod(value, 91)
            result = self.BASE91_CHARS[rem] + result
        return result or "0"
    
    def _from_base91(self, encoded: str) -> bytes:
        """Convert base91 string back to bytes"""
        value = 0
        for char in encoded:
            value = value * 91 + self.BASE91_CHARS.index(char)
        return value.to_bytes((value.bit_length() + 7) // 8, 'big')
    
    def __init__(self, threshold: int, total_shares: int):
        self.threshold = threshold
        self.total_shares = total_shares
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def _encrypt_secret(self, secret: bytes, password: str) -> tuple[bytes, bytes]:
        salt = os.urandom(16)
        key = self._derive_key(password, salt)
        f = Fernet(key)
        encrypted = f.encrypt(secret)
        return encrypted, salt
    
    def _decrypt_secret(self, encrypted: bytes, password: str, salt: bytes) -> bytes:
        key = self._derive_key(password, salt)
        f = Fernet(key)
        return f.decrypt(encrypted)
    
    def _generate_polynomial(self, secret: int, degree: int) -> List[int]:
        coeff = [secret]
        for _ in range(degree):
            coeff.append(int.from_bytes(os.urandom(24), 'big') % self.PRIME)
        return coeff
    
    def _evaluate_polynomial(self, coefficients: List[int], x: int) -> int:
        result = 0
        for coeff in reversed(coefficients):
            result = (result * x + coeff) % self.PRIME
        return result
    
    def generate_shares(self, seed_phrase: str, password: str) -> List[str]:
        # Compress seed phrase
        compressed = zlib.compress(seed_phrase.encode(), level=9)
        
        # Encrypt compressed data
        encrypted, salt = self._encrypt_secret(compressed, password)
        
        # Convert to number for sharing
        secret = int.from_bytes(encrypted, 'big') % self.PRIME
        
        # Generate polynomial coefficients
        coefficients = self._generate_polynomial(secret, self.threshold - 1)
        
        # Generate shares
        shares = []
        for i in range(1, self.total_shares + 1):
            y = self._evaluate_polynomial(coefficients, i)
            # Pack x and y efficiently
            combined = (i << 192) | y
            # Calculate required bytes dynamically
            bytes_needed = (combined.bit_length() + 7) // 8
            share_bytes = combined.to_bytes(bytes_needed, 'big')
            # Include salt with share
            share_with_salt = salt + share_bytes
            # Convert to base91
            shares.append(self._to_base91(share_with_salt))
            
        return shares
    
    def reconstruct_secret(self, shares: List[str], password: str) -> str:
        if len(shares) < self.threshold:
            raise ValueError(f"Need at least {self.threshold} shares")
        
        # Extract salt from first share
        first_share_bytes = self._from_base91(shares[0])
        salt = first_share_bytes[:16]
        
        # Process shares
        points = []
        for share in shares[:self.threshold]:
            share_bytes = self._from_base91(share)[16:]  # Skip salt
            combined = int.from_bytes(share_bytes, 'big')
            x = combined >> 192
            y = combined & ((1 << 192) - 1)
            points.append((x, y))
        
        # Reconstruct encrypted secret
        secret = 0
        for i, (xi, yi) in enumerate(points):
            numerator = denominator = 1
            for j, (xj, _) in enumerate(points):
                if i == j:
                    continue
                numerator = (numerator * -xj) % self.PRIME
                denominator = (denominator * (xi - xj)) % self.PRIME
            
            factor = (numerator * pow(denominator, -1, self.PRIME)) % self.PRIME
            secret = (secret + yi * factor) % self.PRIME
        
        # Convert back to encrypted bytes
        encrypted = secret.to_bytes((secret.bit_length() + 7) // 8, 'big')
        
        # Decrypt and decompress
        try:
            decrypted = self._decrypt_secret(encrypted, password, salt)
            return zlib.decompress(decrypted).decode()
        except Exception:
            raise ValueError("Invalid password or corrupted shares")

# Example usage
if __name__ == "__main__":
    seed = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
    password = "my_secure_password"
    
    obfuscator = PasswordProtectedSeedObfuscator(threshold=3, total_shares=5)
    
    shares = obfuscator.generate_shares(seed, password)
    print("Generated shares:")
    for i, share in enumerate(shares, 1):
        print(f"Share {i}: {share}")
    
    reconstructed = obfuscator.reconstruct_secret(shares[:3], password)
    print("\nReconstructed seed phrase:", reconstructed)
    print("Success:", seed == reconstructed)
    
    # Test wrong password
    try:
        reconstructed = obfuscator.reconstruct_secret(shares[:3], "wrong_password")
    except ValueError as e:
        print("\nWith wrong password:", e)