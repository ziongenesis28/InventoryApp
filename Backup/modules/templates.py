# modules/templates.py
"""
Template System for Inventory Management App
Common patterns and reusable components
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import pandas as pd
from datetime import datetime, timedelta

class AppTemplates:
    """Collection of reusable GUI templates"""
    
    @staticmethod
    def create_section_title(parent, title, font_size=22):
        """Create a standard section title"""
        return ctk.CTkLabel(parent, text=title, 
                          font=("Arial", font_size, "bold"))
    
    @staticmethod
    def create_standard_button(parent, text, command, 
                             color="#3498db", hover_color="#2980b9",
                             width=150, height=40):
        """Create a standard button"""
        return ctk.CTkButton(parent, text=text, command=command,
                           fg_color=color, hover_color=hover_color,
                           width=width, height=height)
    
    @staticmethod
    def create_action_buttons(parent, save_command, clear_command, 
                            extra_buttons=None):
        """
        Create standard Save/Clear action buttons
        
        Args:
            parent: Parent frame
            save_command: Function to call on save
            clear_command: Function to call on clear
            extra_buttons: List of (text, command, color) tuples
        """
        button_frame = ctk.CTkFrame(parent)
        button_frame.pack(pady=20)
        
        # Save button (green)
        ctk.CTkButton(button_frame, text="💾 Save",
                     command=save_command,
                     fg_color="#27ae60", hover_color="#219653",
                     width=150, height=40).pack(side="left", padx=10)
        
        # Clear button (gray)
        ctk.CTkButton(button_frame, text="🗑️ Clear",
                     command=clear_command,
                     fg_color="#95a5a6", hover_color="#7f8c8d",
                     width=150, height=40).pack(side="left", padx=10)
        
        # Extra buttons if provided
        if extra_buttons:
            for text, command, color in extra_buttons:
                ctk.CTkButton(button_frame, text=text,
                            command=command, fg_color=color,
                            width=150, height=40).pack(side="left", padx=10)
        
        return button_frame
    
    @staticmethod
    def create_form_field(parent, label_text, field_type, field_name, 
                         width=250, default_value="", options=None,
                         required=False, row_pady=8):
        """
        Create a standardized form field
        
        Returns:
            Tuple: (frame, widget, label)
        """
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill="x", pady=row_pady)
        
        # Label with asterisk for required fields
        label_text_display = label_text
        if required:
            label_text_display = f"{label_text}*"
        
        label = ctk.CTkLabel(row_frame, text=label_text_display, 
                           width=150, anchor="w")
        label.pack(side="left", padx=10)
        
        widget = None
        
        if field_type == "text":
            widget = ctk.CTkEntry(row_frame, width=width)
            if default_value:
                widget.insert(0, str(default_value))
            widget.pack(side="left", padx=10)
            
        elif field_type == "dropdown":
            options = options or ["Select Option"]
            var = tk.StringVar(value=options[0])
            widget = ctk.CTkOptionMenu(row_frame, values=options,
                                      variable=var, width=width)
            widget.pack(side="left", padx=10)
            widget = var  # Return the StringVar for value access
            
        elif field_type == "number":
            widget = ctk.CTkEntry(row_frame, width=width)
            widget.insert(0, str(default_value) if default_value else "0.00")
            widget.pack(side="left", padx=10)
            
        elif field_type == "date":
            var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
            widget = ctk.CTkEntry(row_frame, textvariable=var, width=width-40)
            widget.pack(side="left", padx=10)
            
            # Calendar button
            calendar_btn = ctk.CTkButton(row_frame, text="📅", width=30, height=30,
                                       fg_color="#3498db", hover_color="#2980b9")
            calendar_btn.pack(side="left", padx=5)
            widget = var  # Return the StringVar
            
        elif field_type == "textarea":
            widget = ctk.CTkTextbox(row_frame, width=width, height=80)
            if default_value:
                widget.insert("1.0", str(default_value))
            widget.pack(side="left", padx=10)
            
        elif field_type == "checkbox":
            var = tk.StringVar(value="Yes" if default_value else "No")
            widget = ctk.CTkSwitch(row_frame, text="", 
                                  variable=var, onvalue="Yes", offvalue="No")
            widget.pack(side="left", padx=10)
            widget = var  # Return the StringVar
            
        return row_frame, widget, label
    
    @staticmethod
    def create_filter_panel(parent, filters_config):
        """
        Create a filter panel with multiple filter options
        
        Args:
            filters_config: List of dicts with filter definitions
                Example: [
                    {"type": "search", "label": "Search:", "width": 300},
                    {"type": "dropdown", "label": "Category:", "options": [...], "width": 200},
                    {"type": "date_range", "label": "Date Range:", "width": 120}
                ]
        """
        filter_frame = ctk.CTkFrame(parent)
        filter_frame.pack(pady=10, padx=20, fill="x")
        
        filter_widgets = {}
        
        for i, config in enumerate(filters_config):
            row_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(row_frame, text=config["label"], 
                        font=("Arial", 12)).pack(side="left", padx=10)
            
            if config["type"] == "search":
                var = tk.StringVar()
                entry = ctk.CTkEntry(row_frame, 
                                    textvariable=var,
                                    placeholder_text=config.get("placeholder", ""),
                                    width=config.get("width", 300))
                entry.pack(side="left", padx=10)
                filter_widgets[config["label"]] = var
                
            elif config["type"] == "dropdown":
                var = tk.StringVar(value=config.get("default", "All"))
                menu = ctk.CTkOptionMenu(row_frame,
                                       values=config["options"],
                                       variable=var,
                                       width=config.get("width", 200))
                menu.pack(side="left", padx=10)
                filter_widgets[config["label"]] = var
                
            elif config["type"] == "date_range":
                # From date
                ctk.CTkLabel(row_frame, text="From:", width=50).pack(side="left", padx=5)
                from_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
                from_entry = ctk.CTkEntry(row_frame, textvariable=from_var, 
                                         width=config.get("width", 120))
                from_entry.pack(side="left", padx=5)
                
                ctk.CTkLabel(row_frame, text="To:", width=50).pack(side="left", padx=5)
                to_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
                to_entry = ctk.CTkEntry(row_frame, textvariable=to_var, 
                                       width=config.get("width", 120))
                to_entry.pack(side="left", padx=5)
                
                filter_widgets[f"{config['label']}_from"] = from_var
                filter_widgets[f"{config['label']}_to"] = to_var
        
        return filter_frame, filter_widgets
    
    @staticmethod
    def create_data_table(parent, headers, column_widths, data, height=400):
        """
        Create a scrollable data table
        
        Args:
            headers: List of column headers
            column_widths: List of column widths
            data: List of dictionaries or pandas DataFrame
            height: Table height
        """
        scroll_frame = ctk.CTkScrollableFrame(parent, height=height)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Table headers
        for col, (header, width) in enumerate(zip(headers, column_widths)):
            ctk.CTkLabel(scroll_frame, text=header, 
                        font=("Arial", 12, "bold"),
                        width=width).grid(row=0, column=col, padx=5, pady=5, sticky="w")
        
        # If data is pandas DataFrame, convert to list of dicts
        if isinstance(data, pd.DataFrame):
            data = data.to_dict('records')
        
        # Add data rows
        for row_idx, row_data in enumerate(data, start=1):
            for col_idx, header in enumerate(headers):
                value = row_data.get(header, "")
                ctk.CTkLabel(scroll_frame, text=str(value)[:50], 
                            width=column_widths[col_idx]).grid(
                            row=row_idx, column=col_idx, padx=5, pady=2, sticky="w")
        
        return scroll_frame
    
    @staticmethod
    def create_status_label(parent, initial_text="", font_size=12):
        """Create a status label for form feedback"""
        return ctk.CTkLabel(parent, text=initial_text, font=("Arial", font_size))
    
    @staticmethod
    def create_tab_section(parent, tab_names, tab_contents):
        """
        Create a tabbed section
        
        Args:
            tab_names: List of tab names
            tab_contents: List of functions that create tab content
        """
        tabview = ctk.CTkTabview(parent)
        tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        tabs = {}
        for name, content_func in zip(tab_names, tab_contents):
            tabview.add(name)
            tabs[name] = tabview.tab(name)
            content_func(tabs[name])
        
        return tabview, tabs
    
    @staticmethod
    def validate_form_fields(fields_dict):
        """
        Validate form fields
        
        Args:
            fields_dict: Dictionary of {field_name: (widget, is_required)}
            
        Returns:
            Tuple: (is_valid, error_message, field_values)
        """
        field_values = {}
        errors = []
        
        for field_name, (widget, is_required) in fields_dict.items():
            value = None
            
            # Get value based on widget type
            if isinstance(widget, ctk.CTkEntry):
                value = widget.get().strip()
            elif isinstance(widget, tk.StringVar):
                value = widget.get().strip()
            elif isinstance(widget, ctk.CTkTextbox):
                value = widget.get("1.0", "end-1c").strip()
            else:
                value = str(widget)
            
            field_values[field_name] = value
            
            # Validate required fields
            if is_required and (not value or value in ["Select Type", "Select Category", "Select Method"]):
                errors.append(f"{field_name} is required")
        
        if errors:
            return False, " • ".join(errors), field_values
        
        return True, "", field_values


class DatabaseTemplates:
    """Templates for database operations"""
    
    @staticmethod
    def generate_id(prefix, existing_ids, digits=4):
        """Generate a sequential ID"""
        numbers = []
        for existing_id in existing_ids:
            if isinstance(existing_id, str) and existing_id.startswith(prefix):
                try:
                    num = int(existing_id[len(prefix):])
                    numbers.append(num)
                except:
                    pass
        
        if numbers:
            next_num = max(numbers) + 1
        else:
            next_num = 1
        
        return f"{prefix}{next_num:0{digits}d}"
    
    @staticmethod
    def filter_by_date(df, date_column, period, custom_from=None, custom_to=None):
        """Filter dataframe by time period"""
        if date_column not in df.columns:
            return df
        
        try:
            df[date_column] = pd.to_datetime(df[date_column])
            
            if period == "All Time":
                return df
            elif period == "Today":
                today = datetime.now().strftime("%Y-%m-%d")
                return df[df[date_column].dt.strftime("%Y-%m-%d") == today]
            elif period == "Yesterday":
                yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                return df[df[date_column].dt.strftime("%Y-%m-%d") == yesterday]
            elif period == "Last 7 days":
                cutoff = datetime.now() - timedelta(days=7)
                return df[df[date_column] >= cutoff]
            elif period == "Last 30 days":
                cutoff = datetime.now() - timedelta(days=30)
                return df[df[date_column] >= cutoff]
            elif period == "This Month":
                now = datetime.now()
                start_of_month = datetime(now.year, now.month, 1)
                return df[df[date_column] >= start_of_month]
            elif period == "Last Month":
                now = datetime.now()
                if now.month == 1:
                    start_last = datetime(now.year - 1, 12, 1)
                    end_last = datetime(now.year, 1, 1)
                else:
                    start_last = datetime(now.year, now.month - 1, 1)
                    end_last = datetime(now.year, now.month, 1)
                return df[(df[date_column] >= start_last) & (df[date_column] < end_last)]
            elif period == "Custom" and custom_from and custom_to:
                from_date = pd.to_datetime(custom_from)
                to_date = pd.to_datetime(custom_to)
                return df[(df[date_column] >= from_date) & (df[date_column] <= to_date)]
            else:
                return df
                
        except Exception as e:
            print(f"Error filtering by date: {e}")
            return df


class CodeGenerator:
    """Generate code snippets from templates"""
    
    @staticmethod
    def generate_form_method(class_name, form_name, fields):
        """Generate a form creation method"""
        code = f'''
    def {form_name}(self, parent_frame):
        """Create {form_name} form"""
        from modules.templates import AppTemplates
        
        # Title
        AppTemplates.create_section_title(parent_frame, "{form_name}").pack(pady=10)
        
        # Form frame
        form_frame = ctk.CTkFrame(parent_frame)
        form_frame.pack(pady=20, padx=50, fill="x")
        
        # Form fields
        self.{form_name}_entries = {{}}
        
        fields = {fields}
        
        for label_text, field_name, field_type, required in fields:
            _, widget, _ = AppTemplates.create_form_field(
                form_frame, label_text, field_type, field_name,
                required=required
            )
            self.{form_name}_entries[field_name] = widget
        
        # Action buttons
        AppTemplates.create_action_buttons(
            parent_frame,
            save_command=self.save_{form_name.replace(' ', '_').lower()},
            clear_command=self.clear_{form_name.replace(' ', '_').lower()}
        )
        
        # Status label
        self.{form_name}_status = AppTemplates.create_status_label(parent_frame)
        self.{form_name}_status.pack(pady=10)
        
        return form_frame
'''
        return code