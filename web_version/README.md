2025-02-20 14:30 v1.2.0

# C Array Image Viewer - Web Application

A powerful web-based tool for visualizing embedded image arrays from C source files. Upload and preview multiple image formats instantly in your browser.

## Features

### File Management
- **Multi-file Upload** - Drag & drop or select multiple `.c`/`.h` files
- **Batch Processing** - Automatically extracts all images from each file
- **File List** - View all loaded images with dimensions and filenames
- **Quick Remove** - Delete individual images without clearing everything
- **Clear All** - Reset and start over

### Image Support
- **RGB565** (standard embedded format, 65K colors)
- **RGB565 + Alpha** (LVGL, with transparency)
- **Monochrome 1-bit** (black & white, minimal memory)
- **4-bit Grayscale** (16 levels)
- **8-bit Grayscale** (256 levels)
- **RGB888** (24-bit true color)
- **ARGB8888** (32-bit with transparency)

### Image Rendering
- **Live Canvas Preview** - Real-time pixel-perfect rendering
- **Auto-scaling** - Adapts to window size
- **Pixel-perfect Display** - Sharp rendering for small images

### Image Controls
- **Navigation** - Back/Next buttons to browse through images
- **Color Inversion** - Toggle RGB value inversion on any image
- **PNG Export** - Download images as standard PNG files

### Parser Features
- **Comment Filtering** - Automatically removes C comments
- **SquareLine Support** - Compatible with SquareLine Studio exports
- **Format Detection** - Auto-detects format based on array size
- **Flexible Parsing** - Supports nested and flat header structures
- **Validation** - Verifies dimensions match data size

### Information Display
- **Image Dimensions** - Width × Height in pixels
- **Color Format** - Shows detected or specified format
- **Data Size** - Total bytes in the array
- **Pixel Count** - Total pixels in image

## How to Use

1. **Load Files** - Drag `.c`/`.h` files onto the upload area or click Select Files
2. **View Images** - Click any image in the list to preview
3. **Navigate** - Use Back/Next buttons to scroll through images
4. **Process** - Invert colors if needed
5. **Export** - Download as PNG

## Technical Details

### Input Format
Expects standard LVGL image structure:
```c
const uint8_t image_data[] = { 0x00, 0xFF, ... };
const lv_img_dsc_t image = {
    .header.w = 50,
    .header.h = 50,
    .header.cf = LV_IMG_CF_TRUE_COLOR_ALPHA,
    .data = image_data
};
```

### Color Formats Supported
- `LV_IMG_CF_INDEXED_1BIT` - 1-bit monochrome
- `LV_IMG_CF_INDEXED_4BIT` - 4-bit indexed
- `LV_IMG_CF_TRUE_COLOR` - RGB565
- `LV_IMG_CF_TRUE_COLOR_ALPHA` - RGB565 + Alpha
- Any format with correct width/height

### Processing
- **100% Client-Side** - No server required
- **In-Browser** - All processing in your browser's memory
- **No Upload** - Files never leave your device
- **Instant Results** - Images render immediately

## Browser Support

Works on all modern browsers:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS, Android)

## Requirements

- Modern web browser
- 2 files only: `index.html` and `app.js`
- Any web server (static files only)

## Deployment

1. Upload `index.html` and `app.js` to your web server
2. Open in browser
3. Done - no installation needed

---

Made for embedded developers working with LVGL and image arrays.
