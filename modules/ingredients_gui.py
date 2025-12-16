# ingredients_gui.py - All ingredient-related GUI code
import customtkinter as ctk
import pandas as pd
import tkinter as tk
from tkinter import messagebox, simpledialog


class IngredientsGUI:
    def __init__(self, window, db, config):
        self.window = window
        self.db = db
        self.config = config
        self.main_content = None
        self.sort_directions = {}  # Track sort direction for each column
        self.current_sort_column = None

    def clear_main_content(self):
        """Clear the main content area"""
        if self.main_content:
            for widget in self.main_content.winfo_children():
                widget.destroy()

    def show_ingredients_management(self, main_content_frame):
        """Show ingredients management interface"""
        self.main_content = main_content_frame
        self.clear_main_content()

        # Create tabview for ingredients
        ingredients_tabs = ctk.CTkTabview(self.main_content)
        ingredients_tabs.pack(fill="both", expand=True, padx=20, pady=20)

        # Add tabs
        ingredients_tabs.add("View Ingredients")
        ingredients_tabs.add("Add Ingredient")

        # Fill each tab
        self.show_all_ingredients(ingredients_tabs.tab("View Ingredients"))
        self.create_ingredient_form(ingredients_tabs.tab("Add Ingredient"))

    def show_all_ingredients(self, parent_frame):
        """Show all ingredients in a table with enhanced filtering"""
        ctk.CTkLabel(parent_frame, text="Ingredients Management",
                     font=("Arial", 22, "bold")).pack(pady=10)

        # ===== ENHANCED FILTER & SORT FRAME =====
        filter_frame = ctk.CTkFrame(parent_frame)
        filter_frame.pack(pady=10, padx=10, fill="x")

        # Row 1: Search and Quick Actions
        top_row = ctk.CTkFrame(filter_frame, fg_color="transparent")
        top_row.pack(fill="x", pady=10, padx=15)

        # Search
        search_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        search_frame.pack(side="left", padx=5)

        ctk.CTkLabel(search_frame, text="🔍 Search:",
                     font=("Arial", 12)).pack(side="left", padx=5)

        self.ingredient_search_var = tk.StringVar()
        self.ingredient_search_var.trace("w", lambda *args: self.refresh_ingredients_table())
        search_entry = ctk.CTkEntry(search_frame,
                                   textvariable=self.ingredient_search_var,
                                   placeholder_text="Search ingredients...",
                                   width=250)
        search_entry.pack(side="left", padx=5)

        # Status filter
        status_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        status_frame.pack(side="left", padx=20)

        ctk.CTkLabel(status_frame, text="Status:",
                     font=("Arial", 12)).pack(side="left", padx=5)

        self.status_filter_var = tk.StringVar(value="All")
        self.status_filter_var.trace("w", lambda *args: self.refresh_ingredients_table())
        status_menu = ctk.CTkOptionMenu(status_frame,
                                       values=["All", "Active", "Inactive"],
                                       variable=self.status_filter_var,
                                       width=100)
        status_menu.pack(side="left", padx=5)

        # Category filter
        category_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        category_frame.pack(side="left", padx=20)

        ctk.CTkLabel(category_frame, text="Category:",
                     font=("Arial", 12)).pack(side="left", padx=5)

        self.category_filter_var = tk.StringVar(value="All Categories")
        self.category_filter_var.trace("w", lambda *args: self.refresh_ingredients_table())
        category_menu = ctk.CTkOptionMenu(category_frame,
                                         values=["All Categories"],
                                         variable=self.category_filter_var,
                                         width=150)
        category_menu.pack(side="left", padx=5)

        # Unit filter
        unit_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        unit_frame.pack(side="left", padx=20)

        ctk.CTkLabel(unit_frame, text="Unit:",
                     font=("Arial", 12)).pack(side="left", padx=5)

        self.unit_filter_var = tk.StringVar(value="All Units")
        self.unit_filter_var.trace("w", lambda *args: self.refresh_ingredients_table())
        unit_menu = ctk.CTkOptionMenu(unit_frame,
                                     values=["All Units"],
                                     variable=self.unit_filter_var,
                                     width=100)
        unit_menu.pack(side="left", padx=5)

        # Row 2: Action buttons
        action_row = ctk.CTkFrame(filter_frame, fg_color="transparent")
        action_row.pack(fill="x", pady=(0, 10), padx=15)

        # Quick action buttons
        ctk.CTkButton(action_row, text="🔄 Refresh",
                     command=self.refresh_ingredients_table,
                     width=100, height=30).pack(side="left", padx=5)

        ctk.CTkButton(action_row, text="🗑️ Clear Filters",
                     command=self.clear_ingredient_filters,
                     fg_color="#95a5a6", hover_color="#7f8c8d",
                     width=120, height=30).pack(side="left", padx=5)

        ctk.CTkButton(action_row, text="📊 Low Stock (<10)",
                     command=lambda: self.filter_low_stock(10),
                     fg_color="#e74c3c", hover_color="#c0392b",
                     width=130, height=30).pack(side="left", padx=5)

        ctk.CTkButton(action_row, text="📦 Out of Stock",
                     command=lambda: self.filter_low_stock(0),
                     fg_color="#d63031", hover_color="#b33939",
                     width=120, height=30).pack(side="left", padx=5)

        # Create frame for table
        self.ingredients_table_frame = ctk.CTkFrame(parent_frame)
        self.ingredients_table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Initial load
        self.refresh_ingredients_table()

    def update_filter_dropdowns(self):
        """Update category and unit filter dropdowns with current data"""
        # Get current data
        ingredients_df = self.db.read_tab('Ingredients')
        
        # Update categories
        if hasattr(self, 'category_menu'):
            categories = ["All Categories"]
            if not ingredients_df.empty and 'Category' in ingredients_df.columns:
                unique_cats = ingredients_df['Category'].dropna().unique()
                for cat in unique_cats:
                    if cat and str(cat).strip() and str(cat).strip().lower() != 'nan':
                        categories.append(str(cat).strip())
            
            categories = sorted(list(set(categories)))
            current_value = self.category_filter_var.get()
            
            # Update the dropdown
            self.category_menu.configure(values=categories)
            
            # Reset value if current value no longer exists
            if current_value not in categories:
                self.category_filter_var.set("All Categories")
        
        # Update units
        if hasattr(self, 'unit_menu'):
            units = ["All Units"]
            if not ingredients_df.empty and 'Unit' in ingredients_df.columns:
                unique_units = ingredients_df['Unit'].dropna().unique()
                for unit in unique_units:
                    if unit and str(unit).strip() and str(unit).strip().lower() != 'nan':
                        units.append(str(unit).strip())
            
            units = sorted(list(set(units)))
            current_unit = self.unit_filter_var.get()
            
            # Update the dropdown
            self.unit_menu.configure(values=units)
            
            # Reset value if current value no longer exists
            if current_unit not in units:
                self.unit_filter_var.set("All Units")

    def clear_ingredient_filters(self):
        """Clear all ingredient filters"""
        self.ingredient_search_var.set("")
        self.status_filter_var.set("All")
        self.category_filter_var.set("All Categories")
        self.unit_filter_var.set("All Units")
        self.sort_directions = {}
        self.current_sort_column = None
        self.refresh_ingredients_table()

    def filter_low_stock(self, threshold):
        """Filter ingredients with low stock"""
        self.ingredient_search_var.set("")
        self.status_filter_var.set("All")
        self.category_filter_var.set("All Categories")
        self.unit_filter_var.set("All Units")
        self.refresh_ingredients_table(threshold)

    def refresh_ingredients_table(self, low_stock_threshold=None):
        """Refresh the ingredients table with filters"""
        if not hasattr(self, 'ingredients_table_frame'):
            return
            
        # Update filter dropdowns first
        self.update_filter_dropdowns()
        
        # Clear existing table
        for widget in self.ingredients_table_frame.winfo_children():
            widget.destroy()
        

        # Get all ingredients
        all_ingredients_df = self.db.read_tab('Ingredients')

        if all_ingredients_df.empty:
            ctk.CTkLabel(self.ingredients_table_frame,
                        text="No ingredients found in database.",
                        font=("Arial", 14)).pack(pady=50)
            return

        # Make a copy for filtering
        ingredients_df = all_ingredients_df.copy()

        # Apply filters
        search_text = self.ingredient_search_var.get().lower() if hasattr(self, 'ingredient_search_var') else ""
        if search_text:
            mask = (ingredients_df['Ingredient_Name'].str.lower().str.contains(search_text) |
                   ingredients_df['Ingredient_ID'].str.lower().str.contains(search_text) |
                   ingredients_df['Description'].astype(str).str.lower().str.contains(search_text))
            ingredients_df = ingredients_df[mask]

        # Status filter
        status_filter = self.status_filter_var.get() if hasattr(self, 'status_filter_var') else "All"
        if status_filter == "Active":
            if 'Active' in ingredients_df.columns:
                ingredients_df['Active'] = ingredients_df['Active'].astype(str).str.upper()
                ingredients_df = ingredients_df[ingredients_df['Active'].str.contains('YES|TRUE|1', na=False)]
        elif status_filter == "Inactive":
            if 'Active' in ingredients_df.columns:
                ingredients_df['Active'] = ingredients_df['Active'].astype(str).str.upper()
                ingredients_df = ingredients_df[~ingredients_df['Active'].str.contains('YES|TRUE|1', na=False)]

        # Category filter
        category_filter = self.category_filter_var.get() if hasattr(self, 'category_filter_var') else "All Categories"
        if category_filter != "All Categories" and 'Category' in ingredients_df.columns:
            ingredients_df['Category'] = ingredients_df['Category'].fillna('Uncategorized')
            ingredients_df = ingredients_df[ingredients_df['Category'] == category_filter]

        # Unit filter
        unit_filter = self.unit_filter_var.get() if hasattr(self, 'unit_filter_var') else "All Units"
        if unit_filter != "All Units" and 'Unit' in ingredients_df.columns:
            ingredients_df['Unit'] = ingredients_df['Unit'].fillna('')
            ingredients_df = ingredients_df[ingredients_df['Unit'] == unit_filter]

        # Low stock filter
        if low_stock_threshold is not None and 'Current_Stock' in ingredients_df.columns:
            try:
                ingredients_df['Current_Stock'] = pd.to_numeric(ingredients_df['Current_Stock'], errors='coerce')
                if low_stock_threshold == 0:
                    ingredients_df = ingredients_df[ingredients_df['Current_Stock'] <= 0]
                else:
                    ingredients_df = ingredients_df[ingredients_df['Current_Stock'] < low_stock_threshold]
            except:
                pass

        # Apply sorting
        if self.current_sort_column:
            column = self.current_sort_column
            ascending = self.sort_directions.get(column, True)
            
            if column in ingredients_df.columns:
                # Handle special columns
                if column == 'Current_Stock':
                    ingredients_df[column] = pd.to_numeric(ingredients_df[column], errors='coerce')
                elif column == 'Cost_Per_Unit':
                    ingredients_df[column] = pd.to_numeric(ingredients_df[column], errors='coerce')
                
                ingredients_df = ingredients_df.sort_values(by=column, ascending=ascending)

        if ingredients_df.empty:
            filter_info = []
            if search_text:
                filter_info.append(f"Search: '{search_text}'")
            if status_filter != "All":
                filter_info.append(f"Status: '{status_filter}'")
            if category_filter != "All Categories":
                filter_info.append(f"Category: '{category_filter}'")
            if unit_filter != "All Units":
                filter_info.append(f"Unit: '{unit_filter}'")
            if low_stock_threshold is not None:
                filter_info.append(f"Low Stock: <{low_stock_threshold}")

            no_results_text = "No ingredients found"
            if filter_info:
                no_results_text += f" with filters: {' • '.join(filter_info)}"
            no_results_text += "."

            ctk.CTkLabel(self.ingredients_table_frame,
                        text=no_results_text,
                        font=("Arial", 14)).pack(pady=50)
            return

        # Display filter summary
        filter_summary_frame = ctk.CTkFrame(self.ingredients_table_frame,
                                          fg_color="#ecf0f1",  # Light gray background
                                          corner_radius=8)
        filter_summary_frame.pack(fill="x", padx=10, pady=10)

        summary_parts = [f"📦 {len(ingredients_df)} ingredients"]

        if search_text:
            summary_parts.append(f"Search: '{search_text}'")
        if status_filter != "All":
            summary_parts.append(f"Status: {status_filter}")
        if category_filter != "All Categories":
            summary_parts.append(f"Category: {category_filter}")
        if unit_filter != "All Units":
            summary_parts.append(f"Unit: {unit_filter}")
        if low_stock_threshold is not None:
            summary_parts.append(f"Stock < {low_stock_threshold}")
        if self.current_sort_column:
            direction = "↑" if self.sort_directions.get(self.current_sort_column, True) else "↓"
            summary_parts.append(f"Sorted: {self.current_sort_column.replace('_', ' ')} {direction}")

        summary_text = " • ".join(summary_parts)

        ctk.CTkLabel(filter_summary_frame, text=summary_text,
                    font=("Arial", 12),
                    text_color="black").pack(pady=8, padx=10)

        # Create table with scrollable frame
        table_container = ctk.CTkFrame(self.ingredients_table_frame)
        table_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Create scrollable frame for the table
        scroll_frame = ctk.CTkScrollableFrame(table_container, width=1100, height=500)
        scroll_frame.pack(fill="both", expand=True)

        # Configure grid for the scrollable frame
        scroll_frame.grid_columnconfigure(0, weight=0, minsize=80)    # ID
        scroll_frame.grid_columnconfigure(1, weight=0, minsize=180)   # Name
        scroll_frame.grid_columnconfigure(2, weight=0, minsize=120)   # Category
        scroll_frame.grid_columnconfigure(3, weight=0, minsize=80)    # Unit
        scroll_frame.grid_columnconfigure(4, weight=0, minsize=100)   # Stock
        scroll_frame.grid_columnconfigure(5, weight=0, minsize=100)   # Cost
        scroll_frame.grid_columnconfigure(6, weight=0, minsize=80)    # Status
        scroll_frame.grid_columnconfigure(7, weight=0, minsize=120)   # Last Updated
        scroll_frame.grid_columnconfigure(8, weight=0, minsize=150)   # Actions

        # Table headers with sort buttons
        headers = [
            ("ID", "Ingredient_ID"),
            ("Ingredient Name", "Ingredient_Name"),
            ("Category", "Category"),
            ("Unit", "Unit"),
            ("Current Stock", "Current_Stock"),
            ("Cost/Unit", "Cost_Per_Unit"),
            ("Status", "Active"),
            ("Last Updated", "Last_Updated"),
            ("Actions", "")
        ]

        # Create header row
        for col, (header_text, column_name) in enumerate(headers):
            header_cell = ctk.CTkFrame(scroll_frame, height=35, corner_radius=5,
                                      fg_color="#2c3e50" if col % 2 == 0 else "#34495e")
            header_cell.grid(row=0, column=col, padx=1, pady=1, sticky="nsew")
            
            if column_name:  # Clickable header for sortable columns
                # Add sort indicator
                sort_indicator = ""
                if self.current_sort_column == column_name:
                    sort_indicator = " ↑" if self.sort_directions.get(column_name, True) else " ↓"
                
                header_btn = ctk.CTkButton(
                    header_cell,
                    text=f"{header_text}{sort_indicator}",
                    font=("Arial", 12, "bold"),
                    fg_color="transparent",
                    hover_color="#4a6fa5",
                    text_color="white",
                    height=35,
                    anchor="center",
                    command=lambda col_name=column_name: self.sort_by_column(col_name)
                )
                header_btn.pack(fill="both", expand=True)
            else:
                # Non-sortable header (Actions)
                ctk.CTkLabel(header_cell, text=header_text,
                           font=("Arial", 12, "bold"),
                           text_color="white").pack(expand=True)

        # Add ingredient rows
        for row_idx, (_, ingredient) in enumerate(ingredients_df.iterrows(), start=1):
            # Alternate row colors for readability
            row_color = "#f8f9fa" if row_idx % 2 == 0 else "white"
            
            # ID
            id_cell = ctk.CTkFrame(scroll_frame, height=35, fg_color=row_color)
            id_cell.grid(row=row_idx, column=0, padx=1, pady=1, sticky="nsew")
            ctk.CTkLabel(id_cell, text=ingredient['Ingredient_ID'],
                        font=("Arial", 11), text_color="black").pack(expand=True)
            
            # Name
            name_cell = ctk.CTkFrame(scroll_frame, height=35, fg_color=row_color)
            name_cell.grid(row=row_idx, column=1, padx=1, pady=1, sticky="nsew")
            ctk.CTkLabel(name_cell, text=ingredient['Ingredient_Name'],
                        font=("Arial", 11), text_color="black").pack(expand=True)
            
            # Category
            category_cell = ctk.CTkFrame(scroll_frame, height=35, fg_color=row_color)
            category_cell.grid(row=row_idx, column=2, padx=1, pady=1, sticky="nsew")
            category = ingredient.get('Category', 'N/A')
            ctk.CTkLabel(category_cell, text=category,
                        font=("Arial", 11), text_color="black").pack(expand=True)
            
            # Unit
            unit_cell = ctk.CTkFrame(scroll_frame, height=35, fg_color=row_color)
            unit_cell.grid(row=row_idx, column=3, padx=1, pady=1, sticky="nsew")
            unit = ingredient.get('Unit', 'N/A')
            ctk.CTkLabel(unit_cell, text=unit,
                        font=("Arial", 11), text_color="black").pack(expand=True)
            
            # Current Stock
            stock_cell = ctk.CTkFrame(scroll_frame, height=35, fg_color=row_color)
            stock_cell.grid(row=row_idx, column=4, padx=1, pady=1, sticky="nsew")
            stock = ingredient.get('Current_Stock', 0)
            try:
                stock_num = float(stock)
                stock_color = "green" if stock_num > 20 else "orange" if stock_num > 0 else "red"
                stock_text = f"{stock_num:.2f}" if stock_num % 1 else f"{int(stock_num)}"
            except:
                stock_color = "gray"
                stock_text = str(stock)
            
            ctk.CTkLabel(stock_cell, text=stock_text,
                        font=("Arial", 11, "bold"),
                        text_color=stock_color).pack(expand=True)
            
            # Cost per Unit
            cost_cell = ctk.CTkFrame(scroll_frame, height=35, fg_color=row_color)
            cost_cell.grid(row=row_idx, column=5, padx=1, pady=1, sticky="nsew")
            cost = ingredient.get('Cost_Per_Unit', 0)
            try:
                cost_num = float(cost)
                cost_text = f"{self.config['currency']}{cost_num:.2f}"
            except:
                cost_text = f"{self.config['currency']}0.00"
            
            ctk.CTkLabel(cost_cell, text=cost_text,
                        font=("Arial", 11), text_color="black").pack(expand=True)
            
            # Status
            status_cell = ctk.CTkFrame(scroll_frame, height=35, fg_color=row_color)
            status_cell.grid(row=row_idx, column=6, padx=1, pady=1, sticky="nsew")
            
            is_active = str(ingredient.get('Active', 'Yes')).upper() == 'YES'
            status_text = "Active" if is_active else "Inactive"
            status_bg_color = "#2ecc71" if is_active else "#e74c3c"
            
            status_frame = ctk.CTkFrame(status_cell, fg_color=status_bg_color,
                                       corner_radius=10, height=25)
            status_frame.place(relx=0.5, rely=0.5, anchor="center")
            ctk.CTkLabel(status_frame, text=status_text,
                        text_color="white", font=("Arial", 10, "bold")).pack(padx=10, pady=2)
            
            # Last Updated
            updated_cell = ctk.CTkFrame(scroll_frame, height=35, fg_color=row_color)
            updated_cell.grid(row=row_idx, column=7, padx=1, pady=1, sticky="nsew")
            last_updated = ingredient.get('Last_Updated', '')
            updated_text = str(last_updated)[:10] if last_updated else 'N/A'
            ctk.CTkLabel(updated_cell, text=updated_text,
                        font=("Arial", 11), text_color="black").pack(expand=True)
            
            # Actions
            action_cell = ctk.CTkFrame(scroll_frame, height=35, fg_color=row_color)
            action_cell.grid(row=row_idx, column=8, padx=1, pady=1, sticky="nsew")
            
            # Create action buttons frame
            action_buttons_frame = ctk.CTkFrame(action_cell, fg_color="transparent")
            action_buttons_frame.place(relx=0.5, rely=0.5, anchor="center")
            
            # View button
            view_btn = ctk.CTkButton(
                action_buttons_frame,
                text="👁️",
                width=35,
                height=25,
                font=("Arial", 12),
                fg_color="#3498db",
                hover_color="#2980b9",
                command=lambda iid=ingredient['Ingredient_ID']: self.view_ingredient_details(iid)
            )
            view_btn.pack(side="left", padx=2)
            
            # Edit button
            edit_btn = ctk.CTkButton(
                action_buttons_frame,
                text="✏️",
                width=35,
                height=25,
                font=("Arial", 12),
                fg_color="#f39c12",
                hover_color="#e67e22",
                command=lambda iid=ingredient['Ingredient_ID']: self.edit_ingredient_popup(iid)
            )
            edit_btn.pack(side="left", padx=2)
            
            # Stock Update button
            stock_btn = ctk.CTkButton(
                action_buttons_frame,
                text="📦",
                width=35,
                height=25,
                font=("Arial", 12),
                fg_color="#2ecc71",
                hover_color="#27ae60",
                command=lambda iid=ingredient['Ingredient_ID']: self.update_stock_popup(iid)
            )
            stock_btn.pack(side="left", padx=2)
            
            # Delete button (only for inactive items)
            if not is_active:
                delete_btn = ctk.CTkButton(
                    action_buttons_frame,
                    text="🗑️",
                    width=35,
                    height=25,
                    font=("Arial", 12),
                    fg_color="#e74c3c",
                    hover_color="#c0392b",
                    command=lambda iid=ingredient['Ingredient_ID']: self.delete_ingredient_popup(iid)
                )
                delete_btn.pack(side="left", padx=2)

    def sort_by_column(self, column_name):
        """Sort table by column"""
        if self.current_sort_column == column_name:
            # Toggle direction
            self.sort_directions[column_name] = not self.sort_directions.get(column_name, True)
        else:
            # New column, default to ascending
            self.current_sort_column = column_name
            self.sort_directions[column_name] = True
        
        self.refresh_ingredients_table()

    def create_ingredient_form(self, parent_frame):
        """Form to add new ingredient"""
        ctk.CTkLabel(parent_frame, text="Add New Ingredient",
                    font=("Arial", 22, "bold")).pack(pady=10)

        # Form frame
        form_frame = ctk.CTkFrame(parent_frame)
        form_frame.pack(pady=20, padx=50, fill="both", expand=True)

        # Auto-generate ID
        new_id = self.db.generate_ingredient_id()
        ctk.CTkLabel(form_frame, text=f"Ingredient ID: {new_id}",
                    font=("Arial", 14, "bold")).pack(pady=5)

        # Store the generated ID
        self.generated_ingredient_id = new_id

        # Form fields in a grid layout
        fields_grid = [
            ("Ingredient Name*:", "ingredient_name", "text", 0, 0),
            ("Category:", "category", "dropdown", 0, 1),
            ("Unit*:", "unit", "dropdown", 1, 0),
            ("Initial Stock:", "initial_stock", "number", 1, 1),
            ("Cost per Unit*:", "cost_per_unit", "number", 2, 0),
            ("Min Stock Level:", "min_stock", "number", 2, 1),
            ("Supplier:", "supplier", "text", 3, 0),
            ("Active (Yes/No):", "active", "dropdown", 3, 1)
        ]

        self.ingredient_form_entries = {}

        # Create a grid container for the form fields
        grid_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        grid_container.pack(fill="both", expand=True, pady=10)
        
        # Configure grid
        grid_container.grid_columnconfigure(0, weight=1)
        grid_container.grid_columnconfigure(1, weight=1)

        for label_text, field_name, field_type, row, col in fields_grid:
            field_frame = ctk.CTkFrame(grid_container, fg_color="transparent")
            field_frame.grid(row=row, column=col, padx=10, pady=12, sticky="ew")

            ctk.CTkLabel(field_frame, text=label_text,
                        font=("Arial", 12),
                        anchor="w").pack(fill="x", pady=(0, 5))

            if field_type == "text":
                entry = ctk.CTkEntry(field_frame, height=35)
                entry.pack(fill="x")
                self.ingredient_form_entries[field_name] = entry

            elif field_type == "number":
                entry = ctk.CTkEntry(field_frame, height=35)
                if field_name in ["initial_stock", "min_stock"]:
                    entry.insert(0, "0")
                elif field_name == "cost_per_unit":
                    entry.insert(0, "0.00")
                entry.pack(fill="x")
                self.ingredient_form_entries[field_name] = entry

            elif field_type == "dropdown":
                if field_name == "category":
                    # Get existing categories
                    ingredients_df = self.db.read_tab('Ingredients')
                    categories = ["General"]
                    if 'Category' in ingredients_df.columns:
                        unique_cats = ingredients_df['Category'].dropna().unique()
                        for cat in unique_cats:
                            cat_str = str(cat).strip()
                            if cat_str and cat_str.lower() != 'nan':
                                categories.append(cat_str)
                    
                    # Create dropdown frame
                    dropdown_frame = ctk.CTkFrame(field_frame, fg_color="transparent")
                    dropdown_frame.pack(fill="x")
                    
                    self.category_dropdown_var = tk.StringVar(value="General")
                    self.ingredient_category_dropdown = ctk.CTkOptionMenu(
                        dropdown_frame,
                        values=categories,
                        variable=self.category_dropdown_var,
                        width=180,
                        height=35
                    )
                    self.ingredient_category_dropdown.pack(side="left", padx=(0, 5))
                    
                    # Add "+" button
                    ctk.CTkButton(
                        dropdown_frame,
                        text="+",
                        command=self.show_add_category_popup,
                        width=35,
                        height=35,
                        fg_color="#3498db",
                        hover_color="#2980b9"
                    ).pack(side="left")
                    
                elif field_name == "unit":
                    units = ["kg", "g", "L", "ml", "pcs", "pack", "bottle", "box"]
                    self.unit_dropdown_var = tk.StringVar(value="kg")
                    dropdown = ctk.CTkOptionMenu(
                        field_frame,
                        values=units,
                        variable=self.unit_dropdown_var,
                        height=35
                    )
                    dropdown.pack(fill="x")
                    self.ingredient_form_entries[field_name] = self.unit_dropdown_var
                    
                elif field_name == "active":
                    self.active_dropdown_var = tk.StringVar(value="Yes")
                    dropdown = ctk.CTkOptionMenu(
                        field_frame,
                        values=["Yes", "No"],
                        variable=self.active_dropdown_var,
                        height=35
                    )
                    dropdown.pack(fill="x")
                    self.ingredient_form_entries[field_name] = self.active_dropdown_var

        # Description field (span 2 columns) - placed outside the grid
        desc_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        desc_frame.pack(fill="x", pady=12, padx=10)

        ctk.CTkLabel(desc_frame, text="Description:",
                    font=("Arial", 12),
                    anchor="w").pack(fill="x", pady=(0, 5))

        self.ingredient_desc_text = ctk.CTkTextbox(desc_frame, height=80)
        self.ingredient_desc_text.pack(fill="x")

        # Buttons
        button_frame = ctk.CTkFrame(parent_frame)
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="💾 Save Ingredient",
                     command=self.save_new_ingredient,
                     fg_color="#27ae60", hover_color="#219653",
                     width=180, height=45).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="🗑️ Clear Form",
                     command=self.clear_ingredient_form,
                     width=150, height=45).pack(side="left", padx=10)

        # Status label
        self.ingredient_form_status = ctk.CTkLabel(parent_frame, text="",
                                                 font=("Arial", 12))
        self.ingredient_form_status.pack(pady=10)

    def save_new_ingredient(self):
        """Save new ingredient to database"""
        try:
            # Get form data with proper defaults for empty fields
            product_data = {
                'Ingredient_ID': self.generated_ingredient_id,
                'Ingredient_Name': self.ingredient_form_entries['ingredient_name'].get(),
                'Category': self.category_dropdown_var.get(),
                'Unit': self.unit_dropdown_var.get(),
                'Active': self.active_dropdown_var.get(),
                'Description': self.ingredient_desc_text.get("1.0", "end-1c").strip(),
                'Last_Updated': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Handle numeric fields with proper conversion
            numeric_fields = {
                'initial_stock': 'Current_Stock',
                'cost_per_unit': 'Cost_Per_Unit', 
                'min_stock': 'Min_Stock_Level'
            }
            
            for form_field, db_field in numeric_fields.items():
                value = self.ingredient_form_entries.get(form_field, '').get() if isinstance(self.ingredient_form_entries.get(form_field), ctk.CTkEntry) else '0'
                if not value.strip():
                    value = '0'
                try:
                    product_data[db_field] = float(value)
                except ValueError:
                    product_data[db_field] = 0.0
            
            # Handle supplier (text field)
            supplier_entry = self.ingredient_form_entries.get('supplier')
            if supplier_entry:
                product_data['Supplier'] = supplier_entry.get()
            else:
                product_data['Supplier'] = ''
            
            # Validate required fields
            if not product_data['Ingredient_Name']:
                self.ingredient_form_status.configure(text="Ingredient Name is required",
                                                     text_color="red")
                return

            if not product_data['Unit']:
                self.ingredient_form_status.configure(text="Unit is required",
                                                     text_color="red")
                return

            if product_data['Cost_Per_Unit'] < 0:
                self.ingredient_form_status.configure(text="Cost cannot be negative",
                                                     text_color="red")
                return

            # Save to database
            success, message = self.db.add_ingredient(product_data)

            if success:
                self.ingredient_form_status.configure(text=f"✅ {message}", text_color="green")
                # Clear form
                self.clear_ingredient_form()
                # Generate new ID for next ingredient
                self.generated_ingredient_id = self.db.generate_ingredient_id()
                
                # Refresh table and update filters
                if hasattr(self, 'ingredients_table_frame'):
                    self.refresh_ingredients_table()
                    
                # Update filter dropdowns in the View tab
                self.update_filter_dropdowns()
            else:
                self.ingredient_form_status.configure(text=f"❌ {message}", text_color="red")

        except ValueError as e:
            self.ingredient_form_status.configure(text=f"Invalid number format: {str(e)}",
                                                 text_color="red")
        except Exception as e:
            self.ingredient_form_status.configure(text=f"Error: {str(e)}",
                                                 text_color="red")

    def clear_ingredient_form(self):
        """Clear the ingredient form"""
        # Clear text entries
        for field_name, entry in self.ingredient_form_entries.items():
            if isinstance(entry, ctk.CTkEntry):
                entry.delete(0, 'end')
        
        # Reset dropdowns
        if hasattr(self, 'category_dropdown_var'):
            self.category_dropdown_var.set("General")
        if hasattr(self, 'unit_dropdown_var'):
            self.unit_dropdown_var.set("kg")
        if hasattr(self, 'active_dropdown_var'):
            self.active_dropdown_var.set("Yes")
        
        # Reset number fields
        if 'initial_stock' in self.ingredient_form_entries:
            self.ingredient_form_entries['initial_stock'].insert(0, "0")
        if 'cost_per_unit' in self.ingredient_form_entries:
            self.ingredient_form_entries['cost_per_unit'].insert(0, "0.00")
        if 'min_stock' in self.ingredient_form_entries:
            self.ingredient_form_entries['min_stock'].insert(0, "0")
        
        # Clear description
        self.ingredient_desc_text.delete("1.0", "end")
        
        # Generate new ID
        self.generated_ingredient_id = self.db.generate_ingredient_id()
        
        # Update status
        self.ingredient_form_status.configure(text="")

    # ===== INGREDIENT ACTION METHODS =====

    def view_ingredient_details(self, ingredient_id):
        """View ingredient details in a popup"""
        ingredients_df = self.db.read_tab('Ingredients')
        ingredient_row = ingredients_df[ingredients_df['Ingredient_ID'] == ingredient_id]

        if ingredient_row.empty:
            messagebox.showerror("Error", f"Ingredient {ingredient_id} not found")
            return

        ingredient = ingredient_row.iloc[0]

        # Create popup
        popup = ctk.CTkToplevel(self.window)
        popup.title(f"Ingredient: {ingredient['Ingredient_Name']}")
        popup.geometry("500x600")
        popup.transient(self.window)
        popup.grab_set()

        # Center
        popup.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() - 500) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - 600) // 2
        popup.geometry(f"+{x}+{y}")

        # Main container
        main_frame = ctk.CTkFrame(popup)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_frame = ctk.CTkFrame(main_frame, fg_color="#2c3e50", corner_radius=10)
        title_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(title_frame,
                    text=f"📋 {ingredient['Ingredient_Name']}",
                    font=("Arial", 20, "bold"),
                    text_color="white").pack(pady=15)

        # Details in a scrollable frame
        details_frame = ctk.CTkScrollableFrame(main_frame, height=400)
        details_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Display details
        details = [
            ("ID:", ingredient_id),
            ("Category:", ingredient.get('Category', 'N/A')),
            ("Unit:", ingredient.get('Unit', 'N/A')),
            ("Current Stock:", f"{ingredient.get('Current_Stock', 0):.2f}"),
            ("Cost per Unit:", f"{self.config['currency']}{ingredient.get('Cost_Per_Unit', 0):.2f}"),
            ("Min Stock Level:", f"{ingredient.get('Min_Stock_Level', 0):.2f}"),
            ("Supplier:", ingredient.get('Supplier', 'N/A')),
            ("Status:", "Active" if str(ingredient.get('Active', 'Yes')).upper() == 'YES' else "Inactive"),
            ("Last Updated:", ingredient.get('Last_Updated', 'N/A')),
            ("Description:", "")
        ]

        for label, value in details:
            if label == "Description:":
                ctk.CTkLabel(details_frame, text=label,
                           font=("Arial", 12, "bold")).pack(anchor="w", pady=(15, 5))
                
                desc_text = ingredient.get('Description', 'No description')
                desc_label = ctk.CTkLabel(details_frame, text=desc_text,
                                        font=("Arial", 11),
                                        wraplength=400,
                                        justify="left")
                desc_label.pack(anchor="w", pady=(0, 10))
            else:
                row_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=5)

                ctk.CTkLabel(row_frame, text=label,
                           font=("Arial", 12, "bold"),
                           width=120,
                           anchor="w").pack(side="left")

                ctk.CTkLabel(row_frame, text=value,
                           font=("Arial", 12)).pack(side="left", padx=10)

        # Close button
        ctk.CTkButton(main_frame, text="✕ Close",
                     command=popup.destroy,
                     width=200, height=45,
                     font=("Arial", 14, "bold"),
                     fg_color="#3498db",
                     hover_color="#2980b9").pack(pady=10)

    def edit_ingredient_popup(self, ingredient_id):
        """Popup to edit ingredient"""
        ingredients_df = self.db.read_tab('Ingredients')
        ingredient_row = ingredients_df[ingredients_df['Ingredient_ID'] == ingredient_id]

        if ingredient_row.empty:
            messagebox.showerror("Error", f"Ingredient {ingredient_id} not found")
            return

        ingredient = ingredient_row.iloc[0]
        ingredient_name = ingredient['Ingredient_Name']

        # Create popup
        popup = ctk.CTkToplevel(self.window)
        popup.title(f"Edit: {ingredient_name}")
        popup.geometry("600x700")
        popup.transient(self.window)
        popup.grab_set()

        # Center
        popup.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() - 600) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - 700) // 2
        popup.geometry(f"+{x}+{y}")

        # Main container
        main_frame = ctk.CTkFrame(popup)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_frame = ctk.CTkFrame(main_frame, fg_color="#2c3e50", corner_radius=10)
        title_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(title_frame,
                    text=f"✏️ Edit: {ingredient_name}",
                    font=("Arial", 18, "bold"),
                    text_color="white").pack(pady=15)

        ctk.CTkLabel(title_frame,
                    text=f"ID: {ingredient_id}",
                    font=("Arial", 12),
                    text_color="#ecf0f1").pack(pady=(0, 10))

        # Create form in scrollable frame
        form_frame = ctk.CTkScrollableFrame(main_frame, height=400)
        form_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Form fields
        fields = [
            ("Ingredient Name*:", "Ingredient_Name", ingredient.get('Ingredient_Name', '')),
            ("Category:", "Category", ingredient.get('Category', 'General')),
            ("Unit*:", "Unit", ingredient.get('Unit', 'kg')),
            ("Cost per Unit*:", "Cost_Per_Unit", ingredient.get('Cost_Per_Unit', 0)),
            ("Min Stock Level:", "Min_Stock_Level", ingredient.get('Min_Stock_Level', 0)),
            ("Supplier:", "Supplier", ingredient.get('Supplier', '')),
            ("Active (Yes/No):", "Active", ingredient.get('Active', 'Yes')),
            ("Description:", "Description", ingredient.get('Description', ''))
        ]

        entries = {}

        for label, field, value in fields:
            field_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            field_frame.pack(fill="x", pady=8)

            ctk.CTkLabel(field_frame, text=label,
                        font=("Arial", 12),
                        width=150,
                        anchor="w").pack(side="left")

            if field in ["Category", "Unit", "Active"]:
                # Dropdown fields
                if field == "Category":
                    # Get categories
                    categories_df = self.db.read_tab('Ingredients')
                    categories = ["General"]
                    if 'Category' in categories_df.columns:
                        unique_cats = categories_df['Category'].dropna().unique()
                        for cat in unique_cats:
                            if cat and str(cat).strip():
                                categories.append(str(cat).strip())
                    
                    var = tk.StringVar(value=str(value) if pd.notna(value) else "General")
                    dropdown_frame = ctk.CTkFrame(field_frame, fg_color="transparent")
                    dropdown_frame.pack(side="left", padx=10)
                    
                    dropdown = ctk.CTkOptionMenu(
                        dropdown_frame,
                        values=categories,
                        variable=var,
                        width=200
                    )
                    dropdown.pack(side="left")
                    
                    # Add "+" button
                    ctk.CTkButton(
                        dropdown_frame,
                        text="+",
                        command=lambda v=var: self.show_add_category_popup(v.get()),
                        width=30,
                        height=30
                    ).pack(side="left", padx=5)
                    
                elif field == "Unit":
                    units = ["kg", "g", "L", "ml", "pcs", "pack", "bottle", "box"]
                    var = tk.StringVar(value=str(value) if pd.notna(value) else "kg")
                    dropdown = ctk.CTkOptionMenu(
                        field_frame,
                        values=units,
                        variable=var,
                        width=250
                    )
                    dropdown.pack(side="left", padx=10)
                    
                elif field == "Active":
                    var = tk.StringVar(value=str(value) if pd.notna(value) else "Yes")
                    dropdown = ctk.CTkOptionMenu(
                        field_frame,
                        values=["Yes", "No"],
                        variable=var,
                        width=250
                    )
                    dropdown.pack(side="left", padx=10)
                
                entries[field] = var
                
            elif field == "Description":
                # Text box for description
                textbox = ctk.CTkTextbox(field_frame, width=250, height=80)
                textbox.pack(side="left", padx=10)
                if pd.notna(value):
                    textbox.insert("1.0", str(value))
                entries[field] = textbox
                
            else:
                # Entry fields
                entry = ctk.CTkEntry(field_frame, width=250)
                entry.pack(side="left", padx=10)
                if pd.notna(value):
                    if field in ["Cost_Per_Unit", "Min_Stock_Level"]:
                        entry.insert(0, f"{float(value):.2f}")
                    else:
                        entry.insert(0, str(value))
                entries[field] = entry

        # Status label
        status_label = ctk.CTkLabel(main_frame, text="",
                                   font=("Arial", 12))
        status_label.pack(pady=10)

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)

        def save_changes():
            try:
                updated_data = {}
                
                for field, widget in entries.items():
                    if isinstance(widget, tk.StringVar):
                        value = widget.get()
                    elif isinstance(widget, ctk.CTkTextbox):
                        value = widget.get("1.0", "end-1c").strip()
                    else:
                        value = widget.get()
                    
                    # Handle empty values
                    if value == '' or value is None:
                        if field in ["Cost_Per_Unit", "Min_Stock_Level", "Current_Stock"]:
                            value = 0.0
                        elif field in ["Supplier", "Description", "Category"]:
                            value = ''
                        elif field == "Active":
                            value = 'Yes'
                    
                    updated_data[field] = value
                
                # Validate required fields
                if not updated_data.get('Ingredient_Name'):
                    status_label.configure(text="Ingredient Name is required",
                                         text_color="red")
                    return
                
                if not updated_data.get('Unit'):
                    status_label.configure(text="Unit is required",
                                         text_color="red")
                    return
                
                # Update in database
                success, message = self.db.update_ingredient(ingredient_id, updated_data)
                
                if success:
                    status_label.configure(text=f"✅ {message}", text_color="green")
                    # Refresh table and update filters
                    self.refresh_ingredients_table()
                    # Update filter dropdowns
                    self.update_filter_dropdowns()
                    popup.after(1500, popup.destroy)
                    
            except ValueError as e:
                status_label.configure(text=f"Invalid number: {str(e)}",
                                     text_color="red")
            except Exception as e:
                status_label.configure(text=f"Error: {str(e)}",
                                     text_color="red")

        ctk.CTkButton(button_frame, text="💾 Save Changes",
                     command=save_changes,
                     fg_color="#27ae60", hover_color="#219653",
                     width=150, height=40).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="✕ Cancel",
                     command=popup.destroy,
                     width=150, height=40).pack(side="left", padx=10)

    def update_stock_popup(self, ingredient_id):
        """Popup to update ingredient stock"""
        ingredients_df = self.db.read_tab('Ingredients')
        ingredient_row = ingredients_df[ingredients_df['Ingredient_ID'] == ingredient_id]

        if ingredient_row.empty:
            messagebox.showerror("Error", f"Ingredient {ingredient_id} not found")
            return

        ingredient = ingredient_row.iloc[0]
        current_stock = float(ingredient.get('Current_Stock', 0))
        ingredient_name = ingredient['Ingredient_Name']

        # Create popup
        popup = ctk.CTkToplevel(self.window)
        popup.title(f"Update Stock: {ingredient_name}")
        popup.geometry("450x700")
        popup.transient(self.window)
        popup.grab_set()

        # Center
        popup.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() - 400) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - 500) // 2
        popup.geometry(f"+{x}+{y}")

        # Main container
        main_frame = ctk.CTkFrame(popup)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_frame = ctk.CTkFrame(main_frame, fg_color="#2c3e50", corner_radius=10)
        title_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(title_frame,
                    text=f"📦 Update Stock",
                    font=("Arial", 18, "bold"),
                    text_color="white").pack(pady=15)

        ctk.CTkLabel(title_frame,
                    text=f"{ingredient_name}",
                    font=("Arial", 14),
                    text_color="#ecf0f1").pack(pady=(0, 10))

        # Current stock display
        stock_frame = ctk.CTkFrame(main_frame, fg_color="#ecf0f1", corner_radius=8)
        stock_frame.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(stock_frame,
                    text=f"Current Stock: {current_stock:.2f} {ingredient.get('Unit', '')}",
                    font=("Arial", 14, "bold"),
                    text_color="#2c3e50").pack(pady=15)

        # Update options
        options_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        options_frame.pack(fill="x", pady=10)

        # Operation selection
        ctk.CTkLabel(options_frame, text="Operation:",
                    font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))

        self.stock_operation = tk.StringVar(value="add")
        
        ctk.CTkRadioButton(options_frame, text="➕ Add Stock",
                          variable=self.stock_operation, value="add").pack(anchor="w", pady=2)
        ctk.CTkRadioButton(options_frame, text="➖ Remove Stock",
                          variable=self.stock_operation, value="remove").pack(anchor="w", pady=2)
        ctk.CTkRadioButton(options_frame, text="✏️ Set Exact Amount",
                          variable=self.stock_operation, value="set").pack(anchor="w", pady=2)

        # Amount entry
        amount_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        amount_frame.pack(fill="x", pady=15)

        ctk.CTkLabel(amount_frame, text="Amount:",
                    font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))

        self.stock_amount_var = tk.StringVar(value="0")
        amount_entry = ctk.CTkEntry(amount_frame,
                                   textvariable=self.stock_amount_var,
                                   height=35)
        amount_entry.pack(fill="x")
        amount_entry.focus_set()

        # Reason entry (optional)
        reason_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        reason_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(reason_frame, text="Reason (optional):",
                    font=("Arial", 12)).pack(anchor="w", pady=(0, 5))

        self.stock_reason_var = tk.StringVar()
        reason_entry = ctk.CTkEntry(reason_frame,
                                   textvariable=self.stock_reason_var,
                                   placeholder_text="e.g., New shipment, Used in production",
                                   height=35)
        reason_entry.pack(fill="x")

        # Status label
        status_label = ctk.CTkLabel(main_frame, text="",
                                   font=("Arial", 12))
        status_label.pack(pady=10)

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)

        def update_stock():
            try:
                amount = float(self.stock_amount_var.get())
                if amount <= 0:
                    status_label.configure(text="Amount must be greater than 0",
                                         text_color="red")
                    return

                operation = self.stock_operation.get()
                reason = self.stock_reason_var.get() or "Stock update"

                # Calculate new stock
                if operation == "add":
                    new_stock = current_stock + amount
                elif operation == "remove":
                    if amount > current_stock:
                        status_label.configure(text="Cannot remove more than current stock",
                                             text_color="red")
                        return
                    new_stock = current_stock - amount
                else:  # set
                    new_stock = amount

                # Update in database
                success, message = self.db.update_ingredient_stock(
                    ingredient_id, new_stock, operation, amount, reason
                )

                if success:
                    status_label.configure(text=f"✅ {message}", text_color="green")
                    
                    # Disable buttons temporarily
                    for widget in button_frame.winfo_children():
                        if isinstance(widget, ctk.CTkButton):
                            widget.configure(state="disabled")
                    
                    # Refresh table and update filters
                    self.refresh_ingredients_table()
                    # Update filter dropdowns
                    self.update_filter_dropdowns()
                    popup.after(1500, popup.destroy)

            except ValueError:
                status_label.configure(text="Please enter a valid number",
                                     text_color="red")

        ctk.CTkButton(button_frame, text="💾 Update Stock",
                     command=update_stock,
                     fg_color="#27ae60", hover_color="#219653",
                     width=150, height=40).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="✕ Cancel",
                     command=popup.destroy,
                     width=150, height=40).pack(side="left", padx=10)

    def delete_ingredient_popup(self, ingredient_id):
        """Popup to delete ingredient"""
        ingredients_df = self.db.read_tab('Ingredients')
        ingredient_row = ingredients_df[ingredients_df['Ingredient_ID'] == ingredient_id]

        if ingredient_row.empty:
            messagebox.showerror("Error", f"Ingredient {ingredient_id} not found")
            return

        ingredient = ingredient_row.iloc[0]
        ingredient_name = ingredient['Ingredient_Name']
        current_stock = float(ingredient.get('Current_Stock', 0))

        # Check if ingredient is used in any recipes
        recipes_df = self.db.read_tab('Recipes')
        used_in_recipes = recipes_df[recipes_df['Ingredient_ID'] == ingredient_id]

        if not used_in_recipes.empty:
            product_ids = recipes_df[recipes_df['Ingredient_ID'] == ingredient_id]['Product_ID'].unique()
            product_list = ", ".join(product_ids[:3])  # Show first 3 products
            if len(product_ids) > 3:
                product_list += f" and {len(product_ids) - 3} more..."

            response = messagebox.askyesno(
                "Cannot Delete",
                f"Cannot delete '{ingredient_name}' because it is used in {len(used_in_recipes)} recipe(s).\n\n"
                f"Used in products: {product_list}\n\n"
                "Mark as inactive instead?"
            )

            if response:
                # Mark as inactive
                success, message = self.db.update_ingredient(ingredient_id, {'Active': 'No'})
                if success:
                    messagebox.showinfo("Success", f"'{ingredient_name}' marked as inactive.")
                    self.refresh_ingredients_table()
            return

        # Confirm deletion
        if current_stock > 0:
            response = messagebox.askyesno(
                "Confirm Deletion",
                f"Delete '{ingredient_name}'?\n\n"
                f"⚠️ Warning: This ingredient has {current_stock} in stock.\n"
                "This action cannot be undone.\n\n"
                "Are you sure?"
            )
        else:
            response = messagebox.askyesno(
                "Confirm Deletion",
                f"Permanently delete '{ingredient_name}'?\n\n"
                "This action cannot be undone.\n\n"
                "Are you sure?"
            )

        if response:
            # Double confirmation for non-zero stock
            if current_stock > 0:
                confirm_text = simpledialog.askstring(
                    "Final Confirmation",
                    f"Type 'DELETE {ingredient_id}' to confirm:"
                )

                if confirm_text != f"DELETE {ingredient_id}":
                    messagebox.showinfo("Cancelled", "Deletion cancelled.")
                    return

            # Perform deletion
            success, message = self.db.delete_ingredient(ingredient_id)

            if success:
                messagebox.showinfo("✅ Success", message)
                self.refresh_ingredients_table()
            else:
                messagebox.showerror("❌ Error", message)

    # Category popup method from ProductsGUI (reuse it)
    def show_add_category_popup(self, current_value=""):
        """Popup to add a new category (reused from ProductsGUI)"""
        # This is the same method we created earlier
        # Make sure to copy it from the ProductsGUI class or create it here
        pass  # You'll need to copy the actual method here