import os
from typing import List, Tuple

class BIP39Shamir:
    # Prime fields for different secret sizes
    PRIME_FIELDS = [
        (16, 2**127 - 1),      # For secrets up to 16 bytes
        (32, 2**255 - 19),     # For secrets up to 32 bytes
        (64, 2**511 - 187),    # For secrets up to 64 bytes
        (128, 2**1023 - 357)   # For secrets up to 128 bytes
    ]

    def _get_prime_field(self, secret: bytes) -> Tuple[int, int]:
        """Returns (field_index, prime) based on secret size"""
        secret_size = len(secret)
        for i, (max_bytes, prime) in enumerate(self.PRIME_FIELDS):
            if secret_size <= max_bytes:
                return i, prime
        raise ValueError("Secret too large")

    def _generate_polynomial(self, secret_int: int, threshold: int, prime: int) -> List[int]:
        coeff = [secret_int]
        for _ in range(threshold - 1):
            coeff.append(int.from_bytes(os.urandom(24), 'big') % prime)
        return coeff

    def _evaluate_polynomial(self, coefficients: List[int], x: int, prime: int) -> int:
        result = 0
        for coeff in reversed(coefficients):
            result = (result * x + coeff) % prime
        return result

    def split(self, secret: bytes, shares: int, threshold: int) -> List[bytes]:
        if threshold > shares:
            raise ValueError("Threshold cannot be greater than total shares")
        if threshold < 2:
            raise ValueError("Threshold must be at least 2")

        # Get appropriate prime field
        field_index, prime = self._get_prime_field(secret)
        
        # Convert secret to integer
        secret_int = int.from_bytes(secret, 'big')
        if secret_int >= prime:
            raise ValueError("Secret too large for field size")

        # Generate polynomial coefficients
        coefficients = self._generate_polynomial(secret_int, threshold, prime)
        
        # Generate shares
        share_points = []
        for i in range(1, shares + 1):
            y = self._evaluate_polynomial(coefficients, i, prime)
            # Pack field_index, threshold, x, y into share
            # Format: field_index (1 byte) || threshold (1 byte) || x (4 bytes) || y (variable)
            share_bytes = bytes([field_index, threshold]) + \
                         i.to_bytes(4, 'big') + \
                         y.to_bytes((y.bit_length() + 7) // 8, 'big')
            share_points.append(share_bytes)

        return share_points

    def combine(self, shares: List[bytes]) -> bytes:
        if not shares:
            raise ValueError("No shares provided")

        # Extract field index and threshold from first share
        field_index = shares[0][0]
        threshold = shares[0][1]
        
        if len(shares) < threshold:
            raise ValueError(f"Insufficient shares: need at least {threshold}")

        if field_index >= len(self.PRIME_FIELDS):
            raise ValueError("Invalid field index")
        
        prime = self.PRIME_FIELDS[field_index][1]
        
        # Process shares
        points = []
        for share in shares:
            if len(share) < 6:  # 1 (field_index) + 1 (threshold) + 4 (x coordinate)
                raise ValueError("Invalid share format")
            
            share_field_index = share[0]
            share_threshold = share[1]
            
            if share_field_index != field_index:
                raise ValueError("Shares from different field sizes")
            if share_threshold != threshold:
                raise ValueError("Shares from different threshold schemes")
            
            x = int.from_bytes(share[2:6], 'big')
            y = int.from_bytes(share[6:], 'big')
            points.append((x, y))

        # Lagrange interpolation
        secret = 0
        for i, (xi, yi) in enumerate(points):
            numerator = denominator = 1
            for j, (xj, _) in enumerate(points):
                if i == j:
                    continue
                numerator = (numerator * -xj) % prime
                denominator = (denominator * (xi - xj)) % prime
            
            factor = (numerator * pow(denominator, -1, prime)) % prime
            secret = (secret + yi * factor) % prime

        # Convert back to bytes
        return secret.to_bytes((secret.bit_length() + 7) // 8, 'big')