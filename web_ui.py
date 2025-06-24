"""
Web-based User Interface for StegoCrypt
Flask-based web application for steganography operations
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import tempfile
import base64
from io import BytesIO
from PIL import Image
import traceback
from stegocrypt import StegoCrypt

app = Flask(__name__)
app.secret_key = 'stegocrypt_web_ui_secret_key_2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize StegoCrypt
stego = StegoCrypt()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/hide', methods=['GET', 'POST'])
def hide_text():
    """Hide text in image"""
    if request.method == 'GET':
        return render_template('hide.html')
    
    try:
        # Get form data
        text = request.form.get('text', '').strip()
        password = request.form.get('password', '').strip()
        use_lzma = request.form.get('compression') == 'lzma'
        
        # Get uploaded file
        if 'image' not in request.files:
            return jsonify({'error': 'No image file uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        if not text:
            return jsonify({'error': 'No text to hide'}), 400
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_input:
            file.save(temp_input.name)
            
            # Create output file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_output:
                # Hide text in image
                stats = stego.hide_text_in_image(
                    temp_input.name,
                    text,
                    password,
                    temp_output.name,
                    use_lzma=use_lzma
                )
                
                # Read the result image
                with open(temp_output.name, 'rb') as f:
                    image_data = f.read()
                
                # Clean up temp files
                os.unlink(temp_input.name)
                os.unlink(temp_output.name)
                
                # Convert to base64 for display
                image_b64 = base64.b64encode(image_data).decode('utf-8')
                
                return jsonify({
                    'success': True,
                    'image_data': image_b64,
                    'stats': stats,
                    'message': 'Text successfully hidden in image!'
                })
    
    except Exception as e:
        return jsonify({'error': f'Error hiding text: {str(e)}'}), 500

@app.route('/extract', methods=['GET', 'POST'])
def extract_text():
    """Extract text from image"""
    if request.method == 'GET':
        return render_template('extract.html')
    
    try:
        # Get form data
        password = request.form.get('password', '').strip()
        
        # Get uploaded file
        if 'image' not in request.files:
            return jsonify({'error': 'No image file uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        if not password:
            return jsonify({'error': 'Password is required'}), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            file.save(temp_file.name)
            
            # Extract text from image
            extracted_text, stats = stego.extract_text_from_image(
                temp_file.name,
                password
            )
            
            # Clean up temp file
            os.unlink(temp_file.name)
            
            return jsonify({
                'success': True,
                'text': extracted_text,
                'stats': stats,
                'message': 'Text successfully extracted from image!'
            })
    
    except Exception as e:
        return jsonify({'error': f'Error extracting text: {str(e)}'}), 500

@app.route('/analyze', methods=['GET', 'POST'])
def analyze_image():
    """Analyze image capacity"""
    if request.method == 'GET':
        return render_template('analyze.html')
    
    try:
        # Get uploaded file
        if 'image' not in request.files:
            return jsonify({'error': 'No image file uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            file.save(temp_file.name)
            
            # Analyze image capacity
            analysis = stego.analyze_image_capacity(temp_file.name)
            
            # Clean up temp file
            os.unlink(temp_file.name)
            
            return jsonify({
                'success': True,
                'analysis': analysis,
                'message': 'Image analysis completed!'
            })
    
    except Exception as e:
        return jsonify({'error': f'Error analyzing image: {str(e)}'}), 500

@app.route('/demo')
def demo():
    """Demo page"""
    try:
        # Create a demo image
        demo_image = stego.create_test_image('demo_web.png', (600, 400))
        
        # Convert to base64 for display
        img_buffer = BytesIO()
        demo_image.save(img_buffer, format='PNG')
        img_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        # Get capacity analysis
        analysis = stego.analyze_image_capacity('demo_web.png')
        
        # Clean up
        if os.path.exists('demo_web.png'):
            os.unlink('demo_web.png')
        
        return render_template('demo.html', 
                             demo_image=img_data, 
                             analysis=analysis)
    
    except Exception as e:
        return render_template('demo.html', 
                             error=f'Error creating demo: {str(e)}')

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    print("🌐 Starting StegoCrypt Web UI...")
    print("📱 Access the application at: http://localhost:5000")
    print("🔐 Features: Hide text, Extract text, Analyze capacity, Demo")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
