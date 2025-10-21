import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
from PIL import Image, ImageTk
import os
import sys

class EpitopeToFastaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FtihoEpitizer - Epitope to FASTA Converter")
        self.root.geometry("800x700")
        self.root.minsize(750, 650)
        self.root.resizable(True, True)
        
        # Dark mode state
        self.dark_mode = False
        
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
                'accent1': '#35bdb1',  # Teal (kept same)
                'accent2': '#b86c93',  # Pink (kept same)
            }
        }
        
        self.load_logo()
        self.create_ui()
        
    def create_ui(self):
        """Create the user interface"""
        # Clear existing widgets if any
        for widget in self.root.winfo_children():
            widget.destroy()
        
        colors = self.colors['dark'] if self.dark_mode else self.colors['light']
        
        # Set background color
        self.root.configure(bg=colors['bg'])
        
        # Create canvas with scrollbar
        self.canvas = tk.Canvas(self.root, bg=colors['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        
        # Scrollable frame
        scrollable_frame = tk.Frame(self.canvas, bg=colors['bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=scrollable_frame, anchor="n", width=800)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Main centered container inside scrollable frame
        main_container = tk.Frame(scrollable_frame, bg=colors['bg'])
        main_container.pack(padx=60, pady=30, fill=tk.BOTH, expand=True)
        
        # Dark mode toggle button at top right
        toggle_frame = tk.Frame(main_container, bg=colors['bg'])
        toggle_frame.pack(fill=tk.X, pady=(0, 10))
        
        dark_mode_btn = tk.Button(toggle_frame,
                                 text="🌙 Dark" if not self.dark_mode else "☀️ Light",
                                 command=self.toggle_dark_mode,
                                 font=("Arial", 9),
                                 bg=colors['content_bg'],
                                 fg=colors['text'],
                                 relief=tk.FLAT,
                                 padx=15,
                                 pady=5,
                                 cursor='hand2')
        dark_mode_btn.pack(side=tk.RIGHT)
        
        # Logo at the top
        if hasattr(self, 'logo_photo'):
            logo_label = tk.Label(main_container, image=self.logo_photo, bg=colors['bg'])
            logo_label.pack(pady=(10, 10))
        
        # Main title - FtihoEpitizer
        title_label = tk.Label(main_container, 
                              text="FtihoEpitizer", 
                              font=("Arial", 26, "bold"),
                              bg=colors['bg'],
                              fg=colors['accent1'])
        title_label.pack(pady=(0, 5))
        
        # Subtitle
        subtitle_label = tk.Label(main_container,
                                 text="Epitope to FASTA Converter",
                                 font=("Arial", 12),
                                 bg=colors['bg'],
                                 fg=colors['text_secondary'])
        subtitle_label.pack(pady=(0, 20))
        
        # Create styled frame for content
        content_frame = tk.Frame(main_container, bg=colors['content_bg'], relief=tk.RIDGE, borderwidth=2)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Padding inside content frame
        inner_frame = tk.Frame(content_frame, bg=colors['content_bg'])
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)
        
        # Input method selection
        input_method_label = tk.Label(inner_frame, 
                                     text="Select Input Method:", 
                                     font=("Arial", 11, "bold"),
                                     bg=colors['content_bg'],
                                     fg=colors['text'])
        input_method_label.pack(anchor=tk.W, pady=(0, 12))
        
        # Radio buttons frame
        radio_frame = tk.Frame(inner_frame, bg=colors['content_bg'])
        radio_frame.pack(anchor=tk.W, pady=(0, 18))
        
        self.input_method = tk.StringVar(value="manual")
        
        manual_radio = tk.Radiobutton(radio_frame, 
                                     text="Manual Entry", 
                                     variable=self.input_method, 
                                     value="manual",
                                     command=self.toggle_input_method,
                                     font=("Arial", 10),
                                     bg=colors['content_bg'],
                                     fg=colors['text'],
                                     selectcolor=colors['accent1'],
                                     activebackground=colors['content_bg'])
        manual_radio.pack(side=tk.LEFT, padx=(0, 40))
        
        file_radio = tk.Radiobutton(radio_frame,
                                   text="Upload File", 
                                   variable=self.input_method, 
                                   value="file",
                                   command=self.toggle_input_method,
                                   font=("Arial", 10),
                                   bg=colors['content_bg'],
                                   fg=colors['text'],
                                   selectcolor=colors['accent1'],
                                   activebackground=colors['content_bg'])
        file_radio.pack(side=tk.LEFT)
        
        # Manual input section
        self.manual_frame = tk.LabelFrame(inner_frame, 
                                         text="  Manual Input  ",
                                         font=("Arial", 10, "bold"),
                                         bg=colors['content_bg'],
                                         fg=colors['accent2'],
                                         relief=tk.GROOVE,
                                         borderwidth=2)
        self.manual_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 18))
        
        manual_inner = tk.Frame(self.manual_frame, bg=colors['content_bg'])
        manual_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        instruction_label = tk.Label(manual_inner,
                                    text="Enter epitopes (one per line or comma-separated):",
                                    font=("Arial", 9),
                                    bg=colors['content_bg'],
                                    fg=colors['text_secondary'])
        instruction_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Text area for manual input
        text_bg = '#2a2a2a' if self.dark_mode else 'white'
        text_fg = '#e0e0e0' if self.dark_mode else 'black'
        
        self.text_input = scrolledtext.ScrolledText(manual_inner,
                                                   width=70, 
                                                   height=8,
                                                   wrap=tk.WORD,
                                                   font=("Courier", 10),
                                                   relief=tk.SOLID,
                                                   borderwidth=1,
                                                   bg=text_bg,
                                                   fg=text_fg,
                                                   insertbackground=text_fg)
        self.text_input.pack(fill=tk.BOTH, expand=True)
        
        # File upload section
        self.file_frame = tk.LabelFrame(inner_frame,
                                       text="  File Upload  ",
                                       font=("Arial", 10, "bold"),
                                       bg=colors['content_bg'],
                                       fg=colors['accent2'],
                                       relief=tk.GROOVE,
                                       borderwidth=2)
        self.file_frame.pack(fill=tk.X, pady=(0, 18))
        self.file_frame.pack_forget()
        
        file_inner = tk.Frame(self.file_frame, bg=colors['content_bg'])
        file_inner.pack(fill=tk.X, padx=15, pady=20)
        
        # File path display frame
        file_display_frame = tk.Frame(file_inner, bg=colors['content_bg'])
        file_display_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.file_path_var = tk.StringVar(value="No file selected")
        file_path_label = tk.Label(file_display_frame,
                                  textvariable=self.file_path_var,
                                  font=("Arial", 9),
                                  bg=colors['content_bg'],
                                  fg=colors['text_secondary'],
                                  wraplength=500,
                                  justify=tk.LEFT)
        file_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Browse button in center
        browse_button_frame = tk.Frame(file_inner, bg=colors['content_bg'])
        browse_button_frame.pack()
        
        browse_button = tk.Button(browse_button_frame,
                                 text="Browse File",
                                 command=self.browse_file,
                                 font=("Arial", 10, "bold"),
                                 bg=colors['accent1'],
                                 fg='white',
                                 activebackground='#2a9589',
                                 relief=tk.FLAT,
                                 padx=25,
                                 pady=8,
                                 cursor='hand2')
        browse_button.pack()
        
        # Convert button - centered
        button_frame = tk.Frame(inner_frame, bg=colors['content_bg'])
        button_frame.pack(pady=(5, 15))
        
        convert_button = tk.Button(button_frame,
                                  text="Convert to FASTA",
                                  command=self.convert_to_fasta,
                                  font=("Arial", 13, "bold"),
                                  bg=colors['accent2'],
                                  fg='white',
                                  activebackground='#9d5a7d',
                                  relief=tk.FLAT,
                                  padx=40,
                                  pady=12,
                                  cursor='hand2')
        convert_button.pack()
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(inner_frame,
                               textvariable=self.status_var,
                               font=("Arial", 10, "italic"),
                               bg=colors['content_bg'],
                               fg=colors['accent1'])
        status_label.pack(pady=(5, 0))
        
        # Credits footer - centered at bottom
        credits_frame = tk.Frame(main_container, bg=colors['bg'])
        credits_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(15, 10))
        
        credits_label = tk.Label(credits_frame,
                                text="© ftihochou 2025",
                                font=("Arial", 9, "italic"),
                                bg=colors['bg'],
                                fg=colors['text_light'])
        credits_label.pack(anchor=tk.CENTER)
        
        # Update canvas width on window resize
        def on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas.find_all()[0], width=event.width)
        self.canvas.bind('<Configure>', on_canvas_configure)
    
    def toggle_dark_mode(self):
        """Toggle between light and dark mode"""
        self.dark_mode = not self.dark_mode
        self.create_ui()
    
    def load_logo(self):
        """Load the logo image"""
        logo_files = ["FtihoEpitizerlogo.jpg", "FtihoEpitizerlogo.png"]
        
        for logo_file in logo_files:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            logo_path = os.path.join(base_path, logo_file)
            
            if os.path.exists(logo_path):
                try:
                    logo_image = Image.open(logo_path)
                    logo_image.thumbnail((160, 160), Image.Resampling.LANCZOS)
                    self.logo_photo = ImageTk.PhotoImage(logo_image)
                    return
                except Exception as e:
                    print(f"Error loading logo: {e}")
        
        print("Logo file not found. Continuing without logo.")
    
    def toggle_input_method(self):
        """Toggle between manual input and file upload"""
        if self.input_method.get() == "manual":
            self.file_frame.pack_forget()
            self.manual_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 18))
        else:
            self.manual_frame.pack_forget()
            self.file_frame.pack(fill=tk.X, pady=(0, 18))
    
    def browse_file(self):
        """Open file dialog to select input file"""
        filename = filedialog.askopenfilename(
            title="Select Epitope File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.file_path_var.set(os.path.basename(filename))
            self.selected_file = filename
            self.status_var.set("File selected ✓")
    
    def parse_epitopes(self, text):
        """Parse epitopes from text (comma or newline separated)"""
        epitopes = []
        
        if ',' in text:
            epitopes = [seq.strip() for seq in text.split(',') if seq.strip()]
        else:
            epitopes = [line.strip() for line in text.split('\n') if line.strip()]
        
        return epitopes
    
    def convert_to_fasta(self):
        """Convert epitopes to FASTA format"""
        epitopes = []
        
        try:
            if self.input_method.get() == "manual":
                text = self.text_input.get("1.0", tk.END)
                if not text.strip():
                    messagebox.showwarning("Warning", "Please enter epitope sequences!")
                    return
                epitopes = self.parse_epitopes(text)
            else:
                if not hasattr(self, 'selected_file'):
                    messagebox.showwarning("Warning", "Please select a file!")
                    return
                
                with open(self.selected_file, 'r') as f:
                    text = f.read()
                epitopes = self.parse_epitopes(text)
            
            if not epitopes:
                messagebox.showwarning("Warning", "No epitopes found!")
                return
            
            output_file = filedialog.asksaveasfilename(
                defaultextension=".fasta",
                filetypes=[("FASTA files", "*.fasta"), ("Text files", "*.txt"), 
                          ("All files", "*.*")],
                title="Save FASTA File"
            )
            
            if not output_file:
                return
            
            with open(output_file, 'w') as f:
                for i, epitope in enumerate(epitopes, start=1):
                    f.write(f">seq{i}\n{epitope}\n")
            
            messagebox.showinfo("Success", 
                              f"Successfully converted {len(epitopes)} epitopes to FASTA!\n"
                              f"Saved to: {os.path.basename(output_file)}")
            self.status_var.set(f"✓ Converted {len(epitopes)} sequences")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_var.set("Error occurred")

def main():
    root = tk.Tk()
    app = EpitopeToFastaGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
