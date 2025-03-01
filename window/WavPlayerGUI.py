import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import vlc
from audio.Audio import AudioTreatment  # Assurez-vous que cette classe est bien accessible

class WavPlayerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Lecteur de fichiers WAV avec VLC")
        master.geometry("800x500")

        self.path = None
        self.outputDir = os.getcwd()

        # Barre de menu
        menubar = tk.Menu(master)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Importer", command=self.importFile)
        filemenu.add_command(label="Configurer", command=self.configure_directory)
        menubar.add_cascade(label="Fichier", menu=filemenu)
        master.config(menu=menubar)

        # Création du frame principal
        main_frame = tk.Frame(master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame gauche : lecteur VLC intégré
        self.left_frame = tk.Frame(main_frame, bg="black", width=500, height=400)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.left_frame.update()  # S'assurer que le widget est créé pour obtenir son identifiant

        # Initialisation de VLC
        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()
        self.embed_vlc()

        # Frame droite : boutons de traitement audio
        self.right_frame = tk.Frame(main_frame, bg="white", width=300)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

        self.amp_button = tk.Button(self.right_frame, text="Amplifier", bg="green", fg="white", command=self.amplifier)
        self.amp_button.pack(pady=10, fill=tk.X, padx=20)

        self.antidist_button = tk.Button(self.right_frame, text="Antidistortion", bg="red", fg="white", command=self.antidistortion)
        self.antidist_button.pack(pady=10, fill=tk.X, padx=20)

        self.antibruit_button = tk.Button(self.right_frame, text="Antibruit", bg="blue", fg="white", command=self.antibruit)
        self.antibruit_button.pack(pady=10, fill=tk.X, padx=20)

    def embed_vlc(self):
        """Intègre le lecteur VLC dans le frame gauche."""
        window_id = self.left_frame.winfo_id()
        if os.name == "nt":  # Windows
            self.media_player.set_hwnd(window_id)
        elif sys.platform == "darwin":  # macOS
            self.media_player.set_nsobject(window_id)
        else:  # Linux et autres
            self.media_player.set_xwindow(window_id)

    def importFile(self):
        filetypes = [("Fichiers WAV", "*.wav")]
        path = filedialog.askopenfilename(title="Importer un fichier WAV", filetypes=filetypes)
        if path:
            self.path = path
            media = self.vlc_instance.media_new(self.path)
            self.media_player.set_media(media)
            self.media_player.play()

    def configure_directory(self):
        directory = filedialog.askdirectory(title="Sélectionner le répertoire de sortie")
        if directory:
            self.outputDir = directory
            messagebox.showinfo("Configuration", f"Répertoire configuré: {self.outputDir}")

    def amplifier(self):
        if not self.path:
            messagebox.showwarning("Attention", "Aucun fichier importé.")
            return
        factor = simpledialog.askfloat("Amplifier", "Entrez le facteur d'amplification:", minvalue=0.0)
        if factor is None:
            return
        output_file = os.path.join(self.outputDir, "amplified.wav")
        AudioTreatment.amplifier(self.path, output_file, factor)

    def antidistortion(self):
        if not self.path:
            messagebox.showwarning("Attention", "Aucun fichier importé.")
            return
        output_file = os.path.join(self.outputDir, "antidistorted.wav")
        AudioTreatment.antidistortion(self.path, output_file)

    def antibruit(self):
        if not self.path:
            messagebox.showwarning("Attention", "Aucun fichier importé.")
            return
        threshold = simpledialog.askinteger("Antibruit", "Entrez la valeur du seuil:", minvalue=0)
        if threshold is None:
            return
        output_file = os.path.join(self.outputDir, "antibruit.wav")
        AudioTreatment.antibruit(self.path, output_file, threshold)

if __name__ == "__main__":
    root = tk.Tk()
    app = WavPlayerGUI(root)
    root.mainloop()
