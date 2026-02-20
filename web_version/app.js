/**
 * C Array Image Viewer - Web Application
 * Version: 1.2.0
 * Created: 2025-02-20
 */

class CArrayImageViewer {
    constructor() {
        this.files = new Map();
        this.currentFile = null;
        this.isInverted = false;
        this.currentImageData = null;
        
        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.fileList = document.getElementById('fileList');
        this.selectBtn = document.getElementById('selectBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.invertBtn = document.getElementById('invertBtn');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.canvas = document.getElementById('imageCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.placeholder = document.getElementById('canvasPlaceholder');
        this.imageInfo = document.getElementById('imageInfo');
        this.statusMessage = document.getElementById('statusMessage');
    }

    attachEventListeners() {
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e.target.files));
        this.selectBtn.addEventListener('click', () => this.fileInput.click());
        this.clearBtn.addEventListener('click', () => this.clearAll());
        this.invertBtn.addEventListener('click', () => this.toggleInvert());
        this.downloadBtn.addEventListener('click', () => this.downloadImage());
        this.prevBtn.addEventListener('click', () => this.showPreviousImage());
        this.nextBtn.addEventListener('click', () => this.showNextImage());
    }

    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
        this.handleFileSelect(e.dataTransfer.files);
    }

    async handleFileSelect(fileList) {
        for (let file of fileList) {
            if (!file.name.endsWith('.c') && !file.name.endsWith('.h')) {
                this.showMessage(`Skipping ${file.name}: only .c and .h files supported`, 'error');
                continue;
            }

            try {
                const content = await this.readFile(file);
                const images = this.parseFile(content, file.name);
                
                if (images.length > 0) {
                    this.files.set(file.name, images);
                    this.showMessage(`✓ Loaded ${images.length} image(s) from ${file.name}`, 'success');
                } else {
                    this.showMessage(`No images found in ${file.name}`, 'error');
                }
            } catch (error) {
                this.showMessage(`Error reading ${file.name}: ${error.message}`, 'error');
            }
        }

        this.updateFileList();
    }

    readFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = () => reject(new Error('Failed to read file'));
            reader.readAsText(file);
        });
    }

    parseFile(content, filename) {
        const images = [];
        
        let cleanContent = content.replace(/\/\/.*$/gm, '');
        cleanContent = cleanContent.replace(/\/\*[\s\S]*?\*\//g, '');
        
        const arrayPattern = /const\s+(?:LV_ATTRIBUTE_MEM_ALIGN\s+)?uint8_t\s+(\w+_data)\s*\[\s*\]\s*=\s*\{([^}]+)\}/g;
        const dscPattern = /const\s+lv_img_dsc_t\s+(\w+)\s*=\s*\{([^}]+)\}/g;

        let arrayMatch;
        const arrays = new Map();

        while ((arrayMatch = arrayPattern.exec(cleanContent)) !== null) {
            const arrayName = arrayMatch[1];
            const arrayData = this.extractHexValues(arrayMatch[2]);
            
            if (arrayData.length > 0) {
                arrays.set(arrayName, arrayData);
            }
        }

        let dscMatch;
        while ((dscMatch = dscPattern.exec(cleanContent)) !== null) {
            const dscName = dscMatch[1];
            const dscContent = dscMatch[2];
            
            const dataNameMatch = dscContent.match(/\.data\s*=\s*(\w+_data)/);
            if (!dataNameMatch) continue;
            
            const arrayName = dataNameMatch[1];
            const arrayData = arrays.get(arrayName);
            
            if (!arrayData) continue;

            let width = this.extractNumber(dscContent, '\\.w\\s*=\\s*(\\d+)');
            let height = this.extractNumber(dscContent, '\\.h\\s*=\\s*(\\d+)');
            let colorFormat = this.extractString(dscContent, '\\.cf\\s*=\\s*(\\w+)');

            if (width && height && width > 0 && height > 0) {
                let expectedSize;
                
                if (colorFormat && colorFormat.includes('1BIT')) {
                    expectedSize = Math.ceil(width * height / 8);
                } else if (colorFormat && colorFormat.includes('4BIT')) {
                    expectedSize = Math.ceil(width * height / 2);
                } else if (colorFormat && colorFormat.includes('8BIT')) {
                    expectedSize = width * height;
                } else if (colorFormat && colorFormat.includes('888')) {
                    expectedSize = width * height * 3;
                } else if (colorFormat && colorFormat.includes('8888')) {
                    expectedSize = width * height * 4;
                } else {
                    const hasAlpha = !colorFormat || colorFormat.includes('ALPHA');
                    expectedSize = width * height * (hasAlpha ? 3 : 2);
                }
                
                if (arrayData.length >= expectedSize * 0.8 && arrayData.length <= expectedSize * 1.2) {
                    images.push({
                        name: dscName,
                        arrayName: arrayName,
                        data: arrayData,
                        width: width,
                        height: height,
                        colorFormat: colorFormat || 'LV_IMG_CF_TRUE_COLOR_ALPHA',
                        filename: filename
                    });
                }
            }
        }

        return images;
    }

    extractHexValues(text) {
        const hexPattern = /0x([0-9A-Fa-f]{2})/g;
        const values = [];
        let match;
        while ((match = hexPattern.exec(text)) !== null) {
            values.push(parseInt(match[1], 16));
        }
        return values;
    }

    extractNumber(text, pattern) {
        const regex = new RegExp(pattern);
        const match = regex.exec(text);
        return match ? parseInt(match[1]) : null;
    }

    extractString(text, pattern) {
        const regex = new RegExp(pattern);
        const match = regex.exec(text);
        return match ? match[1] : null;
    }

    updateFileList() {
        this.fileList.innerHTML = '';

        if (this.files.size === 0) {
            this.fileList.innerHTML = '<li style="padding: 20px; text-align: center; color: #999;">No files loaded</li>';
            return;
        }

        for (let [filename, images] of this.files.entries()) {
            for (let [index, image] of images.entries()) {
                const li = document.createElement('li');
                li.className = 'file-item';
                
                if (this.currentFile === `${filename}_${index}`) {
                    li.classList.add('active');
                }

                li.innerHTML = `
                    <div class="file-info">
                        <div class="file-name">${image.name}</div>
                        <div class="file-count">${image.width}×${image.height} • ${filename}</div>
                    </div>
                    <div class="file-actions">
                        <button class="btn-small btn-secondary">View</button>
                        <button class="btn-small btn-danger">Remove</button>
                    </div>
                `;

                li.addEventListener('click', () => this.selectImage(filename, index));
                
                const removeBtn = li.querySelector('.btn-danger');
                removeBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    this.removeImage(filename, index);
                });

                this.fileList.appendChild(li);
            }
        }
    }

    selectImage(filename, index) {
        const images = this.files.get(filename);
        if (!images || !images[index]) return;

        this.currentFile = `${filename}_${index}`;
        this.currentImageData = images[index];
        this.isInverted = false;
        this.displayImage();
        this.updateFileList();
    }

    removeImage(filename, index) {
        const images = this.files.get(filename);
        if (images) {
            images.splice(index, 1);
            if (images.length === 0) {
                this.files.delete(filename);
            }
            
            if (this.currentFile === `${filename}_${index}`) {
                this.currentFile = null;
                this.currentImageData = null;
                this.clearCanvas();
            }
            
            this.updateFileList();
            this.showMessage('Image removed', 'info');
        }
    }

    displayImage() {
        if (!this.currentImageData) return;

        try {
            const imageData = this.currentImageData;
            const imgData = this.decodeImage(
                imageData.data,
                imageData.width,
                imageData.height,
                imageData.colorFormat,
                this.isInverted
            );

            this.canvas.width = imageData.width;
            this.canvas.height = imageData.height;
            this.ctx.putImageData(imgData, 0, 0);

            this.placeholder.style.display = 'none';
            this.canvas.style.display = 'block';

            this.invertBtn.style.display = 'block';
            this.downloadBtn.style.display = 'block';
            this.imageInfo.style.display = 'block';

            this.updateImageInfo(imageData);
            this.updateNavigationButtons();

        } catch (error) {
            this.showMessage(`Error displaying image: ${error.message}`, 'error');
        }
    }

    decodeImage(data, width, height, colorFormat, invert) {
        const imgData = this.ctx.createImageData(width, height);

        if (colorFormat.includes('1BIT')) {
            return this.decode1Bit(data, width, height, imgData, invert);
        } else if (colorFormat.includes('8BIT') && colorFormat.includes('GRAY')) {
            return this.decode8BitGray(data, width, height, imgData, invert);
        } else {
            return this.decodeRGB565(data, width, height, colorFormat, invert);
        }
    }

    decode1Bit(data, width, height, imgData, invert) {
        let pixelIdx = 0;
        let byteIdx = 0;
        let bitIdx = 7;
        
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const bit = (data[byteIdx] >> bitIdx) & 1;
                const value = bit ? 255 : 0;
                const finalValue = invert ? (255 - value) : value;
                
                const pos = pixelIdx * 4;
                imgData.data[pos + 0] = finalValue;
                imgData.data[pos + 1] = finalValue;
                imgData.data[pos + 2] = finalValue;
                imgData.data[pos + 3] = 255;
                
                pixelIdx++;
                bitIdx--;
                if (bitIdx < 0) {
                    bitIdx = 7;
                    byteIdx++;
                }
            }
        }
        return imgData;
    }

    decode8BitGray(data, width, height, imgData, invert) {
        let pixelIdx = 0;
        
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const value = invert ? (255 - data[pixelIdx]) : data[pixelIdx];
                const pos = pixelIdx * 4;
                
                imgData.data[pos + 0] = value;
                imgData.data[pos + 1] = value;
                imgData.data[pos + 2] = value;
                imgData.data[pos + 3] = 255;
                
                pixelIdx++;
            }
        }
        return imgData;
    }

    decodeRGB565(data, width, height, colorFormat, invert) {
        const hasAlpha = colorFormat.includes('ALPHA');
        const bytesPerPixel = hasAlpha ? 3 : 2;
        const imgData = this.ctx.createImageData(width, height);
        const pixels = imgData.data;

        let pixelIdx = 0;
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                const byteOffset = pixelIdx * bytesPerPixel;
                let r, g, b, a = 255;

                if (hasAlpha && byteOffset + 2 < data.length) {
                    const byte1 = data[byteOffset];
                    const byte2 = data[byteOffset + 1];
                    const rgb565 = (byte2 << 8) | byte1;
                    a = data[byteOffset + 2];

                    b = ((rgb565 >> 0) & 0x1F) << 3;
                    g = ((rgb565 >> 5) & 0x3F) << 2;
                    r = ((rgb565 >> 11) & 0x1F) << 3;
                } else if (byteOffset + 1 < data.length) {
                    const byte1 = data[byteOffset];
                    const byte2 = data[byteOffset + 1];
                    const rgb565 = (byte2 << 8) | byte1;

                    b = ((rgb565 >> 0) & 0x1F) << 3;
                    g = ((rgb565 >> 5) & 0x3F) << 2;
                    r = ((rgb565 >> 11) & 0x1F) << 3;
                }

                if (invert) {
                    r = 255 - r;
                    g = 255 - g;
                    b = 255 - b;
                }

                const pixelPos = pixelIdx * 4;
                pixels[pixelPos + 0] = r;
                pixels[pixelPos + 1] = g;
                pixels[pixelPos + 2] = b;
                pixels[pixelPos + 3] = a;

                pixelIdx++;
            }
        }

        return imgData;
    }

    toggleInvert() {
        this.isInverted = !this.isInverted;
        this.displayImage();
        this.invertBtn.textContent = this.isInverted ? '🔄 Revert Colors' : '🔄 Invert Colors';
    }

    downloadImage() {
        if (!this.currentImageData) return;

        const link = document.createElement('a');
        link.href = this.canvas.toDataURL('image/png');
        link.download = `${this.currentImageData.name}.png`;
        link.click();
    }

    updateImageInfo(imageData) {
        document.getElementById('infoDimensions').textContent = 
            `${imageData.width} × ${imageData.height} px`;
        document.getElementById('infoFormat').textContent = imageData.colorFormat;
        document.getElementById('infoSize').textContent = 
            `${imageData.data.length} bytes`;
        document.getElementById('infoPixels').textContent = 
            `${imageData.width * imageData.height}`;
    }

    getAllImages() {
        const allImages = [];
        for (let [filename, images] of this.files.entries()) {
            for (let [index, image] of images.entries()) {
                allImages.push({
                    key: `${filename}_${index}`,
                    filename,
                    index,
                    image
                });
            }
        }
        return allImages;
    }

    updateNavigationButtons() {
        const allImages = this.getAllImages();
        const currentIdx = allImages.findIndex(img => img.key === this.currentFile);
        
        this.prevBtn.style.display = currentIdx > 0 ? 'block' : 'none';
        this.nextBtn.style.display = currentIdx < allImages.length - 1 ? 'block' : 'none';
    }

    showPreviousImage() {
        const allImages = this.getAllImages();
        const currentIdx = allImages.findIndex(img => img.key === this.currentFile);
        if (currentIdx > 0) {
            const prevImg = allImages[currentIdx - 1];
            this.selectImage(prevImg.filename, prevImg.index);
        }
    }

    showNextImage() {
        const allImages = this.getAllImages();
        const currentIdx = allImages.findIndex(img => img.key === this.currentFile);
        if (currentIdx < allImages.length - 1) {
            const nextImg = allImages[currentIdx + 1];
            this.selectImage(nextImg.filename, nextImg.index);
        }
    }

    clearCanvas() {
        this.canvas.style.display = 'none';
        this.placeholder.style.display = 'block';
        this.invertBtn.style.display = 'none';
        this.downloadBtn.style.display = 'none';
        this.prevBtn.style.display = 'none';
        this.nextBtn.style.display = 'none';
        this.imageInfo.style.display = 'none';
        this.invertBtn.textContent = '🔄 Invert Colors';
    }

    clearAll() {
        if (confirm('Clear all loaded files?')) {
            this.files.clear();
            this.currentFile = null;
            this.currentImageData = null;
            this.isInverted = false;
            this.updateFileList();
            this.clearCanvas();
            this.showMessage('All files cleared', 'info');
        }
    }

    showMessage(text, type) {
        this.statusMessage.textContent = text;
        this.statusMessage.className = `message show ${type}`;
        
        if (type !== 'error') {
            setTimeout(() => {
                this.statusMessage.classList.remove('show');
            }, 3000);
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new CArrayImageViewer();
});