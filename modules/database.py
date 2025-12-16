# modules/database.py - COMPLETE VERSION WITH ALL METHODS
import pandas as pd
import os
import time
from datetime import datetime, timedelta


class InventoryDB:
    def __init__(self, excel_file):
        self.excel_file = excel_file
        self.ensure_tabs_exist()

    # ===== FILE AND TAB MANAGEMENT =====
    def ensure_tabs_exist(self):
        """Make sure all necessary tabs exist in Excel"""
        try:
            if not os.path.exists(self.excel_file):
                self.create_new_database()
            else:
                self.add_missing_tabs()
        except Exception as e:
            print(f"⚠️ Warning creating Excel tabs: {e}")

    def create_new_database(self):
        """Create a new Excel file with all required tabs"""
        default_tabs = {
            'Products': pd.DataFrame(columns=[
                'Product_ID', 'Product_Name', 'Category', 'Selling_Price', 'Active',
                'Cost_Price', 'Profit_Margin', 'Margin_Percentage', 'Notes'
            ]),
            'Ingredients': pd.DataFrame(columns=[
                'Ingredient_ID', 'Ingredient_Name', 'Unit', 'Category', 
                'Current_Stock', 'Min_Stock_Level', 'Cost_Per_Unit', 'Supplier',
                'Description', 'Active', 'Last_Updated'
            ]),
            'Recipes': pd.DataFrame(columns=[
                'Recipe_ID', 'Product_ID', 'Ingredient_ID', 'Quantity_Required'
            ]),
            'Sales': pd.DataFrame(columns=[
                'Sale_ID', 'Product_ID', 'Quantity', 'Sale_Date', 
                'Sale_Time', 'Total_Amount'
            ]),
            'Inventory_Log': pd.DataFrame(columns=[
                'Log_ID', 'Ingredient_ID', 'Change_Type', 'Quantity', 
                'Date', 'Notes'
            ]),
            'Expenses': pd.DataFrame(columns=[
                'Expense_ID', 'Expense_Date', 'Expense_Type', 'Description',
                'Amount', 'Category', 'Payment_Method', 'Notes'
            ])
        }
        
        with pd.ExcelWriter(self.excel_file, engine='openpyxl') as writer:
            for tab_name, df in default_tabs.items():
                df.to_excel(writer, sheet_name=tab_name, index=False)
        print(f"✅ Created new Excel file: {self.excel_file}")

    def add_missing_tabs(self):
        """Add missing tabs to existing Excel file"""
        try:
            existing_tabs = pd.ExcelFile(self.excel_file).sheet_names
        except:
            existing_tabs = []
        
        default_tabs = {
            'Products': pd.DataFrame(columns=['Product_ID', 'Product_Name', 'Category', 
                                            'Selling_Price', 'Active', 'Cost_Price',
                                            'Profit_Margin', 'Margin_Percentage', 'Notes']),
            'Ingredients': pd.DataFrame(columns=['Ingredient_ID', 'Ingredient_Name', 'Unit', 
                                               'Category', 'Current_Stock', 'Min_Stock_Level', 
                                               'Cost_Per_Unit', 'Supplier', 'Description', 
                                               'Active', 'Last_Updated']),
            'Recipes': pd.DataFrame(columns=['Recipe_ID', 'Product_ID', 'Ingredient_ID', 
                                           'Quantity_Required']),
            'Sales': pd.DataFrame(columns=['Sale_ID', 'Product_ID', 'Quantity', 
                                         'Sale_Date', 'Sale_Time', 'Total_Amount']),
            'Inventory_Log': pd.DataFrame(columns=['Log_ID', 'Ingredient_ID', 'Change_Type', 
                                                 'Quantity', 'Date', 'Notes']),
            'Expenses': pd.DataFrame(columns=['Expense_ID', 'Expense_Date', 'Expense_Type', 
                                            'Description', 'Amount', 'Category', 
                                            'Payment_Method', 'Notes'])
        }
        
        with pd.ExcelWriter(self.excel_file, engine='openpyxl', mode='a', 
                          if_sheet_exists='overlay') as writer:
            for tab_name, df in default_tabs.items():
                if tab_name not in existing_tabs:
                    df.to_excel(writer, sheet_name=tab_name, index=False)
                    print(f"➕ Added missing tab: {tab_name}")

    def read_tab(self, tab_name):
        """Read data from an Excel tab"""
        try:
            df = pd.read_excel(self.excel_file, sheet_name=tab_name)
            
            # Define numeric columns for each sheet
            numeric_columns_map = {
                'Ingredients': ['Current_Stock', 'Cost_Per_Unit', 'Min_Stock_Level'],
                'Products': ['Selling_Price', 'Cost_Price', 'Profit_Margin', 'Margin_Percentage'],
                'Sales': ['Quantity', 'Total_Amount'],
                'Expenses': ['Amount'],
                'Recipes': ['Quantity_Required'],
                'Inventory_Log': ['Quantity']
            }
            
            # Convert numeric columns to float64
            if tab_name in numeric_columns_map:
                for col in numeric_columns_map[tab_name]:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0).astype('float64')
            
            # Convert text columns to string and fill NaN with empty string
            text_columns = ['Product_Name', 'Category', 'Notes', 'Description', 
                          'Ingredient_Name', 'Supplier', 'Unit', 'Active',
                          'Expense_Type', 'Payment_Method', 'Change_Type']
            
            for col in text_columns:
                if col in df.columns:
                    df[col] = df[col].astype(str).fillna('')
            
            return df
        except Exception as e:
            print(f"⚠️ Could not read tab '{tab_name}': {e}")
            # Return empty dataframe with correct columns
            if tab_name == 'Ingredients':
                return pd.DataFrame(columns=['Ingredient_ID', 'Ingredient_Name', 'Unit', 'Category', 
                                           'Current_Stock', 'Min_Stock_Level', 'Cost_Per_Unit', 
                                           'Supplier', 'Description', 'Active', 'Last_Updated'])
            elif tab_name == 'Products':
                return pd.DataFrame(columns=['Product_ID', 'Product_Name', 'Category', 'Selling_Price', 
                                           'Active', 'Cost_Price', 'Profit_Margin', 'Margin_Percentage', 'Notes'])
            else:
                return pd.DataFrame()

    def save_tab(self, tab_name, data_df):
        """Save data to an Excel tab with lock handling"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                if self.is_file_locked(self.excel_file):
                    if attempt == max_retries - 1:
                        raise PermissionError(f"File is locked: {self.excel_file}")
                    print(f"⚠️ File locked, retrying... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    continue
                
                # Read all existing tabs
                all_tabs = {}
                try:
                    excel_file = pd.ExcelFile(self.excel_file)
                    for sheet in excel_file.sheet_names:
                        if sheet != tab_name:
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

    def is_file_locked(self, filepath):
        """Check if a file is locked by another process"""
        if not os.path.exists(filepath):
            return False
        
        try:
            with open(filepath, 'a'):
                pass
            return False
        except IOError:
            return True

    # ===== PRODUCT MANAGEMENT =====
    def generate_product_id(self):
        """Generate a new unique product ID"""
        products_df = self.read_tab('Products')
        
        if products_df.empty or 'Product_ID' not in products_df.columns:
            return "PROD001"
        
        prod_numbers = []
        for pid in products_df['Product_ID'].dropna():
            if isinstance(pid, str) and pid.startswith('PROD'):
                try:
                    num = int(pid[4:])
                    prod_numbers.append(num)
                except:
                    pass
        
        next_num = max(prod_numbers) + 1 if prod_numbers else 1
        return f"PROD{next_num:03d}"

    def add_product(self, product_data):
        """Add a new product to the database"""
        try:
            # Validate required fields
            required_fields = ['Product_ID', 'Product_Name', 'Selling_Price', 'Active']
            for field in required_fields:
                if field not in product_data:
                    return False, f"Missing required field: {field}"
            
            products_df = self.read_tab('Products')
            
            # Check if product ID already exists
            if not products_df.empty and 'Product_ID' in products_df.columns:
                if product_data['Product_ID'] in products_df['Product_ID'].values:
                    return False, f"Product ID {product_data['Product_ID']} already exists"
            
            # Ensure all columns exist
            default_columns = ['Product_ID', 'Product_Name', 'Category', 'Selling_Price', 
                             'Active', 'Cost_Price', 'Profit_Margin', 'Margin_Percentage', 'Notes']
            for col in default_columns:
                if col not in products_df.columns:
                    products_df[col] = None
            
            # Prepare new row
            new_row = {}
            for col in products_df.columns:
                if col in product_data:
                    new_row[col] = product_data[col]
                elif col == 'Cost_Price':
                    new_row[col] = 0.0
                elif col == 'Profit_Margin':
                    selling = product_data.get('Selling_Price', 0)
                    cost = product_data.get('Cost_Price', 0)
                    new_row[col] = selling - cost
                elif col == 'Margin_Percentage':
                    selling = product_data.get('Selling_Price', 0)
                    cost = product_data.get('Cost_Price', 0)
                    new_row[col] = ((selling - cost) / selling * 100) if selling > 0 else 0.0
                else:
                    new_row[col] = None
            
            # Add product
            products_df = pd.concat([products_df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Save and update costs
            if self.save_tab('Products', products_df):
                self.update_all_product_costs()
                print(f"✅ Added product: {product_data['Product_Name']}")
                return True, f"Product '{product_data['Product_Name']}' added successfully"
            return False, "Failed to save product"
            
        except Exception as e:
            print(f"❌ Error adding product: {e}")
            return False, f"Error adding product: {str(e)}"

    def update_product(self, product_id, updated_data):
        """Update an existing product"""
        try:
            products_df = self.read_tab('Products')
            
            if products_df.empty or 'Product_ID' not in products_df.columns:
                return False, f"Product {product_id} not found"
            
            mask = products_df['Product_ID'] == product_id
            if not mask.any():
                return False, f"Product {product_id} not found"
            
            idx = products_df[mask].index[0]
            
            # Update fields
            for key, value in updated_data.items():
                if key in products_df.columns:
                    products_df.at[idx, key] = value
            
            # Save
            if self.save_tab('Products', products_df):
                print(f"✅ Updated product: {product_id}")
                return True, f"Product {product_id} updated successfully"
            return False, "Failed to save changes"
            
        except Exception as e:
            print(f"❌ Error updating product: {e}")
            return False, f"Error updating product: {str(e)}"

    def mark_product_inactive(self, product_id):
        """Mark a product as inactive (soft delete)"""
        return self.update_product(product_id, {'Active': 'No'})

    def reactivate_product(self, product_id):
        """Reactivate an inactive product"""
        return self.update_product(product_id, {'Active': 'Yes'})

    def delete_product_permanently(self, product_id):
        """Permanently delete a product and its recipes"""
        try:
            # Delete from Products
            products_df = self.read_tab('Products')
            initial_count = len(products_df)
            products_df = products_df[products_df['Product_ID'] != product_id]
            
            if len(products_df) == initial_count:
                return False, f"Product {product_id} not found"
            
            # Delete associated recipes
            recipes_df = self.read_tab('Recipes')
            if not recipes_df.empty and 'Product_ID' in recipes_df.columns:
                recipes_df = recipes_df[recipes_df['Product_ID'] != product_id]
                self.save_tab('Recipes', recipes_df)
            
            # Save updated products
            if self.save_tab('Products', products_df):
                print(f"✅ Permanently deleted product: {product_id}")
                return True, f"Product {product_id} permanently deleted"
            return False, "Failed to save changes"
            
        except Exception as e:
            print(f"❌ Error deleting product: {e}")
            return False, f"Error deleting product: {str(e)}"

    def get_product_recipes(self, product_id):
        """Get all ingredients for a specific product"""
        recipes_df = self.read_tab('Recipes')
        ingredients_df = self.read_tab('Ingredients')
        
        if recipes_df.empty or 'Product_ID' not in recipes_df.columns:
            return pd.DataFrame()
        
        product_recipes = recipes_df[recipes_df['Product_ID'] == product_id].copy()
        if product_recipes.empty:
            return pd.DataFrame()
        
        if not ingredients_df.empty and 'Ingredient_ID' in ingredients_df.columns:
            merged = pd.merge(product_recipes, ingredients_df, 
                            on='Ingredient_ID', how='left')
            return merged[['Ingredient_ID', 'Ingredient_Name', 'Unit', 
                         'Quantity_Required', 'Cost_Per_Unit']]
        
        return product_recipes

    def calculate_product_cost(self, product_id):
        """Calculate total cost of a product based on its recipe"""
        recipe_items = self.get_product_recipes(product_id)
        
        if recipe_items.empty:
            return 0
        
        total_cost = 0
        for _, item in recipe_items.iterrows():
            cost = item.get('Cost_Per_Unit', 0) * item.get('Quantity_Required', 0)
            total_cost += cost
        
        return total_cost

    def update_all_product_costs(self):
        """Update costs for all products based on current ingredient prices"""
        try:
            products_df = self.read_tab('Products')
            
            if products_df.empty:
                return pd.DataFrame()
            
            # Calculate cost for each product
            costs = []
            for _, product in products_df.iterrows():
                cost = self.calculate_product_cost(product['Product_ID'])
                costs.append(cost)
            
            # Update cost columns
            products_df['Cost_Price'] = costs
            
            if 'Selling_Price' in products_df.columns:
                products_df['Profit_Margin'] = products_df['Selling_Price'] - products_df['Cost_Price']
                products_df['Margin_Percentage'] = (products_df['Profit_Margin'] / 
                                                  products_df['Selling_Price'] * 100).round(2)
            
            # Save updated products
            self.save_tab('Products', products_df)
            print(f"✅ Updated costs for {len(products_df)} products")
            return products_df
        except Exception as e:
            print(f"❌ Error updating product costs: {e}")
            return pd.DataFrame()

    # ===== INGREDIENT MANAGEMENT =====
    def generate_ingredient_id(self):
        """Generate a new unique ingredient ID"""
        ingredients_df = self.read_tab('Ingredients')
        
        if ingredients_df.empty or 'Ingredient_ID' not in ingredients_df.columns:
            return "ING001"
        
        ing_numbers = []
        for iid in ingredients_df['Ingredient_ID'].dropna():
            if isinstance(iid, str) and iid.startswith('ING'):
                try:
                    num = int(iid[3:])
                    ing_numbers.append(num)
                except:
                    pass
        
        next_num = max(ing_numbers) + 1 if ing_numbers else 1
        return f"ING{next_num:03d}"

    def add_ingredient(self, ingredient_data):
        """Add a new ingredient to the database"""
        try:
            ingredients_df = self.read_tab('Ingredients')
            
            # Format all fields properly
            processed_data = {}
            for key, value in ingredient_data.items():
                if key in ['Current_Stock', 'Cost_Per_Unit', 'Min_Stock_Level']:
                    # Handle numeric fields
                    if value == '' or value is None:
                        processed_data[key] = 0.0
                    else:
                        try:
                            processed_data[key] = float(value)
                        except (ValueError, TypeError):
                            processed_data[key] = 0.0
                elif key in ['Supplier', 'Description', 'Category', 'Ingredient_Name', 'Unit']:
                    # Handle text fields
                    processed_data[key] = str(value) if value is not None else ''
                elif key == 'Active':
                    # Handle active field
                    processed_data[key] = str(value).strip() if value else 'Yes'
                else:
                    processed_data[key] = value
            
            # Add timestamp
            processed_data['Last_Updated'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add the ingredient
            ingredients_df = pd.concat([ingredients_df, pd.DataFrame([processed_data])], ignore_index=True)
            
            if self.save_tab('Ingredients', ingredients_df):
                print(f"✅ Added ingredient: {processed_data['Ingredient_ID']}")
                return True, f"Added ingredient: {processed_data['Ingredient_ID']}"
            return False, "Failed to save ingredient"
            
        except Exception as e:
            print(f"❌ Error adding ingredient: {e}")
            return False, f"Error adding ingredient: {str(e)}"

    def update_ingredient(self, ingredient_id, updated_data):
        """Update an existing ingredient in the database"""
        try:
            ingredients_df = self.read_tab('Ingredients')
            
            if ingredients_df.empty or 'Ingredient_ID' not in ingredients_df.columns:
                return False, f"Ingredient {ingredient_id} not found"
            
            mask = ingredients_df['Ingredient_ID'] == ingredient_id
            if not mask.any():
                return False, f"Ingredient {ingredient_id} not found"
            
            idx = ingredients_df[mask].index[0]
            
            # Update each field with proper type handling
            for key, value in updated_data.items():
                if key in ingredients_df.columns:
                    # Handle empty/None values first
                    if value == '' or value is None:
                        if key in ['Current_Stock', 'Cost_Per_Unit', 'Min_Stock_Level']:
                            value = 0.0
                        elif key in ['Supplier', 'Description', 'Category']:
                            value = ''
                        elif key == 'Active':
                            value = 'Yes'
                        else:
                            value = ''
                    
                    # Ensure numeric fields are proper floats
                    if key in ['Current_Stock', 'Cost_Per_Unit', 'Min_Stock_Level']:
                        try:
                            value = float(value)
                        except (ValueError, TypeError):
                            value = 0.0
                    
                    # Update the value - ensure column dtype is correct
                    ingredients_df.at[idx, key] = value
            
            # Update timestamp
            ingredients_df.at[idx, 'Last_Updated'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save to database
            if self.save_tab('Ingredients', ingredients_df):
                print(f"✅ Updated ingredient: {ingredient_id}")
                return True, f"Updated ingredient: {ingredient_id}"
            return False, "Failed to save changes"
            
        except Exception as e:
            print(f"❌ Error updating ingredient: {e}")
            return False, f"Error updating ingredient: {str(e)}"

    def update_ingredient_stock(self, ingredient_id, new_stock, operation="set", amount=0, reason=""):
        """Update ingredient stock with tracking"""
        try:
            ingredients_df = self.read_tab('Ingredients')
            
            mask = ingredients_df['Ingredient_ID'] == ingredient_id
            if not mask.any():
                return False, f"Ingredient {ingredient_id} not found"
            
            idx = ingredients_df[mask].index[0]
            
            # Get current stock
            current_stock = float(ingredients_df.at[idx, 'Current_Stock']) if pd.notna(ingredients_df.at[idx, 'Current_Stock']) else 0.0
            
            # Ensure new_stock is a float
            new_stock = float(new_stock)
            
            # Update stock
            ingredients_df.at[idx, 'Current_Stock'] = new_stock
            ingredients_df.at[idx, 'Last_Updated'] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Save changes
            if self.save_tab('Ingredients', ingredients_df):
                # Log the change
                self.log_stock_change(ingredient_id, current_stock, new_stock, operation, amount, reason)
                return True, f"Updated stock for {ingredient_id}: {current_stock} → {new_stock}"
            return False, "Failed to save stock update"
            
        except Exception as e:
            print(f"❌ Error updating stock: {e}")
            return False, f"Error updating stock: {str(e)}"

    def log_stock_change(self, ingredient_id, old_stock, new_stock, operation, amount, reason):
        """Log stock changes to Inventory_Log"""
        try:
            logs_df = self.read_tab('Inventory_Log')
            
            change_type = "STOCK_UPDATE"
            if operation == "add":
                change_type = "STOCK_ADD"
            elif operation == "remove":
                change_type = "STOCK_REMOVE"
            
            new_log = {
                'Log_ID': f"LOG{len(logs_df) + 1:06d}",
                'Ingredient_ID': ingredient_id,
                'Change_Type': change_type,
                'Quantity': new_stock - old_stock,
                'Date': datetime.now().strftime("%Y-%m-%d"),
                'Notes': f"{reason} (Operation: {operation}, Amount: {amount})"
            }
            
            logs_df = pd.concat([logs_df, pd.DataFrame([new_log])], ignore_index=True)
            self.save_tab('Inventory_Log', logs_df)
            print(f"📝 Logged stock change for {ingredient_id}")
            
        except Exception as e:
            print(f"⚠️ Failed to log stock change: {e}")

    def delete_ingredient(self, ingredient_id):
        """Delete an ingredient"""
        try:
            ingredients_df = self.read_tab('Ingredients')
            
            if ingredients_df.empty or 'Ingredient_ID' not in ingredients_df.columns:
                return False, f"Ingredient {ingredient_id} not found"
            
            initial_count = len(ingredients_df)
            ingredients_df = ingredients_df[ingredients_df['Ingredient_ID'] != ingredient_id]
            
            if len(ingredients_df) == initial_count:
                return False, f"Ingredient {ingredient_id} not found"
            
            # Check if ingredient is used in recipes
            recipes_df = self.read_tab('Recipes')
            if not recipes_df.empty and 'Ingredient_ID' in recipes_df.columns:
                used_in = recipes_df[recipes_df['Ingredient_ID'] == ingredient_id]
                if not used_in.empty:
                    product_ids = used_in['Product_ID'].unique()[:3]  # Show first 3
                    product_list = ", ".join(product_ids)
                    if len(used_in['Product_ID'].unique()) > 3:
                        product_list += f" and {len(used_in['Product_ID'].unique()) - 3} more..."
                    return False, f"Cannot delete! Used in recipes for: {product_list}"
            
            if self.save_tab('Ingredients', ingredients_df):
                print(f"✅ Deleted ingredient: {ingredient_id}")
                return True, f"Ingredient {ingredient_id} deleted"
            return False, "Failed to save changes"
            
        except Exception as e:
            print(f"❌ Error deleting ingredient: {e}")
            return False, f"Error deleting ingredient: {str(e)}"

    # ===== INVENTORY MANAGEMENT =====
    def get_inventory_status(self):
        """Get current inventory status with alerts"""
        inventory_df = self.read_tab('Ingredients')
        
        if inventory_df.empty:
            return pd.DataFrame()
        
        inventory_df = inventory_df.copy()
        
        # Ensure Min_Stock_Level column exists
        if 'Min_Stock_Level' not in inventory_df.columns:
            inventory_df['Min_Stock_Level'] = 0
        
        # Calculate status
        inventory_df['Status'] = 'Normal'
        low_mask = inventory_df['Current_Stock'] <= inventory_df['Min_Stock_Level']
        critical_mask = inventory_df['Current_Stock'] <= (inventory_df['Min_Stock_Level'] * 0.5)
        
        inventory_df.loc[low_mask, 'Status'] = 'Low Stock'
        inventory_df.loc[critical_mask, 'Status'] = 'Critical'
        
        return inventory_df

    def get_all_products(self):
        """Get all active products"""
        products_df = self.read_tab('Products')
        if products_df.empty or 'Active' not in products_df.columns:
            return pd.DataFrame()
        
        # Filter active products
        active_products = products_df[products_df['Active'].astype(str).str.upper() == 'YES']
        return active_products

    def get_all_ingredients(self):
        """Get all ingredients"""
        return self.read_tab('Ingredients')

    # ===== SALES MANAGEMENT =====
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
            
            if self.save_tab('Sales', sales_df):
                print(f"💰 Recorded sale: {quantity} x {product_id}")
                return new_sale
            return None
            
        except Exception as e:
            print(f"❌ Error recording sale: {e}")
            return None

    def update_inventory_from_sale(self, product_id, quantity_sold):
        """Deduct ingredients from inventory when a product is sold"""
        try:
            # Get the recipe for this product
            recipe_items = self.get_product_recipes(product_id)
            
            if recipe_items.empty:
                return False, f"No recipe found for product {product_id}"
            
            # Get current inventory
            inventory_df = self.read_tab('Ingredients')
            if inventory_df.empty:
                return False, "No ingredients in inventory"
            
            # Check stock and prepare deductions
            deductions = []
            insufficient_stock = []
            
            for _, recipe_item in recipe_items.iterrows():
                ingredient_id = recipe_item['Ingredient_ID']
                quantity_needed = recipe_item['Quantity_Required']
                total_needed = quantity_needed * quantity_sold
                
                # Find ingredient
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
                    deductions.append({
                        'ingredient_id': ingredient_id,
                        'ingredient_name': recipe_item.get('Ingredient_Name', ingredient_id),
                        'deduction': total_needed,
                        'old_stock': current_stock,
                        'new_stock': current_stock - total_needed,
                        'index': idx
                    })
            
            # Check if we can proceed
            if insufficient_stock:
                return False, f"Insufficient stock:\n" + "\n".join(insufficient_stock)
            
            # Apply deductions
            for deduction in deductions:
                idx = deduction['index']
                inventory_df.at[idx, 'Current_Stock'] = deduction['new_stock']
            
            # Save inventory
            if not self.save_tab('Ingredients', inventory_df):
                return False, "Failed to save inventory changes"
            
            # Log the inventory change
            self.log_inventory_change(product_id, quantity_sold, deductions)
            
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
                    'Quantity': -deduction['deduction'],
                    'Date': datetime.now().strftime("%Y-%m-%d"),
                    'Notes': f"Product {product_id} x{quantity_sold}"
                }
                logs_df = pd.concat([logs_df, pd.DataFrame([new_log])], ignore_index=True)
            
            self.save_tab('Inventory_Log', logs_df)
            print(f"📝 Logged inventory change for {product_id}")
            
        except Exception as e:
            print(f"⚠️ Failed to log inventory change: {e}")

    # ===== EXPENSE MANAGEMENT =====
    def add_expense(self, expense_data):
        """Add a new expense record"""
        try:
            expenses_df = self.read_tab('Expenses')
            
            # Generate expense ID
            exp_numbers = []
            for exp_id in expenses_df['Expense_ID'].dropna():
                if isinstance(exp_id, str) and exp_id.startswith('EXP'):
                    try:
                        num = int(exp_id[3:])
                        exp_numbers.append(num)
                    except:
                        pass
            
            next_num = max(exp_numbers) + 1 if exp_numbers else 1
            expense_id = f"EXP{next_num:04d}"
            expense_data['Expense_ID'] = expense_id
            
            # Add expense
            expenses_df = pd.concat([expenses_df, pd.DataFrame([expense_data])], ignore_index=True)
            
            if self.save_tab('Expenses', expenses_df):
                print(f"✅ Added expense: {expense_data['Description']}")
                return True, f"Expense added (ID: {expense_id})"
            return False, "Failed to save expense"
            
        except Exception as e:
            print(f"❌ Error adding expense: {e}")
            return False, f"Error adding expense: {str(e)}"

    def get_expenses(self, start_date=None, end_date=None):
        """Get expenses with optional date filtering"""
        try:
            expenses_df = self.read_tab('Expenses')
            
            if expenses_df.empty or 'Expense_Date' not in expenses_df.columns:
                return pd.DataFrame()
            
            # Convert date column
            expenses_df['Expense_Date'] = pd.to_datetime(expenses_df['Expense_Date'], errors='coerce')
            
            # Apply date filters
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

    # ==== ADD THIS MISSING METHOD ====
    def get_expense_summary(self, month=None, year=None):
        """Get expense summary by category"""
        try:
            expenses_df = self.read_tab('Expenses')
            
            if expenses_df.empty:
                return pd.DataFrame()
            
            # Convert date
            if 'Expense_Date' in expenses_df.columns:
                expenses_df['Expense_Date'] = pd.to_datetime(expenses_df['Expense_Date'], errors='coerce')
                expenses_df['Year'] = expenses_df['Expense_Date'].dt.year
                expenses_df['Month'] = expenses_df['Expense_Date'].dt.month
                
                # Filter by month/year if provided
                if year:
                    expenses_df = expenses_df[expenses_df['Year'] == year]
                if month:
                    expenses_df = expenses_df[expenses_df['Month'] == month]
            
            # Group by category
            if 'Category' in expenses_df.columns and 'Amount' in expenses_df.columns:
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
    # =================================

    def delete_expense(self, expense_id):
        """Delete an expense record"""
        try:
            expenses_df = self.read_tab('Expenses')
            
            initial_count = len(expenses_df)
            expenses_df = expenses_df[expenses_df['Expense_ID'] != expense_id]
            
            if len(expenses_df) == initial_count:
                return False, f"Expense {expense_id} not found"
            
            if self.save_tab('Expenses', expenses_df):
                print(f"✅ Deleted expense: {expense_id}")
                return True, f"Expense {expense_id} deleted"
            return False, "Failed to save changes"
            
        except Exception as e:
            print(f"❌ Error deleting expense: {e}")
            return False, f"Error deleting expense: {str(e)}"

    # ===== RECIPE MANAGEMENT =====
    def save_recipe(self, product_id, recipe_items):
        """Save or update a recipe"""
        try:
            recipes_df = self.read_tab('Recipes')
            
            # Remove existing recipe for this product
            if not recipes_df.empty and 'Product_ID' in recipes_df.columns:
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
            
            if self.save_tab('Recipes', recipes_df):
                print(f"✅ Saved recipe for {product_id}")
                return True
            return False
            
        except Exception as e:
            print(f"❌ Error saving recipe: {e}")
            return False

    # ===== UTILITY METHODS =====
    def add_inventory_stock(self, ingredient_id, quantity_to_add, notes=""):
        """Add stock to an ingredient (purchase/replenishment)"""
        try:
            inventory_df = self.read_tab('Ingredients')
            
            if inventory_df.empty or 'Ingredient_ID' not in inventory_df.columns:
                return False, "No ingredients found"
            
            ingredient_idx = inventory_df[inventory_df['Ingredient_ID'] == ingredient_id].index
            if len(ingredient_idx) == 0:
                return False, f"Ingredient {ingredient_id} not found"
            
            idx = ingredient_idx[0]
            old_stock = inventory_df.at[idx, 'Current_Stock']
            new_stock = old_stock + quantity_to_add
            
            # Update stock
            inventory_df.at[idx, 'Current_Stock'] = new_stock
            
            if self.save_tab('Ingredients', inventory_df):
                # Log the addition
                self.log_stock_change(ingredient_id, old_stock, new_stock, "add", quantity_to_add, notes)
                ingredient_name = inventory_df.at[idx, 'Ingredient_Name']
                print(f"📦 Added {quantity_to_add} to {ingredient_name}")
                return True, f"Added {quantity_to_add} to {ingredient_name}"
            return False, "Failed to save stock update"
            
        except Exception as e:
            print(f"❌ Error adding stock: {e}")
            return False, f"Error adding stock: {str(e)}"

    def get_inventory_logs(self, days_back=30):
        """Get recent inventory logs"""
        logs_df = self.read_tab('Inventory_Log')
        
        if logs_df.empty or 'Date' not in logs_df.columns:
            return pd.DataFrame()
        
        try:
            logs_df['Date'] = pd.to_datetime(logs_df['Date'], errors='coerce')
            cutoff_date = datetime.now() - timedelta(days=days_back)
            recent_logs = logs_df[logs_df['Date'] >= cutoff_date].copy()
            return recent_logs.sort_values('Date', ascending=False)
        except:
            return logs_df.tail(100)