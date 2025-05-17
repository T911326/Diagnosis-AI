import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from diagnosis_engine import DiagnosisEngine
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
from localization import get_translation, available_languages
import os

class DiagnosisApp:
    def __init__(self, root):
        # Core setup
        self.root = root
        self.language = "en"
        self.engine = DiagnosisEngine()
        self.diagnosis_results = []
        self.symptom_vars = {}
        
        # Color scheme - Modern and vibrant
        self.colors = {
            "bg_main": "#F5F7FA",  # Light background
            "bg_card": "#FFFFFF",   # White cards
            "primary": "#4361EE",   # Primary action color (deep blue)
            "secondary": "#3A0CA3", # Secondary color (deep purple)
            "accent1": "#4CC9F0",   # Accent color (light blue)
            "accent2": "#F72585",   # Accent color (pink)
            "accent3": "#7209B7",   # Accent color (purple)
            "accent4": "#4D908E",   # Accent color (teal)
            "text_dark": "#2B2D42", # Dark text
            "text_light": "#FFFFFF", # Light text
            "success": "#06D6A0",   # Success color
            "warning": "#FFD166",   # Warning color
            "danger": "#EF476F",    # Danger/error color
            "border": "#E0E0E0"     # Border color
        }
        
        # Set up the root window
        self.root.title(get_translation(self.language, "title"))
        self.root.configure(bg=self.colors["bg_main"])
        
        # Font configuration for larger text
        default_font = ("Segoe UI", 12)
        header_font = ("Segoe UI", 18, "bold")
        title_font = ("Segoe UI", 24, "bold")
        button_font = ("Segoe UI", 13)
        
        # Configure default fonts
        self.root.option_add("*Font", default_font)
        self.root.option_add("*TButton*Font", button_font)
        self.root.option_add("*TLabel*Font", default_font)
        self.root.option_add("*TCheckbutton*Font", default_font)
        
        # Apply a theme to ttk widgets
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles with rounded corners and modern look
        self.style.configure('TFrame', background=self.colors["bg_main"])
        self.style.configure('Card.TFrame', background=self.colors["bg_card"], relief="flat")
        
        # Button styles with rounded corners (simulation)
        self.style.layout('Rounded.TButton', [
            ('Button.focus', {
                'children': [('Button.padding', {
                    'children': [('Button.label', {'side': 'left', 'expand': 1})],
                    'expand': 1})],
                'expand': 1, 'sticky': 'nswe'
            })
        ])
        
        # Default button style
        self.style.configure('Rounded.TButton', 
                             background=self.colors["primary"], 
                             foreground=self.colors["text_light"],
                             borderwidth=0, 
                             focusthickness=0,
                             focuscolor='none',
                             padding=(20, 10),
                             font=button_font)
                             
        self.style.map('Rounded.TButton', 
                       background=[('active', self.colors["secondary"])],
                       foreground=[('active', self.colors["text_light"])])
                       
        # Different colored button styles
        button_colors = {
            "Primary": {"bg": self.colors["primary"], "fg": self.colors["text_light"]},
            "Success": {"bg": self.colors["success"], "fg": self.colors["text_light"]},
            "Warning": {"bg": self.colors["warning"], "fg": self.colors["text_dark"]},
            "Danger": {"bg": self.colors["danger"], "fg": self.colors["text_light"]},
            "Secondary": {"bg": self.colors["secondary"], "fg": self.colors["text_light"]},
            "Accent1": {"bg": self.colors["accent1"], "fg": self.colors["text_dark"]},
            "Accent3": {"bg": self.colors["accent3"], "fg": self.colors["text_light"]}
        }
        
        for name, colors in button_colors.items():
            self.style.configure(f'{name}.Rounded.TButton', 
                                background=colors["bg"], 
                                foreground=colors["fg"])
            self.style.map(f'{name}.Rounded.TButton', 
                          background=[('active', self._darken_color(colors["bg"]))],
                          foreground=[('active', colors["fg"])])
        
        # Checkbox style
        self.style.configure('TCheckbutton', 
                            background=self.colors["bg_main"], 
                            font=default_font)
        
        # Label styles
        self.style.configure('TLabel', 
                            background=self.colors["bg_main"], 
                            foreground=self.colors["text_dark"],
                            font=default_font)
        
        self.style.configure('Title.TLabel', 
                            background=self.colors["bg_main"], 
                            foreground=self.colors["primary"],
                            font=title_font)
                            
        self.style.configure('Header.TLabel', 
                            background=self.colors["bg_main"], 
                            foreground=self.colors["secondary"],
                            font=header_font)
                            
        # Entry style
        self.style.configure('TEntry', 
                            fieldbackground=self.colors["bg_card"],
                            bordercolor=self.colors["border"],
                            lightcolor=self.colors["border"],
                            darkcolor=self.colors["border"],
                            borderwidth=1,
                            font=default_font)
        
        # Combobox style
        self.style.configure('TCombobox', 
                            fieldbackground=self.colors["bg_card"],
                            background=self.colors["primary"],
                            foreground=self.colors["text_dark"],
                            arrowcolor=self.colors["primary"],
                            font=default_font)
        
        # Updated symptoms data with more comprehensive categories and symptoms for new diseases
        self.symptoms_data = {
            "Respiratory": ["cough", "shortness of breath", "sore throat", "loss of taste or smell", "wheezing", "chest pain"],
            "Gastrointestinal": ["nausea", "vomiting", "diarrhea", "abdominal pain", "feeling of fullness", "jaundice", "dark urine"],
            "General": ["fever", "fatigue", "body aches", "night sweats", "unexplained weight loss"],
            "Neurological": ["headache", "dizziness", "blurred vision", "sensitivity to light", "confusion", "persistent sadness"],
            "Metabolic": ["frequent urination", "increased thirst", "unexplained weight loss", "extreme hunger"],
            "Psychiatric": ["excessive worry", "restlessness", "difficulty concentrating", "loss of interest", "sleep disturbance"],
            "Musculoskeletal": ["joint pain", "joint stiffness", "swelling", "reduced range of motion"]
        }
        
        # Initialize symptom variables
        for category, symptoms in self.symptoms_data.items():
            for symptom in symptoms:
                self.symptom_vars[symptom] = tk.BooleanVar()

        # Create the GUI
        self.create_gui(root)
        self.update_ui_text()
        
    def _darken_color(self, hex_color, factor=0.8):
        """Darken a hex color by a factor (0-1)"""
        # Convert hex to RGB
        h = hex_color.lstrip('#')
        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
        
        # Darken
        rgb_darkened = tuple(int(c * factor) for c in rgb)
        
        # Convert back to hex
        return f'#{rgb_darkened[0]:02x}{rgb_darkened[1]:02x}{rgb_darkened[2]:02x}'

    def create_gui(self, root):
        # Main container with padding
        main_container = ttk.Frame(root, padding=20, style='TFrame')
        main_container.pack(fill="both", expand=True)
        
        # App title with logo
        title_frame = ttk.Frame(main_container, style='TFrame')
        title_frame.pack(fill="x", pady=(0, 20))
        
        # Title with large bold font
        self.title_label = ttk.Label(title_frame, 
                                text=get_translation(self.language, "title"),
                                style='Title.TLabel')
        self.title_label.pack(side=tk.LEFT)
        
        # Language Selection
        lang_frame = ttk.Frame(title_frame, style='TFrame')
        lang_frame.pack(side=tk.RIGHT)
        
        ttk.Label(lang_frame, 
                 text=get_translation(self.language, "language_select"),
                 style='TLabel').pack(side=tk.LEFT, padx=(0, 10))
                 
        self.lang_var = tk.StringVar(root)
        self.lang_var.set(self.language)
        
        # Get language display names in a format "English (en)"
        lang_names = [f"{get_translation('en', f'lang_{lang}')} ({lang})" for lang in available_languages()]
        
        lang_menu = ttk.Combobox(lang_frame, 
                               textvariable=self.lang_var, 
                               values=lang_names, 
                               width=20,
                               font=("Segoe UI", 12),
                               state="readonly")
        lang_menu.pack(side=tk.LEFT)
        lang_menu.bind("<<ComboboxSelected>>", self.on_language_change)

        # Content area with cards
        content_frame = ttk.Frame(main_container, style='TFrame')
        content_frame.pack(fill="both", expand=True, pady=10)
        
        # Create left panel for search and symptoms
        left_panel = ttk.Frame(content_frame, style='Card.TFrame', padding=15)
        left_panel.pack(side=tk.LEFT, fill="both", expand=True, padx=(0, 10))
        
        # Search section with rounded style
        search_frame = ttk.Frame(left_panel, style='Card.TFrame', padding=10)
        search_frame.pack(fill="x", pady=(0, 15))
        
        # Section header
        ttk.Label(search_frame, 
                 text=get_translation(self.language, "search_symptoms"),
                 style='Header.TLabel').pack(anchor="w", pady=(0, 10))
                 
        # Search entry with custom style
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, 
                               textvariable=self.search_var, 
                               font=("Segoe UI", 14),
                               style='TEntry')
        search_entry.pack(fill="x", expand=True, ipady=8)
        search_entry.bind("<KeyRelease>", self.filter_symptoms)

        # Symptom section with improved scrolling
        symptom_section = ttk.Frame(left_panel, style='Card.TFrame')
        symptom_section.pack(fill="both", expand=True)
        
        # Scrollable frame for symptoms
        symptom_container = ttk.Frame(symptom_section, style='Card.TFrame')
        symptom_container.pack(fill="both", expand=True, padx=5)
        
        # Canvas for scrolling with custom styling
        canvas = tk.Canvas(symptom_container, 
                        bg=self.colors["bg_card"], 
                        highlightthickness=0,
                        bd=0)
        scrollbar = ttk.Scrollbar(symptom_container, 
                                orient="vertical", 
                                command=canvas.yview)
        
        # Scrollable frame
        self.symptom_frame = ttk.Frame(canvas, style='Card.TFrame', padding=10)
        
        # Configure the canvas
        canvas.create_window((0, 0), window=self.symptom_frame, anchor="nw", tags="self.symptom_frame")
        
        # Pack the scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind the frame size changes to adjust the scroll region
        self.symptom_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("self.symptom_frame", width=e.width - 5))
        
        # Add mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Display initial symptoms
        self.display_symptoms()

        # Create right panel for actions
        right_panel = ttk.Frame(content_frame, style='Card.TFrame', padding=15)
        right_panel.pack(side=tk.RIGHT, fill="both", padx=(10, 0), expand=False, anchor="ne")
        
        # Action buttons section
        action_section = ttk.Frame(right_panel, style='Card.TFrame')
        action_section.pack(fill="x", pady=10)
        
        # Action header
        ttk.Label(action_section, 
                 text="Actions",
                 style='Header.TLabel').pack(anchor="w", pady=(0, 15))
        
        # Button definitions with colors and icons
        button_data = [
            {"text": get_translation(self.language, "diagnose"), 
             "command": self.diagnose, 
             "style": "Success.Rounded.TButton", 
             "name": "diagnose_button",
             "pady": 15},
            {"text": get_translation(self.language, "chart"), 
             "command": self.show_chart, 
             "style": "Primary.Rounded.TButton", 
             "name": "chart_button",
             "pady": 10},
            {"text": get_translation(self.language, "export"), 
             "command": self.export_to_pdf, 
             "style": "Accent1.Rounded.TButton", 
             "name": "export_button",
             "pady": 10},
            {"text": get_translation(self.language, "save"), 
             "command": self.save_results, 
             "style": "Secondary.Rounded.TButton", 
             "name": "save_button",
             "pady": 10},
            {"text": get_translation(self.language, "clear"), 
             "command": self.clear_selections, 
             "style": "Danger.Rounded.TButton", 
             "name": "clear_button",
             "pady": 10}
        ]
        
        # Create action buttons
        for btn_info in button_data:
            btn = ttk.Button(action_section, 
                           text=btn_info["text"], 
                           command=btn_info["command"], 
                           style=btn_info["style"],
                           padding=(20, 15))
            btn.pack(fill="x", pady=btn_info["pady"])
            
            # Store references to buttons for later text updates
            setattr(self, btn_info["name"], btn)
            
        # Help section
        help_section = ttk.Frame(right_panel, style='Card.TFrame', padding=10)
        help_section.pack(fill="x", pady=(20, 0))
        
        # Help header
        ttk.Label(help_section, 
                 text="Help",
                 style='Header.TLabel').pack(anchor="w", pady=(0, 10))
                 
        # Help text
        help_text = ("Select symptoms from the list and click Diagnose to get " 
                   "potential conditions based on your selections.")
        ttk.Label(help_section, 
                 text=help_text,
                 wraplength=250, 
                 style='TLabel').pack(pady=5)

    def display_symptoms(self, search_term=""):
        # Clear current content
        for widget in self.symptom_frame.winfo_children():
            widget.destroy()

        search_term = search_term.lower()
        
        # Use notebook tabs for symptom categories
        notebook = ttk.Notebook(self.symptom_frame)
        notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configure notebook style
        self.style.configure('TNotebook', background=self.colors["bg_main"])
        self.style.configure('TNotebook.Tab', 
                            background=self.colors["bg_card"],
                            foreground=self.colors["text_dark"],
                            padding=(20, 10),
                            font=("Segoe UI", 11))
        self.style.map('TNotebook.Tab',
                      background=[('selected', self.colors["primary"])],
                      foreground=[('selected', self.colors["text_light"])])
        
        # Function to create tab content
        def create_tab_content(parent, category):
            # Create a frame with scrolling capability
            tab_frame = ttk.Frame(parent, style='Card.TFrame', padding=10)
            
            # Filter symptoms by search term
            filtered_symptoms = [s for s in self.symptoms_data[category] 
                              if not search_term or 
                              search_term in s.lower() or 
                              search_term in get_translation(self.language, s).lower()]
            
            if not filtered_symptoms:
                ttk.Label(tab_frame, 
                        text="No matching symptoms in this category",
                        style='TLabel').pack(pady=20)
                return tab_frame
                
            # Create a grid layout for symptoms (2 columns)
            row, col = 0, 0
            max_cols = 2
            
            for symptom in filtered_symptoms:
                var = self.symptom_vars[symptom]
                translated_symptom = get_translation(self.language, symptom)
                
                # Create a frame for each checkbox with a subtle border
                checkbox_frame = ttk.Frame(tab_frame, style='Card.TFrame', padding=5)
                checkbox_frame.grid(row=row, column=col, sticky="w", padx=5, pady=8)
                
                checkbox = ttk.Checkbutton(checkbox_frame, 
                                        text=translated_symptom, 
                                        variable=var,
                                        style='TCheckbutton')
                checkbox.pack(anchor="w")
                
                # Update grid position
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
                    
            # Configure grid weights
            for i in range(max_cols):
                tab_frame.columnconfigure(i, weight=1)
                
            return tab_frame
        
        # Create tabs for each category
        for category in self.symptoms_data.keys():
            # Create content frame for this category
            tab_content = create_tab_content(notebook, category)
            
            # Add tab with translated category name
            notebook.add(tab_content, text=get_translation(self.language, category))

    def filter_symptoms(self, event=None):
        search_term = self.search_var.get()
        self.display_symptoms(search_term)

    def diagnose(self):
        symptom_data = {symptom: var.get() for symptom, var in self.symptom_vars.items()}
        selected_symptoms_list = [symptom for symptom, selected in symptom_data.items() if selected]

        if not selected_symptoms_list:
            messagebox.showwarning(
                get_translation(self.language, "warning"), 
                get_translation(self.language, "no_symptoms_selected"),
                icon='warning'
            )
            return

        self.diagnosis_results = self.engine.run_diagnosis(symptom_data)

        if not self.diagnosis_results:
            messagebox.showinfo(
                get_translation(self.language, "result"), 
                get_translation(self.language, "no_disease_match"),
                icon='info'
            )
        else:
            self.show_diagnosis_results_dialog()

    def show_diagnosis_results_dialog(self):
        # Create a custom dialog for results with modern styling
        dialog = tk.Toplevel(self.root)
        dialog.title(get_translation(self.language, "diagnosis_result"))
        dialog.geometry("650x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Apply styling
        dialog.configure(bg=self.colors["bg_main"])
        dialog.option_add("*Font", ("Segoe UI", 12))
        
        # Create a nice header
        header_frame = ttk.Frame(dialog, style='TFrame', padding=10)
        header_frame.pack(fill="x", pady=10, padx=20)
        
        header = ttk.Label(header_frame, 
                         text=get_translation(self.language, "diagnosis_result_header"),
                         style='Header.TLabel')
        header.pack(anchor="w")
        
        # Results scroll container
        results_container = ttk.Frame(dialog, style='TFrame', padding=10)
        results_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Canvas for scrolling results
        canvas = tk.Canvas(results_container, 
                         bg=self.colors["bg_main"], 
                         highlightthickness=0,
                         bd=0)
        scrollbar = ttk.Scrollbar(results_container, 
                                orient="vertical", 
                                command=canvas.yview)
        
        results_frame = ttk.Frame(canvas, style='TFrame')
        
        # Configure the canvas
        canvas.create_window((0, 0), window=results_frame, anchor="nw", tags="results_frame")
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind the frame size changes and mousewheel
        results_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("results_frame", width=e.width - 5))
        
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Add results to the dialog with modern card design
        for i, (disease, confidence, advice) in enumerate(self.diagnosis_results):
            # Card container with margin
            margin_frame = ttk.Frame(results_frame, style='TFrame')
            margin_frame.pack(fill="x", pady=10)
            
            # Create a beautiful card
            card_style = f"Card{i}.TFrame"
            self.style.configure(card_style, 
                               background=self.colors["bg_card"], 
                               relief="flat")
                               
            card_frame = ttk.Frame(margin_frame, padding=15, style=card_style)
            card_frame.pack(fill="x")
            
            # Card header with disease name and confidence bar
            header_frame = ttk.Frame(card_frame, style=card_style)
            header_frame.pack(fill="x", pady=(0, 10))
            
            # Disease name
            trans_disease = get_translation(self.language, disease)
            disease_label = ttk.Label(header_frame, 
                                    text=trans_disease,
                                    font=("Segoe UI", 16, "bold"), 
                                    foreground=self.colors["primary"],
                                    background=self.colors["bg_card"])
            disease_label.pack(side=tk.LEFT)
            
            # Confidence percentage
            confidence_text = f"{confidence}%"
            confidence_label = ttk.Label(header_frame, 
                                       text=confidence_text,
                                       font=("Segoe UI", 14, "bold"),
                                       foreground=self.colors["secondary"],
                                       background=self.colors["bg_card"])
            confidence_label.pack(side=tk.RIGHT)
            
            # Confidence bar visualization
            bar_container = ttk.Frame(card_frame, height=8, style=card_style)
            bar_container.pack(fill="x", pady=(0, 15))
            
            # Draw confidence bar - colored based on confidence value
            bar_color = self.colors["success"] if confidence >= 70 else \
                      self.colors["warning"] if confidence >= 40 else \
                      self.colors["danger"]
                      
            bar_width = int((confidence / 100) * 580)  # Scale to width
            bar = tk.Canvas(bar_container, 
                          height=8, 
                          width=580, 
                          bg=self.colors["border"],
                          highlightthickness=0)
            bar.pack(fill="x")
            bar.create_rectangle(0, 0, bar_width, 8, fill=bar_color, outline="")
            
            # Separator
            separator = ttk.Separator(card_frame, orient="horizontal")
            separator.pack(fill="x", pady=10)
            
            # Advice section
            advice_frame = ttk.Frame(card_frame, style=card_style)
            advice_frame.pack(fill="x")
            
            # Advice header
            advice_header = ttk.Label(advice_frame, 
                                    text=get_translation(self.language, "advice_label") + ":",
                                    font=("Segoe UI", 14, "bold"),
                                    background=self.colors["bg_card"],
                                    foreground=self.colors["text_dark"])
            advice_header.pack(anchor="w")
            
            # Translated advice text
            trans_advice = get_translation(self.language, advice)
            advice_text = ttk.Label(advice_frame, 
                                  text=trans_advice, 
                                  wraplength=550,
                                  background=self.colors["bg_card"],
                                  foreground=self.colors["text_dark"])
            advice_text.pack(anchor="w", padx=(15, 0), pady=(5, 0))
        
        # Buttons frame at bottom
        button_frame = ttk.Frame(dialog, style='TFrame', padding=15)
        button_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Chart button
        chart_btn = ttk.Button(button_frame, 
                             text=get_translation(self.language, "chart"),
                             command=lambda: self.show_chart(from_dialog=True),
                             style="Primary.Rounded.TButton")
        chart_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Export button
        export_btn = ttk.Button(button_frame, 
                              text=get_translation(self.language, "export"),
                              command=self.export_to_pdf,
                              style="Accent1.Rounded.TButton")
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        close_btn = ttk.Button(button_frame, 
                             text=get_translation(self.language, "close"),
                             command=dialog.destroy,
                             style="Secondary.Rounded.TButton")
        close_btn.pack(side=tk.RIGHT)

    def show_chart(self, from_dialog=False):
        if not self.diagnosis_results:
            messagebox.showwarning(get_translation(self.language, "warning"), 
                                get_translation(self.language, "run_diagnosis_first"))
            return

        diseases = [get_translation(self.language, r[0]) for r in self.diagnosis_results]
        confidences = [r[1] for r in self.diagnosis_results]

        # Create a styled chart window
        chart_win = tk.Toplevel(self.root)
        chart_win.title(get_translation(self.language, "diagnosis_chart_title"))
        chart_win.configure(bg=self.colors["bg_main"])
        chart_win.geometry("800x550")
        
        # Modern color palette for chart
        chart_colors = ['#4361EE', '#3A0CA3', '#4CC9F0', '#F72585', '#7209B7', '#4D908E', '#06D6A0']
        
        # Create the figure with custom styling
        fig = plt.Figure(figsize=(8, 5), dpi=100, facecolor=self.colors["bg_main"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.colors["bg_main"])
        
        # Create horizontal bars with gradient colors
        bars = ax.barh(diseases, confidences, color=chart_colors[:len(diseases)], 
                      height=0.6, edgecolor='none', alpha=0.9)
        
        # Add confidence values as text
        for i, (bar, confidence) in enumerate(zip(bars, confidences)):
            ax.text(confidence + 1, bar.get_y() + bar.get_height()/2, 
                   f"{confidence}%", va='center', color=self.colors["text_dark"], 
                   fontweight='bold', fontsize=12)
        
        # Style the chart for modern look
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#DDDDDD')
        ax.spines['bottom'].set_color('#DDDDDD')
        
        ax.tick_params(axis='both', colors=self.colors["text_dark"], 
                     labelsize=12, grid_alpha=0.3)
        ax.set_xlabel(get_translation(self.language, "confidence_percent"), 
                    fontsize=14, color=self.colors["text_dark"])
        ax.set_title(get_translation(self.language, "diagnosis_confidence"), 
                   fontsize=18, fontweight='bold', color=self.colors["primary"])
        
        # Add grid lines for better readability
        ax.xaxis.grid(True, linestyle='--', alpha=0.2, color='#888888')
        
        # Display the chart in a nicely styled frame
        chart_container = ttk.Frame(chart_win, style='Card.TFrame', padding=20)
        chart_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        canvas_chart = FigureCanvasTkAgg(fig, master=chart_container)
        canvas_chart.draw()
        canvas_chart.get_tk_widget().pack(fill="both", expand=True)
        
        # Bottom button frame
        button_frame = ttk.Frame(chart_win, style='TFrame', padding=10)
        button_frame.pack(pady=(0, 20))
        
        # Close button with styled look
        close_btn = ttk.Button(button_frame, 
                             text=get_translation(self.language, "close"),
                             command=chart_win.destroy,
                             style="Secondary.Rounded.TButton",
                             padding=(20, 10))
        close_btn.pack()

    def export_to_pdf(self):
        if not REPORTLAB_AVAILABLE:
            messagebox.showerror(get_translation(self.language, "error"), get_translation(self.language, "reportlab_missing"))
            return

        if not self.diagnosis_results:
            messagebox.showwarning(get_translation(self.language, "warning"), get_translation(self.language, "no_results_to_export"))
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")],
            title=get_translation(self.language, "save_report_as")
        )
        if not filename:
            return

        try:
            c = canvas.Canvas(filename, pagesize=letter)
            c.setTitle(get_translation(self.language, "diagnosis_report"))
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, 750, get_translation(self.language, "diagnosis_report"))

            c.setFont("Helvetica", 12)
            textobject = c.beginText(100, 700)
            textobject.textLine(get_translation(self.language, "selected_symptoms_label"))
            selected_symptoms_list = [s for s, v in self.symptom_vars.items() if v.get()]
            translated_symptoms = [get_translation(self.language, s) for s in selected_symptoms_list]
            symptoms_text = ", ".join(translated_symptoms) if translated_symptoms else get_translation(self.language, "none")
            textobject.textLine(symptoms_text)
            textobject.moveCursor(0, 20)
            textobject.textLine(get_translation(self.language, "diagnosis_results_label"))

            for disease, confidence, advice in self.diagnosis_results:
                trans_disease = get_translation(self.language, disease)
                trans_advice = get_translation(self.language, advice)
                textobject.textLine(f"- {trans_disease} ({confidence}%)")
                textobject.textLine(f"  {get_translation(self.language, 'advice_label')}: {trans_advice}")
                textobject.moveCursor(0, 10)

            c.drawText(textobject)
            c.save()
            messagebox.showinfo(get_translation(self.language, "success"), f"{get_translation(self.language, 'report_exported_to')} {filename}")
        except Exception as e:
            messagebox.showerror(get_translation(self.language, "error"), f"{get_translation(self.language, 'pdf_export_error')}: {e}")

    def save_results(self):
        if not self.diagnosis_results:
            messagebox.showwarning(get_translation(self.language, "warning"), get_translation(self.language, "no_results_to_save"))
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title=get_translation(self.language, "save_results_as")
        )
        if not filename:
            return

        try:
            selected_symptoms_list = [symptom for symptom, var in self.symptom_vars.items() if var.get()]
            data = {
                "selected_symptoms": selected_symptoms_list,
                "results": self.diagnosis_results,
            }
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)
            messagebox.showinfo(get_translation(self.language, "success"), get_translation(self.language, "results_saved_success"))
        except Exception as e:
            messagebox.showerror(get_translation(self.language, "error"), f"{get_translation(self.language, "save_results_error")}: {e}")

    def clear_selections(self):
        for var in self.symptom_vars.values():
            var.set(False)
        self.diagnosis_results = []
        messagebox.showinfo(get_translation(self.language, "info"), get_translation(self.language, "selections_cleared"))

    def on_language_change(self, event):
        selected_item = self.lang_var.get()
        # Extract the language code from the format "Language Name (code)"
        lang_code = selected_item.split('(')[-1].strip(')')
        self.language = lang_code
        self.update_ui_text()
        # Redisplay symptoms with translated text
        self.display_symptoms(self.search_var.get())

    def update_ui_text(self):
        # Update window title and main title
        self.root.title(get_translation(self.language, "title"))
        self.title_label.config(text=get_translation(self.language, "title"))
        
        # Update button texts and other UI elements
        if hasattr(self, 'diagnose_button'):
            self.diagnose_button.config(text=get_translation(self.language, "diagnose"))
        if hasattr(self, 'chart_button'):
            self.chart_button.config(text=get_translation(self.language, "chart"))
        if hasattr(self, 'export_button'):
            self.export_button.config(text=get_translation(self.language, "export"))
        if hasattr(self, 'clear_button'):
            self.clear_button.config(text=get_translation(self.language, "clear"))
        if hasattr(self, 'save_button'):
            self.save_button.config(text=get_translation(self.language, "save"))
            
        # Refresh symptom display to update translations
        self.display_symptoms(self.search_var.get())


if __name__ == "__main__":
    root = tk.Tk()
    app = DiagnosisApp(root)
    # Set a larger size for better display
    root.geometry("1200x800")
    root.minsize(1000, 700)
    
    # Center window on screen
    root.eval('tk::PlaceWindow . center')
    
    # Start the app
    root.mainloop()
