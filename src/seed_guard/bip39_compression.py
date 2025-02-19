import math
from typing import List

class BIP39Compression:
    BITS_PER_INDEX = 11
    MAX_INDEX_VALUE = 2047
    
    def _calculate_last_byte_bits(self, num_indices: int) -> int:
        """Calculate how many bits are used in the last byte"""
        total_bits = num_indices * self.BITS_PER_INDEX
        return ((total_bits - 1) % 8) + 1

    def _pack_bits(self, data: bytearray, value: int, start_bit: int, num_bits: int) -> None:
        """Pack bits into a byte array at the specified position"""
        for i in range(num_bits):
            # Get the byte index and bit position within that byte
            byte_index = (start_bit + i) // 8
            bit_index = 7 - ((start_bit + i) % 8)  # MSB first
            
            # Set or clear the bit
            if value & (1 << (num_bits - 1 - i)):
                data[byte_index] |= (1 << bit_index)
            else:
                data[byte_index] &= ~(1 << bit_index)

    def _unpack_bits(self, data: bytes, start_bit: int, num_bits: int) -> int:
        """Unpack bits from a byte array at the specified position"""
        result = 0
        
        for i in range(num_bits):
            # Get the byte index and bit position within that byte
            byte_index = (start_bit + i) // 8
            bit_index = 7 - ((start_bit + i) % 8)  # MSB first
            
            # Extract the bit and add it to result
            if data[byte_index] & (1 << bit_index):
                result |= (1 << (num_bits - 1 - i))
                
        return result

    def compress(self, indices: List[int]) -> bytes:
        """Compress indices - unused bits in last byte will be 0"""
        # Validate indices
        for i, index in enumerate(indices):
            if not 0 <= index <= self.MAX_INDEX_VALUE:
                raise ValueError(
                    f"Invalid index at position {i + 1}: {index}. "
                    f"Must be between 0 and {self.MAX_INDEX_VALUE}"
                )

        total_bits = len(indices) * self.BITS_PER_INDEX
        num_bytes = math.ceil(total_bits / 8)
        
        result = bytearray(num_bytes)
        bit_position = 0
        
        for index in indices:
            self._pack_bits(result, index, bit_position, self.BITS_PER_INDEX)
            bit_position += self.BITS_PER_INDEX
            
        return bytes(result)

    def decompress(self, data: bytes) -> List[int]:
        """
        Decompress bytes back into indices by detecting number of indices
        from bit pattern in last byte
        """
        if not data:
            raise ValueError("Empty data")

        # Try each possible number of indices until we find one that matches
        # the bit pattern in the last byte
        total_bytes = len(data)
        last_byte = data[-1]
        
        # Try possible numbers of indices
        for num_indices in range(1, 256):  # reasonable upper limit
            total_bits = num_indices * self.BITS_PER_INDEX
            expected_bytes = math.ceil(total_bits / 8)
            
            if expected_bytes != total_bytes:
                continue
                
            last_byte_bits = self._calculate_last_byte_bits(num_indices)
            unused_bits = 8 - last_byte_bits
            
            # Check if unused bits are all 0
            last_byte_mask = (0xff >> unused_bits) << unused_bits
            if (last_byte & ~last_byte_mask) == 0:
                # Found matching pattern, decompress this many indices
                indices = []
                bit_position = 0
                
                for _ in range(num_indices):
                    index = self._unpack_bits(data, bit_position, self.BITS_PER_INDEX)
                    indices.append(index)
                    bit_position += self.BITS_PER_INDEX
                    
                return indices
                
        raise ValueError("Could not determine number of indices from data")