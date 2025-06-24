"""
Advanced Steganography Engine for StegoCrypt
Implements optimized LSB steganography with error detection and capacity management
"""

import numpy as np
from PIL import Image
from typing import Tuple, Optional
import struct
import hashlib


class SteganographyEngine:
    """Advanced steganography engine with LSB embedding and optimization"""
    
    # Constants for optimization
    HEADER_SIZE = 8  # 4 bytes for data length + 4 bytes for checksum
    MAX_CHANNELS = 4  # RGBA
    SUPPORTED_FORMATS = {'PNG', 'BMP', 'TIFF'}
    
    def __init__(self):
        """Initialize the steganography engine"""
        self.last_capacity = 0
        self.last_used_bits = 0
    
    def _calculate_checksum(self, data: bytes) -> bytes:
        """Calculate SHA-256 checksum for data integrity"""
        return hashlib.sha256(data).digest()[:4]  # Use first 4 bytes
    
    def _validate_image(self, image: Image.Image) -> Tuple[bool, str]:
        """
        Validate image for steganography compatibility
        
        Args:
            image: PIL Image object
            
        Returns:
            (is_valid, error_message)
        """
        # For programmatically created images, format might be None
        if image.format is not None and image.format not in self.SUPPORTED_FORMATS:
            return False, f"Unsupported format: {image.format}. Use PNG, BMP, or TIFF"
        
        if image.mode not in ['RGB', 'RGBA', 'L']:
            return False, f"Unsupported color mode: {image.mode}. Use RGB, RGBA, or L"
        
        width, height = image.size
        if width < 10 or height < 10:
            return False, "Image too small for steganography"
        
        return True, ""
    
    def calculate_capacity(self, image: Image.Image) -> int:
        """
        Calculate maximum data capacity for the image
        
        Args:
            image: PIL Image object
            
        Returns:
            Maximum bytes that can be hidden
        """
        width, height = image.size
        channels = len(image.getbands())
        
        total_pixels = width * height
        total_bits = total_pixels * channels
        
        # Reserve bits for header (data length + checksum)
        header_bits = self.HEADER_SIZE * 8
        available_bits = total_bits - header_bits
        
        self.last_capacity = available_bits // 8
        return self.last_capacity
    
    def hide_data_in_image(self, image: Image.Image, data: bytes) -> Image.Image:
        """
        Hide data in image using optimized LSB steganography
        
        Args:
            image: Cover image
            data: Data to hide
            
        Returns:
            Stego image with hidden data
        """
        # Validate image
        is_valid, error_msg = self._validate_image(image)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Check capacity
        capacity = self.calculate_capacity(image)
        if len(data) > capacity:
            raise ValueError(
                f"Data too large: {len(data)} bytes > {capacity} bytes capacity"
            )
        
        # Calculate checksum for integrity
        checksum = self._calculate_checksum(data)
        
        # Prepare header: data length (4 bytes) + checksum (4 bytes)
        header = struct.pack('<I', len(data)) + checksum
        full_data = header + data
        
        # Convert image to numpy array for efficient processing
        img_array = np.array(image)
        original_shape = img_array.shape
        
        # Flatten array for easier bit manipulation
        flat_array = img_array.flatten()
        
        # Convert data to binary string
        binary_data = ''.join(format(byte, '08b') for byte in full_data)
        data_length = len(binary_data)
        
        # Embed data using LSB
        for i in range(data_length):
            # Get the bit to embed
            bit = int(binary_data[i])
            
            # Modify LSB of current pixel value
            flat_array[i] = (flat_array[i] & 0xFE) | bit
        
        # Reshape back to original image shape
        modified_array = flat_array.reshape(original_shape)
        
        # Create new image
        stego_image = Image.fromarray(modified_array, mode=image.mode)
        
        self.last_used_bits = data_length
        return stego_image
    
    def extract_data_from_image(self, image: Image.Image) -> bytes:
        """
        Extract hidden data from stego image
        
        Args:
            image: Stego image containing hidden data
            
        Returns:
            Extracted data bytes
        """
        # Validate image
        is_valid, error_msg = self._validate_image(image)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Convert image to numpy array
        img_array = np.array(image)
        flat_array = img_array.flatten()
        
        # Extract header first (8 bytes = 64 bits)
        header_bits = []
        for i in range(self.HEADER_SIZE * 8):
            if i >= len(flat_array):
                raise ValueError("Image too small to contain valid header")
            header_bits.append(str(flat_array[i] & 1))
        
        # Convert header bits to bytes
        header_binary = ''.join(header_bits)
        header_bytes = bytes(
            int(header_binary[i:i+8], 2) 
            for i in range(0, len(header_binary), 8)
        )
        
        # Parse header
        data_length = struct.unpack('<I', header_bytes[:4])[0]
        expected_checksum = header_bytes[4:8]
        
        # Validate data length
        max_capacity = self.calculate_capacity(image)
        if data_length > max_capacity:
            raise ValueError(f"Invalid data length: {data_length} > {max_capacity}")
        
        # Extract data bits
        data_bits = []
        start_bit = self.HEADER_SIZE * 8
        end_bit = start_bit + (data_length * 8)
        
        for i in range(start_bit, end_bit):
            if i >= len(flat_array):
                raise ValueError("Unexpected end of image data")
            data_bits.append(str(flat_array[i] & 1))
        
        # Convert data bits to bytes
        if len(data_bits) % 8 != 0:
            raise ValueError("Invalid data bit length")
        
        data_binary = ''.join(data_bits)
        extracted_data = bytes(
            int(data_binary[i:i+8], 2) 
            for i in range(0, len(data_binary), 8)
        )
        
        # Verify checksum
        actual_checksum = self._calculate_checksum(extracted_data)
        if actual_checksum != expected_checksum:
            raise ValueError("Data integrity check failed - corrupted or wrong password")
        
        return extracted_data
    
    def get_embedding_stats(self) -> dict:
        """Get statistics about the last embedding operation"""
        return {
            'capacity_bytes': self.last_capacity,
            'used_bits': self.last_used_bits,
            'utilization_percent': (self.last_used_bits / (self.last_capacity * 8) * 100) 
                                 if self.last_capacity > 0 else 0
        }
    
    def optimize_image_for_steganography(self, image: Image.Image) -> Image.Image:
        """
        Optimize image for better steganography results
        
        Args:
            image: Input image
            
        Returns:
            Optimized image
        """
        # Convert to RGB if needed (removes alpha channel complications)
        if image.mode == 'RGBA':
            # Create white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])  # Use alpha as mask
            image = background
        elif image.mode not in ['RGB', 'L']:
            image = image.convert('RGB')
        
        # Ensure image is large enough for meaningful steganography
        min_size = 100
        width, height = image.size
        if width < min_size or height < min_size:
            # Resize maintaining aspect ratio
            ratio = max(min_size / width, min_size / height)
            new_size = (int(width * ratio), int(height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        return image
    
    def create_test_image(self, size: Tuple[int, int] = (512, 512)) -> Image.Image:
        """
        Create a test image suitable for steganography
        
        Args:
            size: Image dimensions (width, height)
            
        Returns:
            Test image
        """
        # Create a gradient image with some texture
        width, height = size
        img_array = np.zeros((height, width, 3), dtype=np.uint8)
        
        for y in range(height):
            for x in range(width):
                # Create a gradient with some noise
                r = int((x / width) * 255)
                g = int((y / height) * 255)
                b = int(((x + y) / (width + height)) * 255)
                
                # Add some texture
                noise = np.random.randint(-10, 11)
                r = max(0, min(255, r + noise))
                g = max(0, min(255, g + noise))
                b = max(0, min(255, b + noise))
                
                img_array[y, x] = [r, g, b]
        
        return Image.fromarray(img_array, 'RGB')
