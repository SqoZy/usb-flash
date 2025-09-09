"""
Build script for USB Flash Drive Manager
Creates a distributable executable using PyInstaller
"""

import PyInstaller.__main__
import os
import shutil
import zipfile
from datetime import datetime

def clean_build_folders():
    """Clean previous build artifacts"""
    folders_to_clean = ['dist', 'build', '__pycache__']
    for folder in folders_to_clean:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"✓ Cleaned {folder}")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")

    # PyInstaller configuration with additional options to reduce false positives
    args = [
        '--windowed',                    # No console window
        '--onefile',                     # Single executable file
        '--name=USB_Flash_Manager',      # Executable name
        '--clean',                       # Clean cache
        '--noconfirm',                  # Replace output directory
        '--add-data=README.md;.',       # Include README
        '--noupx',                      # Don't use UPX compression (reduces false positives)
        '--exclude-module=PIL',         # Exclude unused modules
        '--exclude-module=matplotlib',
        '--exclude-module=numpy',
        '--exclude-module=scipy',
        '--exclude-module=pandas',
        'usb_manager.py'                # Main script
    ]

    # Add icon if available
    if os.path.exists('usb_icon.ico'):
        args.extend(['--icon=usb_icon.ico'])

    # Add version info to make it look more legitimate
    version_info = """
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1,0,0,0),
    prodvers=(1,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Your Company'),
        StringStruct(u'FileDescription', u'USB Flash Drive Manager'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'USB_Flash_Manager'),
        StringStruct(u'LegalCopyright', u'Copyright (C) 2024'),
        StringStruct(u'OriginalFilename', u'USB_Flash_Manager.exe'),
        StringStruct(u'ProductName', u'USB Flash Drive Manager'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

    # Write version info to file
    with open('version.txt', 'w') as f:
        f.write(version_info)

    args.extend(['--version-file=version.txt'])

    # Run PyInstaller
    PyInstaller.__main__.run(args)

    # Clean up version file
    if os.path.exists('version.txt'):
        os.remove('version.txt')

    print("✓ Executable created successfully!")

def create_distribution_package():
    """Create a complete distribution package"""
    print("Creating distribution package...")

    version = "1.0.0"
    package_name = f"USB_Flash_Manager_v{version}"

    # Create package directory
    if os.path.exists(package_name):
        shutil.rmtree(package_name)
    os.makedirs(package_name)

    # Copy essential files
    files_to_copy = [
        ('dist/USB_Flash_Manager.exe', 'USB_Flash_Manager.exe'),
        ('README.md', 'User_Guide.md'),
        ('requirements.txt', 'requirements.txt')
    ]

    for src, dst in files_to_copy:
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(package_name, dst))
            print(f"✓ Copied {src} -> {dst}")

    # Create installation instructions
    create_install_instructions(package_name)

    # Create ZIP file for distribution
    zip_filename = f'{package_name}.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_name):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, package_name)
                zipf.write(file_path, arcname)

    print(f"✓ Distribution package created: {zip_filename}")
    return zip_filename

def create_install_instructions(package_dir):
    """Create installation and usage instructions"""
    instructions = """# USB Flash Drive Manager - Installation Instructions

## For Your Colleagues

### System Requirements
- Windows 10 or Windows 11
- Administrator privileges (required for formatting USB drives)

### Installation Steps
1. Extract all files from the ZIP to a folder (e.g., Desktop)
2. Right-click on `USB_Flash_Manager.exe`
3. Select "Run as administrator"
4. If Windows shows security warning, click "More info" then "Run anyway"

### How to Use
1. **Connect USB drives** to your computer
2. **Launch the application** as administrator
3. **Scan for drives**: Click "Scan for USB Drives"
4. **Select file system**: Choose from dropdown (exFAT recommended)
5. **Format drives**:
   - Select specific drive and click "Format Selected Drive", OR
   - Click "Format All USB Drives" for bulk formatting
6. **Monitor progress** in the status window

### File System Guide
- **exFAT**: Best for USB drives (recommended)
- **NTFS**: Windows native, good for large files
- **FAT32**: Legacy compatibility (4GB file limit)

### Troubleshooting
- **"Access Denied"**: Run as administrator
- **Drive not detected**: Ensure USB is properly connected
- **Format fails**: Try different file system or check drive health

### Security Warning
WARNING: This tool will PERMANENTLY ERASE all data on formatted drives!
Always verify drive selection before confirming format operations.

### Support
For issues or questions, contact: [Your Name/Email]
"""

    with open(os.path.join(package_dir, 'INSTALLATION_GUIDE.txt'), 'w', encoding='utf-8') as f:
        f.write(instructions)

def main():
    """Main build process"""
    print("=== USB Flash Drive Manager - Build Process ===")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Step 1: Clean previous builds
        clean_build_folders()

        # Step 2: Build executable
        build_executable()

        # Step 3: Create distribution package
        package_file = create_distribution_package()

        print("\n=== Build Completed Successfully! ===")
        print(f"📦 Distribution file: {package_file}")
        print("📋 Ready to share with colleagues!")
        print("\nNext steps:")
        print("1. Test the executable on a clean machine")
        print("2. Share the ZIP file with your colleagues")
        print("3. Include the installation guide")

    except Exception as e:
        print(f"\n❌ Build failed: {str(e)}")
        print("Please check the error and try again.")

if __name__ == "__main__":
    main()
