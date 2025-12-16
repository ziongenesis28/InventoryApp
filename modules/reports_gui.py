# reports_gui.py - All report-related GUI code
import customtkinter as ctk
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

class ReportsGUI:
    def __init__(self, window, db, config):
        self.window = window
        self.db = db
        self.config = config
        self.main_content = None
    
    def clear_main_content(self):
        if self.main_content:
            for widget in self.main_content.winfo_children():
                widget.destroy()
    
    def show_reports(self, main_content_frame):
        self.main_content = main_content_frame
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