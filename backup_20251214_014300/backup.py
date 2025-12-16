# backup.py - Simple backup script
import os
import shutil
from datetime import datetime

def create_backup():
    # Create backup folder with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = f"backup_{timestamp}"
    
    # Create backup folder
    os.makedirs(backup_folder, exist_ok=True)
    
    # Copy all Python files
    files_copied = 0
    for filename in os.listdir("."):
        if filename.endswith(".py"):
            shutil.copy2(filename, os.path.join(backup_folder, filename))
            files_copied += 1
            print(f"📄 Copied: {filename}")
    
    print(f"\n✅ Backup created: {backup_folder}/")
    print(f"   {files_copied} files backed up")
    print("\n💡 To restore: Copy files from backup folder back to main folder")

if __name__ == "__main__":
    print("🛡️  Creating backup of all Python files...")
    create_backup()
    input("\nPress Enter to close...")