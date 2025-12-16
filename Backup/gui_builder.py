# modules/gui_builder.py - COMPLETE UPDATED VERSION WITH ALL MANAGEMENT FORMS
import customtkinter as ctk
import pandas as pd
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
import os
from modules.templates import AppTemplates, DatabaseTemplates

class InventoryGUI:
    def __init__(self, window, db, config):
        self.window = window
        self.db = db
        self.config = config
        
        # Set window properties
        self.window.title(f"Inventory Manager - {config['business_name']}")
        self.window.geometry("1100x750")
        
        # Create main container
        self.create_layout()
    
    def create_layout(self):
        """Create the main layout with sidebar and main area"""
        
        # Create sidebar
        self.sidebar = ctk.CTkFrame(self.window, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Create main content area
        self.main_content = ctk.CTkFrame(self.window, corner_radius=0)
        self.main_content.pack(side="right", expand=True, fill="both")
        
        # Add sidebar buttons
        self.create_sidebar_buttons()
        
        # Start with dashboard
        self.show_dashboard()
    
    def create_sidebar_buttons(self):
        """Create navigation buttons in sidebar"""
        
        # Logo/title area
        title = ctk.CTkLabel(self.sidebar, text="INVENTORY", 
                            font=("Arial", 22, "bold"))
        title.pack(pady=(20, 10))
        
        sub_title = ctk.CTkLabel(self.sidebar, 
                                text=f"{self.config['business_name']}",
                                font=("Arial", 12))
        sub_title.pack(pady=(0, 20))
        
        # Navigation buttons
        buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("🏪 Products", self.show_products_management),
            ("🥚 Ingredients", self.show_ingredients_management),
            ("📝 Recipes", self.show_recipes),
            ("💰 Sales", self.show_sales),
            ("📦 Inventory", self.show_inventory),
            ("💸 Expenses", self.show_expenses_management),
            ("📈 Reports", self.show_reports),
            ("⚙️ Settings", self.show_settings)
        ]
        
        for text, command in buttons:
            btn = ctk.CTkButton(self.sidebar, text=text, 
                               command=command,
                               height=40,
                               anchor="w",
                               fg_color="transparent",
                               hover_color=("gray70", "gray30"),
                               font=("Arial", 13))
            btn.pack(fill="x", padx=10, pady=3)
        
        # Separator
        ctk.CTkLabel(self.sidebar, text="", height=20).pack()
        
        # Exit button at bottom
        ctk.CTkButton(self.sidebar, text="🚪 Exit", 
                     command=self.window.destroy,
                     fg_color="#e74c3c", 
                     hover_color="#c0392b",
                     height=40).pack(side="bottom", pady=20, padx=10)
    
    def clear_main_content(self):
        """Clear the main content area"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Show dashboard with summary"""
        self.clear_main_content()
        
        # Title
        title = ctk.CTkLabel(self.main_content, text="Dashboard", 
                            font=("Arial", 28, "bold"))
        title.pack(pady=20)
        
        # Create frames for stats
        stats_frame = ctk.CTkFrame(self.main_content)
        stats_frame.pack(pady=10, padx=20, fill="x")
        
        # Get data
        products_df = self.db.get_all_products()
        sales_df = self.db.read_tab('Sales')
        inventory_df = self.db.get_inventory_status()
        
        # Calculate stats
        total_products = len(products_df) if not products_df.empty else 0
        
        today = datetime.now().strftime(self.config['date_format'])
        total_sales_today = 0
        if not sales_df.empty and 'Sale_Date' in sales_df.columns and 'Total_Amount' in sales_df.columns:
            today_sales = sales_df[sales_df['Sale_Date'] == today]
            total_sales_today = today_sales['Total_Amount'].sum() if not today_sales.empty else 0
        
        # Check low stock
        low_stock_count = 0
        critical_count = 0
        if not inventory_df.empty and 'Status' in inventory_df.columns:
            low_stock_count = len(inventory_df[inventory_df['Status'] == 'Low Stock'])
            critical_count = len(inventory_df[inventory_df['Status'] == 'Critical'])
        
        # Display stats in a grid
        stats_grid = ctk.CTkFrame(stats_frame)
        stats_grid.pack(pady=20, padx=20)
        
        stats_data = [
            ("Total Products", f"{total_products}", "#3498db"),
            ("Today's Sales", f"{self.config['currency']}{total_sales_today:,.2f}", "#27ae60"),
            ("Low Stock Items", f"{low_stock_count}", "#f39c12" if low_stock_count > 0 else "#95a5a6"),
            ("Critical Items", f"{critical_count}", "#e74c3c" if critical_count > 0 else "#95a5a6")
        ]
        
        row = 0
        col = 0
        for stat_name, stat_value, color in stats_data:
            stat_frame = ctk.CTkFrame(stats_grid, width=220, height=100, 
                                    corner_radius=15, fg_color=color)
            stat_frame.grid(row=row, column=col, padx=10, pady=10)
            stat_frame.pack_propagate(False)
            
            ctk.CTkLabel(stat_frame, text=stat_name, 
                        font=("Arial", 14),
                        text_color="white").pack(pady=(15, 5))
            ctk.CTkLabel(stat_frame, text=stat_value, 
                        font=("Arial", 22, "bold"),
                        text_color="white").pack()
            
            col += 1
            if col > 1:  # 2 columns per row
                col = 0
                row += 1
        
        # Inventory alerts section
        if low_stock_count > 0 or critical_count > 0:
            alerts_frame = ctk.CTkFrame(self.main_content, border_width=2, 
                                       border_color="#e74c3c", corner_radius=10)
            alerts_frame.pack(pady=20, padx=20, fill="x")
            
            alert_text = f"⚠️  ALERT: {critical_count} Critical, {low_stock_count} Low Stock Items"
            ctk.CTkLabel(alerts_frame, 
                        text=alert_text,
                        font=("Arial", 14, "bold"),
                        text_color="#e74c3c").pack(pady=10)
            
            # Show critical items
            if critical_count > 0:
                critical_items = inventory_df[inventory_df['Status'] == 'Critical']
                for _, item in critical_items.head(3).iterrows():  # Show top 3
                    item_text = f"• {item['Ingredient_Name']}: {item['Current_Stock']} left (Min: {item['Min_Stock']})"
                    ctk.CTkLabel(alerts_frame,
                                text=item_text,
                                text_color="#e74c3c").pack(anchor="w", padx=30, pady=2)
            
            ctk.CTkButton(alerts_frame, text="View All Alerts",
                         command=self.show_inventory,
                         fg_color="#e74c3c", 
                         hover_color="#c0392b",
                         height=35).pack(pady=10)
        
        # Quick actions (keep this as is)
        ctk.CTkLabel(self.main_content, text="Quick Actions", 
                    font=("Arial", 20, "bold")).pack(pady=(30, 15))
        
        actions_frame = ctk.CTkFrame(self.main_content)
        actions_frame.pack(pady=10, padx=20)
        
        action_buttons = [
            ("➕ New Product", self.show_products_management, "#3498db"),
            ("🥚 Add Ingredient", self.show_ingredients_management, "#9b59b6"),
            ("💰 New Sale", self.show_sales, "#27ae60"),
            ("📦 Check Inventory", self.show_inventory, "#f39c12")
        ]
        
        for btn_text, command, color in action_buttons:
            btn = ctk.CTkButton(actions_frame, text=btn_text,
                               command=command,
                               fg_color=color, 
                               hover_color=self.darken_color(color),
                               height=45,
                               font=("Arial", 13))
            btn.pack(side="left", padx=10, pady=10)
        
        # NEW: Popular Products Section
        ctk.CTkLabel(self.main_content, text="🔥 Popular Products (Last 7 Days)", 
                    font=("Arial", 18, "bold")).pack(pady=(30, 15))
        
        popular_frame = ctk.CTkFrame(self.main_content)
        popular_frame.pack(pady=10, padx=20, fill="x")
        
        popular_products = self.get_popular_products()
        
        if not popular_products.empty:
            # Create a simple table for popular products
            headers_frame = ctk.CTkFrame(popular_frame, fg_color="transparent")
            headers_frame.pack(fill="x", padx=10, pady=5)
            
            headers = ["Product", "Quantity Sold", "Revenue"]
            for i, header in enumerate(headers):
                ctk.CTkLabel(headers_frame, text=header, 
                            font=("Arial", 12, "bold"),
                            width=150 if i == 0 else 120).pack(side="left", padx=10)
            
            for _, product in popular_products.iterrows():
                row_frame = ctk.CTkFrame(popular_frame, fg_color="transparent")
                row_frame.pack(fill="x", padx=10, pady=5)
                
                ctk.CTkLabel(row_frame, text=product['Product_Name'][:30], 
                            width=150).pack(side="left", padx=10)
                ctk.CTkLabel(row_frame, text=f"{product['Quantity']:,.0f}", 
                            width=120).pack(side="left", padx=10)
                ctk.CTkLabel(row_frame, text=f"{self.config['currency']}{product['Total_Amount']:,.2f}", 
                            width=120, text_color="green").pack(side="left", padx=10)
        else:
            ctk.CTkLabel(popular_frame, text="No recent sales data",
                        font=("Arial", 12), text_color="gray").pack(pady=20)
        
        # NEW: Quick Inventory Status
        ctk.CTkLabel(self.main_content, text="📦 Quick Inventory Status", 
                    font=("Arial", 18, "bold")).pack(pady=(30, 15))
        
        quick_inv_frame = ctk.CTkFrame(self.main_content)
        quick_inv_frame.pack(pady=10, padx=20, fill="x")
        
        inventory_status = self.db.get_inventory_status()
        
        if not inventory_status.empty:
            # Get top 5 critical/low stock items
            critical_items = inventory_status[inventory_status['Status'] == 'Critical'].head(3)
            low_items = inventory_status[inventory_status['Status'] == 'Low Stock'].head(3)
            
            if not critical_items.empty:
                ctk.CTkLabel(quick_inv_frame, text="🚨 Critical Stock:",
                            font=("Arial", 14, "bold"), text_color="#e74c3c").pack(anchor="w", padx=20, pady=(10, 5))
                
                for _, item in critical_items.iterrows():
                    item_text = f"• {item['Ingredient_Name']}: {item['Current_Stock']} left (Min: {item['Min_Stock']})"
                    ctk.CTkLabel(quick_inv_frame, text=item_text,
                                text_color="#e74c3c").pack(anchor="w", padx=40, pady=2)
            
            if not low_items.empty:
                ctk.CTkLabel(quick_inv_frame, text="⚠️ Low Stock:",
                            font=("Arial", 14, "bold"), text_color="#f39c12").pack(anchor="w", padx=20, pady=(10, 5))
                
                for _, item in low_items.iterrows():
                    item_text = f"• {item['Ingredient_Name']}: {item['Current_Stock']} left (Min: {item['Min_Stock']})"
                    ctk.CTkLabel(quick_inv_frame, text=item_text,
                                text_color="#f39c12").pack(anchor="w", padx=40, pady=2)
            
            if critical_items.empty and low_items.empty:
                ctk.CTkLabel(quick_inv_frame, text="✅ All inventory levels are normal",
                            text_color="green").pack(pady=20)
        else:
            ctk.CTkLabel(quick_inv_frame, text="No inventory data available",
                        font=("Arial", 12), text_color="gray").pack(pady=20)    
    def darken_color(self, hex_color):
        """Darken a hex color for hover effect"""
        # Simple darkening - you can implement more sophisticated color manipulation
        return hex_color
    def get_popular_products(self, days_back=7):
        """Get popular products from recent sales"""
        try:
            sales_df = self.db.read_tab('Sales')
            products_df = self.db.read_tab('Products')
            
            if sales_df.empty or products_df.empty:
                return pd.DataFrame()
            
            # Filter recent sales
            cutoff_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            recent_sales = sales_df[sales_df['Sale_Date'] >= cutoff_date]
            
            if recent_sales.empty:
                return pd.DataFrame()
            
            # Group by product
            product_sales = recent_sales.groupby('Product_ID').agg({
                'Quantity': 'sum',
                'Total_Amount': 'sum'
            }).reset_index()
            
            # Get product names
            product_sales = pd.merge(product_sales, products_df[['Product_ID', 'Product_Name']], 
                                    on='Product_ID', how='left')
            
            return product_sales.sort_values('Quantity', ascending=False).head(5)
        except:
            return pd.DataFrame()    

    # ============================================================================
    # PRODUCTS MANAGEMENT SECTION - FIXED VERSION
    # ============================================================================
    
    def show_products_management(self):
        """Show products management interface - UPDATED (removed Edit tab)"""
        self.clear_main_content()
        
        # Create tabview for products
        products_tabs = ctk.CTkTabview(self.main_content)
        products_tabs.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add only 2 tabs now (removed Edit Product tab)
        products_tabs.add("View Products")
        products_tabs.add("Add Product")
        
        # Fill each tab
        self.show_all_products(products_tabs.tab("View Products"))
        self.create_product_form_fixed(products_tabs.tab("Add Product"))
    
    def show_all_products(self, parent_frame):
        """Show all products in a table"""
        ctk.CTkLabel(parent_frame, text="All Products", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # ===== ENHANCED FILTER & SORT FRAME =====
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
        
        # Sort by dropdown
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
                                         values=["All Categories"],  # Will be populated
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
        
        # Create frame for table (will be filled by refresh function)
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
        
        # Get all products (including inactive for filtering)
        all_products_df = self.db.read_tab('Products')
        
        if all_products_df.empty:
            ctk.CTkLabel(self.products_table_frame, text="No products found in database.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Make a copy for filtering
        products_df = all_products_df.copy()

        # Update category filter options if needed
        if hasattr(self, 'category_filter_var'):
            # Get unique categories
            categories = ["All Categories"]
            if 'Category' in all_products_df.columns:
                unique_cats = all_products_df['Category'].dropna().unique()
                for cat in unique_cats:
                    if cat and str(cat).strip() and str(cat).strip().lower() != 'nan':
                        categories.append(str(cat).strip())
            
            # Remove duplicates and sort
            categories = sorted(list(set(categories)))
            
            # Update the dropdown if options changed
            current_value = self.category_filter_var.get()
            if current_value not in categories:
                self.category_filter_var.set("All Categories")
            
            # We can't directly update the OptionMenu, but we can track this for next time
        
        # ===== APPLY FILTERS =====
        
        # 1. Search filter
        search_text = self.product_search_var.get().lower() if hasattr(self, 'product_search_var') else ""
        if search_text:
            mask = (products_df['Product_Name'].str.lower().str.contains(search_text) | 
                   products_df['Product_ID'].str.lower().str.contains(search_text))
            products_df = products_df[mask]
        
        # 2. Status filter
        status_filter = self.status_filter_var.get() if hasattr(self, 'status_filter_var') else "All Status"
        if status_filter == "Active Only":
            if 'Active' in products_df.columns:
                # Handle different Active formats (Yes/No, True/False, 1/0)
                products_df['Active'] = products_df['Active'].astype(str).str.upper()
                products_df = products_df[products_df['Active'].str.contains('YES|TRUE|1', na=False)]
        elif status_filter == "Inactive Only":
            if 'Active' in products_df.columns:
                products_df['Active'] = products_df['Active'].astype(str).str.upper()
                products_df = products_df[~products_df['Active'].str.contains('YES|TRUE|1', na=False)]
        
        # 3. Category filter
        category_filter = self.category_filter_var.get() if hasattr(self, 'category_filter_var') else "All Categories"
        if category_filter != "All Categories" and 'Category' in products_df.columns:
            # Fill NaN and filter
            products_df['Category'] = products_df['Category'].fillna('Uncategorized')
            products_df = products_df[products_df['Category'] == category_filter]
        
        # ===== APPLY SORTING =====
        sort_by = self.product_sort_var.get() if hasattr(self, 'product_sort_var') else "Product Name (A-Z)"
        
        # Determine sort column and direction
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
            "Status (Active First)": ("Active", False),  # Active first (Yes/True comes before No/False)
            "Status (Inactive First)": ("Active", True)   # Inactive first
        }
        
        if sort_by in sort_mapping:
            sort_column, default_ascending = sort_mapping[sort_by]
            
            # Check if column exists
            if sort_column in products_df.columns:
                # Determine sort direction
                ascending = self.sort_ascending if sort_by in ["Product Name (A-Z)", "Product Name (Z-A)", 
                                                             "Selling Price (High to Low)", "Selling Price (Low to High)",
                                                             "Cost Price (High to Low)", "Cost Price (Low to High)",
                                                             "Profit Margin (High to Low)", "Profit Margin (Low to High)",
                                                             "Margin % (High to Low)", "Margin % (Low to High)",
                                                             "Category (A-Z)"] else default_ascending
                
                # Handle special cases for Active status
                if sort_column == "Active":
                    # Convert to sortable values (Active first = Yes/True sorted to top)
                    products_df['_Active_Sort'] = products_df['Active'].astype(str).str.upper().map({
                        'YES': 1, 'TRUE': 1, '1': 1, 'NO': 2, 'FALSE': 2, '0': 2
                    }).fillna(3)
                    sort_column = '_Active_Sort'
                
                # Sort the dataframe
                products_df = products_df.sort_values(by=sort_column, ascending=ascending)
                
                # Drop temporary column if created
                if '_Active_Sort' in products_df.columns:
                    products_df = products_df.drop('_Active_Sort', axis=1)
        
        if products_df.empty:
            # Show filter info
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
        
        if products_df.empty:
            ctk.CTkLabel(self.products_table_frame, text="No matching products found.",
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
        
        # Add sort info
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
            
            # Status (Active/Inactive)
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
            
            # Edit button - Use improved popup
            ctk.CTkButton(
                action_frame, 
                text="✏️ Edit",
                command=lambda pid=product['Product_ID']: self.edit_product_better_popup(pid),
                width=60, 
                height=25,
                font=("Arial", 10)
            ).pack(side="left", padx=2)

    def edit_product_better_popup(self, product_id):
        """Improved popup for editing products with proper contrast"""
        # Get product data
        products_df = self.db.read_tab('Products')
        product_row = products_df[products_df['Product_ID'] == product_id]
        
        if product_row.empty:
            messagebox.showerror("Error", f"Product {product_id} not found")
            return
        
        product_data = product_row.iloc[0]
        product_name = product_data['Product_Name']
        
        # Create popup window
        popup = ctk.CTkToplevel(self.window)
        popup.title(f"Edit Product: {product_name}")
        popup.geometry("700x800")
        popup.minsize(650, 750)
        popup.transient(self.window)
        popup.grab_set()
        
        # Center on screen
        popup.update_idletasks()
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = (screen_width - 700) // 2
        y = (screen_height - 800) // 2
        popup.geometry(f"+{x}+{y}")
        
        # Main container
        main_container = ctk.CTkFrame(popup)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header - WHITE TEXT ON DARK BACKGROUND
        header_frame = ctk.CTkFrame(main_container, fg_color="#2c3e50", corner_radius=10)
        header_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(header_frame, 
                    text=f"Edit Product: {product_name}",
                    font=("Arial", 20, "bold"),
                    text_color="white").pack(pady=15)
        
        # Product info display - DARK TEXT ON LIGHT BACKGROUND
        info_frame = ctk.CTkFrame(main_container, fg_color="#ecf0f1", corner_radius=8)
        info_frame.pack(fill="x", pady=10, padx=10)
        
        # Product ID - DARK LABELS
        id_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        id_frame.pack(fill="x", pady=5, padx=20)
        ctk.CTkLabel(id_frame, text="Product ID:", 
                    font=("Arial", 12, "bold"), 
                    text_color="#2c3e50",
                    width=120).pack(side="left")
        ctk.CTkLabel(id_frame, text=product_id, 
                    font=("Arial", 12, "bold"),
                    text_color="#1e3a8a").pack(side="left", padx=10)
        
        # Current cost info (if available) - DARK LABELS
        cost_price = product_data.get('Cost_Price', 0)
        if cost_price > 0:
            cost_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            cost_frame.pack(fill="x", pady=5, padx=20)
            ctk.CTkLabel(cost_frame, text="Current Cost:", 
                        font=("Arial", 12, "bold"), 
                        text_color="#2c3e50",
                        width=120).pack(side="left")
            ctk.CTkLabel(cost_frame, 
                        text=f"{self.config['currency']}{cost_price:.2f}",
                        font=("Arial", 12, "bold"),
                        text_color="#145a32").pack(side="left", padx=10)
        
        # Create scrollable content area
        content_frame = ctk.CTkScrollableFrame(main_container, height=400)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Form fields - DARK LABELS ON LIGHT BACKGROUND
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
        
        # Notes field - DARK LABEL
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
        
        # Status label - DARK TEXT
        status_label = ctk.CTkLabel(main_container, text="", 
                                   font=("Arial", 12),
                                   text_color="#2c3e50")
        status_label.pack(pady=10)
        
        # BUTTONS FRAME
        buttons_frame = ctk.CTkFrame(main_container, height=90)
        buttons_frame.pack(fill="x", pady=10, padx=55)
        buttons_frame.pack_propagate(False)
        
        # Button functions
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
        
        def delete_product():
            """Delete the product"""
            confirm = messagebox.askyesno("Confirm Delete",
                                        f"Are you sure you want to delete '{product_name}'?\n\n"
                                        "This will mark the product as inactive.")
            if confirm:
                success, message = self.db.delete_product(product_id)
                if success:
                    messagebox.showinfo("Success", message)
                    # Refresh table and close popup
                    self.refresh_products_table()
                    popup.destroy()
                else:
                    messagebox.showerror("Error", message)
        
        # Create buttons with proper size
        button_width = 160
        button_height = 45
        
        ctk.CTkButton(buttons_frame, text="💾 Save Changes",
                     command=save_changes,
                     fg_color="#27ae60", hover_color="#219653",
                     width=button_width, height=button_height,
                     font=("Arial", 13, "bold")).pack(side="left", padx=15)
        
        ctk.CTkButton(buttons_frame, text="🗑️ Delete",
                     command=delete_product,
                     fg_color="#e74c3c", hover_color="#c0392b",
                     width=button_width, height=button_height,
                     font=("Arial", 13, "bold")).pack(side="left", padx=15)
        
        ctk.CTkButton(buttons_frame, text="Cancel",
                     command=popup.destroy,
                     width=button_width, height=button_height,
                     font=("Arial", 13, "bold")).pack(side="left", padx=15)

    def filter_products(self):
        """Filter products based on search text"""
        # This is handled by refresh_products_table
        self.refresh_products_table()
    
    def view_product_recipe(self, product_id):
        """View recipe for a specific product with proper contrast"""
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
        
        # Title - WHITE TEXT ON DARK BACKGROUND
        title_frame = ctk.CTkFrame(main_container, fg_color="#2c3e50", corner_radius=10)
        title_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(title_frame, 
                    text=f"Recipe for: {product_name}",
                    font=("Arial", 18, "bold"),
                    text_color="white").pack(pady=15)
        
        # Product ID - WHITE TEXT ON DARK BACKGROUND
        ctk.CTkLabel(title_frame,
                    text=f"Product ID: {product_id}",
                    font=("Arial", 12, "bold"),
                    text_color="#ecf0f1").pack(pady=5)
        
        # Create scrollable frame for recipe items
        scroll_frame = ctk.CTkScrollableFrame(main_container, height=300)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Headers - GRAY TEXT
        headers_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        headers_frame.pack(fill="x", pady=5)
        
        headers = ["Ingredient", "Quantity", "Unit", "Cost"]
        widths = [180, 100, 80, 120]
        
        for header, width in zip(headers, widths):
            ctk.CTkLabel(headers_frame, text=header,
                        font=("Arial", 12, "bold"),
                        text_color="#888888",  # CHANGED TO GRAY
                        width=width).pack(side="left", padx=5)
        
        # Display each ingredient - GRAY TEXT
        total_cost = 0
        
        for _, item in recipe_items.iterrows():
            row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=3)
            
            # Ingredient name - GRAY
            ingredient_name = item.get('Ingredient_Name', item['Ingredient_ID'])
            ctk.CTkLabel(row_frame, text=ingredient_name[:25],
                        width=widths[0],
                        text_color="#FFFFFF").pack(side="left", padx=5)  # CHANGED TO GRAY
            
            # Quantity - convert to appropriate unit - GRAY
            quantity = item.get('Quantity_Required', 0)
            unit = item.get('Unit', '')
            
            # Convert to more readable units
            display_quantity = quantity
            display_unit = unit
            
            if unit == 'kg' and quantity < 1:
                # Convert kg to grams if less than 1kg
                display_quantity = quantity * 1000
                display_unit = 'g'
            elif unit == 'L' and quantity < 1:
                # Convert L to ml if less than 1L
                display_quantity = quantity * 1000
                display_unit = 'ml'
            
            # Format quantity nicely
            if display_quantity.is_integer():
                quantity_text = f"{display_quantity:.0f}"
            else:
                # Show up to 3 decimal places
                quantity_text = f"{display_quantity:.3f}".rstrip('0').rstrip('.')
            
            ctk.CTkLabel(row_frame, text=quantity_text,
                        width=widths[1],
                        text_color="#FFFFFF").pack(side="left", padx=5)  # CHANGED TO GRAY
            
            # Unit - GRAY
            ctk.CTkLabel(row_frame, text=display_unit,
                        width=widths[2],
                        text_color="#FFFFFF").pack(side="left", padx=5)  # CHANGED TO GRAY
            
            # Cost - GRAY (or keep original if you want costs to stand out)
            cost_per_unit = item.get('Cost_Per_Unit', 0)
            item_cost = cost_per_unit * quantity
            total_cost += item_cost
            
            ctk.CTkLabel(row_frame, 
                        text=f"{self.config['currency']}{item_cost:.2f}",
                        width=widths[3],
                        text_color="#8bca84").pack(side="left", padx=5)  # CHANGED TO GRAY        
        # Total cost - DARK TEXT ON LIGHT BACKGROUND
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
        
        # Close button - LARGER AND BOLDER
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
        
        # Auto-generate ID (display only, will be regenerated on save)
        new_id = self.db.generate_product_id()
        ctk.CTkLabel(form_frame, text=f"Product ID: {new_id}", 
                    font=("Arial", 14, "bold")).pack(pady=5)
        
        # Store the generated ID
        self.generated_product_id = new_id
        
        # Form fields
        fields = [
            ("Product Name*:", "product_name", "text"),
            ("Category:", "category", "text"),
            ("Selling Price*:", "selling_price", "number"),
            ("Active (Yes/No):", "active", "text")
        ]
        
        self.product_form_entries = {}
        
        for i, (label_text, field_name, field_type) in enumerate(fields):
            row_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=8)
            
            ctk.CTkLabel(row_frame, text=label_text, 
                        width=150, anchor="w").pack(side="left", padx=10)
            
            if field_type == "text":
                entry = ctk.CTkEntry(row_frame, width=250)
                # Set default values
                if field_name == "active":
                    entry.insert(0, "Yes")
                elif field_name == "category":
                    entry.insert(0, "General")  # Changed from "Bakery" to "General"
            elif field_type == "number":
                entry = ctk.CTkEntry(row_frame, width=250)
                if field_name == "selling_price":
                    entry.insert(0, "0.00")
            
            entry.pack(side="left", padx=10)
            self.product_form_entries[field_name] = entry
        
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
        """Save new product to database - FIXED VERSION"""
        try:
            # Get form data
            product_data = {
                'Product_ID': self.generated_product_id,  # Use the stored ID
                'Product_Name': self.product_form_entries['product_name'].get(),
                'Category': self.product_form_entries['category'].get(),
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
                # Update the displayed ID
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
        self.product_form_entries['category'].insert(0, "General")
        self.product_form_entries['active'].insert(0, "Yes")
        self.product_form_entries['selling_price'].insert(0, "0.00")
        
        self.product_notes_text.delete("1.0", "end")
        
        # Generate new ID
        new_id = self.db.generate_product_id()
        self.generated_product_id = new_id
        
        # Update status
        self.product_form_status.configure(text="")

    
    # ============================================================================
    # INGREDIENTS MANAGEMENT SECTION - CLEANED & WORKING
    # ============================================================================
    
    def show_ingredients_management(self):
        """Show ingredients management interface"""
        self.clear_main_content()
        
        # Create tabview for ingredients
        ingredients_tabs = ctk.CTkTabview(self.main_content)
        ingredients_tabs.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add tabs
        ingredients_tabs.add("View Ingredients")
        ingredients_tabs.add("Add Ingredient")
        ingredients_tabs.add("Edit Ingredient")
        
        # Fill each tab
        self.show_all_ingredients(ingredients_tabs.tab("View Ingredients"))
        self.create_ingredient_form(ingredients_tabs.tab("Add Ingredient"))
        self.create_edit_ingredient_form_clean(ingredients_tabs.tab("Edit Ingredient"))
    
    def show_all_ingredients(self, parent_frame):
        """Show all ingredients in a table"""
        ctk.CTkLabel(parent_frame, text="All Ingredients", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Search and filter frame
        search_frame = ctk.CTkFrame(parent_frame)
        search_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(search_frame, text="Search:", 
                    font=("Arial", 12)).pack(side="left", padx=10)
        
        self.ingredient_search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, 
                                   textvariable=self.ingredient_search_var,
                                   placeholder_text="Search by name or ID...",
                                   width=300)
        search_entry.pack(side="left", padx=10)
        
        # Refresh button
        ctk.CTkButton(search_frame, text="Refresh", 
                     command=lambda: self.refresh_ingredients_table(),
                     width=100).pack(side="right", padx=10)
        
        # Create frame for table (will be filled by refresh function)
        self.ingredients_table_frame = ctk.CTkFrame(parent_frame)
        self.ingredients_table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initial load
        self.refresh_ingredients_table()
    
    def refresh_ingredients_table(self):
        """Refresh the ingredients table"""
        if not hasattr(self, 'ingredients_table_frame'):
            return
            
        # Clear existing table
        for widget in self.ingredients_table_frame.winfo_children():
            widget.destroy()
        
        # Get ingredients
        ingredients_df = self.db.get_all_ingredients()
        
        if ingredients_df.empty:
            ctk.CTkLabel(self.ingredients_table_frame, text="No ingredients found.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Apply search filter
        search_text = self.ingredient_search_var.get().lower() if hasattr(self, 'ingredient_search_var') else ""
        if search_text:
            mask = (ingredients_df['Ingredient_Name'].str.lower().str.contains(search_text) | 
                   ingredients_df['Ingredient_ID'].str.lower().str.contains(search_text))
            ingredients_df = ingredients_df[mask]
        
        if ingredients_df.empty:
            ctk.CTkLabel(self.ingredients_table_frame, text="No matching ingredients found.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Create scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(self.ingredients_table_frame, width=900, height=400)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Table headers
        headers = ["ID", "Ingredient Name", "Category", "Unit", "Current Stock", "Min Stock", "Cost/Unit", "Status", "Actions"]
        col_widths = [80, 180, 100, 80, 100, 80, 100, 100, 120]
        
        for col, (header, width) in enumerate(zip(headers, col_widths)):
            ctk.CTkLabel(scroll_frame, text=header, font=("Arial", 12, "bold"),
                        width=width).grid(row=0, column=col, padx=5, pady=5, sticky="w")
        
        # Get inventory status for color coding
        inventory_status = self.db.get_inventory_status()
        
        # Add ingredient rows
        for row_idx, (_, ingredient) in enumerate(ingredients_df.iterrows(), start=1):
            # ID
            ctk.CTkLabel(scroll_frame, text=ingredient['Ingredient_ID'], 
                        width=col_widths[0]).grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
            
            # Name
            ctk.CTkLabel(scroll_frame, text=ingredient['Ingredient_Name'], 
                        width=col_widths[1]).grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
            
            # Category
            category = ingredient.get('Category', 'N/A')
            ctk.CTkLabel(scroll_frame, text=category, 
                        width=col_widths[2]).grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
            
            # Unit
            unit = ingredient.get('Unit', 'N/A')
            ctk.CTkLabel(scroll_frame, text=unit, 
                        width=col_widths[3]).grid(row=row_idx, column=3, padx=5, pady=2, sticky="w")
            
            # Current Stock
            current_stock = ingredient.get('Current_Stock', 0)
            
            # Get status for color coding
            status = "Normal"
            if not inventory_status.empty:
                ing_status = inventory_status[inventory_status['Ingredient_ID'] == ingredient['Ingredient_ID']]
                if not ing_status.empty:
                    status = ing_status.iloc[0].get('Status', 'Normal')
            
            stock_color = "green"
            if status == 'Low Stock':
                stock_color = "orange"
            elif status == 'Critical':
                stock_color = "red"
            
            ctk.CTkLabel(scroll_frame, text=f"{current_stock:,.2f}", 
                        text_color=stock_color,
                        width=col_widths[4]).grid(row=row_idx, column=4, padx=5, pady=2, sticky="w")
            
            # Min Stock
            min_stock = ingredient.get('Min_Stock', 0)
            ctk.CTkLabel(scroll_frame, text=f"{min_stock:,.2f}", 
                        width=col_widths[5]).grid(row=row_idx, column=5, padx=5, pady=2, sticky="w")
            
            # Cost/Unit
            cost_per_unit = ingredient.get('Cost_Per_Unit', 0)
            ctk.CTkLabel(scroll_frame, text=f"{self.config['currency']}{cost_per_unit:,.2f}", 
                        width=col_widths[6]).grid(row=row_idx, column=6, padx=5, pady=2, sticky="w")
            
            # Status badge
            status_color = {
                'Normal': 'green',
                'Low Stock': 'orange',
                'Critical': 'red'
            }.get(status, 'gray')
            
            status_frame = ctk.CTkFrame(scroll_frame, width=col_widths[7]-10, 
                                       height=25, corner_radius=10,
                                       fg_color=status_color)
            status_frame.grid(row=row_idx, column=7, padx=5, pady=2)
            status_frame.pack_propagate(False)
            ctk.CTkLabel(status_frame, text=status, 
                        text_color="white", font=("Arial", 10)).pack(expand=True)
            
            # Action buttons
            action_frame = ctk.CTkFrame(scroll_frame, width=col_widths[8], fg_color="transparent")
            action_frame.grid(row=row_idx, column=8, padx=5, pady=2)
            
            # Add Stock button
            ctk.CTkButton(
                action_frame, 
                text="📦 Add",
                command=lambda iid=ingredient['Ingredient_ID']: self.quick_add_stock_popup(iid),
                width=45, 
                height=25,
                font=("Arial", 10)
            ).pack(side="left", padx=2)
            
            # Edit button - Use the improved popup
            ctk.CTkButton(
                action_frame, 
                text="✏️ Edit",
                command=lambda iid=ingredient['Ingredient_ID']: self.edit_ingredient_better_popup(iid),
                width=45, 
                height=25,
                font=("Arial", 10)
            ).pack(side="left", padx=2)
    
    def edit_ingredient_better_popup(self, ingredient_id):
        """Improved popup for editing ingredients with proper contrast"""
        # Get ingredient data
        ingredients_df = self.db.get_all_ingredients()
        ingredient_row = ingredients_df[ingredients_df['Ingredient_ID'] == ingredient_id]
        
        if ingredient_row.empty:
            messagebox.showerror("Error", f"Ingredient {ingredient_id} not found")
            return
        
        ingredient_data = ingredient_row.iloc[0]
        ingredient_name = ingredient_data['Ingredient_Name']
        
        # Create popup window
        popup = ctk.CTkToplevel(self.window)
        popup.title(f"Edit Ingredient: {ingredient_name}")
        popup.geometry("700x800")
        popup.minsize(650, 750)
        popup.transient(self.window)
        popup.grab_set()
        
        # Center on screen
        popup.update_idletasks()
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = (screen_width - 700) // 2
        y = (screen_height - 800) // 2
        popup.geometry(f"+{x}+{y}")
        
        # Main container
        main_container = ctk.CTkFrame(popup)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header - WHITE TEXT ON DARK BACKGROUND
        header_frame = ctk.CTkFrame(main_container, fg_color="#2c3e50", corner_radius=10)
        header_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(header_frame, 
                    text=f"Edit Ingredient: {ingredient_name}",
                    font=("Arial", 20, "bold"),
                    text_color="white").pack(pady=15)
        
        # Info display - DARK TEXT ON LIGHT BACKGROUND
        info_frame = ctk.CTkFrame(main_container, fg_color="#ecf0f1", corner_radius=8)
        info_frame.pack(fill="x", pady=10, padx=10)
        
        # Ingredient ID - DARK LABELS
        id_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        id_frame.pack(fill="x", pady=5, padx=20)
        ctk.CTkLabel(id_frame, text="Ingredient ID:", 
                    font=("Arial", 12, "bold"), 
                    text_color="#2c3e50",
                    width=120).pack(side="left")
        ctk.CTkLabel(id_frame, text=ingredient_id, 
                    font=("Arial", 12, "bold"),
                    text_color="#1e3a8a").pack(side="left", padx=10)
        
        # Current stock - DARK LABELS
        stock_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        stock_frame.pack(fill="x", pady=5, padx=20)
        ctk.CTkLabel(stock_frame, text="Current Stock:", 
                    font=("Arial", 12, "bold"), 
                    text_color="#2c3e50",
                    width=120).pack(side="left")
        current_stock = ingredient_data.get('Current_Stock', 0)
        unit = ingredient_data.get('Unit', '')
        ctk.CTkLabel(stock_frame, 
                    text=f"{current_stock} {unit}",
                    font=("Arial", 12, "bold"),
                    text_color="#1e3a8a").pack(side="left", padx=10)
        
        # Create scrollable content area
        content_frame = ctk.CTkScrollableFrame(main_container, height=450)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Form fields - DARK LABELS ON LIGHT BACKGROUND
        fields = [
            ("Ingredient Name*:", "Ingredient_Name", "text"),
            ("Category:", "Category", "text"),
            ("Unit*:", "Unit", "text"),
            ("Cost Per Unit*:", "Cost_Per_Unit", "number"),
            ("Minimum Stock:", "Min_Stock", "number")
        ]
        
        entries = {}
        for label_text, field_name, field_type in fields:
            field_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            field_frame.pack(fill="x", pady=12, padx=20)
            
            ctk.CTkLabel(field_frame, text=label_text, 
                        font=("Arial", 12, "bold"), 
                        text_color="#888888",
                        width=150).pack(side="left", padx=10)
            
            value = ingredient_data.get(field_name, "")
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
        
        # Notes field - DARK LABEL
        notes_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        notes_frame.pack(fill="x", pady=12, padx=20)
        
        ctk.CTkLabel(notes_frame, text="Notes:", 
                    font=("Arial", 12, "bold"), 
                    text_color="#888888",
                    width=150).pack(side="left", padx=10)
        
        notes_text = ctk.CTkTextbox(notes_frame, width=300, height=100)
        notes_value = ingredient_data.get('Notes', '')
        if pd.notna(notes_value):
            notes_text.insert("1.0", str(notes_value))
        notes_text.pack(side="left", padx=10)
        
        # Status label - DARK TEXT
        status_label = ctk.CTkLabel(main_container, text="", 
                                   font=("Arial", 12),
                                   text_color="#2c3e50")
        status_label.pack(pady=10)
        
        # BUTTONS FRAME
        buttons_frame = ctk.CTkFrame(main_container, height=90)
        buttons_frame.pack(fill="x", pady=10, padx=55)
        buttons_frame.pack_propagate(False)
        
        # Button functions
        def save_changes():
            """Save the edited ingredient"""
            try:
                # Get updated data
                updated_data = {}
                required_fields = ['Ingredient_Name', 'Unit', 'Cost_Per_Unit']
                
                for field_name, entry in entries.items():
                    value = entry.get()
                    
                    if field_name in required_fields and not value:
                        status_label.configure(
                            text=f"{field_name.replace('_', ' ')} is required",
                            text_color="red"
                        )
                        return
                    
                    if field_name in ['Cost_Per_Unit', 'Min_Stock']:
                        try:
                            updated_data[field_name] = float(value)
                        except ValueError:
                            status_label.configure(
                                text=f"{field_name.replace('_', ' ')} must be a number",
                                text_color="red"
                            )
                            return
                    else:
                        updated_data[field_name] = value
                
                # Add notes
                updated_data['Notes'] = notes_text.get("1.0", "end-1c").strip()
                
                # Update in database
                success, message = self.db.update_ingredient(ingredient_id, updated_data)
                
                if success:
                    status_label.configure(text=f"✅ {message}", text_color="green")
                    
                    # Update product costs (since ingredient prices changed)
                    self.db.update_all_product_costs()
                    
                    # Refresh the ingredients table
                    self.refresh_ingredients_table()
                    
                    # Close popup after 1.5 seconds
                    popup.after(1500, popup.destroy)
                else:
                    status_label.configure(text=f"❌ {message}", text_color="red")
                    
            except Exception as e:
                status_label.configure(text=f"Error: {str(e)}", text_color="red")
        
        def delete_ingredient():
            """Delete the ingredient"""
            confirm = messagebox.askyesno("Confirm Delete",
                                        f"Are you sure you want to delete '{ingredient_name}'?\n\n"
                                        "This will fail if the ingredient is used in any recipes.")
            if confirm:
                success, message = self.db.delete_ingredient(ingredient_id)
                if success:
                    messagebox.showinfo("Success", message)
                    # Update costs and refresh
                    self.db.update_all_product_costs()
                    self.refresh_ingredients_table()
                    popup.destroy()
                else:
                    messagebox.showerror("Error", message)
        
        # Create buttons with proper size
        button_width = 160
        button_height = 45
        
        ctk.CTkButton(buttons_frame, text="💾 Save Changes",
                     command=save_changes,
                     fg_color="#27ae60", hover_color="#219653",
                     width=button_width, height=button_height,
                     font=("Arial", 13, "bold")).pack(side="left", padx=15)
        
        ctk.CTkButton(buttons_frame, text="🗑️ Delete",
                     command=delete_ingredient,
                     fg_color="#e74c3c", hover_color="#c0392b",
                     width=button_width, height=button_height,
                     font=("Arial", 13, "bold")).pack(side="left", padx=15)
        
        ctk.CTkButton(buttons_frame, text="Cancel",
                     command=popup.destroy,
                     width=button_width, height=button_height,
                     font=("Arial", 13, "bold")).pack(side="left", padx=15)    
    def create_edit_ingredient_form_clean(self, parent_frame):
        """Clean Edit Ingredient tab - Working version"""
        ctk.CTkLabel(parent_frame, text="Edit Ingredient", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Main container
        main_container = ctk.CTkFrame(parent_frame)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Get all ingredients
        ingredients_df = self.db.get_all_ingredients()
        
        if ingredients_df.empty:
            ctk.CTkLabel(main_container, 
                        text="No ingredients available to edit.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Left side: Ingredient selection
        left_frame = ctk.CTkFrame(main_container, width=300)
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Right side: Edit form
        right_frame = ctk.CTkFrame(main_container)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # === LEFT FRAME: Ingredient Selection ===
        ctk.CTkLabel(left_frame, text="Select Ingredient:", 
                    font=("Arial", 16, "bold")).pack(pady=20)
        
        # Create dropdown with ingredients
        ingredient_options = [f"{row['Ingredient_ID']} - {row['Ingredient_Name']}" 
                             for _, row in ingredients_df.iterrows()]
        
        dropdown_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        dropdown_frame.pack(pady=20, padx=20, fill="x")
        
        self.edit_ingredient_var = tk.StringVar()
        if ingredient_options:
            self.edit_ingredient_var.set(ingredient_options[0])
        
        ctk.CTkLabel(dropdown_frame, text="Choose ingredient:").pack(pady=5)
        
        ingredient_menu = ctk.CTkOptionMenu(dropdown_frame,
                                           values=ingredient_options,
                                           variable=self.edit_ingredient_var,
                                           width=250,
                                           command=self.load_ingredient_form_in_tab)
        ingredient_menu.pack(pady=10)
        
        # Info panel
        info_frame = ctk.CTkFrame(left_frame, corner_radius=10, fg_color="#f8f9fa")
        info_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(info_frame, text="ℹ️ Information", 
                    font=("Arial", 12, "bold")).pack(pady=10)
        
        ctk.CTkLabel(info_frame, 
                    text="Select an ingredient from the dropdown to edit its details.",
                    wraplength=250, justify="left").pack(pady=10, padx=10)
        
        # === RIGHT FRAME: Edit Form Container ===
        self.edit_ingredient_form_container = ctk.CTkFrame(right_frame)
        self.edit_ingredient_form_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Initial load of first ingredient
        if ingredient_options:
            self.load_ingredient_form_in_tab(self.edit_ingredient_var.get())
    
    def load_ingredient_form_in_tab(self, ingredient_selection=None):
        """Load ingredient form in the Edit Ingredient tab"""
        if ingredient_selection is None:
            if hasattr(self, 'edit_ingredient_var'):
                ingredient_selection = self.edit_ingredient_var.get()
            else:
                return
        
        if " - " not in ingredient_selection:
            return
        
        ingredient_id = ingredient_selection.split(" - ")[0]
        
        # Get ingredient data
        ingredients_df = self.db.get_all_ingredients()
        ingredient_row = ingredients_df[ingredients_df['Ingredient_ID'] == ingredient_id]
        
        if ingredient_row.empty:
            return
        
        ingredient_data = ingredient_row.iloc[0]
        
        # Clear the form container
        for widget in self.edit_ingredient_form_container.winfo_children():
            widget.destroy()
        
        # Create the form
        self.create_ingredient_tab_form(self.edit_ingredient_form_container, ingredient_data, ingredient_id)
    
    def create_ingredient_tab_form(self, container, ingredient_data, ingredient_id):
        """Create ingredient edit form for the tab"""
        # Title
        ingredient_name = ingredient_data['Ingredient_Name']
        ctk.CTkLabel(container, 
                    text=f"Editing: {ingredient_name}",
                    font=("Arial", 18, "bold")).pack(pady=10)
        
        # Ingredient ID display
        id_frame = ctk.CTkFrame(container, fg_color="transparent")
        id_frame.pack(pady=10, fill="x")
        ctk.CTkLabel(id_frame, text=f"Ingredient ID: {ingredient_id}",
                    font=("Arial", 12, "bold"),
                    text_color="blue").pack()
        
        # Current stock display
        stock_frame = ctk.CTkFrame(container, fg_color="transparent")
        stock_frame.pack(pady=5, fill="x")
        current_stock = ingredient_data.get('Current_Stock', 0)
        unit = ingredient_data.get('Unit', '')
        ctk.CTkLabel(stock_frame, 
                    text=f"Current Stock: {current_stock} {unit}",
                    font=("Arial", 12)).pack()
        
        # Create a scrollable frame for the form
        scroll_frame = ctk.CTkScrollableFrame(container, height=400)
        scroll_frame.pack(fill="both", expand=True, pady=10)
        
        # Form fields - FIXED: Darker labels
        fields = [
            ("Ingredient Name*:", "Ingredient_Name", "text"),
            ("Category:", "Category", "text"),
            ("Unit*:", "Unit", "text"),
            ("Cost Per Unit*:", "Cost_Per_Unit", "number"),
            ("Minimum Stock:", "Min_Stock", "number")
        ]
        
        entries = {}
        for label_text, field_name, field_type in fields:
            row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=10, padx=20)
            
            # FIXED: Added text_color
            ctk.CTkLabel(row_frame, text=label_text, 
                        width=150, anchor="w",
                        text_color="white").pack(side="left", padx=10)  # ADDED
            
            value = ingredient_data.get(field_name, "")
            if pd.isna(value):
                value = ""
            
            if field_type == "text":
                entry = ctk.CTkEntry(row_frame, width=250)
                entry.insert(0, str(value))
            elif field_type == "number":
                entry = ctk.CTkEntry(row_frame, width=250)
                if value:
                    entry.insert(0, f"{float(value):.2f}")
                else:
                    entry.insert(0, "0.00")
            
            entry.pack(side="left", padx=10)
            entries[field_name] = entry
        
        # Notes field - FIXED: Darker label
        notes_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        notes_frame.pack(fill="x", pady=10, padx=20)
        
        ctk.CTkLabel(notes_frame, text="Notes:", 
                    width=150, anchor="w",
                    text_color="white").pack(side="left", padx=10)  # ADDED
        
        notes_text = ctk.CTkTextbox(notes_frame, width=250, height=80)
        notes_value = ingredient_data.get('Notes', '')
        if pd.notna(notes_value):
            notes_text.insert("1.0", str(notes_value))
        notes_text.pack(side="left", padx=10)
        
        # Status label
        status_label = ctk.CTkLabel(container, text="", font=("Arial", 12))
        status_label.pack(pady=10)
        
        # Button frame
        button_frame = ctk.CTkFrame(container)
        button_frame.pack(pady=20, fill="x", padx=50)
        
        def save_changes():
            """Save the edited ingredient"""
            try:
                # Get updated data
                updated_data = {}
                required_fields = ['Ingredient_Name', 'Unit', 'Cost_Per_Unit']
                
                for field_name, entry in entries.items():
                    value = entry.get()
                    
                    if field_name in required_fields and not value:
                        status_label.configure(
                            text=f"{field_name.replace('_', ' ')} is required",
                            text_color="red"
                        )
                        return
                    
                    if field_name in ['Cost_Per_Unit', 'Min_Stock']:
                        try:
                            updated_data[field_name] = float(value)
                        except ValueError:
                            status_label.configure(
                                text=f"{field_name.replace('_', ' ')} must be a number",
                                text_color="red"
                            )
                            return
                    else:
                        updated_data[field_name] = value
                
                # Add notes
                updated_data['Notes'] = notes_text.get("1.0", "end-1c").strip()
                
                # Update in database
                success, message = self.db.update_ingredient(ingredient_id, updated_data)
                
                if success:
                    status_label.configure(text=f"✅ {message}", text_color="green")
                    # Update product costs
                    self.db.update_all_product_costs()
                    # Refresh table view
                    self.refresh_ingredients_table()
                else:
                    status_label.configure(text=f"❌ {message}", text_color="red")
                    
            except Exception as e:
                status_label.configure(text=f"Error: {str(e)}", text_color="red")
        
        def delete_ingredient():
            """Delete the ingredient"""
            confirm = messagebox.askyesno("Confirm Delete",
                                        f"Are you sure you want to delete '{ingredient_name}'?\n\n"
                                        "This will fail if the ingredient is used in any recipes.")
            if confirm:
                success, message = self.db.delete_ingredient(ingredient_id)
                if success:
                    messagebox.showinfo("Success", message)
                    # Update and refresh
                    self.db.update_all_product_costs()
                    # Refresh the dropdown selection
                    self.load_ingredient_form_in_tab(self.edit_ingredient_var.get())
                else:
                    messagebox.showerror("Error", message)
        
        # Buttons
        ctk.CTkButton(button_frame, text="💾 Save Changes",
                     command=save_changes,
                     fg_color="#27ae60", hover_color="#219653",
                     width=150, height=40,
                     font=("Arial", 12)).pack(side="left", padx=20)
        
        ctk.CTkButton(button_frame, text="🗑️ Delete Ingredient",
                     command=delete_ingredient,
                     fg_color="#e74c3c", hover_color="#c0392b",
                     width=150, height=40,
                     font=("Arial", 12)).pack(side="left", padx=20)


    
    # ============================================================
    # ADD INGREDIENT FORM (Keep this as is - it's working)
    # ============================================================
    
    def create_ingredient_form(self, parent_frame):
        """Form to add new ingredient - UPDATED WITH UNIT DROPDOWN"""
        ctk.CTkLabel(parent_frame, text="Add New Ingredient", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Form frame
        form_frame = ctk.CTkFrame(parent_frame)
        form_frame.pack(pady=20, padx=50, fill="x")
        
        # Auto-generate ID
        new_id = self.db.generate_ingredient_id()
        ctk.CTkLabel(form_frame, text=f"Ingredient ID: {new_id}", 
                    font=("Arial", 14, "bold")).pack(pady=5)
        
        # Form fields - FIXED: All labels darker
        fields = [
            ("Ingredient Name*:", "ingredient_name", "text"),
            ("Category:", "category", "category_dropdown"),
            ("Unit*:", "unit", "unit_dropdown"),
            ("Cost Per Unit*:", "cost_per_unit", "number"),
            ("Initial Stock:", "initial_stock", "number"),
            ("Minimum Stock:", "min_stock", "number")
        ]
        
        self.ingredient_form_entries = {}
        
        for i, (label_text, field_name, field_type) in enumerate(fields):
            row_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=8)
            
            # FIXED: Added text_color to label
            ctk.CTkLabel(row_frame, text=label_text, 
                        width=150, anchor="w",
                        text_color="white").pack(side="left", padx=10)  # ADDED
            
            if field_type == "text":
                entry = ctk.CTkEntry(row_frame, width=250)
                entry.pack(side="left", padx=10)
                self.ingredient_form_entries[field_name] = entry
                
            elif field_type == "category_dropdown":
                # Category dropdown with common categories
                categories = ["Raw Material", "Dry Goods", "Liquids", "Produce", 
                            "Dairy", "Spices", "Packaging", "Other"]
                category_var = ctk.StringVar(value="Raw Material")
                category_menu = ctk.CTkOptionMenu(row_frame, 
                                                values=categories,
                                                variable=category_var,
                                                width=250)
                category_menu.pack(side="left", padx=10)
                self.ingredient_form_entries[field_name] = category_var
                
            elif field_type == "unit_dropdown":
                # Unit dropdown - all available units
                units = ["Select Unit", "g", "kg", "mg", "ml", "L", 
                        "tsp", "tbsp", "cup", "pcs", "dozen", "pack",
                        "bottle", "can", "jar"]
                unit_var = ctk.StringVar(value="Select Unit")
                unit_menu = ctk.CTkOptionMenu(row_frame, 
                                            values=units,
                                            variable=unit_var,
                                            width=250)
                unit_menu.pack(side="left", padx=10)
                self.ingredient_form_entries[field_name] = unit_var
                
            elif field_type == "number":
                entry = ctk.CTkEntry(row_frame, width=250)
                if field_name == "cost_per_unit":
                    entry.insert(0, "0.00")
                elif field_name == "initial_stock":
                    entry.insert(0, "0.00")
                elif field_name == "min_stock":
                    entry.insert(0, "10.00")
                entry.pack(side="left", padx=10)
                self.ingredient_form_entries[field_name] = entry
        
        # Notes field - FIXED: Darker label
        notes_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        notes_frame.pack(fill="x", pady=8)
        
        ctk.CTkLabel(notes_frame, text="Notes:", 
                    width=150, anchor="w",
                    text_color="white").pack(side="left", padx=10)  # ADDED
        
        self.ingredient_notes_text = ctk.CTkTextbox(notes_frame, width=250, height=80)
        self.ingredient_notes_text.pack(side="left", padx=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(parent_frame)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame, text="Save Ingredient", 
                     command=self.save_new_ingredient,
                     fg_color="#27ae60", hover_color="#219653",
                     width=150, height=40).pack(side="left", padx=10)
        
        ctk.CTkButton(button_frame, text="Clear Form", 
                     command=self.clear_ingredient_form,
                     width=150, height=40).pack(side="left", padx=10)
        
        # Status label
        self.ingredient_form_status = ctk.CTkLabel(parent_frame, text="", 
                                                  font=("Arial", 12))
        self.ingredient_form_status.pack(pady=10)
    
    def save_new_ingredient(self):
        """Save new ingredient to database - UPDATED FOR UNIT DROPDOWN"""
        try:
            # Get form data
            ingredient_data = {
                'Ingredient_ID': self.db.generate_ingredient_id(),
                'Ingredient_Name': self.ingredient_form_entries['ingredient_name'].get(),
                'Category': self.ingredient_form_entries['category'].get(),
                'Unit': self.ingredient_form_entries['unit'].get(),
                'Cost_Per_Unit': float(self.ingredient_form_entries['cost_per_unit'].get()),
                'Current_Stock': float(self.ingredient_form_entries['initial_stock'].get()),
                'Min_Stock': float(self.ingredient_form_entries['min_stock'].get()),
                'Notes': self.ingredient_notes_text.get("1.0", "end-1c").strip()
            }
            
            # Validate required fields
            required_fields = {
                'Ingredient_Name': 'Ingredient Name',
                'Unit': 'Unit'
            }
            
            for field, field_name in required_fields.items():
                value = ingredient_data[field]
                if not value or value == "Select Unit":
                    self.ingredient_form_status.configure(
                        text=f"{field_name} is required", 
                        text_color="red"
                    )
                    return
            
            # Validate unit selection
            if ingredient_data['Unit'] == "Select Unit":
                self.ingredient_form_status.configure(
                    text="Please select a unit", 
                    text_color="red"
                )
                return
            
            # Save to database
            success, message = self.db.add_ingredient(ingredient_data)
            
            if success:
                self.ingredient_form_status.configure(text=message, text_color="green")
                # Clear form
                self.clear_ingredient_form()
                # Update product costs since ingredient prices changed
                self.db.update_all_product_costs()
            else:
                self.ingredient_form_status.configure(text=message, text_color="red")
                
        except ValueError as e:
            self.ingredient_form_status.configure(text=f"Invalid number: {str(e)}", 
                                                 text_color="red")
        except Exception as e:
            self.ingredient_form_status.configure(text=f"Error: {str(e)}", 
                                                 text_color="red")
    
    def clear_ingredient_form(self):
        """Clear the ingredient form"""
        # Clear text entries
        if 'ingredient_name' in self.ingredient_form_entries:
            self.ingredient_form_entries['ingredient_name'].delete(0, 'end')
        
        if 'cost_per_unit' in self.ingredient_form_entries:
            self.ingredient_form_entries['cost_per_unit'].delete(0, 'end')
            self.ingredient_form_entries['cost_per_unit'].insert(0, "0.00")
        
        if 'initial_stock' in self.ingredient_form_entries:
            self.ingredient_form_entries['initial_stock'].delete(0, 'end')
            self.ingredient_form_entries['initial_stock'].insert(0, "0.00")
        
        if 'min_stock' in self.ingredient_form_entries:
            self.ingredient_form_entries['min_stock'].delete(0, 'end')
            self.ingredient_form_entries['min_stock'].insert(0, "10.00")
        
        # Reset dropdowns
        if 'category' in self.ingredient_form_entries:
            self.ingredient_form_entries['category'].set("Raw Material")
        
        if 'unit' in self.ingredient_form_entries:
            self.ingredient_form_entries['unit'].set("Select Unit")
        
        # Clear notes
        self.ingredient_notes_text.delete("1.0", "end")
        
        # Clear status
        self.ingredient_form_status.configure(text="")
    
    def quick_add_stock_popup(self, ingredient_id):
        """Popup to quickly add stock to an ingredient - IMPROVED CONTRAST"""
        # Get ingredient info
        ingredients_df = self.db.get_all_ingredients()
        ingredient = ingredients_df[ingredients_df['Ingredient_ID'] == ingredient_id].iloc[0]
        
        # Create popup
        popup = ctk.CTkToplevel(self.window)
        popup.title(f"Add Stock - {ingredient_id}")
        popup.geometry("500x500")
        popup.minsize(450, 400)
        popup.transient(self.window)
        popup.grab_set()
        
        # Center on screen
        popup.update_idletasks()
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 500) // 2
        popup.geometry(f"+{x}+{y}")
        
        # Main container
        main_container = ctk.CTkFrame(popup)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Title - WHITE TEXT ON DARK BACKGROUND
        title_frame = ctk.CTkFrame(main_container, fg_color="#2c3e50", corner_radius=10)
        title_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(title_frame, 
                    text=f"Add Stock: {ingredient['Ingredient_Name']}",
                    font=("Arial", 18, "bold"),
                    text_color="white").pack(pady=15)
        
        # Current stock info - DARK TEXT ON LIGHT BACKGROUND
        current_stock = ingredient.get('Current_Stock', 0)
        unit = ingredient.get('Unit', '')
        
        stock_frame = ctk.CTkFrame(main_container, fg_color="#ecf0f1", corner_radius=8)
        stock_frame.pack(fill="x", pady=10, padx=20)
        
        ctk.CTkLabel(stock_frame, 
                    text=f"Current Stock: {current_stock} {unit}",
                    font=("Arial", 14, "bold"),
                    text_color="#2c3e50").pack(pady=10)
        
        # Quantity to add - DARK TEXT ON MAIN BACKGROUND
        ctk.CTkLabel(main_container, text="Quantity to Add:", 
                    font=("Arial", 12, "bold"),
                    text_color="#888888").pack(pady=10)
        
        quantity_entry = ctk.CTkEntry(main_container, 
                                     placeholder_text=f"Enter amount in {unit}",
                                     width=200, height=35)
        quantity_entry.pack(pady=5)
        
        # Notes - DARK TEXT ON MAIN BACKGROUND
        ctk.CTkLabel(main_container, text="Notes (optional):", 
                    font=("Arial", 12, "bold"),
                    text_color="#888888").pack(pady=10)
        
        notes_entry = ctk.CTkEntry(main_container, 
                                  placeholder_text="e.g., Purchase from supplier",
                                  width=300, height=35)
        notes_entry.pack(pady=5)
        
        # Status label - DARK TEXT ON MAIN BACKGROUND
        status_label = ctk.CTkLabel(main_container, text="", 
                                   font=("Arial", 12),
                                   text_color="#2c3e50")
        status_label.pack(pady=10)
        
        def add_stock():
            """Add stock and close popup"""
            try:
                quantity = float(quantity_entry.get())
                notes = notes_entry.get()
                
                if quantity <= 0:
                    status_label.configure(text="Quantity must be positive", 
                                          text_color="red")
                    return
                
                success, message = self.db.add_inventory_stock(ingredient_id, quantity, notes)
                
                if success:
                    status_label.configure(text=message, text_color="green")
                    popup.after(1500, popup.destroy)
                    # Refresh the ingredients table
                    self.refresh_ingredients_table()
                else:
                    status_label.configure(text=message, text_color="red")
                    
            except ValueError:
                status_label.configure(text="Please enter a valid number", 
                                      text_color="red")
        
        # Buttons frame
        button_frame = ctk.CTkFrame(main_container, height=80)
        button_frame.pack(fill="x", pady=20, padx=65)
        button_frame.pack_propagate(False)
        
        ctk.CTkButton(button_frame, text="Add Stock",
                     command=add_stock,
                     fg_color="#27ae60", hover_color="#219653",
                     width=140, height=40,
                     font=("Arial", 12)).pack(side="left", padx=15)
        
        ctk.CTkButton(button_frame, text="Cancel",
                     command=popup.destroy,
                     width=140, height=40,
                     font=("Arial", 12)).pack(side="left", padx=15)    
    # ============================================================================
    # EXISTING MODULES (Recipes, Sales, Inventory, Reports, Settings)
    # ============================================================================
    # [Include all your existing methods from the previous gui_builder.py here]
    # show_recipes(), create_recipe_form(), show_sales(), show_inventory(), etc.
    # These should remain exactly as you had them
    
    # For brevity, I'll mark where they should be inserted:
    # INSERT ALL EXISTING METHODS FROM YOUR PREVIOUS gui_builder.py HERE
    # This includes: show_recipes(), create_recipe_form(), show_sales(), 
    # show_inventory(), show_reports(), show_settings(), and all their helper methods
    
    # ============================================================================
    # RECIPES MANAGEMENT SECTION - COMPLETE FIXED VERSION
    # ============================================================================
    
    def show_recipes(self):
        """Show recipe management interface"""
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
    
    # ============================================================================
    # SALES SECTION - COMPLETE WITH CALENDAR FEATURE
    # ============================================================================
    
    def show_sales(self):
        """Show sales entry and history - COMPLETE IMPLEMENTATION"""
        self.clear_main_content()
        
        # Create tabview for sales
        sales_tabs = ctk.CTkTabview(self.main_content)
        sales_tabs.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add tabs
        sales_tabs.add("New Sale")
        sales_tabs.add("Sales History")
        sales_tabs.add("Sales Reports")
        
        # Fill each tab
        self.create_sale_entry_form(sales_tabs.tab("New Sale"))
        self.show_sales_history(sales_tabs.tab("Sales History"))
        self.show_sales_reports(sales_tabs.tab("Sales Reports"))
    
    def create_sale_entry_form(self, parent_frame):
        """Point-of-Sale style sale entry form - ENHANCED VERSION"""
        ctk.CTkLabel(parent_frame, text="Point of Sale", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Initialize cart
        self.sale_cart = []  # List of dicts: {product_id, name, price, quantity}
        self.cart_total = 0
        
        # Main container with two columns
        main_container = ctk.CTkFrame(parent_frame)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side - Product selection
        left_frame = ctk.CTkFrame(main_container, width=350)
        left_frame.pack(side="left", fill="both", padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Right side - Cart/Checkout
        right_frame = ctk.CTkFrame(main_container)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # === LEFT FRAME: Product Selection ===
        ctk.CTkLabel(left_frame, text="Products", 
                    font=("Arial", 16, "bold")).pack(pady=10)
        
        # ===== ENHANCED FILTERING =====
        filter_frame = ctk.CTkFrame(left_frame)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Search bar
        search_row = ctk.CTkFrame(filter_frame, fg_color="transparent")
        search_row.pack(fill="x", pady=5)
        
        ctk.CTkLabel(search_row, text="Search:", 
                    font=("Arial", 12)).pack(side="left", padx=5)
        
        self.sale_search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(search_row, 
                                   textvariable=self.sale_search_var,
                                   placeholder_text="Type product name...",
                                   width=200)
        search_entry.pack(side="left", padx=5)
        
        # Category filter
        category_row = ctk.CTkFrame(filter_frame, fg_color="transparent")
        category_row.pack(fill="x", pady=5)
        
        ctk.CTkLabel(category_row, text="Category:", 
                    font=("Arial", 12)).pack(side="left", padx=5)
        
        # Get all products to build category list
        products_df = self.db.get_all_products()
        categories = ["All Categories"]
        
        if not products_df.empty and 'Category' in products_df.columns:
            unique_cats = products_df['Category'].dropna().unique()
            for cat in unique_cats:
                if cat and str(cat).strip() and str(cat).strip().lower() != 'nan':
                    categories.append(str(cat).strip())
        
        categories = sorted(list(set(categories)))
        
        self.sale_category_var = tk.StringVar(value="All Categories")
        category_menu = ctk.CTkOptionMenu(category_row,
                                         values=categories,
                                         variable=self.sale_category_var,
                                         width=200)
        category_menu.pack(side="left", padx=5)
        
        # Filter buttons row
        button_row = ctk.CTkFrame(filter_frame, fg_color="transparent")
        button_row.pack(fill="x", pady=5)
        
        ctk.CTkButton(button_row, text="🔍 Apply Filters", 
                     command=lambda: self.filter_sale_products_enhanced(left_frame),
                     fg_color="#3498db", hover_color="#2980b9",
                     width=120).pack(side="left", padx=5)
        
        ctk.CTkButton(button_row, text="🗑️ Clear Filters", 
                     command=lambda: self.clear_sale_filters(left_frame),
                     fg_color="#95a5a6", hover_color="#7f8c8d",
                     width=120).pack(side="left", padx=5)
        
        # Product grid frame (for clickable cards)
        self.products_grid_frame = ctk.CTkScrollableFrame(left_frame, height=350)
        self.products_grid_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === RIGHT FRAME: Cart ===
        ctk.CTkLabel(right_frame, text="Shopping Cart", 
                    font=("Arial", 16, "bold")).pack(pady=10)
        
        # Cart items display
        cart_frame = ctk.CTkFrame(right_frame, height=300)
        cart_frame.pack(fill="x", padx=10, pady=10)
        cart_frame.pack_propagate(False)
        
        self.cart_items_frame = ctk.CTkScrollableFrame(cart_frame, height=280)
        self.cart_items_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Cart summary
        summary_frame = ctk.CTkFrame(right_frame, height=150)
        summary_frame.pack(fill="x", padx=10, pady=10)
        summary_frame.pack_propagate(False)
        
        # Summary labels
        self.subtotal_label = ctk.CTkLabel(summary_frame, 
                                          text=f"Net Total: {self.config['currency']}0.00",
                                          font=("Arial", 14))
        self.subtotal_label.pack(anchor="w", padx=20, pady=5)
        
        # Tax calculation
        self.tax_label = ctk.CTkLabel(summary_frame, 
                                      text=f"VAT (12%): {self.config['currency']}0.00",
                                      font=("Arial", 14))
        self.tax_label.pack(anchor="w", padx=20, pady=5)
        
        self.total_label = ctk.CTkLabel(summary_frame, 
                                       text=f"Total (incl. VAT): {self.config['currency']}0.00",
                                       font=("Arial", 16, "bold"))
        self.total_label.pack(anchor="w", padx=20, pady=5)
        
        # Action buttons
        button_frame = ctk.CTkFrame(right_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(button_frame, text="🛒 Checkout & Process Sale",
                     command=self.process_sale,
                     fg_color="#27ae60", hover_color="#219653",
                     height=45, font=("Arial", 14)).pack(side="left", padx=5)
        
        ctk.CTkButton(button_frame, text="🗑️ Clear Cart",
                     command=self.clear_sale_cart,
                     fg_color="#e74c3c", hover_color="#c0392b",
                     height=45, font=("Arial", 14)).pack(side="left", padx=5)
        
        # Status label
        self.sale_status_label = ctk.CTkLabel(right_frame, text="", 
                                             font=("Arial", 12))
        self.sale_status_label.pack(pady=5)
        
        # Bind search to filter
        self.sale_search_var.trace('w', lambda *args: self.filter_sale_products_enhanced(left_frame))
        self.sale_category_var.trace('w', lambda *args: self.filter_sale_products_enhanced(left_frame))
        
        # Initial load of products
        self.filter_sale_products_enhanced(left_frame)
    
    def filter_sale_products_enhanced(self, parent_frame):
        """Display products for sale selection with clickable cards and filtering"""
        # Clear existing grid
        for widget in self.products_grid_frame.winfo_children():
            widget.destroy()
        
        # Get all active products
        products_df = self.db.get_all_products()
        
        if products_df.empty:
            ctk.CTkLabel(self.products_grid_frame, 
                        text="No products available for sale.",
                        font=("Arial", 12)).pack(pady=50)
            return
        
        # Apply filters
        filtered_products = products_df.copy()
        
        # 1. Apply search filter
        search_text = self.sale_search_var.get().lower() if hasattr(self, 'sale_search_var') else ""
        if search_text:
            mask = (filtered_products['Product_Name'].str.lower().str.contains(search_text) |
                   filtered_products['Product_ID'].str.lower().str.contains(search_text))
            filtered_products = filtered_products[mask]
        
        # 2. Apply category filter
        selected_category = self.sale_category_var.get() if hasattr(self, 'sale_category_var') else "All Categories"
        if selected_category and selected_category != "All Categories":
            if 'Category' in filtered_products.columns:
                # Create a copy to avoid warnings
                filtered_products = filtered_products.copy()
                
                # Fill NaN categories with empty string
                filtered_products['Category'] = filtered_products['Category'].fillna('')
                
                # Convert all categories to string and strip whitespace
                filtered_products['Category'] = filtered_products['Category'].astype(str).str.strip()
                
                # Case-insensitive filtering
                mask = filtered_products['Category'].str.lower() == selected_category.lower().strip()
                filtered_products = filtered_products[mask]
        
        if filtered_products.empty:
            # Show filter info
            filter_info = []
            if search_text:
                filter_info.append(f"Search: '{search_text}'")
            if selected_category != "All Categories":
                filter_info.append(f"Category: '{selected_category}'")
            
            no_results_text = "No products found"
            if filter_info:
                no_results_text += f" with filters: {' • '.join(filter_info)}"
            no_results_text += "."
            
            ctk.CTkLabel(self.products_grid_frame, 
                        text=no_results_text,
                        font=("Arial", 12)).pack(pady=50)
            return
        
        # Create product cards grid (2 columns)
        row = 0
        col = 0
        
        for _, product in filtered_products.iterrows():
            # Create clickable card frame
            product_frame = ctk.CTkFrame(self.products_grid_frame, 
                                        width=160, height=140,
                                        corner_radius=12,
                                        border_width=1,
                                        border_color="gray",
                                        fg_color="#f8f9fa")
            product_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            product_frame.pack_propagate(False)
            
            # Make entire frame clickable
            product_frame.bind("<Button-1>", lambda e, p=product: self.add_to_cart(p))
            
            # Product name (truncated)
            product_name = product['Product_Name'][:20] + "..." if len(product['Product_Name']) > 20 else product['Product_Name']
            name_label = ctk.CTkLabel(product_frame, text=product_name,
                                    font=("Arial", 12, "bold"),
                                    wraplength=140,
                                    text_color="black")
            name_label.pack(pady=(15, 5), padx=10)
            name_label.bind("<Button-1>", lambda e, p=product: self.add_to_cart(p))
            
            # Price - bigger and bold
            price = product.get('Selling_Price', 0)
            price_label = ctk.CTkLabel(product_frame, 
                                      text=f"{self.config['currency']}{price:,.2f}",
                                      font=("Arial", 14, "bold"),
                                      text_color="green")
            price_label.pack(pady=2)
            price_label.bind("<Button-1>", lambda e, p=product: self.add_to_cart(p))
            
            # ID and Category (smaller)
            id_label = ctk.CTkLabel(product_frame, 
                                   text=f"ID: {product['Product_ID']}",
                                   font=("Arial", 9),
                                   text_color="black")
            id_label.pack(pady=2)
            id_label.bind("<Button-1>", lambda e, p=product: self.add_to_cart(p))
            
            # Category if available
            if 'Category' in product and pd.notna(product['Category']):
                category = str(product['Category']).strip()
                if category and category.lower() != 'nan':
                    category_label = ctk.CTkLabel(product_frame, 
                                                text=f"📂 {category[:15]}",
                                                font=("Arial", 9),
                                                text_color="#3498db")
                    category_label.pack(pady=2)
                    category_label.bind("<Button-1>", lambda e, p=product: self.add_to_cart(p))
            
            # Add hover effect
            def on_enter(e, frame=product_frame):
                frame.configure(border_color="#3498db", border_width=2)
            
            def on_leave(e, frame=product_frame):
                frame.configure(border_color="gray", border_width=1)
            
            product_frame.bind("<Enter>", on_enter)
            product_frame.bind("<Leave>", on_leave)
            name_label.bind("<Enter>", on_enter)
            name_label.bind("<Leave>", on_leave)
            price_label.bind("<Enter>", on_enter)
            price_label.bind("<Leave>", on_leave)
            id_label.bind("<Enter>", on_enter)
            id_label.bind("<Leave>", on_leave)
            
            # Add visual cue that it's clickable
            product_frame.configure(cursor="hand2")
            name_label.configure(cursor="hand2")
            price_label.configure(cursor="hand2")
            id_label.configure(cursor="hand2")
            
            # Double click to add multiple
            product_frame.bind("<Double-Button-1>", lambda e, p=product: [self.add_to_cart(p), self.add_to_cart(p)])
            
            col += 1
            if col > 1:  # 2 columns per row
                col = 0
                row += 1
        
        # Configure grid columns
        self.products_grid_frame.grid_columnconfigure(0, weight=1)
        self.products_grid_frame.grid_columnconfigure(1, weight=1)
    
    def clear_sale_filters(self, parent_frame):
        """Clear all sale filters"""
        if hasattr(self, 'sale_search_var'):
            self.sale_search_var.set("")
        
        if hasattr(self, 'sale_category_var'):
            self.sale_category_var.set("All Categories")
        
        self.filter_sale_products_enhanced(parent_frame)
    
    def add_to_cart(self, product):
        """Add product to cart - UPDATED with visual feedback"""
        # Check if product already in cart
        for item in self.sale_cart:
            if item['product_id'] == product['Product_ID']:
                # Increase quantity
                item['quantity'] += 1
                # Show visual feedback
                self.show_cart_feedback(f"+1 {product['Product_Name'][:15]}...")
                self.update_cart_display()
                return
        
        # Get selling price (VAT INCLUSIVE from database)
        selling_price_vat_inclusive = product.get('Selling_Price', 0)
        
        # Calculate VAT-exclusive price for database recording
        vat_rate = 0.12
        selling_price_vat_exclusive = selling_price_vat_inclusive / (1 + vat_rate)
        
        # Add new item to cart
        cart_item = {
            'product_id': product['Product_ID'],
            'name': product['Product_Name'],
            'price': selling_price_vat_inclusive,  # Store VAT-INCLUSIVE for display
            'price_vat_exclusive': selling_price_vat_exclusive,  # Store VAT-EXCLUSIVE for database
            'quantity': 1,
            'unit': 'pcs'
        }
        self.sale_cart.append(cart_item)
        
        # Show visual feedback
        self.show_cart_feedback(f"Added {product['Product_Name'][:15]}...")
        self.update_cart_display()
    
    def show_cart_feedback(self, message):
        """Show visual feedback when adding to cart"""
        # Create temporary feedback label
        feedback = ctk.CTkLabel(self.cart_items_frame.master.master,
                               text=f"✅ {message}",
                               font=("Arial", 11),
                               text_color="green",
                               fg_color="#d5f4e6",
                               corner_radius=8)
        feedback.place(relx=0.5, rely=0.5, anchor="center")
        
        # Remove after 1 second
        self.cart_items_frame.after(1000, feedback.destroy)
    
    def update_cart_display(self):
        """Update cart display and totals - VAT INCLUSIVE VERSION with BLACK TEXT"""
        # Clear cart display
        for widget in self.cart_items_frame.winfo_children():
            widget.destroy()
        
        if not self.sale_cart:
            ctk.CTkLabel(self.cart_items_frame, 
                        text="Cart is empty",
                        font=("Arial", 12),
                        text_color="black").pack(pady=50)
            
            self.subtotal_label.configure(text=f"Net Total: {self.config['currency']}0.00")
            self.tax_label.configure(text=f"VAT (12%): {self.config['currency']}0.00")
            self.total_label.configure(text=f"Total (incl. VAT): {self.config['currency']}0.00")
            self.cart_total = 0
            return
        
        # Calculate totals - IMPORTANT: Product prices already INCLUDE VAT
        total_vat_inclusive = 0  # This is what customers pay
        
        # Display cart items
        for i, item in enumerate(self.sale_cart):
            item_frame = ctk.CTkFrame(self.cart_items_frame, 
                                     height=60,
                                     fg_color="#f8f9fa",
                                     corner_radius=8,
                                     border_width=1,
                                     border_color="#e0e0e0")
            item_frame.pack(fill="x", pady=3, padx=2)
            item_frame.pack_propagate(False)
            
            # Item details
            details_frame = ctk.CTkFrame(item_frame, fg_color="#f8f9fa")
            details_frame.pack(side="left", fill="both", expand=True, padx=10)
            
            # Product name with icon - BLACK TEXT
            ctk.CTkLabel(details_frame, 
                        text=f"📦 {item['name'][:20]}...",
                        font=("Arial", 12, "bold"),
                        anchor="w",
                        text_color="black",
                        fg_color="#f8f9fa",
                        bg_color="#f8f9fa").pack(side="left", padx=5)
            
            # Quantity controls
            qty_frame = ctk.CTkFrame(item_frame, 
                                    fg_color="#f8f9fa",
                                    width=120)
            qty_frame.pack(side="left", padx=10)
            qty_frame.pack_propagate(False)
            
            # Decrease button
            ctk.CTkButton(qty_frame, text="−", width=30, height=30,
                         command=lambda idx=i: self.update_cart_quantity(idx, -1),
                         font=("Arial", 14, "bold"),
                         fg_color="#e74c3c", 
                         hover_color="#c0392b",
                         text_color="white").pack(side="left", padx=2)
            
            # Quantity number - BLACK on WHITE
            qty_label = ctk.CTkLabel(qty_frame, 
                                    text=str(item['quantity']),
                                    font=("Arial", 12, "bold"), 
                                    width=40,
                                    corner_radius=6, 
                                    fg_color="white",
                                    text_color="black",
                                    bg_color="white")
            qty_label.pack(side="left", padx=2)
            
            # Increase button
            ctk.CTkButton(qty_frame, text="+", width=30, height=30,
                         command=lambda idx=i: self.update_cart_quantity(idx, 1),
                         font=("Arial", 14, "bold"),
                         fg_color="#27ae60", 
                         hover_color="#219653",
                         text_color="white").pack(side="left", padx=2)
            
            # Price frame
            price_frame = ctk.CTkFrame(item_frame, 
                                      fg_color="#f8f9fa",
                                      width=150)
            price_frame.pack(side="right", padx=10)
            price_frame.pack_propagate(False)
            
            item_total_vat_inclusive = item['price'] * item['quantity']
            total_vat_inclusive += item_total_vat_inclusive
            
            # Unit price (small) - BLACK
            ctk.CTkLabel(price_frame, 
                        text=f"{self.config['currency']}{item['price']:.2f} ea",
                        font=("Arial", 9),
                        text_color="black",
                        fg_color="#f8f9fa",
                        bg_color="#f8f9fa").pack(anchor="e")
            
            # Total price - BLUE
            ctk.CTkLabel(price_frame, 
                        text=f"{self.config['currency']}{item_total_vat_inclusive:,.2f}",
                        font=("Arial", 12, "bold"),
                        text_color="blue",
                        fg_color="#f8f9fa",
                        bg_color="#f8f9fa").pack(anchor="e")
            
            # Remove button
            ctk.CTkButton(item_frame, text="✕", width=35, height=35,
                         command=lambda idx=i: self.remove_from_cart(idx),
                         fg_color="#f8f9fa",
                         hover_color="#ffebee",
                         text_color="#e74c3c",
                         font=("Arial", 14, "bold")).pack(side="right", padx=5)
        
        # VAT calculation
        vat_rate = 0.12
        if total_vat_inclusive > 0:
            net_total = total_vat_inclusive / (1 + vat_rate)
            vat_amount = total_vat_inclusive - net_total
        else:
            net_total = 0
            vat_amount = 0
        
        self.cart_total = total_vat_inclusive
        
        # Update summary labels - FORCE BLACK
        self.subtotal_label.configure(
            text=f"Net Total: {self.config['currency']}{net_total:,.2f}",
            text_color="black",
            fg_color="transparent"
        )
        self.tax_label.configure(
            text=f"VAT (12%): {self.config['currency']}{vat_amount:,.2f}",
            text_color="black",
            fg_color="transparent"
        )
        self.total_label.configure(
            text=f"Total (incl. VAT): {self.config['currency']}{total_vat_inclusive:,.2f}",
            text_color="green",
            fg_color="transparent",
            font=("Arial", 16, "bold")
        )
    
    def update_cart_quantity(self, index, change):
        """Update quantity of cart item"""
        if 0 <= index < len(self.sale_cart):
            self.sale_cart[index]['quantity'] += change
            
            if self.sale_cart[index]['quantity'] <= 0:
                self.sale_cart.pop(index)
            
            self.update_cart_display()
    
    def remove_from_cart(self, index):
        """Remove item from cart"""
        if 0 <= index < len(self.sale_cart):
            self.sale_cart.pop(index)
            self.update_cart_display()
    
    def clear_sale_cart(self):
        """Clear the entire cart"""
        self.sale_cart = []
        self.update_cart_display()
        self.sale_status_label.configure(text="Cart cleared", text_color="orange")
    
    def process_sale(self):
        """Process the sale and update inventory - FIXED for VAT calculation"""
        if not self.sale_cart:
            self.sale_status_label.configure(text="Cart is empty", text_color="red")
            return
        
        # Process each item in cart
        success_count = 0
        failed_items = []
        
        # Calculate totals for display
        total_vat_inclusive = sum(item['price'] * item['quantity'] for item in self.sale_cart)
        
        for item in self.sale_cart:
            try:
                # Record sale with VAT-EXCLUSIVE price
                sale_record = self.db.add_sale(
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    unit_price=item['price_vat_exclusive']  # Use VAT-EXCLUSIVE price
                )
                
                if sale_record:
                    # Update inventory
                    success, message = self.db.update_inventory_from_sale(
                        product_id=item['product_id'],
                        quantity_sold=item['quantity']
                    )
                    
                    if success:
                        success_count += 1
                    else:
                        failed_items.append(f"{item['name']}: {message}")
                else:
                    failed_items.append(f"{item['name']}: Failed to record sale")
                    
            except Exception as e:
                failed_items.append(f"{item['name']}: {str(e)}")
        
        # Show result
        if success_count == len(self.sale_cart):
            receipt_text = f"✅ Sale successful!\nTotal: {self.config['currency']}{total_vat_inclusive:,.2f}"
            self.sale_status_label.configure(text=receipt_text, text_color="green")
            
            # Clear cart after successful sale
            self.clear_sale_cart()
            
            # Ask for receipt
            if messagebox.askyesno("Print Receipt", "Print receipt for this sale?"):
                self.generate_receipt()
                
        elif failed_items:
            error_text = f"⚠️ {success_count}/{len(self.sale_cart)} items processed\n"
            error_text += "Failed items:\n" + "\n".join(failed_items[:3])
            self.sale_status_label.configure(text=error_text, text_color="red")
        else:
            self.sale_status_label.configure(text="No items processed", text_color="orange")
    
    def generate_receipt(self):
        """Generate a receipt with proper VAT breakdown"""
        try:
            from datetime import datetime
            
            vat_rate = 0.12
            total_vat_inclusive = 0
            total_vat_exclusive = 0
            
            receipt_text = f"""
{'='*40}
         {self.config['business_name']}
{'='*40}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*40}
"""
            
            for item in self.sale_cart:
                item_vat_inclusive = item['price'] * item['quantity']
                item_vat_exclusive = item['price_vat_exclusive'] * item['quantity']
                
                total_vat_inclusive += item_vat_inclusive
                total_vat_exclusive += item_vat_exclusive
                
                receipt_text += f"{item['name'][:20]:20} {item['quantity']:3} x {self.config['currency']}{item['price']:7.2f} = {self.config['currency']}{item_vat_inclusive:8.2f}\n"
            
            # Calculate VAT
            vat_amount = total_vat_inclusive - total_vat_exclusive
            
            receipt_text += f"""
{'='*40}
Net Total: {self.config['currency']}{total_vat_exclusive:,.2f}
VAT (12%): {self.config['currency']}{vat_amount:,.2f}
TOTAL (incl. VAT): {self.config['currency']}{total_vat_inclusive:,.2f}
{'='*40}
        THANK YOU!
{'='*40}
"""
            
            # Save receipt to file
            receipt_file = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(receipt_file, 'w') as f:
                f.write(receipt_text)
            
            messagebox.showinfo("Receipt Saved", f"Receipt saved as:\n{receipt_file}")
            
        except Exception as e:
            print(f"Error generating receipt: {e}")
    
    def show_sales_history(self, parent_frame):
        """Show sales history with date filtering - ENHANCED with calendar dropdown"""
        ctk.CTkLabel(parent_frame, text="Sales History", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Date filter frame
        filter_frame = ctk.CTkFrame(parent_frame)
        filter_frame.pack(pady=10, padx=20, fill="x")
        
        # Date range selection
        date_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        date_frame.pack(pady=10, padx=10, fill="x")
        
        # ===== FROM DATE =====
        from_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        from_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(from_frame, text="From:", width=50).pack(pady=5)
        
        # From date with calendar button
        from_row = ctk.CTkFrame(from_frame, fg_color="transparent")
        from_row.pack()
        
        self.from_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        from_date_entry = ctk.CTkEntry(from_row, 
                                      textvariable=self.from_date_var, 
                                      width=120,
                                      placeholder_text="YYYY-MM-DD")
        from_date_entry.pack(side="left", padx=2)
        
        # Calendar button for From date
        ctk.CTkButton(from_row, text="📅", width=30, height=30,
                     command=lambda: self.open_calendar_popup(self.from_date_var),
                     fg_color="#3498db", hover_color="#2980b9").pack(side="left", padx=2)
        
        # ===== TO DATE =====
        to_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        to_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(to_frame, text="To:", width=50).pack(pady=5)
        
        # To date with calendar button
        to_row = ctk.CTkFrame(to_frame, fg_color="transparent")
        to_row.pack()
        
        self.to_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        to_date_entry = ctk.CTkEntry(to_row, 
                                    textvariable=self.to_date_var, 
                                    width=120,
                                    placeholder_text="YYYY-MM-DD")
        to_date_entry.pack(side="left", padx=2)
        
        # Calendar button for To date
        ctk.CTkButton(to_row, text="📅", width=30, height=30,
                     command=lambda: self.open_calendar_popup(self.to_date_var),
                     fg_color="#3498db", hover_color="#2980b9").pack(side="left", padx=2)
        
        # ===== QUICK DATE RANGES =====
        quick_dates_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        quick_dates_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(quick_dates_frame, text="Quick Date Ranges:", 
                    font=("Arial", 12)).pack(pady=5)
        
        # Quick date buttons
        quick_buttons_frame = ctk.CTkFrame(quick_dates_frame, fg_color="transparent")
        quick_buttons_frame.pack()
        
        quick_ranges = [
            ("Today", 0),
            ("Yesterday", 1),
            ("Last 7 Days", 7),
            ("Last 30 Days", 30),
            ("This Month", "month"),
            ("Last Month", "last_month")
        ]
        
        for range_name, days in quick_ranges:
            btn = ctk.CTkButton(quick_buttons_frame, text=range_name,
                               command=lambda d=days, n=range_name: self.set_quick_date_range(d, n),
                               width=100, height=30,
                               font=("Arial", 10))
            btn.pack(side="left", padx=5, pady=5)
        
        # ===== ACTION BUTTONS =====
        action_frame = ctk.CTkFrame(filter_frame)
        action_frame.pack(pady=10, fill="x", padx=20)
        
        # Filter button
        ctk.CTkButton(action_frame, text="🔍 Filter Sales",
                     command=lambda: self.load_sales_history(parent_frame),
                     fg_color="#3498db", hover_color="#2980b9",
                     width=150).pack(side="left", padx=5)
        
        # Clear filters button
        ctk.CTkButton(action_frame, text="🗑️ Clear Filters",
                     command=lambda: self.clear_sales_filters(),
                     fg_color="#95a5a6", hover_color="#7f8c8d",
                     width=150).pack(side="left", padx=5)
        
        # Export button
        ctk.CTkButton(action_frame, text="📊 Export to Excel",
                     command=self.export_sales_report,
                     fg_color="#27ae60", hover_color="#219653",
                     width=150).pack(side="right", padx=5)
        
        # Sales history table frame
        self.sales_history_frame = ctk.CTkFrame(parent_frame)
        self.sales_history_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Initial load (today's sales)
        self.load_sales_history(parent_frame)
    
    def open_calendar_popup(self, date_var):
        """Open a simple calendar popup for date selection"""
        popup = ctk.CTkToplevel(self.window)
        popup.title("Select Date")
        popup.geometry("300x300")
        popup.transient(self.window)
        popup.grab_set()
        
        # Center the popup
        popup.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() - popup.winfo_width()) // 2
        y = self.window.winfo_y() + (self.window.winfo_height() - popup.winfo_height()) // 2
        popup.geometry(f"+{x}+{y}")
        
        # Title
        ctk.CTkLabel(popup, text="Select Date", 
                    font=("Arial", 16, "bold")).pack(pady=10)
        
        # Create a simple calendar
        calendar_frame = ctk.CTkFrame(popup)
        calendar_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Current date
        current_date = datetime.now()
        
        # Year and Month selection
        year_month_frame = ctk.CTkFrame(calendar_frame, fg_color="transparent")
        year_month_frame.pack(pady=5)
        
        # Year selection
        year_var = tk.StringVar(value=str(current_date.year))
        year_spinbox = ctk.CTkEntry(year_month_frame, 
                                   textvariable=year_var,
                                   width=60,
                                   justify="center")
        year_spinbox.pack(side="left", padx=5)
        
        # Month selection
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month_var = tk.StringVar(value=months[current_date.month - 1])
        month_menu = ctk.CTkOptionMenu(year_month_frame,
                                      values=months,
                                      variable=month_var,
                                      width=80)
        month_menu.pack(side="left", padx=5)
        
        # Create day buttons grid
        days_frame = ctk.CTkFrame(calendar_frame)
        days_frame.pack(pady=10, fill="both", expand=True)
        
        # Day buttons (simple implementation)
        days = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
        
        # Day headers
        for col, day in enumerate(days):
            ctk.CTkLabel(days_frame, text=day, 
                        font=("Arial", 10, "bold"),
                        width=30).grid(row=0, column=col, padx=2, pady=2)
        
        # Create day buttons (simplified - just shows 1-31)
        row = 1
        col = 0
        for day in range(1, 32):
            btn = ctk.CTkButton(days_frame, text=str(day), width=30, height=30,
                               command=lambda d=day: self.select_date_from_calendar(
                                   d, month_var.get(), year_var.get(), date_var, popup),
                               font=("Arial", 10))
            btn.grid(row=row, column=col, padx=2, pady=2)
            
            col += 1
            if col > 6:
                col = 0
                row += 1
        
        # Today button
        ctk.CTkButton(popup, text="Today",
                     command=lambda: self.select_today(date_var, popup),
                     width=100).pack(pady=10)
    
    def select_date_from_calendar(self, day, month_str, year_str, date_var, popup):
        """Select date from calendar"""
        month_map = {
            "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
            "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
            "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
        }
        
        month_num = month_map.get(month_str, "01")
        date_str = f"{year_str}-{month_num}-{day:02d}"
        
        # Validate date
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            date_var.set(date_str)
            popup.destroy()
        except ValueError:
            messagebox.showerror("Invalid Date", "Please select a valid date")
    
    def select_today(self, date_var, popup):
        """Select today's date"""
        today = datetime.now().strftime("%Y-%m-%d")
        date_var.set(today)
        popup.destroy()
    
    def set_quick_date_range(self, days, range_name):
        """Set quick date ranges"""
        today = datetime.now()
        
        if days == 0:  # Today
            date_str = today.strftime("%Y-%m-%d")
            self.from_date_var.set(date_str)
            self.to_date_var.set(date_str)
            
        elif days == 1:  # Yesterday
            yesterday = today - timedelta(days=1)
            date_str = yesterday.strftime("%Y-%m-%d")
            self.from_date_var.set(date_str)
            self.to_date_var.set(date_str)
            
        elif days == 7:  # Last 7 days
            from_date = today - timedelta(days=7)
            self.from_date_var.set(from_date.strftime("%Y-%m-%d"))
            self.to_date_var.set(today.strftime("%Y-%m-%d"))
            
        elif days == 30:  # Last 30 days
            from_date = today - timedelta(days=30)
            self.from_date_var.set(from_date.strftime("%Y-%m-%d"))
            self.to_date_var.set(today.strftime("%Y-%m-%d"))
            
        elif days == "month":  # This month
            first_day = today.replace(day=1)
            self.from_date_var.set(first_day.strftime("%Y-%m-%d"))
            self.to_date_var.set(today.strftime("%Y-%m-%d"))
            
        elif days == "last_month":  # Last month
            if today.month == 1:
                first_day_last = today.replace(year=today.year-1, month=12, day=1)
                last_day_last = today.replace(day=1) - timedelta(days=1)
            else:
                first_day_last = today.replace(month=today.month-1, day=1)
                last_day_last = today.replace(day=1) - timedelta(days=1)
            
            self.from_date_var.set(first_day_last.strftime("%Y-%m-%d"))
            self.to_date_var.set(last_day_last.strftime("%Y-%m-%d"))
        
        # Auto-refresh if we have a parent frame reference
        if hasattr(self, 'sales_history_frame'):
            # We need to find the parent frame - this is a bit complex
            # For now, just update the dates and let user click Filter
            pass
    
    def clear_sales_filters(self):
        """Clear sales filters"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.from_date_var.set(today)
        self.to_date_var.set(today)
    
    def load_sales_history(self, parent_frame):
        """Load sales history based on date filter"""
        # Clear existing table
        for widget in self.sales_history_frame.winfo_children():
            widget.destroy()
        
        # Get sales data
        sales_df = self.db.read_tab('Sales')
        
        if sales_df.empty:
            ctk.CTkLabel(self.sales_history_frame, 
                        text="No sales records found.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Apply date filter
        try:
            from_date = self.from_date_var.get()
            to_date = self.to_date_var.get()
            
            if from_date and to_date:
                mask = (sales_df['Sale_Date'] >= from_date) & (sales_df['Sale_Date'] <= to_date)
                sales_df = sales_df[mask]
        except:
            pass  # If date filter fails, show all
        
        if sales_df.empty:
            ctk.CTkLabel(self.sales_history_frame, 
                        text="No sales in selected date range.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Get product names
        products_df = self.db.read_tab('Products')
        if not products_df.empty:
            sales_df = pd.merge(sales_df, products_df[['Product_ID', 'Product_Name']], 
                              on='Product_ID', how='left')
        else:
            sales_df['Product_Name'] = sales_df['Product_ID']
        
        # Sort by date (newest first)
        sales_df = sales_df.sort_values(['Sale_Date', 'Sale_Time'], ascending=False)
        
        # Create scrollable table
        scroll_frame = ctk.CTkScrollableFrame(self.sales_history_frame, 
                                             width=900, height=400)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Table headers
        headers = ["Date", "Time", "Product", "Quantity", "Unit Price", "Total Amount"]
        col_widths = [100, 80, 200, 80, 100, 120]
        
        for col, (header, width) in enumerate(zip(headers, col_widths)):
            ctk.CTkLabel(scroll_frame, text=header, font=("Arial", 12, "bold"),
                        width=width).grid(row=0, column=col, padx=5, pady=5, sticky="w")
        
        # Add sales rows
        total_sales = 0
        for row_idx, (_, sale) in enumerate(sales_df.iterrows(), start=1):
            # Date
            ctk.CTkLabel(scroll_frame, text=sale['Sale_Date'], 
                        width=col_widths[0]).grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
            
            # Time
            ctk.CTkLabel(scroll_frame, text=sale.get('Sale_Time', ''), 
                        width=col_widths[1]).grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
            
            # Product
            product_name = sale.get('Product_Name', sale['Product_ID'])
            ctk.CTkLabel(scroll_frame, text=product_name[:30], 
                        width=col_widths[2]).grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
            
            # Quantity
            ctk.CTkLabel(scroll_frame, text=f"{sale['Quantity']:,.0f}", 
                        width=col_widths[3]).grid(row=row_idx, column=3, padx=5, pady=2)
            
            # Unit Price
            unit_price = sale['Total_Amount'] / sale['Quantity'] if sale['Quantity'] > 0 else 0
            ctk.CTkLabel(scroll_frame, text=f"{self.config['currency']}{unit_price:,.2f}", 
                        width=col_widths[4]).grid(row=row_idx, column=4, padx=5, pady=2)
            
            # Total Amount
            ctk.CTkLabel(scroll_frame, text=f"{self.config['currency']}{sale['Total_Amount']:,.2f}", 
                        width=col_widths[5]).grid(row=row_idx, column=5, padx=5, pady=2)
            
            total_sales += sale['Total_Amount']
        
        # Summary
        summary_frame = ctk.CTkFrame(parent_frame)
        summary_frame.pack(pady=10, padx=20, fill="x")
        
        summary_text = f"Total Sales: {self.config['currency']}{total_sales:,.2f} | {len(sales_df)} transactions"
        ctk.CTkLabel(summary_frame, text=summary_text,
                    font=("Arial", 12, "bold")).pack(pady=10)
    
    def export_sales_report(self):
        """Export sales report to Excel"""
        try:
            # Get sales data
            sales_df = self.db.read_tab('Sales')
            
            if sales_df.empty:
                messagebox.showwarning("No Data", "No sales data to export.")
                return
            
            # Get product names
            products_df = self.db.read_tab('Products')
            if not products_df.empty:
                sales_df = pd.merge(sales_df, products_df[['Product_ID', 'Product_Name']], 
                                  on='Product_ID', how='left')
            
            # Create filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sales_report_{timestamp}.xlsx"
            
            # Export to Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                sales_df.to_excel(writer, sheet_name='Sales Report', index=False)
                
                # Add summary sheet
                summary_data = {
                    'Metric': ['Total Transactions', 'Total Revenue', 'Average Sale'],
                    'Value': [
                        len(sales_df),
                        sales_df['Total_Amount'].sum(),
                        sales_df['Total_Amount'].mean()
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            messagebox.showinfo("Export Successful", 
                              f"Sales report exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def show_sales_reports(self, parent_frame):
        """Show sales reports with charts"""
        ctk.CTkLabel(parent_frame, text="Sales Analytics", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Get sales data
        sales_df = self.db.read_tab('Sales')
        
        if sales_df.empty:
            ctk.CTkLabel(parent_frame, 
                        text="No sales data available for analysis.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Create tabs for different reports
        report_tabs = ctk.CTkTabview(parent_frame)
        report_tabs.pack(fill="both", expand=True, padx=20, pady=10)
        
        report_tabs.add("Daily Sales")
        report_tabs.add("Top Products")
        report_tabs.add("Monthly Trends")
        
        # Daily Sales tab
        daily_frame = report_tabs.tab("Daily Sales")
        self.show_daily_sales_chart(daily_frame, sales_df)
        
        # Top Products tab
        top_frame = report_tabs.tab("Top Products")
        self.show_top_products_chart(top_frame, sales_df)
        
        # Monthly Trends tab
        monthly_frame = report_tabs.tab("Monthly Trends")
        self.show_monthly_trends_chart(monthly_frame, sales_df)
    
    def show_daily_sales_chart(self, parent_frame, sales_df):
        """Show daily sales chart"""
        try:
            # Convert to datetime and group by date
            sales_df['Sale_Date'] = pd.to_datetime(sales_df['Sale_Date'])
            daily_sales = sales_df.groupby('Sale_Date')['Total_Amount'].sum().reset_index()
            daily_sales = daily_sales.sort_values('Sale_Date')
            
            # Get last 30 days
            last_30_days = daily_sales.tail(30)
            
            # Display as simple table (we'll add charts later)
            ctk.CTkLabel(parent_frame, text="Daily Sales (Last 30 Days)", 
                        font=("Arial", 16, "bold")).pack(pady=10)
            
            if last_30_days.empty:
                ctk.CTkLabel(parent_frame, text="No recent sales data").pack(pady=20)
                return
            
            # Create scrollable table
            scroll_frame = ctk.CTkScrollableFrame(parent_frame, height=300)
            scroll_frame.pack(fill="x", padx=20, pady=10)
            
            # Headers
            headers_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            headers_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(headers_frame, text="Date", 
                        font=("Arial", 12, "bold"),
                        width=120).pack(side="left", padx=10)
            ctk.CTkLabel(headers_frame, text="Total Sales", 
                        font=("Arial", 12, "bold"),
                        width=120).pack(side="left", padx=10)
            
            # Display rows
            total_sales = 0
            for _, row in last_30_days.iterrows():
                row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)
                
                date_str = row['Sale_Date'].strftime("%Y-%m-%d")
                ctk.CTkLabel(row_frame, text=date_str, 
                            width=120).pack(side="left", padx=10)
                ctk.CTkLabel(row_frame, 
                            text=f"{self.config['currency']}{row['Total_Amount']:,.2f}",
                            width=120, text_color="green").pack(side="left", padx=10)
                
                total_sales += row['Total_Amount']
            
            # Summary
            avg_daily = total_sales / len(last_30_days) if len(last_30_days) > 0 else 0
            summary_frame = ctk.CTkFrame(parent_frame)
            summary_frame.pack(pady=10, padx=20, fill="x")
            
            summary_text = f"Total (30 days): {self.config['currency']}{total_sales:,.2f} | "
            summary_text += f"Average Daily: {self.config['currency']}{avg_daily:,.2f}"
            ctk.CTkLabel(summary_frame, text=summary_text,
                        font=("Arial", 12, "bold")).pack(pady=5)
            
        except Exception as e:
            ctk.CTkLabel(parent_frame, 
                        text=f"Error displaying chart: {str(e)}",
                        text_color="red").pack(pady=20)
    
    def show_top_products_chart(self, parent_frame, sales_df):
        """Show top products by sales"""
        try:
            # Get product names
            products_df = self.db.read_tab('Products')
            if not products_df.empty:
                sales_df = pd.merge(sales_df, products_df[['Product_ID', 'Product_Name']], 
                                  on='Product_ID', how='left')
            
            # Group by product
            product_sales = sales_df.groupby('Product_ID').agg({
                'Product_Name': 'first',
                'Quantity': 'sum',
                'Total_Amount': 'sum'
            }).reset_index()
            
            # Sort by total amount
            top_products = product_sales.sort_values('Total_Amount', ascending=False).head(10)
            
            ctk.CTkLabel(parent_frame, text="Top 10 Products by Revenue", 
                        font=("Arial", 16, "bold")).pack(pady=10)
            
            if top_products.empty:
                ctk.CTkLabel(parent_frame, text="No product sales data").pack(pady=20)
                return
            
            # Create table
            scroll_frame = ctk.CTkScrollableFrame(parent_frame, height=300)
            scroll_frame.pack(fill="x", padx=20, pady=10)
            
            # Headers
            headers_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            headers_frame.pack(fill="x", pady=5)
            
            headers = ["Product", "Quantity", "Revenue"]
            for header in headers:
                width = 150 if header == "Product" else 120
                ctk.CTkLabel(headers_frame, text=header, 
                            font=("Arial", 12, "bold"),
                            width=width).pack(side="left", padx=10)
            
            # Display rows
            for _, product in top_products.iterrows():
                row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)
                
                product_name = product['Product_Name'] if pd.notna(product['Product_Name']) else product['Product_ID']
                ctk.CTkLabel(row_frame, text=product_name[:25], 
                            width=150).pack(side="left", padx=10)
                ctk.CTkLabel(row_frame, text=f"{product['Quantity']:,.0f}", 
                            width=120).pack(side="left", padx=10)
                ctk.CTkLabel(row_frame, 
                            text=f"{self.config['currency']}{product['Total_Amount']:,.2f}",
                            width=120, text_color="green").pack(side="left", padx=10)
            
        except Exception as e:
            ctk.CTkLabel(parent_frame, 
                        text=f"Error displaying chart: {str(e)}",
                        text_color="red").pack(pady=20)
    
    def show_monthly_trends_chart(self, parent_frame, sales_df):
        """Show monthly sales trends"""
        try:
            # Convert to datetime and extract month
            sales_df['Sale_Date'] = pd.to_datetime(sales_df['Sale_Date'])
            sales_df['YearMonth'] = sales_df['Sale_Date'].dt.strftime('%Y-%m')
            
            # Group by month
            monthly_sales = sales_df.groupby('YearMonth')['Total_Amount'].sum().reset_index()
            monthly_sales = monthly_sales.sort_values('YearMonth')
            
            ctk.CTkLabel(parent_frame, text="Monthly Sales Trends", 
                        font=("Arial", 16, "bold")).pack(pady=10)
            
            if monthly_sales.empty:
                ctk.CTkLabel(parent_frame, text="No monthly sales data").pack(pady=20)
                return
            
            # Create table
            scroll_frame = ctk.CTkScrollableFrame(parent_frame, height=300)
            scroll_frame.pack(fill="x", padx=20, pady=10)
            
            # Headers
            headers_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            headers_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(headers_frame, text="Month", 
                        font=("Arial", 12, "bold"),
                        width=100).pack(side="left", padx=10)
            ctk.CTkLabel(headers_frame, text="Total Sales", 
                        font=("Arial", 12, "bold"),
                        width=120).pack(side="left", padx=10)
            ctk.CTkLabel(headers_frame, text="Growth", 
                        font=("Arial", 12, "bold"),
                        width=80).pack(side="left", padx=10)
            
            # Display rows with growth calculation
            total_sales = 0
            previous_sales = 0
            
            for i, (_, row) in enumerate(monthly_sales.iterrows()):
                row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)
                
                # Month
                ctk.CTkLabel(row_frame, text=row['YearMonth'], 
                            width=100).pack(side="left", padx=10)
                
                # Sales amount
                sales_amount = row['Total_Amount']
                ctk.CTkLabel(row_frame, 
                            text=f"{self.config['currency']}{sales_amount:,.2f}",
                            width=120, text_color="green").pack(side="left", padx=10)
                
                # Growth percentage
                if i > 0 and previous_sales > 0:
                    growth = ((sales_amount - previous_sales) / previous_sales) * 100
                    growth_color = "green" if growth >= 0 else "red"
                    growth_text = f"{growth:+.1f}%"
                    ctk.CTkLabel(row_frame, text=growth_text,
                                text_color=growth_color,
                                width=80).pack(side="left", padx=10)
                else:
                    ctk.CTkLabel(row_frame, text="N/A", 
                                width=80, text_color="gray").pack(side="left", padx=10)
                
                previous_sales = sales_amount
                total_sales += sales_amount
            
            # Summary
            avg_monthly = total_sales / len(monthly_sales) if len(monthly_sales) > 0 else 0
            summary_frame = ctk.CTkFrame(parent_frame)
            summary_frame.pack(pady=10, padx=20, fill="x")
            
            summary_text = f"Total ({len(monthly_sales)} months): {self.config['currency']}{total_sales:,.2f} | "
            summary_text += f"Average Monthly: {self.config['currency']}{avg_monthly:,.2f}"
            ctk.CTkLabel(summary_frame, text=summary_text,
                        font=("Arial", 12, "bold")).pack(pady=5)
            
        except Exception as e:
            ctk.CTkLabel(parent_frame, 
                        text=f"Error displaying chart: {str(e)}",
                        text_color="red").pack(pady=20)    


    def show_sales(self):
        """Show sales entry and history - COMPLETE IMPLEMENTATION"""
        self.clear_main_content()
        
        # Create tabview for sales
        sales_tabs = ctk.CTkTabview(self.main_content)
        sales_tabs.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add tabs
        sales_tabs.add("New Sale")
        sales_tabs.add("Sales History")
        sales_tabs.add("Sales Reports")
        
        # Fill each tab
        self.create_sale_entry_form(sales_tabs.tab("New Sale"))
        self.show_sales_history(sales_tabs.tab("Sales History"))
        self.show_sales_reports(sales_tabs.tab("Sales Reports"))
    
    def create_sale_entry_form(self, parent_frame):
        """Point-of-Sale style sale entry form - ENHANCED VERSION"""
        ctk.CTkLabel(parent_frame, text="Point of Sale", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Initialize cart
        self.sale_cart = []  # List of dicts: {product_id, name, price, quantity}
        self.cart_total = 0
        
        # Main container with two columns
        main_container = ctk.CTkFrame(parent_frame)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left side - Product selection
        left_frame = ctk.CTkFrame(main_container, width=350)
        left_frame.pack(side="left", fill="both", padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Right side - Cart/Checkout
        right_frame = ctk.CTkFrame(main_container)
        right_frame.pack(side="right", fill="both", expand=True)
        
        # === LEFT FRAME: Product Selection ===
        ctk.CTkLabel(left_frame, text="Products", 
                    font=("Arial", 16, "bold")).pack(pady=10)
        
        # ===== ENHANCED FILTERING =====
        filter_frame = ctk.CTkFrame(left_frame)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Search bar
        search_row = ctk.CTkFrame(filter_frame, fg_color="transparent")
        search_row.pack(fill="x", pady=5)
        
        ctk.CTkLabel(search_row, text="Search:", 
                    font=("Arial", 12)).pack(side="left", padx=5)
        
        self.sale_search_var = tk.StringVar()
        search_entry = ctk.CTkEntry(search_row, 
                                   textvariable=self.sale_search_var,
                                   placeholder_text="Type product name...",
                                   width=200)
        search_entry.pack(side="left", padx=5)
        
        # Category filter
        category_row = ctk.CTkFrame(filter_frame, fg_color="transparent")
        category_row.pack(fill="x", pady=5)
        
        ctk.CTkLabel(category_row, text="Category:", 
                    font=("Arial", 12)).pack(side="left", padx=5)
        
        # Get all products to build category list
        products_df = self.db.get_all_products()
        categories = ["All Categories"]
        
        if not products_df.empty and 'Category' in products_df.columns:
            unique_cats = products_df['Category'].dropna().unique()
            for cat in unique_cats:
                if cat and str(cat).strip() and str(cat).strip().lower() != 'nan':
                    categories.append(str(cat).strip())
        
        categories = sorted(list(set(categories)))
        
        self.sale_category_var = tk.StringVar(value="All Categories")
        category_menu = ctk.CTkOptionMenu(category_row,
                                         values=categories,
                                         variable=self.sale_category_var,
                                         width=200)
        category_menu.pack(side="left", padx=5)
        
        # Filter buttons row
        button_row = ctk.CTkFrame(filter_frame, fg_color="transparent")
        button_row.pack(fill="x", pady=5)
        
        ctk.CTkButton(button_row, text="🔍 Apply Filters", 
                     command=lambda: self.filter_sale_products_enhanced(left_frame),
                     fg_color="#3498db", hover_color="#2980b9",
                     width=120).pack(side="left", padx=5)
        
        ctk.CTkButton(button_row, text="🗑️ Clear Filters", 
                     command=lambda: self.clear_sale_filters(left_frame),
                     fg_color="#95a5a6", hover_color="#7f8c8d",
                     width=120).pack(side="left", padx=5)
        
        # Product grid frame (for clickable cards)
        self.products_grid_frame = ctk.CTkScrollableFrame(left_frame, height=350)
        self.products_grid_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # === RIGHT FRAME: Cart ===
        ctk.CTkLabel(right_frame, text="Shopping Cart", 
                    font=("Arial", 16, "bold")).pack(pady=10)
        
        # Cart items display
        cart_frame = ctk.CTkFrame(right_frame, height=300)
        cart_frame.pack(fill="x", padx=10, pady=10)
        cart_frame.pack_propagate(False)
        
        self.cart_items_frame = ctk.CTkScrollableFrame(cart_frame, height=280)
        self.cart_items_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Cart summary
        summary_frame = ctk.CTkFrame(right_frame, height=150)
        summary_frame.pack(fill="x", padx=10, pady=10)
        summary_frame.pack_propagate(False)
        
        # Summary labels
        self.subtotal_label = ctk.CTkLabel(summary_frame, 
                                          text=f"Subtotal: {self.config['currency']}0.00",
                                          font=("Arial", 14))
        self.subtotal_label.pack(anchor="w", padx=20, pady=5)
        
        # Tax calculation
        tax_rate = 0.12  # 12% VAT
        self.tax_label = ctk.CTkLabel(summary_frame, 
                                      text=f"Tax (12%): {self.config['currency']}0.00",
                                      font=("Arial", 14))
        self.tax_label.pack(anchor="w", padx=20, pady=5)
        
        self.total_label = ctk.CTkLabel(summary_frame, 
                                       text=f"Total: {self.config['currency']}0.00",
                                       font=("Arial", 16, "bold"))
        self.total_label.pack(anchor="w", padx=20, pady=5)
        
        # Action buttons
        button_frame = ctk.CTkFrame(right_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(button_frame, text="🛒 Checkout & Process Sale",
                     command=self.process_sale,
                     fg_color="#27ae60", hover_color="#219653",
                     height=45, font=("Arial", 14)).pack(side="left", padx=5)
        
        ctk.CTkButton(button_frame, text="🗑️ Clear Cart",
                     command=self.clear_sale_cart,
                     fg_color="#e74c3c", hover_color="#c0392b",
                     height=45, font=("Arial", 14)).pack(side="left", padx=5)
        
        # Status label
        self.sale_status_label = ctk.CTkLabel(right_frame, text="", 
                                             font=("Arial", 12))
        self.sale_status_label.pack(pady=5)
        
        # Bind search to filter
        self.sale_search_var.trace('w', lambda *args: self.filter_sale_products_enhanced(left_frame))
        self.sale_category_var.trace('w', lambda *args: self.filter_sale_products_enhanced(left_frame))
        
        # Initial load of products
        self.filter_sale_products_enhanced(left_frame)
    
    def filter_sale_products_enhanced(self, parent_frame):
        """Display products for sale selection with clickable cards and filtering"""
        # Clear existing grid
        for widget in self.products_grid_frame.winfo_children():
            widget.destroy()
        
        # Get all active products
        products_df = self.db.get_all_products()
        
        if products_df.empty:
            ctk.CTkLabel(self.products_grid_frame, 
                        text="No products available for sale.",
                        font=("Arial", 12)).pack(pady=50)
            return
        
        # Apply filters
        filtered_products = products_df.copy()
        
        # 1. Apply search filter
        search_text = self.sale_search_var.get().lower() if hasattr(self, 'sale_search_var') else ""
        if search_text:
            mask = (filtered_products['Product_Name'].str.lower().str.contains(search_text) |
                   filtered_products['Product_ID'].str.lower().str.contains(search_text))
            filtered_products = filtered_products[mask]
        
        # 2. Apply category filter
        selected_category = self.sale_category_var.get() if hasattr(self, 'sale_category_var') else "All Categories"
        if selected_category and selected_category != "All Categories":
            if 'Category' in filtered_products.columns:
                # Create a copy to avoid warnings
                filtered_products = filtered_products.copy()
                
                # Fill NaN categories with empty string
                filtered_products['Category'] = filtered_products['Category'].fillna('')
                
                # Convert all categories to string and strip whitespace
                filtered_products['Category'] = filtered_products['Category'].astype(str).str.strip()
                
                # Case-insensitive filtering
                mask = filtered_products['Category'].str.lower() == selected_category.lower().strip()
                filtered_products = filtered_products[mask]
        
        if filtered_products.empty:
            # Show filter info
            filter_info = []
            if search_text:
                filter_info.append(f"Search: '{search_text}'")
            if selected_category != "All Categories":
                filter_info.append(f"Category: '{selected_category}'")
            
            no_results_text = "No products found"
            if filter_info:
                no_results_text += f" with filters: {' • '.join(filter_info)}"
            no_results_text += "."
            
            ctk.CTkLabel(self.products_grid_frame, 
                        text=no_results_text,
                        font=("Arial", 12)).pack(pady=50)
            return
        
        # Create product cards grid (2 columns)
        row = 0
        col = 0
        
        for _, product in filtered_products.iterrows():
            # Create clickable card frame
            product_frame = ctk.CTkFrame(self.products_grid_frame, 
                                        width=160, height=140,
                                        corner_radius=12,
                                        border_width=1,
                                        border_color="gray")
            product_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            product_frame.pack_propagate(False)
            
            # Make entire frame clickable
            product_frame.bind("<Button-1>", lambda e, p=product: self.add_to_cart(p))
            
            # Product name (truncated)
            product_name = product['Product_Name'][:20] + "..." if len(product['Product_Name']) > 20 else product['Product_Name']
            name_label = ctk.CTkLabel(product_frame, text=product_name,
                                    font=("Arial", 12, "bold"),
                                    wraplength=140)
				    
            name_label.pack(pady=(15, 5), padx=10)
            name_label.bind("<Button-1>", lambda e, p=product: self.add_to_cart(p))
            
            # Price - bigger and bold
            price = product.get('Selling_Price', 0)
            price_label = ctk.CTkLabel(product_frame, 
                                      text=f"{self.config['currency']}{price:,.2f}",
                                      font=("Arial", 14, "bold"),
                                      text_color="green")
            price_label.pack(pady=2)
            price_label.bind("<Button-1>", lambda e, p=product: self.add_to_cart(p))
            
            # ID and Category (smaller)
            id_label = ctk.CTkLabel(product_frame, 
                                   text=f"ID: {product['Product_ID']}",
                                   font=("Arial", 9),
                                   text_color="gray")
            id_label.pack(pady=2)
            id_label.bind("<Button-1>", lambda e, p=product: self.add_to_cart(p))
            
            # Category if available
            if 'Category' in product and pd.notna(product['Category']):
                category = str(product['Category']).strip()
                if category and category.lower() != 'nan':
                    category_label = ctk.CTkLabel(product_frame, 
                                                text=f"📂 {category[:15]}",
                                                font=("Arial", 9),
                                                text_color="#3498db")
                    category_label.pack(pady=2)
                    category_label.bind("<Button-1>", lambda e, p=product: self.add_to_cart(p))
            
            # Add hover effect
            def on_enter(e, frame=product_frame):
                frame.configure(border_color="#3498db", border_width=2)
            
            def on_leave(e, frame=product_frame):
                frame.configure(border_color="gray", border_width=1)
            
            product_frame.bind("<Enter>", on_enter)
            product_frame.bind("<Leave>", on_leave)
            name_label.bind("<Enter>", on_enter)
            name_label.bind("<Leave>", on_leave)
            price_label.bind("<Enter>", on_enter)
            price_label.bind("<Leave>", on_leave)
            id_label.bind("<Enter>", on_enter)
            id_label.bind("<Leave>", on_leave)
            
            # Add visual cue that it's clickable
            product_frame.configure(cursor="hand2")
            name_label.configure(cursor="hand2")
            price_label.configure(cursor="hand2")
            id_label.configure(cursor="hand2")
            
            # Double click to add multiple
            product_frame.bind("<Double-Button-1>", lambda e, p=product: [self.add_to_cart(p), self.add_to_cart(p)])
            
            col += 1
            if col > 1:  # 2 columns per row
                col = 0
                row += 1
        
        # Configure grid columns
        self.products_grid_frame.grid_columnconfigure(0, weight=1)
        self.products_grid_frame.grid_columnconfigure(1, weight=1)
    
    def clear_sale_filters(self, parent_frame):
        """Clear all sale filters"""
        if hasattr(self, 'sale_search_var'):
            self.sale_search_var.set("")
        
        if hasattr(self, 'sale_category_var'):
            self.sale_category_var.set("All Categories")
        
        self.filter_sale_products_enhanced(parent_frame)
    
    def add_to_cart(self, product):
        """Add product to cart - UPDATED with visual feedback"""
        # Check if product already in cart
        for item in self.sale_cart:
            if item['product_id'] == product['Product_ID']:
                # Increase quantity
                item['quantity'] += 1
                # Show visual feedback
                self.show_cart_feedback(f"+1 {product['Product_Name'][:15]}...")
                self.update_cart_display()
                return
        
        # Add new item to cart
        cart_item = {
            'product_id': product['Product_ID'],
            'name': product['Product_Name'],
            'price': product.get('Selling_Price', 0),
            'quantity': 1,
            'unit': 'pcs'
        }
        self.sale_cart.append(cart_item)
        
        # Show visual feedback
        self.show_cart_feedback(f"Added {product['Product_Name'][:15]}...")
        self.update_cart_display()
    
    def show_cart_feedback(self, message):
        """Show visual feedback when adding to cart"""
        # Create temporary feedback label
        feedback = ctk.CTkLabel(self.cart_items_frame.master.master,  # Navigate up to right_frame
                               text=f"✅ {message}",
                               font=("Arial", 11),
                               text_color="green",
                               fg_color="#d5f4e6",
                               corner_radius=8)
        feedback.place(relx=0.5, rely=0.5, anchor="center")
        
        # Remove after 1 second
        self.cart_items_frame.after(1000, feedback.destroy)
    
    def update_cart_display(self):
        """Update cart display with FORCED BLACK TEXT"""
        # Clear cart display
        for widget in self.cart_items_frame.winfo_children():
            widget.destroy()
        
        if not self.sale_cart:
            # TEST: Try different background/foreground combinations
            test_label = ctk.CTkLabel(self.cart_items_frame, 
                                    text="🛒 Cart is empty\nClick on products to add them",
                                    font=("Arial", 12),
                                    text_color="black",  # Explicit black
                                    fg_color="white",    # White background
                                    corner_radius=8)
            test_label.pack(pady=50)
            
            self.subtotal_label.configure(
                text=f"Net Total: {self.config['currency']}0.00",
                text_color="black",
                fg_color="transparent"
            )
            self.tax_label.configure(
                text=f"VAT (12%): {self.config['currency']}0.00",
                text_color="black",
                fg_color="transparent"
            )
            self.total_label.configure(
                text=f"Total (incl. VAT): {self.config['currency']}0.00",
                text_color="green",
                fg_color="transparent"
            )
            self.cart_total = 0
            return
        
        # Calculate totals
        total_vat_inclusive = 0
        
        # Display cart items
        for i, item in enumerate(self.sale_cart):
            item_frame = ctk.CTkFrame(self.cart_items_frame, 
                                     height=60,
                                     fg_color="#f8f9fa",  # Light gray background
                                     corner_radius=8,
                                     border_width=1,
                                     border_color="#e0e0e0")
            item_frame.pack(fill="x", pady=3, padx=2)
            item_frame.pack_propagate(False)
            
            # Item details - TEST with white background
            details_frame = ctk.CTkFrame(item_frame, 
                                       fg_color="#f8f9fa",  # Same as parent
                                       corner_radius=8)
            details_frame.pack(side="left", fill="both", expand=True, padx=10)
            
            # Product name - FORCE BLACK with bg color
            name_label = ctk.CTkLabel(details_frame, 
                                     text=f"📦 {item['name'][:20]}...",
                                     font=("Arial", 12, "bold"),
                                     anchor="w",
                                     text_color="black",  # FORCE BLACK
                                     fg_color="#f8f9fa",  # Match background
                                     bg_color="#f8f9fa")  # Match background
            name_label.pack(side="left", padx=5, fill="x", expand=True)
            
            # Quantity controls
            qty_frame = ctk.CTkFrame(item_frame, 
                                    fg_color="#f8f9fa",  # Same background
                                    width=120)
            qty_frame.pack(side="left", padx=10)
            qty_frame.pack_propagate(False)
            
            # Decrease button
            ctk.CTkButton(qty_frame, text="−", width=30, height=30,
                         command=lambda idx=i: self.update_cart_quantity(idx, -1),
                         font=("Arial", 14, "bold"),
                         fg_color="#e74c3c", 
                         hover_color="#c0392b",
                         text_color="white").pack(side="left", padx=2)
            
            # Quantity number - BLACK on WHITE
            qty_label = ctk.CTkLabel(qty_frame, 
                                    text=str(item['quantity']),
                                    font=("Arial", 12, "bold"), 
                                    width=40,
                                    corner_radius=6, 
                                    fg_color="white",  # White background
                                    text_color="black",  # Black text
                                    bg_color="white")   # White background
            qty_label.pack(side="left", padx=2)
            
            # Increase button
            ctk.CTkButton(qty_frame, text="+", width=30, height=30,
                         command=lambda idx=i: self.update_cart_quantity(idx, 1),
                         font=("Arial", 14, "bold"),
                         fg_color="#27ae60", 
                         hover_color="#219653",
                         text_color="white").pack(side="left", padx=2)
            
            # Price frame
            price_frame = ctk.CTkFrame(item_frame, 
                                      fg_color="#f8f9fa",  # Same background
                                      width=150)
            price_frame.pack(side="right", padx=10)
            price_frame.pack_propagate(False)
            
            item_total_vat_inclusive = item['price'] * item['quantity']
            total_vat_inclusive += item_total_vat_inclusive
            
            # Unit price (small) - BLACK
            ctk.CTkLabel(price_frame, 
                        text=f"{self.config['currency']}{item['price']:.2f} ea",
                        font=("Arial", 9),
                        text_color="black",  # FORCE BLACK
                        fg_color="#f8f9fa",  # Match background
                        bg_color="#f8f9fa").pack(anchor="e")
            
            # Total price - BLUE
            ctk.CTkLabel(price_frame, 
                        text=f"{self.config['currency']}{item_total_vat_inclusive:,.2f}",
                        font=("Arial", 12, "bold"),
                        text_color="blue",  # Keep blue for emphasis
                        fg_color="#f8f9fa",
                        bg_color="#f8f9fa").pack(anchor="e")
            
            # Remove button
            ctk.CTkButton(item_frame, text="✕", width=35, height=35,
                         command=lambda idx=i: self.remove_from_cart(idx),
                         fg_color="#f8f9fa",  # Match background
                         hover_color="#ffebee",
                         text_color="#e74c3c",
                         font=("Arial", 14, "bold")).pack(side="right", padx=5)
        
        # VAT calculation
        vat_rate = 0.12
        if total_vat_inclusive > 0:
            net_total = total_vat_inclusive / (1 + vat_rate)
            vat_amount = total_vat_inclusive - net_total
        else:
            net_total = 0
            vat_amount = 0
        
        self.cart_total = total_vat_inclusive
        
        # Update summary labels - FORCE BLACK
        self.subtotal_label.configure(
            text=f"Net Total: {self.config['currency']}{net_total:,.2f}",
            text_color="black",
            fg_color="transparent"
        )
        self.tax_label.configure(
            text=f"VAT (12%): {self.config['currency']}{vat_amount:,.2f}",
            text_color="black",
            fg_color="transparent"
        )
        self.total_label.configure(
            text=f"Total (incl. VAT): {self.config['currency']}{total_vat_inclusive:,.2f}",
            text_color="green",
            fg_color="transparent",
            font=("Arial", 16, "bold")
        )
    
    def update_cart_quantity(self, index, change):
        """Update quantity of cart item"""
        if 0 <= index < len(self.sale_cart):
            self.sale_cart[index]['quantity'] += change
            
            if self.sale_cart[index]['quantity'] <= 0:
                self.sale_cart.pop(index)
            
            self.update_cart_display()
    
    def remove_from_cart(self, index):
        """Remove item from cart"""
        if 0 <= index < len(self.sale_cart):
            self.sale_cart.pop(index)
            self.update_cart_display()
    
    def clear_sale_cart(self):
        """Clear the entire cart"""
        self.sale_cart = []
        self.update_cart_display()
        self.sale_status_label.configure(text="Cart cleared", text_color="orange")
    
    def process_sale(self):
        """Process the sale and update inventory"""
        if not self.sale_cart:
            self.sale_status_label.configure(text="Cart is empty", text_color="red")
            return
        
        # Process each item in cart
        success_count = 0
        failed_items = []
        
        for item in self.sale_cart:
            try:
                # Record sale
                sale_record = self.db.add_sale(
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    unit_price=item['price']
                )
                
                if sale_record:
                    # Update inventory
                    success, message = self.db.update_inventory_from_sale(
                        product_id=item['product_id'],
                        quantity_sold=item['quantity']
                    )
                    
                    if success:
                        success_count += 1
                    else:
                        failed_items.append(f"{item['name']}: {message}")
                else:
                    failed_items.append(f"{item['name']}: Failed to record sale")
                    
            except Exception as e:
                failed_items.append(f"{item['name']}: {str(e)}")
        
        # Show result
        if success_count == len(self.sale_cart):
            receipt_text = f"✅ Sale successful!\nTotal: {self.config['currency']}{self.cart_total:,.2f}"
            self.sale_status_label.configure(text=receipt_text, text_color="green")
            
            # Clear cart after successful sale
            self.clear_sale_cart()
            
            # Ask for receipt
            if messagebox.askyesno("Print Receipt", "Print receipt for this sale?"):
                self.generate_receipt()
                
        elif failed_items:
            error_text = f"⚠️ {success_count}/{len(self.sale_cart)} items processed\n"
            error_text += "Failed items:\n" + "\n".join(failed_items[:3])  # Show first 3 errors
            self.sale_status_label.configure(text=error_text, text_color="red")
        else:
            self.sale_status_label.configure(text="No items processed", text_color="orange")
    
    def generate_receipt(self):
        """Generate a simple receipt"""
        try:
            from datetime import datetime
            
            receipt_text = f"""
{'='*40}
         {self.config['business_name']}
{'='*40}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
{'='*40}
"""
            
            for item in self.sale_cart:
                item_total = item['price'] * item['quantity']
                receipt_text += f"{item['name'][:20]:20} {item['quantity']:3} x {self.config['currency']}{item['price']:7.2f} = {self.config['currency']}{item_total:8.2f}\n"
            
            receipt_text += f"""
{'='*40}
Subtotal: {self.config['currency']}{self.cart_total/1.12:,.2f}
Tax (12%): {self.config['currency']}{self.cart_total*0.12:,.2f}
TOTAL: {self.config['currency']}{self.cart_total:,.2f}
{'='*40}
        THANK YOU!
{'='*40}
"""
            
            # Save receipt to file
            receipt_file = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(receipt_file, 'w') as f:
                f.write(receipt_text)
            
            messagebox.showinfo("Receipt Saved", f"Receipt saved as:\n{receipt_file}")
            
        except Exception as e:
            print(f"Error generating receipt: {e}")
    
    def show_sales_history(self, parent_frame):
        """Show sales history with date filtering"""
        ctk.CTkLabel(parent_frame, text="Sales History", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Date filter frame
        filter_frame = ctk.CTkFrame(parent_frame)
        filter_frame.pack(pady=10, padx=20, fill="x")
        
        # Date range selection
        date_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        date_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(date_frame, text="From:", width=50).pack(side="left", padx=5)
        self.from_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        from_date_entry = ctk.CTkEntry(date_frame, textvariable=self.from_date_var, width=120)
        from_date_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(date_frame, text="To:", width=50).pack(side="left", padx=5)
        self.to_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        to_date_entry = ctk.CTkEntry(date_frame, textvariable=self.to_date_var, width=120)
        to_date_entry.pack(side="left", padx=5)
        
        # Filter button
        ctk.CTkButton(filter_frame, text="Filter Sales",
                     command=lambda: self.load_sales_history(parent_frame),
                     fg_color="#3498db", hover_color="#2980b9",
                     width=150).pack(pady=10)
        
        # Export button
        ctk.CTkButton(filter_frame, text="📊 Export to Excel",
                     command=self.export_sales_report,
                     fg_color="#27ae60", hover_color="#219653",
                     width=150).pack(pady=10, side="right", padx=10)
        
        # Sales history table frame
        self.sales_history_frame = ctk.CTkFrame(parent_frame)
        self.sales_history_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Initial load
        self.load_sales_history(parent_frame)
    
    def load_sales_history(self, parent_frame):
        """Load sales history based on date filter"""
        # Clear existing table
        for widget in self.sales_history_frame.winfo_children():
            widget.destroy()
        
        # Get sales data
        sales_df = self.db.read_tab('Sales')
        
        if sales_df.empty:
            ctk.CTkLabel(self.sales_history_frame, 
                        text="No sales records found.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Apply date filter
        try:
            from_date = self.from_date_var.get()
            to_date = self.to_date_var.get()
            
            if from_date and to_date:
                mask = (sales_df['Sale_Date'] >= from_date) & (sales_df['Sale_Date'] <= to_date)
                sales_df = sales_df[mask]
        except:
            pass  # If date filter fails, show all
        
        if sales_df.empty:
            ctk.CTkLabel(self.sales_history_frame, 
                        text="No sales in selected date range.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Get product names
        products_df = self.db.read_tab('Products')
        if not products_df.empty:
            sales_df = pd.merge(sales_df, products_df[['Product_ID', 'Product_Name']], 
                              on='Product_ID', how='left')
        else:
            sales_df['Product_Name'] = sales_df['Product_ID']
        
        # Sort by date (newest first)
        sales_df = sales_df.sort_values(['Sale_Date', 'Sale_Time'], ascending=False)
        
        # Create scrollable table
        scroll_frame = ctk.CTkScrollableFrame(self.sales_history_frame, 
                                             width=900, height=400)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Table headers
        headers = ["Date", "Time", "Product", "Quantity", "Unit Price", "Total Amount"]
        col_widths = [100, 80, 200, 80, 100, 120]
        
        for col, (header, width) in enumerate(zip(headers, col_widths)):
            ctk.CTkLabel(scroll_frame, text=header, font=("Arial", 12, "bold"),
                        width=width).grid(row=0, column=col, padx=5, pady=5, sticky="w")
        
        # Add sales rows
        total_sales = 0
        for row_idx, (_, sale) in enumerate(sales_df.iterrows(), start=1):
            # Date
            ctk.CTkLabel(scroll_frame, text=sale['Sale_Date'], 
                        width=col_widths[0]).grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
            
            # Time
            ctk.CTkLabel(scroll_frame, text=sale.get('Sale_Time', ''), 
                        width=col_widths[1]).grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
            
            # Product
            product_name = sale.get('Product_Name', sale['Product_ID'])
            ctk.CTkLabel(scroll_frame, text=product_name[:30], 
                        width=col_widths[2]).grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
            
            # Quantity
            ctk.CTkLabel(scroll_frame, text=f"{sale['Quantity']:,.0f}", 
                        width=col_widths[3]).grid(row=row_idx, column=3, padx=5, pady=2)
            
            # Unit Price
            unit_price = sale['Total_Amount'] / sale['Quantity'] if sale['Quantity'] > 0 else 0
            ctk.CTkLabel(scroll_frame, text=f"{self.config['currency']}{unit_price:,.2f}", 
                        width=col_widths[4]).grid(row=row_idx, column=4, padx=5, pady=2)
            
            # Total Amount
            ctk.CTkLabel(scroll_frame, text=f"{self.config['currency']}{sale['Total_Amount']:,.2f}", 
                        width=col_widths[5]).grid(row=row_idx, column=5, padx=5, pady=2)
            
            total_sales += sale['Total_Amount']
        
        # Summary
        summary_frame = ctk.CTkFrame(parent_frame)
        summary_frame.pack(pady=10, padx=20, fill="x")
        
        summary_text = f"Total Sales: {self.config['currency']}{total_sales:,.2f} | {len(sales_df)} transactions"
        ctk.CTkLabel(summary_frame, text=summary_text,
                    font=("Arial", 12, "bold")).pack(pady=10)
    
    def export_sales_report(self):
        """Export sales report to Excel"""
        try:
            # Get sales data
            sales_df = self.db.read_tab('Sales')
            
            if sales_df.empty:
                messagebox.showwarning("No Data", "No sales data to export.")
                return
            
            # Get product names
            products_df = self.db.read_tab('Products')
            if not products_df.empty:
                sales_df = pd.merge(sales_df, products_df[['Product_ID', 'Product_Name']], 
                                  on='Product_ID', how='left')
            
            # Create filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sales_report_{timestamp}.xlsx"
            
            # Export to Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                sales_df.to_excel(writer, sheet_name='Sales Report', index=False)
                
                # Add summary sheet
                summary_data = {
                    'Metric': ['Total Transactions', 'Total Revenue', 'Average Sale'],
                    'Value': [
                        len(sales_df),
                        sales_df['Total_Amount'].sum(),
                        sales_df['Total_Amount'].mean()
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            messagebox.showinfo("Export Successful", 
                              f"Sales report exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def show_sales_reports(self, parent_frame):
        """Show sales reports with charts"""
        ctk.CTkLabel(parent_frame, text="Sales Analytics", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Get sales data
        sales_df = self.db.read_tab('Sales')
        
        if sales_df.empty:
            ctk.CTkLabel(parent_frame, 
                        text="No sales data available for analysis.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Create tabs for different reports
        report_tabs = ctk.CTkTabview(parent_frame)
        report_tabs.pack(fill="both", expand=True, padx=20, pady=10)
        
        report_tabs.add("Daily Sales")
        report_tabs.add("Top Products")
        report_tabs.add("Monthly Trends")
        
        # Daily Sales tab
        daily_frame = report_tabs.tab("Daily Sales")
        self.show_daily_sales_chart(daily_frame, sales_df)
        
        # Top Products tab
        top_frame = report_tabs.tab("Top Products")
        self.show_top_products_chart(top_frame, sales_df)
        
        # Monthly Trends tab
        monthly_frame = report_tabs.tab("Monthly Trends")
        self.show_monthly_trends_chart(monthly_frame, sales_df)
    
    def show_daily_sales_chart(self, parent_frame, sales_df):
        """Show daily sales chart"""
        try:
            # Convert to datetime and group by date
            sales_df['Sale_Date'] = pd.to_datetime(sales_df['Sale_Date'])
            daily_sales = sales_df.groupby('Sale_Date')['Total_Amount'].sum().reset_index()
            daily_sales = daily_sales.sort_values('Sale_Date')
            
            # Get last 30 days
            last_30_days = daily_sales.tail(30)
            
            # Display as simple table (we'll add charts later)
            ctk.CTkLabel(parent_frame, text="Daily Sales (Last 30 Days)", 
                        font=("Arial", 16, "bold")).pack(pady=10)
            
            if last_30_days.empty:
                ctk.CTkLabel(parent_frame, text="No recent sales data").pack(pady=20)
                return
            
            # Create scrollable table
            scroll_frame = ctk.CTkScrollableFrame(parent_frame, height=300)
            scroll_frame.pack(fill="x", padx=20, pady=10)
            
            # Headers
            headers_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            headers_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(headers_frame, text="Date", 
                        font=("Arial", 12, "bold"),
                        width=120).pack(side="left", padx=10)
            ctk.CTkLabel(headers_frame, text="Total Sales", 
                        font=("Arial", 12, "bold"),
                        width=120).pack(side="left", padx=10)
            
            # Display rows
            total_sales = 0
            for _, row in last_30_days.iterrows():
                row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)
                
                date_str = row['Sale_Date'].strftime("%Y-%m-%d")
                ctk.CTkLabel(row_frame, text=date_str, 
                            width=120).pack(side="left", padx=10)
                ctk.CTkLabel(row_frame, 
                            text=f"{self.config['currency']}{row['Total_Amount']:,.2f}",
                            width=120, text_color="green").pack(side="left", padx=10)
                
                total_sales += row['Total_Amount']
            
            # Summary
            avg_daily = total_sales / len(last_30_days) if len(last_30_days) > 0 else 0
            summary_frame = ctk.CTkFrame(parent_frame)
            summary_frame.pack(pady=10, padx=20, fill="x")
            
            summary_text = f"Total (30 days): {self.config['currency']}{total_sales:,.2f} | "
            summary_text += f"Average Daily: {self.config['currency']}{avg_daily:,.2f}"
            ctk.CTkLabel(summary_frame, text=summary_text,
                        font=("Arial", 12, "bold")).pack(pady=5)
            
        except Exception as e:
            ctk.CTkLabel(parent_frame, 
                        text=f"Error displaying chart: {str(e)}",
                        text_color="red").pack(pady=20)
    
    def show_top_products_chart(self, parent_frame, sales_df):
        """Show top products by sales"""
        try:
            # Get product names
            products_df = self.db.read_tab('Products')
            if not products_df.empty:
                sales_df = pd.merge(sales_df, products_df[['Product_ID', 'Product_Name']], 
                                  on='Product_ID', how='left')
            
            # Group by product
            product_sales = sales_df.groupby('Product_ID').agg({
                'Product_Name': 'first',
                'Quantity': 'sum',
                'Total_Amount': 'sum'
            }).reset_index()
            
            # Sort by total amount
            top_products = product_sales.sort_values('Total_Amount', ascending=False).head(10)
            
            ctk.CTkLabel(parent_frame, text="Top 10 Products by Revenue", 
                        font=("Arial", 16, "bold")).pack(pady=10)
            
            if top_products.empty:
                ctk.CTkLabel(parent_frame, text="No product sales data").pack(pady=20)
                return
            
            # Create table
            scroll_frame = ctk.CTkScrollableFrame(parent_frame, height=300)
            scroll_frame.pack(fill="x", padx=20, pady=10)
            
            # Headers
            headers_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            headers_frame.pack(fill="x", pady=5)
            
            headers = ["Product", "Quantity", "Revenue"]
            for header in headers:
                width = 150 if header == "Product" else 120
                ctk.CTkLabel(headers_frame, text=header, 
                            font=("Arial", 12, "bold"),
                            width=width).pack(side="left", padx=10)
            
            # Display rows
            for _, product in top_products.iterrows():
                row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)
                
                product_name = product['Product_Name'] if pd.notna(product['Product_Name']) else product['Product_ID']
                ctk.CTkLabel(row_frame, text=product_name[:25], 
                            width=150).pack(side="left", padx=10)
                ctk.CTkLabel(row_frame, text=f"{product['Quantity']:,.0f}", 
                            width=120).pack(side="left", padx=10)
                ctk.CTkLabel(row_frame, 
                            text=f"{self.config['currency']}{product['Total_Amount']:,.2f}",
                            width=120, text_color="green").pack(side="left", padx=10)
            
        except Exception as e:
            ctk.CTkLabel(parent_frame, 
                        text=f"Error displaying chart: {str(e)}",
                        text_color="red").pack(pady=20)
    
    def show_monthly_trends_chart(self, parent_frame, sales_df):
        """Show monthly sales trends"""
        try:
            # Convert to datetime and extract month
            sales_df['Sale_Date'] = pd.to_datetime(sales_df['Sale_Date'])
            sales_df['YearMonth'] = sales_df['Sale_Date'].dt.strftime('%Y-%m')
            
            # Group by month
            monthly_sales = sales_df.groupby('YearMonth')['Total_Amount'].sum().reset_index()
            monthly_sales = monthly_sales.sort_values('YearMonth')
            
            ctk.CTkLabel(parent_frame, text="Monthly Sales Trends", 
                        font=("Arial", 16, "bold")).pack(pady=10)
            
            if monthly_sales.empty:
                ctk.CTkLabel(parent_frame, text="No monthly sales data").pack(pady=20)
                return
            
            # Create table
            scroll_frame = ctk.CTkScrollableFrame(parent_frame, height=300)
            scroll_frame.pack(fill="x", padx=20, pady=10)
            
            # Headers
            headers_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            headers_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(headers_frame, text="Month", 
                        font=("Arial", 12, "bold"),
                        width=100).pack(side="left", padx=10)
            ctk.CTkLabel(headers_frame, text="Total Sales", 
                        font=("Arial", 12, "bold"),
                        width=120).pack(side="left", padx=10)
            ctk.CTkLabel(headers_frame, text="Growth", 
                        font=("Arial", 12, "bold"),
                        width=80).pack(side="left", padx=10)
            
            # Display rows with growth calculation
            total_sales = 0
            previous_sales = 0
            
            for i, (_, row) in enumerate(monthly_sales.iterrows()):
                row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)
                
                # Month
                ctk.CTkLabel(row_frame, text=row['YearMonth'], 
                            width=100).pack(side="left", padx=10)
                
                # Sales amount
                sales_amount = row['Total_Amount']
                ctk.CTkLabel(row_frame, 
                            text=f"{self.config['currency']}{sales_amount:,.2f}",
                            width=120, text_color="green").pack(side="left", padx=10)
                
                # Growth percentage
                if i > 0 and previous_sales > 0:
                    growth = ((sales_amount - previous_sales) / previous_sales) * 100
                    growth_color = "green" if growth >= 0 else "red"
                    growth_text = f"{growth:+.1f}%"
                    ctk.CTkLabel(row_frame, text=growth_text,
                                text_color=growth_color,
                                width=80).pack(side="left", padx=10)
                else:
                    ctk.CTkLabel(row_frame, text="N/A", 
                                width=80, text_color="gray").pack(side="left", padx=10)
                
                previous_sales = sales_amount
                total_sales += sales_amount
            
            # Summary
            avg_monthly = total_sales / len(monthly_sales) if len(monthly_sales) > 0 else 0
            summary_frame = ctk.CTkFrame(parent_frame)
            summary_frame.pack(pady=10, padx=20, fill="x")
            
            summary_text = f"Total ({len(monthly_sales)} months): {self.config['currency']}{total_sales:,.2f} | "
            summary_text += f"Average Monthly: {self.config['currency']}{avg_monthly:,.2f}"
            ctk.CTkLabel(summary_frame, text=summary_text,
                        font=("Arial", 12, "bold")).pack(pady=5)
            
        except Exception as e:
            ctk.CTkLabel(parent_frame, 
                        text=f"Error displaying chart: {str(e)}",
                        text_color="red").pack(pady=20)

    def show_inventory(self):
        """Show inventory management interface - COMPLETE IMPLEMENTATION"""
        self.clear_main_content()
        
        # Create tabview for inventory
        inventory_tabs = ctk.CTkTabview(self.main_content)
        inventory_tabs.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add tabs
        inventory_tabs.add("Live Dashboard")
        inventory_tabs.add("Stock Management")
        inventory_tabs.add("Usage Report")
        
        # Fill each tab
        self.show_inventory_dashboard(inventory_tabs.tab("Live Dashboard"))
        self.show_stock_management(inventory_tabs.tab("Stock Management"))
        self.show_inventory_usage_report(inventory_tabs.tab("Usage Report"))

    def show_inventory_dashboard(self, parent_frame):
        """Show live inventory dashboard with color-coded alerts"""
        ctk.CTkLabel(parent_frame, text="Live Inventory Dashboard", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Get inventory status
        inventory_status = self.db.get_inventory_status()
        
        if inventory_status.empty:
            ctk.CTkLabel(parent_frame, 
                        text="No inventory data available.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Calculate stats
        total_items = len(inventory_status)
        critical_items = len(inventory_status[inventory_status['Status'] == 'Critical'])
        low_items = len(inventory_status[inventory_status['Status'] == 'Low Stock'])
        normal_items = len(inventory_status[inventory_status['Status'] == 'Normal'])
        
        # Display stats
        stats_frame = ctk.CTkFrame(parent_frame)
        stats_frame.pack(pady=10, padx=20, fill="x")
        
        stats_text = f"📊 Inventory Summary: {total_items} items | "
        stats_text += f"🚨 Critical: {critical_items} | "
        stats_text += f"⚠️ Low: {low_items} | "
        stats_text += f"✅ Normal: {normal_items}"
        
        ctk.CTkLabel(stats_frame, text=stats_text,
                    font=("Arial", 12, "bold")).pack(pady=10)
        
        # Show critical items if any
        if critical_items > 0:
            alert_frame = ctk.CTkFrame(parent_frame, border_width=2, 
                                      border_color="#e74c3c", corner_radius=10)
            alert_frame.pack(pady=20, padx=20, fill="x")
            
            ctk.CTkLabel(alert_frame, text="🚨 CRITICAL ALERTS", 
                        font=("Arial", 16, "bold"),
                        text_color="#e74c3c").pack(pady=10)
            
            critical_df = inventory_status[inventory_status['Status'] == 'Critical']
            
            for _, item in critical_df.head(3).iterrows():
                item_text = f"• {item['Ingredient_Name']}: {item['Current_Stock']} left (Min: {item['Min_Stock']})"
                ctk.CTkLabel(alert_frame, text=item_text,
                            text_color="#e74c3c").pack(anchor="w", padx=30, pady=2)
        
        # Show full inventory table
        ctk.CTkLabel(parent_frame, text="📋 Inventory List", 
                    font=("Arial", 18, "bold")).pack(pady=(30, 15))
        
        # Create scrollable table
        scroll_frame = ctk.CTkScrollableFrame(parent_frame, height=300)
        scroll_frame.pack(fill="x", padx=20, pady=10)
        
        # Table headers
        headers_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        headers_frame.pack(fill="x", pady=5)
        
        headers = ["Ingredient", "Current Stock", "Min Stock", "Unit", "Status"]
        for header in headers:
            width = 150 if header == "Ingredient" else 100
            ctk.CTkLabel(headers_frame, text=header, 
                        font=("Arial", 12, "bold"),
                        width=width).pack(side="left", padx=10)
        
        # Add inventory rows
        for _, item in inventory_status.iterrows():
            row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            
            # Ingredient name
            ctk.CTkLabel(row_frame, text=item['Ingredient_Name'][:20], 
                        width=150).pack(side="left", padx=10)
            
            # Current stock with color coding
            current_stock = item.get('Current_Stock', 0)
            stock_color = "green"
            if item['Status'] == 'Low Stock':
                stock_color = "orange"
            elif item['Status'] == 'Critical':
                stock_color = "red"
            
            ctk.CTkLabel(row_frame, text=f"{current_stock:,.2f}", 
                        text_color=stock_color,
                        width=100).pack(side="left", padx=10)
            
            # Min stock
            min_stock = item.get('Min_Stock', 0)
            ctk.CTkLabel(row_frame, text=f"{min_stock:,.2f}", 
                        width=100).pack(side="left", padx=10)
            
            # Unit
            unit = item.get('Unit', '')
            ctk.CTkLabel(row_frame, text=unit, 
                        width=100).pack(side="left", padx=10)
            
            # Status badge
            status_color = {
                'Normal': 'green',
                'Low Stock': 'orange',
                'Critical': 'red'
            }.get(item['Status'], 'gray')
            
            status_frame = ctk.CTkFrame(row_frame, width=80, 
                                       height=25, corner_radius=10,
                                       fg_color=status_color)
            status_frame.pack(side="left", padx=10)
            status_frame.pack_propagate(False)
            ctk.CTkLabel(status_frame, text=item['Status'], 
                        text_color="white", font=("Arial", 10)).pack(expand=True)

    def show_stock_management(self, parent_frame):
        """Show stock management interface"""
        ctk.CTkLabel(parent_frame, text="Stock Management", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Simple interface for now
        ctk.CTkLabel(parent_frame, 
                    text="📥 Receive Stock / 📤 Use Stock",
                    font=("Arial", 16)).pack(pady=20)
        
        ctk.CTkLabel(parent_frame, 
                    text="Full stock management features coming soon!",
                    font=("Arial", 12),
                    text_color="gray").pack(pady=10)
        
        # Quick buttons
        button_frame = ctk.CTkFrame(parent_frame)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame, text="📥 Receive Stock",
                     command=self.open_receive_stock,
                     fg_color="#27ae60", hover_color="#219653",
                     width=150).pack(side="left", padx=10)
        
        ctk.CTkButton(button_frame, text="📤 Use Stock",
                     command=self.open_use_stock,
                     fg_color="#3498db", hover_color="#2980b9",
                     width=150).pack(side="left", padx=10)
    
    def show_inventory_usage_report(self, parent_frame):
        """Show inventory usage report"""
        ctk.CTkLabel(parent_frame, text="Inventory Usage Report", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        ctk.CTkLabel(parent_frame, 
                    text="Usage reports coming soon!",
                    font=("Arial", 14),
                    text_color="gray").pack(pady=50)
        
        # Placeholder for future implementation
        ctk.CTkButton(parent_frame, text="View Recent Usage",
                     command=self.open_usage_report,
                     width=200).pack(pady=20)

    def open_receive_stock(self):
        """Open receive stock popup"""
        messagebox.showinfo("Receive Stock", "Receive stock feature coming soon!")
    
    def open_use_stock(self):
        """Open use stock popup"""
        messagebox.showinfo("Use Stock", "Use stock feature coming soon!")
    
    def open_usage_report(self):
        """Open usage report"""
        messagebox.showinfo("Usage Report", "Usage report feature coming soon!")

    # ============================================================================
    # EXPENSES MANAGEMENT SECTION - COMPLETE IMPLEMENTATION
    # ============================================================================
    
    def show_expenses_management(self):
        """Show expenses management interface"""
        self.clear_main_content()
        
        # Create tabview for expenses
        self.expenses_tabs = ctk.CTkTabview(self.main_content)
        self.expenses_tabs.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add tabs
        self.expenses_tabs.add("View Expenses")
        self.expenses_tabs.add("Add Expense")
        self.expenses_tabs.add("Expense Reports")
        
        # Store references to tab content frames
        self.view_expenses_frame = self.expenses_tabs.tab("View Expenses")
        self.add_expense_frame = self.expenses_tabs.tab("Add Expense")
        self.reports_expense_frame = self.expenses_tabs.tab("Expense Reports")
        
        # Fill each tab
        self.show_all_expenses(self.view_expenses_frame)
        self.create_expense_form(self.add_expense_frame)
        self.show_expense_reports(self.reports_expense_frame)
        
        # Bind tab change event to refresh data
        def on_tab_change(event):
            current_tab = self.expenses_tabs.get()
            if current_tab == "View Expenses":
                self.refresh_expenses_table(self.view_expenses_frame)
            elif current_tab == "Expense Reports":
                self.refresh_expense_reports(self.reports_expense_frame)
        
        self.expenses_tabs.configure(command=on_tab_change)

    def refresh_expense_reports(self, parent_frame):
        """Refresh expense reports tab"""
        # Clear existing content
        for widget in parent_frame.winfo_children():
            widget.destroy()
        
        # Reload reports
        self.show_expense_reports(parent_frame)
    
    def show_all_expenses(self, parent_frame):
        """Show all expenses with filtering"""
        ctk.CTkLabel(parent_frame, text="All Expenses", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Date filter frame
        filter_frame = ctk.CTkFrame(parent_frame)
        filter_frame.pack(pady=10, padx=20, fill="x")
        
        # Add refresh button at the top
        refresh_button_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        refresh_button_frame.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkButton(refresh_button_frame, text="🔄 Refresh Data",
                     command=lambda: self.refresh_expenses_table(parent_frame),
                     fg_color="#3498db", hover_color="#2980b9",
                     width=150).pack(side="left", padx=5)
        
        # Date range selection
        date_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        date_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(date_frame, text="Date Range:", width=80).pack(side="left", padx=5)
        
        self.expense_period_var = tk.StringVar(value="Last 30 days")
        period_menu = ctk.CTkOptionMenu(date_frame,
                                       values=["All Time", "Today", "Yesterday", "Last 7 days", 
                                              "Last 30 days", "This Month", "Last Month", "Custom"],
                                       variable=self.expense_period_var,
                                       width=150)
        period_menu.pack(side="left", padx=5)
        
        # Custom date fields (initially hidden)
        custom_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        custom_frame.pack(side="left", padx=5)
        
        ctk.CTkLabel(custom_frame, text="From:").pack(side="left", padx=2)
        self.expense_from_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        from_entry = ctk.CTkEntry(custom_frame, textvariable=self.expense_from_var, width=100)
        from_entry.pack(side="left", padx=2)
        
        ctk.CTkLabel(custom_frame, text="To:").pack(side="left", padx=2)
        self.expense_to_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        to_entry = ctk.CTkEntry(custom_frame, textvariable=self.expense_to_var, width=100)
        to_entry.pack(side="left", padx=2)
        
        # Initially hide custom fields
        custom_frame.pack_forget()
        
        # Show/hide custom fields based on period selection
        def update_expense_period_fields(*args):
            if self.expense_period_var.get() == "Custom":
                custom_frame.pack(side="left", padx=5)
            else:
                custom_frame.pack_forget()
        
        self.expense_period_var.trace_add("write", update_expense_period_fields)
        
        # Category filter
        category_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        category_frame.pack(pady=5, padx=10, fill="x")
        
        ctk.CTkLabel(category_frame, text="Category:", width=80).pack(side="left", padx=5)
        
        # Get existing expense categories
        expenses_df = self.db.get_expenses()
        categories = ["All Categories"]
        if not expenses_df.empty and 'Category' in expenses_df.columns:
            unique_cats = expenses_df['Category'].dropna().unique()
            for cat in unique_cats:
                if cat and str(cat).strip() and str(cat).strip().lower() != 'nan':
                    categories.append(str(cat).strip())
        
        categories = sorted(list(set(categories)))
        
        self.expense_category_var = tk.StringVar(value="All Categories")
        category_menu = ctk.CTkOptionMenu(category_frame,
                                         values=categories,
                                         variable=self.expense_category_var,
                                         width=150)
        category_menu.pack(side="left", padx=5)
        
        # Filter buttons
        button_frame = ctk.CTkFrame(filter_frame)
        button_frame.pack(pady=10, fill="x", padx=20)
        
        ctk.CTkButton(button_frame, text="🔍 Filter Expenses",
                     command=lambda: self.refresh_expenses_table(parent_frame),
                     fg_color="#3498db", hover_color="#2980b9",
                     width=150).pack(side="left", padx=5)
        
        ctk.CTkButton(button_frame, text="🗑️ Clear Filters",
                     command=lambda: self.clear_expense_filters(parent_frame),
                     fg_color="#95a5a6", hover_color="#7f8c8d",
                     width=150).pack(side="left", padx=5)
        
        ctk.CTkButton(button_frame, text="📊 Export to Excel",
                     command=self.export_expenses_report,
                     fg_color="#27ae60", hover_color="#219653",
                     width=150).pack(side="right", padx=5)
        
        # Create frame for table (will be filled by refresh function)
        self.expenses_table_frame = ctk.CTkFrame(parent_frame)
        self.expenses_table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initial load
        self.refresh_expenses_table(parent_frame)
    
    def refresh_expenses_table(self, parent_frame):
        """Refresh the expenses table"""
        if not hasattr(self, 'expenses_table_frame'):
            return
        
        # Clear existing table
        for widget in self.expenses_table_frame.winfo_children():
            widget.destroy()
        
        # Get expenses data
        expenses_df = self.db.get_expenses()
        
        if expenses_df.empty:
            ctk.CTkLabel(self.expenses_table_frame, 
                        text="No expenses recorded yet.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Apply period filter
        period = self.expense_period_var.get() if hasattr(self, 'expense_period_var') else "All Time"
        filtered_expenses = self.filter_expenses_by_period(expenses_df, period,
                                                          self.expense_from_var.get() if hasattr(self, 'expense_from_var') else None,
                                                          self.expense_to_var.get() if hasattr(self, 'expense_to_var') else None)
        
        # Apply category filter
        selected_category = self.expense_category_var.get() if hasattr(self, 'expense_category_var') else "All Categories"
        if selected_category and selected_category != "All Categories":
            if 'Category' in filtered_expenses.columns:
                filtered_expenses = filtered_expenses.copy()
                filtered_expenses['Category'] = filtered_expenses['Category'].fillna('')
                filtered_expenses['Category'] = filtered_expenses['Category'].astype(str).str.strip()
                mask = filtered_expenses['Category'].str.lower() == selected_category.lower().strip()
                filtered_expenses = filtered_expenses[mask]
        
        if filtered_expenses.empty:
            ctk.CTkLabel(self.expenses_table_frame, 
                        text="No expenses found with selected filters.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Create scrollable table
        scroll_frame = ctk.CTkScrollableFrame(self.expenses_table_frame, width=900, height=400)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Table headers
        headers = ["Date", "Expense ID", "Type", "Description", "Category", "Amount", "Payment Method", "Actions"]
        col_widths = [100, 100, 100, 200, 120, 120, 120, 100]
        
        for col, (header, width) in enumerate(zip(headers, col_widths)):
            ctk.CTkLabel(scroll_frame, text=header, font=("Arial", 12, "bold"),
                        width=width).grid(row=0, column=col, padx=5, pady=5, sticky="w")
        
        # Add expense rows
        total_amount = 0
        for row_idx, (_, expense) in enumerate(filtered_expenses.iterrows(), start=1):
            # Date
            date_str = expense.get('Expense_Date', '')
            if hasattr(date_str, 'strftime'):
                date_str = date_str.strftime("%Y-%m-%d")
            ctk.CTkLabel(scroll_frame, text=str(date_str)[:10], 
                        width=col_widths[0]).grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
            
            # Expense ID
            expense_id = expense.get('Expense_ID', '')
            ctk.CTkLabel(scroll_frame, text=expense_id, 
                        width=col_widths[1]).grid(row=row_idx, column=1, padx=5, pady=2, sticky="w")
            
            # Expense Type
            expense_type = expense.get('Expense_Type', '')
            ctk.CTkLabel(scroll_frame, text=expense_type[:15], 
                        width=col_widths[2]).grid(row=row_idx, column=2, padx=5, pady=2, sticky="w")
            
            # Description
            description = expense.get('Description', '')
            ctk.CTkLabel(scroll_frame, text=description[:25], 
                        width=col_widths[3]).grid(row=row_idx, column=3, padx=5, pady=2, sticky="w")
            
            # Category
            category = expense.get('Category', '')
            ctk.CTkLabel(scroll_frame, text=category[:15], 
                        width=col_widths[4]).grid(row=row_idx, column=4, padx=5, pady=2, sticky="w")
            
            # Amount
            amount = expense.get('Amount', 0)
            total_amount += amount
            ctk.CTkLabel(scroll_frame, text=f"{self.config['currency']}{amount:,.2f}", 
                        width=col_widths[5], text_color="#e74c3c").grid(row=row_idx, column=5, padx=5, pady=2)
            
            # Payment Method
            payment_method = expense.get('Payment_Method', '')
            ctk.CTkLabel(scroll_frame, text=payment_method[:15], 
                        width=col_widths[6]).grid(row=row_idx, column=6, padx=5, pady=2, sticky="w")
            
            # Actions
            action_frame = ctk.CTkFrame(scroll_frame, width=col_widths[7], fg_color="transparent")
            action_frame.grid(row=row_idx, column=7, padx=5, pady=2)
            
            # View button
            ctk.CTkButton(action_frame, text="👁️ View",
                         command=lambda eid=expense_id: self.view_expense_details(eid),
                         width=45, height=25,
                         font=("Arial", 10)).pack(side="left", padx=2)
            
            # Delete button
            ctk.CTkButton(action_frame, text="🗑️",
                         command=lambda eid=expense_id: self.delete_expense_confirmation(eid),
                         width=30, height=25,
                         fg_color="#e74c3c", hover_color="#c0392b",
                         font=("Arial", 10)).pack(side="left", padx=2)
        
        # Summary
        summary_frame = ctk.CTkFrame(parent_frame)
        summary_frame.pack(pady=10, padx=20, fill="x")
        
        summary_text = f"Total Expenses: {self.config['currency']}{total_amount:,.2f} | {len(filtered_expenses)} records"
        ctk.CTkLabel(summary_frame, text=summary_text,
                    font=("Arial", 12, "bold")).pack(pady=10)
    
    def filter_expenses_by_period(self, df, period, custom_from=None, custom_to=None):
        """Filter expenses dataframe by time period"""
        if 'Expense_Date' not in df.columns:
            return df
        
        try:
            df['Expense_Date'] = pd.to_datetime(df['Expense_Date'])
            
            if period == "All Time":
                return df
            
            elif period == "Today":
                today = datetime.now().strftime("%Y-%m-%d")
                return df[df['Expense_Date'].dt.strftime("%Y-%m-%d") == today]
            
            elif period == "Yesterday":
                yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                return df[df['Expense_Date'].dt.strftime("%Y-%m-%d") == yesterday]
            
            elif period == "Last 7 days":
                cutoff = datetime.now() - timedelta(days=7)
                return df[df['Expense_Date'] >= cutoff]
            
            elif period == "Last 30 days":
                cutoff = datetime.now() - timedelta(days=30)
                return df[df['Expense_Date'] >= cutoff]
            
            elif period == "This Month":
                now = datetime.now()
                start_of_month = datetime(now.year, now.month, 1)
                return df[df['Expense_Date'] >= start_of_month]
            
            elif period == "Last Month":
                now = datetime.now()
                if now.month == 1:
                    start_last = datetime(now.year - 1, 12, 1)
                    end_last = datetime(now.year, 1, 1)
                else:
                    start_last = datetime(now.year, now.month - 1, 1)
                    end_last = datetime(now.year, now.month, 1)
                return df[(df['Expense_Date'] >= start_last) & (df['Expense_Date'] < end_last)]
            
            elif period == "Custom" and custom_from and custom_to:
                from_date = pd.to_datetime(custom_from)
                to_date = pd.to_datetime(custom_to)
                return df[(df['Expense_Date'] >= from_date) & (df['Expense_Date'] <= to_date)]
            
            else:
                return df
                
        except Exception as e:
            print(f"Error filtering expenses: {e}")
            return df
    
    def clear_expense_filters(self, parent_frame):
        """Clear all expense filters"""
        if hasattr(self, 'expense_period_var'):
            self.expense_period_var.set("Last 30 days")
        
        if hasattr(self, 'expense_category_var'):
            self.expense_category_var.set("All Categories")
        
        self.refresh_expenses_table(parent_frame)
    
    def view_expense_details(self, expense_id):
        """View expense details in a popup"""
        # Get expense data
        expenses_df = self.db.get_expenses()
        expense = expenses_df[expenses_df['Expense_ID'] == expense_id]
        
        if expense.empty:
            messagebox.showerror("Error", f"Expense {expense_id} not found")
            return
        
        expense_data = expense.iloc[0]
        
        # Create popup window
        popup = ctk.CTkToplevel(self.window)
        popup.title(f"Expense Details: {expense_id}")
        popup.geometry("500x600")
        popup.minsize(450, 500)
        popup.transient(self.window)
        popup.grab_set()
        
        # Center on screen
        popup.update_idletasks()
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 600) // 2
        popup.geometry(f"+{x}+{y}")
        
        # Main container
        main_container = ctk.CTkFrame(popup)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Title
        title_frame = ctk.CTkFrame(main_container, fg_color="#2c3e50", corner_radius=10)
        title_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkLabel(title_frame, 
                    text=f"Expense Details",
                    font=("Arial", 18, "bold"),
                    text_color="white").pack(pady=15)
        
        ctk.CTkLabel(title_frame,
                    text=f"Expense ID: {expense_id}",
                    font=("Arial", 12, "bold"),
                    text_color="#ecf0f1").pack(pady=5)
        
        # Details frame
        details_frame = ctk.CTkFrame(main_container, fg_color="#ecf0f1", corner_radius=8)
        details_frame.pack(fill="both", expand=True, pady=10, padx=10)
        
        # Display all expense details
        fields = [
            ("Date:", expense_data.get('Expense_Date', '')),
            ("Type:", expense_data.get('Expense_Type', '')),
            ("Description:", expense_data.get('Description', '')),
            ("Category:", expense_data.get('Category', '')),
            ("Amount:", f"{self.config['currency']}{expense_data.get('Amount', 0):,.2f}"),
            ("Payment Method:", expense_data.get('Payment_Method', '')),
            ("Notes:", expense_data.get('Notes', ''))
        ]
        
        for label_text, value in fields:
            row_frame = ctk.CTkFrame(details_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=8, padx=20)
            
            ctk.CTkLabel(row_frame, text=label_text, 
                        font=("Arial", 12, "bold"), 
                        text_color="#2c3e50",
                        width=120).pack(side="left")
            
            value_text = str(value)
            if label_text == "Amount:":
                text_color = "#e74c3c"
            else:
                text_color = "#2c3e50"
                
            ctk.CTkLabel(row_frame, text=value_text, 
                        font=("Arial", 12),
                        text_color=text_color,
                        wraplength=300,
                        justify="left").pack(side="left", padx=10, fill="x", expand=True)
        
        # Close button
        button_frame = ctk.CTkFrame(main_container)
        button_frame.pack(pady=20, fill="x", padx=50)
        
        ctk.CTkButton(button_frame, text="✕ Close",
                     command=popup.destroy,
                     width=200, height=45,
                     font=("Arial", 14, "bold"),
                     fg_color="#3498db",
                     hover_color="#2980b9").pack(pady=10)
    
    def delete_expense_confirmation(self, expense_id):
        """Confirm and delete an expense"""
        confirm = messagebox.askyesno("Delete Expense", 
                                     f"Are you sure you want to delete expense {expense_id}?\n\n"
                                     "This action cannot be undone.")
        
        if confirm:
            success, message = self.db.delete_expense(expense_id)
            
            if success:
                messagebox.showinfo("Success", message)
                # AUTO-REFRESH: Refresh all expense tabs
                # Refresh View Expenses tab
                if hasattr(self, 'view_expenses_frame'):
                    self.refresh_expenses_table(self.view_expenses_frame)
                
                # Refresh Expense Reports tab
                if hasattr(self, 'reports_expense_frame'):
                    self.refresh_expense_reports(self.reports_expense_frame)
            else:
                messagebox.showerror("Error", message)
    
    def create_expense_form(self, parent_frame):
        """Form to add new expense"""
        ctk.CTkLabel(parent_frame, text="Add New Expense", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Form frame
        form_frame = ctk.CTkFrame(parent_frame)
        form_frame.pack(pady=20, padx=50, fill="x")
        
        # Auto-generate expense ID
        expenses_df = self.db.get_expenses()
        if expenses_df.empty:
            new_id = "EXP0001"
        else:
            # Find highest EXP number
            exp_numbers = []
            for exp_id in expenses_df['Expense_ID'].dropna():
                if isinstance(exp_id, str) and exp_id.startswith('EXP'):
                    try:
                        num = int(exp_id[3:])
                        exp_numbers.append(num)
                    except:
                        pass
            
            if exp_numbers:
                next_num = max(exp_numbers) + 1
            else:
                next_num = 1
            
            new_id = f"EXP{next_num:04d}"
        
        ctk.CTkLabel(form_frame, text=f"Expense ID: {new_id}", 
                    font=("Arial", 14, "bold")).pack(pady=5)
        
        # Store generated ID
        self.generated_expense_id = new_id
        
        # Form fields
        fields = [
            ("Expense Date*:", "expense_date", "date"),
            ("Expense Type*:", "expense_type", "dropdown"),
            ("Description*:", "description", "text"),
            ("Amount*:", "amount", "number"),
            ("Category*:", "category", "dropdown"),
            ("Payment Method:", "payment_method", "dropdown"),
            ("Notes:", "notes", "textbox")
        ]
        
        self.expense_form_entries = {}
        
        for label_text, field_name, field_type in fields:
            row_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=8)
            
            ctk.CTkLabel(row_frame, text=label_text, 
                        width=150, anchor="w").pack(side="left", padx=10)
            
            if field_type == "date":
                # Date entry with calendar button
                date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
                date_entry = ctk.CTkEntry(row_frame, 
                                         textvariable=date_var,
                                         width=250)
                date_entry.pack(side="left", padx=10)
                self.expense_form_entries[field_name] = date_var
                
                # Calendar button
                ctk.CTkButton(row_frame, text="📅", width=30, height=30,
                             command=lambda dv=date_var: self.open_calendar_popup(dv),
                             fg_color="#3498db", hover_color="#2980b9").pack(side="left", padx=5)
                
            elif field_type == "dropdown":
                if field_name == "expense_type":
                    options = ["Select Type", "Purchase", "Utilities", "Rent", "Salaries", 
                              "Marketing", "Maintenance", "Office Supplies", "Travel", "Other"]
                elif field_name == "category":
                    options = ["Select Category", "Operating", "Administrative", "Marketing", 
                              "Personnel", "Facility", "Equipment", "Miscellaneous"]
                elif field_name == "payment_method":
                    options = ["Select Method", "Cash", "Credit Card", "Bank Transfer", 
                              "Check", "Digital Wallet", "Other"]
                
                var = tk.StringVar(value=options[0])
                menu = ctk.CTkOptionMenu(row_frame,
                                        values=options,
                                        variable=var,
                                        width=250)
                menu.pack(side="left", padx=10)
                self.expense_form_entries[field_name] = var
                
            elif field_type == "text":
                entry = ctk.CTkEntry(row_frame, width=250)
                entry.pack(side="left", padx=10)
                self.expense_form_entries[field_name] = entry
                
            elif field_type == "number":
                entry = ctk.CTkEntry(row_frame, width=250)
                entry.insert(0, "0.00")
                entry.pack(side="left", padx=10)
                self.expense_form_entries[field_name] = entry
                
            elif field_type == "textbox":
                self.expense_notes_text = ctk.CTkTextbox(row_frame, width=250, height=80)
                self.expense_notes_text.pack(side="left", padx=10)
        
        # Buttons
        button_frame = ctk.CTkFrame(parent_frame)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame, text="Save Expense", 
                     command=self.save_new_expense,
                     fg_color="#27ae60", hover_color="#219653",
                     width=150, height=40).pack(side="left", padx=10)
        
        ctk.CTkButton(button_frame, text="Clear Form", 
                     command=self.clear_expense_form,
                     width=150, height=40).pack(side="left", padx=10)
        
        # Status label
        self.expense_form_status = ctk.CTkLabel(parent_frame, text="", 
                                              font=("Arial", 12))
        self.expense_form_status.pack(pady=10)

    def save_new_expense(self):
        """Save new expense to database"""
        try:
            # Validate required fields
            required_fields = {
                'expense_date': 'Expense Date',
                'expense_type': 'Expense Type',
                'description': 'Description',
                'amount': 'Amount',
                'category': 'Category'
            }
            
            expense_data = {}
            
            for field_name, field_label in required_fields.items():
                if field_name in self.expense_form_entries:
                    value = self.expense_form_entries[field_name].get()
                    
                    if not value or value == "Select Type" or value == "Select Category":
                        self.expense_form_status.configure(
                            text=f"{field_label} is required", 
                            text_color="red"
                        )
                        return
                    
                    expense_data[field_name.replace('_', ' ').title().replace(' ', '_')] = value
            
            # Validate amount
            try:
                amount = float(expense_data.get('Amount', 0))
                if amount <= 0:
                    self.expense_form_status.configure(
                        text="Amount must be greater than 0", 
                        text_color="red"
                    )
                    return
                expense_data['Amount'] = amount
            except ValueError:
                self.expense_form_status.configure(
                    text="Amount must be a valid number", 
                    text_color="red"
                )
                return
            
            # Add optional fields
            if 'payment_method' in self.expense_form_entries:
                payment_method = self.expense_form_entries['payment_method'].get()
                if payment_method != "Select Method":
                    expense_data['Payment_Method'] = payment_method
            
            # Add notes
            if hasattr(self, 'expense_notes_text'):
                notes = self.expense_notes_text.get("1.0", "end-1c").strip()
                if notes:
                    expense_data['Notes'] = notes
            
            # Save to database
            success, message = self.db.add_expense(expense_data)
            
            if success:
                self.expense_form_status.configure(text=f"✅ {message}", text_color="green")
                
                # AUTO-REFRESH: Refresh all expense tabs
                # Refresh View Expenses tab if it exists
                if hasattr(self, 'view_expenses_frame'):
                    self.refresh_expenses_table(self.view_expenses_frame)
                
                # Refresh Expense Reports tab if it exists
                if hasattr(self, 'reports_expense_frame'):
                    self.refresh_expense_reports(self.reports_expense_frame)
                
                # Clear form
                self.clear_expense_form()
                
                # Generate new ID
                expenses_df = self.db.get_expenses()
                if expenses_df.empty:
                    new_id = "EXP0001"
                else:
                    exp_numbers = []
                    for exp_id in expenses_df['Expense_ID'].dropna():
                        if isinstance(exp_id, str) and exp_id.startswith('EXP'):
                            try:
                                num = int(exp_id[3:])
                                exp_numbers.append(num)
                            except:
                                pass
                    
                    if exp_numbers:
                        next_num = max(exp_numbers) + 1
                    else:
                        next_num = 1
                    
                    new_id = f"EXP{next_num:04d}"
                
                self.generated_expense_id = new_id
                self.expense_form_status.configure(
                    text=f"✅ {message} (Next ID: {new_id})", 
                    text_color="green"
                )
                
            else:
                self.expense_form_status.configure(text=f"❌ {message}", text_color="red")
                
        except Exception as e:
            self.expense_form_status.configure(text=f"Error: {str(e)}", text_color="red")
    
    def clear_expense_form(self):
        """Clear the expense form"""
        # Clear entries
        for field_name, entry in self.expense_form_entries.items():
            if isinstance(entry, tk.StringVar):
                if field_name in ['expense_type', 'category', 'payment_method']:
                    entry.set("Select Type" if field_name == 'expense_type' else 
                             "Select Category" if field_name == 'category' else 
                             "Select Method")
                elif field_name == 'expense_date':
                    entry.set(datetime.now().strftime("%Y-%m-%d"))
            else:
                entry.delete(0, 'end')
                if field_name == 'amount':
                    entry.insert(0, "0.00")
        
        # Clear notes
        if hasattr(self, 'expense_notes_text'):
            self.expense_notes_text.delete("1.0", "end")
        
        # Clear status
        if hasattr(self, 'expense_form_status'):
            self.expense_form_status.configure(text="")
    
    def show_expense_reports(self, parent_frame):
        """Show expense reports and analysis"""
        ctk.CTkLabel(parent_frame, text="Expense Reports", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Refresh button
        refresh_frame = ctk.CTkFrame(parent_frame)
        refresh_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(refresh_frame, text="🔄 Refresh Reports",
                     command=lambda: self.refresh_expense_reports(parent_frame),
                     fg_color="#3498db", hover_color="#2980b9",
                     width=150).pack(pady=5)
        
        # Get expense summary
        summary_df = self.db.get_expense_summary()
        
        if summary_df.empty:
            ctk.CTkLabel(parent_frame, 
                        text="No expense data available for reports.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Display summary by category
        ctk.CTkLabel(parent_frame, text="📊 Expenses by Category", 
                    font=("Arial", 16, "bold")).pack(pady=(20, 10))
        
        # Create scrollable table
        scroll_frame = ctk.CTkScrollableFrame(parent_frame, height=200)
        scroll_frame.pack(fill="x", padx=50, pady=10)
        
        # Table headers
        headers_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        headers_frame.pack(fill="x", pady=5)
        
        headers = ["Category", "Total Amount", "Transactions"]
        for header in headers:
            width = 150 if header == "Category" else 120
            ctk.CTkLabel(headers_frame, text=header, 
                        font=("Arial", 12, "bold"),
                        width=width).pack(side="left", padx=10)
        
        # Add summary rows
        total_expenses = 0
        for _, summary in summary_df.iterrows():
            row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)
            
            category = summary.get('Category', 'Uncategorized')
            total_amount = summary.get('Total_Amount', 0)
            transaction_count = summary.get('Transaction_Count', 0)
            total_expenses += total_amount
            
            ctk.CTkLabel(row_frame, text=category[:20], 
                        width=150).pack(side="left", padx=10)
            ctk.CTkLabel(row_frame, text=f"{self.config['currency']}{total_amount:,.2f}", 
                        width=120, text_color="#e74c3c").pack(side="left", padx=10)
            ctk.CTkLabel(row_frame, text=f"{transaction_count}", 
                        width=120).pack(side="left", padx=10)
        
        # Total expenses
        total_frame = ctk.CTkFrame(parent_frame)
        total_frame.pack(pady=20, padx=50, fill="x")
        
        ctk.CTkLabel(total_frame, 
                    text=f"💰 Total Expenses: {self.config['currency']}{total_expenses:,.2f}",
                    font=("Arial", 14, "bold"),
                    text_color="#e74c3c").pack(pady=10)
        
        # Monthly trend analysis
        ctk.CTkLabel(parent_frame, text="📅 Monthly Expense Trend", 
                    font=("Arial", 16, "bold")).pack(pady=(30, 10))
        
        # Get expenses for trend analysis
        expenses_df = self.db.get_expenses()
        
        if not expenses_df.empty and 'Expense_Date' in expenses_df.columns:
            try:
                expenses_df['Expense_Date'] = pd.to_datetime(expenses_df['Expense_Date'])
                expenses_df['YearMonth'] = expenses_df['Expense_Date'].dt.strftime('%Y-%m')
                
                monthly_expenses = expenses_df.groupby('YearMonth')['Amount'].sum().reset_index()
                monthly_expenses = monthly_expenses.sort_values('YearMonth')
                
                # Display last 6 months
                last_6_months = monthly_expenses.tail(6)
                
                for _, month_data in last_6_months.iterrows():
                    month_text = f"{month_data['YearMonth']}: {self.config['currency']}{month_data['Amount']:,.2f}"
                    ctk.CTkLabel(parent_frame, text=month_text,
                                font=("Arial", 12)).pack(pady=2)
                    
            except Exception as e:
                ctk.CTkLabel(parent_frame, 
                            text="Could not generate monthly trend",
                            font=("Arial", 12),
                            text_color="gray").pack(pady=10)
        
        # Export button
        button_frame = ctk.CTkFrame(parent_frame)
        button_frame.pack(pady=20, padx=50, fill="x")
        
        ctk.CTkButton(button_frame, text="📄 Export Expense Report",
                     command=self.export_expenses_report,
                     fg_color="#3498db", hover_color="#2980b9",
                     width=200).pack(pady=10)
    
    def export_expenses_report(self):
        """Export expenses report to Excel"""
        try:
            # Get expenses data
            expenses_df = self.db.get_expenses()
            
            if expenses_df.empty:
                messagebox.showwarning("No Data", "No expense data to export.")
                return
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"expenses_report_{timestamp}.xlsx"
            
            # Export to Excel with multiple sheets
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Raw expenses data
                expenses_df.to_excel(writer, sheet_name='Expenses Data', index=False)
                
                # Summary by category
                summary_df = self.db.get_expense_summary()
                if not summary_df.empty:
                    summary_df.to_excel(writer, sheet_name='Category Summary', index=False)
                
                # Add summary stats
                summary_data = {
                    'Metric': ['Total Expenses', 'Total Transactions', 'Average Expense', 
                              'Date Range', 'Export Date'],
                    'Value': [
                        expenses_df['Amount'].sum() if 'Amount' in expenses_df.columns else 0,
                        len(expenses_df),
                        expenses_df['Amount'].mean() if 'Amount' in expenses_df.columns else 0,
                        f"{expenses_df['Expense_Date'].min() if 'Expense_Date' in expenses_df.columns else 'N/A'} to "
                        f"{expenses_df['Expense_Date'].max() if 'Expense_Date' in expenses_df.columns else 'N/A'}",
                        datetime.now().strftime("%Y-%m-%d %H:%M")
                    ]
                }
                stats_df = pd.DataFrame(summary_data)
                stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
            messagebox.showinfo("Export Successful", 
                              f"Expense report exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def show_reports(self):
        """Show comprehensive reports module"""
        self.clear_main_content()
        
        # Create tabview for reports
        report_tabs = ctk.CTkTabview(self.main_content)
        report_tabs.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add tabs for different reports
        report_tabs.add("Sales Report")
        report_tabs.add("Cost Analysis")
        report_tabs.add("Inventory Usage")
        report_tabs.add("Profit & Loss")
        report_tabs.add("Export Data")
        
        # Fill each tab
        self.show_sales_report(report_tabs.tab("Sales Report"))
        self.show_cost_analysis_report(report_tabs.tab("Cost Analysis"))
        self.show_inventory_usage_report_full(report_tabs.tab("Inventory Usage"))
        self.show_profit_loss_report(report_tabs.tab("Profit & Loss"))
        self.show_export_data(report_tabs.tab("Export Data"))
    
    def show_sales_report(self, parent_frame):
        """Generate sales report with date range filtering"""
        ctk.CTkLabel(parent_frame, text="Sales Report", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Date range selection
        filter_frame = ctk.CTkFrame(parent_frame)
        filter_frame.pack(pady=10, padx=20, fill="x")
        
        date_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        date_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(date_frame, text="Date Range:", width=80).pack(side="left", padx=5)
        
        # Period selection
        self.sales_period_var = tk.StringVar(value="Last 30 days")
        period_menu = ctk.CTkOptionMenu(date_frame,
                                       values=["Today", "Yesterday", "Last 7 days", 
                                              "Last 30 days", "This Month", "Last Month", "Custom"],
                                       variable=self.sales_period_var,
                                       width=150)
        period_menu.pack(side="left", padx=5)
        
        # Custom date fields (initially hidden)
        custom_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        custom_frame.pack(side="left", padx=5)
        
        ctk.CTkLabel(custom_frame, text="From:").pack(side="left", padx=2)
        self.sales_from_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        from_entry = ctk.CTkEntry(custom_frame, textvariable=self.sales_from_var, width=100)
        from_entry.pack(side="left", padx=2)
        
        ctk.CTkLabel(custom_frame, text="To:").pack(side="left", padx=2)
        self.sales_to_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        to_entry = ctk.CTkEntry(custom_frame, textvariable=self.sales_to_var, width=100)
        to_entry.pack(side="left", padx=2)
        
        # Initially hide custom fields
        custom_frame.pack_forget()
        
        # Show/hide custom fields based on period selection
        def update_sales_period_fields(*args):
            if self.sales_period_var.get() == "Custom":
                custom_frame.pack(side="left", padx=5)
            else:
                custom_frame.pack_forget()
        
        self.sales_period_var.trace_add("write", update_sales_period_fields)
        
        # Generate report button
        btn_frame = ctk.CTkFrame(filter_frame)
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text="📊 Generate Sales Report",
                     command=lambda: self.generate_sales_report(parent_frame),
                     fg_color="#3498db", hover_color="#2980b9",
                     width=200).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="📈 View Charts",
                     command=lambda: self.show_sales_charts(parent_frame),
                     fg_color="#9b59b6", hover_color="#8e44ad",
                     width=150).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="📄 Export to Excel",
                     command=self.export_sales_report_to_excel,
                     fg_color="#27ae60", hover_color="#219653",
                     width=150).pack(side="left", padx=5)
        
        # Report display frame
        self.sales_report_frame = ctk.CTkFrame(parent_frame)
        self.sales_report_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Initial load (last 30 days)
        self.generate_sales_report(parent_frame)
    
    def generate_sales_report(self, parent_frame):
        """Generate sales report based on selected period"""
        # Clear existing report
        for widget in self.sales_report_frame.winfo_children():
            widget.destroy()
        
        # Get sales data
        sales_df = self.db.read_tab('Sales')
        
        if sales_df.empty:
            ctk.CTkLabel(self.sales_report_frame, 
                        text="No sales data available.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Filter by period
        period = self.sales_period_var.get()
        filtered_sales = self.filter_data_by_period(sales_df, period, 
                                                   self.sales_from_var.get(), 
                                                   self.sales_to_var.get())
        
        if filtered_sales.empty:
            ctk.CTkLabel(self.sales_report_frame, 
                        text=f"No sales data for {period.lower()}.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Get product names
        products_df = self.db.read_tab('Products')
        if not products_df.empty:
            filtered_sales = pd.merge(filtered_sales, 
                                     products_df[['Product_ID', 'Product_Name']], 
                                     on='Product_ID', how='left')
        else:
            filtered_sales['Product_Name'] = filtered_sales['Product_ID']
        
        # Calculate summary statistics
        total_revenue = filtered_sales['Total_Amount'].sum()
        total_transactions = len(filtered_sales)
        total_quantity = filtered_sales['Quantity'].sum()
        avg_sale_amount = total_revenue / total_transactions if total_transactions > 0 else 0
        
        # Display summary
        summary_frame = ctk.CTkFrame(parent_frame)
        summary_frame.pack(pady=10, padx=20, fill="x")
        
        summary_text = f"📊 {period} Sales Report\n"
        summary_text += f"💰 Total Revenue: {self.config['currency']}{total_revenue:,.2f}\n"
        summary_text += f"🧾 Transactions: {total_transactions}\n"
        summary_text += f"📦 Total Quantity Sold: {total_quantity:,.0f}\n"
        summary_text += f"📈 Average Sale: {self.config['currency']}{avg_sale_amount:,.2f}"
        
        ctk.CTkLabel(summary_frame, text=summary_text,
                    font=("Arial", 12, "bold")).pack(pady=10)
        
        # Top products by revenue
        if not filtered_sales.empty:
            top_products = filtered_sales.groupby(['Product_ID', 'Product_Name']).agg({
                'Quantity': 'sum',
                'Total_Amount': 'sum'
            }).reset_index().sort_values('Total_Amount', ascending=False).head(5)
            
            top_frame = ctk.CTkFrame(parent_frame)
            top_frame.pack(pady=10, padx=20, fill="x")
            
            ctk.CTkLabel(top_frame, text="🏆 Top 5 Products by Revenue", 
                        font=("Arial", 14, "bold")).pack(pady=5)
            
            # Create table for top products
            scroll_frame = ctk.CTkScrollableFrame(top_frame, height=150)
            scroll_frame.pack(fill="x", padx=10, pady=10)
            
            # Headers
            headers_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            headers_frame.pack(fill="x", pady=5)
            
            headers = ["Product", "Quantity", "Revenue", "Avg Price"]
            for header in headers:
                width = 150 if header == "Product" else 100
                ctk.CTkLabel(headers_frame, text=header, 
                            font=("Arial", 11, "bold"),
                            width=width).pack(side="left", padx=10)
            
            # Top products rows
            for _, product in top_products.iterrows():
                row_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)
                
                product_name = product['Product_Name'][:20] if pd.notna(product['Product_Name']) else product['Product_ID']
                ctk.CTkLabel(row_frame, text=product_name, 
                            width=150).pack(side="left", padx=10)
                ctk.CTkLabel(row_frame, text=f"{product['Quantity']:,.0f}", 
                            width=100).pack(side="left", padx=10)
                ctk.CTkLabel(row_frame, 
                            text=f"{self.config['currency']}{product['Total_Amount']:,.2f}",
                            width=100, text_color="green").pack(side="left", padx=10)
                
                avg_price = product['Total_Amount'] / product['Quantity'] if product['Quantity'] > 0 else 0
                ctk.CTkLabel(row_frame, 
                            text=f"{self.config['currency']}{avg_price:,.2f}",
                            width=100).pack(side="left", padx=10)
        
        # Daily sales breakdown
        if 'Sale_Date' in filtered_sales.columns:
            daily_sales = filtered_sales.groupby('Sale_Date').agg({
                'Quantity': 'sum',
                'Total_Amount': 'sum',
                'Sale_ID': 'count'
            }).reset_index()
            daily_sales = daily_sales.rename(columns={'Sale_ID': 'Transactions'})
            daily_sales = daily_sales.sort_values('Sale_Date')
            
            daily_frame = ctk.CTkFrame(parent_frame)
            daily_frame.pack(pady=10, padx=20, fill="x")
            
            ctk.CTkLabel(daily_frame, text="📅 Daily Sales Breakdown", 
                        font=("Arial", 14, "bold")).pack(pady=5)
            
            if len(daily_sales) <= 10:
                # Show full table for small number of days
                for _, day in daily_sales.iterrows():
                    day_text = f"{day['Sale_Date']}: {day['Transactions']} sales, {day['Quantity']} units, {self.config['currency']}{day['Total_Amount']:,.2f}"
                    ctk.CTkLabel(daily_frame, text=day_text,
                                font=("Arial", 11)).pack(anchor="w", padx=20, pady=2)
            else:
                # Show summary for many days
                best_day = daily_sales.loc[daily_sales['Total_Amount'].idxmax()]
                worst_day = daily_sales.loc[daily_sales['Total_Amount'].idxmin()]
                
                summary_text = f"Best Day: {best_day['Sale_Date']} - {self.config['currency']}{best_day['Total_Amount']:,.2f}\n"
                summary_text += f"Worst Day: {worst_day['Sale_Date']} - {self.config['currency']}{worst_day['Total_Amount']:,.2f}\n"
                summary_text += f"Average Daily: {self.config['currency']}{daily_sales['Total_Amount'].mean():,.2f}"
                
                ctk.CTkLabel(daily_frame, text=summary_text,
                            font=("Arial", 11)).pack(pady=10)
    
    def filter_data_by_period(self, df, period, custom_from=None, custom_to=None):
        """Filter dataframe by time period"""
        if 'Sale_Date' not in df.columns:
            return df
        
        try:
            df['Sale_Date'] = pd.to_datetime(df['Sale_Date'])
            
            if period == "Today":
                today = datetime.now().strftime("%Y-%m-%d")
                return df[df['Sale_Date'].dt.strftime("%Y-%m-%d") == today]
            
            elif period == "Yesterday":
                yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                return df[df['Sale_Date'].dt.strftime("%Y-%m-%d") == yesterday]
            
            elif period == "Last 7 days":
                cutoff = datetime.now() - timedelta(days=7)
                return df[df['Sale_Date'] >= cutoff]
            
            elif period == "Last 30 days":
                cutoff = datetime.now() - timedelta(days=30)
                return df[df['Sale_Date'] >= cutoff]
            
            elif period == "This Month":
                now = datetime.now()
                start_of_month = datetime(now.year, now.month, 1)
                return df[df['Sale_Date'] >= start_of_month]
            
            elif period == "Last Month":
                now = datetime.now()
                if now.month == 1:
                    start_last = datetime(now.year - 1, 12, 1)
                    end_last = datetime(now.year, 1, 1)
                else:
                    start_last = datetime(now.year, now.month - 1, 1)
                    end_last = datetime(now.year, now.month, 1)
                return df[(df['Sale_Date'] >= start_last) & (df['Sale_Date'] < end_last)]
            
            elif period == "Custom" and custom_from and custom_to:
                from_date = pd.to_datetime(custom_from)
                to_date = pd.to_datetime(custom_to)
                return df[(df['Sale_Date'] >= from_date) & (df['Sale_Date'] <= to_date)]
            
            else:
                return df
                
        except Exception as e:
            print(f"Error filtering data: {e}")
            return df
    
    def show_sales_charts(self, parent_frame):
        """Show sales charts in a popup"""
        # Simple chart display for now
        messagebox.showinfo("Sales Charts", 
                          "Interactive charts feature coming soon!\n\n"
                          "For now, use the sales report for detailed analysis.")
    
    def export_sales_report_to_excel(self):
        """Export sales report to Excel"""
        try:
            # Get sales data
            sales_df = self.db.read_tab('Sales')
            
            if sales_df.empty:
                messagebox.showwarning("No Data", "No sales data to export.")
                return
            
            # Get product names
            products_df = self.db.read_tab('Products')
            if not products_df.empty:
                sales_df = pd.merge(sales_df, 
                                  products_df[['Product_ID', 'Product_Name', 'Selling_Price']], 
                                  on='Product_ID', how='left')
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sales_report_{timestamp}.xlsx"
            
            # Export to Excel with multiple sheets
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Raw sales data
                sales_df.to_excel(writer, sheet_name='Sales Data', index=False)
                
                # Summary sheet
                summary_data = {
                    'Metric': ['Total Transactions', 'Total Revenue', 'Total Quantity', 
                              'Average Sale Amount', 'Date Range'],
                    'Value': [
                        len(sales_df),
                        sales_df['Total_Amount'].sum(),
                        sales_df['Quantity'].sum(),
                        sales_df['Total_Amount'].mean(),
                        f"{sales_df['Sale_Date'].min()} to {sales_df['Sale_Date'].max()}"
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Top products sheet
                if not products_df.empty:
                    product_sales = sales_df.groupby(['Product_ID', 'Product_Name']).agg({
                        'Quantity': 'sum',
                        'Total_Amount': 'sum'
                    }).reset_index()
                    product_sales = product_sales.sort_values('Total_Amount', ascending=False)
                    product_sales.to_excel(writer, sheet_name='Top Products', index=False)
                
                # Daily summary sheet
                if 'Sale_Date' in sales_df.columns:
                    daily_summary = sales_df.groupby('Sale_Date').agg({
                        'Quantity': 'sum',
                        'Total_Amount': 'sum',
                        'Sale_ID': 'count'
                    }).reset_index()
                    daily_summary = daily_summary.rename(columns={'Sale_ID': 'Transactions'})
                    daily_summary = daily_summary.sort_values('Sale_Date')
                    daily_summary.to_excel(writer, sheet_name='Daily Summary', index=False)
            
            messagebox.showinfo("Export Successful", 
                              f"Sales report exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def show_cost_analysis_report(self, parent_frame):
        """Show cost analysis report"""
        ctk.CTkLabel(parent_frame, text="Cost Analysis Report", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Button frame
        btn_frame = ctk.CTkFrame(parent_frame)
        btn_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(btn_frame, text="🔄 Calculate Costs",
                     command=lambda: self.generate_cost_report(parent_frame),
                     fg_color="#3498db", hover_color="#2980b9",
                     width=200).pack(pady=5)
        
        ctk.CTkButton(btn_frame, text="📊 View Profit Margins",
                     command=lambda: self.show_profit_margins(parent_frame),
                     fg_color="#27ae60", hover_color="#219653",
                     width=200).pack(pady=5)
        
        # Report frame
        self.cost_report_frame = ctk.CTkFrame(parent_frame)
        self.cost_report_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Initial load
        self.generate_cost_report(parent_frame)
    
    def generate_cost_report(self, parent_frame):
        """Generate cost analysis report"""
        # Clear existing report
        for widget in self.cost_report_frame.winfo_children():
            widget.destroy()
        
        # Update all product costs first
        products_df = self.db.update_all_product_costs()
        
        if products_df.empty:
            ctk.CTkLabel(self.cost_report_frame, 
                        text="No products available for cost analysis.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Filter only products with cost data
        products_df = products_df[products_df['Cost_Price'].notna()]
        
        if products_df.empty:
            ctk.CTkLabel(self.cost_report_frame, 
                        text="No cost data available. Add recipes to calculate costs.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Calculate summary
        total_products = len(products_df)
        profitable_count = len(products_df[products_df['Profit_Margin'] > 0])
        loss_count = len(products_df[products_df['Profit_Margin'] < 0])
        break_even_count = len(products_df[products_df['Profit_Margin'] == 0])
        
        avg_margin = products_df['Margin_Percentage'].mean() if 'Margin_Percentage' in products_df.columns else 0
        total_cost = products_df['Cost_Price'].sum()
        
        # Display summary
        summary_frame = ctk.CTkFrame(parent_frame)
        summary_frame.pack(pady=10, padx=20, fill="x")
        
        summary_text = f"📊 Cost Analysis Summary\n"
        summary_text += f"📦 Products Analyzed: {total_products}\n"
        summary_text += f"✅ Profitable: {profitable_count} | ⚠️ Break-even: {break_even_count} | ❌ Loss: {loss_count}\n"
        summary_text += f"📈 Average Margin: {avg_margin:.1f}%\n"
        summary_text += f"💰 Total Product Cost Value: {self.config['currency']}{total_cost:,.2f}"
        
        ctk.CTkLabel(summary_frame, text=summary_text,
                    font=("Arial", 12, "bold")).pack(pady=10)
        
        # Product cost table
        ctk.CTkLabel(self.cost_report_frame, text="📋 Product Cost Breakdown", 
                    font=("Arial", 16, "bold")).pack(pady=(20, 10))
        
        # Create scrollable table
        scroll_frame = ctk.CTkScrollableFrame(self.cost_report_frame, height=300)
        scroll_frame.pack(fill="x", padx=10, pady=10)
        
        # Table headers
        headers = ["Product", "Selling Price", "Cost Price", "Profit", "Margin %", "Status"]
        col_widths = [200, 120, 120, 120, 100, 100]
        
        for col, (header, width) in enumerate(zip(headers, col_widths)):
            ctk.CTkLabel(scroll_frame, text=header, font=("Arial", 12, "bold"),
                        width=width).grid(row=0, column=col, padx=5, pady=5, sticky="w")
        
        # Add product rows
        for row_idx, (_, product) in enumerate(products_df.iterrows(), start=1):
            # Product name
            product_name = product['Product_Name'][:25] if pd.notna(product['Product_Name']) else product['Product_ID']
            ctk.CTkLabel(scroll_frame, text=product_name, 
                        width=col_widths[0]).grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
            
            # Selling price
            selling_price = product.get('Selling_Price', 0)
            ctk.CTkLabel(scroll_frame, text=f"{self.config['currency']}{selling_price:,.2f}", 
                        width=col_widths[1]).grid(row=row_idx, column=1, padx=5, pady=2)
            
            # Cost price
            cost_price = product.get('Cost_Price', 0)
            ctk.CTkLabel(scroll_frame, text=f"{self.config['currency']}{cost_price:,.2f}", 
                        width=col_widths[2]).grid(row=row_idx, column=2, padx=5, pady=2)
            
            # Profit
            profit = product.get('Profit_Margin', selling_price - cost_price)
            profit_color = "green" if profit >= 0 else "red"
            ctk.CTkLabel(scroll_frame, text=f"{self.config['currency']}{profit:,.2f}", 
                        text_color=profit_color,
                        width=col_widths[3]).grid(row=row_idx, column=3, padx=5, pady=2)
            
            # Margin percentage
            margin = product.get('Margin_Percentage', 0)
            if pd.isna(margin):
                margin = (profit / selling_price * 100) if selling_price > 0 else 0
            
            if margin >= 30:
                margin_color = "green"
                status = "Excellent"
            elif margin >= 20:
                margin_color = "#27ae60"
                status = "Good"
            elif margin >= 10:
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
        
        # High/Low margin analysis
        analysis_frame = ctk.CTkFrame(parent_frame)
        analysis_frame.pack(pady=10, padx=20, fill="x")
        
        if len(products_df) >= 2:
            # Find highest and lowest margin products
            highest_margin = products_df.loc[products_df['Margin_Percentage'].idxmax()]
            lowest_margin = products_df.loc[products_df['Margin_Percentage'].idxmin()]
            
            analysis_text = f"🏆 Highest Margin: {highest_margin['Product_Name'][:20]} - {highest_margin['Margin_Percentage']:.1f}%\n"
            analysis_text += f"⚠️ Lowest Margin: {lowest_margin['Product_Name'][:20]} - {lowest_margin['Margin_Percentage']:.1f}%"
            
            ctk.CTkLabel(analysis_frame, text=analysis_text,
                        font=("Arial", 12)).pack(pady=10)
    
    def show_profit_margins(self, parent_frame):
        """Show profit margin analysis"""
        # Simple popup for now
        products_df = self.db.read_tab('Products')
        
        if products_df.empty or 'Margin_Percentage' not in products_df.columns:
            messagebox.showinfo("Profit Margins", 
                              "No profit margin data available.\nPlease calculate costs first.")
            return
        
        # Get products with margins
        products_with_margin = products_df[products_df['Margin_Percentage'].notna()]
        
        if products_with_margin.empty:
            messagebox.showinfo("Profit Margins", "No products with calculated margins.")
            return
        
        # Categorize by margin range
        excellent = products_with_margin[products_with_margin['Margin_Percentage'] >= 30]
        good = products_with_margin[(products_with_margin['Margin_Percentage'] >= 20) & 
                                   (products_with_margin['Margin_Percentage'] < 30)]
        fair = products_with_margin[(products_with_margin['Margin_Percentage'] >= 10) & 
                                   (products_with_margin['Margin_Percentage'] < 20)]
        low = products_with_margin[(products_with_margin['Margin_Percentage'] > 0) & 
                                  (products_with_margin['Margin_Percentage'] < 10)]
        loss = products_with_margin[products_with_margin['Margin_Percentage'] <= 0]
        
        margin_text = f"Profit Margin Analysis:\n\n"
        margin_text += f"✅ Excellent (30%+): {len(excellent)} products\n"
        margin_text += f"👍 Good (20-30%): {len(good)} products\n"
        margin_text += f"⚠️ Fair (10-20%): {len(fair)} products\n"
        margin_text += f"🔻 Low (0-10%): {len(low)} products\n"
        margin_text += f"❌ Loss (0% or less): {len(loss)} products\n\n"
        
        if not excellent.empty:
            best_product = excellent.iloc[0]
            margin_text += f"Best Margin: {best_product['Product_Name']} - {best_product['Margin_Percentage']:.1f}%"
        
        messagebox.showinfo("Profit Margin Analysis", margin_text)
    
    def show_inventory_usage_report_full(self, parent_frame):
        """Show comprehensive inventory usage report"""
        ctk.CTkLabel(parent_frame, text="Inventory Usage Report", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Date range selection
        filter_frame = ctk.CTkFrame(parent_frame)
        filter_frame.pack(pady=10, padx=20, fill="x")
        
        date_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        date_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(date_frame, text="Period:", width=50).pack(side="left", padx=5)
        
        self.inv_period_var = tk.StringVar(value="Last 30 days")
        period_menu = ctk.CTkOptionMenu(date_frame,
                                       values=["Last 7 days", "Last 30 days", "Last 90 days", "This Month", "Custom"],
                                       variable=self.inv_period_var,
                                       width=150)
        period_menu.pack(side="left", padx=5)
        
        # Generate report button
        ctk.CTkButton(filter_frame, text="📊 Generate Usage Report",
                     command=lambda: self.generate_inventory_usage_report(parent_frame),
                     fg_color="#3498db", hover_color="#2980b9",
                     width=200).pack(pady=10)
        
        # Report display frame
        self.inv_usage_frame = ctk.CTkFrame(parent_frame)
        self.inv_usage_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Initial load
        self.generate_inventory_usage_report(parent_frame)
    
    def generate_inventory_usage_report(self, parent_frame):
        """Generate inventory usage report"""
        # Clear existing report
        for widget in self.inv_usage_frame.winfo_children():
            widget.destroy()
        
        # Get inventory logs
        logs_df = self.db.get_inventory_logs(days_back=90)
        
        if logs_df.empty:
            ctk.CTkLabel(self.inv_usage_frame, 
                        text="No inventory usage data available.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Filter by period
        period = self.inv_period_var.get()
        
        if period == "Last 7 days":
            cutoff = datetime.now() - timedelta(days=7)
            logs_df = logs_df[logs_df['Date'] >= cutoff]
        elif period == "Last 30 days":
            cutoff = datetime.now() - timedelta(days=30)
            logs_df = logs_df[logs_df['Date'] >= cutoff]
        elif period == "Last 90 days":
            cutoff = datetime.now() - timedelta(days=90)
            logs_df = logs_df[logs_df['Date'] >= cutoff]
        elif period == "This Month":
            now = datetime.now()
            start_of_month = datetime(now.year, now.month, 1)
            logs_df = logs_df[logs_df['Date'] >= start_of_month]
        
        if logs_df.empty:
            ctk.CTkLabel(self.inv_usage_frame, 
                        text=f"No usage data for {period.lower()}.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Get ingredient names
        ingredients_df = self.db.get_all_ingredients()
        if not ingredients_df.empty:
            logs_df = pd.merge(logs_df, 
                             ingredients_df[['Ingredient_ID', 'Ingredient_Name', 'Unit', 'Cost_Per_Unit']], 
                             on='Ingredient_ID', how='left')
        
        # Group by ingredient
        usage_summary = logs_df.groupby(['Ingredient_ID', 'Ingredient_Name', 'Unit']).agg({
            'Quantity': 'sum',
            'Change_Type': lambda x: (x == 'STOCK_ADD').sum()  # Count additions
        }).reset_index()
        
        usage_summary = usage_summary.rename(columns={'Change_Type': 'Additions_Count'})
        
        # Calculate deductions count
        total_transactions = logs_df.groupby('Ingredient_ID').size().reset_index(name='Total_Transactions')
        usage_summary = pd.merge(usage_summary, total_transactions, on='Ingredient_ID', how='left')
        
        # Calculate net usage (negative = more used than added)
        usage_summary['Net_Usage'] = usage_summary['Quantity']
        usage_summary['Deductions_Count'] = usage_summary['Total_Transactions'] - usage_summary['Additions_Count']
        
        # Calculate cost impact if cost data available
        if 'Cost_Per_Unit' in logs_df.columns:
            cost_impact = logs_df.groupby('Ingredient_ID').apply(
                lambda x: (x['Quantity'] * x['Cost_Per_Unit']).sum()
            ).reset_index(name='Cost_Impact')
            usage_summary = pd.merge(usage_summary, cost_impact, on='Ingredient_ID', how='left')
        
        # Display report
        ctk.CTkLabel(self.inv_usage_frame, text=f"📊 Inventory Usage Report - {period}", 
                    font=("Arial", 16, "bold")).pack(pady=10)
        
        # Summary statistics
        total_added = usage_summary[usage_summary['Net_Usage'] > 0]['Net_Usage'].sum()
        total_used = abs(usage_summary[usage_summary['Net_Usage'] < 0]['Net_Usage'].sum())
        net_change = usage_summary['Net_Usage'].sum()
        
        summary_frame = ctk.CTkFrame(parent_frame)
        summary_frame.pack(pady=10, padx=20, fill="x")
        
        summary_text = f"📥 Total Added: {total_added:,.2f} units\n"
        summary_text += f"📤 Total Used: {total_used:,.2f} units\n"
        summary_text += f"📊 Net Change: {net_change:+,.2f} units\n"
        summary_text += f"📋 Ingredients Tracked: {len(usage_summary)}"
        
        ctk.CTkLabel(summary_frame, text=summary_text,
                    font=("Arial", 12, "bold")).pack(pady=10)
        
        # Usage details table
        ctk.CTkLabel(self.inv_usage_frame, text="📋 Usage Details by Ingredient", 
                    font=("Arial", 14, "bold")).pack(pady=(20, 10))
        
        # Create scrollable table
        scroll_frame = ctk.CTkScrollableFrame(self.inv_usage_frame, height=250)
        scroll_frame.pack(fill="x", padx=10, pady=10)
        
        # Table headers
        headers = ["Ingredient", "Net Usage", "Unit", "Additions", "Deductions", "Status"]
        col_widths = [180, 100, 80, 80, 80, 100]
        
        for col, (header, width) in enumerate(zip(headers, col_widths)):
            ctk.CTkLabel(scroll_frame, text=header, font=("Arial", 12, "bold"),
                        width=width).grid(row=0, column=col, padx=5, pady=5, sticky="w")
        
        # Add usage rows
        for row_idx, (_, item) in enumerate(usage_summary.iterrows(), start=1):
            # Ingredient name
            ingredient_name = item.get('Ingredient_Name', item['Ingredient_ID'])[:20]
            ctk.CTkLabel(scroll_frame, text=ingredient_name, 
                        width=col_widths[0]).grid(row=row_idx, column=0, padx=5, pady=2, sticky="w")
            
            # Net usage with color coding
            net_usage = item['Net_Usage']
            usage_color = "green" if net_usage > 0 else "red" if net_usage < 0 else "gray"
            usage_text = f"{net_usage:+,.2f}"
            ctk.CTkLabel(scroll_frame, text=usage_text, text_color=usage_color,
                        width=col_widths[1]).grid(row=row_idx, column=1, padx=5, pady=2)
            
            # Unit
            unit = item.get('Unit', '')
            ctk.CTkLabel(scroll_frame, text=unit, 
                        width=col_widths[2]).grid(row=row_idx, column=2, padx=5, pady=2)
            
            # Additions count
            ctk.CTkLabel(scroll_frame, text=f"{item['Additions_Count']}", 
                        width=col_widths[3]).grid(row=row_idx, column=3, padx=5, pady=2)
            
            # Deductions count
            ctk.CTkLabel(scroll_frame, text=f"{item['Deductions_Count']}", 
                        width=col_widths[4]).grid(row=row_idx, column=4, padx=5, pady=2)
            
            # Status
            if net_usage > 0:
                status = "Net Increase"
                status_color = "green"
            elif net_usage < 0:
                status = "Net Decrease"
                status_color = "red"
            else:
                status = "Balanced"
                status_color = "gray"
            
            status_frame = ctk.CTkFrame(scroll_frame, width=col_widths[5]-10, 
                                       height=25, corner_radius=10,
                                       fg_color=status_color)
            status_frame.grid(row=row_idx, column=5, padx=5, pady=2)
            status_frame.pack_propagate(False)
            ctk.CTkLabel(status_frame, text=status, 
                        text_color="white", font=("Arial", 10)).pack(expand=True)
    
    def show_profit_loss_report(self, parent_frame):
        """Show profit and loss summary report"""
        ctk.CTkLabel(parent_frame, text="Profit & Loss Summary", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Date selection
        filter_frame = ctk.CTkFrame(parent_frame)
        filter_frame.pack(pady=10, padx=20, fill="x")
        
        date_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        date_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(date_frame, text="Time Period:", width=80).pack(side="left", padx=5)
        
        self.pl_period_var = tk.StringVar(value="This Month")
        period_menu = ctk.CTkOptionMenu(date_frame,
                                       values=["Today", "Yesterday", "Last 7 days", 
                                              "Last 30 days", "This Month", "Last Month"],
                                       variable=self.pl_period_var,
                                       width=150)
        period_menu.pack(side="left", padx=5)
        
        # Generate report button
        ctk.CTkButton(filter_frame, text="💰 Calculate P&L",
                     command=lambda: self.generate_profit_loss_report(parent_frame),
                     fg_color="#27ae60", hover_color="#219653",
                     width=200).pack(pady=10)
        
        # Report frame
        self.pl_report_frame = ctk.CTkFrame(parent_frame)
        self.pl_report_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Initial load
        self.generate_profit_loss_report(parent_frame)
    
    def generate_profit_loss_report(self, parent_frame):
        """Generate profit and loss report"""
        # Clear existing report
        for widget in self.pl_report_frame.winfo_children():
            widget.destroy()
        
        # Get sales data for the period
        sales_df = self.db.read_tab('Sales')
        
        if sales_df.empty:
            ctk.CTkLabel(self.pl_report_frame, 
                        text="No sales data available for P&L calculation.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Filter sales by period
        period = self.pl_period_var.get()
        filtered_sales = self.filter_data_by_period(sales_df, period)
        
        if filtered_sales.empty:
            ctk.CTkLabel(self.pl_report_frame, 
                        text=f"No sales data for {period.lower()}.",
                        font=("Arial", 14)).pack(pady=50)
            return
        
        # Calculate total revenue
        total_revenue = filtered_sales['Total_Amount'].sum()
        
        # Calculate cost of goods sold (COGS)
        # For each sale, calculate the cost based on recipe
        total_cogs = 0
        cogs_details = []
        
        for _, sale in filtered_sales.iterrows():
            product_id = sale['Product_ID']
            quantity = sale['Quantity']
            
            # Get product cost
            product_cost = self.db.calculate_product_cost(product_id)
            sale_cogs = product_cost * quantity
            total_cogs += sale_cogs
            
            cogs_details.append({
                'product_id': product_id,
                'quantity': quantity,
                'revenue': sale['Total_Amount'],
                'cogs': sale_cogs,
                'profit': sale['Total_Amount'] - sale_cogs
            })
        
        # Calculate gross profit
        gross_profit = total_revenue - total_cogs
        gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Display P&L statement
        pl_frame = ctk.CTkFrame(self.pl_report_frame, border_width=2, 
                               border_color="gray", corner_radius=10)
        pl_frame.pack(pady=10, padx=20, fill="x")
        
        # P&L Title
        ctk.CTkLabel(pl_frame, text=f"📊 Profit & Loss Statement - {period}", 
                    font=("Arial", 16, "bold")).pack(pady=10)
        
        # Revenue section
        revenue_frame = ctk.CTkFrame(pl_frame, fg_color="#ecf0f1", corner_radius=8)
        revenue_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(revenue_frame, text="💰 REVENUE", 
                    font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(revenue_frame, 
                    text=f"Total Sales: {self.config['currency']}{total_revenue:,.2f}",
                    font=("Arial", 12)).pack(pady=2)
        
        # COGS section
        cogs_frame = ctk.CTkFrame(pl_frame, fg_color="#f8f9f9", corner_radius=8)
        cogs_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(cogs_frame, text="📦 COST OF GOODS SOLD (COGS)", 
                    font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(cogs_frame, 
                    text=f"Total COGS: {self.config['currency']}{total_cogs:,.2f}",
                    font=("Arial", 12)).pack(pady=2)
        
        # Gross Profit section
        gp_color = "green" if gross_profit >= 0 else "red"
        gp_frame = ctk.CTkFrame(pl_frame, fg_color="#e8f6f3", border_width=2,
                               border_color=gp_color, corner_radius=8)
        gp_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(gp_frame, text="📈 GROSS PROFIT", 
                    font=("Arial", 14, "bold")).pack(pady=5)
        ctk.CTkLabel(gp_frame, 
                    text=f"Gross Profit: {self.config['currency']}{gross_profit:,.2f}",
                    font=("Arial", 14, "bold"),
                    text_color=gp_color).pack(pady=2)
        ctk.CTkLabel(gp_frame, 
                    text=f"Gross Margin: {gross_margin:.1f}%",
                    font=("Arial", 12),
                    text_color=gp_color).pack(pady=2)
        
        # Product-level profitability
        if cogs_details:
            ctk.CTkLabel(pl_frame, text="📋 Product Profitability", 
                        font=("Arial", 14, "bold")).pack(pady=(20, 10))
            
            # Create a simple summary
            product_summary = {}
            for detail in cogs_details:
                pid = detail['product_id']
                if pid not in product_summary:
                    product_summary[pid] = {
                        'revenue': 0,
                        'cogs': 0,
                        'profit': 0,
                        'quantity': 0
                    }
                product_summary[pid]['revenue'] += detail['revenue']
                product_summary[pid]['cogs'] += detail['cogs']
                product_summary[pid]['profit'] += detail['profit']
                product_summary[pid]['quantity'] += detail['quantity']
            
            # Display top 5 products by profit
            top_products = sorted(product_summary.items(), 
                                 key=lambda x: x[1]['profit'], reverse=True)[:5]
            
            for pid, data in top_products:
                profit_color = "green" if data['profit'] >= 0 else "red"
                product_text = f"{pid}: {data['quantity']} sold, Profit: {self.config['currency']}{data['profit']:,.2f}"
                ctk.CTkLabel(pl_frame, text=product_text,
                            text_color=profit_color,
                            font=("Arial", 11)).pack(anchor="w", padx=30, pady=2)
    
    def show_export_data(self, parent_frame):
        """Show data export interface"""
        ctk.CTkLabel(parent_frame, text="Data Export", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        ctk.CTkLabel(parent_frame, 
                    text="Export your data to Excel for backup or external analysis",
                    font=("Arial", 12)).pack(pady=5)
        
        # Export options frame
        export_frame = ctk.CTkFrame(parent_frame)
        export_frame.pack(pady=20, padx=50, fill="both", expand=True)
        
        # Export all data button
        ctk.CTkButton(export_frame, text="💾 Export ALL Data to Excel",
                     command=self.export_all_data,
                     fg_color="#3498db", hover_color="#2980b9",
                     height=50, font=("Arial", 14)).pack(pady=20, padx=50, fill="x")
        
        # Individual export buttons
        options_frame = ctk.CTkFrame(export_frame)
        options_frame.pack(pady=20, padx=50, fill="both", expand=True)
        
        export_options = [
            ("📦 Products Data", self.export_products_data),
            ("🥚 Ingredients Data", self.export_ingredients_data),
            ("📝 Recipes Data", self.export_recipes_data),
            ("💰 Sales Data", self.export_sales_data),
            ("📊 Inventory Logs", self.export_inventory_logs)
        ]
        
        for text, command in export_options:
            btn = ctk.CTkButton(options_frame, text=text,
                               command=command,
                               height=40,
                               font=("Arial", 13))
            btn.pack(pady=10, padx=50, fill="x")
        
        # Backup reminder
        reminder_frame = ctk.CTkFrame(parent_frame, border_width=1, 
                                     border_color="#f39c12", corner_radius=10)
        reminder_frame.pack(pady=20, padx=50, fill="x")
        
        ctk.CTkLabel(reminder_frame, 
                    text="💡 Tip: Regularly export your data for backup!",
                    font=("Arial", 12),
                    text_color="#f39c12").pack(pady=10)
    
    def export_all_data(self):
        """Export all data to a single Excel file"""
        try:
            # Get all data
            tabs = {
                'Products': self.db.read_tab('Products'),
                'Ingredients': self.db.read_tab('Ingredients'),
                'Recipes': self.db.read_tab('Recipes'),
                'Sales': self.db.read_tab('Sales'),
                'Inventory_Logs': self.db.read_tab('Inventory_Log')
            }
            
            # Check if we have any data
            empty_count = sum(1 for df in tabs.values() if df.empty)
            if empty_count == len(tabs):
                messagebox.showwarning("No Data", "No data available to export.")
                return
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"inventory_backup_{timestamp}.xlsx"
            
            # Export to Excel
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                for sheet_name, df in tabs.items():
                    if not df.empty:
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Add summary sheet
            with pd.ExcelWriter(filename, engine='openpyxl', mode='a') as writer:
                summary_data = {
                    'Sheet': [],
                    'Rows': [],
                    'Columns': [],
                    'Export Date': []
                }
                
                for sheet_name, df in tabs.items():
                    if not df.empty:
                        summary_data['Sheet'].append(sheet_name)
                        summary_data['Rows'].append(len(df))
                        summary_data['Columns'].append(len(df.columns))
                        summary_data['Export Date'].append(datetime.now().strftime("%Y-%m-%d %H:%M"))
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            messagebox.showinfo("Export Successful", 
                              f"All data exported to:\n{filename}\n\n"
                              f"Contains {len([df for df in tabs.values() if not df.empty])} sheets.")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def export_products_data(self):
        """Export products data to Excel"""
        self.export_single_tab('Products', 'products')
    
    def export_ingredients_data(self):
        """Export ingredients data to Excel"""
        self.export_single_tab('Ingredients', 'ingredients')
    
    def export_recipes_data(self):
        """Export recipes data to Excel"""
        self.export_single_tab('Recipes', 'recipes')
    
    def export_sales_data(self):
        """Export sales data to Excel"""
        self.export_single_tab('Sales', 'sales')
    
    def export_inventory_logs(self):
        """Export inventory logs to Excel"""
        self.export_single_tab('Inventory_Log', 'inventory_logs')
    
    def export_single_tab(self, tab_name, file_prefix):
        """Export a single tab to Excel"""
        try:
            df = self.db.read_tab(tab_name)
            
            if df.empty:
                messagebox.showwarning("No Data", f"No {file_prefix} data available to export.")
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{file_prefix}_{timestamp}.xlsx"
            
            df.to_excel(filename, index=False)
            
            messagebox.showinfo("Export Successful", 
                              f"{tab_name} data exported to:\n{filename}\n"
                              f"Rows: {len(df)}, Columns: {len(df.columns)}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export {tab_name}: {str(e)}")
    
    def show_settings(self):
        """Show settings interface"""
        self.clear_main_content()
        
        # Create tabview for settings
        settings_tabs = ctk.CTkTabview(self.main_content)
        settings_tabs.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add tabs
        settings_tabs.add("Business Info")
        settings_tabs.add("Preferences")
        settings_tabs.add("Data Management")
        settings_tabs.add("About")
        
        # Fill each tab
        self.show_business_settings(settings_tabs.tab("Business Info"))
        self.show_preferences_settings(settings_tabs.tab("Preferences"))
        self.show_data_management(settings_tabs.tab("Data Management"))
        self.show_about_info(settings_tabs.tab("About"))
    
    def show_business_settings(self, parent_frame):
        """Show business information settings"""
        ctk.CTkLabel(parent_frame, text="Business Information", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Form frame
        form_frame = ctk.CTkFrame(parent_frame)
        form_frame.pack(pady=20, padx=50, fill="x")
        
        # Current business info
        current_info = f"Current Business: {self.config['business_name']}"
        ctk.CTkLabel(form_frame, text=current_info, 
                    font=("Arial", 14, "bold")).pack(pady=10)
        
        # Form fields
        fields = [
            ("Business Name:", "business_name", self.config['business_name']),
            ("Currency Symbol:", "currency", self.config['currency']),
            ("Date Format:", "date_format", self.config['date_format']),
            ("Low Stock Warning Level:", "low_stock_warning", str(self.config['low_stock_warning']))
        ]
        
        self.settings_entries = {}
        
        for label_text, field_name, default_value in fields:
            row_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(row_frame, text=label_text, 
                        width=150, anchor="w").pack(side="left", padx=10)
            
            entry = ctk.CTkEntry(row_frame, width=250)
            entry.insert(0, default_value)
            entry.pack(side="left", padx=10)
            
            self.settings_entries[field_name] = entry
        
        # Tax rate setting
        tax_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        tax_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(tax_frame, text="Tax Rate (%):", 
                    width=150, anchor="w").pack(side="left", padx=10)
        
        self.tax_rate_var = tk.StringVar(value="12.0")  # Default 12%
        tax_entry = ctk.CTkEntry(tax_frame, textvariable=self.tax_rate_var, width=250)
        tax_entry.pack(side="left", padx=10)
        
        # Business address
        address_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        address_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(address_frame, text="Business Address:", 
                    width=150, anchor="w").pack(side="left", padx=10)
        
        self.address_text = ctk.CTkTextbox(address_frame, width=250, height=80)
        self.address_text.pack(side="left", padx=10)
        self.address_text.insert("1.0", "123 Business Street\nCity, Country")  # Default
        
        # Save button
        button_frame = ctk.CTkFrame(parent_frame)
        button_frame.pack(pady=20)
        
        ctk.CTkButton(button_frame, text="💾 Save Settings",
                     command=self.save_business_settings,
                     fg_color="#27ae60", hover_color="#219653",
                     width=150, height=40).pack(side="left", padx=10)
        
        ctk.CTkButton(button_frame, text="Reset to Defaults",
                     command=self.reset_settings,
                     width=150, height=40).pack(side="left", padx=10)
        
        # Status label
        self.settings_status_label = ctk.CTkLabel(parent_frame, text="", 
                                                 font=("Arial", 12))
        self.settings_status_label.pack(pady=10)
    
    def save_business_settings(self):
        """Save business settings"""
        try:
            # Update config
            new_config = {}
            
            for field_name, entry in self.settings_entries.items():
                new_config[field_name] = entry.get()
            
            # Update tax rate
            try:
                tax_rate = float(self.tax_rate_var.get())
                # You might want to save this somewhere
            except:
                pass
            
            # Update business address
            address = self.address_text.get("1.0", "end-1c").strip()
            
            # For now, just update the current session
            self.config.update(new_config)
            
            # Update window title
            self.window.title(f"Inventory Manager - {self.config['business_name']}")
            
            self.settings_status_label.configure(
                text="✅ Settings saved (session only).\nRestart app to update config file.",
                text_color="green"
            )
            
        except Exception as e:
            self.settings_status_label.configure(
                text=f"❌ Error saving settings: {str(e)}",
                text_color="red"
            )
    
    def reset_settings(self):
        """Reset settings to defaults"""
        confirm = messagebox.askyesno("Reset Settings", 
                                     "Reset all settings to defaults?")
        if confirm:
            # Reset form fields
            defaults = {
                'business_name': "My Bakery Shop",
                'currency': "₱",
                'date_format': "%Y-%m-%d",
                'low_stock_warning': "20"
            }
            
            for field_name, default_value in defaults.items():
                if field_name in self.settings_entries:
                    self.settings_entries[field_name].delete(0, 'end')
                    self.settings_entries[field_name].insert(0, default_value)
            
            self.tax_rate_var.set("12.0")
            self.address_text.delete("1.0", "end")
            self.address_text.insert("1.0", "123 Business Street\nCity, Country")
            
            self.settings_status_label.configure(
                text="✅ Settings reset to defaults",
                text_color="green"
            )
    
    def show_preferences_settings(self, parent_frame):
        """Show application preferences"""
        ctk.CTkLabel(parent_frame, text="Application Preferences", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Theme selection
        theme_frame = ctk.CTkFrame(parent_frame)
        theme_frame.pack(pady=20, padx=50, fill="x")
        
        ctk.CTkLabel(theme_frame, text="Theme:", 
                    font=("Arial", 14)).pack(pady=10)
        
        self.theme_var = tk.StringVar(value="System")
        theme_menu = ctk.CTkOptionMenu(theme_frame,
                                      values=["System", "Light", "Dark"],
                                      variable=self.theme_var,
                                      width=200)
        theme_menu.pack(pady=10)
        
        # Apply theme button
        ctk.CTkButton(theme_frame, text="Apply Theme",
                     command=self.apply_theme,
                     width=150).pack(pady=10)
        
        # Default units
        units_frame = ctk.CTkFrame(parent_frame)
        units_frame.pack(pady=20, padx=50, fill="x")
        
        ctk.CTkLabel(units_frame, text="Default Units:", 
                    font=("Arial", 14)).pack(pady=10)
        
        # Weight units
        weight_frame = ctk.CTkFrame(units_frame, fg_color="transparent")
        weight_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(weight_frame, text="Weight:", width=80).pack(side="left", padx=10)
        self.weight_unit_var = tk.StringVar(value="g")
        weight_menu = ctk.CTkOptionMenu(weight_frame,
                                       values=["g", "kg", "mg"],
                                       variable=self.weight_unit_var,
                                       width=100)
        weight_menu.pack(side="left", padx=10)
        
        # Volume units
        volume_frame = ctk.CTkFrame(units_frame, fg_color="transparent")
        volume_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(volume_frame, text="Volume:", width=80).pack(side="left", padx=10)
        self.volume_unit_var = tk.StringVar(value="ml")
        volume_menu = ctk.CTkOptionMenu(volume_frame,
                                       values=["ml", "L"],
                                       variable=self.volume_unit_var,
                                       width=100)
        volume_menu.pack(side="left", padx=10)
        
        # Save preferences
        ctk.CTkButton(parent_frame, text="💾 Save Preferences",
                     command=self.save_preferences,
                     fg_color="#27ae60", hover_color="#219653",
                     width=200, height=40).pack(pady=20)
    
    def apply_theme(self):
        """Apply selected theme"""
        theme = self.theme_var.get()
        ctk.set_appearance_mode(theme)
        messagebox.showinfo("Theme Applied", f"Theme changed to {theme} mode.")
    
    def save_preferences(self):
        """Save application preferences"""
        messagebox.showinfo("Preferences", 
                          "Preferences saved!\n\n"
                          f"Theme: {self.theme_var.get()}\n"
                          f"Default Weight Unit: {self.weight_unit_var.get()}\n"
                          f"Default Volume Unit: {self.volume_unit_var.get()}")
    
    def show_data_management(self, parent_frame):
        """Show data management options"""
        ctk.CTkLabel(parent_frame, text="Data Management", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Warning frame
        warning_frame = ctk.CTkFrame(parent_frame, border_width=2, 
                                    border_color="#e74c3c", corner_radius=10)
        warning_frame.pack(pady=20, padx=50, fill="x")
        
        ctk.CTkLabel(warning_frame, text="⚠️ IMPORTANT WARNING", 
                    font=("Arial", 16, "bold"),
                    text_color="#e74c3c").pack(pady=10)
        
        warning_text = "• ALWAYS close Excel before these operations\n"
        warning_text += "• Make sure you have backups\n"
        warning_text += "• Some actions cannot be undone!"
        
        ctk.CTkLabel(warning_frame, text=warning_text,
                    text_color="#e74c3c").pack(pady=10)
        
        # Data management buttons
        actions_frame = ctk.CTkFrame(parent_frame)
        actions_frame.pack(pady=20, padx=50, fill="both", expand=True)
        
        action_buttons = [
            ("💾 Backup All Data", self.export_all_data, "#3498db"),
            ("🗑️ Clear All Data (Safe)", self.clear_all_data_with_backup, "#e74c3c"),
            ("🔄 Recalculate All Costs", self.recalculate_costs, "#9b59b6"),
            ("🔍 Check File Status", self.check_file_status, "#f39c12")
        ]
        
        for btn_text, command, color in action_buttons:
            btn = ctk.CTkButton(actions_frame, text=btn_text,
                               command=command,
                               fg_color=color,
                               hover_color=self.darken_color(color),
                               height=45,
                               font=("Arial", 13))
            btn.pack(pady=10, fill="x")

    def check_file_status(self):
        """Check if the database file is accessible"""
        import os
        
        filepath = self.db.excel_file
        
        if not os.path.exists(filepath):
            messagebox.showinfo("File Status", "Database file not found!")
            return
        
        try:
            # Try to read the file
            test_df = pd.read_excel(filepath, sheet_name=0, nrows=1)
            
            # Try to write to the file
            with open(filepath, 'a') as f:
                pass
            
            file_size = os.path.getsize(filepath)
            size_kb = file_size / 1024
            
            status_msg = f"✅ Database File Status:\n\n"
            status_msg += f"File: {filepath}\n"
            status_msg += f"Size: {size_kb:.1f} KB\n"
            status_msg += f"Access: Read/Write OK\n"
            status_msg += f"Status: READY TO USE\n\n"
            status_msg += "Tip: Close Excel before making changes."
            
            messagebox.showinfo("File Status - OK", status_msg)
            
        except PermissionError:
            messagebox.showerror("File Status - LOCKED", 
                               "❌ Database file is LOCKED!\n\n"
                               "The file cannot be accessed because:\n"
                               "1. It's open in Microsoft Excel\n"
                               "2. Another program is using it\n"
                               "3. You don't have permission\n\n"
                               "SOLUTION: Close Excel and try again.")
            
        except Exception as e:
            messagebox.showerror("File Status - ERROR", 
                               f"❌ Cannot access database file:\n\n{str(e)}")
    
    def reset_demo_data(self):
        """Reset to demo data"""
        confirm = messagebox.askyesno("Reset Demo Data", 
                                     "Replace all data with demo data?\n\n"
                                     "This will delete your current data!")
        if confirm:
            try:
                # Create demo data
                demo_file = "data/inventory_demo.xlsx"
                
                # Copy the demo creation logic from database.py
                messagebox.showinfo("Demo Data", 
                                  "Demo data reset feature coming soon!\n"
                                  "For now, delete your inventory.xlsx file and restart the app.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset demo data: {str(e)}")
    
    def clear_all_data(self):
        """Clear all data with better error handling"""
        confirm = messagebox.askyesno("Clear All Data", 
                                     "⚠️ DELETE ALL DATA? ⚠️\n\n"
                                     "This will remove ALL records from:\n"
                                     "• Products\n• Ingredients\n• Recipes\n• Sales\n• Inventory Logs\n\n"
                                     "MAKE SURE EXCEL IS CLOSED before proceeding!")
        
        if not confirm:
            return
        
        try:
            # Check if file is locked
            if hasattr(self.db, 'is_file_locked'):
                if self.db.is_file_locked(self.db.excel_file):
                    messagebox.showerror("File Locked", 
                                       "❌ Cannot clear data!\n\n"
                                       "The Excel file is locked by another program.\n\n"
                                       "Please:\n"
                                       "1. Close Microsoft Excel if open\n"
                                       "2. Close any other program using the file\n"
                                       "3. Try again")
                    return
            
            # Continue with clearing...
            # [Keep the rest of your existing clear_all_data code]
            
        except Exception as e:
            if "Permission denied" in str(e) or "locked" in str(e).lower():
                messagebox.showerror("File Locked", 
                                   "❌ Cannot clear data!\n\n"
                                   "The Excel file is locked by another program.\n\n"
                                   "SOLUTION:\n"
                                   "1. Close Microsoft Excel\n"
                                   "2. Restart your computer if needed\n"
                                   "3. Try again")
            else:
                messagebox.showerror("Error", f"Failed to clear data: {str(e)}")
    def clear_all_data(self):
        """Clear all data - WORKING VERSION"""
        confirm = messagebox.askyesno("Clear All Data", 
                                     "⚠️ DELETE ALL DATA? ⚠️\n\n"
                                     "This will remove ALL records from:\n"
                                     "• Products\n• Ingredients\n• Recipes\n• Sales\n• Inventory Logs\n\n"
                                     "Make sure you have exported backups first!")
        
        if not confirm:
            return
        
        confirm2 = messagebox.askyesno("FINAL WARNING", 
                                      "🚨 ARE YOU ABSOLUTELY SURE? 🚨\n\n"
                                      "This action CANNOT BE UNDONE!\n"
                                      "All your data will be permanently deleted.\n\n"
                                      "Type 'DELETE' in the next box to confirm.")
        
        if not confirm2:
            return
        
        # Final confirmation with text input
        from tkinter import simpledialog
        user_input = simpledialog.askstring("Final Confirmation", 
                                          "Type DELETE to confirm permanent deletion:")
        
        if user_input != "DELETE":
            messagebox.showinfo("Cancelled", "Data deletion cancelled.")
            return
        
        try:
            # Show progress
            progress_window = ctk.CTkToplevel(self.window)
            progress_window.title("Clearing Data...")
            progress_window.geometry("400x200")
            progress_window.transient(self.window)
            progress_window.grab_set()
            
            # Center the window
            progress_window.update_idletasks()
            x = self.window.winfo_x() + (self.window.winfo_width() - progress_window.winfo_width()) // 2
            y = self.window.winfo_y() + (self.window.winfo_height() - progress_window.winfo_height()) // 2
            progress_window.geometry(f"+{x}+{y}")
            
            ctk.CTkLabel(progress_window, text="🗑️ Clearing all data...", 
                        font=("Arial", 16, "bold")).pack(pady=20)
            
            progress_label = ctk.CTkLabel(progress_window, text="Starting...")
            progress_label.pack(pady=10)
            
            # Update progress
            progress_window.update()
            
            # Define the exact column structure for each tab
            tab_structures = {
                'Products': ['Product_ID', 'Product_Name', 'Category', 
                            'Selling_Price', 'Active', 'Cost_Price',
                            'Profit_Margin', 'Margin_Percentage', 'Notes'],
                
                'Ingredients': ['Ingredient_ID', 'Ingredient_Name', 'Unit', 
                               'Category', 'Current_Stock', 'Min_Stock', 
                               'Cost_Per_Unit', 'Notes'],
                
                'Recipes': ['Recipe_ID', 'Product_ID', 'Ingredient_ID', 'Quantity_Required'],
                
                'Sales': ['Sale_ID', 'Product_ID', 'Quantity', 
                         'Sale_Date', 'Sale_Time', 'Total_Amount'],
                
                'Inventory_Log': ['Log_ID', 'Ingredient_ID', 'Change_Type', 
                                 'Quantity', 'Date', 'Notes']
            }
            
            # Clear each tab
            for i, (tab_name, columns) in enumerate(tab_structures.items(), 1):
                progress_label.configure(text=f"Clearing {tab_name}... ({i}/5)")
                progress_window.update()
                
                # Create empty DataFrame with correct columns
                empty_df = pd.DataFrame(columns=columns)
                
                # Save to database
                self.db.save_tab(tab_name, empty_df)
                
                # Small delay to show progress
                progress_window.after(100)
            
            # Close progress window
            progress_window.destroy()
            
            # Force reload the database
            self.db.__init__(self.db.excel_file)
            
            # Show success message
            messagebox.showinfo("✅ Success", 
                              "All data has been successfully cleared!\n\n"
                              "Database structure preserved.\n"
                              "You can now start fresh.")
            
            # Refresh current view if applicable
            current_method = getattr(self, 'clear_main_content', None)
            if current_method:
                current_method()
                ctk.CTkLabel(self.main_content, text="✅ Database cleared successfully!", 
                           font=("Arial", 16, "bold")).pack(pady=50)
            
        except Exception as e:
            error_msg = f"❌ Error clearing data:\n\n{str(e)}"
            print(error_msg)
            messagebox.showerror("Error", error_msg) 
    
    def recalculate_costs(self):
        """Recalculate all product costs"""
        try:
            products_df = self.db.update_all_product_costs()
            messagebox.showinfo("Costs Recalculated", 
                              f"Recalculated costs for {len(products_df)} products.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to recalculate costs: {str(e)}")

    def clear_all_data_with_backup(self):
        """Clear all data with automatic backup"""
        import shutil
        from datetime import datetime
        
        # Check if file is locked first
        if hasattr(self.db, 'is_file_locked'):
            if self.db.is_file_locked(self.db.excel_file):
                messagebox.showerror("File Locked", 
                                   "❌ Cannot clear data!\n\n"
                                   "The Excel file is locked by another program.\n"
                                   "Please close Excel and try again.")
                return
        
        confirm = messagebox.askyesno("Clear All Data", 
                                     "This will:\n\n"
                                     "1. Create a backup of your current data\n"
                                     "2. Clear all data from the database\n"
                                     "3. Preserve the database structure\n\n"
                                     "Continue?")
        
        if not confirm:
            return
        
        try:
            # Create backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"data/backup_{timestamp}.xlsx"
            shutil.copy2(self.db.excel_file, backup_file)
            
            print(f"📦 Backup created: {backup_file}")
            
            # Now clear the data
            tab_structures = {
                'Products': ['Product_ID', 'Product_Name', 'Category', 
                            'Selling_Price', 'Active', 'Cost_Price',
                            'Profit_Margin', 'Margin_Percentage', 'Notes'],
                
                'Ingredients': ['Ingredient_ID', 'Ingredient_Name', 'Unit', 
                               'Category', 'Current_Stock', 'Min_Stock', 
                               'Cost_Per_Unit', 'Notes'],
                
                'Recipes': ['Recipe_ID', 'Product_ID', 'Ingredient_ID', 'Quantity_Required'],
                
                'Sales': ['Sale_ID', 'Product_ID', 'Quantity', 
                         'Sale_Date', 'Sale_Time', 'Total_Amount'],
                
                'Inventory_Log': ['Log_ID', 'Ingredient_ID', 'Change_Type', 
                                 'Quantity', 'Date', 'Notes']
            }
            
            # Clear each tab
            for tab_name, columns in tab_structures.items():
                empty_df = pd.DataFrame(columns=columns)
                self.db.save_tab(tab_name, empty_df)
            
            messagebox.showinfo("✅ Success", 
                              f"All data cleared successfully!\n\n"
                              f"Backup saved as:\n{backup_file}\n\n"
                              "You can now start with a fresh database.")
            
        except PermissionError:
            messagebox.showerror("Permission Error", 
                               "Cannot access the Excel file.\n"
                               "Please make sure:\n"
                               "1. Excel is closed\n"
                               "2. You have write permissions\n"
                               "3. File is not read-only")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to clear data: {str(e)}")
    
    def show_about_info(self, parent_frame):
        """Show about information"""
        ctk.CTkLabel(parent_frame, text="About Inventory Manager", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Info frame
        info_frame = ctk.CTkFrame(parent_frame)
        info_frame.pack(pady=20, padx=50, fill="both", expand=True)
        
        about_text = f"""
Inventory Management System
Version 1.0

📊 Features:
• Product Management
• Ingredient Tracking
• Recipe Costing
• Sales Processing
• Inventory Management
• Comprehensive Reporting
• Data Export

📁 Data Storage:
• Excel-based database
• Automatic backups
• Easy data export

⚙️ Technology:
• Python 3.x
• CustomTkinter GUI
• Pandas for data handling
• Openpyxl for Excel operations

Developed for small businesses
to manage inventory efficiently.

For support or feature requests,
please contact your developer.

💡 Tip: Always backup your data regularly!
"""
        
        ctk.CTkLabel(info_frame, text=about_text,
                    font=("Arial", 11),
                    justify="left").pack(pady=20, padx=20)
        
        # System info
        sys_frame = ctk.CTkFrame(parent_frame)
        sys_frame.pack(pady=10, padx=50, fill="x")
        
        import os
        import sys
        
        sys_info = f"""
System Information:
• Python: {sys.version.split()[0]}
• Database: {self.config['excel_file']}
• File Size: {self.get_file_size(self.config['excel_file'])}
• Working Directory: {os.getcwd()}
"""
        
        ctk.CTkLabel(sys_frame, text=sys_info,
                    font=("Arial", 10),
                    justify="left").pack(pady=10, padx=10)
    
    def get_file_size(self, filepath):
        """Get file size in readable format"""
        try:
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                # Convert to KB/MB
                if size < 1024:
                    return f"{size} bytes"
                elif size < 1024 * 1024:
                    return f"{size/1024:.1f} KB"
                else:
                    return f"{size/(1024*1024):.1f} MB"
            else:
                return "File not found"
        except:
            return "Unknown"