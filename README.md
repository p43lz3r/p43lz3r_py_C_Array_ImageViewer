# p43lz3r_py_C_Array_ImageViewer
Can show the RGB656 images from a C header file

# RGB565 Image Viewer for C Header Files

A Python tool to visualize image data stored C arrays in C header files.

## Overview

When working with embedded graphics, images are often converted to RGB565 format and stored as C arrays in header files. This tool allows you to preview these images on your computer before flashing to your microcontroller, making it easier to debug display issues and verify your graphics.

## Features

- ✅ **Multi-array support** - Handle multiple images in a single header file
- ✅ **Smart dimension matching** - Automatically pairs arrays with their width/height definitions  
- ✅ **Comment filtering** - Safely ignores inline comments that could corrupt pixel data
- ✅ **Robust parsing** - Works with various C array formats (`const unsigned short`, `uint16_t`, etc.)
- ✅ **PROGMEM support** - Handles Arduino PROGMEM declarations
- ✅ **Automatic saving** - Saves each image as PNG with descriptive filenames
- ✅ **Dimension guessing** - Attempts to infer dimensions from common screen sizes
- ✅ **Detailed analysis** - Shows statistics and debug information for each array

## Requirements

```bash
pip install numpy pillow matplotlib
```

## Usage

### Basic Usage

1. Place your C header file in the same directory as the script
2. Update the filename in the script:
   ```python
   header_filename = "your_image_file.h"  # Change this line
   ```
3. Run the script:
   ```bash
   python multi_array_viewer.py
   ```

### Supported Header File Formats

The tool works with standard C header files containing RGB565 image data:

```c
// Dimensions
const uint16_t logoWidth = 64;
const uint16_t logoHeight = 32;

// Image data
const unsigned short logoImage[0x800] PROGMEM = {
    0x1082, 0x1082, 0x0861, 0x0841,   // Optional comments
    0x0020, 0x0000, 0x0000, 0x0000,   // 0x0010 (16)
    // ... more pixel data
};
```

### Multiple Arrays Example

```c
// Setup screen
const uint16_t setupModeWidth = 320;
const uint16_t setupModeHeight = 170;
const unsigned short setupModeScreen[0xFC58] PROGMEM = { /* data */ };

// Logo image  
const uint16_t logoWidth = 64;
const uint16_t logoHeight = 32;
const unsigned short logoImage[0x800] PROGMEM = { /* data */ };
```

## How It Works

1. **File Parsing**: Scans the header file for dimension definitions and array declarations
2. **Smart Matching**: Pairs arrays with dimensions based on name similarity (e.g., `logoImage` → `logoWidth/logoHeight`)
3. **Data Extraction**: Extracts hex values while filtering out comment artifacts
4. **RGB Conversion**: Converts RGB565 format to standard RGB888 for display
5. **Image Generation**: Creates PIL images and displays them using matplotlib

## Common Use Cases

- **Arduino TFT Projects**: Preview splash screens and UI graphics for ILI9341, ST7735, etc.
- **Embedded Graphics**: Debug image conversion issues before deployment
- **Image Verification**: Ensure converted images look correct before burning to flash
- **Batch Processing**: Handle multiple images/icons in a single header file

## Troubleshooting

### No Images Displayed
- Check that your header file contains valid RGB565 arrays
- Verify dimension definitions are present or use common sizes (320x240, 128x64, etc.)

### Corrupted/Distorted Images
- Ensure hex values in comments aren't being extracted as pixel data
- Verify your RGB565 data is in little-endian format (most common)
- Check that array size matches width × height

### Wrong Dimensions
- Make sure width/height variable names match or are similar to array names
- Add explicit dimension definitions if missing
- The tool will attempt to guess common screen dimensions

## Technical Details

- **RGB565 Format**: 16-bit color format (5-bit red, 6-bit green, 5-bit blue)
- **Endianness**: Handles standard little-endian RGB565 format
- **Memory Layout**: Expects row-major pixel ordering (left-to-right, top-to-bottom)

## Example Output

```
Reading multi-array C header file: images.h

=== ANALYSIS RESULTS ===
Found 2 dimension definitions
Found 2 array declarations

=== ARRAY ANALYSIS ===

Array 1: setupModeScreen
  Matched dimensions: 320x170 (setupMode)
  Expected pixels: 54400
  Found pixels: 54400
  Saved: setupModeScreen.png

Array 2: logoImage  
  Matched dimensions: 64x32 (logo)
  Expected pixels: 2048
  Found pixels: 2048
  Saved: logoImage.png
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests for:
- Additional image format support
- Better dimension detection algorithms
- UI improvements
- Bug fixes

## License

MIT License - feel free to use in your projects!

## Related Tools

This tool pairs well with:
- [LCD Image Converter](https://github.com/riuson/lcd-image-converter) - Convert images to C arrays
- [TFT_eSPI Library](https://github.com/Bodmer/TFT_eSPI) - Arduino TFT display library
- [LVGL](https://lvgl.io/) - Embedded graphics library

---

**Happy coding!** 🚀 If this tool helped you debug your embedded graphics, consider giving it a ⭐
