# sales_gui.py - All sales-related GUI code
import customtkinter as ctk
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

class SalesGUI:
    def __init__(self, window, db, config):
        self.window = window
        self.db = db
        self.config = config
        self.main_content = None
        self.sale_cart = []
        self.cart_total = 0
        
        # Constants
        self.VAT_RATE = 0.12  # 12% VAT
    
    def clear_main_content(self):
        """Clear the main content area"""
        if self.main_content:
            for widget in self.main_content.winfo_children():
                widget.destroy()
    
    def show_sales(self, main_content_frame):
        """Main sales interface with tabs"""
        self.main_content = main_content_frame
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
    
    # ============================================
    # POINT OF SALE SECTION
    # ============================================
    
    def create_sale_entry_form(self, parent_frame):
        """Point-of-Sale style sale entry form"""
        ctk.CTkLabel(parent_frame, text="Point of Sale", 
                    font=("Arial", 22, "bold")).pack(pady=10)
        
        # Reset cart
        self.sale_cart = []
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
        
        # Filtering section
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
        
        # Get categories from products
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
        
        # Filter buttons
        button_row = ctk.CTkFrame(filter_frame, fg_color="transparent")
        button_row.pack(fill="x", pady=5)
        
        ctk.CTkButton(button_row, text="🔍 Apply Filters", 
                     command=lambda: self.filter_sale_products(),
                     fg_color="#3498db", hover_color="#2980b9",
                     width=120).pack(side="left", padx=5)
        
        ctk.CTkButton(button_row, text="🗑️ Clear Filters", 
                     command=self.clear_sale_filters,
                     fg_color="#95a5a6", hover_color="#7f8c8d",
                     width=120).pack(side="left", padx=5)
        
        # Product grid frame
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
        self.sale_search_var.trace('w', lambda *args: self.filter_sale_products())
        self.sale_category_var.trace('w', lambda *args: self.filter_sale_products())
        
        # Initial load of products
        self.filter_sale_products()
    
    def filter_sale_products(self):
        """Display products for sale selection"""
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
        
        # Search filter
        search_text = self.sale_search_var.get().lower()
        if search_text:
            mask = (filtered_products['Product_Name'].str.lower().str.contains(search_text) |
                   filtered_products['Product_ID'].str.lower().str.contains(search_text))
            filtered_products = filtered_products[mask]
        
        # Category filter
        selected_category = self.sale_category_var.get()
        if selected_category != "All Categories":
            if 'Category' in filtered_products.columns:
                filtered_products = filtered_products.copy()
                filtered_products['Category'] = filtered_products['Category'].fillna('')
                filtered_products['Category'] = filtered_products['Category'].astype(str).str.strip()
                mask = filtered_products['Category'].str.lower() == selected_category.lower().strip()
                filtered_products = filtered_products[mask]
        
        if filtered_products.empty:
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
            
            # Price
            price = product.get('Selling_Price', 0)
            price_label = ctk.CTkLabel(product_frame, 
                                      text=f"{self.config['currency']}{price:,.2f}",
                                      font=("Arial", 14, "bold"),
                                      text_color="green")
            price_label.pack(pady=2)
            price_label.bind("<Button-1>", lambda e, p=product: self.add_to_cart(p))
            
            # ID
            ctk.CTkLabel(product_frame, 
                        text=f"ID: {product['Product_ID']}",
                        font=("Arial", 9),
                        text_color="black").pack(pady=2)
            
            # Hover effect
            product_frame.configure(cursor="hand2")
            product_frame.bind("<Enter>", lambda e, f=product_frame: f.configure(border_color="#3498db", border_width=2))
            product_frame.bind("<Leave>", lambda e, f=product_frame: f.configure(border_color="gray", border_width=1))
            
            # Double click to add multiple
            product_frame.bind("<Double-Button-1>", lambda e, p=product: [self.add_to_cart(p), self.add_to_cart(p)])
            
            col += 1
            if col > 1:  # 2 columns per row
                col = 0
                row += 1
        
        # Configure grid columns
        self.products_grid_frame.grid_columnconfigure(0, weight=1)
        self.products_grid_frame.grid_columnconfigure(1, weight=1)
    
    def clear_sale_filters(self):
        """Clear all sale filters"""
        self.sale_search_var.set("")
        self.sale_category_var.set("All Categories")
        self.filter_sale_products()
    
    def add_to_cart(self, product):
        """Add product to cart"""
        # Check if product already in cart
        for item in self.sale_cart:
            if item['product_id'] == product['Product_ID']:
                item['quantity'] += 1
                self.show_cart_feedback(f"+1 {product['Product_Name'][:15]}...")
                self.update_cart_display()
                return
        
        # Calculate VAT-exclusive price
        selling_price_vat_inclusive = product.get('Selling_Price', 0)
        selling_price_vat_exclusive = selling_price_vat_inclusive / (1 + self.VAT_RATE)
        
        # Add new item to cart
        cart_item = {
            'product_id': product['Product_ID'],
            'name': product['Product_Name'],
            'price': selling_price_vat_inclusive,
            'price_vat_exclusive': selling_price_vat_exclusive,
            'quantity': 1,
            'unit': 'pcs'
        }
        self.sale_cart.append(cart_item)
        
        self.show_cart_feedback(f"Added {product['Product_Name'][:15]}...")
        self.update_cart_display()
    
    def show_cart_feedback(self, message):
        """Show visual feedback when adding to cart"""
        feedback = ctk.CTkLabel(self.cart_items_frame.master.master,
                               text=f"✅ {message}",
                               font=("Arial", 11),
                               text_color="green",
                               fg_color="#d5f4e6",
                               corner_radius=8)
        feedback.place(relx=0.5, rely=0.5, anchor="center")
        self.cart_items_frame.after(1000, feedback.destroy)
    
    def update_cart_display(self):
        """Update cart display and totals"""
        # Clear cart display
        for widget in self.cart_items_frame.winfo_children():
            widget.destroy()
        
        if not self.sale_cart:
            ctk.CTkLabel(self.cart_items_frame, 
                        text="🛒 Cart is empty\nClick on products to add them",
                        font=("Arial", 12),
                        text_color="black").pack(pady=50)
            
            self.subtotal_label.configure(text=f"Net Total: {self.config['currency']}0.00")
            self.tax_label.configure(text=f"VAT (12%): {self.config['currency']}0.00")
            self.total_label.configure(text=f"Total (incl. VAT): {self.config['currency']}0.00")
            self.cart_total = 0
            return
        
        # Calculate totals
        total_vat_inclusive = 0
        
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
            
            ctk.CTkLabel(details_frame, 
                        text=f"📦 {item['name'][:20]}...",
                        font=("Arial", 12, "bold"),
                        anchor="w",
                        text_color="black").pack(side="left", padx=5)
            
            # Quantity controls
            qty_frame = ctk.CTkFrame(item_frame, 
                                    fg_color="#f8f9fa",
                                    width=120)
            qty_frame.pack(side="left", padx=10)
            qty_frame.pack_propagate(False)
            
            ctk.CTkButton(qty_frame, text="−", width=30, height=30,
                         command=lambda idx=i: self.update_cart_quantity(idx, -1),
                         font=("Arial", 14, "bold"),
                         fg_color="#e74c3c", 
                         hover_color="#c0392b").pack(side="left", padx=2)
            
            qty_label = ctk.CTkLabel(qty_frame, 
                                    text=str(item['quantity']),
                                    font=("Arial", 12, "bold"), 
                                    width=40,
                                    corner_radius=6, 
                                    fg_color="white",
                                    text_color="black")
            qty_label.pack(side="left", padx=2)
            
            ctk.CTkButton(qty_frame, text="+", width=30, height=30,
                         command=lambda idx=i: self.update_cart_quantity(idx, 1),
                         font=("Arial", 14, "bold"),
                         fg_color="#27ae60", 
                         hover_color="#219653").pack(side="left", padx=2)
            
            # Price frame
            price_frame = ctk.CTkFrame(item_frame, 
                                      fg_color="#f8f9fa",
                                      width=150)
            price_frame.pack(side="right", padx=10)
            price_frame.pack_propagate(False)
            
            item_total_vat_inclusive = item['price'] * item['quantity']
            total_vat_inclusive += item_total_vat_inclusive
            
            ctk.CTkLabel(price_frame, 
                        text=f"{self.config['currency']}{item['price']:.2f} ea",
                        font=("Arial", 9),
                        text_color="black").pack(anchor="e")
            
            ctk.CTkLabel(price_frame, 
                        text=f"{self.config['currency']}{item_total_vat_inclusive:,.2f}",
                        font=("Arial", 12, "bold"),
                        text_color="blue").pack(anchor="e")
            
            # Remove button
            ctk.CTkButton(item_frame, text="✕", width=35, height=35,
                         command=lambda idx=i: self.remove_from_cart(idx),
                         fg_color="#f8f9fa",
                         hover_color="#ffebee",
                         text_color="#e74c3c").pack(side="right", padx=5)
        
        # VAT calculation
        if total_vat_inclusive > 0:
            net_total = total_vat_inclusive / (1 + self.VAT_RATE)
            vat_amount = total_vat_inclusive - net_total
        else:
            net_total = 0
            vat_amount = 0
        
        self.cart_total = total_vat_inclusive
        
        # Update summary labels
        self.subtotal_label.configure(
            text=f"Net Total: {self.config['currency']}{net_total:,.2f}",
            text_color="black"
        )
        self.tax_label.configure(
            text=f"VAT (12%): {self.config['currency']}{vat_amount:,.2f}",
            text_color="black"
        )
        self.total_label.configure(
            text=f"Total (incl. VAT): {self.config['currency']}{total_vat_inclusive:,.2f}",
            text_color="green",
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
        
        success_count = 0
        failed_items = []
        total_vat_inclusive = sum(item['price'] * item['quantity'] for item in self.sale_cart)
        
        for item in self.sale_cart:
            try:
                # Record sale with VAT-EXCLUSIVE price
                sale_record = self.db.add_sale(
                    product_id=item['product_id'],
                    quantity=item['quantity'],
                    unit_price=item['price_vat_exclusive']
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
    
    # ============================================
    # SALES HISTORY SECTION
    # ============================================
    
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
        
        # From date
        ctk.CTkLabel(date_frame, text="From:", width=50).pack(side="left", padx=5)
        self.from_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        from_date_entry = ctk.CTkEntry(date_frame, textvariable=self.from_date_var, width=120)
        from_date_entry.pack(side="left", padx=5)
        
        # To date
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
    
    # ============================================
    # SALES REPORTS SECTION
    # ============================================
    
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