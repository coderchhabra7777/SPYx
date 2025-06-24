"""
StegoCrypt Command Line Interface
Advanced CLI for steganography operations with comprehensive features
"""

import argparse
import sys
import os
from pathlib import Path
import json
from typing import Optional

from stegocrypt import StegoCrypt, hide_text, extract_text, analyze_capacity


def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                        StegoCrypt v1.0                      ║
║              Secure Text Hiding System                      ║
║                                                              ║
║  Advanced steganography with AES-256 encryption             ║
║  LZMA compression and LSB embedding                          ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")


def print_error(message: str):
    """Print error message"""
    print(f"❌ Error: {message}")


def print_info(message: str):
    """Print info message"""
    print(f"ℹ️  {message}")


def print_stats(stats: dict):
    """Print operation statistics"""
    print("\n📊 Operation Statistics:")
    print("=" * 50)
    
    if 'compression_stats' in stats:
        comp_stats = stats['compression_stats']
        print(f"Original text size: {comp_stats['original_size']:,} bytes")
        print(f"Compressed size: {comp_stats['compressed_size']:,} bytes")
        print(f"Compression ratio: {comp_stats['compression_ratio']:.2%}")
    
    if 'encrypted_data_size' in stats:
        print(f"Encrypted data size: {stats['encrypted_data_size']:,} bytes")
    
    if 'embedding_stats' in stats:
        embed_stats = stats['embedding_stats']
        print(f"Image capacity: {embed_stats['capacity_bytes']:,} bytes")
        print(f"Image utilization: {embed_stats['utilization_percent']:.2f}%")
    
    if 'processing_time' in stats:
        print(f"Processing time: {stats['processing_time']:.2f} seconds")


def cmd_hide(args):
    """Handle hide command"""
    try:
        # Validate inputs
        if not os.path.exists(args.cover_image):
            print_error(f"Cover image not found: {args.cover_image}")
            return 1
        
        if args.text_file:
            if not os.path.exists(args.text_file):
                print_error(f"Text file not found: {args.text_file}")
                return 1
            with open(args.text_file, 'r', encoding='utf-8') as f:
                secret_text = f.read()
        else:
            secret_text = args.text
        
        if not secret_text:
            print_error("No text provided to hide")
            return 1
        
        # Get password
        if args.password:
            password = args.password
        else:
            import getpass
            password = getpass.getpass("Enter encryption password: ")
        
        if not password:
            print_error("Password is required")
            return 1
        
        print_info(f"Hiding {len(secret_text)} characters in {args.cover_image}")
        
        # Perform hiding operation
        stegocrypt = StegoCrypt()
        stats = stegocrypt.hide_text_in_image(
            args.cover_image,
            secret_text,
            password,
            args.output,
            use_lzma=not args.use_zlib,
            optimize_image=not args.no_optimize
        )
        
        print_success(f"Text hidden successfully in {args.output}")
        
        if args.verbose:
            print_stats(stats)
        
        return 0
        
    except Exception as e:
        print_error(str(e))
        return 1


def cmd_extract(args):
    """Handle extract command"""
    try:
        # Validate inputs
        if not os.path.exists(args.stego_image):
            print_error(f"Stego image not found: {args.stego_image}")
            return 1
        
        # Get password
        if args.password:
            password = args.password
        else:
            import getpass
            password = getpass.getpass("Enter decryption password: ")
        
        if not password:
            print_error("Password is required")
            return 1
        
        print_info(f"Extracting text from {args.stego_image}")
        
        # Perform extraction
        stegocrypt = StegoCrypt()
        extracted_text, stats = stegocrypt.extract_text_from_image(
            args.stego_image,
            password
        )
        
        # Output text
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            print_success(f"Extracted text saved to {args.output}")
        else:
            print("\n📝 Extracted Text:")
            print("=" * 50)
            print(extracted_text)
        
        if args.verbose:
            print_stats(stats)
        
        return 0
        
    except Exception as e:
        print_error(str(e))
        return 1


def cmd_analyze(args):
    """Handle analyze command"""
    try:
        if not os.path.exists(args.image):
            print_error(f"Image not found: {args.image}")
            return 1
        
        print_info(f"Analyzing capacity of {args.image}")
        
        stegocrypt = StegoCrypt()
        analysis = stegocrypt.analyze_image_capacity(args.image)
        
        print("\n📊 Image Analysis Results:")
        print("=" * 50)
        print(f"File: {analysis['image_path']}")
        print(f"Dimensions: {analysis['image_size'][0]} x {analysis['image_size'][1]} pixels")
        print(f"Format: {analysis['image_format']}")
        print(f"Color Mode: {analysis['image_mode']}")
        print(f"Channels: {analysis['color_channels']}")
        print(f"Total Pixels: {analysis['total_pixels']:,}")
        print()
        print("Steganography Capacity:")
        print(f"  Raw Capacity: {analysis['raw_capacity_bytes']:,} bytes")
        print(f"  Estimated Text Capacity: ~{analysis['estimated_text_capacity_chars']:,} characters")
        print(f"  Recommended Max: ~{analysis['recommended_max_text_length']:,} characters")
        
        if args.json:
            json_output = json.dumps(analysis, indent=2)
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(json_output)
                print_success(f"Analysis saved to {args.output}")
            else:
                print("\n📄 JSON Output:")
                print(json_output)
        
        return 0
        
    except Exception as e:
        print_error(str(e))
        return 1


def cmd_validate(args):
    """Handle validate command"""
    try:
        print_info("Running system validation...")
        
        stegocrypt = StegoCrypt()
        results = stegocrypt.validate_setup()
        
        print("\n🔍 System Validation Results:")
        print("=" * 40)
        
        for component, status in results.items():
            status_icon = "✅" if status else "❌"
            component_name = component.replace('_', ' ').title()
            print(f"{status_icon} {component_name}: {'PASS' if status else 'FAIL'}")
        
        overall_status = all(results.values())
        print(f"\n🎯 Overall Status: {'✅ ALL SYSTEMS OPERATIONAL' if overall_status else '❌ ISSUES DETECTED'}")
        
        if args.verbose:
            print("\nTest Details:")
            print("- Crypto Engine: AES-256 encryption/decryption with compression")
            print("- Steganography Engine: LSB embedding and extraction")
            print("- Integration: End-to-end workflow validation")
        
        return 0 if overall_status else 1
        
    except Exception as e:
        print_error(str(e))
        return 1


def cmd_demo(args):
    """Handle demo command"""
    try:
        print_info("Running StegoCrypt demonstration...")
        
        stegocrypt = StegoCrypt()
        
        # Create test image
        test_image_path = "demo_test_image.png"
        print_info(f"Creating test image: {test_image_path}")
        stegocrypt.create_test_image(test_image_path, (800, 600))
        
        # Demo text
        demo_text = """This is a demonstration of StegoCrypt!

StegoCrypt is an advanced steganography system that combines:
• AES-256 encryption for security
• LZMA compression for efficiency  
• LSB steganography for concealment
• Modern GUI and CLI interfaces

This text is hidden inside an image using advanced cryptographic techniques.
The image looks completely normal, but contains this secret message!

Features demonstrated:
- Secure encryption with PBKDF2 key derivation
- Efficient compression reducing data size
- Invisible embedding in image pixels
- Data integrity verification
- Cross-platform compatibility

StegoCrypt - Where security meets steganography! 🔐"""
        
        demo_password = "demo123"
        stego_image_path = "demo_stego_image.png"
        
        # Hide text
        print_info("Hiding demo text in image...")
        hide_stats = stegocrypt.hide_text_in_image(
            test_image_path,
            demo_text,
            demo_password,
            stego_image_path
        )
        
        print_success("Demo text hidden successfully!")
        print_stats(hide_stats)
        
        # Extract text
        print_info("Extracting text from stego image...")
        extracted_text, extract_stats = stegocrypt.extract_text_from_image(
            stego_image_path,
            demo_password
        )
        
        print_success("Demo text extracted successfully!")
        
        # Verify
        if extracted_text == demo_text:
            print_success("✅ Verification passed - extracted text matches original!")
        else:
            print_error("❌ Verification failed - text mismatch!")
            return 1
        
        print("\n📝 Extracted Demo Text:")
        print("=" * 50)
        print(extracted_text)
        
        # Cleanup
        if not args.keep_files:
            try:
                os.remove(test_image_path)
                os.remove(stego_image_path)
                print_info("Demo files cleaned up")
            except:
                pass
        else:
            print_info(f"Demo files kept: {test_image_path}, {stego_image_path}")
        
        return 0
        
    except Exception as e:
        print_error(str(e))
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="StegoCrypt - Advanced Steganography System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s hide -c cover.png -t "Secret message" -o stego.png
  %(prog)s hide -c cover.png -f secret.txt -o stego.png -p mypassword
  %(prog)s extract -s stego.png -o extracted.txt
  %(prog)s analyze -i image.png
  %(prog)s validate
  %(prog)s demo
        """
    )
    
    parser.add_argument('--version', action='version', version='StegoCrypt 1.0.0')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Hide command
    hide_parser = subparsers.add_parser('hide', help='Hide text in image')
    hide_parser.add_argument('-c', '--cover-image', required=True, help='Cover image path')
    hide_parser.add_argument('-t', '--text', help='Text to hide')
    hide_parser.add_argument('-f', '--text-file', help='File containing text to hide')
    hide_parser.add_argument('-o', '--output', required=True, help='Output stego image path')
    hide_parser.add_argument('-p', '--password', help='Encryption password (will prompt if not provided)')
    hide_parser.add_argument('--use-zlib', action='store_true', help='Use zlib instead of LZMA compression')
    hide_parser.add_argument('--no-optimize', action='store_true', help='Skip image optimization')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract text from stego image')
    extract_parser.add_argument('-s', '--stego-image', required=True, help='Stego image path')
    extract_parser.add_argument('-o', '--output', help='Output text file (prints to console if not provided)')
    extract_parser.add_argument('-p', '--password', help='Decryption password (will prompt if not provided)')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze image capacity')
    analyze_parser.add_argument('-i', '--image', required=True, help='Image to analyze')
    analyze_parser.add_argument('-o', '--output', help='Output file for results')
    analyze_parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate system setup')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run demonstration')
    demo_parser.add_argument('--keep-files', action='store_true', help='Keep demo files after completion')
    
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == 'hide':
        return cmd_hide(args)
    elif args.command == 'extract':
        return cmd_extract(args)
    elif args.command == 'analyze':
        return cmd_analyze(args)
    elif args.command == 'validate':
        return cmd_validate(args)
    elif args.command == 'demo':
        return cmd_demo(args)
    else:
        print_error(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
