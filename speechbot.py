import webbrowser
import speech_recognition as sr
from urllib.parse import urlparse
import os
from playsound import playsound
from threading import Thread

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
        print("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError:
        print("Unable to access the Google Speech Recognition API.")
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

# Main function
def main():
    # Load trigger words, URLs, and shortcuts
    if not all(os.path.isfile(file) for file in [TRIGGER_FILE, URL_FILE, SHORTCUT_FILE]):
        print("One or more required files are missing. Please check the file paths.")
        return

    with open(TRIGGER_FILE) as file:
        trigger_words = file.read().splitlines()
    
    url_dict = read_dict_from_file(URL_FILE)
    shortcut_dict = read_dict_from_file(SHORTCUT_FILE)

    if not url_dict or not shortcut_dict:
        print("Failed to read one of the required files.")
        return

    play_sound(WELCOME_SOUND)

    while True:
        command = recognize_speech("Say the trigger words: ")
        if command and any(trigger in command for trigger in trigger_words):
            play_sound(TRIGGER_SOUND)
            print("Trigger detected. Listening for command...")

            while True:
                actual_command = recognize_speech("Say the command: ")
                if not actual_command:
                    print("Invalid command. Please try again.")
                    continue

                if "exit" in actual_command or "quit" in actual_command:
                    print("Exiting the chatbot. Goodbye!")
                    return

                if "start" in actual_command or "launch" in actual_command:
                    if open_program(actual_command, shortcut_dict):
                        break
                    else:
                        print("Invalid program name. Please try again.")
                else:
                    open_url(actual_command, url_dict)
                    play_sound(SUCCESS_SOUND)
                    break
        else:
            print("No valid trigger detected. Please try again.")

if __name__ == "__main__":
    main()
