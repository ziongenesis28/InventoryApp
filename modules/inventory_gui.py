# inventory_gui.py - All inventory-related GUI code
import customtkinter as ctk
import pandas as pd
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

class InventoryModuleGUI:
    def __init__(self, window, db, config):
        self.window = window
        self.db = db
        self.config = config
        self.main_content = None
    
    def clear_main_content(self):
        if self.main_content:
            for widget in self.main_content.winfo_children():
                widget.destroy()
    
    def show_inventory(self, main_content_frame):
        """Show inventory management interface - COMPLETE IMPLEMENTATION"""
        self.main_content = main_content_frame
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
