import struct
import io
from PIL import Image

# Dummy function derived from core/cursor.py to get simple .cur binary
def build_simple_cur(img):
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    png_data = img_byte_arr.getvalue()
    w, h = img.size
    w = 0 if w == 256 else w
    h = 0 if h == 256 else h
    header = struct.pack('<HHH', 0, 2, 1) # 1 image
    entry = struct.pack('<BBBBHHII', w, h, 0, 0, 0, 0, len(png_data), 22)
    return header + entry + png_data

def build_ani(frames_cur, jif_rate=10):
    # jif_rate is in 1/60th second. 10 jifs = 1/6 sec = ~166ms
    c_frames = len(frames_cur)
    
    # build fram list
    fram_chunks = b""
    for f in frames_cur:
        fram_chunks += b"icon" + struct.pack("<I", len(f)) + f
        
    # RIFF sizes padding (each chunk must be padded to 2-byte boundary, but sizes here are exact)
    # fram list size:
    fram_list_data = b"fram" + fram_chunks
    fram_list_chunk = b"LIST" + struct.pack("<I", len(fram_list_data)) + fram_list_data
    
    # anih chunk
    # cbSize(36), cFrames, cSteps, cx(0), cy(0), cBitCount(0), cPlanes(0), JifRate, flags(1)
    anih_data = struct.pack("<IIIIIIIII", 36, c_frames, c_frames, 0, 0, 0, 0, jif_rate, 1)
    anih_chunk = b"anih" + struct.pack("<I", len(anih_data)) + anih_data
    
    # ACON size
    acon_data = anih_chunk + fram_list_chunk
    riff = b"RIFF" + struct.pack("<I", len(acon_data) + 4) + b"ACON" + acon_data
    
    return riff

if __name__ == "__main__":
    # Create 3 frames of different colors
    frames = []
    for c in [(255,0,0), (0,255,0), (0,0,255)]:
        img = Image.new("RGBA", (32, 32), c)
        frames.append(build_simple_cur(img))
        
    ani_data = build_ani(frames, 10)
    with open("test.ani", "wb") as f:
        f.write(ani_data)
    print("test.ani generated")
