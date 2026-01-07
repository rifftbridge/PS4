#!/usr/bin/env python3
"""
Rocksmith 2014 PC to PS4 Converter - GUI Edition
Full-featured Windows application with drag-and-drop batch conversion
"""

import os
import sys
import json
import struct
import threading
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinterdnd2 import DND_FILES, TkinterDnD

# Import converter modules
try:
    from enhanced_converter import EnhancedRocksmithConverter
    from steam_dlc_database import SteamDLCDatabase
except ImportError:
    print("Error: Converter modules not found!")
    print("Make sure enhanced_converter.py and steam_dlc_database.py are in the same directory")
    sys.exit(1)

class ConversionJob:
    """Represents a single conversion job"""
    def __init__(self, input_file: Path, format_type: str = "Unknown"):
        self.input_file = input_file
        self.status = "Pending"
        self.progress = 0
        self.output_dir = None
        self.error = None
        self.song_info = {}
        self.format_type = format_type  # PC, PS4, or Unknown

class RocksmithGUI:
    """Main GUI Application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("RiffBridge - Rocksmith PC → PS4 Converter")
        self.root.geometry("1600x800")  # Increased height from 700 to 800 for more room
        
        # Set window icon
        try:
            icon_path = self.get_resource_path('RiffBridge_icon.ico')
            if icon_path and os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Application state
        self.jobs: List[ConversionJob] = []
        self.output_base_dir = Path.home() / "Desktop"  # Default to Desktop
        self.is_converting = False
        self.converter = None
        
        # Settings
        self.settings = {
            'region': tk.StringVar(value='EP0001'),
            'title_id': tk.StringVar(value='CUSA00745'),
            'use_steam': tk.BooleanVar(value=True),
            'build_pkg': tk.BooleanVar(value=True),
            'auto_open_output': tk.BooleanVar(value=True),
        }
        
        # Setup UI
        self.setup_ui()
        
        # Initialize converter
        self.initialize_converter()
    
    def get_resource_path(self, relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
            result = os.path.join(base_path, relative_path)
            # Debug: Log when running as .exe
            if hasattr(self, 'log_message'):
                self.log_message(f"  Checking embedded: {result}", 'info')
            return result
        except Exception:
            base_path = os.path.abspath(".")
            return os.path.join(base_path, relative_path)
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for two-column layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=3)  # Left side (controls) - 75% width
        main_frame.columnconfigure(1, weight=1)  # Right side (artwork) - 25% width
        main_frame.rowconfigure(2, weight=1)
        
        # Left panel for controls
        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_panel.columnconfigure(0, weight=1)
        
        # Row weights: 
        # Row 0 (title) - no weight
        # Row 1 (drop zone) - no weight  
        # Row 2 (file list) - weight 1 (can shrink if needed)
        # Row 3 (log) - weight 1 (can shrink if needed)
        # Row 4 (controls) - no weight (always visible!)
        left_panel.rowconfigure(2, weight=1)
        left_panel.rowconfigure(3, weight=1)
        
        # Title (without emoji)
        title_label = ttk.Label(
            left_panel, 
            text="RiffBridge - Rocksmith PC → PS4 Converter",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)
        
        # Drop zone
        self.setup_drop_zone(left_panel)
        
        # File list
        self.setup_file_list(left_panel)
        
        # Log area
        self.setup_log_area(left_panel)
        
        # Control buttons
        self.setup_controls(left_panel)
        
        # Right panel for artwork
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.setup_artwork(right_panel)
        
        # Status bar
        self.setup_status_bar()
        
        # Menu bar
        self.setup_menu()
    
    def setup_artwork(self, parent):
        """Setup artwork display on right side"""
        try:
            from PIL import Image, ImageTk
            
            # Try to load the square artwork
            artwork_path = None
            
            # List of possible filenames
            possible_names = [
                'Riff_Bridge_cover_art.jpg',
                'Rifft_Bridge_square_artwork_02_copy.jpg', 
                'artwork.jpg', 
                'logo.jpg'
            ]
            
            # Try each filename
            for possible_name in possible_names:
                # First check current directory
                if os.path.exists(possible_name):
                    artwork_path = possible_name
                    self.log_message(f"✓ Found artwork in current dir: {possible_name}", 'success')
                    break
                
                # Then check embedded resources (for .exe)
                try:
                    embedded_path = self.get_resource_path(possible_name)
                    if embedded_path and os.path.exists(embedded_path):
                        artwork_path = embedded_path
                        self.log_message(f"✓ Found embedded artwork: {possible_name}", 'success')
                        break
                except Exception as e:
                    pass  # Silent fail, try next
            
            if not artwork_path:
                self.log_message("⚠ Artwork not found - using default layout", 'warning')
                return
            
            # Load and resize image
            image = Image.open(artwork_path)
            
            # Calculate size to fit in panel (DOUBLED to 700px width!)
            max_width = 700
            ratio = max_width / image.width
            new_height = int(image.height * ratio)
            image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Display image
            label = tk.Label(parent, image=photo, bg='white')
            label.image = photo  # Keep a reference
            label.pack(pady=20, padx=10)
            
            self.log_message(f"✓ Loaded artwork: {os.path.basename(artwork_path)}", 'success')
                
        except Exception as e:
            # If image loading fails, show placeholder
            placeholder = ttk.Label(
                parent,
                text="RiffBridge",
                font=('Arial', 18, 'bold')
            )
            placeholder.pack(pady=50)
    
    def setup_drop_zone(self, parent):
        """Setup drag-and-drop zone"""
        drop_frame = ttk.LabelFrame(parent, text="Drag & Drop PSARC Files Here", padding="20")
        drop_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        drop_frame.columnconfigure(0, weight=1)
        
        # Drop label
        self.drop_label = tk.Label(
            drop_frame,
            text="Drag PC .psarc files here\nor click 'Add Files' button below",
            font=('Arial', 11),
            bg='#f0f0f0',
            fg='#666',
            relief=tk.SUNKEN,
            height=4
        )
        self.drop_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Enable drag and drop
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.on_drop)
        
        # Add files button
        add_btn = ttk.Button(drop_frame, text="➕ Add Files", command=self.add_files)
        add_btn.grid(row=1, column=0, pady=(10, 0))
    
    def setup_file_list(self, parent):
        """Setup file list with treeview"""
        list_frame = ttk.LabelFrame(parent, text="Conversion Queue", padding="10")
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Treeview
        columns = ('filename', 'status', 'progress')
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=5)  # Reduced from 8
        
        # Define columns
        self.file_tree.heading('filename', text='Filename')
        self.file_tree.heading('status', text='Status')
        self.file_tree.heading('progress', text='Progress')
        
        self.file_tree.column('filename', width=400)
        self.file_tree.column('status', width=150)
        self.file_tree.column('progress', width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self.file_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Buttons
        btn_frame = ttk.Frame(list_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(btn_frame, text="🗑️ Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)
    
    def setup_log_area(self, parent):
        """Setup log output area"""
        log_frame = ttk.LabelFrame(parent, text="Conversion Log", padding="10")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=4,  # Reduced from 6 to 4 - makes room for controls below!
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure tags for colored output
        self.log_text.tag_config('info', foreground='black')
        self.log_text.tag_config('success', foreground='green')
        self.log_text.tag_config('warning', foreground='orange')
        self.log_text.tag_config('error', foreground='red')
        
        btn_frame = ttk.Frame(log_frame)
        btn_frame.grid(row=1, column=0, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Save Log", command=self.save_log).pack(side=tk.LEFT, padx=5)
    
    def setup_controls(self, parent):
        """Setup control buttons"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)
        
        # Left side - Output directory
        output_frame = ttk.Frame(control_frame)
        output_frame.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(output_frame, text="Output:").pack(side=tk.LEFT, padx=5)
        
        self.output_label = ttk.Label(
            output_frame, 
            text=str(self.output_base_dir)[:50] + "...",
            foreground='blue',
            cursor='hand2'
        )
        self.output_label.pack(side=tk.LEFT, padx=5)
        self.output_label.bind('<Button-1>', lambda e: self.choose_output_dir())
        
        ttk.Button(output_frame, text="📁 Change", command=self.choose_output_dir).pack(side=tk.LEFT)
        
        # Right side - Convert button (Large & Red!)
        self.convert_btn = tk.Button(
            control_frame,
            text="🚀 CONVERT ALL",
            command=self.start_conversion,
            font=('Arial', 16, 'bold'),
            bg='#DC143C',  # Crimson red
            fg='white',
            activebackground='#FF0000',  # Bright red when clicked
            activeforeground='white',
            relief=tk.RAISED,
            bd=3,
            padx=30,
            pady=15,
            cursor='hand2'
        )
        self.convert_btn.grid(row=0, column=1, sticky=tk.E, padx=10, pady=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            control_frame,
            mode='determinate',
            length=200
        )
        self.progress_bar.grid(row=0, column=2, sticky=tk.E, padx=5)
    
    def setup_status_bar(self):
        """Setup status bar at bottom"""
        self.status_bar = ttk.Label(
            self.root,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
    
    def setup_menu(self):
        """Setup menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add Files", command=self.add_files)
        file_menu.add_command(label="Choose Output Directory", command=self.choose_output_dir)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Conversion Settings", command=self.show_settings)
        settings_menu.add_checkbutton(
            label="Use Steam Integration",
            variable=self.settings['use_steam'],
            command=self.toggle_steam
        )
        settings_menu.add_checkbutton(
            label="Build Final PKG File",
            variable=self.settings['build_pkg']
        )
        settings_menu.add_checkbutton(
            label="Auto-open Output Folder",
            variable=self.settings['auto_open_output']
        )
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Steam DLC Database", command=self.show_steam_database)
        tools_menu.add_command(label="Open Output Folder", command=self.open_output_folder)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Quick Start Guide", command=self.show_help)
        help_menu.add_command(label="About", command=self.show_about)
    
    def initialize_converter(self):
        """Initialize the converter"""
        try:
            self.converter = EnhancedRocksmithConverter(
                verbose=True,  # Enable verbose output!
                use_steam_db=self.settings['use_steam'].get()
            )
            # Redirect converter output to GUI log
            self.converter.log = self.converter_log
            self.log_message("✓ Converter initialized", 'success')
        except Exception as e:
            self.log_message(f"✗ Converter initialization failed: {e}", 'error')
            messagebox.showerror("Error", f"Failed to initialize converter:\n{e}")
    
    def converter_log(self, message):
        """Custom log handler for converter output"""
        self.log_message(message, 'info')
    
    def on_drop(self, event):
        """Handle drag and drop"""
        files = self.root.tk.splitlist(event.data)
        self.add_files_to_queue(files)
    
    def add_files(self):
        """Add files via file dialog"""
        files = filedialog.askopenfilenames(
            title="Select PC PSARC Files",
            filetypes=[
                ("PSARC Files", "*.psarc"),
                ("All Files", "*.*")
            ]
        )
        if files:
            self.add_files_to_queue(files)
    
    def check_psarc_format(self, file_path):
        """Check if psarc is PC (0x0) or PS4 (0x4) format"""
        try:
            with open(file_path, 'rb') as f:
                magic = f.read(4)
                if magic != b'PSAR':
                    return None, "Not a valid PSARC file"
                
                # Archive flags are at byte offset 28-31
                f.seek(28)
                archive_flags = struct.unpack('>I', f.read(4))[0]
                
                if archive_flags == 0x0:
                    return 'PC', None
                elif archive_flags == 0x4:
                    return 'PS4', None  # PS4 is valid! No error!
                else:
                    return None, f"Unknown format (flags: 0x{archive_flags:x})"
        except Exception as e:
            return None, str(e)
    
    def add_files_to_queue(self, files):
        """Add files to conversion queue"""
        added = 0
        for file_path in files:
            file_path = Path(file_path)
            
            # Check if file exists and is .psarc
            if not file_path.exists():
                self.log_message(f"⚠ File not found: {file_path.name}", 'warning')
                continue
            
            if file_path.suffix.lower() != '.psarc':
                self.log_message(f"⚠ Not a PSARC file: {file_path.name}", 'warning')
                continue
            
            # Check PSARC format (PC vs PS4)
            format_type, error = self.check_psarc_format(file_path)
            if error:
                self.log_message(f"⚠ {file_path.name}: {error}", 'warning')
                continue
            
            # Both PC and PS4 formats are accepted!
            if format_type == 'PS4':
                self.log_message(f"✓ {file_path.name}: PS4 format detected - will create PKG directly", 'success')
            elif format_type == 'PC':
                self.log_message(f"✓ {file_path.name}: PC format detected - will convert then create PKG", 'success')
            
            # Check if already in queue
            if any(job.input_file == file_path for job in self.jobs):
                self.log_message(f"⚠ Already in queue: {file_path.name}", 'warning')
                continue
            
            # Create job with format type
            job = ConversionJob(file_path, format_type)
            self.jobs.append(job)
            
            # Add to treeview
            self.file_tree.insert('', tk.END, values=(
                file_path.name,
                'Pending',
                '0%'
            ))
            
            added += 1
        
        if added > 0:
            self.log_message(f"✓ Added {added} file(s) to queue", 'success')
            self.update_status(f"{len(self.jobs)} file(s) in queue")
    
    def remove_selected(self):
        """Remove selected files from queue"""
        selected = self.file_tree.selection()
        if not selected:
            return
        
        for item in selected:
            index = self.file_tree.index(item)
            self.file_tree.delete(item)
            del self.jobs[index]
        
        self.log_message(f"Removed {len(selected)} file(s) from queue", 'info')
        self.update_status(f"{len(self.jobs)} file(s) in queue")
    
    def clear_all(self):
        """Clear all files from queue"""
        if not self.jobs:
            return
        
        if messagebox.askyesno("Clear All", "Remove all files from queue?"):
            self.file_tree.delete(*self.file_tree.get_children())
            self.jobs.clear()
            self.log_message("Queue cleared", 'info')
            self.update_status("Ready")
    
    def choose_output_dir(self):
        """Choose output directory"""
        directory = filedialog.askdirectory(
            title="Choose Output Directory",
            initialdir=self.output_base_dir
        )
        
        if directory:
            self.output_base_dir = Path(directory)
            self.output_label.config(text=str(self.output_base_dir)[:50] + "...")
            self.log_message(f"Output directory: {self.output_base_dir}", 'info')
    
    def start_conversion(self):
        """Start batch conversion"""
        if not self.jobs:
            messagebox.showwarning("No Files", "Please add files to the queue first")
            return
        
        if self.is_converting:
            messagebox.showwarning("Converting", "Conversion already in progress")
            return
        
        # Disable convert button
        self.convert_btn.config(state=tk.DISABLED, text="⏳ CONVERTING...", bg='#808080')
        self.is_converting = True
        
        # Start conversion in thread
        thread = threading.Thread(target=self.run_conversions, daemon=True)
        thread.start()
    
    def run_conversions(self):
        """Run all conversions (in thread)"""
        total = len(self.jobs)
        
        self.log_message(f"\n{'='*60}", 'info')
        self.log_message(f"Starting batch conversion of {total} file(s)", 'info')
        self.log_message(f"{'='*60}\n", 'info')
        
        for i, job in enumerate(self.jobs, 1):
            try:
                # Update progress
                progress = int((i - 1) / total * 100)
                self.root.after(0, self.update_progress, progress)
                
                # Update tree item
                item_id = self.file_tree.get_children()[i-1]
                self.root.after(0, self.file_tree.item, item_id, values=(
                    job.input_file.name,
                    'Converting...',
                    f'{progress}%'
                ))
                
                self.log_message(f"\n[{i}/{total}] Processing: {job.input_file.name}", 'info')
                
                # Create output directory
                output_dir = self.output_base_dir / job.input_file.stem
                output_dir.mkdir(parents=True, exist_ok=True)
                job.output_dir = output_dir
                
                # Check format and choose workflow
                if job.format_type == 'PS4':
                    # File is already PS4 - skip conversion, go straight to PKG creation
                    self.log_message(f"  → File is PS4 format - creating PKG files directly", 'info')
                    success = self.converter.create_pkg_from_ps4(
                        input_psarc=job.input_file,
                        output_dir=output_dir,
                        title_id=self.settings['title_id'].get(),
                        region=self.settings['region'].get(),
                        auto_steam=self.settings['use_steam'].get(),
                        build_pkg=self.settings['build_pkg'].get()
                    )
                else:
                    # File is PC format - convert to PS4 then create PKG
                    self.log_message(f"  → File is PC format - converting to PS4 then creating PKG", 'info')
                    success = self.converter.convert_enhanced(
                        input_psarc=job.input_file,
                        output_dir=output_dir,
                        title_id=self.settings['title_id'].get(),
                        region=self.settings['region'].get(),
                        auto_steam=self.settings['use_steam'].get(),
                        build_pkg=self.settings['build_pkg'].get()
                    )
                
                if success:
                    job.status = "Complete"
                    self.root.after(0, self.file_tree.item, item_id, values=(
                        job.input_file.name,
                        '✓ Complete',
                        '100%'
                    ))
                    self.log_message(f"✓ Successfully processed: {job.input_file.name}", 'success')
                else:
                    job.status = "Failed"
                    self.root.after(0, self.file_tree.item, item_id, values=(
                        job.input_file.name,
                        '✗ Failed',
                        'Error'
                    ))
                    self.log_message(f"✗ Processing failed: {job.input_file.name}", 'error')
                    self.log_message(f"  Check that all required files are present", 'error')
                
            except Exception as e:
                job.status = "Error"
                job.error = str(e)
                self.log_message(f"✗ Error: {e}", 'error')
                
                # Log detailed traceback
                import traceback
                self.log_message(f"Traceback:", 'error')
                for line in traceback.format_exc().split('\n'):
                    if line.strip():
                        self.log_message(f"  {line}", 'error')
                
                item_id = self.file_tree.get_children()[i-1]
                self.root.after(0, self.file_tree.item, item_id, values=(
                    job.input_file.name,
                    '✗ Error',
                    'Failed'
                ))
        
        # Complete
        self.root.after(0, self.update_progress, 100)
        self.root.after(0, self.conversion_complete)
    
    def conversion_complete(self):
        """Called when batch conversion completes"""
        self.is_converting = False
        self.convert_btn.config(state=tk.NORMAL, text="🚀 CONVERT ALL", bg='#DC143C')
        
        # Count results
        completed = sum(1 for job in self.jobs if job.status == "Complete")
        failed = sum(1 for job in self.jobs if job.status in ["Failed", "Error"])
        
        self.log_message(f"\n{'='*60}", 'info')
        self.log_message(f"Batch conversion complete!", 'success')
        self.log_message(f"Completed: {completed} | Failed: {failed}", 'info')
        self.log_message(f"{'='*60}\n", 'info')
        
        # Show completion message
        msg = f"Conversion complete!\n\nCompleted: {completed}\nFailed: {failed}"
        messagebox.showinfo("Complete", msg)
        
        # Auto-open output folder
        if self.settings['auto_open_output'].get() and completed > 0:
            self.open_output_folder()
        
        self.update_status("Conversion complete")
    
    def log_message(self, message: str, tag: str = 'info'):
        """Add message to log"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + '\n', tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def clear_log(self):
        """Clear log text"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def save_log(self):
        """Save log to file"""
        filename = filedialog.asksaveasfilename(
            title="Save Log",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log_message(f"✓ Log saved to: {filename}", 'success')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save log:\n{e}")
    
    def update_progress(self, value: int):
        """Update progress bar"""
        self.progress_bar['value'] = value
    
    def update_status(self, message: str):
        """Update status bar"""
        self.status_bar.config(text=message)
    
    def open_output_folder(self):
        """Open output folder in file explorer"""
        if sys.platform == 'win32':
            os.startfile(self.output_base_dir)
        elif sys.platform == 'darwin':
            os.system(f'open "{self.output_base_dir}"')
        else:
            os.system(f'xdg-open "{self.output_base_dir}"')
    
    def toggle_steam(self):
        """Toggle Steam integration"""
        if self.converter:
            self.converter.use_steam_db = self.settings['use_steam'].get()
            status = "enabled" if self.settings['use_steam'].get() else "disabled"
            self.log_message(f"Steam integration {status}", 'info')
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Conversion Settings")
        settings_window.geometry("400x300")
        
        frame = ttk.Frame(settings_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Region
        ttk.Label(frame, text="Region Code:").grid(row=0, column=0, sticky=tk.W, pady=5)
        region_combo = ttk.Combobox(
            frame,
            textvariable=self.settings['region'],
            values=['EP0001', 'UP0001', 'JP0001', 'HP0001'],
            width=15
        )
        region_combo.grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # Title ID
        ttk.Label(frame, text="Title ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=self.settings['title_id'], width=18).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Help text
        help_text = tk.Text(frame, height=10, width=45, wrap=tk.WORD)
        help_text.grid(row=2, column=0, columnspan=2, pady=20)
        help_text.insert(1.0, """Region Codes:
• EP0001 - Europe
• UP0001 - North America
• JP0001 - Japan
• HP0001 - Asia

Title ID:
• CUSA00745 - Rocksmith 2014 (default)

These settings apply to all conversions.""")
        help_text.config(state=tk.DISABLED)
        
        ttk.Button(frame, text="Close", command=settings_window.destroy).grid(row=3, column=0, columnspan=2)
    
    def show_steam_database(self):
        """Show Steam database window"""
        db_window = tk.Toplevel(self.root)
        db_window.title("Steam DLC Database")
        db_window.geometry("600x400")
        
        frame = ttk.Frame(db_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        # Search
        search_frame = ttk.Frame(frame)
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Results
        results_text = scrolledtext.ScrolledText(frame, height=20, wrap=tk.WORD)
        results_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        def do_search():
            query = search_var.get()
            if not query:
                return
            
            results_text.delete(1.0, tk.END)
            results_text.insert(tk.END, f"Searching for '{query}'...\n\n")
            
            if self.converter and self.converter.steam_db:
                results = self.converter.steam_db.find_by_name(query)
                if results:
                    for dlc in results:
                        results_text.insert(tk.END, f"App ID: {dlc['app_id']}\n")
                        results_text.insert(tk.END, f"Artist: {dlc.get('artist', 'N/A')}\n")
                        results_text.insert(tk.END, f"Song: {dlc.get('song', 'N/A')}\n")
                        results_text.insert(tk.END, f"Name: {dlc.get('name', 'N/A')}\n")
                        results_text.insert(tk.END, "\n" + "-"*50 + "\n\n")
                else:
                    results_text.insert(tk.END, "No results found.")
            else:
                results_text.insert(tk.END, "Steam database not available.")
        
        ttk.Button(search_frame, text="Search", command=do_search).pack(side=tk.LEFT, padx=5)
        
        search_entry.bind('<Return>', lambda e: do_search())
    
    def show_help(self):
        """Show help/quick start"""
        help_text = """
🎸 Rocksmith 2014 PC → PS4 Converter - Quick Start

1. DRAG & DROP
   • Drag PC .psarc files into the drop zone
   • Or click "Add Files" button

2. CHOOSE OUTPUT
   • Click "Change" to select where to save converted files
   • Each song gets its own folder

3. CONVERT
   • Click "Convert All" to start batch conversion
   • Watch the log for progress

4. COMPLETE CONVERSION
   • Use Song Creator Toolkit: PC → Mac
   • Rename output: song_m.psarc → song_p.psarc
   • Build PKG using generated GP4 files

SETTINGS:
• Region Code: EP0001 (Europe), UP0001 (USA)
• Steam Integration: Auto-fetch DLC info
• Auto-open Output: Opens folder when done

For full documentation, see README files.
        """
        
        messagebox.showinfo("Quick Start Guide", help_text)
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""
🎸 RiffBridge
Rocksmith 2014 PC → PS4 Converter
Version 1.0

Bridge your Rocksmith DLC between platforms
with drag & drop simplicity.

A comprehensive tool for converting Rocksmith 2014 
PC DLC to PS4 PKG format.

Features:
• Drag & drop batch conversion
• Steam DLC integration
• Automatic metadata extraction
• PS4 PKG structure generation

© 2025 - Open Source
MIT License

Converter Status:
• Steam Integration: {'Enabled' if self.settings['use_steam'].get() else 'Disabled'}
• Region: {self.settings['region'].get()}
• Title ID: {self.settings['title_id'].get()}
        """
        
        messagebox.showinfo("About", about_text)

def main():
    """Main entry point"""
    try:
        # Create root window with DnD support
        root = TkinterDnD.Tk()
        
        # Set icon if available
        try:
            if sys.platform == 'win32':
                self.root.iconbitmap('RiffBridge.ico')
            else:
                # For Linux/Mac, use PNG
                icon_img = tk.PhotoImage(file='RiffBridge_512.png')
                self.root.iconphoto(True, icon_img)
        except Exception as e:
            # Icon not critical, continue without it
            pass
        
        # Create and run app
        app = RocksmithGUI(root)
        
        # Start main loop
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application failed to start:\n{e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
