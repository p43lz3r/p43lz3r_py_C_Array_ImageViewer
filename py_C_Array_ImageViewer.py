#!/usr/bin/env python3
"""
Multi-Array RGB565 Viewer for C Header Files
Handles multiple RGB565 arrays in a single header file
"""

import re
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def rgb565_to_rgb888(rgb565):
    """Convert RGB565 to RGB888 format"""
    r = (rgb565 >> 11) & 0x1F  # 5 bits
    g = (rgb565 >> 5) & 0x3F   # 6 bits  
    b = rgb565 & 0x1F          # 5 bits
    
    # Scale to 8-bit values
    r = (r * 255) // 31
    g = (g * 255) // 63
    b = (b * 255) // 31
    
    return (r, g, b)

def find_all_dimensions(content):
    """Find all width/height definitions in the file"""
    width_matches = re.findall(r'(\w*[Ww]idth\w*)\s*=\s*(\d+)', content)
    height_matches = re.findall(r'(\w*[Hh]eight\w*)\s*=\s*(\d+)', content)
    
    print("=== FOUND DIMENSIONS ===")
    print(f"Width definitions: {width_matches}")
    print(f"Height definitions: {height_matches}")
    
    # Create dimension pairs by matching similar names
    dimensions = {}
    for width_name, width_val in width_matches:
        # Try to find matching height
        base_name = width_name.replace('Width', '').replace('width', '').replace('WIDTH', '')
        
        for height_name, height_val in height_matches:
            if base_name.lower() in height_name.lower():
                dimensions[base_name] = (int(width_val), int(height_val))
                break
    
    return dimensions

def find_all_arrays(content):
    """Find all array declarations in the file"""
    # Pattern to match array declarations
    pattern = r'(?:const\s+)?(?:unsigned\s+)?(?:short|int|uint16_t)\s+(\w+)\[([^\]]*)\]\s*(?:PROGMEM\s*)?=\s*\{'
    
    arrays = []
    for match in re.finditer(pattern, content, re.IGNORECASE):
        array_name = match.group(1)
        array_size = match.group(2)
        start_pos = match.start()
        
        # Find the opening brace
        brace_pos = content.find('{', start_pos)
        if brace_pos == -1:
            continue
            
        # Find matching closing brace
        brace_count = 0
        end_pos = brace_pos
        for i, char in enumerate(content[brace_pos:], brace_pos):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i
                    break
        
        arrays.append({
            'name': array_name,
            'size': array_size,
            'start': brace_pos,
            'end': end_pos,
            'declaration': match.group(0)
        })
    
    return arrays

def extract_array_data(content, array_info):
    """Extract pixel data from a specific array"""
    array_content = content[array_info['start']+1:array_info['end']]
    
    # Extract hex values while filtering out comments
    lines = array_content.split('\n')
    hex_values = []
    
    for line in lines:
        # Remove comments first
        comment_pos = line.find('//')
        if comment_pos != -1:
            line = line[:comment_pos]
        
        # Extract hex values from the cleaned line
        line_hex = re.findall(r'0x([0-9A-Fa-f]+)', line, re.IGNORECASE)
        hex_values.extend(line_hex)
    
    # Convert to integers
    pixel_data = [int(val, 16) for val in hex_values]
    
    return pixel_data

def match_arrays_to_dimensions(arrays, dimensions, content):
    """Try to match array names to dimension definitions"""
    matches = []
    
    for array in arrays:
        array_name = array['name']
        best_match = None
        
        # Try to find dimension set that matches array name
        for dim_name, (width, height) in dimensions.items():
            if dim_name.lower() in array_name.lower() or array_name.lower() in dim_name.lower():
                best_match = (dim_name, width, height)
                break
        
        if not best_match:
            # Try to guess dimensions from array size
            try:
                if array['size'].startswith('0x'):
                    array_size = int(array['size'], 16)
                else:
                    array_size = int(array['size'])
                
                # Try common screen dimensions
                common_dims = [(320, 240), (240, 320), (320, 170), (128, 64), (128, 128), (96, 96), (64, 64)]
                for w, h in common_dims:
                    if w * h == array_size:
                        best_match = (f"guessed_{w}x{h}", w, h)
                        break
            except:
                pass
        
        matches.append({
            'array': array,
            'dimensions': best_match,
            'pixel_count': len(extract_array_data(content, array)) if best_match else 0
        })
    
    return matches

def create_image_from_data(width, height, pixel_data):
    """Create PIL Image from RGB565 pixel data"""
    expected_pixels = width * height
    
    if len(pixel_data) > expected_pixels:
        print(f"  Truncating {len(pixel_data)} pixels to {expected_pixels}")
        pixel_data = pixel_data[:expected_pixels]
    elif len(pixel_data) < expected_pixels:
        print(f"  Padding {len(pixel_data)} pixels to {expected_pixels}")
        pixel_data = pixel_data + [0] * (expected_pixels - len(pixel_data))
    
    # Convert RGB565 to RGB888
    rgb_data = []
    for pixel in pixel_data:
        r, g, b = rgb565_to_rgb888(pixel)
        rgb_data.extend([r, g, b])
    
    # Create PIL Image
    rgb_array = np.array(rgb_data, dtype=np.uint8).reshape(height, width, 3)
    image = Image.fromarray(rgb_array)
    
    return image

def display_image(image, title):
    """Display image using matplotlib"""
    plt.figure(figsize=(12, 8))
    plt.imshow(image)
    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    plt.show()

def main():
    header_filename = "images_320_170.h"  # Change this to your header file name
    
    try:
        print(f"Reading multi-array C header file: {header_filename}")
        
        with open(header_filename, 'r') as f:
            content = f.read()
        
        # Find all dimensions and arrays
        dimensions = find_all_dimensions(content)
        arrays = find_all_arrays(content)
        
        print(f"\n=== ANALYSIS RESULTS ===")
        print(f"Found {len(dimensions)} dimension definitions")
        print(f"Found {len(arrays)} array declarations")
        
        if not arrays:
            print("No arrays found!")
            return
        
        # Match arrays to dimensions
        matches = match_arrays_to_dimensions(arrays, dimensions, content)
        
        print(f"\n=== ARRAY ANALYSIS ===")
        for i, match in enumerate(matches):
            array = match['array']
            dims = match['dimensions']
            
            print(f"\nArray {i+1}: {array['name']}")
            print(f"  Declaration: {array['declaration']}")
            print(f"  Array size: {array['size']}")
            
            if dims:
                dim_name, width, height = dims
                print(f"  Matched dimensions: {width}x{height} ({dim_name})")
                print(f"  Expected pixels: {width * height}")
                
                # Extract and analyze data
                pixel_data = extract_array_data(content, array)
                print(f"  Found pixels: {len(pixel_data)}")
                
                if len(pixel_data) > 0:
                    print(f"  Data range: 0x{min(pixel_data):04X} to 0x{max(pixel_data):04X}")
                    
                    # Create and display image
                    try:
                        image = create_image_from_data(width, height, pixel_data)
                        title = f"{array['name']} ({width}x{height})"
                        display_image(image, title)
                        
                        # Save image
                        output_filename = f"{array['name']}.png"
                        image.save(output_filename)
                        print(f"  Saved: {output_filename}")
                        
                    except Exception as e:
                        print(f"  Error creating image: {e}")
            else:
                print("  No matching dimensions found")
        
        # Interactive selection if multiple arrays found
        if len([m for m in matches if m['dimensions']]) > 1:
            print(f"\n=== INTERACTIVE SELECTION ===")
            valid_matches = [m for m in matches if m['dimensions']]
            
            print("Multiple valid arrays found:")
            for i, match in enumerate(valid_matches):
                array_name = match['array']['name']
                dims = match['dimensions']
                print(f"  {i+1}. {array_name} ({dims[1]}x{dims[2]})")
            
            print("\nAll images have been displayed and saved automatically.")
            print("You can also run the script again and modify the array selection logic if needed.")
        
    except FileNotFoundError:
        print(f"Error: Could not find file '{header_filename}'")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
