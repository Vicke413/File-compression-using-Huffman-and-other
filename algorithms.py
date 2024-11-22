import os
import heapq
import gzip
from collections import defaultdict
from lzw import lzw_compress
from huffman import huffman_compress


# RLE 
def rle_compress(input_filepath, output_filepath):
    """Compress a text file using Run-Length Encoding (RLE)."""
    try:
        with open(input_filepath, "r") as f_in:
            data = f_in.read()

        encoded_data = []
        i = 0
        while i < len(data):
            count = 1
            while i + 1 < len(data) and data[i] == data[i + 1]:
                i += 1
                count += 1
            encoded_data.append((data[i], count))
            i += 1
        
        with open(output_filepath, "w") as f_out:
            for char, count in encoded_data:
                f_out.write(f"{char}{count}")
        return "RLE Compression"
    except Exception as e:
        print(f"Error during RLE compression: {e}")
        raise e


# GZIP 
def gzip_compress(input_filepath, output_filepath):
    """Compress a file using GZIP."""
    try:
        with open(input_filepath, "rb") as f_in:
            with gzip.open(output_filepath, "wb") as f_out:
                f_out.writelines(f_in)
        return "GZIP Compression"
    except Exception as e:
        print(f"Error during GZIP compression: {e}")
        raise e


# Huffman 
def huffman_compress(input_filepath, output_filepath):
    """Compress a text file using Huffman coding."""
    try:
    
        with open(input_filepath, "r") as f_in:
            data = f_in.read()
        
        freq = defaultdict(int)
        for char in data:
            freq[char] += 1
        
        heap = [[weight, [char, ""]] for char, weight in freq.items()]
        heapq.heapify(heap)
        
        while len(heap) > 1:
            lo = heapq.heappop(heap)
            hi = heapq.heappop(heap)
            for pair in lo[1:]:
                pair[1] = '0' + pair[1]
            for pair in hi[1:]:
                pair[1] = '1' + pair[1]
            heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
        
        huffman_code = sorted(heap[0][1:], key=lambda p: (len(p[-1]), p))
        
        huff_dict = {item[0]: item[1] for item in huffman_code}
        
        encoded_data = ''.join(huff_dict[char] for char in data)
        
        with open(output_filepath, "wb") as f_out:
            f_out.write(bytes(encoded_data, 'utf-8'))
        
        return "Huffman Compression"
    except Exception as e:
        print(f"Error during Huffman compression: {e}")
        raise e


# LZW C
def lzw_compress(input_filepath, output_filepath):
    """Compress a text file using LZW compression."""
    try:
        with open(input_filepath, "r") as f_in:
            data = f_in.read()
        
        dictionary = {chr(i): i for i in range(256)}
        result = []
        w = ""
        code = 256
        
        for char in data:
            wc = w + char
            if wc in dictionary:
                w = wc
            else:
                result.append(dictionary[w])
                dictionary[wc] = code
                code += 1
                w = char
        
        if w:
            result.append(dictionary[w])
        
        with open(output_filepath, "wb") as f_out:
            for item in result:
                f_out.write(item.to_bytes(2, 'big'))
        
        return "LZW Compression"
    except Exception as e:
        print(f"Error during LZW compression: {e}")
        raise e


# Compare 
def compare_compression_algorithms(input_filepath, output_filepath):
    """Compress the text file using multiple algorithms and select the best based on file size."""
    
    gzip_output = output_filepath + ".gzip"
    huffman_output = output_filepath + ".huff"
    lzw_output = output_filepath + ".lzw"
    rle_output = output_filepath + ".rle"

    # Apply all compression algorithms
    gzip_result = gzip_compress(input_filepath, gzip_output)
    huffman_result = huffman_compress(input_filepath, huffman_output)
    lzw_result = lzw_compress(input_filepath, lzw_output)
    rle_result = rle_compress(input_filepath, rle_output)

    file_sizes = {
        "GZIP": os.path.getsize(gzip_output),
        "Huffman": os.path.getsize(huffman_output),
        "LZW": os.path.getsize(lzw_output),
        "RLE": os.path.getsize(rle_output),
    }
    
    
    best_algorithm = min(file_sizes, key=file_sizes.get)

    if best_algorithm == "GZIP":
        os.rename(gzip_output, output_filepath)
    elif best_algorithm == "Huffman":
        os.rename(huffman_output, output_filepath)
    elif best_algorithm == "LZW":
        os.rename(lzw_output, output_filepath)
    elif best_algorithm == "RLE":
        os.rename(rle_output, output_filepath)
    
    for algo, path in zip(["GZIP", "Huffman", "LZW", "RLE"], [gzip_output, huffman_output, lzw_output, rle_output]):
        if algo != best_algorithm:
            os.remove(path)
    
    return f"Best Algorithm: {best_algorithm}"
def hybrid_compress(input_filepath, output_filepath):
    """Apply Hybrid Compression using RLE followed by Huffman."""
    try:
        # Step 1: Apply RLE compression
        temp_rle_output = "temp_rle_output.txt"
        rle_compress(input_filepath, temp_rle_output)

        huffman_compress(temp_rle_output, output_filepath)

        # Clean up the temporary RLE file
        os.remove(temp_rle_output)

        print(f"Hybrid Compression (RLE + Huffman) Complete: {output_filepath}")
        return output_filepath
    except Exception as e:
        print(f"Error during Hybrid compression: {e}")
        raise e


# Example usage:
input_filepath = "example.txt"  
output_filepath = "compressed_output.txt"  

# Perform Hybrid Compression (RLE + Huffman)
# s


def handle_compression(input_filepath, output_filepath, file_extension):
    """Decide and apply the best compression algorithm based on file type."""
    if file_extension in [".txt", ".csv", ".log"]:
        return compare_compression_algorithms(input_filepath, output_filepath)
    elif file_extension in [".jpg", ".jpeg", ".png"]:
        # Implement image compression logic
        return "Image Compression"
    elif file_extension == ".pdf":
        # Implement PDF compression logic
        return "PDF Compression"
    else:
        # Implement binary file compression logic
        return "Binary Compression"
