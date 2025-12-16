# main_app.py - SIMPLE VERSION
import traceback
import sys
import os

def main():
    try:
        print("=" * 50)
        print("🚀 STARTING INVENTORY MANAGER")
        print("=" * 50)
        
        # Add current directory to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Import modules
        from config import CLIENT_CONFIG
        from modules.database import InventoryDB
        from modules.gui_builder import InventoryGUI
        import customtkinter as ctk
        
        print("✅ All modules imported successfully")
        
        # Create database connection
        print(f"💾 Loading database: {CLIENT_CONFIG['excel_file']}")
        db = InventoryDB(CLIENT_CONFIG['excel_file'])
        print("✅ Database connected")
        
        # Setup GUI theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create main window
        window = ctk.CTk()
        
        # Create GUI
        app = InventoryGUI(window, db, CLIENT_CONFIG)
        
        print("\n" + "=" * 50)
        print("✅ APPLICATION STARTED!")
        print("=" * 50)
        
        # Start the application
        window.mainloop()
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        traceback.print_exc()
        input("\nPress Enter to close...")

if __name__ == "__main__":
    main()