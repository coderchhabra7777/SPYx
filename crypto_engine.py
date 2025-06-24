"""
Advanced Cryptography Engine for StegoCrypt
Implements AES-256 encryption with PBKDF2 key derivation and optimized compression
"""

import os
import lzma
import zlib
import hashlib
from typing import Tuple, Optional
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad


class CryptoEngine:
    """Advanced cryptography engine with compression and encryption capabilities"""
    
    # Constants for optimization
    AES_KEY_SIZE = 32  # 256 bits
    IV_SIZE = 16       # 128 bits
    SALT_SIZE = 16     # 128 bits
    PBKDF2_ITERATIONS = 100000  # High security iterations
    CHUNK_SIZE = 8192  # Optimized chunk size for processing
    
    # Compression levels
    LZMA_PRESET = 6    # Balanced compression/speed
    ZLIB_LEVEL = 6     # Balanced compression/speed
    
    def __init__(self):
        """Initialize the crypto engine"""
        self.compression_stats = {
            'original_size': 0,
            'compressed_size': 0,
            'compression_ratio': 0.0
        }
    
    def compress_text(self, text: str, use_lzma: bool = True) -> bytes:
        """
        Compress text using LZMA or zlib with optimization
        
        Args:
            text: Input text to compress
            use_lzma: Use LZMA compression (better ratio) or zlib (faster)
            
        Returns:
            Compressed bytes
        """
        try:
            text_bytes = text.encode('utf-8')
            self.compression_stats['original_size'] = len(text_bytes)
            
            if use_lzma:
                # LZMA compression with optimized preset
                compressed = lzma.compress(
                    text_bytes, 
                    format=lzma.FORMAT_XZ,
                    preset=self.LZMA_PRESET
                )
                compression_type = b'LZMA'
            else:
                # zlib compression as fallback
                compressed = zlib.compress(text_bytes, level=self.ZLIB_LEVEL)
                compression_type = b'ZLIB'
            
            self.compression_stats['compressed_size'] = len(compressed)
            self.compression_stats['compression_ratio'] = (
                len(compressed) / len(text_bytes) if text_bytes else 1.0
            )
            
            # Prepend compression type for proper decompression
            return compression_type + compressed
            
        except Exception as e:
            raise RuntimeError(f"Compression failed: {str(e)}")
    
    def decompress_text(self, compressed_data: bytes) -> str:
        """
        Decompress text data
        
        Args:
            compressed_data: Compressed bytes with type header
            
        Returns:
            Original text string
        """
        try:
            if len(compressed_data) < 4:
                raise ValueError("Invalid compressed data format")
            
            # Extract compression type
            compression_type = compressed_data[:4]
            data = compressed_data[4:]
            
            if compression_type == b'LZMA':
                decompressed = lzma.decompress(data)
            elif compression_type == b'ZLIB':
                decompressed = zlib.decompress(data)
            else:
                raise ValueError(f"Unknown compression type: {compression_type}")
            
            return decompressed.decode('utf-8')
            
        except Exception as e:
            raise RuntimeError(f"Decompression failed: {str(e)}")
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive encryption key using PBKDF2 with SHA-256
        
        Args:
            password: User password
            salt: Random salt bytes
            
        Returns:
            Derived key bytes
        """
        from Crypto.Hash import SHA256
        return PBKDF2(
            password.encode('utf-8'),
            salt,
            dkLen=self.AES_KEY_SIZE,
            count=self.PBKDF2_ITERATIONS,
            hmac_hash_module=SHA256
        )
    
    def encrypt_data(self, data: bytes, password: str) -> bytes:
        """
        Encrypt data using AES-256-CBC with PBKDF2 key derivation
        
        Args:
            data: Data to encrypt
            password: Encryption password
            
        Returns:
            Encrypted data with salt and IV prepended
        """
        try:
            # Generate random salt and IV
            salt = get_random_bytes(self.SALT_SIZE)
            iv = get_random_bytes(self.IV_SIZE)
            
            # Derive key from password
            key = self._derive_key(password, salt)
            
            # Create cipher and encrypt
            cipher = AES.new(key, AES.MODE_CBC, iv)
            padded_data = pad(data, AES.block_size)
            encrypted_data = cipher.encrypt(padded_data)
            
            # Prepend salt and IV for decryption
            return salt + iv + encrypted_data
            
        except Exception as e:
            raise RuntimeError(f"Encryption failed: {str(e)}")
    
    def decrypt_data(self, encrypted_data: bytes, password: str) -> bytes:
        """
        Decrypt AES-256-CBC encrypted data
        
        Args:
            encrypted_data: Encrypted data with salt and IV
            password: Decryption password
            
        Returns:
            Original decrypted data
        """
        try:
            if len(encrypted_data) < self.SALT_SIZE + self.IV_SIZE:
                raise ValueError("Invalid encrypted data format")
            
            # Extract salt, IV, and encrypted data
            salt = encrypted_data[:self.SALT_SIZE]
            iv = encrypted_data[self.SALT_SIZE:self.SALT_SIZE + self.IV_SIZE]
            ciphertext = encrypted_data[self.SALT_SIZE + self.IV_SIZE:]
            
            # Derive key from password
            key = self._derive_key(password, salt)
            
            # Create cipher and decrypt
            cipher = AES.new(key, AES.MODE_CBC, iv)
            padded_data = cipher.decrypt(ciphertext)
            
            # Remove padding
            return unpad(padded_data, AES.block_size)
            
        except Exception as e:
            raise RuntimeError(f"Decryption failed: {str(e)}")
    
    def get_compression_stats(self) -> dict:
        """Get compression statistics"""
        return self.compression_stats.copy()
    
    def estimate_capacity(self, image_size: Tuple[int, int], channels: int = 3) -> int:
        """
        Estimate maximum data capacity for steganography
        
        Args:
            image_size: (width, height) of image
            channels: Number of color channels (3 for RGB, 4 for RGBA)
            
        Returns:
            Maximum bytes that can be hidden
        """
        width, height = image_size
        total_pixels = width * height
        
        # Use 1 bit per channel (LSB steganography)
        total_bits = total_pixels * channels
        
        # Reserve bits for data length header (32 bits)
        available_bits = total_bits - 32
        
        return available_bits // 8  # Convert to bytes
