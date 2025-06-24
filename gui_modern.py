"""
StegoCrypt Modern GUI - Beautiful & Professional Interface
Enhanced with modern design principles, animations, and superior UX
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk, ImageDraw, ImageFont
import threading
import os
import time
from typing import Optional, Dict, Any
import math

from stegocrypt import StegoCrypt


class ModernTheme:
    """Modern dark/light theme with beautiful colors"""
    
    # Color Palette - Modern Blue/Purple Gradient
    PRIMARY = "#667eea"          # Beautiful blue
    PRIMARY_DARK = "#5a67d8"     # Darker blue
    SECONDARY = "#764ba2"        # Purple accent
    SUCCESS = "#48bb78"          # Green
    WARNING = "#ed8936"          # Orange
    DANGER = "#f56565"           # Red
    
    # Background colors
    BG_DARK = "#1a202c"          # Dark background
    BG_LIGHT = "#f7fafc"         # Light background
    BG_CARD = "#2d3748"          # Card background
    BG_CARD_LIGHT = "#ffffff"    # Light card background
    
    # Text colors
    TEXT_PRIMARY = "#2d3748"     # Dark text
    TEXT_SECONDARY = "#718096"   # Gray text
    TEXT_LIGHT = "#ffffff"       # White text
    TEXT_MUTED = "#a0aec0"       # Muted text
    
    # Fonts
    FONT_TITLE = ("Segoe UI", 24, "bold")
    FONT_HEADING = ("Segoe UI", 16, "bold")
    FONT_SUBHEADING = ("Segoe UI", 14, "bold")
    FONT_BODY = ("Segoe UI", 11)
    FONT_SMALL = ("Segoe UI", 9)
    FONT_MONO = ("Consolas", 10)
    
    # Spacing
    PADDING_LARGE = 30
    PADDING_MEDIUM = 20
    PADDING_SMALL = 10
    BORDER_RADIUS = 12


class AnimatedButton(tk.Frame):
    """Custom animated button with hover effects"""
    
    def __init__(self, parent, text="Button", command=None, style="primary", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.command = command
        self.style = style
        self.is_hovered = False
        
        # Style configuration
        if style == "primary":
            self.bg_normal = ModernTheme.PRIMARY
            self.bg_hover = ModernTheme.PRIMARY_DARK
            self.text_color = ModernTheme.TEXT_LIGHT
        elif style == "success":
            self.bg_normal = ModernTheme.SUCCESS
            self.bg_hover = "#38a169"
            self.text_color = ModernTheme.TEXT_LIGHT
        elif style == "secondary":
            self.bg_normal = ModernTheme.BG_CARD_LIGHT
            self.bg_hover = "#e2e8f0"
            self.text_color = ModernTheme.TEXT_PRIMARY
        else:
            self.bg_normal = ModernTheme.PRIMARY
            self.bg_hover = ModernTheme.PRIMARY_DARK
            self.text_color = ModernTheme.TEXT_LIGHT
        
        # Create button
        self.button = tk.Label(
            self,
            text=text,
            font=ModernTheme.FONT_BODY,
            bg=self.bg_normal,
            fg=self.text_color,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.button.pack(fill="both", expand=True)
        
        # Bind events
        self.button.bind("<Button-1>", self.on_click)
        self.button.bind("<Enter>", self.on_enter)
        self.button.bind("<Leave>", self.on_leave)
        
        self.configure(bg=self.bg_normal)
    
    def on_click(self, event):
        if self.command:
            self.command()
    
    def on_enter(self, event):
        self.is_hovered = True
        self.button.configure(bg=self.bg_hover)
        self.configure(bg=self.bg_hover)
    
    def on_leave(self, event):
        self.is_hovered = False
        self.button.configure(bg=self.bg_normal)
        self.configure(bg=self.bg_normal)


class ModernCard(tk.Frame):
    """Modern card widget with shadow effect"""
    
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, bg=ModernTheme.BG_CARD_LIGHT, relief="flat", bd=0, **kwargs)
        
        # Add subtle border
        self.configure(highlightbackground="#e2e8f0", highlightthickness=1)
        
        if title:
            title_label = tk.Label(
                self,
                text=title,
                font=ModernTheme.FONT_SUBHEADING,
                bg=ModernTheme.BG_CARD_LIGHT,
                fg=ModernTheme.TEXT_PRIMARY,
                anchor="w"
            )
            title_label.pack(fill="x", padx=ModernTheme.PADDING_MEDIUM, 
                           pady=(ModernTheme.PADDING_MEDIUM, ModernTheme.PADDING_SMALL))


class ProgressIndicator(tk.Frame):
    """Modern progress indicator with smooth animation"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=ModernTheme.BG_LIGHT, **kwargs)
        
        self.canvas = tk.Canvas(
            self,
            height=6,
            bg=ModernTheme.BG_LIGHT,
            highlightthickness=0
        )
        self.canvas.pack(fill="x", padx=ModernTheme.PADDING_MEDIUM)
        
        self.progress_bar = None
        self.is_animating = False
        self.animation_position = 0
    
    def start_animation(self):
        """Start progress animation"""
        self.is_animating = True
        self.animate()
    
    def stop_animation(self):
        """Stop progress animation"""
        self.is_animating = False
        self.canvas.delete("all")
    
    def animate(self):
        """Animate the progress bar"""
        if not self.is_animating:
            return
        
        self.canvas.delete("all")
        
        width = self.canvas.winfo_width()
        if width > 1:
            # Create animated progress bar
            bar_width = width // 3
            x = (self.animation_position % (width + bar_width)) - bar_width
            
            self.canvas.create_rectangle(
                x, 0, x + bar_width, 6,
                fill=ModernTheme.PRIMARY,
                outline=""
            )
            
            self.animation_position += 5
        
        self.after(50, self.animate)


class ImagePreviewWidget(tk.Frame):
    """Enhanced image preview with modern styling"""
    
    def __init__(self, parent, width=400, height=300, **kwargs):
        super().__init__(parent, bg=ModernTheme.BG_CARD_LIGHT, **kwargs)
        
        self.preview_width = width
        self.preview_height = height
        
        # Create canvas with modern styling
        self.canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            bg="#f8f9fa",
            highlightthickness=1,
            highlightbackground="#e2e8f0"
        )
        self.canvas.pack(padx=ModernTheme.PADDING_MEDIUM, pady=ModernTheme.PADDING_MEDIUM)
        
        # Image variables
        self.current_image = None
        self.photo_image = None
        
        # Default placeholder
        self.show_placeholder()
    
    def show_placeholder(self):
        """Show placeholder when no image is loaded"""
        self.canvas.delete("all")
        
        # Draw placeholder
        center_x = self.preview_width // 2
        center_y = self.preview_height // 2
        
        # Background
        self.canvas.create_rectangle(
            0, 0, self.preview_width, self.preview_height,
            fill="#f8f9fa", outline=""
        )
        
        # Icon
        self.canvas.create_oval(
            center_x - 30, center_y - 40,
            center_x + 30, center_y - 10,
            fill="#e2e8f0", outline=""
        )
        
        # Text
        self.canvas.create_text(
            center_x, center_y + 20,
            text="No image selected",
            font=ModernTheme.FONT_BODY,
            fill=ModernTheme.TEXT_SECONDARY
        )
        
        self.canvas.create_text(
            center_x, center_y + 40,
            text="Click Browse to select an image",
            font=ModernTheme.FONT_SMALL,
            fill=ModernTheme.TEXT_MUTED
        )
    
    def load_image(self, image_path: str):
        """Load and display an image"""
        try:
            # Load image
            image = Image.open(image_path)
            self.current_image = image
            
            # Calculate scaling to fit preview
            img_width, img_height = image.size
            scale_x = self.preview_width / img_width
            scale_y = self.preview_height / img_height
            scale = min(scale_x, scale_y, 1.0)  # Don't upscale
            
            # Resize image
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.photo_image = ImageTk.PhotoImage(resized_image)
            
            # Clear canvas and display image
            self.canvas.delete("all")
            
            # Center the image
            x = (self.preview_width - new_width) // 2
            y = (self.preview_height - new_height) // 2
            
            self.canvas.create_image(x, y, anchor="nw", image=self.photo_image)
            
            # Add image info
            info_text = f"{img_width} × {img_height} pixels"
            self.canvas.create_text(
                10, self.preview_height - 10,
                text=info_text,
                font=ModernTheme.FONT_SMALL,
                fill=ModernTheme.TEXT_SECONDARY,
                anchor="sw"
            )
            
        except Exception as e:
            self.show_error(f"Error loading image: {str(e)}")
    
    def show_error(self, error_message: str):
        """Show error message"""
        self.canvas.delete("all")
        
        center_x = self.preview_width // 2
        center_y = self.preview_height // 2
        
        # Error icon
        self.canvas.create_oval(
            center_x - 20, center_y - 30,
            center_x + 20, center_y + 10,
            fill=ModernTheme.DANGER, outline=""
        )
        
        # Error text
        self.canvas.create_text(
            center_x, center_y + 30,
            text=error_message,
            font=ModernTheme.FONT_SMALL,
            fill=ModernTheme.DANGER,
            width=self.preview_width - 40,
            justify="center"
        )
    
    def clear(self):
        """Clear the preview"""
        self.current_image = None
        self.photo_image = None
        self.show_placeholder()


class StegoCryptModernGUI:
    """Modern, beautiful GUI for StegoCrypt"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("StegoCrypt - Secure Text Hiding System")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg=ModernTheme.BG_LIGHT)
        
        # Initialize StegoCrypt
        self.stegocrypt = StegoCrypt()
        
        # GUI state
        self.current_cover_image = None
        self.current_stego_image = None
        self.current_analyze_image = None
        
        # Create GUI
        self.setup_styles()
        self.create_header()
        self.create_main_content()
        self.create_footer()
        
        # Initial validation
        self.root.after(1000, self.validate_system)
    
    def setup_styles(self):
        """Setup modern styling"""
        style = ttk.Style()
        
        # Configure notebook style
        style.configure(
            "Modern.TNotebook",
            background=ModernTheme.BG_LIGHT,
            borderwidth=0,
            tabmargins=[0, 0, 0, 0]
        )
        
        style.configure(
            "Modern.TNotebook.Tab",
            padding=[30, 15],
            font=ModernTheme.FONT_BODY,
            background=ModernTheme.BG_CARD_LIGHT,
            foreground=ModernTheme.TEXT_PRIMARY,
            borderwidth=0
        )
        
        style.map(
            "Modern.TNotebook.Tab",
            background=[("selected", ModernTheme.PRIMARY)],
            foreground=[("selected", ModernTheme.TEXT_LIGHT)]
        )
    
    def create_header(self):
        """Create the header section"""
        header_frame = tk.Frame(self.root, bg=ModernTheme.PRIMARY, height=100)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Title and subtitle
        title_label = tk.Label(
            header_frame,
            text="🔐 StegoCrypt",
            font=ModernTheme.FONT_TITLE,
            bg=ModernTheme.PRIMARY,
            fg=ModernTheme.TEXT_LIGHT
        )
        title_label.pack(pady=(20, 5))
        
        subtitle_label = tk.Label(
            header_frame,
            text="Advanced Steganography System with Military-Grade Security",
            font=ModernTheme.FONT_BODY,
            bg=ModernTheme.PRIMARY,
            fg=ModernTheme.TEXT_LIGHT
        )
        subtitle_label.pack()
    
    def create_main_content(self):
        """Create the main content area"""
        # Main container
        main_frame = tk.Frame(self.root, bg=ModernTheme.BG_LIGHT)
        main_frame.pack(fill="both", expand=True, padx=ModernTheme.PADDING_LARGE, 
                       pady=ModernTheme.PADDING_LARGE)
        
        # Create notebook
        self.notebook = ttk.Notebook(main_frame, style="Modern.TNotebook")
        self.notebook.pack(fill="both", expand=True)
        
        # Create tabs
        self.create_hide_tab()
        self.create_extract_tab()
        self.create_analyze_tab()
        self.create_about_tab()
    
    def create_hide_tab(self):
        """Create the hide text tab"""
        hide_frame = tk.Frame(self.notebook, bg=ModernTheme.BG_LIGHT)
        self.notebook.add(hide_frame, text="🔒 Hide Text")
        
        # Main container with two columns
        container = tk.Frame(hide_frame, bg=ModernTheme.BG_LIGHT)
        container.pack(fill="both", expand=True, padx=ModernTheme.PADDING_MEDIUM, 
                      pady=ModernTheme.PADDING_MEDIUM)
        
        # Left column - Controls
        left_column = tk.Frame(container, bg=ModernTheme.BG_LIGHT)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, ModernTheme.PADDING_MEDIUM))
        
        # Cover image card
        cover_card = ModernCard(left_column, title="📁 Select Cover Image")
        cover_card.pack(fill="x", pady=(0, ModernTheme.PADDING_MEDIUM))
        
        # Image selection controls
        img_controls = tk.Frame(cover_card, bg=ModernTheme.BG_CARD_LIGHT)
        img_controls.pack(fill="x", padx=ModernTheme.PADDING_MEDIUM, pady=ModernTheme.PADDING_SMALL)
        
        self.cover_image_var = tk.StringVar()
        cover_entry = tk.Entry(
            img_controls,
            textvariable=self.cover_image_var,
            font=ModernTheme.FONT_BODY,
            state="readonly",
            bg="#f8f9fa",
            relief="flat",
            bd=5
        )
        cover_entry.pack(side="left", fill="x", expand=True, padx=(0, ModernTheme.PADDING_SMALL))
        
        browse_btn = AnimatedButton(
            img_controls,
            text="Browse",
            command=self.browse_cover_image,
            style="primary"
        )
        browse_btn.pack(side="right", padx=(ModernTheme.PADDING_SMALL, 0))
        
        test_btn = AnimatedButton(
            img_controls,
            text="Create Test",
            command=self.create_test_image,
            style="secondary"
        )
        test_btn.pack(side="right")
        
        # Secret text card
        text_card = ModernCard(left_column, title="✍️ Secret Message")
        text_card.pack(fill="both", expand=True, pady=(0, ModernTheme.PADDING_MEDIUM))
        
        self.secret_text = scrolledtext.ScrolledText(
            text_card,
            height=8,
            font=ModernTheme.FONT_BODY,
            wrap="word",
            relief="flat",
            bd=5,
            bg="#f8f9fa"
        )
        self.secret_text.pack(fill="both", expand=True, padx=ModernTheme.PADDING_MEDIUM, 
                             pady=ModernTheme.PADDING_SMALL)
        
        # Options card
        options_card = ModernCard(left_column, title="⚙️ Encryption Options")
        options_card.pack(fill="x", pady=(0, ModernTheme.PADDING_MEDIUM))
        
        options_content = tk.Frame(options_card, bg=ModernTheme.BG_CARD_LIGHT)
        options_content.pack(fill="x", padx=ModernTheme.PADDING_MEDIUM, pady=ModernTheme.PADDING_SMALL)
        
        # Password
        pwd_frame = tk.Frame(options_content, bg=ModernTheme.BG_CARD_LIGHT)
        pwd_frame.pack(fill="x", pady=(0, ModernTheme.PADDING_SMALL))
        
        tk.Label(
            pwd_frame,
            text="🔑 Password:",
            font=ModernTheme.FONT_BODY,
            bg=ModernTheme.BG_CARD_LIGHT,
            fg=ModernTheme.TEXT_PRIMARY
        ).pack(side="left")
        
        self.hide_password_var = tk.StringVar()
        pwd_entry = tk.Entry(
            pwd_frame,
            textvariable=self.hide_password_var,
            font=ModernTheme.FONT_BODY,
            show="*",
            relief="flat",
            bd=5,
            bg="#f8f9fa"
        )
        pwd_entry.pack(side="right", fill="x", expand=True, padx=(ModernTheme.PADDING_SMALL, 0))
        
        # Compression option
        self.use_lzma_var = tk.BooleanVar(value=True)
        lzma_check = tk.Checkbutton(
            options_content,
            text="🗜️ Use LZMA compression (better ratio)",
            variable=self.use_lzma_var,
            font=ModernTheme.FONT_BODY,
            bg=ModernTheme.BG_CARD_LIGHT,
            fg=ModernTheme.TEXT_PRIMARY,
            selectcolor=ModernTheme.BG_CARD_LIGHT
        )
        lzma_check.pack(anchor="w")
        
        # Hide button
        hide_btn = AnimatedButton(
            left_column,
            text="🔒 Hide Text in Image",
            command=self.hide_text_action,
            style="success"
        )
        hide_btn.pack(fill="x", pady=ModernTheme.PADDING_SMALL)
        
        # Progress indicator
        self.hide_progress = ProgressIndicator(left_column)
        self.hide_progress.pack(fill="x", pady=ModernTheme.PADDING_SMALL)
        
        # Right column - Image preview
        right_column = tk.Frame(container, bg=ModernTheme.BG_LIGHT)
        right_column.pack(side="right", fill="both", padx=(ModernTheme.PADDING_MEDIUM, 0))
        
        preview_card = ModernCard(right_column, title="🖼️ Image Preview")
        preview_card.pack(fill="both", expand=True)
        
        self.hide_preview = ImagePreviewWidget(preview_card, 400, 350)
        self.hide_preview.pack(fill="both", expand=True)
    
    def create_extract_tab(self):
        """Create the extract text tab"""
        extract_frame = tk.Frame(self.notebook, bg=ModernTheme.BG_LIGHT)
        self.notebook.add(extract_frame, text="🔍 Extract Text")
        
        # Main container
        container = tk.Frame(extract_frame, bg=ModernTheme.BG_LIGHT)
        container.pack(fill="both", expand=True, padx=ModernTheme.PADDING_MEDIUM, 
                      pady=ModernTheme.PADDING_MEDIUM)
        
        # Left column
        left_column = tk.Frame(container, bg=ModernTheme.BG_LIGHT)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, ModernTheme.PADDING_MEDIUM))
        
        # Stego image card
        stego_card = ModernCard(left_column, title="📁 Select Stego Image")
        stego_card.pack(fill="x", pady=(0, ModernTheme.PADDING_MEDIUM))
        
        img_controls = tk.Frame(stego_card, bg=ModernTheme.BG_CARD_LIGHT)
        img_controls.pack(fill="x", padx=ModernTheme.PADDING_MEDIUM, pady=ModernTheme.PADDING_SMALL)
        
        self.stego_image_var = tk.StringVar()
        stego_entry = tk.Entry(
            img_controls,
            textvariable=self.stego_image_var,
            font=ModernTheme.FONT_BODY,
            state="readonly",
            bg="#f8f9fa",
            relief="flat",
            bd=5
        )
        stego_entry.pack(side="left", fill="x", expand=True, padx=(0, ModernTheme.PADDING_SMALL))
        
        browse_stego_btn = AnimatedButton(
            img_controls,
            text="Browse",
            command=self.browse_stego_image,
            style="primary"
        )
        browse_stego_btn.pack(side="right")
        
        # Password card
        pwd_card = ModernCard(left_column, title="🔑 Decryption Password")
        pwd_card.pack(fill="x", pady=(0, ModernTheme.PADDING_MEDIUM))
        
        self.extract_password_var = tk.StringVar()
        pwd_entry = tk.Entry(
            pwd_card,
            textvariable=self.extract_password_var,
            font=ModernTheme.FONT_BODY,
            show="*",
            relief="flat",
            bd=5,
            bg="#f8f9fa"
        )
        pwd_entry.pack(fill="x", padx=ModernTheme.PADDING_MEDIUM, pady=ModernTheme.PADDING_SMALL)
        
        # Extract button
        extract_btn = AnimatedButton(
            left_column,
            text="🔍 Extract Hidden Text",
            command=self.extract_text_action,
            style="success"
        )
        extract_btn.pack(fill="x", pady=ModernTheme.PADDING_SMALL)
        
        # Progress indicator
        self.extract_progress = ProgressIndicator(left_column)
        self.extract_progress.pack(fill="x", pady=ModernTheme.PADDING_SMALL)
        
        # Extracted text card
        result_card = ModernCard(left_column, title="📝 Extracted Text")
        result_card.pack(fill="both", expand=True, pady=(ModernTheme.PADDING_MEDIUM, 0))
        
        self.extracted_text = scrolledtext.ScrolledText(
            result_card,
            height=10,
            font=ModernTheme.FONT_BODY,
            wrap="word",
            state="disabled",
            relief="flat",
            bd=5,
            bg="#f8f9fa"
        )
        self.extracted_text.pack(fill="both", expand=True, padx=ModernTheme.PADDING_MEDIUM, 
                                pady=ModernTheme.PADDING_SMALL)
        
        # Right column - Image preview
        right_column = tk.Frame(container, bg=ModernTheme.BG_LIGHT)
        right_column.pack(side="right", fill="both", padx=(ModernTheme.PADDING_MEDIUM, 0))
        
        preview_card = ModernCard(right_column, title="🖼️ Image Preview")
        preview_card.pack(fill="both", expand=True)
        
        self.extract_preview = ImagePreviewWidget(preview_card, 400, 350)
        self.extract_preview.pack(fill="both", expand=True)
    
    def create_analyze_tab(self):
        """Create the analyze tab"""
        analyze_frame = tk.Frame(self.notebook, bg=ModernTheme.BG_LIGHT)
        self.notebook.add(analyze_frame, text="📊 Analyze")
        
        container = tk.Frame(analyze_frame, bg=ModernTheme.BG_LIGHT)
        container.pack(fill="both", expand=True, padx=ModernTheme.PADDING_MEDIUM, 
                      pady=ModernTheme.PADDING_MEDIUM)
        
        # Image selection card
        select_card = ModernCard(container, title="📁 Select Image to Analyze")
        select_card.pack(fill="x", pady=(0, ModernTheme.PADDING_MEDIUM))
        
        img_controls = tk.Frame(select_card, bg=ModernTheme.BG_CARD_LIGHT)
        img_controls.pack(fill="x", padx=ModernTheme.PADDING_MEDIUM, pady=ModernTheme.PADDING_SMALL)
        
        self.analyze_image_var = tk.StringVar()
        analyze_entry = tk.Entry(
            img_controls,
            textvariable=self.analyze_image_var,
            font=ModernTheme.FONT_BODY,
            state="readonly",
            bg="#f8f9fa",
            relief="flat",
            bd=5
        )
        analyze_entry.pack(side="left", fill="x", expand=True, padx=(0, ModernTheme.PADDING_SMALL))
        
        browse_analyze_btn = AnimatedButton(
            img_controls,
            text="Browse",
            command=self.browse_analyze_image,
            style="primary"
        )
        browse_analyze_btn.pack(side="right", padx=(ModernTheme.PADDING_SMALL, 0))
        
        analyze_btn = AnimatedButton(
            img_controls,
            text="Analyze",
            command=self.analyze_image_action,
            style="success"
        )
        analyze_btn.pack(side="right")
        
        # Progress indicator
        self.analyze_progress = ProgressIndicator(container)
        self.analyze_progress.pack(fill="x", pady=ModernTheme.PADDING_SMALL)
        
        # Results card
        results_card = ModernCard(container, title="📊 Analysis Results")
        results_card.pack(fill="both", expand=True)
        
        self.analysis_text = scrolledtext.ScrolledText(
            results_card,
            height=15,
            font=ModernTheme.FONT_MONO,
            wrap="word",
            state="disabled",
            relief="flat",
            bd=5,
            bg="#f8f9fa"
        )
        self.analysis_text.pack(fill="both", expand=True, padx=ModernTheme.PADDING_MEDIUM, 
                               pady=ModernTheme.PADDING_SMALL)
    
    def create_about_tab(self):
        """Create the about tab"""
        about_frame = tk.Frame(self.notebook, bg=ModernTheme.BG_LIGHT)
        self.notebook.add(about_frame, text="ℹ️ About")
        
        container = tk.Frame(about_frame, bg=ModernTheme.BG_LIGHT)
        container.pack(fill="both", expand=True, padx=ModernTheme.PADDING_MEDIUM, 
                      pady=ModernTheme.PADDING_MEDIUM)
        
        # About card
        about_card = ModernCard(container, title="🔐 About StegoCrypt")
        about_card.pack(fill="both", expand=True)
        
        about_text = scrolledtext.ScrolledText(
            about_card,
            height=20,
            font=ModernTheme.FONT_BODY,
            wrap="word",
            state="disabled",
            relief="flat",
            bd=5,
            bg="#f8f9fa"
        )
        about_text.pack(fill="both", expand=True, padx=ModernTheme.PADDING_MEDIUM, 
                       pady=ModernTheme.PADDING_SMALL)
        
        about_content = """🔐 StegoCrypt - Advanced Steganography System

Version: 2.0.0
Author: Advanced Cryptography Team

🌟 FEATURES:
• Military-grade AES-256 encryption with PBKDF2 key derivation
• LZMA/zlib compression for optimal space efficiency
• LSB steganography with integrity verification
• Modern GUI with beautiful design and animations
• Comprehensive image capacity analysis
• Cross-platform compatibility (Windows, macOS, Linux)

🔒 SECURITY:
• 100,000 PBKDF2 iterations for key strengthening
• SHA-256 checksums for data integrity verification
• Secure random salt and IV generation
• Lossless image format enforcement
• Password-based encryption with strong key derivation

🎨 INTERFACE:
• Modern card-based design with smooth animations
• Real-time image preview with scaling
• Progress indicators with beautiful animations
• Intuitive tabbed interface for different operations
• Professional color scheme and typography

📊 ANALYSIS:
• Detailed image capacity calculations
• Compression ratio analysis
• Processing time measurements
• Image format compatibility checking
• Steganography suitability scoring

🚀 PERFORMANCE:
• Optimized algorithms for fast processing
• Multi-threaded operations to prevent UI freezing
• Efficient memory usage for large images
• Smart compression selection based on content
• Minimal overhead for maximum capacity

For support and documentation, visit our project repository.
Built with ❤️ using Python, Tkinter, PIL, and advanced cryptography."""
        
        about_text.config(state="normal")
        about_text.insert("1.0", about_content)
        about_text.config(state="disabled")
    
    def create_footer(self):
        """Create the footer section"""
        footer_frame = tk.Frame(self.root, bg=ModernTheme.TEXT_SECONDARY, height=40)
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)
        
        # Status and info
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(
            footer_frame,
            textvariable=self.status_var,
            font=ModernTheme.FONT_SMALL,
            bg=ModernTheme.TEXT_SECONDARY,
            fg=ModernTheme.TEXT_LIGHT,
            anchor="w"
        )
        status_label.pack(side="left", padx=ModernTheme.PADDING_MEDIUM, pady=10)
        
        # Version info
        version_label = tk.Label(
            footer_frame,
            text="StegoCrypt v2.0.0",
            font=ModernTheme.FONT_SMALL,
            bg=ModernTheme.TEXT_SECONDARY,
            fg=ModernTheme.TEXT_LIGHT,
            anchor="e"
        )
        version_label.pack(side="right", padx=ModernTheme.PADDING_MEDIUM, pady=10)
    
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
            self.current_analyze_image = filename
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
                messagebox.showinfo("Success", "Test image created successfully!")
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
            try:
                self.hide_progress.start_animation()
                self.update_status("Hiding text in image...")
                
                stats = self.stegocrypt.hide_text_in_image(
                    self.current_cover_image,
                    secret_text,
                    password,
                    output_filename,
                    use_lzma=self.use_lzma_var.get()
                )
                
                self.hide_progress.stop_animation()
                
                # Show success message with stats
                compression_ratio = stats['compression_stats']['compression_ratio']
                utilization = stats['embedding_stats']['utilization_percent']
                
                messagebox.showinfo(
                    "Success! 🎉",
                    f"Text hidden successfully!\n\n"
                    f"📊 Compression ratio: {compression_ratio:.2%}\n"
                    f"📈 Image utilization: {utilization:.2f}%\n"
                    f"📁 Output: {os.path.basename(output_filename)}\n\n"
                    f"Your secret message is now safely hidden!"
                )
                
                self.update_status("✅ Text hidden successfully")
                
            except Exception as e:
                self.hide_progress.stop_animation()
                messagebox.showerror("Error", f"Failed to hide text: {str(e)}")
                self.update_status("❌ Hide operation failed")
        
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
            try:
                self.extract_progress.start_animation()
                self.update_status("Extracting text from image...")
                
                extracted_text, stats = self.stegocrypt.extract_text_from_image(
                    self.current_stego_image,
                    password
                )
                
                self.extract_progress.stop_animation()
                
                # Display extracted text
                self.extracted_text.config(state="normal")
                self.extracted_text.delete("1.0", "end")
                self.extracted_text.insert("1.0", extracted_text)
                self.extracted_text.config(state="disabled")
                
                # Show success message
                messagebox.showinfo(
                    "Success! 🎉",
                    f"Text extracted successfully!\n\n"
                    f"📝 Extracted {len(extracted_text)} characters\n"
                    f"⏱️ Processing time: {stats['processing_time']:.2f} seconds\n\n"
                    f"Your secret message has been revealed!"
                )
                
                self.update_status("✅ Text extracted successfully")
                
            except Exception as e:
                self.extract_progress.stop_animation()
                messagebox.showerror("Error", f"Failed to extract text: {str(e)}")
                self.update_status("❌ Extract operation failed")
        
        threading.Thread(target=extract_thread, daemon=True).start()
    
    def analyze_image_action(self):
        """Analyze image capacity action"""
        if not self.current_analyze_image:
            messagebox.showerror("Error", "Please select an image to analyze")
            return
        
        def analyze_thread():
            try:
                self.analyze_progress.start_animation()
                self.update_status("Analyzing image capacity...")
                
                analysis = self.stegocrypt.analyze_image_capacity(self.current_analyze_image)
                
                self.analyze_progress.stop_animation()
                
                # Format analysis results
                results = f"""🔍 Image Analysis Results
{'=' * 60}

📁 File Information:
  Path: {analysis['image_path']}
  Size: {analysis['image_size'][0]} × {analysis['image_size'][1]} pixels
  Mode: {analysis['image_mode']}
  Format: {analysis['image_format']}
  Total Pixels: {analysis['total_pixels']:,}
  Color Channels: {analysis['color_channels']}

📊 Steganography Capacity:
  Raw Capacity: {analysis['raw_capacity_bytes']:,} bytes
  Estimated Text Capacity: ~{analysis['estimated_text_capacity_chars']:,} characters
  Recommended Max Text: ~{analysis['recommended_max_text_length']:,} characters

💡 Analysis Notes:
- Raw capacity assumes 1 bit per color channel (LSB steganography)
- Estimated capacity accounts for compression and encryption overhead
- Recommended max provides a safe margin for reliable operation
- Actual capacity may vary based on text content and compression ratio

🎯 Suitability Score: {analysis.get('suitability_score', 0.8) * 100:.1f}%

✅ Analysis completed successfully!
"""
                
                # Display results
                self.analysis_text.config(state="normal")
                self.analysis_text.delete("1.0", "end")
                self.analysis_text.insert("1.0", results)
                self.analysis_text.config(state="disabled")
                
                self.update_status("✅ Image analysis completed")
                
            except Exception as e:
                self.analyze_progress.stop_animation()
                messagebox.showerror("Error", f"Analysis failed: {str(e)}")
                self.update_status("❌ Analysis failed")
        
        threading.Thread(target=analyze_thread, daemon=True).start()
    
    def validate_system(self):
        """Validate system setup"""
        def validate_thread():
            try:
                self.update_status("Validating system...")
                
                results = self.stegocrypt.validate_setup()
                
                if all(results.values()):
                    self.update_status("✅ System validation passed - All systems operational")
                else:
                    self.update_status("⚠️ System validation issues detected")
                    
            except Exception as e:
                self.update_status(f"❌ System validation error: {str(e)}")
        
        threading.Thread(target=validate_thread, daemon=True).start()
    
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    app = StegoCryptModernGUI()
    app.run()


if __name__ == "__main__":
    main()
