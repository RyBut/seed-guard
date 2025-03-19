class SecretSplitter:
    def __init__(self, split_ratio=0.95):
        if not 0 < split_ratio < 1:
            raise ValueError("Split ratio must be between 0 and 1")
        self.split_ratio = split_ratio

    def split(self, secret: bytes) -> tuple[bytes, bytes]:
        if not secret:
            raise ValueError("Empty input")
            
        total_length = len(secret)
        split_point = round(total_length * self.split_ratio)
        
        if split_point >= total_length:
            split_point = total_length - 1
        elif split_point <= 0:
            split_point = 1
            
        primary = secret[:split_point]
        secondary = secret[split_point:]
        
        return primary, secondary

    def combine(self, primary: bytes, secondary: bytes) -> bytes:
        """
        Combine the two pieces back into the original secret
        """
        if not primary or not secondary:
            raise ValueError("Both pieces required")
        return primary + secondary

    def get_split_lengths(self, total_length: int) -> tuple[int, int]:
        split_point = round(total_length * self.split_ratio)
        
        if split_point >= total_length:
            split_point = total_length - 1
        elif split_point <= 0:
            split_point = 1
            
        return split_point, total_length - split_point