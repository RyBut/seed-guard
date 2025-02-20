class ShareEncoder:
    CHARSET = "23456789ABCDEFGHJKLMNPQRTUXYabcdefhjkmnprtuy!@#$%^&*_-+=';<,>.?/|"
    
    def __init__(self):
        self.REVERSE_LOOKUP = {char: idx for idx, char in enumerate(self.CHARSET)}
        
    def encode_share(self, data: bytes) -> str:
        if not data:
            raise ValueError("Empty input")
            
        base = len(self.CHARSET)
        result = []
        
        # Ensure we maintain leading zeros by encoding the length
        length = len(data)
        value = int.from_bytes(data, byteorder='big')
        
        # Encode both length and value
        while value > 0 or len(result) < 1:
            value, remainder = divmod(value, base)
            result.append(self.CHARSET[remainder])
            
        # Add length marker
        length_chars = []
        while length > 0 or len(length_chars) < 1:
            length, remainder = divmod(length, base)
            length_chars.append(self.CHARSET[remainder])
            
        # Combine length and data with a separator
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
            
        # Decode value
        value = 0
        for char in data_part.strip():
            if char in [' ', '\n', '\t']:  # Skip whitespace in formatted shares
                continue
            if char not in self.REVERSE_LOOKUP:
                raise ValueError("Invalid character in share")
            value = value * base + self.REVERSE_LOOKUP[char]
            
        # Convert to bytes with the correct length
        return value.to_bytes(length, byteorder='big', signed=False)
        
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