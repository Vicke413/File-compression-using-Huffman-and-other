import os
import glob
import gzip
import zipfile
from PIL import Image

from flask import Flask, render_template, request, send_file, jsonify
from algorithms import compare_compression_algorithms
import os

def compress_file(input_filepath, output_filepath):
    
    file_extension = os.path.splitext(input_filepath)[1]
    
    result = compare_compression_algorithms(input_filepath, output_filepath)

    return result

# Configure Application
app = Flask(__name__)


app.config["FILE_UPLOADS"] = os.path.join(os.getcwd(), 'uploads')
app.config["UPLOAD_FOLDER"] = 'uploads'
app.config["DOWNLOAD_FOLDER"] = 'downloads'

# Create directories if they don't exist
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])
if not os.path.exists(app.config["DOWNLOAD_FOLDER"]):
    os.makedirs(app.config["DOWNLOAD_FOLDER"])

@app.route("/")
def home():
    # Clear old files
    filelist = glob.glob(f'{app.config["UPLOAD_FOLDER"]}/*')
    for f in filelist:
        os.remove(f)
    filelist = glob.glob(f'{app.config["DOWNLOAD_FOLDER"]}/*')
    for f in filelist:
        os.remove(f)
    return render_template("home.html")

# Compression Functions
def compress_text_file(input_filepath, output_filepath):
    """Compress text file using gzip."""
    try:
        with open(input_filepath, 'rb') as f_in:
            with gzip.open(output_filepath, 'wb') as f_out:
                f_out.writelines(f_in)
        print(f"Successfully compressed text file: {input_filepath} -> {output_filepath}")
    except Exception as e:
        print(f"Error during text file compression: {e}")
        raise e

def decompress_text_file(input_filepath, output_filepath):
    """Decompress gzip-compressed text file."""
    try:
        with gzip.open(input_filepath, 'rb') as f_in:
            with open(output_filepath, 'wb') as f_out:
                f_out.write(f_in.read())
        print(f"Successfully decompressed text file: {input_filepath} -> {output_filepath}")
    except Exception as e:
        print(f"Error during text file decompression: {e}")
        raise e

def compress_image(input_filepath, output_filepath, image_format='JPEG'):
    """Compress image using Pillow (JPEG or PNG)."""
    try:
        with Image.open(input_filepath) as img:
          
            if img.mode == 'RGBA':
                img = img.convert('RGB')  
            img.save(output_filepath, format=image_format, quality=85)
        print(f"Successfully compressed image: {input_filepath} -> {output_filepath}")
    except Exception as e:
        print(f"Error during image compression: {e}")
        raise e

def decompress_image(input_filepath, output_filepath):
    """Decompress image (no compression for decompressed files)."""
    try:
        with Image.open(input_filepath) as img:
            img.save(output_filepath)
        print(f"Successfully decompressed image: {input_filepath} -> {output_filepath}")
    except Exception as e:
        print(f"Error during image decompression: {e}")
        raise e

def compress_zip(input_filepath, output_filepath):
    """Compress file into a ZIP archive."""
    try:
        with zipfile.ZipFile(output_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(input_filepath, os.path.basename(input_filepath))
        print(f"Successfully compressed ZIP file: {input_filepath} -> {output_filepath}")
    except Exception as e:
        print(f"Error during ZIP file compression: {e}")
        raise e

def decompress_zip(input_filepath, output_filepath):
    """Decompress a ZIP archive."""
    try:
        with zipfile.ZipFile(input_filepath, 'r') as zipf:
            zipf.extractall(output_filepath)
        print(f"Successfully decompressed ZIP file: {input_filepath} -> {output_filepath}")
    except Exception as e:
        print(f"Error during ZIP file decompression: {e}")
        raise e

def handle_compression(input_filepath, output_filepath, file_extension):
    """Compress file based on its type."""
    if file_extension in ['.txt']:
        compress_text_file(input_filepath, output_filepath)
    elif file_extension in ['.jpg', '.jpeg', '.png']:
        compress_image(input_filepath, output_filepath)
    elif file_extension == '.zip':
        compress_zip(input_filepath, output_filepath)
    else:
        raise ValueError("Unsupported file type for compression")

def handle_decompression(input_filepath, output_filepath, file_extension):
    """Decompress file based on its type."""
    if file_extension == '.gz':
        decompress_text_file(input_filepath, output_filepath)
    elif file_extension in ['.jpg', '.jpeg', '.png']:
        decompress_image(input_filepath, output_filepath)
    elif file_extension == '.zip':
        decompress_zip(input_filepath, output_filepath)
    else:
        raise ValueError("Unsupported file type for decompression")

@app.route("/compress", methods=["GET", "POST"])
def compress():
    if request.method == "GET":
        return render_template("compress.html", check=0)
    else:
        up_file = request.files["file"]

        if len(up_file.filename) > 0:
            filename = up_file.filename
            filepath = os.path.join(app.config["FILE_UPLOADS"], filename)
            up_file.save(filepath)

            file_extension = os.path.splitext(filename)[1].lower()
            compressed_filepath = os.path.join(app.config["DOWNLOAD_FOLDER"], filename)

            try:
                # Set the output file name with the proper extension
                if file_extension in ['.txt']:
                    compressed_filepath += '.gz'  # For text files, append .gz
                elif file_extension in ['.jpg', '.jpeg', '.png']:
                    compressed_filepath += ''  # For images, keep the original file extension
                elif file_extension == '.zip':
                    compressed_filepath += ''  # For zip files, keep the .zip extension
                else:
                    raise ValueError("Unsupported file type for compression")
                
                # Perform compression
                handle_compression(filepath, compressed_filepath, file_extension)

                return render_template("compress.html", check=1, filename=compressed_filepath)

            except ValueError as e:
                print(f"Error during compression: {e}")
                return render_template("compress.html", check=-1, error="Unsupported file type for compression")

        else:
            return render_template("compress.html", check=-1)

@app.route("/decompress", methods=["GET", "POST"])
def decompress():
    if request.method == "GET":
        return render_template("decompress.html", check=0)
    else:
        up_file = request.files["file"]

        if len(up_file.filename) > 0:
            filename = up_file.filename
            filepath = os.path.join(app.config["FILE_UPLOADS"], filename)
            up_file.save(filepath)

            file_extension = os.path.splitext(filename)[1].lower()
            decompressed_filepath = os.path.join(app.config["DOWNLOAD_FOLDER"], filename.replace(file_extension, '-decompressed' + file_extension))

            try:
                # Perform decompression based on file type
                handle_decompression(filepath, decompressed_filepath, file_extension)

                return render_template("decompress.html", check=1, filename=decompressed_filepath)

            except ValueError as e:
                print(f"Error during decompression: {e}")
                return render_template("decompress.html", check=-1, error="Unsupported file type for decompression")

        else:
            return render_template("decompress.html", check=-1)
        

# Download File Route
@app.route("/download")
def download_file():
    filename = request.args.get('filename')
    if filename:
        path = os.path.join(app.config["DOWNLOAD_FOLDER"], filename)
        if os.path.exists(path):
            return send_file(path, as_attachment=True)
    return "Error: File not found", 404

if __name__ == "__main__":
    app.run(debug=True)
