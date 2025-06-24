"""
StegoCrypt GUI - Modern Tkinter Interface
Professional GUI with advanced features and optimizations
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import threading
import os
from typing import Optional, Dict, Any
import json

from stegocrypt import StegoCrypt


class ModernStyle:
    """Modern color scheme and styling constants"""
    
    # Color palette
    PRIMARY = "#2C3E50"      # Dark blue-gray
    SECONDARY = "#3498DB"    # Blue
    SUCCESS = "#27AE60"      # Green
    WARNING = "#F39C12"      # Orange
    DANGER = "#E74C3C"       # Red
    LIGHT = "#ECF0F1"        # Light gray
    DARK = "#34495E"         # Dark gray
    WHITE = "#FFFFFF"
    
    # Fonts
    FONT_LARGE = ("Segoe UI", 14, "bold")
    FONT_MEDIUM = ("Segoe UI", 11)
    FONT_SMALL = ("Segoe UI", 9)
    FONT_MONO = ("Consolas", 10)


class ProgressDialog:
    """Custom progress dialog for long operations"""
    
    def __init__(self, parent, title="Processing..."):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.dialog, 
            mode='indeterminate',
            length=350
        )
        self.progress.pack(pady=20)
        
        # Status label
        self.status_label = tk.Label(
            self.dialog,
            text="Initializing...",
            font=ModernStyle.FONT_MEDIUM
        )
        self.status_label.pack(pady=10)
        
        # Cancel button
        self.cancel_button = ttk.Button(
            self.dialog,
            text="Cancel",
            command=self.cancel
        )
        self.cancel_button.pack(pady=10)
        
        self.cancelled = False
        self.progress.start(10)
    
    def update_status(self, status: str):
        """Update the status message"""
        self.status_label.config(text=status)
        self.dialog.update()
    
    def cancel(self):
        """Cancel the operation"""
        self.cancelled = True
        self.close()
    
    def close(self):
        """Close the dialog"""
        self.progress.stop()
        self.dialog.destroy()


class ImagePreview:
    """Image preview widget with zoom and pan capabilities"""
    
    def __init__(self, parent, width=300, height=200):
        self.frame = tk.Frame(parent, bg=ModernStyle.LIGHT, relief="sunken", bd=2)
        self.canvas = tk.Canvas(
            self.frame, 
            width=width, 
            height=height,
            bg=ModernStyle.WHITE,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        self.image = None
        self.photo = None
        self.scale = 1.0
        
        # Bind mouse events for zoom
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
    
    def load_image(self, image_path: str):
        """Load and display an image"""
        try:
            self.image = Image.open(image_path)
            self.display_image()
        except Exception as e:
            self.canvas.delete("all")
            self.canvas.create_text(
                150, 100,
                text=f"Error loading image:\n{str(e)}",
                fill=ModernStyle.DANGER,
                font=ModernStyle.FONT_SMALL,
                justify="center"
            )
    
    def display_image(self):
        """Display the image on canvas"""
        if not self.image:
            return
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            self.canvas.after(100, self.display_image)
            return
        
        # Calculate scale to fit image in canvas
        img_width, img_height = self.image.size
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        self.scale = min(scale_x, scale_y, 1.0)  # Don't upscale
        
        # Resize image
        new_width = int(img_width * self.scale)
        new_height = int(img_height * self.scale)
        
        resized_image = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(resized_image)
        
        # Clear canvas and display image
        self.canvas.delete("all")
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        self.canvas.create_image(x, y, anchor="nw", image=self.photo)
    
    def on_click(self, event):
        """Handle mouse click"""
        pass
    
    def on_mousewheel(self, event):
        """Handle mouse wheel for zoom"""
        pass
    
    def clear(self):
        """Clear the preview"""
        self.canvas.delete("all")
        self.image = None
        self.photo = None


class StegoCryptGUI:
    """Main GUI application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("StegoCrypt - Secure Text Hiding System")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Initialize StegoCrypt engine
        self.stegocrypt = StegoCrypt()
        
        # GUI state
        self.current_cover_image = None
        self.current_stego_image = None
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        self.setup_layout()
        
        # Validate setup on startup
        self.root.after(1000, self.validate_setup)
    
    def setup_styles(self):
        """Configure modern styling"""
        style = ttk.Style()
        
        # Configure notebook style
        style.configure(
            "Modern.TNotebook",
            background=ModernStyle.LIGHT,
            borderwidth=0
        )
        style.configure(
            "Modern.TNotebook.Tab",
            padding=[20, 10],
            font=ModernStyle.FONT_MEDIUM
        )
        
        # Configure button styles
        style.configure(
            "Primary.TButton",
            font=ModernStyle.FONT_MEDIUM,
            padding=[10, 5]
        )
        style.configure(
            "Success.TButton",
            font=ModernStyle.FONT_MEDIUM,
            padding=[10, 5]
        )
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root, style="Modern.TNotebook")
        
        # Create tabs
        self.create_hide_tab()
        self.create_extract_tab()
        self.create_analyze_tab()
        self.create_settings_tab()
        
        # Status bar
        self.status_bar = tk.Frame(self.root, bg=ModernStyle.PRIMARY, height=30)
        self.status_label = tk.Label(
            self.status_bar,
            text="Ready",
            bg=ModernStyle.PRIMARY,
            fg=ModernStyle.WHITE,
            font=ModernStyle.FONT_SMALL,
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5)
    
    def create_hide_tab(self):
        """Create the hide text tab"""
        self.hide_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.hide_frame, text="Hide Text")
        
        # Main container with padding
        main_container = tk.Frame(self.hide_frame, bg=ModernStyle.WHITE)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_container,
            text="Hide Secret Text in Image",
            font=ModernStyle.FONT_LARGE,
            bg=ModernStyle.WHITE,
            fg=ModernStyle.PRIMARY
        )
        title_label.pack(pady=(0, 20))
        
        # Left and right panels
        panels_frame = tk.Frame(main_container, bg=ModernStyle.WHITE)
        panels_frame.pack(fill="both", expand=True)
        
        # Left panel - Controls
        left_panel = tk.Frame(panels_frame, bg=ModernStyle.WHITE)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Cover image selection
        img_frame = tk.LabelFrame(
            left_panel,
            text="Cover Image",
            font=ModernStyle.FONT_MEDIUM,
            bg=ModernStyle.WHITE,
            fg=ModernStyle.DARK
        )
        img_frame.pack(fill="x", pady=(0, 15))
        
        img_controls = tk.Frame(img_frame, bg=ModernStyle.WHITE)
        img_controls.pack(fill="x", padx=10, pady=10)
        
        self.cover_image_var = tk.StringVar()
        self.cover_image_entry = tk.Entry(
            img_controls,
            textvariable=self.cover_image_var,
            font=ModernStyle.FONT_MEDIUM,
            state="readonly"
        )
        self.cover_image_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.browse_cover_btn = ttk.Button(
            img_controls,
            text="Browse",
            command=self.browse_cover_image,
            style="Primary.TButton"
        )
        self.browse_cover_btn.pack(side="right")
        
        self.create_test_btn = ttk.Button(
            img_controls,
            text="Create Test Image",
            command=self.create_test_image
        )
        self.create_test_btn.pack(side="right", padx=(0, 5))
        
        # Secret text input
        text_frame = tk.LabelFrame(
            left_panel,
            text="Secret Text",
            font=ModernStyle.FONT_MEDIUM,
            bg=ModernStyle.WHITE,
            fg=ModernStyle.DARK
        )
        text_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        self.secret_text = scrolledtext.ScrolledText(
            text_frame,
            height=8,
            font=ModernStyle.FONT_MEDIUM,
            wrap="word"
        )
        self.secret_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Password and options
        options_frame = tk.LabelFrame(
            left_panel,
            text="Encryption Options",
            font=ModernStyle.FONT_MEDIUM,
            bg=ModernStyle.WHITE,
            fg=ModernStyle.DARK
        )
        options_frame.pack(fill="x", pady=(0, 15))
        
        # Password
        pwd_frame = tk.Frame(options_frame, bg=ModernStyle.WHITE)
        pwd_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            pwd_frame,
            text="Password:",
            font=ModernStyle.FONT_MEDIUM,
            bg=ModernStyle.WHITE
        ).pack(side="left")
        
        self.hide_password_var = tk.StringVar()
        self.hide_password_entry = tk.Entry(
            pwd_frame,
            textvariable=self.hide_password_var,
            font=ModernStyle.FONT_MEDIUM,
            show="*",
            width=20
        )
        self.hide_password_entry.pack(side="right", fill="x", expand=True, padx=(10, 0))
        
        # Compression option
        comp_frame = tk.Frame(options_frame, bg=ModernStyle.WHITE)
        comp_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.use_lzma_var = tk.BooleanVar(value=True)
        self.lzma_check = tk.Checkbutton(
            comp_frame,
            text="Use LZMA compression (better ratio)",
            variable=self.use_lzma_var,
            font=ModernStyle.FONT_MEDIUM,
            bg=ModernStyle.WHITE
        )
        self.lzma_check.pack(side="left")
        
        # Hide button
        self.hide_btn = ttk.Button(
            left_panel,
            text="Hide Text in Image",
            command=self.hide_text_action,
            style="Success.TButton"
        )
        self.hide_btn.pack(fill="x", pady=10)
        
        # Right panel - Image preview
        right_panel = tk.Frame(panels_frame, bg=ModernStyle.WHITE)
        right_panel.pack(side="right", fill="both", padx=(10, 0))
        
        preview_frame = tk.LabelFrame(
            right_panel,
            text="Image Preview",
            font=ModernStyle.FONT_MEDIUM,
            bg=ModernStyle.WHITE,
            fg=ModernStyle.DARK
        )
        preview_frame.pack(fill="both", expand=True)
        
        self.hide_preview = ImagePreview(preview_frame, 350, 300)
        self.hide_preview.frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_extract_tab(self):
        """Create the extract text tab"""
        self.extract_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.extract_frame, text="Extract Text")
        
        # Main container
        main_container = tk.Frame(self.extract_frame, bg=ModernStyle.WHITE)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_container,
            text="Extract Secret Text from Image",
            font=ModernStyle.FONT_LARGE,
            bg=ModernStyle.WHITE,
            fg=ModernStyle.PRIMARY
        )
        title_label.pack(pady=(0, 20))
        
        # Panels
        panels_frame = tk.Frame(main_container, bg=ModernStyle.WHITE)
        panels_frame.pack(fill="both", expand=True)
        
        # Left panel
        left_panel = tk.Frame(panels_frame, bg=ModernStyle.WHITE)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Stego image selection
        img_frame = tk.LabelFrame(
            left_panel,
            text="Stego Image",
            font=ModernStyle.FONT_MEDIUM,
            bg=ModernStyle.WHITE,
            fg=ModernStyle.DARK
        )
        img_frame.pack(fill="x", pady=(0, 15))
        
        img_controls = tk.Frame(img_frame, bg=ModernStyle.WHITE)
        img_controls.pack(fill="x", padx=10, pady=10)
        
        self.stego_image_var = tk.StringVar()
        self.stego_image_entry = tk.Entry(
            img_controls,
            textvariable=self.stego_image_var,
            font=ModernStyle.FONT_MEDIUM,
            state="readonly"
        )
        self.stego_image_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.browse_stego_btn = ttk.Button(
            img_controls,
            text="Browse",
            command=self.browse_stego_image,
            style="Primary.TButton"
        )
        self.browse_stego_btn.pack(side="right")
        
        # Password
        pwd_frame = tk.LabelFrame(
            left_panel,
            text="Decryption Password",
            font=ModernStyle.FONT_MEDIUM,
            bg=ModernStyle.WHITE,
            fg=ModernStyle.DARK
        )
        pwd_frame.pack(fill="x", pady=(0, 15))
        
        pwd_controls = tk.Frame(pwd_frame, bg=ModernStyle.WHITE)
        pwd_controls.pack(fill="x", padx=10, pady=10)
        
        self.extract_password_var = tk.StringVar()
        self.extract_password_entry = tk.Entry(
            pwd_controls,
            textvariable=self.extract_password_var,
            font=ModernStyle.FONT_MEDIUM,
            show="*"
        )
        self.extract_password_entry.pack(fill="x")
        
        # Extract button
        self.extract_btn = ttk.Button(
            left_panel,
            text="Extract Text from Image",
            command=self.extract_text_action,
            style="Success.TButton"
        )
        self.extract_btn.pack(fill="x", pady=10)
        
        # Extracted text display
        result_frame = tk.LabelFrame(
            left_panel,
            text="Extracted Text",
            font=ModernStyle.FONT_MEDIUM,
            bg=ModernStyle.WHITE,
            fg=ModernStyle.DARK
        )
        result_frame.pack(fill="both", expand=True, pady=(15, 0))
        
        self.extracted_text = scrolledtext.ScrolledText(
            result_frame,
            height=10,
            font=ModernStyle.FONT_MEDIUM,
            wrap="word",
            state="disabled"
        )
        self.extracted_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Right panel - Image preview
        right_panel = tk.Frame(panels_frame, bg=ModernStyle.WHITE)
        right_panel.pack(side="right", fill="both", padx=(10, 0))
        
        preview_frame = tk.LabelFrame(
            right_panel,
            text="Image Preview",
            font=ModernStyle.FONT_MEDIUM,
            bg=ModernStyle.WHITE,
            fg=ModernStyle.DARK
        )
        preview_frame.pack(fill="both", expand=True)
        
        self.extract_preview = ImagePreview(preview_frame, 350, 300)
        self.extract_preview.frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_analyze_tab(self):
        """Create the analyze capacity tab"""
        self.analyze_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analyze_frame, text="Analyze Image")
        
        # Main container
        main_container = tk.Frame(self.analyze_frame, bg=ModernStyle.WHITE)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_container,
            text="Analyze Image Capacity",
            font=ModernStyle.FONT_LARGE,
            bg=ModernStyle.WHITE,
            fg=ModernStyle.PRIMARY
        )
        title_label.pack(pady=(0, 20))
        
        # Image selection
        img_frame = tk.LabelFrame(
            main_container,
            text="Select Image to Analyze",
            font=ModernStyle.FONT_MEDIUM,
            bg=ModernStyle.WHITE,
            fg=ModernStyle.DARK
        )
        img_frame.pack(fill="x", pady=(0, 20))
        
        img_controls = tk.Frame(img_frame, bg=ModernStyle.WHITE)
        img_controls.pack(fill="x", padx=10, pady=10)
        
        self.analyze_image_var = tk.StringVar()
        self.analyze_image_entry = tk.Entry(
            img_controls,
            textvariable=self.analyze_image_var,
            font=ModernStyle.FONT_MEDIUM,
            state="readonly"
        )
        self.analyze_image_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.browse_analyze_btn = ttk.Button(
            img_controls,
            text="Browse",
            command=self.browse_analyze_image,
            style="Primary.TButton"
        )
        self.browse_analyze_btn.pack(side="right")
        
        self.analyze_btn = ttk.Button(
            img_controls,
            text="Analyze",
            command=self.analyze_image_action
        )
        self.analyze_btn.pack(side="right", padx=(0, 5))
        
        # Results display
        results_frame = tk.LabelFrame(
            main_container,
            text="Analysis Results",
            font=ModernStyle.FONT_MEDIUM,
            bg=ModernStyle.WHITE,
            fg=ModernStyle.DARK
        )
        results_frame.pack(fill="both", expand=True)
        
        self.analysis_text = scrolledtext.ScrolledText(
            results_frame,
            height=15,
            font=ModernStyle.FONT_MONO,
            wrap="word",
            state="disabled"
        )
        self.analysis_text.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_settings_tab(self):
        """Create the settings tab"""
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")
        
        # Main container
        main_container = tk.Frame(self.settings_frame, bg=ModernStyle.WHITE)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_container,
            text="StegoCrypt Settings",
            font=ModernStyle.FONT_LARGE,
            bg=ModernStyle.WHITE,
            fg=ModernStyle.PRIMARY
        )
        title_label.pack(pady=(0, 20))
        
        # System validation
        validation_frame = tk.LabelFrame(
            main_container,
            text="System Validation",
            font=ModernStyle.FONT_MEDIUM,
            bg=ModernStyle.WHITE,
            fg=ModernStyle.DARK
        )
        validation_frame.pack(fill="x", pady=(0, 20))
        
        self.validation_text = scrolledtext.ScrolledText(
            validation_frame,
            height=8,
            font=ModernStyle.FONT_MONO,
            wrap="word",
            state="disabled"
        )
        self.validation_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        validate_btn = ttk.Button(
            validation_frame,
            text="Run Validation",
            command=self.validate_setup
        )
        validate_btn.pack(pady=10)
        
        # About section
        about_frame = tk.LabelFrame(
            main_container,
            text="About StegoCrypt",
            font=ModernStyle.FONT_MEDIUM,
            bg=ModernStyle.WHITE,
            fg=ModernStyle.DARK
        )
        about_frame.pack(fill="x")
        
        about_text = tk.Text(
            about_frame,
            height=8,
            font=ModernStyle.FONT_MEDIUM,
            wrap="word",
            state="disabled",
            bg=ModernStyle.WHITE
        )
        about_text.pack(fill="x", padx=10, pady=10)
        
        about_content = """StegoCrypt - Secure Text Hiding System

Version: 1.0.0
Author: Advanced Cryptography Team

Features:
• AES-256 encryption with PBKDF2 key derivation
• LZMA/zlib compression for optimal space usage
• LSB steganography with integrity checking
• Modern GUI with image preview
• Comprehensive capacity analysis

Security:
• 100,000 PBKDF2 iterations
• SHA-256 checksums for data integrity
• Secure random salt and IV generation
• Lossless image format enforcement"""
        
        about_text.config(state="normal")
        about_text.insert("1.0", about_content)
        about_text.config(state="disabled")
    
    def setup_layout(self):
        """Setup the main layout"""
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        self.status_bar.pack(fill="x", side="bottom")
    
    # Event handlers
    def browse_cover_image(self):
        """Browse for cover image"""
        filename = filedialog.askopenfilename(
            title="Select Cover Image",
            filetypes=[
                ("PNG files", "*.png"),
                ("BMP files", "*.bmp"),
                ("TIFF files", "*.tiff *.tif"),
                ("All supported", "*.png *.bmp *.tiff *.tif")
            ]
        )
        if filename:
            self.cover_image_var.set(filename)
            self.current_cover_image = filename
            self.hide_preview.load_image(filename)
            self.update_status(f"Cover image loaded: {os.path.basename(filename)}")
    
    def browse_stego_image(self):
        """Browse for stego image"""
        filename = filedialog.askopenfilename(
            title="Select Stego Image",
            filetypes=[
                ("PNG files", "*.png"),
                ("BMP files", "*.bmp"),
                ("TIFF files", "*.tiff *.tif"),
                ("All supported", "*.png *.bmp *.tiff *.tif")
            ]
        )
        if filename:
            self.stego_image_var.set(filename)
            self.current_stego_image = filename
            self.extract_preview.load_image(filename)
            self.update_status(f"Stego image loaded: {os.path.basename(filename)}")
    
    def browse_analyze_image(self):
        """Browse for image to analyze"""
        filename = filedialog.askopenfilename(
            title="Select Image to Analyze",
            filetypes=[
                ("PNG files", "*.png"),
                ("BMP files", "*.bmp"),
                ("TIFF files", "*.tiff *.tif"),
                ("All supported", "*.png *.bmp *.tiff *.tif")
            ]
        )
        if filename:
            self.analyze_image_var.set(filename)
            self.update_status(f"Analysis image loaded: {os.path.basename(filename)}")
    
    def create_test_image(self):
        """Create a test image"""
        filename = filedialog.asksaveasfilename(
            title="Save Test Image",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")]
        )
        if filename:
            try:
                self.stegocrypt.create_test_image(filename, (800, 600))
                self.cover_image_var.set(filename)
                self.current_cover_image = filename
                self.hide_preview.load_image(filename)
                self.update_status("Test image created successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create test image: {str(e)}")
    
    def hide_text_action(self):
        """Hide text in image action"""
        # Validate inputs
        if not self.current_cover_image:
            messagebox.showerror("Error", "Please select a cover image")
            return
        
        secret_text = self.secret_text.get("1.0", "end-1c").strip()
        if not secret_text:
            messagebox.showerror("Error", "Please enter secret text")
            return
        
        password = self.hide_password_var.get().strip()
        if not password:
            messagebox.showerror("Error", "Please enter a password")
            return
        
        # Get output filename
        output_filename = filedialog.asksaveasfilename(
            title="Save Stego Image",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")]
        )
        if not output_filename:
            return
        
        # Run in thread to prevent GUI freezing
        def hide_thread():
            progress = ProgressDialog(self.root, "Hiding Text...")
            try:
                progress.update_status("Compressing text...")
                
                stats = self.stegocrypt.hide_text_in_image(
                    self.current_cover_image,
                    secret_text,
                    password,
                    output_filename,
                    use_lzma=self.use_lzma_var.get()
                )
                
                progress.close()
                
                # Show success message with stats
                compression_ratio = stats['compression_stats']['compression_ratio']
                utilization = stats['embedding_stats']['utilization_percent']
                
                messagebox.showinfo(
                    "Success",
                    f"Text hidden successfully!\n\n"
                    f"Compression ratio: {compression_ratio:.2%}\n"
                    f"Image utilization: {utilization:.2f}%\n"
                    f"Output: {os.path.basename(output_filename)}"
                )
                
                self.update_status("Text hidden successfully")
                
            except Exception as e:
                progress.close()
                messagebox.showerror("Error", str(e))
                self.update_status("Hide operation failed")
        
        threading.Thread(target=hide_thread, daemon=True).start()
    
    def extract_text_action(self):
        """Extract text from image action"""
        # Validate inputs
        if not self.current_stego_image:
            messagebox.showerror("Error", "Please select a stego image")
            return
        
        password = self.extract_password_var.get().strip()
        if not password:
            messagebox.showerror("Error", "Please enter the decryption password")
            return
        
        # Run in thread to prevent GUI freezing
        def extract_thread():
            progress = ProgressDialog(self.root, "Extracting Text...")
            try:
                progress.update_status("Extracting data from image...")
                
                extracted_text, stats = self.stegocrypt.extract_text_from_image(
                    self.current_stego_image,
                    password
                )
                
                progress.close()
                
                # Display extracted text
                self.extracted_text.config(state="normal")
                self.extracted_text.delete("1.0", "end")
                self.extracted_text.insert("1.0", extracted_text)
                self.extracted_text.config(state="disabled")
                
                # Show success message
                messagebox.showinfo(
                    "Success",
                    f"Text extracted successfully!\n\n"
                    f"Extracted {len(extracted_text)} characters\n"
                    f"Processing time: {stats['processing_time']:.2f} seconds"
                )
                
                self.update_status("Text extracted successfully")
                
            except Exception as e:
                progress.close()
                messagebox.showerror("Error", str(e))
                self.update_status("Extract operation failed")
        
        threading.Thread(target=extract_thread, daemon=True).start()
    
    def analyze_image_action(self):
        """Analyze image capacity action"""
        image_path = self.analyze_image_var.get()
        if not image_path:
            messagebox.showerror("Error", "Please select an image to analyze")
            return
        
        try:
            analysis = self.stegocrypt.analyze_image_capacity(image_path)
            
            # Format analysis results
            results = f"""Image Analysis Results
{'=' * 50}

File Information:
  Path: {analysis['image_path']}
  Size: {analysis['image_size'][0]} x {analysis['image_size'][1]} pixels
  Mode: {analysis['image_mode']}
  Format: {analysis['image_format']}
  Total Pixels: {analysis['total_pixels']:,}
  Color Channels: {analysis['color_channels']}

Steganography Capacity:
  Raw Capacity: {analysis['raw_capacity_bytes']:,} bytes
  Estimated Text Capacity: ~{analysis['estimated_text_capacity_chars']:,} characters
  Recommended Max Text: ~{analysis['recommended_max_text_length']:,} characters

Notes:
- Raw capacity assumes 1 bit per color channel (LSB steganography)
- Estimated capacity accounts for compression and encryption overhead
- Recommended max provides a safe margin for reliable operation
- Actual capacity may vary based on text content and compression ratio
"""
            
            # Display results
            self.analysis_text.config(state="normal")
            self.analysis_text.delete("1.0", "end")
            self.analysis_text.insert("1.0", results)
            self.analysis_text.config(state="disabled")
            
            self.update_status("Image analysis completed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")
            self.update_status("Analysis failed")
    
    def validate_setup(self):
        """Validate system setup"""
        try:
            results = self.stegocrypt.validate_setup()
            
            validation_text = f"""System Validation Results
{'=' * 40}

Component Status:
  Crypto Engine: {'✅ PASS' if results['crypto_engine'] else '❌ FAIL'}
  Steganography Engine: {'✅ PASS' if results['steganography_engine'] else '❌ FAIL'}
  Integration: {'✅ PASS' if results['integration'] else '❌ FAIL'}

Overall Status: {'✅ ALL SYSTEMS OPERATIONAL' if all(results.values()) else '❌ SYSTEM ISSUES DETECTED'}

Test Details:
- Crypto Engine: AES-256 encryption/decryption with LZMA compression
- Steganography Engine: LSB embedding and extraction with integrity checking
- Integration: End-to-end workflow validation

Timestamp: {self.get_timestamp()}
"""
            
            # Display validation results
            self.validation_text.config(state="normal")
            self.validation_text.delete("1.0", "end")
            self.validation_text.insert("1.0", validation_text)
            self.validation_text.config(state="disabled")
            
            if all(results.values()):
                self.update_status("System validation passed")
            else:
                self.update_status("System validation failed")
                
        except Exception as e:
            error_text = f"""System Validation Error
{'=' * 40}

Error: {str(e)}

This indicates a critical system issue. Please check:
1. All required dependencies are installed
2. Python environment is properly configured
3. No conflicting packages are present

Timestamp: {self.get_timestamp()}
"""
            self.validation_text.config(state="normal")
            self.validation_text.delete("1.0", "end")
            self.validation_text.insert("1.0", error_text)
            self.validation_text.config(state="disabled")
            
            self.update_status("System validation error")
    
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def get_timestamp(self):
        """Get current timestamp"""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    app = StegoCryptGUI()
    app.run()


if __name__ == "__main__":
    main()
