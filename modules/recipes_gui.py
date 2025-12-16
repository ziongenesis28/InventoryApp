# recipes_gui.py - All recipe-related GUI code
import customtkinter as ctk
import pandas as pd
import tkinter as tk
from tkinter import messagebox

class RecipesGUI:
    def __init__(self, window, db, config):
        self.window = window
        self.db = db
        self.config = config
        self.main_content = None
    
    def clear_main_content(self):
        if self.main_content:
            for widget in self.main_content.winfo_children():
                widget.destroy()
    
    def show_recipes(self, main_content_frame):
        self.main_content = main_content_frame
        self.clear_main_content()
        
        # Create tabview for recipes
        recipe_tabs = ctk.CTkTabview(self.main_content)
        recipe_tabs.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add tabs
        recipe_tabs.add("View Recipes")
        recipe_tabs.add("Create Recipe")
        recipe_tabs.add("Cost Analysis")
        
        # Store tabview reference
        self.recipe_tabview = recipe_tabs
        
        # Fill each tab
        self.show_all_recipes(recipe_tabs.tab("View Recipes"))
        self.create_recipe_form(recipe_tabs.tab("Create Recipe"))
        self.show_cost_analysis(recipe_tabs.tab("Cost Analysis"))
    
    def show_all_recipes(self, parent_frame):
        """Show all products with their recipes - FIXED"""
        ctk.CTkLabel(parent_frame, text="All Product Recipes", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Top button frame - FIXED: Now opens popup
        top_button_frame = ctk.CTkFrame(parent_frame)
        top_button_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkButton(top_button_frame, text="➕ Create New Recipe",
                     command=self.open_create_recipe_popup,
                     fg_color="#27ae60", hover_color="#219653",
                     height=40, font=("Arial", 13)).pack(pady=5)
        
        # ===== ENHANCED FILTER FRAME =====
        filter_frame = ctk.CTkFrame(parent_frame)
        filter_frame.pack(pady=10, padx=10, fill="x")
        
        # Row 1: Search
        search_row = ctk.CTkFrame(filter_frame, fg_color="transparent")
        search_row.pack(fill="x", pady=5)
        
        ctk.CTkLabel(search_row, text="Search:", 
                    font=("Arial", 12)).pack(side="left", padx=10)
        
        self.recipe_search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(search_row, 
                                   textvariable=self.recipe_search_var,
                                   placeholder_text="Search product name or ID...",
                                   width=300)
        search_entry.pack(side="left", padx=10)
        
        # Row 2: Category Filter
        category_row = ctk.CTkFrame(filter_frame, fg_color="transparent")
        category_row.pack(fill="x", pady=5)
        
        ctk.CTkLabel(category_row, text="Category Filter:", 
                    font=("Arial", 12)).pack(side="left", padx=10)
        
        # Get unique categories from products
        products_df = self.db.get_all_products()
        categories = ["All Categories"]  # Default option
        
        if not products_df.empty and 'Category' in products_df.columns:
            # Get unique categories, remove NaN/None
            unique_cats = products_df['Category'].dropna().unique()
            for cat in unique_cats:
                if cat and str(cat).strip() and str(cat).strip().lower() != 'nan':
                    categories.append(str(cat).strip())
        
        # Remove duplicates and sort
        categories = sorted(list(set(categories)))
        
        self.recipe_category_var = tk.StringVar(value="All Categories")
        category_menu = ctk.CTkOptionMenu(category_row,
                                         values=categories,
                                         variable=self.recipe_category_var,
                                         width=200)
        category_menu.pack(side="left", padx=10)
        
        # Row 3: Status Filter and Buttons
        button_row = ctk.CTkFrame(filter_frame, fg_color="transparent")
        button_row.pack(fill="x", pady=5)
        
        # Search button
        ctk.CTkButton(button_row, text="🔍 Search & Filter", 
                     command=lambda: self.refresh_recipes_view(),
                     fg_color="#3498db", hover_color="#2980b9",
                     width=150).pack(side="left", padx=5)
        
        # Clear filters button
        ctk.CTkButton(button_row, text="🗑️ Clear Filters", 
                     command=self.clear_recipe_filters,
                     fg_color="#95a5a6", hover_color="#7f8c8d",
                     width=120).pack(side="left", padx=5)
        
        # Refresh all button
        ctk.CTkButton(button_row, text="🔄 Refresh All", 
                     command=lambda: self.refresh_all_recipes(),
                     fg_color="#27ae60", hover_color="#219653",
                     width=120).pack(side="right", padx=5)
        
        # Initialize recipes_display_container
        self.recipes_display_container = None
        
        # Create recipes display frame
        recipes_display_container = ctk.CTkFrame(parent_frame)
        recipes_display_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Store reference
        self.recipes_display_container = recipes_display_container
        
        # Initial load
        self.refresh_all_recipes()

    def edit_existing_recipe_popup(self, product_id):
        """Open popup to edit existing recipe WITH UNIT CONVERSION"""
        # Get product info
        products_df = self.db.read_tab('Products')
        product_info = products_df[products_df['Product_ID'] == product_id]
        
        if product_info.empty:
            messagebox.showerror("Error", f"Product {product_id} not found")
            return
        
        product_name = product_info.iloc[0]['Product_Name']
        
        # Get existing recipe with ingredient details
        existing_recipe = self.db.get_product_recipes(product_id)
        
        if existing_recipe.empty:
            messagebox.showinfo("No Recipe", f"Product '{product_name}' has no recipe to edit.")
            return
        
        # Get all ingredients for dropdown
        all_ingredients_df = self.db.get_all_ingredients()
        
        # Create popup window
        popup = ctk.CTkToplevel(self.window)
        popup.title(f"Edit Recipe: {product_name}")
        popup.geometry("700x850")
        popup.minsize(600, 750)
        popup.transient(self.window)
        popup.grab_set()
        
        # Center popup
        popup.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() - popup.winfo_width()) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - popup.winfo_height()) // 2
        popup.geometry(f"+{x}+{y}")
        
        # Main container
        main_container = ctk.CTkFrame(popup)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Title
        title_frame = ctk.CTkFrame(main_container, fg_color="#2c3e50", corner_radius=10)
        title_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(title_frame, 
                    text=f"Edit Recipe: {product_name}",
                    font=("Arial", 18, "bold"),
                    text_color="white").pack(pady=15)
        
        # Product ID display
        ctk.CTkLabel(title_frame,
                    text=f"Product ID: {product_id}",
                    font=("Arial", 12),
                    text_color="#ecf0f1").pack(pady=5)
        
        # Create scrollable frame for ingredients
        scroll_frame = ctk.CTkScrollableFrame(main_container, height=450)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Headers for ingredient table
        headers_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        headers_frame.pack(fill="x", pady=5)
        
        headers = ["Ingredient", "Quantity", "Unit", ""]
        widths = [250, 100, 80, 60]
        
        for header, width in zip(headers, widths):
            ctk.CTkLabel(headers_frame, text=header, 
                        font=("Arial", 12, "bold"),
                        width=width).pack(side="left", padx=5)
        
        # Store ingredient data for this popup
        popup_ingredients = []
        
        # Display each existing recipe item WITH CONVERSION
        for idx, (_, recipe_item) in enumerate(existing_recipe.iterrows()):
            row_frame = ctk.CTkFrame(scroll_frame)
            row_frame.pack(fill="x", pady=5, padx=5)
            
            ingredient_id = recipe_item['Ingredient_ID']
            ingredient_name = recipe_item.get('Ingredient_Name', ingredient_id)
            base_unit = recipe_item.get('Unit', 'pcs')
            base_quantity = recipe_item.get('Quantity_Required', 0)
            
            # Ingredient dropdown
            ingredient_options = ["Select Ingredient"] + [
                f"{row['Ingredient_ID']} - {row['Ingredient_Name']} ({row['Unit']})" 
                for _, row in all_ingredients_df.iterrows()
            ]
            
            # Find current ingredient in options
            current_option = ""
            for option in ingredient_options:
                if option.startswith(ingredient_id + " - "):
                    current_option = option
                    break
            
            ing_var = tk.StringVar(value=current_option if current_option else "Select Ingredient")
            ing_menu = ctk.CTkOptionMenu(row_frame, 
                                        values=ingredient_options,
                                        variable=ing_var,
                                        width=250)
            ing_menu.pack(side="left", padx=5, pady=5)
            
            # CONVERSION LOGIC
            # Determine best display unit and quantity
            display_quantity = base_quantity
            display_unit = base_unit
            
            # Convert to more user-friendly units
            if base_unit == 'kg' and base_quantity < 1:
                if base_quantity >= 0.001:  # Convert to grams if < 1kg but >= 1g
                    display_quantity = base_quantity * 1000
                    display_unit = 'g'
                else:  # Convert to milligrams if < 1g
                    display_quantity = base_quantity * 1000000
                    display_unit = 'mg'
            elif base_unit == 'L' and base_quantity < 1:
                display_quantity = base_quantity * 1000
                display_unit = 'ml'
            elif base_unit == 'dozen':
                # Check if it's better to show as pieces
                if base_quantity < 1:
                    display_quantity = base_quantity * 12
                    display_unit = 'pcs'
            
            # Format quantity nicely
            if display_quantity.is_integer():
                quantity_text = f"{display_quantity:.0f}"
            else:
                # Show up to 3 decimal places
                quantity_text = f"{display_quantity:.3f}".rstrip('0').rstrip('.')
            
            # Quantity entry
            qty_entry = ctk.CTkEntry(row_frame, 
                                    placeholder_text="Qty",
                                    width=100)
            qty_entry.insert(0, quantity_text)
            qty_entry.pack(side="left", padx=5, pady=5)
            
            # Unit dropdown with appropriate options
            unit_var = tk.StringVar(value=display_unit)
            
            # Determine available units based on base unit
            if base_unit in ['kg', 'g', 'mg']:
                unit_options = ['kg', 'g', 'mg']
            elif base_unit in ['L', 'ml']:
                unit_options = ['L', 'ml']
            elif base_unit in ['pcs', 'dozen']:
                unit_options = ['pcs', 'dozen']
            elif base_unit in ['tsp', 'tbsp', 'cup']:
                unit_options = ['tsp', 'tbsp', 'cup']
            else:
                unit_options = [base_unit]
            
            unit_menu = ctk.CTkOptionMenu(row_frame,
                                         values=unit_options,
                                         variable=unit_var,
                                         width=80)
            unit_menu.pack(side="left", padx=5, pady=5)
            
            # Base unit display (read-only)
            base_label = ctk.CTkLabel(row_frame, 
                                     text=f"Base: {base_quantity:.4f} {base_unit}",
                                     font=("Arial", 9),
                                     text_color="gray",
                                     width=120)
            base_label.pack(side="left", padx=5, pady=5)
            
            # Remove button
            remove_btn = ctk.CTkButton(row_frame, text="❌", width=30, height=30,
                                      command=lambda frame=row_frame: frame.destroy(),
                                      fg_color="#e74c3c", hover_color="#c0392b")
            remove_btn.pack(side="right", padx=5, pady=5)
            
            # Store data with base unit info for conversion
            ingredient_data = {
                'frame': row_frame,
                'ing_var': ing_var,
                'qty_entry': qty_entry,
                'unit_var': unit_var,
                'base_unit': base_unit,
                'base_quantity': base_quantity,
                'base_label': base_label
            }
            popup_ingredients.append(ingredient_data)
            
            # Function to update conversion display
            def update_conversion(ing_data=ingredient_data):
                try:
                    qty_text = ing_data['qty_entry'].get()
                    selected_unit = ing_data['unit_var'].get()
                    base_unit = ing_data['base_unit']
                    
                    if qty_text and selected_unit:
                        qty = float(qty_text)
                        
                        # Convert to base unit
                        conversions = {
                            ('kg', 'g'): 1000,
                            ('kg', 'mg'): 1000000,
                            ('g', 'kg'): 0.001,
                            ('g', 'mg'): 1000,
                            ('mg', 'g'): 0.001,
                            ('mg', 'kg'): 0.000001,
                            ('L', 'ml'): 1000,
                            ('ml', 'L'): 0.001,
                            ('dozen', 'pcs'): 12,
                            ('pcs', 'dozen'): 1/12,
                            ('cup', 'tbsp'): 16,
                            ('cup', 'tsp'): 48,
                            ('tbsp', 'cup'): 1/16,
                            ('tbsp', 'tsp'): 3,
                            ('tsp', 'cup'): 1/48,
                            ('tsp', 'tbsp'): 1/3
                        }
                        
                        if (selected_unit, base_unit) in conversions:
                            factor = conversions[(selected_unit, base_unit)]
                            base_qty = qty * factor
                            ing_data['base_label'].configure(
                                text=f"Base: {base_qty:.4f} {base_unit}",
                                text_color="blue"
                            )
                            ing_data['base_quantity'] = base_qty
                        else:
                            # Same unit or no conversion needed
                            ing_data['base_label'].configure(
                                text=f"Base: {qty:.4f} {base_unit}"
                            )
                            ing_data['base_quantity'] = qty
                except ValueError:
                    ing_data['base_label'].configure(text="Invalid", text_color="red")
            
            # Bind events to update conversion
            unit_var.trace_add("write", lambda *args, d=ingredient_data: update_conversion(d))
            qty_entry.bind("<KeyRelease>", lambda e, d=ingredient_data: update_conversion(d))
            
            # Initial conversion update
            update_conversion(ingredient_data)
        
        # Add New Ingredient button
        def add_new_ingredient_row():
            """Add a new ingredient row to the popup"""
            row_frame = ctk.CTkFrame(scroll_frame)
            row_frame.pack(fill="x", pady=5, padx=5)
            
            # Ingredient dropdown
            ingredient_options = ["Select Ingredient"] + [
                f"{row['Ingredient_ID']} - {row['Ingredient_Name']} ({row['Unit']})" 
                for _, row in all_ingredients_df.iterrows()
            ]
            
            ing_var = tk.StringVar(value=ingredient_options[0])
            ing_menu = ctk.CTkOptionMenu(row_frame, 
                                        values=ingredient_options,
                                        variable=ing_var,
                                        width=250)
            ing_menu.pack(side="left", padx=5, pady=5)
            
            # Quantity entry
            qty_entry = ctk.CTkEntry(row_frame, 
                                    placeholder_text="Qty",
                                    width=100)
            qty_entry.insert(0, "0")
            qty_entry.pack(side="left", padx=5, pady=5)
            
            # Unit dropdown (initially empty, will update when ingredient selected)
            unit_var = tk.StringVar(value="")
            unit_menu = ctk.CTkOptionMenu(row_frame,
                                         values=[""],
                                         variable=unit_var,
                                         width=80,
                                         state="disabled")
            unit_menu.pack(side="left", padx=5, pady=5)
            
            # Base unit display
            base_label = ctk.CTkLabel(row_frame, 
                                     text="",
                                     font=("Arial", 9),
                                     text_color="gray",
                                     width=120)
            base_label.pack(side="left", padx=5, pady=5)
            
            # Remove button
            remove_btn = ctk.CTkButton(row_frame, text="❌", width=30, height=30,
                                      command=lambda: row_frame.destroy(),
                                      fg_color="#e74c3c", hover_color="#c0392b")
            remove_btn.pack(side="right", padx=5, pady=5)
            
            # Store data
            ingredient_data = {
                'frame': row_frame,
                'ing_var': ing_var,
                'qty_entry': qty_entry,
                'unit_var': unit_var,
                'unit_menu': unit_menu,
                'base_label': base_label,
                'base_unit': "",
                'base_quantity': 0
            }
            popup_ingredients.append(ingredient_data)
            
            # Function to update unit options when ingredient is selected
            def update_unit_options(ing_data=ingredient_data):
                selected = ing_data['ing_var'].get()
                if selected != "Select Ingredient" and " - " in selected and "(" in selected:
                    # Extract base unit from parentheses
                    base_unit = selected.split("(")[1].split(")")[0]
                    ing_data['base_unit'] = base_unit
                    
                    # Set up unit options based on base unit
                    if base_unit in ['kg', 'g', 'mg']:
                        units = ['kg', 'g', 'mg']
                    elif base_unit in ['L', 'ml']:
                        units = ['L', 'ml']
                    elif base_unit in ['pcs', 'dozen']:
                        units = ['pcs', 'dozen']
                    elif base_unit in ['tsp', 'tbsp', 'cup']:
                        units = ['tsp', 'tbsp', 'cup']
                    else:
                        units = [base_unit]
                    
                    ing_data['unit_menu'].configure(values=units, state="normal")
                    ing_data['unit_var'].set(base_unit)  # Default to base unit
            
            # Function to update conversion
            def update_conversion_new(ing_data=ingredient_data):
                try:
                    qty_text = ing_data['qty_entry'].get()
                    selected_unit = ing_data['unit_var'].get()
                    base_unit = ing_data.get('base_unit', '')
                    
                    if qty_text and selected_unit and base_unit:
                        qty = float(qty_text)
                        
                        # Convert to base unit
                        conversions = {
                            ('kg', 'g'): 1000,
                            ('kg', 'mg'): 1000000,
                            ('g', 'kg'): 0.001,
                            ('g', 'mg'): 1000,
                            ('mg', 'g'): 0.001,
                            ('mg', 'kg'): 0.000001,
                            ('L', 'ml'): 1000,
                            ('ml', 'L'): 0.001,
                            ('dozen', 'pcs'): 12,
                            ('pcs', 'dozen'): 1/12,
                            ('cup', 'tbsp'): 16,
                            ('cup', 'tsp'): 48,
                            ('tbsp', 'cup'): 1/16,
                            ('tbsp', 'tsp'): 3,
                            ('tsp', 'cup'): 1/48,
                            ('tsp', 'tbsp'): 1/3
                        }
                        
                        if (selected_unit, base_unit) in conversions:
                            factor = conversions[(selected_unit, base_unit)]
                            base_qty = qty * factor
                            ing_data['base_label'].configure(
                                text=f"Base: {base_qty:.4f} {base_unit}",
                                text_color="blue"
                            )
                            ing_data['base_quantity'] = base_qty
                        else:
                            ing_data['base_label'].configure(
                                text=f"Base: {qty:.4f} {base_unit}"
                            )
                            ing_data['base_quantity'] = qty
                except ValueError:
                    ing_data['base_label'].configure(text="Invalid", text_color="red")
            
            # Bind events
            ing_var.trace_add("write", lambda *args, d=ingredient_data: update_unit_options(d))
            unit_var.trace_add("write", lambda *args, d=ingredient_data: update_conversion_new(d))
            qty_entry.bind("<KeyRelease>", lambda e, d=ingredient_data: update_conversion_new(d))
            
            # Initial update
            update_unit_options(ingredient_data)
        
        # Button to add more ingredients
        button_frame = ctk.CTkFrame(main_container)
        button_frame.pack(pady=10, padx=10)
        
        ctk.CTkButton(button_frame, text="➕ Add More Ingredients",
                     command=add_new_ingredient_row,
                     fg_color="#3498db", hover_color="#2980b9").pack(pady=5)
        
        # Status label
        status_label = ctk.CTkLabel(main_container, text="", font=("Arial", 12))
        status_label.pack(pady=10)
        
        def save_edited_recipe():
            """Save the edited recipe"""
            try:
                # Collect ingredients from all visible frames
                recipe_items = []
                
                for ing_data in popup_ingredients:
                    if not ing_data['frame'].winfo_exists():
                        continue
                    
                    ing_selection = ing_data['ing_var'].get()
                    
                    if ing_selection == "Select Ingredient":
                        continue
                    
                    # Extract ingredient ID
                    if " - " in ing_selection:
                        ing_id = ing_selection.split(" - ")[0]
                        
                        # Use base quantity (already converted)
                        base_qty = ing_data.get('base_quantity', 0)
                        
                        if base_qty <= 0:
                            status_label.configure(text="Quantity must be positive", 
                                                 text_color="red")
                            return
                        
                        recipe_items.append({
                            'ingredient_id': ing_id,
                            'quantity': base_qty
                        })
                
                if not recipe_items:
                    status_label.configure(text="Recipe must have at least one ingredient", 
                                         text_color="red")
                    return
                
                # Save the recipe
                success = self.db.save_recipe(product_id, recipe_items)
                
                if success:
                    status_label.configure(text="✅ Recipe updated successfully!", text_color="green")
                    
                    # Update product costs
                    self.db.update_all_product_costs()
                    
                    # Refresh recipes view
                    self.refresh_all_recipes()
                    
                    # Close popup after 2 seconds
                    popup.after(2000, popup.destroy)
                else:
                    status_label.configure(text="❌ Failed to update recipe", text_color="red")
                    
            except Exception as e:
                status_label.configure(text=f"Error: {str(e)}", text_color="red")
        
        # Action buttons
        action_frame = ctk.CTkFrame(main_container)
        action_frame.pack(pady=20, padx=10)
        
        ctk.CTkButton(action_frame, text="💾 Save Changes",
                     command=save_edited_recipe,
                     fg_color="#27ae60", hover_color="#219653",
                     width=150, height=40).pack(side="left", padx=10)
        
        ctk.CTkButton(action_frame, text="Cancel",
                     command=popup.destroy,
                     width=150, height=40).pack(side="left", padx=10)    
    def open_create_recipe_popup(self):
        """Open popup window to create recipe - NEW"""
        popup = ctk.CTkToplevel(self.window)
        popup.title("Create New Recipe")
        popup.geometry("500x900")
        popup.transient(self.window)
        popup.grab_set()
        
        # Center popup
        popup.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() - popup.winfo_width()) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - popup.winfo_height()) // 2
        popup.geometry(f"+{x}+{y}")
        
        # Title
        ctk.CTkLabel(popup, text="Create New Recipe", 
                    font=("Arial", 22, "bold")).pack(pady=20)
        
        # Product selection
        product_frame = ctk.CTkFrame(popup)
        product_frame.pack(fill="x", padx=50, pady=10)
        
        ctk.CTkLabel(product_frame, text="Select Product:", 
                    font=("Arial", 14)).pack(pady=5)
        
        products_df = self.db.get_all_products()
        if products_df.empty:
            ctk.CTkLabel(product_frame, text="No products available.",
                        text_color="red").pack(pady=10)
            return
        
        product_options = [f"{row['Product_ID']} - {row['Product_Name']}" 
                          for _, row in products_df.iterrows()]
        
        product_var = ctk.StringVar(value=product_options[0])
        product_menu = ctk.CTkOptionMenu(product_frame, 
                                        values=product_options,
                                        variable=product_var,
                                        width=350)
        product_menu.pack(pady=10)
        
        # Product price display
        price_label = ctk.CTkLabel(product_frame, text="", font=("Arial", 12))
        price_label.pack(pady=5)
        
        # Update price display
        def update_price(*args):
            selection = product_var.get()
            if " - " in selection:
                product_id = selection.split(" - ")[0]
                product = products_df[products_df['Product_ID'] == product_id]
                if not product.empty:
                    price = product.iloc[0]['Selling_Price']
                    price_label.configure(
                        text=f"Selling Price: {self.config['currency']}{price:,.2f}",
                        text_color="blue"
                    )
        
        product_var.trace_add("write", update_price)
        update_price()
        
        # Ingredients section
        ctk.CTkLabel(popup, text="Recipe Ingredients:", 
                    font=("Arial", 14)).pack(pady=20)
        
        # Frame for ingredient entries
        ingredient_frame = ctk.CTkScrollableFrame(popup, height=300)
        ingredient_frame.pack(fill="x", padx=50, pady=10)
        
        # Track ingredients in popup
        popup_ingredients = []
        
        def add_ingredient_row():
            """Add ingredient row to popup"""
            row_frame = ctk.CTkFrame(ingredient_frame)
            row_frame.pack(fill="x", pady=5, padx=5)
            
            # Get all ingredients
            ingredients_df = self.db.get_all_ingredients()
            if ingredients_df.empty:
                ingredient_options = ["No ingredients"]
            else:
                ingredient_options = ["Select Ingredient"] + [
                    f"{row['Ingredient_ID']} - {row['Ingredient_Name']} ({row['Unit']})" 
                    for _, row in ingredients_df.iterrows()
                ]
            
            # Ingredient dropdown
            ing_var = tk.StringVar(value=ingredient_options[0])
            ing_menu = ctk.CTkOptionMenu(row_frame, values=ingredient_options,
                                       variable=ing_var, width=200)
            ing_menu.pack(side="left", padx=5)
            
            # Quantity
            qty_entry = ctk.CTkEntry(row_frame, placeholder_text="Qty", width=70)
            qty_entry.pack(side="left", padx=5)
            
            # Unit conversion dropdown
            unit_var = tk.StringVar(value="")
            unit_menu = ctk.CTkOptionMenu(row_frame, values=[""], 
                                        variable=unit_var, width=70, state="disabled")
            unit_menu.pack(side="left", padx=5)
            
            # Base unit info
            base_label = ctk.CTkLabel(row_frame, text="", width=100, 
                                     font=("Arial", 9), text_color="gray")
            base_label.pack(side="left", padx=5)
            
            # Remove button
            remove_btn = ctk.CTkButton(row_frame, text="❌", width=30, height=30,
                                      command=lambda: row_frame.destroy(),
                                      fg_color="#e74c3c", hover_color="#c0392b")
            remove_btn.pack(side="left", padx=5)
            
            # Store data
            ingredient_data = {
                'frame': row_frame,
                'ing_var': ing_var,
                'qty_entry': qty_entry,
                'unit_var': unit_var,
                'unit_menu': unit_menu,
                'base_label': base_label,
                'base_unit': ""
            }
            popup_ingredients.append(ingredient_data)
            
            def update_unit_options(*args):
                """Update unit options when ingredient is selected"""
                selected = ing_var.get()
                if selected != "Select Ingredient" and " - " in selected:
                    # Extract unit from parentheses
                    if "(" in selected and ")" in selected:
                        base_unit = selected.split("(")[1].split(")")[0]
                        ingredient_data['base_unit'] = base_unit
                        
                        # Set up unit options based on base unit
                        if base_unit in ['kg', 'g', 'mg']:
                            units = ['kg', 'g', 'mg']
                        elif base_unit in ['L', 'ml']:
                            units = ['L', 'ml']
                        elif base_unit in ['pcs', 'dozen', 'pack']:
                            units = ['pcs', 'dozen', 'pack']
                        else:
                            units = [base_unit]
                        
                        unit_menu.configure(values=units, state="normal")
                        unit_var.set(base_unit)  # Default to base unit
            
            ing_var.trace_add("write", update_unit_options)
            
            def update_conversion(*args):
                """Update conversion display"""
                qty_text = qty_entry.get()
                selected_unit = unit_var.get()
                base_unit = ingredient_data.get('base_unit', '')
                
                if qty_text and selected_unit and base_unit:
                    try:
                        qty = float(qty_text)
                        # Convert to base unit
                        conversions = {
                            ('kg', 'g'): 1000,
                            ('kg', 'mg'): 1000000,
                            ('g', 'kg'): 0.001,
                            ('g', 'mg'): 1000,
                            ('mg', 'g'): 0.001,
                            ('mg', 'kg'): 0.000001,
                            ('L', 'ml'): 1000,
                            ('ml', 'L'): 0.001,
                            ('dozen', 'pcs'): 12,
                            ('pcs', 'dozen'): 1/12
                        }
                        
                        if (selected_unit, base_unit) in conversions:
                            factor = conversions[(selected_unit, base_unit)]
                            base_qty = qty * factor
                            base_label.configure(
                                text=f"= {base_qty:,.3f} {base_unit}",
                                text_color="blue"
                            )
                            ingredient_data['base_qty'] = base_qty
                        else:
                            base_label.configure(text="")
                            ingredient_data['base_qty'] = qty
                    except ValueError:
                        base_label.configure(text="Invalid")
            
            unit_var.trace_add("write", update_conversion)
            qty_entry.bind("<KeyRelease>", lambda e: update_conversion())
            
            # Initial update
            update_unit_options()
        
        # Add first row
        add_ingredient_row()
        
        # Add more ingredient button
        ctk.CTkButton(popup, text="➕ Add Another Ingredient",
                     command=add_ingredient_row,
                     fg_color="#3498db", hover_color="#2980b9").pack(pady=10)
        
        # Notes
        notes_frame = ctk.CTkFrame(popup)
        notes_frame.pack(fill="x", padx=50, pady=10)
        
        ctk.CTkLabel(notes_frame, text="Notes:", 
                    font=("Arial", 12)).pack(anchor="w", pady=5)
        
        notes_text = ctk.CTkTextbox(notes_frame, height=60)
        notes_text.pack(fill="x", pady=5)
        
        # Status label
        status_label = ctk.CTkLabel(popup, text="", font=("Arial", 12))
        status_label.pack(pady=10)
        
        def save_recipe():
            """Save recipe from popup"""
            try:
                # Get selected product
                selection = product_var.get()
                if " - " not in selection:
                    status_label.configure(text="Select a product", text_color="red")
                    return
                
                product_id = selection.split(" - ")[0]
                
                # Collect ingredients
                recipe_items = []
                for ing_data in popup_ingredients:
                    if not ing_data['frame'].winfo_exists():
                        continue
                    
                    ing_selection = ing_data['ing_var'].get()
                    qty_text = ing_data['qty_entry'].get()
                    
                    if ing_selection == "Select Ingredient" or not qty_text:
                        continue
                    
                    # Get ingredient ID
                    if " - " in ing_selection:
                        ing_id = ing_selection.split(" - ")[0]
                        
                        try:
                            # Use converted quantity if available
                            if 'base_qty' in ing_data:
                                quantity = ing_data['base_qty']
                            else:
                                quantity = float(qty_text)
                            
                            if quantity <= 0:
                                status_label.configure(text="Quantity must be positive", 
                                                     text_color="red")
                                return
                            
                            recipe_items.append({
                                'ingredient_id': ing_id,
                                'quantity': quantity
                            })
                        except ValueError:
                            status_label.configure(text="Invalid quantity", 
                                                 text_color="red")
                            return
                
                if not recipe_items:
                    status_label.configure(text="Add at least one ingredient", 
                                         text_color="red")
                    return
                
                # Check if recipe exists
                existing = self.db.get_product_recipes(product_id)
                if not existing.empty:
                    confirm = messagebox.askyesno("Recipe Exists", 
                        f"Recipe already exists for {selection.split(' - ')[1]}.\nOverwrite?")
                    if not confirm:
                        return
                
                # Save recipe
                success = self.db.save_recipe(product_id, recipe_items)
                
                if success:
                    status_label.configure(text="✅ Recipe saved!", text_color="green")
                    # Update costs
                    self.db.update_all_product_costs()
                    # Refresh recipes view
                    self.refresh_all_recipes()
                    # Close popup after 2 seconds
                    popup.after(2000, popup.destroy)
                else:
                    status_label.configure(text="❌ Failed to save", text_color="red")
                    
            except Exception as e:
                status_label.configure(text=f"Error: {str(e)}", text_color="red")
        
        # Buttons
        button_frame = ctk.CTkFrame(popup)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame, text="💾 Save Recipe",
                     command=save_recipe,
                     fg_color="#27ae60", hover_color="#219653",
                     width=150).pack(side="left", padx=10)
        
        ctk.CTkButton(button_frame, text="Cancel",
                     command=popup.destroy,
                     width=150).pack(side="left", padx=10)
    
    def refresh_all_recipes(self):
        """Refresh all recipes"""
        if hasattr(self, 'recipe_search_var'):
            self.recipe_search_var.set("")
        if hasattr(self, 'recipe_category_var'):
            self.recipe_category_var.set("All Categories")
        self.refresh_recipes_view()

    def clear_recipe_filters(self):
        """Clear all recipe filters"""
        if hasattr(self, 'recipe_search_var'):
            self.recipe_search_var.set("")
        if hasattr(self, 'recipe_category_var'):
            self.recipe_category_var.set("All Categories")
        self.refresh_recipes_view()
    
    def refresh_recipes_view(self):
        """Refresh the recipes display"""
        # Check if recipes_display_container exists
        if not hasattr(self, 'recipes_display_container') or self.recipes_display_container is None:
            print("⚠️ recipes_display_container not initialized yet")
            return
        
        # Clear existing display
        for widget in self.recipes_display_container.winfo_children():
            widget.destroy()
        
        # Get all products
        products_df = self.db.get_all_products()
        
        if products_df.empty:
            ctk.CTkLabel(self.recipes_display_container, 
                        text="No products found. Add products first.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # ===== APPLY FILTERS =====
        
        # 1. Apply search filter
        search_text = self.recipe_search_var.get().lower()
        if search_text:
            mask = (products_df['Product_Name'].str.lower().str.contains(search_text) |
                   products_df['Product_ID'].str.lower().str.contains(search_text))
            products_df = products_df[mask]
        
        # 2. Apply category filter
        selected_category = self.recipe_category_var.get()
        if selected_category and selected_category != "All Categories":
            if 'Category' in products_df.columns:
                # Create a copy to avoid warnings
                products_df = products_df.copy()
                
                # Fill NaN categories with empty string
                products_df['Category'] = products_df['Category'].fillna('')
                
                # Convert all categories to string and strip whitespace
                products_df['Category'] = products_df['Category'].astype(str).str.strip()
                
                # Case-insensitive filtering
                mask = products_df['Category'].str.lower() == selected_category.lower().strip()
                products_df = products_df[mask]
        
        # ===== DISPLAY FILTER SUMMARY =====
        
        # Create filter summary frame
        filter_summary_frame = ctk.CTkFrame(self.recipes_display_container, 
                                          fg_color="#f8f9fa",  # Light background
                                          corner_radius=8)
        filter_summary_frame.pack(fill="x", padx=10, pady=10)
        
        # Build summary parts
        summary_parts = []
        
        if search_text:
            summary_parts.append(f"Search: '{search_text}'")
        
        if selected_category and selected_category != "All Categories":
            summary_parts.append(f"Category: '{selected_category}'")
        
        summary_text = f"📊 Showing {len(products_df)} products"
        if summary_parts:
            summary_text += f" • {' • '.join(summary_parts)}"
        
        # Create label with proper colors
        ctk.CTkLabel(filter_summary_frame, text=summary_text,
                    font=("Arial", 12),
                    text_color="#333333",      # Dark gray text
                    fg_color="#f8f9fa",        # Match frame background
                    bg_color="#f8f9fa").pack(pady=8, padx=10)
        
        if products_df.empty:
            # Show filter info
            no_results_text = "No products found"
            if summary_parts:
                no_results_text += f" with filters: {' • '.join(summary_parts)}"
            no_results_text += "."
            
            ctk.CTkLabel(self.recipes_display_container, 
                        text=no_results_text,
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Create scrollable frame for products
        scroll_frame = ctk.CTkScrollableFrame(self.recipes_display_container, 
                                             width=850, height=500)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Display each product
        for _, product in products_df.iterrows():
            product_frame = ctk.CTkFrame(scroll_frame, border_width=1, 
                                        border_color="gray", corner_radius=10)
            product_frame.pack(fill="x", pady=8, padx=5)
            
            # Product header
            header_frame = ctk.CTkFrame(product_frame, fg_color="#2c3e50", 
                                       corner_radius=10)
            header_frame.pack(fill="x", padx=5, pady=5)
            
            # Product info
            product_info = f"{product['Product_Name']} ({product['Product_ID']})"
            ctk.CTkLabel(header_frame, 
                        text=product_info,
                        font=("Arial", 14, "bold"),
                        text_color="white").pack(side="left", padx=15, pady=8)
            
            # Price
            price = product.get('Selling_Price', 0)
            price_info = f"Price: {self.config['currency']}{price:,.2f}"
            ctk.CTkLabel(header_frame, 
                        text=price_info,
                        font=("Arial", 12),
                        text_color="white").pack(side="right", padx=15, pady=8)
            
            # Get recipe for this product
            try:
                recipe_items = self.db.get_product_recipes(product['Product_ID'])
            except Exception as e:
                print(f"Error getting recipe: {e}")
                recipe_items = pd.DataFrame()
            
            if recipe_items.empty:
                ctk.CTkLabel(product_frame, text="No recipe defined",
                            text_color="gray", font=("Arial", 12)).pack(pady=20)
                
                # Create recipe button
                ctk.CTkButton(product_frame, text="➕ Create Recipe",
                             command=lambda pid=product['Product_ID']: self.open_create_recipe_popup(),
                             fg_color="#27ae60", hover_color="#219653",
                             height=30).pack(pady=10)
            else:
                # Display recipe
                table_frame = ctk.CTkFrame(product_frame)
                table_frame.pack(fill="x", padx=15, pady=10)
                
                # Table headers
                headers = ["Ingredient", "Quantity", "Unit", "Cost/Unit", "Total Cost"]
                col_widths = [180, 100, 80, 100, 120]
                
                for col, (header, width) in enumerate(zip(headers, col_widths)):
                    ctk.CTkLabel(table_frame, text=header, font=("Arial", 11, "bold"),
                                width=width).grid(row=0, column=col, padx=5, pady=5, sticky="w")
                
                # Add recipe items
                total_recipe_cost = 0
                for row_idx, (_, item) in enumerate(recipe_items.iterrows(), start=1):
                    ingredient_name = item.get('Ingredient_Name', item['Ingredient_ID'])
                    quantity = item.get('Quantity_Required', 0)
                    unit = item.get('Unit', '')
                    cost_per_unit = item.get('Cost_Per_Unit', 0)
                    item_cost = cost_per_unit * quantity
                    total_recipe_cost += item_cost
                    
                    # Display row
                    ctk.CTkLabel(table_frame, text=ingredient_name, 
                                width=col_widths[0]).grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
                    ctk.CTkLabel(table_frame, text=f"{quantity:,.3f}", 
                                width=col_widths[1]).grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
                    ctk.CTkLabel(table_frame, text=unit, 
                                width=col_widths[2]).grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
                    ctk.CTkLabel(table_frame, text=f"{self.config['currency']}{cost_per_unit:,.2f}", 
                                width=col_widths[3]).grid(row=row_idx, column=3, padx=5, pady=2, sticky="w")
                    ctk.CTkLabel(table_frame, text=f"{self.config['currency']}{item_cost:,.2f}", 
                                width=col_widths[4]).grid(row=row_idx, column=4, padx=5, pady=2, sticky="w")
                
                # Show total cost and profit
                total_frame = ctk.CTkFrame(product_frame, fg_color="black", 
                                          corner_radius=10)
                total_frame.pack(fill="x", padx=15, pady=10)
                
                # Total cost
                total_cost_label = ctk.CTkLabel(total_frame, 
                    text=f"Total Cost: {self.config['currency']}{total_recipe_cost:,.2f}",
                    font=("Arial", 12, "bold"))
                total_cost_label.pack(side="left", padx=15, pady=8)
                
                # Profit calculation
                selling_price = product.get('Selling_Price', 0)
                profit = selling_price - total_recipe_cost
                profit_margin = (profit / selling_price * 100) if selling_price > 0 else 0
                
                profit_color = "green" if profit >= 0 else "red"
                profit_label = ctk.CTkLabel(total_frame, 
                    text=f"Profit: {self.config['currency']}{profit:,.2f} ({profit_margin:.1f}%)",
                    font=("Arial", 12, "bold"),
                    text_color=profit_color)
                profit_label.pack(side="right", padx=15, pady=8)
                
                # Recipe actions
                actions_frame = ctk.CTkFrame(product_frame)
                actions_frame.pack(pady=10, padx=15)
                
                # Add Edit button
                ctk.CTkButton(actions_frame, text="✏️ Edit Recipe",
                             command=lambda pid=product['Product_ID']: self.edit_existing_recipe_popup(pid),
                             fg_color="#3498db", hover_color="#2980b9",
                             width=120).pack(side="left", padx=5)
                
                # Keep Delete button
                ctk.CTkButton(actions_frame, text="🗑️ Delete",
                             command=lambda pid=product['Product_ID']: self.delete_recipe_confirmation(pid),
                             fg_color="#e74c3c", hover_color="#c0392b",
                             width=120).pack(side="left", padx=5)
    
    def open_create_recipe_for_product(self, product_id):
        """Open create recipe popup for specific product"""
        # This is similar to open_create_recipe_popup but pre-selects the product
        self.open_create_recipe_popup()  # For now, use general popup
    
    def edit_recipe_popup(self, product_id):
        """Edit recipe popup"""
        # Similar to create popup but loads existing data
        messagebox.showinfo("Edit Recipe", 
                          f"To edit recipe for {product_id}, please use the Create Recipe tab.")
    
    def delete_recipe_confirmation(self, product_id):
        """Delete recipe"""
        confirm = messagebox.askyesno("Delete Recipe", 
                                     f"Delete recipe for {product_id}?")
        if confirm:
            success = self.db.save_recipe(product_id, [])
            if success:
                messagebox.showinfo("Success", "Recipe deleted")
                self.refresh_all_recipes()
            else:
                messagebox.showerror("Error", "Failed to delete")
    
    def create_recipe_form(self, parent_frame):
        """Create Recipe tab form"""
        ctk.CTkLabel(parent_frame, text="Create Recipe", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Instructions
        ctk.CTkLabel(parent_frame, 
                    text="Use the 'Create New Recipe' button in View Recipes tab,\n"
                         "or select a product below:",
                    font=("Arial", 12),
                    text_color="gray").pack(pady=10)
        
        # Product selection
        product_frame = ctk.CTkFrame(parent_frame)
        product_frame.pack(fill="x", padx=50, pady=20)
        
        ctk.CTkLabel(product_frame, text="Or select product:", 
                    font=("Arial", 14)).pack(pady=5)
        
        products_df = self.db.get_all_products()
        if products_df.empty:
            ctk.CTkLabel(product_frame, text="No products available.",
                        text_color="red").pack(pady=10)
            return
        
        product_options = [f"{row['Product_ID']} - {row['Product_Name']}" 
                          for _, row in products_df.iterrows()]
        
        product_var = ctk.StringVar(value=product_options[0])
        product_menu = ctk.CTkOptionMenu(product_frame, 
                                        values=product_options,
                                        variable=product_var,
                                        width=350)
        product_menu.pack(pady=10)
        
        # Create button for selected product
        ctk.CTkButton(product_frame, text="Create Recipe for Selected Product",
                     command=lambda: self.open_create_recipe_for_selected(product_var.get()),
                     fg_color="#3498db", hover_color="#2980b9",
                     height=40).pack(pady=20)
    
    def open_create_recipe_for_selected(self, product_selection):
        """Open create recipe for selected product"""
        if " - " in product_selection:
            product_id = product_selection.split(" - ")[0]
            self.open_create_recipe_popup()  # Would need to pre-select
    
    def show_cost_analysis(self, parent_frame):
        """Show cost analysis - FIXED"""
        ctk.CTkLabel(parent_frame, text="Cost Analysis", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Button frame
        btn_frame = ctk.CTkFrame(parent_frame)
        btn_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(btn_frame, text="🔄 Calculate All Costs",
                     command=lambda: self.calculate_and_show_costs(parent_frame),
                     fg_color="#3498db", hover_color="#2980b9",
                     width=200).pack(pady=5)
        
        # Analysis frame
        self.cost_analysis_frame = ctk.CTkFrame(parent_frame)
        self.cost_analysis_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Initial load
        self.calculate_and_show_costs(parent_frame)
    
    def calculate_and_show_costs(self, parent_frame):
        """Calculate and show costs - FIXED"""
        # Clear frame
        for widget in self.cost_analysis_frame.winfo_children():
            widget.destroy()
        
        # Get all products
        products_df = self.db.get_all_products()
        
        if products_df.empty:
            ctk.CTkLabel(self.cost_analysis_frame, 
                        text="No products found in database.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Update costs for all products
        products_df = self.db.update_all_product_costs()
        
        if products_df.empty:
            ctk.CTkLabel(self.cost_analysis_frame, 
                        text="Error calculating costs.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Filter out products without cost data
        products_df = products_df[products_df['Cost_Price'].notna()]
        
        if products_df.empty:
            ctk.CTkLabel(self.cost_analysis_frame, 
                        text="No products with cost data available.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self.cost_analysis_frame, 
                                             width=900, height=400)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Table headers
        headers = ["Product", "Selling Price", "Cost Price", "Profit", "Margin %", "Status"]
        col_widths = [200, 120, 120, 120, 100, 100]
        
        for col, (header, width) in enumerate(zip(headers, col_widths)):
            ctk.CTkLabel(scroll_frame, text=header, font=("Arial", 12, "bold"),
                        width=width).grid(row=0, column=col, padx=5, pady=5, sticky="w")
        
        # Calculate totals
        total_products = len(products_df)
        total_profit = 0
        profitable_count = 0
        
        # Add product rows
        for row_idx, (_, product) in enumerate(products_df.iterrows(), start=1):
            product_name = product['Product_Name']
            selling_price = product.get('Selling_Price', 0)
            cost_price = product.get('Cost_Price', 0)
            profit = product.get('Profit_Margin', selling_price - cost_price)
            margin = product.get('Margin_Percentage', 0)
            
            if pd.isna(margin):
                margin = (profit / selling_price * 100) if selling_price > 0 else 0
            
            # Product name
            ctk.CTkLabel(scroll_frame, text=product_name[:25], 
                        width=col_widths[0]).grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
            
            # Selling price
            ctk.CTkLabel(scroll_frame, text=f"{self.config['currency']}{selling_price:,.2f}", 
                        width=col_widths[1]).grid(row=row_idx, column=1, padx=5, pady=2)
            
            # Cost price
            ctk.CTkLabel(scroll_frame, text=f"{self.config['currency']}{cost_price:,.2f}", 
                        width=col_widths[2]).grid(row=row_idx, column=2, padx=5, pady=2)
            
            # Profit
            profit_color = "green" if profit >= 0 else "red"
            ctk.CTkLabel(scroll_frame, text=f"{self.config['currency']}{profit:,.2f}", 
                        text_color=profit_color,
                        width=col_widths[3]).grid(row=row_idx, column=3, padx=5, pady=2)
            
            # Margin percentage
            if margin >= 30:
                margin_color = "green"
                status = "Good"
            elif margin >= 20:
                margin_color = "#f39c12"
                status = "Fair"
            elif margin > 0:
                margin_color = "orange"
                status = "Low"
            else:
                margin_color = "red"
                status = "Loss"
            
            margin_text = f"{margin:.1f}%"
            ctk.CTkLabel(scroll_frame, text=margin_text, text_color=margin_color,
                        width=col_widths[4]).grid(row=row_idx, column=4, padx=5, pady=2)
            
            # Status badge
            status_frame = ctk.CTkFrame(scroll_frame, width=col_widths[5]-10, 
                                       height=25, corner_radius=10,
                                       fg_color=margin_color)
            status_frame.grid(row=row_idx, column=5, padx=5, pady=2)
            status_frame.pack_propagate(False)
            ctk.CTkLabel(status_frame, text=status, 
                        text_color="white", font=("Arial", 10)).pack(expand=True)
            
            # Update totals
            total_profit += profit
            if profit > 0:
                profitable_count += 1
        
        # Summary
        avg_margin = sum(products_df.get('Margin_Percentage', 0)) / total_products
        
        summary_frame = ctk.CTkFrame(parent_frame)
        summary_frame.pack(pady=10, padx=20, fill="x")
        
        summary_text = (
            f"📊 Summary: {total_products} Products | "
            f"💰 Total Profit: {self.config['currency']}{total_profit:,.2f} | "
            f"📈 Profitable: {profitable_count}/{total_products} | "
            f"📊 Avg Margin: {avg_margin:.1f}%"
        )
        
        ctk.CTkLabel(summary_frame, text=summary_text,
                    font=("Arial", 12, "bold")).pack(pady=10)