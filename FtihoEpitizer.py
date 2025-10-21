"""
FtihoEpitizer - Epitope to FASTA Converter

A desktop application for converting epitope sequences to FASTA format.
Supports manual input, file upload, duplicate removal, and dark/light themes.

Author: ftihochou
Date: 2025
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
from PIL import Image, ImageTk
import os
import sys
from typing import List, Optional, Tuple, Dict


class EpitopeToFastaGUI:
    """
    A GUI application for converting epitope sequences to FASTA format.
    
    This class provides a user interface for:
    - Manual input of epitope sequences
    - File upload of epitope sequences
    - Converting sequences to FASTA format
    - Dark/light mode toggle
    - Duplicate removal option
    
    Attributes:
        root (tk.Tk): The main window of the application
        dark_mode (bool): Current theme state
        colors (dict): Color schemes for light and dark modes
        remove_duplicates (tk.BooleanVar): Checkbox state for duplicate removal
    """
    
    # Class-level constants
    DEFAULT_WINDOW_SIZE = "800x700"
    MIN_WINDOW_WIDTH = 750
    MIN_WINDOW_HEIGHT = 650
    MAX_INPUT_SIZE = 10000000  # 10MB limit
    LOGO_SIZE = (160, 160)
    
    # Font sizes
    FONT_TITLE = 26
    FONT_SUBTITLE = 12
    FONT_HEADING = 11
    FONT_NORMAL = 10
    FONT_SMALL = 9
    
    # Padding
    PADDING_MAIN = 60
    PADDING_CONTENT = 30
    PADDING_SECTION = 15
    
    # Valid amino acid characters for epitope validation
    VALID_AMINO_ACIDS = set('ACDEFGHIKLMNPQRSTVWY')
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the FtihoEpitizer application.
        
        Args:
            root: The main Tkinter window
        """
        self.root = root
        self.root.title("FtihoEpitizer - Epitope to FASTA Converter")
        self.root.geometry(self.DEFAULT_WINDOW_SIZE)
        self.root.minsize(self.MIN_WINDOW_WIDTH, self.MIN_WINDOW_HEIGHT)
        self.root.resizable(True, True)
        
        # Set window icon
        self.set_window_icon()
        
        # State variables
        self.dark_mode = False
        self.selected_file: Optional[str] = None
        self._cached_colors: Optional[Tuple[bool, Dict]] = None
        
        # Color schemes
        self.colors = {
            'light': {
                'bg': '#f5f5f5',
                'content_bg': 'white',
                'text': '#333333',
                'text_secondary': '#666666',
                'text_light': '#999999',
                'accent1': '#35bdb1',  # Teal
                'accent2': '#b86c93',  # Pink
            },
            'dark': {
                'bg': '#1e1e1e',
                'content_bg': '#2d2d2d',
                'text': '#e0e0e0',
                'text_secondary': '#b0b0b0',
                'text_light': '#808080',
                'accent1': '#35bdb1',
                'accent2': '#b86c93',
            }
        }
        
        # Load resources
        self.load_logo()
        
        # Create UI
        self.create_ui()
    
    def get_current_colors(self) -> Dict[str, str]:
        """
        Get current color scheme with caching for performance.
        
        Returns:
            Dictionary containing current theme colors
        """
        if self._cached_colors is None or self._cached_colors[0] != self.dark_mode:
            self._cached_colors = (
                self.dark_mode,
                self.colors['dark'] if self.dark_mode else self.colors['light']
            )
        return self._cached_colors[1]
    
    def set_window_icon(self) -> None:
        """Set the window icon from the icon file."""
        icon_file = "FtihoEpitizer.ico"
        
        # Determine base path
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        icon_path = os.path.join(base_path, icon_file)
        
        try:
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                print(f"Icon file not found at: {icon_path}")
        except Exception as e:
            # Fallback for Linux/Mac
            try:
                png_icon = "FtihoEpitizer.png"
                png_path = os.path.join(base_path, png_icon)
                if os.path.exists(png_path):
                    icon = tk.PhotoImage(file=png_path)
                    self.root.iconphoto(True, icon)
            except Exception as e2:
                print(f"Could not set icon: {e}, {e2}")
    
    def load_logo(self) -> None:
        """Load and cache the application logo."""
        logo_files = ["FtihoEpitizerlogo.jpg", "FtihoEpitizerlogo.png"]
        
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        for logo_file in logo_files:
            logo_path = os.path.join(base_path, logo_file)
            
            if os.path.exists(logo_path):
                try:
                    logo_image = Image.open(logo_path)
                    logo_image.thumbnail(self.LOGO_SIZE, Image.Resampling.LANCZOS)
                    self.logo_photo = ImageTk.PhotoImage(logo_image)
                    return
                except Exception as e:
                    print(f"Error loading logo: {e}")
        
        print("Logo file not found. Continuing without logo.")
    
    def create_ui(self) -> None:
        """Create the main user interface."""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        colors = self.get_current_colors()
        self.root.configure(bg=colors['bg'])
        
        # Create scrollable canvas
        self._create_scrollable_canvas(colors)
        
        # Create UI sections
        self._create_header(colors)
        self._create_input_section(colors)
        self._create_options_section(colors)
        self._create_convert_button(colors)
        self._create_status_label(colors)
        self._create_footer(colors)
    
    def _create_scrollable_canvas(self, colors: Dict[str, str]) -> None:
        """Create canvas with scrollbar for content."""
        self.canvas = tk.Canvas(self.root, bg=colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=colors['bg'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="n", width=800)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mousewheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Main container
        self.main_container = tk.Frame(
            self.scrollable_frame,
            bg=colors['bg']
        )
        self.main_container.pack(
            padx=self.PADDING_MAIN,
            pady=self.PADDING_CONTENT,
            fill=tk.BOTH,
            expand=True
        )
    
    def _on_mousewheel(self, event: tk.Event) -> None:
        """Handle mousewheel scrolling."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _create_header(self, colors: Dict[str, str]) -> None:
        """Create header section with logo and title."""
        # Logo
        if hasattr(self, 'logo_photo'):
            logo_label = tk.Label(
                self.main_container,
                image=self.logo_photo,
                bg=colors['bg']
            )
            logo_label.pack(pady=(10, 10))
        
        # Title
        title_label = tk.Label(
            self.main_container,
            text="FtihoEpitizer",
            font=("Arial", self.FONT_TITLE, "bold"),
            bg=colors['bg'],
            fg=colors['accent1']
        )
        title_label.pack(pady=(0, 5))
        
        # Subtitle
        subtitle_label = tk.Label(
            self.main_container,
            text="Epitope to FASTA Converter",
            font=("Arial", self.FONT_SUBTITLE),
            bg=colors['bg'],
            fg=colors['text_secondary']
        )
        subtitle_label.pack(pady=(0, 20))
    
    def _create_input_section(self, colors: Dict[str, str]) -> None:
        """Create input section with manual entry and file upload options."""
        # Content frame
        content_frame = tk.Frame(
            self.main_container,
            bg=colors['content_bg'],
            relief=tk.RIDGE,
            borderwidth=2
        )
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        self.inner_frame = tk.Frame(content_frame, bg=colors['content_bg'])
        self.inner_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=self.PADDING_CONTENT,
            pady=25
        )
        
        # Input method selection
        input_method_label = tk.Label(
            self.inner_frame,
            text="Select Input Method:",
            font=("Arial", self.FONT_HEADING, "bold"),
            bg=colors['content_bg'],
            fg=colors['text']
        )
        input_method_label.pack(anchor=tk.W, pady=(0, 12))
        
        # Radio buttons
        self._create_radio_buttons(colors)
        
        # Manual input frame
        self._create_manual_input_frame(colors)
        
        # File upload frame
        self._create_file_upload_frame(colors)
    
    def _create_radio_buttons(self, colors: Dict[str, str]) -> None:
        """Create radio buttons for input method selection."""
        radio_frame = tk.Frame(self.inner_frame, bg=colors['content_bg'])
        radio_frame.pack(anchor=tk.W, pady=(0, 18))
        
        self.input_method = tk.StringVar(value="manual")
        
        manual_radio = tk.Radiobutton(
            radio_frame,
            text="Manual Entry",
            variable=self.input_method,
            value="manual",
            command=self.toggle_input_method,
            font=("Arial", self.FONT_NORMAL),
            bg=colors['content_bg'],
            fg=colors['text'],
            selectcolor=colors['accent1'],
            activebackground=colors['content_bg']
        )
        manual_radio.pack(side=tk.LEFT, padx=(0, 40))
        
        file_radio = tk.Radiobutton(
            radio_frame,
            text="Upload File",
            variable=self.input_method,
            value="file",
            command=self.toggle_input_method,
            font=("Arial", self.FONT_NORMAL),
            bg=colors['content_bg'],
            fg=colors['text'],
            selectcolor=colors['accent1'],
            activebackground=colors['content_bg']
        )
        file_radio.pack(side=tk.LEFT)
    
    def _create_manual_input_frame(self, colors: Dict[str, str]) -> None:
        """Create manual input text area."""
        self.manual_frame = tk.LabelFrame(
            self.inner_frame,
            text="  Manual Input  ",
            font=("Arial", self.FONT_NORMAL, "bold"),
            bg=colors['content_bg'],
            fg=colors['accent2'],
            relief=tk.GROOVE,
            borderwidth=2
        )
        self.manual_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 18))
        
        manual_inner = tk.Frame(self.manual_frame, bg=colors['content_bg'])
        manual_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        instruction_label = tk.Label(
            manual_inner,
            text="Enter epitopes (one per line or comma-separated):",
            font=("Arial", self.FONT_SMALL),
            bg=colors['content_bg'],
            fg=colors['text_secondary']
        )
        instruction_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Text area
        text_bg = '#2a2a2a' if self.dark_mode else 'white'
        text_fg = '#e0e0e0' if self.dark_mode else 'black'
        
        self.text_input = scrolledtext.ScrolledText(
            manual_inner,
            width=70,
            height=8,
            wrap=tk.WORD,
            font=("Courier", self.FONT_NORMAL),
            relief=tk.SOLID,
            borderwidth=1,
            bg=text_bg,
            fg=text_fg,
            insertbackground=text_fg
        )
        self.text_input.pack(fill=tk.BOTH, expand=True)
    
    def _create_file_upload_frame(self, colors: Dict[str, str]) -> None:
        """Create file upload section."""
        self.file_frame = tk.LabelFrame(
            self.inner_frame,
            text="  File Upload  ",
            font=("Arial", self.FONT_NORMAL, "bold"),
            bg=colors['content_bg'],
            fg=colors['accent2'],
            relief=tk.GROOVE,
            borderwidth=2
        )
        self.file_frame.pack(fill=tk.X, pady=(0, 18))
        self.file_frame.pack_forget()
        
        file_inner = tk.Frame(self.file_frame, bg=colors['content_bg'])
        file_inner.pack(fill=tk.X, padx=15, pady=20)
        
        # File path display
        file_display_frame = tk.Frame(file_inner, bg=colors['content_bg'])
        file_display_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_path_var = tk.StringVar(value="No file selected")
        file_path_label = tk.Label(
            file_display_frame,
            textvariable=self.file_path_var,
            font=("Arial", self.FONT_SMALL),
            bg=colors['content_bg'],
            fg=colors['text_secondary'],
            wraplength=500,
            justify=tk.LEFT
        )
        file_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Browse button
        browse_button_frame = tk.Frame(file_inner, bg=colors['content_bg'])
        browse_button_frame.pack()
        
        browse_button = tk.Button(
            browse_button_frame,
            text="Browse File",
            command=self.browse_file,
            font=("Arial", self.FONT_NORMAL, "bold"),
            bg=colors['accent1'],
            fg='white',
            activebackground='#2a9589',
            relief=tk.FLAT,
            padx=25,
            pady=8,
            cursor='hand2'
        )
        browse_button.pack()
    
    def _create_options_section(self, colors: Dict[str, str]) -> None:
        """Create options section with checkbox for duplicate removal."""
        options_frame = tk.Frame(self.inner_frame, bg=colors['content_bg'])
        options_frame.pack(pady=(0, 15))
        
        self.remove_duplicates = tk.BooleanVar(value=False)
        duplicates_check = tk.Checkbutton(
            options_frame,
            text="Remove duplicate epitopes",
            variable=self.remove_duplicates,
            font=("Arial", self.FONT_NORMAL),
            bg=colors['content_bg'],
            fg=colors['text'],
            selectcolor=colors['accent1'],
            activebackground=colors['content_bg'],
            cursor='hand2'
        )
        duplicates_check.pack()
    
    def _create_convert_button(self, colors: Dict[str, str]) -> None:
        """Create the main convert button."""
        button_frame = tk.Frame(self.inner_frame, bg=colors['content_bg'])
        button_frame.pack(pady=(5, 15))
        
        convert_button = tk.Button(
            button_frame,
            text="Convert to FASTA",
            command=self.convert_to_fasta,
            font=("Arial", 13, "bold"),
            bg=colors['accent2'],
            fg='white',
            activebackground='#9d5a7d',
            relief=tk.FLAT,
            padx=40,
            pady=12,
            cursor='hand2'
        )
        convert_button.pack()
    
    def _create_status_label(self, colors: Dict[str, str]) -> None:
        """Create status label for user feedback."""
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(
            self.inner_frame,
            textvariable=self.status_var,
            font=("Arial", self.FONT_NORMAL, "italic"),
            bg=colors['content_bg'],
            fg=colors['accent1']
        )
        status_label.pack(pady=(5, 0))
    
    def _create_footer(self, colors: Dict[str, str]) -> None:
        """Create footer with credits and dark mode toggle."""
        footer_frame = tk.Frame(self.main_container, bg=colors['bg'])
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(15, 10))
        
        # Credits
        credits_label = tk.Label(
            footer_frame,
            text="© ftihochou 2025",
            font=("Arial", self.FONT_SMALL, "italic"),
            bg=colors['bg'],
            fg=colors['text_light']
        )
        credits_label.pack(side=tk.LEFT)
        
        # Dark mode toggle
        dark_mode_btn = tk.Button(
            footer_frame,
            text="🌙 Dark Mode" if not self.dark_mode else "☀️ Light Mode",
            command=self.toggle_dark_mode,
            font=("Arial", self.FONT_SMALL),
            bg=colors['content_bg'],
            fg=colors['text'],
            activebackground=colors['accent1'],
            activeforeground='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        dark_mode_btn.pack(side=tk.RIGHT)
        
        # Canvas resize handler
        self.canvas.bind('<Configure>', self._on_canvas_configure)
    
    def _on_canvas_configure(self, event: tk.Event) -> None:
        """Handle canvas resize events."""
        if self.canvas.find_all():
            self.canvas.itemconfig(self.canvas.find_all()[0], width=event.width)
    
    def toggle_dark_mode(self) -> None:
        """Toggle between light and dark mode."""
        self.dark_mode = not self.dark_mode
        self._cached_colors = None  # Invalidate cache
        self.create_ui()
    
    def toggle_input_method(self) -> None:
        """Toggle between manual input and file upload."""
        if self.input_method.get() == "manual":
            self.file_frame.pack_forget()
            self.manual_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 18))
        else:
            self.manual_frame.pack_forget()
            self.file_frame.pack(fill=tk.X, pady=(0, 18))
    
    def browse_file(self) -> None:
        """Open file dialog to select input file."""
        try:
            filename = filedialog.askopenfilename(
                title="Select Epitope File",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                self.file_path_var.set(os.path.basename(filename))
                self.selected_file = filename
                self.status_var.set("File selected ✓")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")
            self.status_var.set("Error selecting file")
    
    def validate_input(self, text: str) -> bool:
        """
        Validate input size and format.
        
        Args:
            text: Input text to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(text, str):
            messagebox.showerror("Error", "Invalid input type")
            return False
        
        if len(text) > self.MAX_INPUT_SIZE:
            messagebox.showerror(
                "Error",
                f"Input size too large. Maximum size is {self.MAX_INPUT_SIZE / 1000000}MB"
            )
            return False
        
        return True
    
    def _is_valid_epitope(self, sequence: str) -> bool:
        """
        Validate if a sequence contains only valid amino acid characters.
        
        Args:
            sequence: Epitope sequence to validate
            
        Returns:
            True if valid, False otherwise
        """
        return all(char.upper() in self.VALID_AMINO_ACIDS for char in sequence)
    
    def parse_epitopes(self, text: str) -> List[str]:
        """
        Parse epitopes from text input.
        
        Args:
            text: Input text containing epitopes
            
        Returns:
            List of parsed epitope sequences
            
        Raises:
            ValueError: If epitope format is invalid
        """
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        
        epitopes = []
        invalid_sequences = []
        
        # Parse comma or newline separated
        if ',' in text:
            raw_epitopes = text.split(',')
        else:
            raw_epitopes = text.split('\n')
        
        for epitope in raw_epitopes:
            epitope = epitope.strip()
            if epitope:
                if not self._is_valid_epitope(epitope):
                    invalid_sequences.append(epitope)
                else:
                    epitopes.append(epitope)
        
        # If there are invalid sequences, raise an error with details
        if invalid_sequences:
            error_msg = "Invalid epitope sequence(s) detected:\n\n"
            # Show up to 5 invalid sequences
            for seq in invalid_sequences[:5]:
                error_msg += f"• {seq}\n"
            if len(invalid_sequences) > 5:
                error_msg += f"\n...and {len(invalid_sequences) - 5} more\n"
            error_msg += "\nEpitopes must contain only valid amino acid letters:\nA, C, D, E, F, G, H, I, K, L, M, N, P, Q, R, S, T, V, W, Y"
            raise ValueError(error_msg)
        
        return epitopes
    
    def convert_to_fasta(self) -> None:
        """Convert epitopes to FASTA format with error handling."""
        epitopes = []
        
        try:
            # Get input based on method
            if self.input_method.get() == "manual":
                text = self.text_input.get("1.0", tk.END)
                if not text.strip():
                    messagebox.showwarning("Warning", "Please enter epitope sequences!")
                    return
                
                if not self.validate_input(text):
                    return
                
                epitopes = self.parse_epitopes(text)
                
            else:
                if not self.selected_file:
                    messagebox.showwarning("Warning", "Please select a file!")
                    return
                
                try:
                    with open(self.selected_file, 'r', encoding='utf-8') as f:
                        text = f.read()
                    
                    if not self.validate_input(text):
                        return
                    
                    epitopes = self.parse_epitopes(text)
                    
                except FileNotFoundError:
                    messagebox.showerror("Error", "File not found")
                    return
                except PermissionError:
                    messagebox.showerror("Error", "Permission denied to read file")
                    return
                except UnicodeDecodeError:
                    messagebox.showerror("Error", "File encoding not supported. Please use UTF-8")
                    return
            
            if not epitopes:
                messagebox.showwarning("Warning", "No valid epitopes found!")
                return
            
            # Store original count
            original_count = len(epitopes)
            
            # Remove duplicates if requested
            if self.remove_duplicates.get():
                epitopes = self._remove_duplicates(epitopes)
                duplicates_removed = original_count - len(epitopes)
                if duplicates_removed > 0:
                    self.status_var.set(f"Removed {duplicates_removed} duplicate(s)")
            
            # Save to file
            output_file = filedialog.asksaveasfilename(
                defaultextension=".fasta",
                filetypes=[
                    ("FASTA files", "*.fasta"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*")
                ],
                title="Save FASTA File"
            )
            
            if not output_file:
                return
            
            # Write FASTA file
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    for i, epitope in enumerate(epitopes, start=1):
                        f.write(f">seq{i}\n{epitope}\n")
            except PermissionError:
                messagebox.showerror("Error", "Permission denied to write file")
                return
            except Exception as e:
                messagebox.showerror("Error", f"Failed to write file: {str(e)}")
                return
            
            # Success message
            message = f"Successfully converted {len(epitopes)} epitopes to FASTA!"
            if self.remove_duplicates.get() and original_count != len(epitopes):
                message += f"\n({original_count - len(epitopes)} duplicates removed)"
            message += f"\nSaved to: {os.path.basename(output_file)}"
            
            messagebox.showinfo("Success", message)
            self.status_var.set(f"✓ Converted {len(epitopes)} sequences")
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            self.status_var.set("Invalid epitope sequence(s)")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            self.status_var.set("Error occurred")
    
    def _remove_duplicates(self, epitopes: List[str]) -> List[str]:
        """
        Remove duplicate epitopes while preserving order.
        
        Args:
            epitopes: List of epitope sequences
            
        Returns:
            List with duplicates removed
        """
        seen = set()
        unique_epitopes = []
        for epitope in epitopes:
            if epitope not in seen:
                seen.add(epitope)
                unique_epitopes.append(epitope)
        return unique_epitopes
    
    # Testing support methods
    def get_epitope_count(self) -> int:
        """
        Get the number of currently loaded epitopes.
        
        Returns:
            Number of epitopes in current input
        """
        try:
            if self.input_method.get() == "manual":
                text = self.text_input.get("1.0", tk.END)
                return len(self.parse_epitopes(text))
            return 0
        except Exception:
            return 0
    
    def get_current_mode(self) -> str:
        """
        Get the current input mode.
        
        Returns:
            'manual' or 'file'
        """
        return self.input_method.get()
    
    def __del__(self):
        """Clean up resources on deletion."""
        try:
            if hasattr(self, 'logo_photo'):
                del self.logo_photo
            
            if hasattr(self, 'canvas'):
                self.canvas.unbind_all("<MouseWheel>")
        except Exception:
            pass


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = EpitopeToFastaGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
### All rights reserved Ftihochou
