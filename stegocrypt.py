"""
StegoCrypt - Main Integration Class
Combines cryptography and steganography engines for secure text hiding
"""

from PIL import Image
from typing import Tuple, Dict, Any, Optional
import time
import os

from crypto_engine import CryptoEngine
from steganography_engine import SteganographyEngine


class StegoCrypt:
    """Main StegoCrypt class integrating all functionality"""
    
    def __init__(self):
        """Initialize StegoCrypt with crypto and steganography engines"""
        self.crypto_engine = CryptoEngine()
        self.stego_engine = SteganographyEngine()
        self.operation_stats = {}
    
    def hide_text_in_image(
        self, 
        cover_image_path: str, 
        secret_text: str, 
        password: str,
        output_path: str,
        use_lzma: bool = True,
        optimize_image: bool = True
    ) -> Dict[str, Any]:
        """
        Complete workflow to hide text in an image
        
        Args:
            cover_image_path: Path to cover image
            secret_text: Text to hide
            password: Encryption password
            output_path: Path for output stego image
            use_lzma: Use LZMA compression (better ratio) vs zlib (faster)
            optimize_image: Optimize image for steganography
            
        Returns:
            Operation statistics and results
        """
        start_time = time.time()
        
        try:
            # Load and validate cover image
            if not os.path.exists(cover_image_path):
                raise FileNotFoundError(f"Cover image not found: {cover_image_path}")
            
            cover_image = Image.open(cover_image_path)
            original_format = cover_image.format
            
            # Optimize image if requested
            if optimize_image:
                cover_image = self.stego_engine.optimize_image_for_steganography(cover_image)
            
            # Check capacity before processing
            capacity = self.stego_engine.calculate_capacity(cover_image)
            
            # Step 1: Compress text
            print("Compressing text...")
            compressed_data = self.crypto_engine.compress_text(secret_text, use_lzma)
            compression_stats = self.crypto_engine.get_compression_stats()
            
            # Step 2: Encrypt compressed data
            print("Encrypting data...")
            encrypted_data = self.crypto_engine.encrypt_data(compressed_data, password)
            
            # Check if encrypted data fits in image
            if len(encrypted_data) > capacity:
                raise ValueError(
                    f"Encrypted data ({len(encrypted_data)} bytes) exceeds image capacity "
                    f"({capacity} bytes). Use a larger image or shorter text."
                )
            
            # Step 3: Hide encrypted data in image
            print("Embedding data in image...")
            stego_image = self.stego_engine.hide_data_in_image(cover_image, encrypted_data)
            
            # Step 4: Save stego image
            # Ensure output format supports lossless compression
            if output_path.lower().endswith(('.jpg', '.jpeg')):
                output_path = output_path.rsplit('.', 1)[0] + '.png'
                print("Warning: Changed output format to PNG for lossless compression")
            
            stego_image.save(output_path, format='PNG', optimize=True)
            
            # Calculate statistics
            end_time = time.time()
            embedding_stats = self.stego_engine.get_embedding_stats()
            
            self.operation_stats = {
                'operation': 'hide',
                'success': True,
                'processing_time': end_time - start_time,
                'original_text_length': len(secret_text),
                'compression_stats': compression_stats,
                'encrypted_data_size': len(encrypted_data),
                'image_capacity': capacity,
                'embedding_stats': embedding_stats,
                'cover_image_size': cover_image.size,
                'output_path': output_path,
                'compression_type': 'LZMA' if use_lzma else 'zlib'
            }
            
            print(f"✅ Text successfully hidden in image!")
            print(f"📁 Output saved to: {output_path}")
            print(f"📊 Compression ratio: {compression_stats['compression_ratio']:.2%}")
            print(f"📈 Image utilization: {embedding_stats['utilization_percent']:.2f}%")
            
            return self.operation_stats
            
        except Exception as e:
            self.operation_stats = {
                'operation': 'hide',
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
            raise RuntimeError(f"Failed to hide text: {str(e)}")
    
    def extract_text_from_image(
        self, 
        stego_image_path: str, 
        password: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Complete workflow to extract text from a stego image
        
        Args:
            stego_image_path: Path to stego image
            password: Decryption password
            
        Returns:
            (extracted_text, operation_statistics)
        """
        start_time = time.time()
        
        try:
            # Load stego image
            if not os.path.exists(stego_image_path):
                raise FileNotFoundError(f"Stego image not found: {stego_image_path}")
            
            stego_image = Image.open(stego_image_path)
            
            # Step 1: Extract encrypted data from image
            print("Extracting data from image...")
            encrypted_data = self.stego_engine.extract_data_from_image(stego_image)
            
            # Step 2: Decrypt data
            print("Decrypting data...")
            compressed_data = self.crypto_engine.decrypt_data(encrypted_data, password)
            
            # Step 3: Decompress text
            print("Decompressing text...")
            extracted_text = self.crypto_engine.decompress_text(compressed_data)
            
            # Calculate statistics
            end_time = time.time()
            
            self.operation_stats = {
                'operation': 'extract',
                'success': True,
                'processing_time': end_time - start_time,
                'extracted_text_length': len(extracted_text),
                'encrypted_data_size': len(encrypted_data),
                'stego_image_size': stego_image.size,
                'stego_image_path': stego_image_path
            }
            
            print(f"✅ Text successfully extracted from image!")
            print(f"📝 Extracted text length: {len(extracted_text)} characters")
            
            return extracted_text, self.operation_stats
            
        except Exception as e:
            self.operation_stats = {
                'operation': 'extract',
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
            raise RuntimeError(f"Failed to extract text: {str(e)}")
    
    def analyze_image_capacity(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze an image's steganography capacity
        
        Args:
            image_path: Path to image file
            
        Returns:
            Capacity analysis results
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            image = Image.open(image_path)
            
            # Calculate capacity
            capacity = self.stego_engine.calculate_capacity(image)
            
            # Estimate text capacity (accounting for compression and encryption overhead)
            # Typical overhead: ~30% for encryption + headers, compression saves ~50-70%
            estimated_text_capacity = int(capacity * 0.7 * 2)  # Conservative estimate
            
            analysis = {
                'image_path': image_path,
                'image_size': image.size,
                'image_mode': image.mode,
                'image_format': image.format,
                'total_pixels': image.size[0] * image.size[1],
                'color_channels': len(image.getbands()),
                'raw_capacity_bytes': capacity,
                'estimated_text_capacity_chars': estimated_text_capacity,
                'recommended_max_text_length': estimated_text_capacity // 2  # Very safe estimate
            }
            
            return analysis
            
        except Exception as e:
            raise RuntimeError(f"Failed to analyze image: {str(e)}")
    
    def create_test_image(
        self, 
        output_path: str, 
        size: Tuple[int, int] = (800, 600)
    ) -> str:
        """
        Create a test image suitable for steganography
        
        Args:
            output_path: Path for output test image
            size: Image dimensions (width, height)
            
        Returns:
            Path to created test image
        """
        try:
            test_image = self.stego_engine.create_test_image(size)
            test_image.save(output_path, format='PNG')
            
            print(f"✅ Test image created: {output_path}")
            print(f"📏 Size: {size[0]}x{size[1]} pixels")
            
            # Analyze capacity
            analysis = self.analyze_image_capacity(output_path)
            print(f"📊 Estimated text capacity: ~{analysis['estimated_text_capacity_chars']} characters")
            
            return output_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to create test image: {str(e)}")
    
    def get_last_operation_stats(self) -> Dict[str, Any]:
        """Get statistics from the last operation"""
        return self.operation_stats.copy()
    
    def validate_setup(self) -> Dict[str, bool]:
        """
        Validate that all components are working correctly
        
        Returns:
            Validation results for each component
        """
        results = {
            'crypto_engine': False,
            'steganography_engine': False,
            'integration': False
        }
        
        try:
            # Test crypto engine
            test_text = "Hello, StegoCrypt!"
            test_password = "test123"
            
            compressed = self.crypto_engine.compress_text(test_text)
            encrypted = self.crypto_engine.encrypt_data(compressed, test_password)
            decrypted = self.crypto_engine.decrypt_data(encrypted, test_password)
            decompressed = self.crypto_engine.decompress_text(decrypted)
            
            if decompressed == test_text:
                results['crypto_engine'] = True
            
            # Test steganography engine
            test_image = self.stego_engine.create_test_image((100, 100))
            test_data = b"test data"
            
            stego_image = self.stego_engine.hide_data_in_image(test_image, test_data)
            extracted_data = self.stego_engine.extract_data_from_image(stego_image)
            
            if extracted_data == test_data:
                results['steganography_engine'] = True
            
            # Test integration
            if results['crypto_engine'] and results['steganography_engine']:
                results['integration'] = True
            
        except Exception as e:
            print(f"Validation error: {str(e)}")
        
        return results


# Convenience functions for direct usage
def hide_text(cover_image_path: str, secret_text: str, password: str, output_path: str) -> Dict[str, Any]:
    """Convenience function to hide text in image"""
    stegocrypt = StegoCrypt()
    return stegocrypt.hide_text_in_image(cover_image_path, secret_text, password, output_path)


def extract_text(stego_image_path: str, password: str) -> str:
    """Convenience function to extract text from image"""
    stegocrypt = StegoCrypt()
    text, _ = stegocrypt.extract_text_from_image(stego_image_path, password)
    return text


def analyze_capacity(image_path: str) -> Dict[str, Any]:
    """Convenience function to analyze image capacity"""
    stegocrypt = StegoCrypt()
    return stegocrypt.analyze_image_capacity(image_path)
