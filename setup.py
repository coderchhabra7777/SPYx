"""
StegoCrypt Setup Script
Automated setup and validation for the StegoCrypt system
"""

import subprocess
import sys
import os
from pathlib import Path


def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_step(step: str):
    """Print a step indicator"""
    print(f"\n🔧 {step}...")


def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")


def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")


def check_python_version():
    """Check if Python version is compatible"""
    print_step("Checking Python version")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print_error(f"Python 3.10+ required, found {version.major}.{version.minor}")
        return False
    
    print_success(f"Python {version.major}.{version.minor}.{version.micro} ✓")
    return True


def install_dependencies():
    """Install required dependencies"""
    print_step("Installing dependencies")
    
    try:
        # Check if requirements.txt exists
        if not Path("requirements.txt").exists():
            print_error("requirements.txt not found")
            return False
        
        # Install dependencies
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print_error(f"Failed to install dependencies: {result.stderr}")
            return False
        
        print_success("Dependencies installed successfully")
        return True
        
    except Exception as e:
        print_error(f"Error installing dependencies: {str(e)}")
        return False


def validate_installation():
    """Validate the installation"""
    print_step("Validating installation")
    
    try:
        # Try importing main modules
        from stegocrypt import StegoCrypt
        from crypto_engine import CryptoEngine
        from steganography_engine import SteganographyEngine
        
        print_success("All modules imported successfully")
        
        # Run system validation
        stego = StegoCrypt()
        results = stego.validate_setup()
        
        all_passed = True
        for component, status in results.items():
            component_name = component.replace('_', ' ').title()
            if status:
                print_success(f"{component_name} validation passed")
            else:
                print_error(f"{component_name} validation failed")
                all_passed = False
        
        return all_passed
        
    except ImportError as e:
        print_error(f"Import error: {str(e)}")
        return False
    except Exception as e:
        print_error(f"Validation error: {str(e)}")
        return False


def run_demo():
    """Run a quick demonstration"""
    print_step("Running demonstration")
    
    try:
        from stegocrypt import StegoCrypt
        
        stego = StegoCrypt()
        
        # Create test image
        test_image = "setup_test_image.png"
        stego.create_test_image(test_image, (400, 300))
        print_success("Test image created")
        
        # Test hide/extract cycle
        test_text = "StegoCrypt setup test - Hello World! 🔐"
        test_password = "setup_test_123"
        stego_image = "setup_stego_image.png"
        
        # Hide text
        stats = stego.hide_text_in_image(
            test_image,
            test_text,
            test_password,
            stego_image
        )
        print_success("Text hidden successfully")
        
        # Extract text
        extracted_text, _ = stego.extract_text_from_image(
            stego_image,
            test_password
        )
        
        # Verify
        if extracted_text == test_text:
            print_success("Text extraction verified ✓")
        else:
            print_error("Text extraction verification failed")
            return False
        
        # Cleanup
        try:
            os.remove(test_image)
            os.remove(stego_image)
            print_success("Test files cleaned up")
        except:
            pass
        
        return True
        
    except Exception as e:
        print_error(f"Demo failed: {str(e)}")
        return False


def create_shortcuts():
    """Create convenient shortcuts"""
    print_step("Creating shortcuts")
    
    try:
        # Create launcher scripts
        if os.name == 'nt':  # Windows
            # Create batch files
            with open("stegocrypt-gui.bat", "w") as f:
                f.write(f"@echo off\n")
                f.write(f"cd /d \"{os.getcwd()}\"\n")
                f.write(f"python gui.py\n")
                f.write(f"pause\n")
            
            with open("stegocrypt-cli.bat", "w") as f:
                f.write(f"@echo off\n")
                f.write(f"cd /d \"{os.getcwd()}\"\n")
                f.write(f"python cli.py %*\n")
            
            print_success("Windows batch files created")
            
        else:  # Unix-like systems
            # Create shell scripts
            with open("stegocrypt-gui.sh", "w") as f:
                f.write(f"#!/bin/bash\n")
                f.write(f"cd \"{os.getcwd()}\"\n")
                f.write(f"python3 gui.py\n")
            
            with open("stegocrypt-cli.sh", "w") as f:
                f.write(f"#!/bin/bash\n")
                f.write(f"cd \"{os.getcwd()}\"\n")
                f.write(f"python3 cli.py \"$@\"\n")
            
            # Make executable
            os.chmod("stegocrypt-gui.sh", 0o755)
            os.chmod("stegocrypt-cli.sh", 0o755)
            
            print_success("Shell scripts created")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to create shortcuts: {str(e)}")
        return False


def print_usage_info():
    """Print usage information"""
    print_header("🎉 Setup Complete!")
    
    print("\n📚 Quick Start Guide:")
    print("=" * 30)
    
    print("\n🖥️  GUI Application:")
    if os.name == 'nt':
        print("   Double-click: stegocrypt-gui.bat")
    else:
        print("   Run: ./stegocrypt-gui.sh")
    print("   Or: python gui.py")
    
    print("\n💻 Command Line:")
    if os.name == 'nt':
        print("   stegocrypt-cli.bat <command>")
    else:
        print("   ./stegocrypt-cli.sh <command>")
    print("   Or: python cli.py <command>")
    
    print("\n🔧 Available CLI Commands:")
    print("   validate  - Validate system setup")
    print("   demo      - Run demonstration")
    print("   hide      - Hide text in image")
    print("   extract   - Extract text from image")
    print("   analyze   - Analyze image capacity")
    
    print("\n📖 Examples:")
    print("   python cli.py demo")
    print("   python cli.py hide -c cover.png -t \"Secret\" -o stego.png")
    print("   python cli.py extract -s stego.png")
    print("   python cli.py analyze -i image.png")
    
    print("\n📄 Documentation:")
    print("   README.md - Complete documentation")
    print("   python cli.py --help - CLI help")
    
    print("\n🔐 StegoCrypt is ready to use!")
    print("   Secure • Efficient • User-friendly")


def main():
    """Main setup function"""
    print_header("🔐 StegoCrypt Setup")
    print("Advanced Steganography System")
    print("Setting up your secure text hiding environment...")
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Install dependencies
    if success and not install_dependencies():
        success = False
    
    # Validate installation
    if success and not validate_installation():
        success = False
    
    # Run demo
    if success and not run_demo():
        success = False
    
    # Create shortcuts
    if success:
        create_shortcuts()  # Non-critical, don't fail setup
    
    if success:
        print_usage_info()
        return 0
    else:
        print_header("❌ Setup Failed")
        print("\nPlease check the errors above and try again.")
        print("For help, visit: https://github.com/your-username/stegocrypt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
