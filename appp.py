import os
import subprocess
import glob
import bz2
from flask import Flask, render_template, request, send_file

# Configure Application
app = Flask(__name__)

# File paths and directories
app.config["FILE_UPLOADS"] = "/Users/dheerajsayam/Downloads"
app.config["UPLOAD_FOLDER"] = 'uploads'
app.config["DOWNLOAD_FOLDER"] = 'downloads'

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

# Function to call C++ Huffman compression executable
def compress_huffman(input_filepath, output_filepath):
    try:
        subprocess.run(['./huffcompress', input_filepath, output_filepath], check=True)
        print(f"Successfully compressed file: {input_filepath} -> {output_filepath}")
    except subprocess.CalledProcessError as e:
        print(f"Error during Huffman compression: {e}")
        raise e

# Function to call C++ Huffman decompression executable
def decompress_huffman(input_filepath, output_filepath):
    try:
        subprocess.run(['./huffdecompress', input_filepath, output_filepath], check=True)
        print(f"Successfully decompressed file: {input_filepath} -> {output_filepath}")
    except subprocess.CalledProcessError as e:
        print(f"Error during Huffman decompression: {e}")
        raise e

# Function to handle RLE compression (Basic RLE logic as an example)
def compress_rle(input_filepath, output_filepath):
    with open(input_filepath, 'r') as input_file:
        data = input_file.read()
    compressed_data = ''
    count = 1
    for i in range(1, len(data)):
        if data[i] == data[i-1]:
            count += 1
        else:
            compressed_data += str(count) + data[i-1]
            count = 1
    compressed_data += str(count) + data[-1]

    with open(output_filepath, 'w') as output_file:
        output_file.write(compressed_data)

# Function to handle RLE decompression
def decompress_rle(input_filepath, output_filepath):
    with open(input_filepath, 'r') as input_file:
        data = input_file.read()
    decompressed_data = ''
    i = 0
    while i < len(data):
        count = int(data[i])
        char = data[i + 1]
        decompressed_data += char * count
        i += 2
    
    with open(output_filepath, 'w') as output_file:
        output_file.write(decompressed_data)

# LZW Compression (Simplified version)
def compress_lzw(input_filepath, output_filepath):
    with open(input_filepath, 'r') as file:
        data = file.read()

    # Create a dictionary to map string patterns to integers
    dictionary = {chr(i): i for i in range(256)}
    code = 256
    s = ""
    compressed_data = []
    
    for c in data:
        sc = s + c
        if sc in dictionary:
            s = sc
        else:
            compressed_data.append(dictionary[s])
            dictionary[sc] = code
            code += 1
            s = c
    if s:
        compressed_data.append(dictionary[s])

    # Save compressed data as binary
    with open(output_filepath, 'wb') as file:
        for code in compressed_data:
            file.write(code.to_bytes(2, byteorder='big'))  # Each code is 2 bytes

# BZIP2 Compression using Python's bz2 library
def compress_bzip2(input_filepath, output_filepath):
    with open(input_filepath, 'rb') as file:
        data = file.read()
    with bz2.BZ2File(output_filepath, 'wb') as f:
        f.write(data)

# Function to calculate file size in bytes
def get_file_size(filepath):
    return os.path.getsize(filepath)

# Handling compression for files based on extension and comparing results
def handle_compression(input_filepath, output_filepath, file_extension):
    """Compress file based on its type and compare results."""
    best_algorithm = None
    best_size = float('inf')
    best_filepath = None
    
    # Test Huffman compression
    if file_extension == '.txt':
        compress_huffman(input_filepath, output_filepath + '.huff')
        huff_size = get_file_size(output_filepath + '.huff')
        if huff_size < best_size:
            best_size = huff_size
            best_filepath = output_filepath + '.huff'
            best_algorithm = "Huffman"

    # Test LZW compression
    compress_lzw(input_filepath, output_filepath + '.lzw')
    lzw_size = get_file_size(output_filepath + '.lzw')
    if lzw_size < best_size:
        best_size = lzw_size
        best_filepath = output_filepath + '.lzw'
        best_algorithm = "LZW"

    # Test BZIP2 compression
    compress_bzip2(input_filepath, output_filepath + '.bz2')
    bzip2_size = get_file_size(output_filepath + '.bz2')
    if bzip2_size < best_size:
        best_size = bzip2_size
        best_filepath = output_filepath + '.bz2'
        best_algorithm = "BZIP2"

    # Test RLE compression
    compress_rle(input_filepath, output_filepath + '.rle')
    rle_size = get_file_size(output_filepath + '.rle')
    if rle_size < best_size:
        best_size = rle_size
        best_filepath = output_filepath + '.rle'
        best_algorithm = "RLE"

    return best_algorithm, best_filepath

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
                # Perform compression and comparison
                best_algorithm, best_compressed_filepath = handle_compression(filepath, compressed_filepath, file_extension)

                return render_template("compress.html", check=1, filename=best_compressed_filepath, algorithm=best_algorithm)

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
