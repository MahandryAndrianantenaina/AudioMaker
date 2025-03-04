import tkinter as tk
from tkinter import ttk, filedialog
import pygame
import time
import ttkbootstrap as tb  # Pour un style moderne
import numpy as np
import wave
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from audio.Audio import AudioTreatment  # Vérifie que cette classe est bien définie
from PIL import Image, ImageTk  # Nécessite Pillow (pip install Pillow)

# =============================================================================
# Fonction utilitaire pour charger et redimensionner les icônes
# =============================================================================
def load_icon(path, size=(32, 32)):
    img = Image.open(path)
    img = img.resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)


# =============================================================================
# Classe MusicPlayer
# =============================================================================
class MusicPlayer:
    def __init__(self):
        # Variables audio et lecture
        self.music_file = r"E:\IT University\Codes\S6\INF310-Codage\AudioMaker\PinkPanther.wav"
        self.sound = None
        self.music_length = 0
        self.sample_rate = 0
        self.n_channels = 0
        self.n_frames = 0
        self.audio_data = None
        self.output_directory = os.path.join(os.getcwd(), "finish")
        self.is_playing = False
        self.is_paused = False
        self.start_time = 0
        self.pause_start = 0
        self.pause_duration = 0
        self.window_size = 1024

        # Initialisation de pygame
        pygame.mixer.init()

        # Création de l'interface graphique
        self.root = tb.Window(themename="darkly")
        self.root.title("Music Player")
        self.root.geometry("700x500")

        # Chargement des icônes
        self.load_icons()
        # Construction de l'interface
        self.build_ui()
        # Chargement du fichier audio par défaut
        self.load_audio_file(self.music_file)

        # Démarrage des mises à jour périodiques
        self.update_progress()
        self.update_frequency_spectrum()

    # -------------------------------------------------------------------------
    # Chargement des icônes
    # -------------------------------------------------------------------------
    def load_icons(self):
        icon_size = (32, 32)
        self.play_icon = load_icon("icons/play.png", icon_size)
        self.pause_icon = load_icon("icons/pause.png", icon_size)
        self.stop_icon = load_icon("icons/stop.png", icon_size)
        self.amplifier_icon = load_icon("icons/amplifier.png", icon_size)
        self.antidistortion_icon = load_icon("icons/distortion.png", icon_size)
        self.antibruit_icon = load_icon("icons/noise.png", icon_size)
        self.open_icon = load_icon("icons/open.png", icon_size)
        self.load_icon = load_icon("icons/load.png", icon_size)

    # -------------------------------------------------------------------------
    # Construction de l'interface graphique
    # -------------------------------------------------------------------------
    def build_ui(self):
        self.frame = ttk.Frame(self.root, padding=20)
        self.frame.pack(expand=True)

        # Canevas pour le spectre de fréquence
        self.freq_canvas = tk.Canvas(self.frame, width=400, height=100, bg="black")
        self.freq_canvas.pack(pady=10)

        # Cadre de la barre de progression
        self.progress_frame = ttk.Frame(self.frame)
        self.progress_frame.pack(pady=10)

        # Cadre pour les paramètres d'amplification et de réduction du bruit
        self.param_frame = ttk.Frame(self.frame)
        self.param_frame.pack(pady=10)

        # Facteur d'amplification via Spinbox
        amplify_label = ttk.Label(self.param_frame, text="Facteur d'amplification :")
        amplify_label.grid(row=0, column=0, padx=5)
        self.amplify_entry = ttk.Spinbox(self.param_frame, from_=2, to=100.0, increment=1)
        self.amplify_entry.grid(row=0, column=1, padx=5)
        self.amplify_entry.set("2.0")  # Valeur par défaut

        # Seuil de réduction du bruit via Spinbox
        noise_label = ttk.Label(self.param_frame, text="Seuil de réduction du bruit :")
        noise_label.grid(row=1, column=0, padx=5)
        self.noise_entry = ttk.Spinbox(self.param_frame, from_=0, to=100000, increment=100)
        self.noise_entry.grid(row=1, column=1, padx=5)
        self.noise_entry.set("500")  # Valeur par défaut

        # Barre de progression et affichage du temps
        self.current_time_label = ttk.Label(self.progress_frame, text=self.format_time(0), font=("Segoe UI", 10))
        self.current_time_label.pack(side="left", padx=5)
        self.progress_scale = ttk.Scale(self.progress_frame, from_=0, to=self.music_length,
                                        orient="horizontal", length=350)
        self.progress_scale.pack(side="left", padx=5)
        self.progress_scale.bind("<ButtonRelease-1>", self.seek)
        self.total_time_label = ttk.Label(self.progress_frame, text=self.format_time(self.music_length),
                                          font=("Segoe UI", 10))
        self.total_time_label.pack(side="left", padx=5)

        # Boutons de commande et de traitement
        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.pack(pady=10)

        open_button = ttk.Button(self.button_frame, image=self.open_icon, command=self.open_file)
        open_button.grid(row=0, column=0, padx=5)
        output_button = ttk.Button(self.button_frame, image=self.load_icon, command=self.choose_output_directory)
        output_button.grid(row=0, column=1, padx=5)
        self.play_button = ttk.Button(self.button_frame, image=self.play_icon, command=self.play_pause)
        self.play_button.grid(row=0, column=2, padx=5)
        stop_button = ttk.Button(self.button_frame, image=self.stop_icon, command=self.stop)
        stop_button.grid(row=0, column=3, padx=5)
        amp_button = ttk.Button(self.button_frame, image=self.amplifier_icon, command=self.amplifier_action)
        amp_button.grid(row=0, column=4, padx=5)
        antid_button = ttk.Button(self.button_frame, image=self.antidistortion_icon, command=self.antidistortion_action)
        antid_button.grid(row=0, column=5, padx=5)
        antibr_button = ttk.Button(self.button_frame, image=self.antibruit_icon, command=self.antibruit_action)
        antibr_button.grid(row=0, column=6, padx=5)

    # -------------------------------------------------------------------------
    # Fonctions utilitaires
    # -------------------------------------------------------------------------
    def format_time(self, seconds):
        """Convertit un temps (en secondes) au format hh:mm:ss."""
        minutes, secs = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    # -------------------------------------------------------------------------
    # Gestion du fichier audio
    # -------------------------------------------------------------------------
    def load_audio_file(self, filepath):
        """Charge le fichier audio et met à jour les paramètres."""
        self.music_file = filepath
        pygame.mixer.music.load(self.music_file)
        self.sound = pygame.mixer.Sound(self.music_file)
        self.music_length = self.sound.get_length()
        self.progress_scale.config(to=self.music_length)
        self.total_time_label.config(text=self.format_time(self.music_length))
        self.progress_scale.set(0)
        self.current_time_label.config(text=self.format_time(0))

        # Réouverture du fichier pour l'analyse FFT
        wf = wave.open(self.music_file, 'rb')
        self.sample_rate = wf.getframerate()
        self.n_channels = wf.getnchannels()
        self.n_frames = wf.getnframes()
        raw_data = wf.readframes(self.n_frames)
        wf.close()
        self.audio_data = np.frombuffer(raw_data, dtype=np.int16)
        if self.n_channels == 2:
            self.audio_data = self.audio_data[::2]

    def open_file(self):
        """Ouvre une boîte de dialogue pour choisir un fichier WAV."""
        filepath = filedialog.askopenfilename(filetypes=[("Fichiers WAV", "*.wav")])
        if filepath:
            self.load_audio_file(filepath)
            # Met à jour le répertoire de sortie par défaut
            self.output_directory = os.path.dirname(self.music_file)
            print("Fichier chargé :", filepath)

    def choose_output_directory(self):
        """Ouvre une boîte de dialogue pour choisir le répertoire de sortie."""
        directory = filedialog.askdirectory()
        if directory:
            self.output_directory = directory
            print("Répertoire de sortie :", self.output_directory)

    # -------------------------------------------------------------------------
    # Gestion de la lecture et de l'affichage
    # -------------------------------------------------------------------------
    def update_progress(self):
        """Met à jour la barre de progression et le label du temps."""
        if self.is_playing and not self.is_paused:
            current_time = time.time() - self.start_time - self.pause_duration
            if current_time > self.music_length:
                current_time = self.music_length
            self.progress_scale.set(current_time)
            self.current_time_label.config(text=self.format_time(current_time))
        else:
            self.current_time_label.config(text=self.format_time(self.progress_scale.get()))
        self.root.after(100, self.update_progress)

    def update_frequency_spectrum(self):
        """Calcule et affiche la FFT du segment courant dans le canevas."""
        if self.is_playing and not self.is_paused:
            current_time_sec = time.time() - self.start_time - self.pause_duration
        else:
            current_time_sec = self.progress_scale.get()

        sample_index = int(current_time_sec * self.sample_rate)
        window_data = self.audio_data[sample_index: sample_index + self.window_size]
        if len(window_data) < self.window_size:
            window_data = np.pad(window_data, (0, self.window_size - len(window_data)), mode='constant')
        windowed = window_data * np.hanning(self.window_size)
        fft_result = np.fft.rfft(windowed)
        magnitudes = np.abs(fft_result)

        n_bins = 50
        bin_size = len(magnitudes) // n_bins
        bins = [np.mean(magnitudes[i * bin_size:(i + 1) * bin_size]) for i in range(n_bins)]

        max_val = max(bins) if bins else 1
        canvas_height = self.freq_canvas.winfo_height() or 100
        self.freq_canvas.delete("all")
        canvas_width = self.freq_canvas.winfo_width() or 400
        bar_width = canvas_width / n_bins
        for i, value in enumerate(bins):
            normalized_height = (value / max_val) * canvas_height
            x0 = i * bar_width
            y0 = canvas_height - normalized_height
            x1 = (i + 1) * bar_width - 2
            y1 = canvas_height
            self.freq_canvas.create_rectangle(x0, y0, x1, y1, fill="cyan", outline="")
        self.root.after(50, self.update_frequency_spectrum)

    def play_pause(self):
        """Gère le bouton Play/Pause."""
        if not self.is_playing:
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.play()
            self.start_time = time.time()
            self.pause_duration = 0
            self.is_playing = True
            self.is_paused = False
            self.play_button.config(image=self.pause_icon)
        else:
            if not self.is_paused:
                pygame.mixer.music.pause()
                self.pause_start = time.time()
                self.is_paused = True
                self.play_button.config(image=self.play_icon)
            else:
                pygame.mixer.music.unpause()
                self.pause_duration += time.time() - self.pause_start
                self.is_paused = False
                self.play_button.config(image=self.pause_icon)

    def stop(self):
        """Arrête la lecture et réinitialise l'état."""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.play_button.config(image=self.play_icon)
        self.progress_scale.set(0)
        self.current_time_label.config(text=self.format_time(0))

    def seek(self, event):
        """Modifie la position de lecture via la barre de progression."""
        new_time = self.progress_scale.get()
        if self.is_playing:
            pygame.mixer.music.play(start=new_time)
            self.start_time = time.time() - new_time
            self.pause_duration = 0
        self.current_time_label.config(text=self.format_time(new_time))

    # -------------------------------------------------------------------------
    # Fonctions de traitement audio
    # -------------------------------------------------------------------------
    def amplifier_action(self):
        """Amplifie l'audio avec un facteur d'amplification saisi par l'utilisateur."""
        output_file = os.path.join(self.output_directory, "amplified.wav")
        try:
            factor = float(self.amplify_entry.get())
            AudioTreatment.amplifier(self.music_file, output_file, factor)
            print(f"Amplification effectuée avec un facteur de {factor}, fichier enregistré :", output_file)
        except ValueError:
            print("Erreur : Le facteur d'amplification doit être un nombre.")

    def antibruit_action(self):
        """Réduit le bruit de l'audio avec un seuil saisi par l'utilisateur."""
        output_file = os.path.join(self.output_directory, "antibruit.wav")
        try:
            threshold = int(self.noise_entry.get())
            AudioTreatment.antibruit(self.music_file, output_file, threshold)
            print(f"Réduction du bruit effectuée avec un seuil de {threshold}, fichier enregistré :", output_file)
        except ValueError:
            print("Erreur : Le seuil doit être un nombre entier.")

    def antidistortion_action(self):
        """Applique un traitement antidistortion à l'audio."""
        output_file = os.path.join(self.output_directory, "antidistorted.wav")
        AudioTreatment.antidistortion(self.music_file, output_file)
        print("Antidistortion effectuée, fichier enregistré :", output_file)

    # -------------------------------------------------------------------------
    # Lancement de l'application
    # -------------------------------------------------------------------------
    def run(self):
        self.root.mainloop()


# =============================================================================
# Point d'entrée de l'application
# =============================================================================
if __name__ == '__main__':
    player = MusicPlayer()
    player.run()
