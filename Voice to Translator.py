import speech_recognition as sr
from gtts import gTTS
from googletrans import Translator
import os
import tkinter as tk
from tkinter import messagebox, ttk
import threading

class SpeechTranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech Translator")
        self.root.geometry("600x600")
        self.root.config(bg="#E0F7FA")  # Light Cyan Background

        # Set the font style
        self.title_font = ("Helvetica", 24, "bold")
        self.label_font = ("Helvetica", 12)
        self.button_font = ("Helvetica", 12)

        # Create instances of Recognizer and Translator
        self.recognizer = sr.Recognizer()
        self.translator = Translator()

        # Header
        header = tk.Label(root, text="Speech Translator", font=self.title_font, bg="#00695C", fg="white")
        header.pack(pady=20, fill=tk.X)

        # Language selection frame
        lang_frame = tk.Frame(root, bg="#E0F7FA")
        lang_frame.pack(pady=10, fill=tk.X)

        # Language selection for speech recognition
        self.speech_language_var = tk.StringVar(value="en")  # Default to English
        speech_lang_frame = tk.Frame(lang_frame, bg="#E0F7FA")
        speech_lang_frame.pack(side='left', padx=10)

        tk.Label(speech_lang_frame, text="Speech Recognition Language:", font=self.label_font, bg="#E0F7FA").pack(anchor='w')

        speech_lang_options = [("English (en)", "en"), ("Bangla (bn)", "bn"), ("Russian (ru)", "ru")]
        for text, value in speech_lang_options:
            tk.Radiobutton(speech_lang_frame, text=text, variable=self.speech_language_var, value=value,
                           bg="#E0F7FA", font=self.label_font, selectcolor="#B2DFDB").pack(anchor='w')

        # Language selection for translation
        self.translation_language_var = tk.StringVar(value="en")  # Default to English
        translation_lang_frame = tk.Frame(lang_frame, bg="#E0F7FA")
        translation_lang_frame.pack(side='right', padx=10)

        tk.Label(translation_lang_frame, text="Translation Language:", font=self.label_font, bg="#E0F7FA").pack(anchor='w')

        translation_lang_options = [("English (en)", "en"), ("Bangla (bn)", "bn"), ("Russian (ru)", "ru")]
        for text, value in translation_lang_options:
            tk.Radiobutton(translation_lang_frame, text=text, variable=self.translation_language_var, value=value,
                           bg="#E0F7FA", font=self.label_font, selectcolor="#B2DFDB").pack(anchor='w')

        # Translate button
        self.translate_button = tk.Button(root, text="Recognize Speech", command=self.start_recognition_thread,
                                           font=self.button_font, bg="#00796B", fg="white", padx=10, pady=10, borderwidth=0)
        self.translate_button.pack(pady=20, padx=10, fill=tk.X)

        # Output text with scrollbar
        self.output_frame = tk.Frame(root)
        self.output_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.output_text = tk.Text(self.output_frame, wrap=tk.WORD, height=10, font=self.label_font, bg="#ffffff", borderwidth=2, relief="groove")
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.output_frame, command=self.output_text.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.output_text.config(yscrollcommand=self.scrollbar.set)

        # Speak button
        self.speak_button = tk.Button(root, text="Speak Translated Text", command=self.speak_text,
                                       font=self.button_font, bg="#0288D1", fg="white", padx=10, pady=10, borderwidth=0)
        self.speak_button.pack(pady=5, padx=10, fill=tk.X)

        # Additional button to read recognized text
        self.read_recognized_button = tk.Button(root, text="Read Recognized Text", command=self.speak_recognized_text,
                                                 font=self.button_font, bg="#F57C00", fg="white", padx=10, pady=10, borderwidth=0)
        self.read_recognized_button.pack(pady=5, padx=10, fill=tk.X)

        # Footer
        footer = tk.Label(root, text="© 2024 Speech Translator App", bg="#E0F7FA", fg="#888888")
        footer.pack(side='bottom', pady=10)

        # Progress bar
        self.progress_bar = ttk.Progressbar(root, length=200, mode='indeterminate', style='TProgressbar')
        self.progress_bar.pack(pady=10)

        # Style for progress bar
        style = ttk.Style()
        style.configure("TProgressbar", thickness=20, troughcolor="#B2DFDB", background="#00796B")

        # Store recognized text for reading
        self.recognized_text = ""

    def start_progress(self):
        self.progress_bar.start()
        self.root.update()  # Update the GUI

    def stop_progress(self):
        self.progress_bar.stop()
        self.root.update()  # Update the GUI

    def start_recognition_thread(self):
        # Clear previous data
        self.clear_previous_data()  # Clear any previously recognized text or output

        # Create a new thread for the speech recognition process
        recognition_thread = threading.Thread(target=self.recognize_speech)
        recognition_thread.start()  # Start the thread

    def clear_previous_data(self):
        """Clear previous recognized text and output."""
        self.recognized_text = ""
        self.output_text.delete(1.0, tk.END)  # Clear previous output

    def recognize_speech(self):
        speech_language = self.speech_language_var.get()
        mic = sr.Microphone()

        self.start_progress()  # Start the progress bar
        self.translate_button.config(text="Listening...")  # Update button text
        self.output_text.delete(1.0, tk.END)  # Clear previous output
        self.output_text.insert(tk.END, "")  # Show analyzing message
        self.root.update()  # Update the GUI

        with mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)

        self.translate_button.config(text="Analyzing...")  # Update button text to Analyzing
        self.stop_progress()  # Stop the progress bar

        try:
            if speech_language == "en":
                self.recognized_text = self.recognizer.recognize_google(audio, language='en-US')
            elif speech_language == "bn":
                self.recognized_text = self.recognizer.recognize_google(audio, language='bn-BD')
            elif speech_language == "ru":
                self.recognized_text = self.recognizer.recognize_google(audio, language='ru-RU')
            else:
                messagebox.showerror("Error", "Unsupported speech recognition language!")
                self.reset_button()  # Reset button text
                return
            
            self.output_text.insert(tk.END, f"Recognized Text: {self.recognized_text}\n")
            self.translate_text(self.recognized_text)
            self.classify_speech(self.recognized_text)  # Classify the recognized speech

        except sr.UnknownValueError:
            messagebox.showerror("Error", "Sorry, I could not understand the audio.")
            self.reset_button()  # Reset button text
        except sr.RequestError as e:
            messagebox.showerror("Error", f"Could not request results; {e}")
            self.reset_button()  # Reset button text

    def translate_text(self, text):
        translation_language = self.translation_language_var.get()  # Get the selected translation language

        self.start_progress()  # Start the progress bar

        try:
            translated = self.translator.translate(text, dest=translation_language)
            self.output_text.insert(tk.END, f"Translated Text: {translated.text}\n")
           # messagebox.showinfo("Translation", f"Translated Text: {translated.text}")
        except Exception as e:
            messagebox.showerror("Error", f"Translation failed; {e}")
        
        self.stop_progress()  # Stop the progress bar
        self.reset_button()  # Reset button text

    def classify_speech(self, text):
        categories = {
            "greeting": ["hello", "hi", "hey", "greetings"],
            "question": ["what", "who", "where", "when", "why", "how"],
            "command": ["open", "close", "start", "stop", "play"],
            "farewell": ["bye", "goodbye", "see you", "later"],
        }

        found_category = "unknown"
        for category, keywords in categories.items():
            if any(keyword in text.lower() for keyword in keywords):
                found_category = category
                break

        self.output_text.insert(tk.END, f"Category: {found_category.capitalize()}\n")  # Display the category

    def speak_text(self):
        if self.recognized_text:
            tts = gTTS(text=self.recognized_text, lang='en')  # Speak recognized text in English
            tts.save("translated.mp3")
            os.system("start translated.mp3")  # Play the audio file

    def speak_recognized_text(self):
        if self.recognized_text:
            tts = gTTS(text=self.recognized_text, lang='en')  # Speak recognized text in English
            tts.save("recognized.mp3")
            os.system("start recognized.mp3")  # Play the audio file

    def reset_button(self):
        self.translate_button.config(text="Recognize Speech")  # Reset button text


root = tk.Tk()
app = SpeechTranslatorApp(root)
root.mainloop()
