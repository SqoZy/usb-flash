"""
PowerShell Integration Module
Handles PowerShell commands for USB drive detection and management.
"""

import subprocess
import json
import re
import tempfile
import os

class PowerShellManager:
    @staticmethod
    def run_command(command, capture_output=True):
        """Execute a PowerShell command and return result"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=capture_output,
                text=True,
                shell=False,
                timeout=30
            )
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': 'Command timed out',
                'returncode': -1
            }
        except Exception as e:
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'returncode': -1
            }

    @staticmethod
    def get_usb_drives():
        """Get list of USB drives (DriveType 2) with detailed information"""
        ps_command = """Get-WmiObject -Class Win32_LogicalDisk | Where-Object {$_.DriveType -eq 2} | ForEach-Object { $size = if ($_.Size) { [math]::Round($_.Size / 1GB, 2) } else { 0 }; $free = if ($_.FreeSpace) { [math]::Round($_.FreeSpace / 1GB, 2) } else { 0 }; $used = $size - $free; $label = if ($_.VolumeName) { $_.VolumeName } else { 'No Label' }; $fs = if ($_.FileSystem) { $_.FileSystem } else { 'Unknown' }; $sn = if ($_.VolumeSerialNumber) { $_.VolumeSerialNumber } else { 'Unknown' }; \"$($_.DeviceID)|$label|$size|$free|$used|$fs|$sn\" }"""

        result = PowerShellManager.run_command(ps_command)

        if result['success']:
            drives = []
            for line in result['stdout'].strip().split('\n'):
                line = line.strip()
                if line and '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 6:
                        drives.append({
                            'Drive': parts[0],
                            'Label': parts[1],
                            'Size': f"{parts[2]} GB",
                            'Free': f"{parts[3]} GB",
                            'Used': f"{parts[4]} GB",
                            'FileSystem': parts[5],
                            'SerialNumber': parts[6] if len(parts) > 6 else 'Unknown'
                        })
            return drives
        return []

    @staticmethod
    def get_usb_disk_letter_map():
        """Get mapping of USB disk numbers to drive letters (excluding disk 0)"""
        ps_command = """Get-WmiObject Win32_DiskDrive | Where-Object { $_.InterfaceType -eq 'USB' } | ForEach-Object { $disk = $_; Get-WmiObject Win32_DiskPartition | Where-Object { $_.DiskIndex -eq $disk.Index } | ForEach-Object { $partition = $_; Get-WmiObject Win32_LogicalDiskToPartition | Where-Object { $_.Antecedent -match "Disk #$($disk.Index)," } | ForEach-Object { $deviceID = ($_.Dependent -split '\"')[1]; \"$($disk.Index)|$deviceID\" } } }"""

        result = PowerShellManager.run_command(ps_command)
        disk_map = {}

        if result['success']:
            for line in result['stdout'].strip().split('\n'):
                line = line.strip()
                if line and '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        try:
                            disk_num = int(parts[0])
                            if disk_num > 0:  # Exclude disk 0 (primary disk)
                                disk_map[disk_num] = parts[1]
                        except ValueError:
                            continue

        return disk_map

    @staticmethod
    def check_admin_rights():
        """Check if running with administrator privileges"""
        ps_command = "([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] \"Administrator\")"
        result = PowerShellManager.run_command(ps_command)

        if result['success']:
            return result['stdout'].strip().lower() == 'true'
        return False

    @staticmethod
    def format_usb_drive(disk_number, drive_letter):
        """
        Format a USB drive using the exact diskpart commands specified by user

        Args:
            disk_number (int): The disk number (e.g., 2 for Disk 2)
            drive_letter (str): The drive letter (e.g., 'E:' or 'E')

        Returns:
            dict: Result with success status and messages
        """
        # Ensure drive letter is just the letter without colon
        if drive_letter.endswith(':'):
            drive_letter = drive_letter[:-1]

        # Create diskpart script exactly as user specified
        diskpart_script = f"""select disk {disk_number}
clean
convert mbr
create partition primary
exit
"""

        try:
            # Create temporary diskpart script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as script_file:
                script_file.write(diskpart_script)
                script_file_path = script_file.name

            # Run diskpart with the script
            diskpart_command = f'diskpart /s "{script_file_path}"'
            diskpart_result = PowerShellManager.run_command(diskpart_command)

            # Clean up the temporary file
            try:
                os.unlink(script_file_path)
            except:
                pass  # Ignore cleanup errors

            if not diskpart_result['success']:
                return {
                    'success': False,
                    'message': f"Diskpart failed: {diskpart_result['stderr']}",
                    'diskpart_output': diskpart_result['stdout']
                }

            # Wait for diskpart operations to complete - increased wait time
            import time
            time.sleep(15)  # Increased from 5 to 15 seconds

            # Run the format command exactly as user specified: format {drive_letter}: /q
            format_command = f'format {drive_letter}: /q'

            # Create batch file to automatically answer the prompts
            batch_script = """@echo off
echo Y
echo Y
"""

            with tempfile.NamedTemporaryFile(mode='w', suffix='.bat', delete=False) as batch_file:
                batch_file.write(batch_script)
                batch_file_path = batch_file.name

            # Run format command using cmd with the batch file as input
            full_command = f'cmd /c "type "{batch_file_path}" | {format_command}"'
            format_result = PowerShellManager.run_command(full_command)

            # Clean up batch file
            try:
                os.unlink(batch_file_path)
            except:
                pass

            if format_result['success']:
                return {
                    'success': True,
                    'message': f"Successfully formatted disk {disk_number} (drive {drive_letter}:)",
                    'diskpart_output': diskpart_result['stdout'],
                    'format_output': format_result['stdout']
                }
            else:
                return {
                    'success': False,
                    'message': f"Format failed: {format_result['stderr']}",
                    'diskpart_output': diskpart_result['stdout'],
                    'format_output': format_result['stdout']
                }

        except Exception as e:
            return {
                'success': False,
                'message': f"Error during format operation: {str(e)}"
            }

    @staticmethod
    def format_all_usb_drives():
        """
        Format all connected USB drives (excluding disk 0)

        Returns:
            list: List of results for each drive formatted
        """
        # Get mapping of USB disk numbers to drive letters
        disk_map = PowerShellManager.get_usb_disk_letter_map()

        if not disk_map:
            return [{
                'success': False,
                'message': 'No USB drives found to format'
            }]

        results = []
        for disk_number, drive_letter in disk_map.items():
            result = PowerShellManager.format_usb_drive(disk_number, drive_letter)
            result['disk_number'] = disk_number
            result['drive_letter'] = drive_letter
            results.append(result)

        return results
