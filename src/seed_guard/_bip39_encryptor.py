from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
from typing import Tuple, Optional

class BIP39Encryptor:
    NONCE_SIZE = 12  # Standard for AES-GCM
    SALT_SIZE = 16   # Standard size for PBKDF2
    KEY_SIZE = 32    # Using AES-256
    DEFAULT_PASSWORD = "default-secure-password-123"  # Added default password
    
    def derive_key(self, password: Optional[str] = None, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """Derive encryption key from password using PBKDF2"""
        if salt is None:
            salt = os.urandom(self.SALT_SIZE)
            
        # Use default password if none provided
        actual_password = password if password is not None else self.DEFAULT_PASSWORD
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            iterations=100000,  # OWASP recommended minimum
        )
        key = kdf.derive(actual_password.encode())
        return key, salt

    def encrypt(self, data: bytes, password: Optional[str] = None) -> bytes:
        """
        Encrypt data using AES-GCM with password
        Returns: salt + nonce + ciphertext + tag
        """
        # Generate salt and derive key
        key, salt = self.derive_key(password)
        
        # Create cipher and nonce
        aesgcm = AESGCM(key)
        nonce = os.urandom(self.NONCE_SIZE)
        
        # Encrypt data
        ciphertext = aesgcm.encrypt(nonce, data, None)  # None = no associated data
        
        # Combine salt + nonce + ciphertext (includes tag)
        return salt + nonce + ciphertext

    def decrypt(self, encrypted_data: bytes, password: Optional[str] = None) -> bytes:
        """
        Decrypt data using AES-GCM with password
        Input format: salt + nonce + ciphertext + tag
        """
        # Extract salt, nonce, and ciphertext
        salt = encrypted_data[:self.SALT_SIZE]
        nonce = encrypted_data[self.SALT_SIZE:self.SALT_SIZE + self.NONCE_SIZE]
        ciphertext = encrypted_data[self.SALT_SIZE + self.NONCE_SIZE:]
        
        # Derive key and decrypt
        key, _ = self.derive_key(password, salt)
        aesgcm = AESGCM(key)
        
        return aesgcm.decrypt(nonce, ciphertext, None)  # None = no associated data