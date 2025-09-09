"""
USB Flash Drive Manager
A Python application for managing multiple USB flash drives with GUI interface.
Integrates with PowerShell for drive detection and formatting operations.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import os
from powershell_manager import PowerShellManager

# Optional imports with fallbacks
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("psutil not available - some features may be limited")

try:
    import win32api
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("win32api not available - some Windows features may be limited")

class USBManager:
    def __init__(self, root):
        self.root = root
        self.root.title("USB Flash Drive Manager")
        self.root.geometry("800x600")

        # USB drive tracking
        self.usb_drives = []

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(main_frame, text="USB Flash Drive Manager",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # USB Drive Detection Section
        detection_frame = ttk.LabelFrame(main_frame, text="USB Drive Detection", padding="10")
        detection_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(detection_frame, text="Scan for USB Drives",
                  command=self.scan_usb_drives).grid(row=0, column=0, padx=(0, 10))

        ttk.Button(detection_frame, text="Refresh",
                  command=self.refresh_drives).grid(row=0, column=1)

        # Admin status indicator
        is_admin = PowerShellManager.check_admin_rights()
        admin_text = "✓ Administrator" if is_admin else "⚠ Not Administrator"
        admin_color = "green" if is_admin else "red"
        ttk.Label(detection_frame, text=admin_text, foreground=admin_color).grid(row=0, column=2, padx=(20, 0))

        # USB Drives List
        drives_frame = ttk.LabelFrame(main_frame, text="Detected USB Drives", padding="10")
        drives_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Treeview for drives
        columns = ("Drive", "Label", "Size", "Free", "Status")
        self.drives_tree = ttk.Treeview(drives_frame, columns=columns, show="headings", height=8)

        for col in columns:
            self.drives_tree.heading(col, text=col)
            self.drives_tree.column(col, width=120)

        self.drives_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(drives_frame, orient=tk.VERTICAL, command=self.drives_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.drives_tree.configure(yscrollcommand=scrollbar.set)

        # Manual Drive Entry Section
        manual_frame = ttk.LabelFrame(main_frame, text="Manual Drive Entry", padding="10")
        manual_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(manual_frame, text="Drive Letter:").grid(row=0, column=0, padx=(0, 5))
        self.drive_entry = ttk.Entry(manual_frame, width=5)
        self.drive_entry.grid(row=0, column=1, padx=(0, 10))

        ttk.Label(manual_frame, text="Label:").grid(row=0, column=2, padx=(0, 5))
        self.label_entry = ttk.Entry(manual_frame, width=15)
        self.label_entry.grid(row=0, column=3, padx=(0, 10))

        ttk.Button(manual_frame, text="Add Drive",
                  command=self.add_manual_drive).grid(row=0, column=4)

        # Format Operations Section
        format_frame = ttk.LabelFrame(main_frame, text="Format Operations", padding="10")
        format_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # Format buttons
        format_buttons_frame = ttk.Frame(format_frame)
        format_buttons_frame.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        ttk.Button(format_buttons_frame, text="Format Selected Drive",
                  command=self.format_selected_drive).grid(row=0, column=0, padx=(0, 10))

        ttk.Button(format_buttons_frame, text="Format All USB Drives",
                  command=self.format_all_drives).grid(row=0, column=1, padx=(0, 10))

        # Warning label
        warning_label = ttk.Label(format_frame,
                                 text="⚠ WARNING: Formatting will erase all data on the drive(s)!",
                                 foreground="red")
        warning_label.grid(row=1, column=0, columnspan=3, pady=(5, 0))

        # Status Section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        self.status_text = tk.Text(status_frame, height=8, width=70)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        status_scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        status_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=status_scrollbar.set)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        drives_frame.columnconfigure(0, weight=1)
        drives_frame.rowconfigure(0, weight=1)
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)

    def log_status(self, message):
        """Add message to status log"""
        self.status_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()

    def scan_usb_drives(self):
        """Scan for USB drives using PowerShell Manager"""
        self.log_status("Scanning for USB drives...")

        try:
            drives = PowerShellManager.get_usb_drives()

            self.usb_drives.clear()
            # Clear existing items
            for item in self.drives_tree.get_children():
                self.drives_tree.delete(item)

            for drive_info in drives:
                self.usb_drives.append({
                    'drive': drive_info['Drive'],
                    'label': drive_info['Label'],
                    'size': drive_info['Size'],
                    'free': drive_info['Free'],
                    'status': 'Ready'
                })

                self.drives_tree.insert('', 'end', values=(
                    drive_info['Drive'],
                    drive_info['Label'],
                    drive_info['Size'],
                    drive_info['Free'],
                    'Ready'
                ))

            self.log_status(f"Found {len(self.usb_drives)} USB drive(s)")

            # Also show disk mapping
            disk_map = PowerShellManager.get_usb_disk_letter_map()
            if disk_map:
                self.log_status(f"Disk mapping: {disk_map}")

        except Exception as e:
            self.log_status(f"Error scanning drives: {str(e)}")

    def refresh_drives(self):
        """Refresh the drive list"""
        self.scan_usb_drives()

    def add_manual_drive(self):
        """Add a drive manually"""
        drive = self.drive_entry.get().strip().upper()
        label = self.label_entry.get().strip()

        if not drive:
            messagebox.showerror("Error", "Please enter a drive letter")
            return

        if not drive.endswith(':'):
            drive += ':'

        # Check if drive already exists
        for existing_drive in self.usb_drives:
            if existing_drive['drive'] == drive:
                messagebox.showwarning("Warning", "Drive already exists")
                return

        self.usb_drives.append({
            'drive': drive,
            'label': label if label else "Manual Entry",
            'size': "Unknown",
            'free': "Unknown",
            'status': 'Ready'
        })

        self.drives_tree.insert('', 'end', values=(
            drive,
            label if label else "Manual Entry",
            "Unknown",
            "Unknown",
            'Ready'
        ))

        self.drive_entry.delete(0, tk.END)
        self.label_entry.delete(0, tk.END)

        self.log_status(f"Added drive {drive} manually")

    def format_selected_drive(self):
        """Format the selected USB drive"""
        selected_items = self.drives_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a drive to format")
            return

        # Check admin rights
        if not PowerShellManager.check_admin_rights():
            messagebox.showerror("Error", "Administrator privileges required for formatting drives")
            return

        # Get selected drive info
        selected_item = selected_items[0]
        drive_values = self.drives_tree.item(selected_item)['values']
        drive_letter = drive_values[0]  # Drive letter (e.g., 'E:')

        # Get disk mapping to find disk number
        disk_map = PowerShellManager.get_usb_disk_letter_map()
        disk_number = None
        for disk_num, letter in disk_map.items():
            if letter == drive_letter:
                disk_number = disk_num
                break

        if disk_number is None:
            messagebox.showerror("Error", f"Could not find disk number for drive {drive_letter}")
            return

        # Simple confirmation dialog
        result = messagebox.askyesno(
            "Confirm Format",
            f"Are you sure you want to format drive {drive_letter} (Disk {disk_number})?\n\n"
            "This will run the following commands:\n"
            f"1. Diskpart: select disk {disk_number}, clean, convert mbr, create partition primary\n"
            f"2. Format: format {drive_letter[:-1] if drive_letter.endswith(':') else drive_letter}: /q\n\n"
            "⚠ ALL DATA ON THIS DRIVE WILL BE PERMANENTLY ERASED!"
        )

        if not result:
            return

        # Update status in tree
        self.drives_tree.item(selected_item, values=(
            drive_values[0], drive_values[1], drive_values[2], drive_values[3], "Formatting..."
        ))

        self.log_status(f"Starting format of drive {drive_letter} (Disk {disk_number})...")
        self.log_status(f"Commands: diskpart (select disk {disk_number}, clean, convert mbr, create partition primary) + format {drive_letter[:-1] if drive_letter.endswith(':') else drive_letter}: /q")

        # Run format in background thread
        def format_thread():
            try:
                result = PowerShellManager.format_usb_drive(disk_number, drive_letter)

                # Update UI in main thread
                self.root.after(0, lambda: self.format_complete_callback(selected_item, result, drive_letter))

            except Exception as e:
                error_msg = f"Format failed with exception: {str(e)}"
                self.root.after(0, lambda: self.log_status(error_msg))
                self.root.after(0, lambda: self.drives_tree.item(selected_item, values=(
                    drive_values[0], drive_values[1], drive_values[2], drive_values[3], "Format Failed"
                )))

        threading.Thread(target=format_thread, daemon=True).start()

    def format_all_drives(self):
        """Format all USB drives"""
        # Check admin rights
        if not PowerShellManager.check_admin_rights():
            messagebox.showerror("Error", "Administrator privileges required for formatting drives")
            return

        disk_map = PowerShellManager.get_usb_disk_letter_map()
        if not disk_map:
            messagebox.showwarning("Warning", "No USB drives found to format")
            return

        # Confirm with user
        result = messagebox.askyesno(
            "Confirm Format All",
            f"Are you sure you want to format ALL {len(disk_map)} USB drives?\n\n"
            "⚠ ALL DATA ON THESE DRIVES WILL BE PERMANENTLY ERASED!\n\n"
            f"Drives to format: {', '.join(disk_map.values())}"
        )

        if not result:
            return

        self.log_status(f"Starting format of all {len(disk_map)} USB drives...")

        # Run format in background thread
        def format_all_thread():
            try:
                results = PowerShellManager.format_all_usb_drives()

                # Update UI in main thread
                self.root.after(0, lambda: self.format_all_complete_callback(results))

            except Exception as e:
                error_msg = f"Format all failed with exception: {str(e)}"
                self.root.after(0, lambda: self.log_status(error_msg))

        threading.Thread(target=format_all_thread, daemon=True).start()

    def format_complete_callback(self, tree_item, result, drive_letter):
        """Callback when single drive format completes"""
        if result['success']:
            self.log_status(f"✓ {result['message']}")
            # Update tree status
            values = list(self.drives_tree.item(tree_item)['values'])
            values[4] = "Formatted"
            self.drives_tree.item(tree_item, values=values)
        else:
            self.log_status(f"✗ Format failed for {drive_letter}: {result['message']}")
            # Update tree status
            values = list(self.drives_tree.item(tree_item)['values'])
            values[4] = "Format Failed"
            self.drives_tree.item(tree_item, values=values)

    def format_all_complete_callback(self, results):
        """Callback when all drives format completes"""
        successful = 0
        failed = 0

        for result in results:
            if result['success']:
                successful += 1
                self.log_status(f"✓ {result['message']}")
            else:
                failed += 1
                self.log_status(f"✗ {result['message']}")

        self.log_status(f"Format all completed: {successful} successful, {failed} failed")

        # Refresh the drive list after formatting
        self.refresh_drives()

def main():
    root = tk.Tk()
    app = USBManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
