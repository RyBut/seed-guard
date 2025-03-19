# SeedGuard

SeedGuard is a secure Python library for splitting and sharing cryptocurrency seed phrases using Shamir's Secret Sharing. It allows you to split your seed phrase into multiple shares, where only a specific threshold of those shares is needed to reconstruct the original phrase.

## Features

- Supports 12 and 24-word BIP39 seed phrases
- Implements Shamir's Secret Sharing for secure distribution
- Optional password encryption for additional security
- Compact encoding format for easy storage and transmission
- Simple, minimalist API with just two main methods

## Installation

```bash
pip install seed-guard
```

## Usage

### Splitting a Seed Phrase

```python
from seed_guard import SeedGuard

# Initialize SeedGuard
sg = SeedGuard()

# Your seed phrase (12 or 24 BIP39 words)
seed_phrase = [
    "abandon", "ability", "able", "about", "above", "absent",
    "absorb", "abstract", "absurd", "abuse", "access", "accident"
]

# Encode the seed phrase into shares
# - shares_required: How many shares are needed to recover (threshold)
# - shares_total: Total number of shares to generate
# - password: Optional for additional encryption
primary, shares = sg.encode_seed_phrase(
    seed_words=seed_phrase,
    shares_required=3,
    shares_total=5,
    password="optional-password"  # Optional
)

print(f"Primary piece: {primary}")
for i, share in enumerate(shares, 1):
    print(f"Share {i}: {share}")

# Store these shares separately in secure locations
# IMPORTANT: The primary piece must be stored separately from any shares
```

### Recovering a Seed Phrase

```python
from seed_guard import SeedGuard

# Initialize SeedGuard
sg = SeedGuard()

# The primary piece and at least 'shares_required' shares
primary_piece = "2:7fHs4ZpLKvQBD58XmnzhyfKk8Vy9jR2C3W6TgNJtPbrd"  # Example
collected_shares = [
    "2:hQxPvCkJRL54zSDtNnFM27YbgZ3j8VyKWXc9pBG6Ts",  # Example
    "2:ZPqD5F8KzJVX4gYmN6tnjRv2WTh7cCsLxb3SBpHM",    # Example
    "2:gBtDVKLM53zSrJP64NmfGZcXvkYF8h2T7sRHnWqj",    # Example
]

# Must provide at least 'shares_required' shares as defined when encoding
recovered_seed = sg.decode_shares(
    encoded_primary=primary_piece,
    shares=collected_shares,
    password="optional-password"  # Must match if used during encoding
)

print(f"Recovered seed phrase: {recovered_seed}")
```

## Security Recommendations

1. **Primary Piece Security**: The primary piece should be stored separately from any of the shares, ideally in a different location.

2. **Share Distribution**: Distribute shares to trusted individuals or store in different secure locations.

3. **Password Handling**: If using a password, ensure it's strong and don't store it with the shares.

4. **Minimum Shares**: The threshold (shares_required) should be set to balance security vs. recoverability. Setting it too low reduces security, while setting it too high might make recovery difficult if shares are lost.

5. **Testing Recovery**: Always test the recovery process with your actual shares before relying on them in a real scenario.

## Use Cases

- **Personal Backup**: Secure your own cryptocurrency seed phrases against loss while protecting against theft.
- **Inheritance Planning**: Distribute shares to family members or attorneys to ensure assets can be recovered in case of emergency.
- **Multi-signature Wallets**: Implement secure key sharing for multi-signature cryptocurrency wallets.
- **Business Key Management**: Implement secure key sharing for business cryptocurrency holdings.

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.