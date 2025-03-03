import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pygame
from PIL import Image, ImageTk  # Pour charger les icônes
import time
import threading  # Pour la mise à jour du temps en parallèle
from audio.Audio import AudioTreatment  # Vérifie que cette classe est bien définie

class WavPlayerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Lecteur de musique")
        master.geometry("500x500")
        master.resizable(False, False)

        self.path = None
        self.outputDir = os.getcwd() + "/finish/"

        # Initialisation de pygame mixer
        pygame.mixer.init()

        # Chargement des icônes
        self.icons = {
            "play": ImageTk.PhotoImage(Image.open("icons/play.png").resize((40, 40))),
            "stop": ImageTk.PhotoImage(Image.open("icons/stop.png").resize((40, 40))),
            "open": ImageTk.PhotoImage(Image.open("icons/open.png").resize((30, 30))),
            "amp": ImageTk.PhotoImage(Image.open("icons/amplifier.png").resize((40, 40))),
            "distortion": ImageTk.PhotoImage(Image.open("icons/distortion.png").resize((40, 40))),
            "noise": ImageTk.PhotoImage(Image.open("icons/noise.png").resize((40, 40))),
        }

        # Sélection du fichier
        self.open_button = tk.Button(master, image=self.icons["open"], command=self.importFile)
        self.open_button.pack(pady=10)

        # Nom du fichier
        self.file_label = tk.Label(master, text="Aucun fichier sélectionné", font=("Arial", 12))
        self.file_label.pack()

        # Barre de progression
        self.progress_var = tk.DoubleVar()
        self.progress_bar = tk.Scale(master, from_=0, to=100, orient="horizontal", variable=self.progress_var, length=400)
        self.progress_bar.pack(pady=10)

        # Durée actuelle et totale
        self.time_label = tk.Label(master, text="00:00 / 00:00", font=("Arial", 12))
        self.time_label.pack()

        # Contrôles de lecture (Play & Stop uniquement)
        controls_frame = tk.Frame(master)
        controls_frame.pack(pady=10)

        self.play_button = tk.Button(controls_frame, image=self.icons["play"], command=self.playFile)
        self.play_button.grid(row=0, column=0, padx=10)

        self.stop_button = tk.Button(controls_frame, image=self.icons["stop"], command=self.stopFile)
        self.stop_button.grid(row=0, column=1, padx=10)

        # Boutons de traitement audio
        processing_frame = tk.Frame(master)
        processing_frame.pack(pady=10)

        self.amp_button = tk.Button(processing_frame, image=self.icons["amp"], command=self.amplifier)
        self.amp_button.grid(row=0, column=0, padx=5)

        self.distortion_button = tk.Button(processing_frame, image=self.icons["distortion"], command=self.antidistortion)
        self.distortion_button.grid(row=0, column=1, padx=5)

        self.noise_button = tk.Button(processing_frame, image=self.icons["noise"], command=self.antibruit)
        self.noise_button.grid(row=0, column=2, padx=5)

        # Gestion du temps
        self.music_length = 0
        self.update_thread = None

    def importFile(self):
        filetypes = [("Fichiers audio", "*.wav;*.mp3")]
        path = filedialog.askopenfilename(title="Importer un fichier audio", filetypes=filetypes)
        if path:
            self.path = path
            self.file_label.config(text=os.path.basename(self.path))
            try:
                pygame.mixer.music.load(self.path)
                self.music_length = pygame.mixer.Sound(self.path).get_length()
                self.update_duration()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de lire le fichier audio: {e}")

    def playFile(self):
        if not self.path:
            messagebox.showwarning("Attention", "Aucun fichier importé.")
            return
        pygame.mixer.music.play()
        self.update_thread = threading.Thread(target=self.update_progress, daemon=True)
        self.update_thread.start()

    def stopFile(self):
        pygame.mixer.music.stop()
        self.progress_var.set(0)

    def update_progress(self):
        """Met à jour la barre de progression et la durée actuelle"""
        while pygame.mixer.music.get_busy():
            time.sleep(1)
            current_time = pygame.mixer.music.get_pos() // 1000  # en secondes
            self.progress_var.set((current_time / self.music_length) * 100)
            self.update_duration(current_time)
        self.progress_var.set(0)

    def update_duration(self, current_time=0):
        """Affiche la durée actuelle et la durée totale"""
        total_time = self.format_time(self.music_length)
        current_time = self.format_time(current_time)
        self.time_label.config(text=f"{current_time} / {total_time}")

    def format_time(self, seconds):
        """Convertit des secondes en mm:ss"""
        minutes = int(seconds) // 60
        seconds = int(seconds) % 60
        return f"{minutes:02}:{seconds:02}"

    def amplifier(self):
        if not self.path:
            messagebox.showwarning("Attention", "Aucun fichier importé.")
            return
        factor = simpledialog.askfloat("Amplifier", "Entrez le facteur d'amplification:", minvalue=0.0)
        if factor is None:
            return
        output_file = os.path.join(self.outputDir, "amplified.wav")
        AudioTreatment.amplifier(self.path, output_file, factor)
        messagebox.showinfo("Traitement", f"Fichier amplifié enregistré sous : {output_file}")

    def antidistortion(self):
        if not self.path:
            messagebox.showwarning("Attention", "Aucun fichier importé.")
            return
        output_file = os.path.join(self.outputDir, "antidistorted.wav")
        AudioTreatment.antidistortion(self.path, output_file)
        messagebox.showinfo("Traitement", f"Fichier antidistorsion enregistré sous : {output_file}")

    def antibruit(self):
        if not self.path:
            messagebox.showwarning("Attention", "Aucun fichier importé.")
            return
        threshold = simpledialog.askinteger("Antibruit", "Entrez la valeur du seuil:", minvalue=0)
        if threshold is None:
            return
        output_file = os.path.join(self.outputDir, "antibruit.wav")
        AudioTreatment.antibruit(self.path, output_file, threshold)
        messagebox.showinfo("Traitement", f"Fichier antibruit enregistré sous : {output_file}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WavPlayerGUI(root)
    root.mainloop()
