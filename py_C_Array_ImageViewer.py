#!/usr/bin/env python3
"""
RGB565 GUI Viewer for C Header Files
GUI tool to select and visualize RGB565 image data from C header files
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import re
import numpy as np
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

class RGB565Viewer:
    def __init__(self, root):
        self.root = root
        self.root.title("RGB565 Image Viewer")
        self.root.geometry("800x800")
        
        self.current_images = []
        self.current_index = 0
        
        self.setup_ui()
        self.refresh_file_list()
    
    def setup_ui(self):
        """Setup the GUI interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Select Header File", padding="5")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        # File listbox
        ttk.Label(file_frame, text="Available .h files:").grid(row=0, column=0, sticky=tk.W)
        
        listbox_frame = ttk.Frame(file_frame)
        listbox_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        listbox_frame.columnconfigure(0, weight=1)
        
        self.file_listbox = tk.Listbox(listbox_frame, height=4)
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # Buttons
        button_frame = ttk.Frame(file_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=5)
        
        ttk.Button(button_frame, text="Refresh", command=self.refresh_file_list).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Browse...", command=self.browse_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Process File", command=self.process_selected_file).pack(side=tk.LEFT, padx=5)
        
        # Info frame
        info_frame = ttk.LabelFrame(main_frame, text="File Information", padding="5")
        info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(0, weight=1)
        
        self.info_text = tk.Text(info_frame, height=6, wrap=tk.WORD)
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        info_scroll = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        info_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.info_text.configure(yscrollcommand=info_scroll.set)
        
        # Image display frame
        image_frame = ttk.LabelFrame(main_frame, text="Image Preview", padding="5")
        image_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        image_frame.columnconfigure(0, weight=1)
        image_frame.rowconfigure(0, weight=1)
        
        # Canvas for image display
        self.canvas_frame = ttk.Frame(image_frame)
        self.canvas_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)
        
        # Navigation frame
        nav_frame = ttk.Frame(image_frame)
        nav_frame.grid(row=1, column=0, pady=5)
        
        self.prev_button = ttk.Button(nav_frame, text="← Previous", command=self.prev_image, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.image_label = ttk.Label(nav_frame, text="No images loaded")
        self.image_label.pack(side=tk.LEFT, padx=10)
        
        self.next_button = ttk.Button(nav_frame, text="Next →", command=self.next_image, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(nav_frame, text="Save Current", command=self.save_current_image).pack(side=tk.LEFT, padx=10)
        ttk.Button(nav_frame, text="Save All", command=self.save_all_images).pack(side=tk.LEFT, padx=5)
        
        # Get references to save buttons
        nav_buttons = nav_frame.winfo_children()
        self.save_button = nav_buttons[-2]  # Save Current button
        self.save_all_button = nav_buttons[-1]  # Save All button
        
        # Initially disable save buttons
        self.save_button.config(state=tk.DISABLED)
        self.save_all_button.config(state=tk.DISABLED)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Select a header file to begin")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
    
    def refresh_file_list(self):
        """Refresh the list of .h files in current directory"""
        self.file_listbox.delete(0, tk.END)
        
        try:
            current_dir = os.getcwd()
            h_files = [f for f in os.listdir(current_dir) if f.endswith('.h')]
            h_files.sort()
            
            for file in h_files:
                self.file_listbox.insert(tk.END, file)
            
            if h_files:
                self.status_var.set(f"Found {len(h_files)} header files in {current_dir}")
            else:
                self.status_var.set(f"No .h files found in {current_dir}")
                
        except Exception as e:
            self.status_var.set(f"Error reading directory: {e}")
    
    def browse_file(self):
        """Browse for a header file"""
        filename = filedialog.askopenfilename(
            title="Select Header File",
            filetypes=[("Header files", "*.h"), ("All files", "*.*")]
        )
        
        if filename:
            # Add to listbox if not already there
            basename = os.path.basename(filename)
            
            # Clear selection and add file
            self.file_listbox.delete(0, tk.END)
            self.file_listbox.insert(0, filename)  # Insert full path for browsed files
            self.file_listbox.selection_set(0)
            
            self.status_var.set(f"Selected: {basename}")
    
    def on_file_select(self, event):
        """Handle file selection from listbox"""
        selection = self.file_listbox.curselection()
        if selection:
            filename = self.file_listbox.get(selection[0])
            self.status_var.set(f"Selected: {filename}")
    
    def process_selected_file(self):
        """Process the selected header file"""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a header file first.")
            return
        
        filename = self.file_listbox.get(selection[0])
        
        # Handle both relative and absolute paths
        if not os.path.isabs(filename):
            filename = os.path.join(os.getcwd(), filename)
        
        if not os.path.exists(filename):
            messagebox.showerror("File Not Found", f"Could not find file: {filename}")
            return
        
        # Process in separate thread to avoid blocking GUI
        self.status_var.set("Processing file...")
        try:
            self.root.config(cursor="watch")  # More compatible cursor
        except:
            pass  # Ignore cursor errors on some systems
        
        thread = threading.Thread(target=self.process_file_thread, args=(filename,))
        thread.daemon = True
        thread.start()
    
    def process_file_thread(self, filename):
        """Process file in separate thread"""
        try:
            results = self.analyze_header_file(filename)
            
            # Update GUI in main thread
            self.root.after(0, self.display_results, results, filename)
            
        except Exception as e:
            self.root.after(0, self.show_error, f"Error processing file: {e}")
    
    def analyze_header_file(self, filename):
        """Analyze header file and extract images"""
        with open(filename, 'r') as f:
            content = f.read()
        
        # Find dimensions and arrays (reusing logic from previous script)
        dimensions = self.find_all_dimensions(content)
        arrays = self.find_all_arrays(content)
        matches = self.match_arrays_to_dimensions(arrays, dimensions, content)
        
        results = {
            'filename': filename,
            'dimensions': dimensions,
            'arrays': arrays,
            'matches': matches,
            'content': content
        }
        
        return results
    
    def display_results(self, results, filename):
        """Display analysis results in GUI"""
        try:
            self.root.config(cursor="")
        except:
            pass  # Ignore cursor errors
        
        # Update info text
        info = f"File: {os.path.basename(filename)}\n"
        info += f"Dimensions found: {len(results['dimensions'])}\n"
        info += f"Arrays found: {len(results['arrays'])}\n\n"
        
        # Process images
        self.current_images = []
        
        for match in results['matches']:
            array = match['array']
            dims = match['dimensions']
            
            info += f"Array: {array['name']}\n"
            
            if dims:
                dim_name, width, height = dims
                info += f"  Size: {width}×{height}\n"
                
                try:
                    pixel_data = self.extract_array_data(results['content'], array)
                    if len(pixel_data) > 0:
                        image = self.create_image_from_data(width, height, pixel_data)
                        self.current_images.append({
                            'name': array['name'],
                            'image': image,
                            'dimensions': (width, height),
                            'pixel_count': len(pixel_data)
                        })
                        info += f"  Status: Loaded successfully\n"
                    else:
                        info += f"  Status: No pixel data found\n"
                except Exception as e:
                    info += f"  Status: Error - {e}\n"
            else:
                info += f"  Status: No dimensions found\n"
            
            info += "\n"
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info)
        
        # Setup image navigation
        self.current_index = 0
        self.update_image_display()
        
        self.status_var.set(f"Loaded {len(self.current_images)} images from {os.path.basename(filename)}")
    
    def update_image_display(self):
        """Update the image display"""
        # Clear previous canvas
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        if not self.current_images:
            self.image_label.config(text="No images loaded")
            self.prev_button.config(state=tk.DISABLED)
            self.next_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.DISABLED)
            self.save_all_button.config(state=tk.DISABLED)
            return
        
        # Update navigation
        self.image_label.config(text=f"Image {self.current_index + 1} of {len(self.current_images)}")
        self.prev_button.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.current_index < len(self.current_images) - 1 else tk.DISABLED)
        self.save_button.config(state=tk.NORMAL)
        self.save_all_button.config(state=tk.NORMAL)
        
        # Display current image
        current = self.current_images[self.current_index]
        
        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.imshow(current['image'])
        ax.set_title(f"{current['name']} ({current['dimensions'][0]}×{current['dimensions'][1]})")
        ax.axis('off')
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        plt.close(fig)  # Close to free memory
    
    def prev_image(self):
        """Show previous image"""
        if self.current_index > 0:
            self.current_index -= 1
            self.update_image_display()
    
    def next_image(self):
        """Show next image"""
        if self.current_index < len(self.current_images) - 1:
            self.current_index += 1
            self.update_image_display()
    
    def save_current_image(self):
        """Save current image"""
        if not self.current_images:
            return
        
        current = self.current_images[self.current_index]
        filename = f"{current['name']}.png"
        
        try:
            current['image'].save(filename)
            messagebox.showinfo("Saved", f"Image saved as: {filename}")
            self.status_var.set(f"Saved: {filename}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save image: {e}")
    
    def save_all_images(self):
        """Save all loaded images"""
        if not self.current_images:
            return
        
        saved_count = 0
        for img_data in self.current_images:
            filename = f"{img_data['name']}.png"
            try:
                img_data['image'].save(filename)
                saved_count += 1
            except Exception as e:
                print(f"Error saving {filename}: {e}")
        
        messagebox.showinfo("Saved", f"Saved {saved_count} images")
        self.status_var.set(f"Saved {saved_count} images")
    
    def show_error(self, message):
        """Show error message"""
        try:
            self.root.config(cursor="")
        except:
            pass  # Ignore cursor errors
        messagebox.showerror("Error", message)
        self.status_var.set("Error occurred")
    
    # Include the core processing functions from the previous script
    def rgb565_to_rgb888(self, rgb565):
        """Convert RGB565 to RGB888 format"""
        r = (rgb565 >> 11) & 0x1F
        g = (rgb565 >> 5) & 0x3F  
        b = rgb565 & 0x1F
        
        r = (r * 255) // 31
        g = (g * 255) // 63
        b = (b * 255) // 31
        
        return (r, g, b)
    
    def find_all_dimensions(self, content):
        """Find all width/height definitions in the file"""
        width_matches = re.findall(r'(\w*[Ww]idth\w*)\s*=\s*(\d+)', content)
        height_matches = re.findall(r'(\w*[Hh]eight\w*)\s*=\s*(\d+)', content)
        
        dimensions = {}
        for width_name, width_val in width_matches:
            base_name = width_name.replace('Width', '').replace('width', '').replace('WIDTH', '')
            
            for height_name, height_val in height_matches:
                if base_name.lower() in height_name.lower():
                    dimensions[base_name] = (int(width_val), int(height_val))
                    break
        
        return dimensions
    
    def find_all_arrays(self, content):
        """Find all array declarations in the file"""
        pattern = r'(?:const\s+)?(?:unsigned\s+)?(?:short|int|uint16_t)\s+(\w+)\[([^\]]*)\]\s*(?:PROGMEM\s*)?=\s*\{'
        
        arrays = []
        for match in re.finditer(pattern, content, re.IGNORECASE):
            array_name = match.group(1)
            array_size = match.group(2)
            start_pos = match.start()
            
            brace_pos = content.find('{', start_pos)
            if brace_pos == -1:
                continue
                
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
    
    def match_arrays_to_dimensions(self, arrays, dimensions, content):
        """Match arrays to dimensions (simplified version for GUI)"""
        matches = []
        
        for array in arrays:
            array_name = array['name']
            best_match = None
            
            # Simple matching for GUI version
            for dim_name, (width, height) in dimensions.items():
                if dim_name.lower() in array_name.lower() or array_name.lower() in dim_name.lower():
                    best_match = (dim_name, width, height)
                    break
            
            # Try guessing from array size
            if not best_match:
                try:
                    if isinstance(array['size'], str):
                        if array['size'].startswith('0x'):
                            array_size = int(array['size'], 16)
                        else:
                            array_size = int(array['size'])
                    else:
                        array_size = int(array['size'])
                    
                    common_dims = [(320, 240), (240, 320), (320, 170), (320, 70), (128, 64), (128, 128)]
                    for w, h in common_dims:
                        if w * h == array_size:
                            best_match = (f"guessed_{w}x{h}", w, h)
                            break
                except:
                    pass
            
            matches.append({
                'array': array,
                'dimensions': best_match
            })
        
        return matches
    
    def extract_array_data(self, content, array_info):
        """Extract pixel data from array"""
        array_content = content[array_info['start']+1:array_info['end']]
        
        lines = array_content.split('\n')
        hex_values = []
        
        for line in lines:
            comment_pos = line.find('//')
            if comment_pos != -1:
                line = line[:comment_pos]
            
            line_hex = re.findall(r'0x([0-9A-Fa-f]+)', line, re.IGNORECASE)
            hex_values.extend(line_hex)
        
        pixel_data = [int(val, 16) for val in hex_values]
        return pixel_data
    
    def create_image_from_data(self, width, height, pixel_data):
        """Create PIL Image from RGB565 data"""
        expected_pixels = width * height
        
        if len(pixel_data) > expected_pixels:
            pixel_data = pixel_data[:expected_pixels]
        elif len(pixel_data) < expected_pixels:
            pixel_data = pixel_data + [0] * (expected_pixels - len(pixel_data))
        
        rgb_data = []
        for pixel in pixel_data:
            r, g, b = self.rgb565_to_rgb888(pixel)
            rgb_data.extend([r, g, b])
        
        rgb_array = np.array(rgb_data, dtype=np.uint8).reshape(height, width, 3)
        image = Image.fromarray(rgb_array)
        
        return image

def main():
    """Main function to start the GUI"""
    try:
        root = tk.Tk()
        app = RGB565Viewer(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
