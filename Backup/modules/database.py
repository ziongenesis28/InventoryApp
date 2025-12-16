# modules/database.py - COMPLETE VERSION WITH ALL METHODS
import pandas as pd
import os
from datetime import datetime, timedelta

class InventoryDB:
    def __init__(self, excel_file):
        self.excel_file = excel_file
        self.ensure_tabs_exist()
    
    def ensure_tabs_exist(self):
        """Make sure all necessary tabs exist in Excel"""
        try:
            # Check if file exists
            if not os.path.exists(self.excel_file):
                # Create new Excel file with all tabs
                with pd.ExcelWriter(self.excel_file, engine='openpyxl') as writer:
                    # Create default tabs
                    default_tabs = {
                        'Products': pd.DataFrame(columns=[
                            'Product_ID', 'Product_Name', 'Category', 
                            'Selling_Price', 'Active', 'Cost_Price',
                            'Profit_Margin', 'Margin_Percentage'
                        ]),
                        'Ingredients': pd.DataFrame(columns=[
                            'Ingredient_ID', 'Ingredient_Name', 'Unit', 
                            'Category', 'Current_Stock', 'Min_Stock', 'Cost_Per_Unit'
                        ]),
                        'Recipes': pd.DataFrame(columns=[
                            'Recipe_ID', 'Product_ID', 'Ingredient_ID', 'Quantity_Required'
                        ]),
                        'Sales': pd.DataFrame(columns=[
                            'Sale_ID', 'Product_ID', 'Quantity', 
                            'Sale_Date', 'Sale_Time', 'Total_Amount'
                        ]),
                        'Inventory_Log': pd.DataFrame(columns=[
                            'Log_ID', 'Ingredient_ID', 'Change_Type', 
                            'Quantity', 'Date', 'Notes'
                        ])
                    }
                    
                    for tab_name, df in default_tabs.items():
                        df.to_excel(writer, sheet_name=tab_name, index=False)
                print(f"✅ Created new Excel file: {self.excel_file}")
            else:
                # File exists, ensure all tabs are there
                with pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                    # Try to read existing tabs
                    try:
                        existing_tabs = pd.ExcelFile(self.excel_file).sheet_names
                    except:
                        existing_tabs = []
                    
                    # Add missing tabs
                    default_tabs = {
                        'Products': pd.DataFrame(columns=['Product_ID', 'Product_Name', 'Category', 'Selling_Price', 'Active']),
                        'Ingredients': pd.DataFrame(columns=['Ingredient_ID', 'Ingredient_Name', 'Unit', 'Category', 'Current_Stock', 'Min_Stock', 'Cost_Per_Unit']),
                        'Recipes': pd.DataFrame(columns=['Recipe_ID', 'Product_ID', 'Ingredient_ID', 'Quantity_Required']),
                        'Sales': pd.DataFrame(columns=['Sale_ID', 'Product_ID', 'Quantity', 'Sale_Date', 'Sale_Time', 'Total_Amount']),
                        'Inventory_Log': pd.DataFrame(columns=['Log_ID', 'Ingredient_ID', 'Change_Type', 'Quantity', 'Date', 'Notes']),
                        'Expenses': pd.DataFrame(columns=[
                        'Expense_ID', 'Expense_Date', 'Expense_Type', 
                        'Description', 'Amount', 'Category', 'Payment_Method', 'Notes']),
                        
                    }
                    
                    for tab_name, df in default_tabs.items():
                        if tab_name not in existing_tabs:
                            df.to_excel(writer, sheet_name=tab_name, index=False)
                            print(f"➕ Added missing tab: {tab_name}")
        except Exception as e:
            print(f"⚠️ Warning creating Excel tabs: {e}")

    def add_expense(self, expense_data):
        """Add a new expense record"""
        try:
            expenses_df = self.read_tab('Expenses')
            
            # Generate expense ID
            if expenses_df.empty:
                expense_id = "EXP0001"
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
                
                expense_id = f"EXP{next_num:04d}"
            
            expense_data['Expense_ID'] = expense_id
            
            # Add to dataframe
            new_expense_df = pd.DataFrame([expense_data])
            expenses_df = pd.concat([expenses_df, new_expense_df], ignore_index=True)
            
            # Save
            self.save_tab('Expenses', expenses_df)
            print(f"✅ Added expense: {expense_data['Description']} - {expense_data['Amount']}")
            return True, f"Expense added successfully (ID: {expense_id})"
            
        except Exception as e:
            print(f"❌ Error adding expense: {e}")
            return False, f"Error adding expense: {str(e)}"
    
    def get_expenses(self, start_date=None, end_date=None):
        """Get expenses with optional date filtering"""
        try:
            expenses_df = self.read_tab('Expenses')
            
            if expenses_df.empty:
                return pd.DataFrame()
            
            # Convert date column
            if 'Expense_Date' in expenses_df.columns:
                expenses_df['Expense_Date'] = pd.to_datetime(expenses_df['Expense_Date'])
                
                # Apply date filter if provided
                if start_date:
                    start_date = pd.to_datetime(start_date)
                    expenses_df = expenses_df[expenses_df['Expense_Date'] >= start_date]
                
                if end_date:
                    end_date = pd.to_datetime(end_date)
                    expenses_df = expenses_df[expenses_df['Expense_Date'] <= end_date]
            
            return expenses_df.sort_values('Expense_Date', ascending=False)
            
        except Exception as e:
            print(f"❌ Error getting expenses: {e}")
            return pd.DataFrame()
    
    def get_expense_summary(self, month=None, year=None):
        """Get expense summary by category"""
        try:
            expenses_df = self.read_tab('Expenses')
            
            if expenses_df.empty:
                return pd.DataFrame()
            
            # Convert date
            if 'Expense_Date' in expenses_df.columns:
                expenses_df['Expense_Date'] = pd.to_datetime(expenses_df['Expense_Date'])
                expenses_df['Year'] = expenses_df['Expense_Date'].dt.year
                expenses_df['Month'] = expenses_df['Expense_Date'].dt.month
                
                # Filter by month/year if provided
                if year:
                    expenses_df = expenses_df[expenses_df['Year'] == year]
                if month:
                    expenses_df = expenses_df[expenses_df['Month'] == month]
            
            # Group by category
            if 'Category' in expenses_df.columns:
                summary = expenses_df.groupby('Category').agg({
                    'Amount': ['sum', 'count']
                }).reset_index()
                
                # Flatten column names
                summary.columns = ['Category', 'Total_Amount', 'Transaction_Count']
                return summary.sort_values('Total_Amount', ascending=False)
            
            return pd.DataFrame()
            
        except Exception as e:
            print(f"❌ Error getting expense summary: {e}")
            return pd.DataFrame()
    
    def delete_expense(self, expense_id):
        """Delete an expense record"""
        try:
            expenses_df = self.read_tab('Expenses')
            
            if expenses_df.empty:
                return False, "No expenses found"
            
            # Find and remove expense
            initial_count = len(expenses_df)
            expenses_df = expenses_df[expenses_df['Expense_ID'] != expense_id]
            
            if len(expenses_df) == initial_count:
                return False, f"Expense {expense_id} not found"
            
            # Save updated expenses
            self.save_tab('Expenses', expenses_df)
            print(f"✅ Deleted expense: {expense_id}")
            return True, f"Expense {expense_id} deleted successfully"
            
        except Exception as e:
            print(f"❌ Error deleting expense: {e}")
            return False, f"Error deleting expense: {str(e)}"
    
    def read_tab(self, tab_name):
        """Read data from an Excel tab"""
        try:
            df = pd.read_excel(self.excel_file, sheet_name=tab_name)
            return df
        except Exception as e:
            print(f"⚠️ Could not read tab '{tab_name}': {e}")
            return pd.DataFrame()
    
    def save_tab(self, tab_name, data_df):
        """Save data to an Excel tab with lock handling"""
        import time
        
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                if self.is_file_locked(self.excel_file):
                    if attempt == max_retries - 1:
                        raise PermissionError(f"File is locked by another process: {self.excel_file}")
                    print(f"⚠️ File locked, retrying in {retry_delay} second(s)... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    continue
                
                # Read all existing tabs
                all_tabs = {}
                try:
                    excel_file = pd.ExcelFile(self.excel_file)
                    for sheet in excel_file.sheet_names:
                        if sheet != tab_name:  # Keep other sheets
                            all_tabs[sheet] = pd.read_excel(self.excel_file, sheet_name=sheet)
                except:
                    pass
                
                # Add/update our tab
                all_tabs[tab_name] = data_df
                
                # Write all tabs back
                with pd.ExcelWriter(self.excel_file, engine='openpyxl') as writer:
                    for sheet_name, sheet_data in all_tabs.items():
                        sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)
                
                return True
                
            except PermissionError as e:
                if attempt == max_retries - 1:
                    print(f"❌ Error saving tab '{tab_name}': {e}")
                    print("Please close Excel or any other program using this file.")
                    return False
                time.sleep(retry_delay)
                
            except Exception as e:
                print(f"❌ Error saving tab '{tab_name}': {e}")
                return False
        
        return False    
    def add_sale(self, product_id, quantity, unit_price):
        """Record a new sale"""
        try:
            sales_df = self.read_tab('Sales')
            
            new_sale = {
                'Sale_ID': f"SALE{len(sales_df) + 1:04d}",
                'Product_ID': product_id,
                'Quantity': quantity,
                'Sale_Date': datetime.now().strftime("%Y-%m-%d"),
                'Sale_Time': datetime.now().strftime("%H:%M:%S"),
                'Total_Amount': quantity * unit_price
            }
            
            sales_df = pd.concat([sales_df, pd.DataFrame([new_sale])], ignore_index=True)
            self.save_tab('Sales', sales_df)
            print(f"💰 Recorded sale: {quantity} x {product_id}")
            return new_sale
        except Exception as e:
            print(f"❌ Error recording sale: {e}")
            return None
    
    def get_all_products(self):
        """Get all active products"""
        products_df = self.read_tab('Products')
        if products_df.empty:
            return pd.DataFrame()
        
        # Filter active products
        if 'Active' in products_df.columns:
            active_products = products_df[products_df['Active'].astype(str).str.upper() == 'YES']
        else:
            active_products = products_df
        
        return active_products
    
    def get_all_ingredients(self):
        """Get all ingredients"""
        ingredients_df = self.read_tab('Ingredients')
        return ingredients_df
    
    def get_product_recipes(self, product_id):
        """Get all ingredients for a specific product"""
        recipes_df = self.read_tab('Recipes')
        ingredients_df = self.read_tab('Ingredients')
        
        if recipes_df.empty:
            return pd.DataFrame()
        
        # Filter recipes for this product
        product_recipes = recipes_df[recipes_df['Product_ID'] == product_id].copy()
        
        if product_recipes.empty:
            return pd.DataFrame()
        
        # Join with ingredient details
        if not ingredients_df.empty:
            merged = pd.merge(product_recipes, ingredients_df, 
                            left_on='Ingredient_ID', right_on='Ingredient_ID', 
                            how='left')
            
            return merged[['Ingredient_ID', 'Ingredient_Name', 'Unit', 'Quantity_Required', 'Cost_Per_Unit']]
        else:
            return product_recipes
    
    def save_recipe(self, product_id, recipe_items):
        """
        Save or update a recipe
        recipe_items: list of dictionaries with Ingredient_ID and Quantity_Required
        """
        try:
            recipes_df = self.read_tab('Recipes')
            
            # Remove existing recipe for this product
            if not recipes_df.empty:
                recipes_df = recipes_df[recipes_df['Product_ID'] != product_id]
            
            # Add new recipe items
            new_records = []
            for idx, item in enumerate(recipe_items):
                new_records.append({
                    'Recipe_ID': f"{product_id}-REC{idx+1:03d}",
                    'Product_ID': product_id,
                    'Ingredient_ID': item['ingredient_id'],
                    'Quantity_Required': item['quantity']
                })
            
            # Add to dataframe
            new_df = pd.DataFrame(new_records)
            recipes_df = pd.concat([recipes_df, new_df], ignore_index=True)
            
            # Save back to Excel
            success = self.save_tab('Recipes', recipes_df)
            
            if success:
                print(f"✅ Saved recipe for {product_id} with {len(recipe_items)} ingredients")
            else:
                print(f"❌ Failed to save recipe for {product_id}")
            
            return success
        except Exception as e:
            print(f"❌ Error saving recipe: {e}")
            return False
    
    def calculate_product_cost(self, product_id):
        """Calculate total cost of a product based on its recipe"""
        recipe_items = self.get_product_recipes(product_id)
        
        if recipe_items.empty:
            return 0
        
        total_cost = 0
        for _, item in recipe_items.iterrows():
            if 'Cost_Per_Unit' in item and 'Quantity_Required' in item:
                cost = item['Cost_Per_Unit'] * item['Quantity_Required']
                total_cost += cost
        
        return total_cost
    
    def update_all_product_costs(self):
        """Update costs for all products based on current ingredient prices"""
        try:
            products_df = self.read_tab('Products')
            
            if products_df.empty:
                return products_df
            
            # Calculate cost for each product
            costs = []
            for _, product in products_df.iterrows():
                product_id = product['Product_ID']
                cost = self.calculate_product_cost(product_id)
                costs.append(cost)
            
            # Add/update cost columns
            products_df['Cost_Price'] = costs
            
            # Calculate profit margin if Selling_Price exists
            if 'Selling_Price' in products_df.columns:
                products_df['Profit_Margin'] = products_df['Selling_Price'] - products_df['Cost_Price']
                products_df['Margin_Percentage'] = (products_df['Profit_Margin'] / products_df['Selling_Price'] * 100).round(2)
            
            # Save updated products
            self.save_tab('Products', products_df)
            print(f"✅ Updated costs for {len(products_df)} products")
            return products_df
        except Exception as e:
            print(f"❌ Error updating product costs: {e}")
            return pd.DataFrame()
    
    def update_inventory_from_sale(self, product_id, quantity_sold):
        """
        Deduct ingredients from inventory when a product is sold
        Returns: success (True/False), message
        """
        try:
            # 1. Get the recipe for this product
            recipe_items = self.get_product_recipes(product_id)
            
            if recipe_items.empty:
                return False, f"No recipe found for product {product_id}"
            
            # 2. Get current inventory
            inventory_df = self.read_tab('Ingredients')
            if inventory_df.empty:
                return False, "No ingredients in inventory"
            
            # 3. Check if we have enough stock and calculate deductions
            deductions = []
            insufficient_stock = []
            
            for _, recipe_item in recipe_items.iterrows():
                ingredient_id = recipe_item['Ingredient_ID']
                quantity_needed = recipe_item['Quantity_Required']
                total_needed = quantity_needed * quantity_sold
                
                # Find the ingredient in inventory
                ingredient_idx = inventory_df[inventory_df['Ingredient_ID'] == ingredient_id].index
                
                if len(ingredient_idx) == 0:
                    insufficient_stock.append(f"{recipe_item.get('Ingredient_Name', ingredient_id)}: not in inventory")
                    continue
                
                idx = ingredient_idx[0]
                current_stock = inventory_df.at[idx, 'Current_Stock']
                
                if current_stock < total_needed:
                    insufficient_stock.append(
                        f"{recipe_item.get('Ingredient_Name', ingredient_id)}: "
                        f"need {total_needed}, have {current_stock}"
                    )
                else:
                    # Record the deduction
                    deductions.append({
                        'ingredient_id': ingredient_id,
                        'ingredient_name': recipe_item.get('Ingredient_Name', ingredient_id),
                        'deduction': total_needed,
                        'old_stock': current_stock,
                        'new_stock': current_stock - total_needed,
                        'index': idx
                    })
            
            # 4. If any ingredient is insufficient, don't proceed
            if insufficient_stock:
                return False, f"Insufficient stock:\n" + "\n".join(insufficient_stock)
            
            # 5. Apply all deductions
            for deduction in deductions:
                idx = deduction['index']
                inventory_df.at[idx, 'Current_Stock'] = deduction['new_stock']
            
            # 6. Save updated inventory
            self.save_tab('Ingredients', inventory_df)
            
            # 7. Log the inventory change
            self.log_inventory_change(
                product_id=product_id,
                quantity_sold=quantity_sold,
                deductions=deductions
            )
            
            # Get ingredient names for message
            ingredient_names = [d['ingredient_name'] for d in deductions]
            return True, f"Deducted from: {', '.join(ingredient_names)}"
            
        except Exception as e:
            return False, f"Error updating inventory: {str(e)}"
    
    def log_inventory_change(self, product_id, quantity_sold, deductions):
        """Log inventory changes to Inventory_Log tab"""
        try:
            logs_df = self.read_tab('Inventory_Log')
            
            for deduction in deductions:
                new_log = {
                    'Log_ID': f"LOG{len(logs_df) + 1:06d}",
                    'Ingredient_ID': deduction['ingredient_id'],
                    'Change_Type': 'SALE_DEDUCTION',
                    'Quantity': -deduction['deduction'],  # Negative for deduction
                    'Date': datetime.now().strftime("%Y-%m-%d"),
                    'Notes': f"Product {product_id} x{quantity_sold}"
                }
                logs_df = pd.concat([logs_df, pd.DataFrame([new_log])], ignore_index=True)
            
            self.save_tab('Inventory_Log', logs_df)
            print(f"📝 Logged inventory change for {product_id}")
            
        except Exception as e:
            print(f"⚠️ Failed to log inventory change: {e}")
    
    def add_inventory_stock(self, ingredient_id, quantity_to_add, notes=""):
        """Add stock to an ingredient (purchase/replenishment)"""
        try:
            inventory_df = self.read_tab('Ingredients')
            
            if inventory_df.empty:
                return False, "No ingredients found"
            
            # Find the ingredient
            ingredient_idx = inventory_df[inventory_df['Ingredient_ID'] == ingredient_id].index
            
            if len(ingredient_idx) == 0:
                return False, f"Ingredient {ingredient_id} not found"
            
            idx = ingredient_idx[0]
            old_stock = inventory_df.at[idx, 'Current_Stock']
            new_stock = old_stock + quantity_to_add
            
            # Update stock
            inventory_df.at[idx, 'Current_Stock'] = new_stock
            self.save_tab('Ingredients', inventory_df)
            
            # Log the addition
            logs_df = self.read_tab('Inventory_Log')
            new_log = {
                'Log_ID': f"LOG{len(logs_df) + 1:06d}",
                'Ingredient_ID': ingredient_id,
                'Change_Type': 'STOCK_ADD',
                'Quantity': quantity_to_add,
                'Date': datetime.now().strftime("%Y-%m-%d"),
                'Notes': notes or f"Manual stock addition"
            }
            logs_df = pd.concat([logs_df, pd.DataFrame([new_log])], ignore_index=True)
            self.save_tab('Inventory_Log', logs_df)
            
            ingredient_name = inventory_df.at[idx, 'Ingredient_Name']
            print(f"📦 Added {quantity_to_add} to {ingredient_name}. New stock: {new_stock}")
            return True, f"Added {quantity_to_add} to {ingredient_name}. New stock: {new_stock}"
            
        except Exception as e:
            print(f"❌ Error adding stock: {e}")
            return False, f"Error adding stock: {str(e)}"
    
    def get_inventory_status(self):
        """Get current inventory status with alerts"""
        inventory_df = self.read_tab('Ingredients')
        
        if inventory_df.empty:
            return pd.DataFrame()
        
        # Calculate status
        inventory_df = inventory_df.copy()
        
        # Ensure columns exist
        if 'Min_Stock' not in inventory_df.columns:
            inventory_df['Min_Stock'] = 0
        
        # Calculate status
        inventory_df['Status'] = 'Normal'
        inventory_df['Days_Remaining'] = None
        
        # Check low stock
        low_stock_mask = inventory_df['Current_Stock'] <= inventory_df['Min_Stock']
        inventory_df.loc[low_stock_mask, 'Status'] = 'Low Stock'
        
        # Check critical (below 50% of min stock)
        critical_mask = inventory_df['Current_Stock'] <= (inventory_df['Min_Stock'] * 0.5)
        inventory_df.loc[critical_mask, 'Status'] = 'Critical'
        
        # Calculate stock-out risk (simple estimation)
        for idx, row in inventory_df.iterrows():
            if row['Min_Stock'] > 0 and row['Current_Stock'] > 0:
                days = (row['Current_Stock'] / row['Min_Stock']) * 7  # Rough estimate
                inventory_df.at[idx, 'Days_Remaining'] = round(days, 1)
        
        return inventory_df
    
    def get_inventory_logs(self, days_back=30):
        """Get recent inventory logs"""
        logs_df = self.read_tab('Inventory_Log')
        
        if logs_df.empty:
            return pd.DataFrame()
        
        # Convert date column if it exists
        if 'Date' in logs_df.columns:
            try:
                logs_df['Date'] = pd.to_datetime(logs_df['Date'])
                cutoff_date = datetime.now() - timedelta(days=days_back)
                recent_logs = logs_df[logs_df['Date'] >= cutoff_date].copy()
                recent_logs = recent_logs.sort_values('Date', ascending=False)
                return recent_logs
            except:
                return logs_df.tail(100)  # Return last 100 if date conversion fails
        
        return logs_df.tail(100)
    
    def add_product(self, product_data):
        """Add a new product to the database"""
        try:
            print(f"🔍 DEBUG: Adding product with data: {product_data}")
            
            # Check if product_data has required fields
            required_fields = ['Product_ID', 'Product_Name', 'Selling_Price', 'Active']
            for field in required_fields:
                if field not in product_data:
                    print(f"❌ Missing required field: {field}")
                    return False, f"Missing required field: {field}"
            
            products_df = self.read_tab('Products')
            print(f"🔍 DEBUG: Current products: {len(products_df)} rows")
            
            # Check if product ID already exists
            if 'Product_ID' in products_df.columns:
                if product_data['Product_ID'] in products_df['Product_ID'].values:
                    return False, f"Product ID {product_data['Product_ID']} already exists"
            else:
                # If Product_ID column doesn't exist, add it
                products_df['Product_ID'] = ''
            
            # Ensure all required columns exist
            required_columns = ['Product_ID', 'Product_Name', 'Category', 'Selling_Price', 'Active', 
                               'Cost_Price', 'Profit_Margin', 'Margin_Percentage']
            
            for col in required_columns:
                if col not in products_df.columns:
                    products_df[col] = None
            
            # Prepare new product row
            new_product_row = {}
            for col in products_df.columns:
                if col in product_data:
                    new_product_row[col] = product_data[col]
                elif col == 'Cost_Price':
                    new_product_row[col] = 0.0  # Default cost price
                elif col == 'Profit_Margin':
                    # Calculate profit margin
                    selling_price = product_data.get('Selling_Price', 0)
                    cost_price = product_data.get('Cost_Price', 0)
                    new_product_row[col] = selling_price - cost_price
                elif col == 'Margin_Percentage':
                    # Calculate margin percentage
                    selling_price = product_data.get('Selling_Price', 0)
                    cost_price = product_data.get('Cost_Price', 0)
                    if selling_price > 0:
                        new_product_row[col] = ((selling_price - cost_price) / selling_price * 100)
                    else:
                        new_product_row[col] = 0.0
                else:
                    new_product_row[col] = None
            
            # Add new product
            new_product_df = pd.DataFrame([new_product_row])
            products_df = pd.concat([products_df, new_product_df], ignore_index=True)
            
            # Save
            success = self.save_tab('Products', products_df)
            
            if success:
                print(f"✅ Added product: {product_data['Product_Name']} ({product_data['Product_ID']})")
                
                # Update cost for this product
                self.update_all_product_costs()
                
                return True, f"Product '{product_data['Product_Name']}' added successfully"
            else:
                return False, "Failed to save product to database"
            
        except Exception as e:
            print(f"❌ Error adding product: {e}")
            import traceback
            traceback.print_exc()  # Print full traceback for debugging
            return False, f"Error adding product: {str(e)}"
    
    def update_product(self, product_id, updated_data):
        """Update an existing product"""
        try:
            products_df = self.read_tab('Products')
            
            # Find the product
            product_idx = products_df[products_df['Product_ID'] == product_id].index
            
            if len(product_idx) == 0:
                return False, f"Product {product_id} not found"
            
            idx = product_idx[0]
            
            # Update fields
            for key, value in updated_data.items():
                if key in products_df.columns:
                    products_df.at[idx, key] = value
            
            # Save
            self.save_tab('Products', products_df)
            print(f"✅ Updated product: {product_id}")
            return True, f"Product {product_id} updated successfully"
            
        except Exception as e:
            print(f"❌ Error updating product: {e}")
            return False, f"Error updating product: {str(e)}"
    
    def delete_product(self, product_id):
        """Delete a product (soft delete by marking as inactive)"""
        try:
            products_df = self.read_tab('Products')
            
            # Find the product
            product_idx = products_df[products_df['Product_ID'] == product_id].index
            
            if len(product_idx) == 0:
                return False, f"Product {product_id} not found"
            
            idx = product_idx[0]
            
            # Soft delete - mark as inactive
            if 'Active' in products_df.columns:
                products_df.at[idx, 'Active'] = 'No'
            else:
                # Hard delete if no Active column
                products_df = products_df.drop(idx).reset_index(drop=True)
            
            # Save
            self.save_tab('Products', products_df)
            print(f"✅ Deleted (marked inactive) product: {product_id}")
            return True, f"Product {product_id} deleted (marked as inactive)"
            
        except Exception as e:
            print(f"❌ Error deleting product: {e}")
            return False, f"Error deleting product: {str(e)}"
    
    def add_ingredient(self, ingredient_data):
        """Add a new ingredient to the database"""
        try:
            ingredients_df = self.read_tab('Ingredients')
            
            # Check if ingredient ID already exists
            if ingredient_data['Ingredient_ID'] in ingredients_df['Ingredient_ID'].values:
                return False, f"Ingredient ID {ingredient_data['Ingredient_ID']} already exists"
            
            # Add new ingredient
            new_ingredient_df = pd.DataFrame([ingredient_data])
            ingredients_df = pd.concat([ingredients_df, new_ingredient_df], ignore_index=True)
            
            # Save
            self.save_tab('Ingredients', ingredients_df)
            print(f"✅ Added ingredient: {ingredient_data['Ingredient_Name']} ({ingredient_data['Ingredient_ID']})")
            return True, f"Ingredient '{ingredient_data['Ingredient_Name']}' added successfully"
            
        except Exception as e:
            print(f"❌ Error adding ingredient: {e}")
            return False, f"Error adding ingredient: {str(e)}"
    
    def update_ingredient(self, ingredient_id, updated_data):
        """Update an existing ingredient"""
        try:
            ingredients_df = self.read_tab('Ingredients')
            
            # Find the ingredient
            ingredient_idx = ingredients_df[ingredients_df['Ingredient_ID'] == ingredient_id].index
            
            if len(ingredient_idx) == 0:
                return False, f"Ingredient {ingredient_id} not found"
            
            idx = ingredient_idx[0]
            
            # Update fields
            for key, value in updated_data.items():
                if key in ingredients_df.columns:
                    ingredients_df.at[idx, key] = value
            
            # Save
            self.save_tab('Ingredients', ingredients_df)
            print(f"✅ Updated ingredient: {ingredient_id}")
            return True, f"Ingredient {ingredient_id} updated successfully"
            
        except Exception as e:
            print(f"❌ Error updating ingredient: {e}")
            return False, f"Error updating ingredient: {str(e)}"
    
    def delete_ingredient(self, ingredient_id):
        """Delete an ingredient"""
        try:
            ingredients_df = self.read_tab('Ingredients')
            
            # Find the ingredient
            ingredient_idx = ingredients_df[ingredients_df['Ingredient_ID'] == ingredient_id].index
            
            if len(ingredient_idx) == 0:
                return False, f"Ingredient {ingredient_id} not found"
            
            idx = ingredient_idx[0]
            
            # Check if ingredient is used in any recipes
            recipes_df = self.read_tab('Recipes')
            if not recipes_df.empty:
                used_in = recipes_df[recipes_df['Ingredient_ID'] == ingredient_id]
                if not used_in.empty:
                    product_ids = used_in['Product_ID'].unique()
                    return False, f"Cannot delete! Used in recipes for products: {', '.join(product_ids)}"
            
            # Delete the ingredient
            ingredients_df = ingredients_df.drop(idx).reset_index(drop=True)
            
            # Save
            self.save_tab('Ingredients', ingredients_df)
            print(f"✅ Deleted ingredient: {ingredient_id}")
            return True, f"Ingredient {ingredient_id} deleted successfully"
            
        except Exception as e:
            print(f"❌ Error deleting ingredient: {e}")
            return False, f"Error deleting ingredient: {str(e)}"
    
    def generate_product_id(self):
        """Generate a new unique product ID"""
        products_df = self.read_tab('Products')
        
        if products_df.empty:
            return "PROD001"
        
        # Find the highest PROD number
        product_ids = products_df['Product_ID'].dropna()
        prod_numbers = []
        
        for pid in product_ids:
            if isinstance(pid, str) and pid.startswith('PROD'):
                try:
                    num = int(pid[4:])  # Extract number after 'PROD'
                    prod_numbers.append(num)
                except:
                    pass
        
        if prod_numbers:
            next_num = max(prod_numbers) + 1
        else:
            next_num = 1
        
        return f"PROD{next_num:03d}"  # Format as 3-digit number
    
    def generate_ingredient_id(self):
        """Generate a new unique ingredient ID"""
        ingredients_df = self.read_tab('Ingredients')
        
        if ingredients_df.empty:
            return "ING001"
        
        # Find the highest ING number
        ingredient_ids = ingredients_df['Ingredient_ID'].dropna()
        ing_numbers = []
        
        for iid in ingredient_ids:
            if isinstance(iid, str) and iid.startswith('ING'):
                try:
                    num = int(iid[3:])
                    ing_numbers.append(num)
                except:
                    pass
        
        if ing_numbers:
            next_num = max(ing_numbers) + 1
        else:
            next_num = 1
        
        return f"ING{next_num:03d}"

    def is_file_locked(self, filepath):
        """Check if a file is locked by another process"""
        import os
        if not os.path.exists(filepath):
            return False
        
        try:
            # Try to open the file in append mode
            with open(filepath, 'a') as f:
                pass
            return False
        except IOError:
            return True
