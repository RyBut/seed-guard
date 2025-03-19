class ShareEncoder:
    CHARSET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    
    def __init__(self):
        self.REVERSE_LOOKUP = {char: idx for idx, char in enumerate(self.CHARSET)}
        
    def encode_share(self, data: bytes) -> str:
        if not data:
            raise ValueError("Empty input")
            
        base = len(self.CHARSET)
        # Convert length to share format
        length = len(data)
        length_chars = []
        temp_length = length
        while temp_length > 0 or len(length_chars) < 1:
            temp_length, remainder = divmod(temp_length, base)
            length_chars.append(self.CHARSET[remainder])
            
        # Convert data to share format in chunks to avoid overflow
        result = []
        value = int.from_bytes(data, byteorder='big')
        while value > 0 or len(result) < 1:
            value, remainder = divmod(value, base)
            result.append(self.CHARSET[remainder])
            
        return ''.join(reversed(length_chars)) + ':' + ''.join(reversed(result))
        
    def decode_share(self, share: str) -> bytes:
        if not share:
            raise ValueError("Empty input")
            
        # Split length and data
        try:
            length_part, data_part = share.split(':')
        except ValueError:
            length_part = '2'  # Default length for backward compatibility
            data_part = share
            
        base = len(self.CHARSET)
        
        # Decode length
        length = 0
        for char in length_part.strip():
            if char not in self.REVERSE_LOOKUP:
                raise ValueError("Invalid character in share")
            length = length * base + self.REVERSE_LOOKUP[char]
            
        # Decode value in chunks to avoid overflow
        value = 0
        for char in data_part.strip():
            if char in [' ', '\n', '\t']:  # Skip whitespace in formatted shares
                continue
            if char not in self.REVERSE_LOOKUP:
                raise ValueError("Invalid character in share")
            try:
                value = value * base + self.REVERSE_LOOKUP[char]
            except OverflowError:
                raise ValueError("Share value too large to decode")
                
        try:
            return value.to_bytes(length, byteorder='big', signed=False)
        except OverflowError:
            raise ValueError("Share value too large to decode")
        
    def format_share(self, share: str, group_size: int = 4) -> str:
        """Format the share string into groups for better readability"""
        if ':' not in share:
            return ' '.join(share[i:i+group_size] for i in range(0, len(share), group_size))
            
        # Split into prefix and data
        prefix, data = share.split(':')
        
        # Format data part into groups
        formatted_data = ' '.join(data[i:i+group_size] for i in range(0, len(data), group_size))
        
        # Combine with prefix
        return prefix + ':' + formatted_data