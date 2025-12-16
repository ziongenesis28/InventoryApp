# products_gui.py - All product-related GUI code
import customtkinter as ctk
import pandas as pd
import tkinter as tk
from tkinter import messagebox, simpledialog


class ProductsGUI:
    def __init__(self, window, db, config):
        self.window = window
        self.db = db
        self.config = config
        self.main_content = None  # Will be set later

    def clear_main_content(self):
        """Clear the main content area"""
        if self.main_content:  # Check if it exists
            for widget in self.main_content.winfo_children():
                widget.destroy()

    def show_products_management(self, main_content_frame):
        """Show products management interface"""
        self.main_content = main_content_frame
        self.clear_main_content()

        # Create tabview for products
        products_tabs = ctk.CTkTabview(self.main_content)
        products_tabs.pack(fill="both", expand=True, padx=20, pady=20)

        # Add tabs
        products_tabs.add("View Products")
        products_tabs.add("Add Product")

        # Fill each tab
        self.show_all_products(products_tabs.tab("View Products"))
        self.create_product_form_fixed(products_tabs.tab("Add Product"))

    def show_all_products(self, parent_frame):
        """Show all products in a table"""
        ctk.CTkLabel(parent_frame, text="All Products",
                     font=("Arial", 22, "bold")).pack(pady=10)

        # Filter & Sort Frame
        filter_frame = ctk.CTkFrame(parent_frame)
        filter_frame.pack(pady=10, padx=10, fill="x")

        # Row 1: Search
        search_row = ctk.CTkFrame(filter_frame, fg_color="transparent")
        search_row.pack(fill="x", pady=5)

        ctk.CTkLabel(search_row, text="Search:",
                     font=("Arial", 12)).pack(side="left", padx=10)

        self.product_search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(search_row,
                                   textvariable=self.product_search_var,
                                   placeholder_text="Search product name or ID...",
                                   width=300)
        search_entry.pack(side="left", padx=10)

        # Row 2: Sort Options
        sort_row = ctk.CTkFrame(filter_frame, fg_color="transparent")
        sort_row.pack(fill="x", pady=5)

        ctk.CTkLabel(sort_row, text="Sort by:",
                     font=("Arial", 12)).pack(side="left", padx=10)

        sort_options = [
            "Product Name (A-Z)",
            "Product Name (Z-A)",
            "Selling Price (High to Low)",
            "Selling Price (Low to High)",
            "Cost Price (High to Low)",
            "Cost Price (Low to High)",
            "Profit Margin (High to Low)",
            "Profit Margin (Low to High)",
            "Margin % (High to Low)",
            "Margin % (Low to High)",
            "Category (A-Z)",
            "Status (Active First)",
            "Status (Inactive First)"
        ]

        self.product_sort_var = tk.StringVar(value="Product Name (A-Z)")
        sort_menu = ctk.CTkOptionMenu(sort_row,
                                     values=sort_options,
                                     variable=self.product_sort_var,
                                     width=250)
        sort_menu.pack(side="left", padx=10)

        # Sort order button
        self.sort_ascending = True
        self.sort_order_btn = ctk.CTkButton(sort_row, text="↑ Asc",
                                           command=self.toggle_sort_order,
                                           width=80, height=28)
        self.sort_order_btn.pack(side="left", padx=5)

        # Row 3: Filters and Actions
        action_row = ctk.CTkFrame(filter_frame, fg_color="transparent")
        action_row.pack(fill="x", pady=5)

        # Status filter
        ctk.CTkLabel(action_row, text="Status:",
                     font=("Arial", 12)).pack(side="left", padx=10)

        self.status_filter_var = tk.StringVar(value="All Status")
        status_menu = ctk.CTkOptionMenu(action_row,
                                       values=["All Status", "Active Only", "Inactive Only"],
                                       variable=self.status_filter_var,
                                       width=120)
        status_menu.pack(side="left", padx=5)

        # Category filter
        ctk.CTkLabel(action_row, text="Category:",
                     font=("Arial", 12)).pack(side="left", padx=10)

        self.category_filter_var = tk.StringVar(value="All Categories")
        category_menu = ctk.CTkOptionMenu(action_row,
                                         values=["All Categories"],
                                         variable=self.category_filter_var,
                                         width=150)
        category_menu.pack(side="left", padx=5)

        # Apply Filters button
        ctk.CTkButton(action_row, text="🔍 Apply Filters",
                     command=self.refresh_products_table,
                     fg_color="#3498db", hover_color="#2980b9",
                     width=130).pack(side="left", padx=20)

        # Clear Filters button
        ctk.CTkButton(action_row, text="🗑️ Clear Filters",
                     command=self.clear_product_filters,
                     fg_color="#95a5a6", hover_color="#7f8c8d",
                     width=120).pack(side="left", padx=5)

        # Create frame for table
        self.products_table_frame = ctk.CTkFrame(parent_frame)
        self.products_table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Initial load
        self.refresh_products_table()

    def toggle_sort_order(self):
        """Toggle between ascending and descending sort order"""
        self.sort_ascending = not self.sort_ascending
        if self.sort_ascending:
            self.sort_order_btn.configure(text="↑ Asc")
        else:
            self.sort_order_btn.configure(text="↓ Desc")
        self.refresh_products_table()

    def clear_product_filters(self):
        """Clear all product filters"""
        self.product_search_var.set("")
        self.product_sort_var.set("Product Name (A-Z)")
        self.sort_ascending = True
        self.sort_order_btn.configure(text="↑ Asc")
        self.status_filter_var.set("All Status")
        self.category_filter_var.set("All Categories")
        self.refresh_products_table()

    def refresh_products_table(self):
        """Refresh the products table"""
        if not hasattr(self, 'products_table_frame'):
            return

        # Clear existing table
        for widget in self.products_table_frame.winfo_children():
            widget.destroy()

        # Get all products
        all_products_df = self.db.read_tab('Products')

        if all_products_df.empty:
            ctk.CTkLabel(self.products_table_frame, text="No products found in database.",
                        font=("Arial", 14)).pack(pady=50)
            return

        # Make a copy for filtering
        products_df = all_products_df.copy()

        # Update category filter options
        if hasattr(self, 'category_filter_var'):
            categories = ["All Categories"]
            if 'Category' in all_products_df.columns:
                unique_cats = all_products_df['Category'].dropna().unique()
                for cat in unique_cats:
                    if cat and str(cat).strip() and str(cat).strip().lower() != 'nan':
                        categories.append(str(cat).strip())

            categories = sorted(list(set(categories)))
            current_value = self.category_filter_var.get()
            if current_value not in categories:
                self.category_filter_var.set("All Categories")

        # Apply filters
        search_text = self.product_search_var.get().lower() if hasattr(self, 'product_search_var') else ""
        if search_text:
            mask = (products_df['Product_Name'].str.lower().str.contains(search_text) |
                   products_df['Product_ID'].str.lower().str.contains(search_text))
            products_df = products_df[mask]

        status_filter = self.status_filter_var.get() if hasattr(self, 'status_filter_var') else "All Status"
        if status_filter == "Active Only":
            if 'Active' in products_df.columns:
                products_df['Active'] = products_df['Active'].astype(str).str.upper()
                products_df = products_df[products_df['Active'].str.contains('YES|TRUE|1', na=False)]
        elif status_filter == "Inactive Only":
            if 'Active' in products_df.columns:
                products_df['Active'] = products_df['Active'].astype(str).str.upper()
                products_df = products_df[~products_df['Active'].str.contains('YES|TRUE|1', na=False)]

        category_filter = self.category_filter_var.get() if hasattr(self, 'category_filter_var') else "All Categories"
        if category_filter != "All Categories" and 'Category' in products_df.columns:
            products_df['Category'] = products_df['Category'].fillna('Uncategorized')
            products_df = products_df[products_df['Category'] == category_filter]

        # Apply sorting
        sort_by = self.product_sort_var.get() if hasattr(self, 'product_sort_var') else "Product Name (A-Z)"

        sort_mapping = {
            "Product Name (A-Z)": ("Product_Name", True),
            "Product Name (Z-A)": ("Product_Name", False),
            "Selling Price (High to Low)": ("Selling_Price", False),
            "Selling Price (Low to High)": ("Selling_Price", True),
            "Cost Price (High to Low)": ("Cost_Price", False),
            "Cost Price (Low to High)": ("Cost_Price", True),
            "Profit Margin (High to Low)": ("Profit_Margin", False),
            "Profit Margin (Low to High)": ("Profit_Margin", True),
            "Margin % (High to Low)": ("Margin_Percentage", False),
            "Margin % (Low to High)": ("Margin_Percentage", True),
            "Category (A-Z)": ("Category", True),
            "Status (Active First)": ("Active", False),
            "Status (Inactive First)": ("Active", True)
        }

        if sort_by in sort_mapping:
            sort_column, default_ascending = sort_mapping[sort_by]

            if sort_column in products_df.columns:
                ascending = self.sort_ascending if sort_by in ["Product Name (A-Z)", "Product Name (Z-A)",
                                                             "Selling Price (High to Low)", "Selling Price (Low to High)",
                                                             "Cost Price (High to Low)", "Cost Price (Low to High)",
                                                             "Profit Margin (High to Low)", "Profit Margin (Low to High)",
                                                             "Margin % (High to Low)", "Margin % (Low to High)",
                                                             "Category (A-Z)"] else default_ascending

                if sort_column == "Active":
                    products_df['_Active_Sort'] = products_df['Active'].astype(str).str.upper().map({
                        'YES': 1, 'TRUE': 1, '1': 1, 'NO': 2, 'FALSE': 2, '0': 2
                    }).fillna(3)
                    sort_column = '_Active_Sort'

                products_df = products_df.sort_values(by=sort_column, ascending=ascending)

                if '_Active_Sort' in products_df.columns:
                    products_df = products_df.drop('_Active_Sort', axis=1)

        if products_df.empty:
            filter_info = []
            if search_text:
                filter_info.append(f"Search: '{search_text}'")
            if status_filter != "All Status":
                filter_info.append(f"Status: '{status_filter}'")
            if category_filter != "All Categories":
                filter_info.append(f"Category: '{category_filter}'")

            no_results_text = "No products found"
            if filter_info:
                no_results_text += f" with filters: {' • '.join(filter_info)}"
            no_results_text += "."

            ctk.CTkLabel(self.products_table_frame, text=no_results_text,
                        font=("Arial", 14)).pack(pady=50)
            return

        # Display filter summary
        filter_summary_frame = ctk.CTkFrame(self.products_table_frame,
                                          fg_color="#ecf0f1",
                                          corner_radius=8)
        filter_summary_frame.pack(fill="x", padx=10, pady=10)

        summary_parts = []

        if search_text:
            summary_parts.append(f"Search: '{search_text}'")

        status_filter = self.status_filter_var.get() if hasattr(self, 'status_filter_var') else "All Status"
        if status_filter != "All Status":
            summary_parts.append(f"Status: '{status_filter}'")

        category_filter = self.category_filter_var.get() if hasattr(self, 'category_filter_var') else "All Categories"
        if category_filter != "All Categories":
            summary_parts.append(f"Category: '{category_filter}'")

        sort_by = self.product_sort_var.get() if hasattr(self, 'product_sort_var') else "Product Name (A-Z)"
        sort_direction = "↑ Asc" if self.sort_ascending else "↓ Desc"
        summary_parts.append(f"Sort: {sort_by} ({sort_direction})")

        summary_text = f"📊 Showing {len(products_df)} products"
        if summary_parts:
            summary_text += f" • {' • '.join(summary_parts)}"

        ctk.CTkLabel(filter_summary_frame, text=summary_text,
                    font=("Arial", 12),
                    text_color="black").pack(pady=8, padx=10)

        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self.products_table_frame, width=900, height=400)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Table headers
        headers = ["ID", "Product Name", "Category", "Selling Price", "Cost Price", "Margin %", "Status", "Actions"]
        col_widths = [80, 200, 120, 100, 100, 80, 80, 120]

        for col, (header, width) in enumerate(zip(headers, col_widths)):
            ctk.CTkLabel(scroll_frame, text=header, font=("Arial", 12, "bold"),
                        width=width).grid(row=0, column=col, padx=5, pady=5, sticky="w")

        # Add product rows
        for row_idx, (_, product) in enumerate(products_df.iterrows(), start=1):
            # ID
            ctk.CTkLabel(scroll_frame, text=product['Product_ID'],
                        width=col_widths[0]).grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")

            # Name
            ctk.CTkLabel(scroll_frame, text=product['Product_Name'],
                        width=col_widths[1]).grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")

            # Category
            category = product.get('Category', 'N/A')
            ctk.CTkLabel(scroll_frame, text=category,
                        width=col_widths[2]).grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")

            # Selling Price
            selling_price = product.get('Selling_Price', 0)
            ctk.CTkLabel(scroll_frame, text=f"{self.config['currency']}{selling_price:,.2f}",
                        width=col_widths[3]).grid(row=row_idx, column=3, padx=5, pady=2, sticky="w")

            # Cost Price
            cost_price = product.get('Cost_Price', 0)
            ctk.CTkLabel(scroll_frame, text=f"{self.config['currency']}{cost_price:,.2f}",
                        width=col_widths[4]).grid(row=row_idx, column=4, padx=5, pady=2, sticky="w")

            # Margin %
            margin = product.get('Margin_Percentage', 0)
            margin_color = "green" if margin >= 30 else "orange" if margin >= 10 else "red"
            margin_text = f"{margin:.1f}%" if pd.notna(margin) else "N/A"
            ctk.CTkLabel(scroll_frame, text=margin_text, text_color=margin_color,
                        width=col_widths[5]).grid(row=row_idx, column=5, padx=5, pady=2, sticky="w")

            # Status
            is_active = str(product.get('Active', 'Yes')).upper() == 'YES'
            status_text = "Active" if is_active else "Inactive"
            status_color = "green" if is_active else "red"

            status_frame = ctk.CTkFrame(scroll_frame, width=col_widths[6]-10,
                                       height=25, corner_radius=10,
                                       fg_color=status_color)
            status_frame.grid(row=row_idx, column=6, padx=5, pady=2)
            status_frame.pack_propagate(False)
            ctk.CTkLabel(status_frame, text=status_text,
                        text_color="white", font=("Arial", 10)).pack(expand=True)

            # Action buttons
            action_frame = ctk.CTkFrame(scroll_frame, width=col_widths[7], fg_color="transparent")
            action_frame.grid(row=row_idx, column=7, padx=5, pady=2)

            # View Recipe button
            ctk.CTkButton(
                action_frame,
                text="📝 Recipe",
                command=lambda pid=product['Product_ID']: self.view_product_recipe(pid),
                width=60,
                height=25,
                font=("Arial", 10)
            ).pack(side="left", padx=2)

            # Edit button
            ctk.CTkButton(
                action_frame,
                text="✏️ Edit",
                command=lambda pid=product['Product_ID']: self.edit_product_better_popup(pid),
                width=60,
                height=25,
                font=("Arial", 10)
            ).pack(side="left", padx=2)

    def edit_product_better_popup(self, product_id):
        """Improved popup for editing products with delete options"""
        # Get product data
        products_df = self.db.read_tab('Products')
        product_row = products_df[products_df['Product_ID'] == product_id]

        if product_row.empty:
            messagebox.showerror("Error", f"Product {product_id} not found")
            return

        product_data = product_row.iloc[0]
        product_name = product_data['Product_Name']
        is_active = str(product_data.get('Active', 'Yes')).upper() == 'YES'

        # Create popup window
        popup = ctk.CTkToplevel(self.window)
        popup.title(f"Edit Product: {product_name}")
        popup.geometry("700x900")
        popup.minsize(650, 850)
        popup.transient(self.window)
        popup.grab_set()

        # Center on screen
        popup.update_idletasks()
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = (screen_width - 700) // 2
        y = (screen_height - 900) // 2
        popup.geometry(f"+{x}+{y}")

        # Main container
        main_container = ctk.CTkFrame(popup)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Header
        header_frame = ctk.CTkFrame(main_container, fg_color="#2c3e50", corner_radius=10)
        header_frame.pack(fill="x", pady=10, padx=10)

        ctk.CTkLabel(header_frame,
                    text=f"Edit Product: {product_name}",
                    font=("Arial", 20, "bold"),
                    text_color="white").pack(pady=15)

        # Product info display
        info_frame = ctk.CTkFrame(main_container, fg_color="#ecf0f1", corner_radius=8)
        info_frame.pack(fill="x", pady=10, padx=10)

        # Product ID
        id_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        id_frame.pack(fill="x", pady=5, padx=20)
        ctk.CTkLabel(id_frame, text="Product ID:",
                    font=("Arial", 12, "bold"),
                    text_color="#2c3e50",
                    width=120).pack(side="left")
        ctk.CTkLabel(id_frame, text=product_id,
                    font=("Arial", 12, "bold"),
                    text_color="#1e3a8a").pack(side="left", padx=10)

        # Current status
        status_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        status_frame.pack(fill="x", pady=5, padx=20)
        ctk.CTkLabel(status_frame, text="Current Status:",
                    font=("Arial", 12, "bold"),
                    text_color="#2c3e50",
                    width=120).pack(side="left")

        status_text = "Active ✅" if is_active else "Inactive ⏸️"
        status_color = "green" if is_active else "orange"
        ctk.CTkLabel(status_frame, text=status_text,
                    font=("Arial", 12, "bold"),
                    text_color=status_color).pack(side="left", padx=10)

        # Create scrollable content area
        content_frame = ctk.CTkScrollableFrame(main_container, height=400)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Form fields
        fields = [
            ("Product Name*:", "Product_Name", "text"),
            ("Category:", "Category", "text"),
            ("Selling Price*:", "Selling_Price", "number"),
            ("Active (Yes/No):", "Active", "text")
        ]

        entries = {}
        for label_text, field_name, field_type in fields:
            field_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            field_frame.pack(fill="x", pady=12, padx=20)

            ctk.CTkLabel(field_frame, text=label_text,
                        font=("Arial", 12, "bold"),
                        text_color="#888888",
                        width=150).pack(side="left", padx=10)

            value = product_data.get(field_name, "")
            if pd.isna(value):
                value = ""

            if field_type == "text":
                entry = ctk.CTkEntry(field_frame, width=300, height=35)
                entry.insert(0, str(value))
            elif field_type == "number":
                entry = ctk.CTkEntry(field_frame, width=300, height=35)
                if value:
                    entry.insert(0, f"{float(value):.2f}")
                else:
                    entry.insert(0, "0.00")

            entry.pack(side="left", padx=10)
            entries[field_name] = entry

        # Notes field
        notes_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        notes_frame.pack(fill="x", pady=12, padx=20)

        ctk.CTkLabel(notes_frame, text="Notes:",
                    font=("Arial", 12, "bold"),
                    text_color="#888888",
                    width=150).pack(side="left", padx=10)

        notes_text = ctk.CTkTextbox(notes_frame, width=300, height=100)
        notes_value = product_data.get('Notes', '')
        if pd.notna(notes_value):
            notes_text.insert("1.0", str(notes_value))
        notes_text.pack(side="left", padx=10)

        # Status label
        status_label = ctk.CTkLabel(main_container, text="",
                                   font=("Arial", 12),
                                   text_color="#2c3e50")
        status_label.pack(pady=10)

        # ===== DELETE OPTIONS FRAME =====
        delete_frame = ctk.CTkFrame(main_container, fg_color="#fff5f5",
                                   border_width=2, border_color="#fecaca",
                                   corner_radius=10)
        delete_frame.pack(fill="x", pady=15, padx=55)

        ctk.CTkLabel(delete_frame, text="⚠️ DELETE OPTIONS",
                    font=("Arial", 14, "bold"),
                    text_color="#dc2626").pack(pady=10)

        # Delete buttons frame
        delete_buttons_frame = ctk.CTkFrame(delete_frame, fg_color="transparent")
        delete_buttons_frame.pack(pady=10, padx=20)

        # ===== BUTTON FUNCTIONS =====
        def mark_inactive():
            """Mark product as inactive (soft delete)"""
            confirm = messagebox.askyesno("Mark as Inactive",
                                        f"Mark '{product_name}' as INACTIVE?\n\n"
                                        "This will:\n"
                                        "• Hide from sales/cart\n"
                                        "• Keep in database\n"
                                        "• Can be reactivated later")
            if confirm:
                success, message = self.db.mark_product_inactive(product_id)
                if success:
                    messagebox.showinfo("Success", message)
                    # Refresh table and close popup
                    self.refresh_products_table()
                    popup.destroy()
                else:
                    messagebox.showerror("Error", message)

        def delete_permanently():
            """Permanently delete product from database"""
            # Double confirmation
            confirm1 = messagebox.askyesno("⚠️ PERMANENT DELETE - WARNING",
                                         f"PERMANENTLY DELETE '{product_name}'?\n\n"
                                         "This will:\n"
                                         "• Remove ALL data permanently\n"
                                         "• Delete any recipes for this product\n"
                                         "• Cannot be undone!\n\n"
                                         "Are you ABSOLUTELY sure?")

            if not confirm1:
                return

            # Final confirmation with typing
            confirm_text = simpledialog.askstring("FINAL CONFIRMATION",
                                                f"Type 'DELETE {product_id}' to confirm permanent deletion:")

            if confirm_text != f"DELETE {product_id}":
                messagebox.showinfo("Cancelled", "Deletion cancelled.")
                return

            try:
                # First check if product has recipes
                recipes = self.db.get_product_recipes(product_id)
                has_recipes = not recipes.empty

                if has_recipes:
                    recipe_count = len(recipes)
                    confirm2 = messagebox.askyesno("Delete Associated Recipes",
                                                 f"This product has {recipe_count} recipe(s).\n\n"
                                                 "Delete these recipes too?\n"
                                                 "(Required for permanent deletion)")
                    if not confirm2:
                        return

                # Perform deletion
                success, message = self.db.delete_product_permanently(product_id)

                if success:
                    messagebox.showinfo("✅ Success", message)
                    # Update product costs
                    self.db.update_all_product_costs()
                    # Refresh table and close
                    self.refresh_products_table()
                    popup.destroy()
                else:
                    messagebox.showerror("❌ Error", message)

            except Exception as e:
                messagebox.showerror("Error", f"Deletion failed: {str(e)}")

        def reactivate_product():
            """Reactivate an inactive product"""
            confirm = messagebox.askyesno("Reactivate Product",
                                        f"Reactivate '{product_name}'?\n\n"
                                        "This will make it available for sale again.")
            if confirm:
                success, message = self.db.reactivate_product(product_id)
                if success:
                    messagebox.showinfo("Success", message)
                    # Refresh table and close
                    self.refresh_products_table()
                    popup.destroy()
                else:
                    messagebox.showerror("Error", message)

        # ===== CREATE DELETE BUTTONS =====
        button_width = 140
        button_height = 45

        # First row for status toggle buttons
        status_row = ctk.CTkFrame(delete_buttons_frame, fg_color="transparent")
        status_row.pack(fill="x", pady=5)

        if is_active:
            # For active products: Show mark inactive button
            ctk.CTkButton(status_row, text="⏸️ Mark Inactive",
                         command=mark_inactive,
                         fg_color="#f39c12", hover_color="#e67e22",
                         width=button_width, height=button_height,
                         font=("Arial", 13)).pack(side="left", padx=15)
        else:
            # For inactive products: Show reactivate button
            ctk.CTkButton(status_row, text="✅ Reactivate",
                         command=reactivate_product,
                         fg_color="#3498db", hover_color="#2980b9",
                         width=button_width, height=button_height,
                         font=("Arial", 13)).pack(side="left", padx=15)

        # Second row for permanent delete
        delete_row = ctk.CTkFrame(delete_buttons_frame, fg_color="transparent")
        delete_row.pack(fill="x", pady=5)

        # Permanent delete button (always visible)
        ctk.CTkButton(delete_row, text="🗑️ PERMANENT DELETE",
                     command=delete_permanently,
                     fg_color="#e74c3c", hover_color="#c0392b",
                     width=button_width, height=button_height,
                     font=("Arial", 13, "bold")).pack(side="left", padx=15)

        # ===== SAVE/CANCEL BUTTONS FRAME =====
        buttons_frame = ctk.CTkFrame(main_container, height=120)
        buttons_frame.pack(fill="x", pady=10, padx=55)
        buttons_frame.pack_propagate(False)

        def save_changes():
            """Save the edited product"""
            try:
                # Get updated data
                updated_data = {}

                for field_name, entry in entries.items():
                    value = entry.get()

                    if field_name in ['Product_Name', 'Active'] and not value:
                        status_label.configure(
                            text=f"{field_name.replace('_', ' ')} is required",
                            text_color="red"
                        )
                        return

                    if field_name == 'Selling_Price':
                        try:
                            updated_data[field_name] = float(value)
                        except ValueError:
                            status_label.configure(
                                text="Selling Price must be a number",
                                text_color="red"
                            )
                            return
                    else:
                        updated_data[field_name] = value

                # Add notes
                updated_data['Notes'] = notes_text.get("1.0", "end-1c").strip()

                # Update in database
                success, message = self.db.update_product(product_id, updated_data)

                if success:
                    status_label.configure(text=f"✅ {message}", text_color="green")

                    # Update product costs
                    self.db.update_all_product_costs()

                    # Refresh the products table
                    self.refresh_products_table()

                    # Close popup after 1.5 seconds
                    popup.after(1500, popup.destroy)
                else:
                    status_label.configure(text=f"❌ {message}", text_color="red")

            except Exception as e:
                status_label.configure(text=f"Error: {str(e)}", text_color="red")

        # Top row: Save and Cancel
        top_row = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        top_row.pack(fill="x", pady=5)

        ctk.CTkButton(top_row, text="💾 Save Changes",
                     command=save_changes,
                     fg_color="#27ae60", hover_color="#219653",
                     width=button_width, height=button_height,
                     font=("Arial", 13, "bold")).pack(side="left", padx=15)

        ctk.CTkButton(top_row, text="Cancel",
                     command=popup.destroy,
                     width=button_width, height=button_height,
                     font=("Arial", 13, "bold")).pack(side="left", padx=15)

    def filter_products(self):
        """Filter products based on search text"""
        self.refresh_products_table()

    def view_product_recipe(self, product_id):
        """View recipe for a specific product"""
        # Get product info
        products_df = self.db.read_tab('Products')
        product_info = products_df[products_df['Product_ID'] == product_id]

        if product_info.empty:
            messagebox.showerror("Error", f"Product {product_id} not found")
            return

        product_name = product_info.iloc[0]['Product_Name']

        # Get recipe items
        recipe_items = self.db.get_product_recipes(product_id)

        if recipe_items.empty:
            messagebox.showinfo("No Recipe", f"Product '{product_name}' has no recipe defined.")
            return

        # Create popup window
        popup = ctk.CTkToplevel(self.window)
        popup.title(f"Recipe: {product_name}")
        popup.geometry("600x750")
        popup.minsize(450, 550)
        popup.transient(self.window)
        popup.grab_set()

        # Center the popup
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
                    text=f"Recipe for: {product_name}",
                    font=("Arial", 18, "bold"),
                    text_color="white").pack(pady=15)

        ctk.CTkLabel(title_frame,
                    text=f"Product ID: {product_id}",
                    font=("Arial", 12, "bold"),
                    text_color="#ecf0f1").pack(pady=5)

        # Create scrollable frame for recipe items
        scroll_frame = ctk.CTkScrollableFrame(main_container, height=300)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Headers
        headers_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        headers_frame.pack(fill="x", pady=5)

        headers = ["Ingredient", "Quantity", "Unit", "Cost"]
        widths = [180, 100, 80, 120]

        for header, width in zip(headers, widths):
            ctk.CTkLabel(headers_frame, text=header,
                        font=("Arial", 12, "bold"),
                        text_color="#888888",
                        width=width).pack(side="left", padx=5)

        # Display each ingredient
        total_cost = 0

        for _, item in recipe_items.iterrows():
            row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=3)

            # Ingredient name
            ingredient_name = item.get('Ingredient_Name', item['Ingredient_ID'])
            ctk.CTkLabel(row_frame, text=ingredient_name[:25],
                        width=widths[0],
                        text_color="#FFFFFF").pack(side="left", padx=5)

            # Quantity - convert to appropriate unit
            quantity = item.get('Quantity_Required', 0)
            unit = item.get('Unit', '')

            # Convert to more readable units
            display_quantity = quantity
            display_unit = unit

            if unit == 'kg' and quantity < 1:
                display_quantity = quantity * 1000
                display_unit = 'g'
            elif unit == 'L' and quantity < 1:
                display_quantity = quantity * 1000
                display_unit = 'ml'

            # Format quantity nicely
            if display_quantity.is_integer():
                quantity_text = f"{display_quantity:.0f}"
            else:
                quantity_text = f"{display_quantity:.3f}".rstrip('0').rstrip('.')

            ctk.CTkLabel(row_frame, text=quantity_text,
                        width=widths[1],
                        text_color="#FFFFFF").pack(side="left", padx=5)

            # Unit
            ctk.CTkLabel(row_frame, text=display_unit,
                        width=widths[2],
                        text_color="#FFFFFF").pack(side="left", padx=5)

            # Cost
            cost_per_unit = item.get('Cost_Per_Unit', 0)
            item_cost = cost_per_unit * quantity
            total_cost += item_cost

            ctk.CTkLabel(row_frame,
                        text=f"{self.config['currency']}{item_cost:.2f}",
                        width=widths[3],
                        text_color="#8bca84").pack(side="left", padx=5)

        # Total cost
        total_frame = ctk.CTkFrame(main_container, fg_color="#ecf0f1", corner_radius=8)
        total_frame.pack(fill="x", pady=10, padx=10)

        ctk.CTkLabel(total_frame,
                    text=f"Total Recipe Cost: {self.config['currency']}{total_cost:.2f}",
                    font=("Arial", 14, "bold"),
                    text_color="#2c3e50").pack(pady=10)

        # Get product selling price for profit calculation
        selling_price = product_info.iloc[0].get('Selling_Price', 0)
        if selling_price > 0:
            profit = selling_price - total_cost
            profit_margin = (profit / selling_price * 100) if selling_price > 0 else 0

            profit_color = "#27ae60" if profit >= 0 else "#e74c3c"

            profit_frame = ctk.CTkFrame(main_container, fg_color="#f8f9f9", corner_radius=8)
            profit_frame.pack(fill="x", pady=5, padx=10)

            profit_text = f"Profit: {self.config['currency']}{profit:.2f} ({profit_margin:.1f}%)"
            ctk.CTkLabel(profit_frame, text=profit_text,
                        font=("Arial", 12, "bold"),
                        text_color=profit_color).pack(pady=8)

        # Close button
        button_frame = ctk.CTkFrame(main_container)
        button_frame.pack(pady=20, fill="x", padx=20)

        ctk.CTkButton(button_frame, text="✕ Close",
                     command=popup.destroy,
                     width=200, height=45,
                     font=("Arial", 14, "bold"),
                     fg_color="#3498db",
                     hover_color="#2980b9").pack(pady=10)

    def create_product_form_fixed(self, parent_frame):
        """Form to add new product - FIXED VERSION"""
        ctk.CTkLabel(parent_frame, text="Add New Product",
                    font=("Arial", 22, "bold")).pack(pady=10)

        # Form frame
        form_frame = ctk.CTkFrame(parent_frame)
        form_frame.pack(pady=20, padx=50, fill="x")

        # Auto-generate ID
        new_id = self.db.generate_product_id()
        ctk.CTkLabel(form_frame, text=f"Product ID: {new_id}",
                    font=("Arial", 14, "bold")).pack(pady=5)

        # Store the generated ID
        self.generated_product_id = new_id

        # Form fields - ALL FIELDS EXCEPT CATEGORY
        fields = [
            ("Product Name*:", "product_name", "text"),
            ("Selling Price*:", "selling_price", "number"),
            ("Active (Yes/No):", "active", "text")
        ]

        self.product_form_entries = {}

        for label_text, field_name, field_type in fields:
            row_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=8)

            ctk.CTkLabel(row_frame, text=label_text,
                        width=150, anchor="w").pack(side="left", padx=10)

            if field_type == "text":
                entry = ctk.CTkEntry(row_frame, width=250)
                # Set default values
                if field_name == "active":
                    entry.insert(0, "Yes")
            elif field_type == "number":
                entry = ctk.CTkEntry(row_frame, width=250)
                if field_name == "selling_price":
                    entry.insert(0, "0.00")

            entry.pack(side="left", padx=10)
            self.product_form_entries[field_name] = entry

        # ===== SPECIAL CATEGORY FIELD WITH DROPDOWN =====
        category_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        category_row.pack(fill="x", pady=8)

        ctk.CTkLabel(category_row, text="Category:",
                    width=150, anchor="w").pack(side="left", padx=10)

        # Get existing categories from database
        products_df = self.db.read_tab('Products')
        categories = ["General"]  # Default value
        
        if 'Category' in products_df.columns:
            # Get all unique categories, remove empty ones
            unique_cats = products_df['Category'].dropna().unique()
            for cat in unique_cats:
                cat_str = str(cat).strip()
                if cat_str and cat_str.lower() != 'nan':
                    categories.append(cat_str)
        
        # Remove duplicates and sort
        categories = sorted(list(set(categories)))
        
        # Create dropdown for category
        self.category_dropdown_var = tk.StringVar(value="General")
        self.category_dropdown = ctk.CTkOptionMenu(
            category_row,
            values=categories,
            variable=self.category_dropdown_var,
            width=200,
            height=35,
            dropdown_font=("Arial", 11)
        )
        self.category_dropdown.pack(side="left", padx=10)

        # Add "+" button for new category
        add_category_btn = ctk.CTkButton(
            category_row,
            text="+",
            command=self.show_add_category_popup,
            width=40,
            height=35,
            fg_color="#3498db",
            hover_color="#2980b9",
            font=("Arial", 14, "bold")
        )
        add_category_btn.pack(side="left", padx=5)

        # Notes field
        notes_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        notes_frame.pack(fill="x", pady=8)

        ctk.CTkLabel(notes_frame, text="Notes:",
                    width=150, anchor="w").pack(side="left", padx=10)

        self.product_notes_text = ctk.CTkTextbox(notes_frame, width=250, height=80)
        self.product_notes_text.pack(side="left", padx=10)

        # Buttons
        button_frame = ctk.CTkFrame(parent_frame)
        button_frame.pack(pady=20)

        ctk.CTkButton(button_frame, text="Save Product",
                     command=self.save_new_product_fixed,
                     fg_color="#27ae60", hover_color="#219653",
                     width=150, height=40).pack(side="left", padx=10)

        ctk.CTkButton(button_frame, text="Clear Form",
                     command=self.clear_product_form,
                     width=150, height=40).pack(side="left", padx=10)

        # Status label
        self.product_form_status = ctk.CTkLabel(parent_frame, text="",
                                              font=("Arial", 12))
        self.product_form_status.pack(pady=10)

    def save_new_product_fixed(self):
        """Save new product to database"""
        try:
            # Get form data
            product_data = {
                'Product_ID': self.generated_product_id,
                'Product_Name': self.product_form_entries['product_name'].get(),
                'Category': self.category_dropdown_var.get(),  # Changed to use dropdown value
                'Selling_Price': float(self.product_form_entries['selling_price'].get()),
                'Active': self.product_form_entries['active'].get(),
                'Notes': self.product_notes_text.get("1.0", "end-1c").strip()
            }

            # Validate required fields
            if not product_data['Product_Name']:
                self.product_form_status.configure(text="Product Name is required",
                                                  text_color="red")
                return

            if product_data['Selling_Price'] < 0:
                self.product_form_status.configure(text="Selling Price cannot be negative",
                                                  text_color="red")
                return

            # Save to database
            success, message = self.db.add_product(product_data)

            if success:
                self.product_form_status.configure(text=f"✅ {message}", text_color="green")
                # Clear form
                self.clear_product_form()
                # Generate new ID for next product
                new_id = self.db.generate_product_id()
                self.generated_product_id = new_id

                # Refresh products table if it exists
                if hasattr(self, 'products_table_frame'):
                    self.refresh_products_table()

                # Update product costs
                self.db.update_all_product_costs()

            else:
                self.product_form_status.configure(text=f"❌ {message}", text_color="red")

        except ValueError as e:
            self.product_form_status.configure(text=f"Invalid number format: {str(e)}",
                                             text_color="red")
        except Exception as e:
            self.product_form_status.configure(text=f"Error: {str(e)}",
                                             text_color="red")

    def clear_product_form(self):
        """Clear the product form"""
        for entry in self.product_form_entries.values():
            entry.delete(0, 'end')

        # Set defaults
        if hasattr(self, 'category_dropdown_var'):
            self.category_dropdown_var.set("General")
        self.product_form_entries['active'].insert(0, "Yes")
        self.product_form_entries['selling_price'].insert(0, "0.00")

        self.product_notes_text.delete("1.0", "end")

        # Generate new ID
        new_id = self.db.generate_product_id()
        self.generated_product_id = new_id

        # Update status
        self.product_form_status.configure(text="")

    def show_add_category_popup(self, current_value=""):
        """Popup to add a new category"""
        popup = ctk.CTkToplevel(self.window)
        popup.title("Add New Category")
        popup.geometry("450x400")
        popup.transient(self.window)
        popup.grab_set()
        
        # Center the popup
        popup.update_idletasks()
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 250) // 2
        popup.geometry(f"+{x}+{y}")
        
        # Main container
        main_frame = ctk.CTkFrame(popup)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(main_frame, text="Add New Category",
                    font=("Arial", 18, "bold")).pack(pady=15)
        
        # Info text
        ctk.CTkLabel(main_frame, 
                    text="Enter a new category name:",
                    font=("Arial", 12)).pack(pady=5)
        
        # Entry field
        category_var = tk.StringVar(value=current_value)
        category_entry = ctk.CTkEntry(main_frame,
                                     textvariable=category_var,
                                     width=300,
                                     height=35,
                                     font=("Arial", 12))
        category_entry.pack(pady=15)
        category_entry.focus_set()
        
        # Status label
        status_label = ctk.CTkLabel(main_frame, text="",
                                   font=("Arial", 11))
        status_label.pack(pady=5)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(pady=10)
        
        def save_category():
            """Save the new category"""
            new_category = category_var.get().strip()
            
            if not new_category:
                status_label.configure(text="Category name cannot be empty",
                                     text_color="red")
                return
            
            if len(new_category) > 50:
                status_label.configure(text="Category name too long (max 50 characters)",
                                     text_color="red")
                return
            
            # Get existing categories
            products_df = self.db.read_tab('Products')
            existing_categories = []
            if 'Category' in products_df.columns:
                existing_categories = products_df['Category'].dropna().unique()
            
            # Check if category already exists
            if new_category in existing_categories:
                status_label.configure(text=f"Category '{new_category}' already exists",
                                     text_color="orange")
                return
            
            # Success
            status_label.configure(text=f"✅ Category '{new_category}' added!",
                                 text_color="green")
            
            # Close popup after 1 second
            popup.after(1000, popup.destroy)
            
            # Update the dropdown in the form
            self.update_category_dropdown(new_category)
        
        ctk.CTkButton(buttons_frame, text="Save",
                     command=save_category,
                     fg_color="#27ae60", hover_color="#219653",
                     width=120, height=40).pack(side="left", padx=10)
        
        ctk.CTkButton(buttons_frame, text="Cancel",
                     command=popup.destroy,
                     width=120, height=40).pack(side="left", padx=10)
    
    def update_category_dropdown(self, new_category):
        """Update the category dropdown with a new category"""
        if hasattr(self, 'category_dropdown'):
            # Get current values
            current_values = list(self.category_dropdown.cget("values"))
            
            # Add new category if not already in list
            if new_category not in current_values:
                # Sort the values alphabetically
                current_values.append(new_category)
                current_values.sort()
                
                # Update the dropdown
                self.category_dropdown.configure(values=current_values)
                
                # Select the new category
                self.category_dropdown.set(new_category)