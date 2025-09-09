# USB Flash Drive Manager

A Python application for managing multiple USB flash drives with a GUI interface. This tool integrates with PowerShell for drive detection and formatting operations.

## Features

- **USB Drive Detection**: Automatically scan and detect USB drives using PowerShell
- **Manual Drive Entry**: Add drives manually by specifying drive letter and label
- **Bulk Formatting**: Format multiple drives simultaneously
- **Real-time Status**: Monitor formatting progress and status
- **PowerShell Integration**: Leverage Windows PowerShell for drive management

## Requirements

- Windows OS
- Python 3.7+
- PowerShell (included with Windows)

## Installation

1. Clone or download this repository
2. Install required Python packages:
   ```
   pip install -r requirements.txt
   ```

## Dependencies

- `tkinter` - GUI framework (included with Python)
- `psutil` - System and process utilities (optional)
- `pywin32` - Windows API access (optional)

## Usage

1. Run the main application:
   ```
   python usb_manager.py
   ```

2. **Scanning for USB Drives**:
   - Click "Scan for USB Drives" to automatically detect connected USB drives
   - Use "Refresh" to update the drive list

3. **Manual Drive Entry**:
   - Enter drive letter (e.g., E, F, G)
   - Optionally enter a label
   - Click "Add Drive" to add to the list

4. **Formatting Operations**:
   - Select specific drives or use "Format All USB Drives"
   - Monitor progress in the status log

## Project Structure

```
usbFlash/
├── usb_manager.py          # Main GUI application
├── powershell_manager.py   # PowerShell integration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Key Components

### USB Manager (`usb_manager.py`)
The main GUI application built with tkinter that provides:
- Drive detection and listing
- Manual drive entry
- Format operation controls
- Status monitoring

### PowerShell Manager (`powershell_manager.py`)
Handles Windows PowerShell integration for:
- USB drive detection using WMI
- Drive formatting operations
- Administrator privilege checking

## Configuration

### PowerShell Security
If PowerShell execution is restricted:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Limitations

- Administrator privileges may be required for formatting operations
- PowerShell must be available and unrestricted

## Security Notes

- This tool can format and erase USB drives - use with caution
- Administrator privileges may be required
- Always verify drive selection before formatting
- Test with non-critical drives first

## Troubleshooting

### Common Issues

1. **"Import could not be resolved" errors**:
   - Install missing packages: `pip install -r requirements.txt`
   - Some packages are optional and wrapped in try/except blocks

2. **PowerShell access denied**:
   - Run as Administrator
   - Check PowerShell execution policy

## Development

To extend functionality:

1. **Enhanced GUI**: Modify `usb_manager.py` with additional tkinter widgets
2. **Better drive detection**: Enhance PowerShell queries in `powershell_manager.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is provided as-is for educational and utility purposes. Use at your own risk.

## Disclaimer

This tool can permanently erase data on USB drives. Always verify your selections and ensure you have backups of important data. The authors are not responsible for data loss.
