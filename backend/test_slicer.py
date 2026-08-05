

import math
import base64

def prepare_file_chunks(fake_large_file_data: str, chunk_size: int):
    # Convert the text into raw bytes (just like a movie file would be read)
    file_bytes = fake_large_file_data.encode('utf-8')
    total_bytes = len(file_bytes)
    
    # Calculate how many pieces we need
    total_chunks = math.ceil(total_bytes / chunk_size)
    
    print(f"Total File Size: {total_bytes} bytes")
    print(f"Slicing into {total_chunks} chunks (size: {chunk_size} bytes each)\n")
    
    chunks_list = []
    for i in range(total_chunks):
        start = i * chunk_size
        end = start + chunk_size
        
        # Slice the raw bytes
        chunk_data = file_bytes[start:end]
        
        # WebSockets handle text data best via JSON. 
        # To safely embed raw binary bytes inside a JSON object, we encode it to Base64.
        b64_encoded = base64.b64encode(chunk_data).decode('utf-8')
        
        chunk_packet = {
            "type": "file_chunk",
            "target_id": "phone_b",
            "filename": "mock_movie.mp4",
            "chunk_index": i,
            "total_chunks": total_chunks,
            "payload": b64_encoded
        }
        chunks_list.append(chunk_packet)
        
    return chunks_list

# Simulate a "movie file" using a long repeating string
mock_movie = "SUPER_LONG_MOVIE_BINARY_DATA_STREAM_" * 10 
all_prepared_packets = prepare_file_chunks(mock_movie, chunk_size=15)

# Let's inspect the first 2 prepared packets
print("🔍 First prepared packet:")
print(all_prepared_packets[0])
print("\n🔍 Second prepared packet:")
print(all_prepared_packets[1])