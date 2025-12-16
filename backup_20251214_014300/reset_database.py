# reset_database.py
import os
import pandas as pd
from datetime import datetime

def recreate_database():
    """Recreate the inventory database with proper structure"""
    excel_file = "data/inventory.xlsx"
    
    print(f"🔧 Recreating database: {excel_file}")
    
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Define all tabs with proper column structure
    tabs = {
        'Products': pd.DataFrame(columns=[
            'Product_ID', 'Product_Name', 'Category', 
            'Selling_Price', 'Active', 'Cost_Price',
            'Profit_Margin', 'Margin_Percentage', 'Notes'
        ]),
        
        'Ingredients': pd.DataFrame(columns=[
            'Ingredient_ID', 'Ingredient_Name', 'Unit', 
            'Category', 'Current_Stock', 'Min_Stock', 'Cost_Per_Unit', 'Notes'
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
    
    # Create Excel file with all tabs
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        for tab_name, df in tabs.items():
            df.to_excel(writer, sheet_name=tab_name, index=False)
            print(f"✅ Created tab: {tab_name}")
    
    print(f"\n🎉 Database created successfully!")
    print(f"Location: {excel_file}")
    print(f"Size: {os.path.getsize(excel_file)} bytes")
    
    # Add some sample data (optional)
    add_sample_data(excel_file)

def add_sample_data(excel_file):
    """Add some sample data for testing"""
    print("\n📝 Adding sample data...")
    
    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        # Sample products
        products_data = {
            'Product_ID': ['PROD001', 'PROD002', 'PROD003'],
            'Product_Name': ['Chocolate Cake', 'Vanilla Cupcake', 'Cheesecake'],
            'Category': ['Cake', 'Pastry', 'Cake'],
            'Selling_Price': [25.00, 3.50, 30.00],
            'Active': ['Yes', 'Yes', 'Yes'],
            'Cost_Price': [10.00, 1.20, 12.00],
            'Profit_Margin': [15.00, 2.30, 18.00],
            'Margin_Percentage': [60.0, 65.7, 60.0],
            'Notes': ['Best seller', 'Popular item', 'New addition']
        }
        
        products_df = pd.DataFrame(products_data)
        products_df.to_excel(writer, sheet_name='Products', index=False)
        print(f"✅ Added {len(products_df)} sample products")
        
        # Sample ingredients
        ingredients_data = {
            'Ingredient_ID': ['ING001', 'ING002', 'ING003', 'ING004', 'ING005'],
            'Ingredient_Name': ['Flour', 'Sugar', 'Eggs', 'Butter', 'Chocolate'],
            'Unit': ['kg', 'kg', 'pcs', 'kg', 'kg'],
            'Category': ['Dry Goods', 'Dry Goods', 'Dairy', 'Dairy', 'Dry Goods'],
            'Current_Stock': [10.0, 5.0, 50.0, 3.0, 2.0],
            'Min_Stock': [2.0, 1.0, 24.0, 1.0, 0.5],
            'Cost_Per_Unit': [1.50, 2.00, 0.30, 8.00, 12.00],
            'Notes': ['All-purpose flour', 'White sugar', 'Large eggs', 'Unsalted butter', 'Dark chocolate']
        }
        
        ingredients_df = pd.DataFrame(ingredients_data)
        ingredients_df.to_excel(writer, sheet_name='Ingredients', index=False)
        print(f"✅ Added {len(ingredients_df)} sample ingredients")
        
        # Sample sales (last 7 days)
        from datetime import datetime, timedelta
        import random
        
        sales_data = []
        products = ['PROD001', 'PROD002', 'PROD003']
        
        for i in range(20):
            date = datetime.now() - timedelta(days=random.randint(0, 7))
            product = random.choice(products)
            quantity = random.randint(1, 5)
            price = 25.00 if product == 'PROD001' else 3.50 if product == 'PROD002' else 30.00
            total = quantity * price
            
            sales_data.append({
                'Sale_ID': f"SALE{1000 + i}",
                'Product_ID': product,
                'Quantity': quantity,
                'Sale_Date': date.strftime('%Y-%m-%d'),
                'Sale_Time': date.strftime('%H:%M:%S'),
                'Total_Amount': total
            })
        
        sales_df = pd.DataFrame(sales_data)
        sales_df.to_excel(writer, sheet_name='Sales', index=False)
        print(f"✅ Added {len(sales_df)} sample sales")

if __name__ == "__main__":
    print("=" * 50)
    print("DATABASE RESET TOOL")
    print("=" * 50)
    
    # Ask for confirmation
    response = input("This will recreate your database. Continue? (y/n): ")
    
    if response.lower() == 'y':
        # Backup old file if exists
        if os.path.exists("data/inventory.xlsx"):
            backup_name = f"data/inventory_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            os.rename("data/inventory.xlsx", backup_name)
            print(f"📦 Old database backed up as: {backup_name}")
        
        recreate_database()
        
        print("\n" + "=" * 50)
        print("🎯 NEXT STEPS:")
        print("1. Restart your Inventory Application")
        print("2. You should see sample data loaded")
        print("3. Test adding new products/ingredients")
        print("=" * 50)
    else:
        print("Operation cancelled.")