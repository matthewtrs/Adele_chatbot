import webbrowser
import speech_recognition as sr
from urllib.parse import urlparse
import os
from playsound import playsound
from threading import Thread
import tkinter as tk
from tkinter import scrolledtext, messagebox

# Constants for file paths
TRIGGER_FILE = "trigger.txt"
URL_FILE = "website.txt"
SHORTCUT_FILE = "shortcutlaunch.txt"
WELCOME_SOUND = "welcome_sound.mp3"
TRIGGER_SOUND = "trigger_sound.mp3"
SUCCESS_SOUND = "success_sound.mp3"

# Function to recognize speech and return the recognized text
def recognize_speech(prompt):
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        print(prompt)
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        audio = recognizer.listen(source)

    try:
        return recognizer.recognize_google(audio).lower()
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        return None

# Function to read key-value pairs from a text file and return a dictionary
def read_dict_from_file(file_path):
    result_dict = {}
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    result_dict[key.lower()] = value
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None
    return result_dict

# Function to format the recognized text as a valid URL
def format_url(text, url_dict):
    for word in text.lower().split():
        if word in url_dict:
            return url_dict[word]
    
    parsed_url = urlparse(text)
    if not parsed_url.scheme:
        text = "http://" + text
        parsed_url = urlparse(text)

    if not parsed_url.netloc:
        text += ".com"
        parsed_url = urlparse(text)

    return parsed_url.geturl()

# Function to open a program based on the recognized command
def open_program(command, shortcut_dict):
    for word in command.lower().split():
        if word in shortcut_dict:
            program_path = shortcut_dict[word]
            try:
                os.startfile(program_path)
                return True
            except Exception as e:
                print(f"Failed to open {program_path}: {e}")
                return False
    return False

# Function to handle URL opening
def open_url(url_command, url_dict):
    url = format_url(url_command, url_dict)
    if not url:
        print("Invalid URL.")
        return

    firefox_path = "C:/Program Files/Mozilla Firefox/firefox.exe"
    webbrowser.register('firefox', None, webbrowser.BackgroundBrowser(firefox_path))
    webbrowser.get('firefox').open(url)

# Function to play sound in a separate thread
def play_sound(file_path):
    if os.path.exists(file_path):
        Thread(target=playsound, args=(file_path,)).start()
    else:
        print(f"Sound file not found: {file_path}")

# GUI Application
class ChatbotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice-Controlled Chatbot")
        self.root.geometry("600x400")

        # Load trigger words, URLs, and shortcuts
        if not all(os.path.isfile(file) for file in [TRIGGER_FILE, URL_FILE, SHORTCUT_FILE]):
            messagebox.showerror("Error", "One or more required files are missing. Please check the file paths.")
            self.root.destroy()
            return

        with open(TRIGGER_FILE) as file:
            self.trigger_words = file.read().splitlines()
        
        self.url_dict = read_dict_from_file(URL_FILE)
        self.shortcut_dict = read_dict_from_file(SHORTCUT_FILE)

        if not self.url_dict or not self.shortcut_dict:
            messagebox.showerror("Error", "Failed to read one of the required files.")
            self.root.destroy()
            return

        # GUI Elements
        self.log_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled')
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.start_button = tk.Button(root, text="Start Listening", command=self.start_listening)
        self.start_button.pack(pady=10)

        self.exit_button = tk.Button(root, text="Exit", command=self.root.destroy)
        self.exit_button.pack(pady=10)

        # Play welcome sound
        play_sound(WELCOME_SOUND)
        self.log("Welcome to the Voice-Controlled Chatbot!")

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.config(state='disabled')
        self.log_area.yview(tk.END)

    def start_listening(self):
        self.log("Listening for trigger words...")
        command = recognize_speech("Say the trigger words: ")
        if command and any(trigger in command for trigger in self.trigger_words):
            play_sound(TRIGGER_SOUND)
            self.log("Trigger detected. Listening for command...")

            while True:
                actual_command = recognize_speech("Say the command: ")
                if not actual_command:
                    self.log("Invalid command. Please try again.")
                    continue

                if "exit" in actual_command or "quit" in actual_command:
                    self.log("Exiting the chatbot. Goodbye!")
                    self.root.destroy()
                    return

                if "start" in actual_command or "launch" in actual_command:
                    if open_program(actual_command, self.shortcut_dict):
                        self.log(f"Launched program: {actual_command}")
                        break
                    else:
                        self.log("Invalid program name. Please try again.")
                else:
                    open_url(actual_command, self.url_dict)
                    play_sound(SUCCESS_SOUND)
                    self.log(f"Opened URL: {actual_command}")
                    break
        else:
            self.log("No valid trigger detected. Please try again.")

# Main function
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatbotApp(root)
    root.mainloop()
