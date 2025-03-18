import os
from typing import List, Tuple

class BIP39Shamir:
    # Prime fields for different secret sizes
    PRIME_FIELDS = [
        (1, 257),
        (2, 65537),
        (3, 16777259),
        (4, 4294967311),
        (5, 1099511627791),
        (6, 281474976710677),
        (7, 72057594037928017),
        (8, 18446744073709551629),
        (9, 4722366482869645213711),
        (10, 1208925819614629174706189),
        (11, 309485009821345068724781063),
        (12, 79228162514264337593543950397),
        (13, 20282409603651670423947251286127),
        (14, 5192296858534827628530496329220121),
        (15, 1329227995784915872903807060280345027),
        (16, 340282366920938463463374607431768211507),  # For secrets up to 16 bytes
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
        # Use coefficient size based on secret size
        coeff_bytes = max(len(secret_int.to_bytes((secret_int.bit_length() + 7) // 8, 'big')), 4)
        for _ in range(threshold - 1):
            coeff.append(int.from_bytes(os.urandom(coeff_bytes), 'big') % prime)
        return coeff

    def _evaluate_polynomial(self, coefficients: List[int], x: int, prime: int) -> int:
        result = 0
        for coeff in reversed(coefficients):
            result = (result * x + coeff) % prime
        return result

    def _generate_unique_x_coordinates(self, count: int) -> List[int]:
        """Generate 'count' unique random x-coordinates between 1 and 255"""
        if count > 255:
            raise ValueError("Cannot generate more than 255 unique x-coordinates")
        # Create a set of random values until we have enough unique ones
        x_coords = set()
        while len(x_coords) < count:
            x = int.from_bytes(os.urandom(1), 'big')
            if x != 0:  # Exclude 0
                x_coords.add(x)
        return sorted(list(x_coords))  # Sort for deterministic ordering

    def split(self, secret: bytes, shares: int, threshold: int) -> List[bytes]:
        if threshold > shares:
            raise ValueError("Threshold cannot be greater than total shares")
        if threshold < 2:
            raise ValueError("Threshold must be at least 2")
        if shares > 255:
            raise ValueError("Maximum 255 shares supported")
        if threshold > 255:
            raise ValueError("Maximum threshold of 255 supported")

        # Get appropriate prime field
        field_index, prime = self._get_prime_field(secret)
        
        # Convert secret to integer
        secret_int = int.from_bytes(secret, 'big')
        if secret_int >= prime:
            raise ValueError("Secret too large for field size")

        # Generate polynomial coefficients
        coefficients = self._generate_polynomial(secret_int, threshold, prime)
        
        # Generate random x-coordinates
        x_coordinates = self._generate_unique_x_coordinates(shares)
        
        # Generate shares
        share_points = []
        for x in x_coordinates:
            y = self._evaluate_polynomial(coefficients, x, prime)
            # Format: field_index (1 byte) || threshold (1 byte) || x (1 byte) || y (variable)
            share_bytes = bytes([field_index, threshold, x]) + \
                         y.to_bytes((y.bit_length() + 7) // 8, 'big')
            share_points.append(share_bytes)

        return share_points

    def combine(self, shares: List[bytes]) -> bytes:
        if not shares:
            raise ValueError("No shares provided")

        # Extract field index and threshold from first share
        if len(shares[0]) < 3:  # Minimum share length: field_index + threshold + x
            raise ValueError("Invalid share format")
            
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
            if len(share) < 3:
                raise ValueError("Invalid share format")
            
            share_field_index = share[0]
            share_threshold = share[1]
            
            if share_field_index != field_index:
                raise ValueError("Shares from different field sizes")
            if share_threshold != threshold:
                raise ValueError("Shares from different threshold schemes")
            
            x = share[2]
            y = int.from_bytes(share[3:], 'big')
            points.append((x, y))

        # Lagrange interpolation
        secret = 0
        for i, (xi, yi) in enumerate(points[:threshold]):  # Only use required number of shares
            numerator = denominator = 1
            for j, (xj, _) in enumerate(points[:threshold]):
                if i == j:
                    continue
                numerator = (numerator * -xj) % prime
                denominator = (denominator * (xi - xj)) % prime
            
            factor = (numerator * pow(denominator, -1, prime)) % prime
            secret = (secret + yi * factor) % prime

        # Convert back to bytes
        return secret.to_bytes((secret.bit_length() + 7) // 8, 'big')