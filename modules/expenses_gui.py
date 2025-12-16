# expenses_gui.py - All expense-related GUI code
import customtkinter as ctk
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

class ExpensesGUI:
    def __init__(self, window, db, config):
        self.window = window
        self.db = db
        self.config = config
        self.main_content = None
    
    def clear_main_content(self):
        if self.main_content:
            for widget in self.main_content.winfo_children():
                widget.destroy()
    
    def show_expenses_management(self, main_content_frame):
        self.main_content = main_content_frame
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
        def on_tab_change(event=None):  # FIX: Add =None or remove event
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