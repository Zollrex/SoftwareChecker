import os
import sys
import json
import time
import glob
import winreg
import win32api
import requests
import threading
import webbrowser
import subprocess
import customtkinter as ctk
from datetime import datetime
from plyer import notification
from PIL import Image, ImageTk
import tkinter as tk
import re
from math import sin, pi
import tempfile
import asyncio
import aiohttp
import shutil
from plyer import notification
import psutil
import platform
import math
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Modern Dark Theme
THEME = {
    "bg_color": "#0A0A0A",  # Sehr dunkles Schwarz
    "secondary_bg": "#141414",  # Dunkelgrau
    "accent_color": "#2196F3",  # Material Blue
    "accent_hover": "#1976D2",  # Dunkleres Blau
    "text_color": "#E0E0E0",  # Helles Grau
    "text_secondary": "#909090",  # Mittleres Grau
    "button_color": "#1E1E1E",  # Dunkel für Buttons
    "button_hover": "#2D2D2D",  # Etwas heller für Hover
    "border_color": "#2A2A2A",  # Dunkelgrau für Borders
    "success_color": "#4CAF50",  # Material Green
    "warning_color": "#FFC107",  # Material Amber
    "error_color": "#F44336",  # Material Red
    "card_bg": "#141414",  # Dunkelgrau für Karten
    "card_hover": "#1A1A1A",  # Etwas heller für Hover
}

class AnimatedLabel(ctk.CTkLabel):
    """Label mit Fade und Pulse Animationen"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pulse_scale = 1.0
        self.pulse_growing = False
        self.animation_active = False

    def start_pulse(self):
        if not self.animation_active:
            self.animation_active = True
            self._pulse_animation()

    def stop_pulse(self):
        self.animation_active = False

    def _pulse_animation(self):
        if not self.animation_active:
            return

        if self.pulse_growing:
            self.pulse_scale += 0.001
            if self.pulse_scale >= 1.02:
                self.pulse_growing = False
        else:
            self.pulse_scale -= 0.001
            if self.pulse_scale <= 0.98:
                self.pulse_growing = True

        # Sanfte Skalierung
        current_font = self.cget("font")
        base_size = current_font[1]  # Originalgrößen beibehalten
        new_size = int(base_size * self.pulse_scale)
        self.configure(font=(current_font[0], new_size, current_font[2]))
        
        self.after(50, self._pulse_animation)

class LoadingSpinner(ctk.CTkCanvas):
    """Fancy Loading Spinner"""
    def __init__(self, parent, size=30, width=4, speed=5, color=THEME['accent_color']):
        super().__init__(parent, width=size, height=size, bg=THEME['bg_color'], 
                        highlightthickness=0)
        self.size = size
        self.width = width
        self.speed = speed
        self.color = color
        self._angle = 0
        self._running = False
        
    def start(self):
        """Startet die Spinner-Animation"""
        self._running = True
        self._spin_step()
        
    def stop(self):
        """Stoppt die Spinner-Animation"""
        self._running = False
        
    def _spin_step(self):
        """Ein Schritt der Spinner-Animation"""
        if not self._running:
            return
            
        self.delete("spinner")
        
        # Zeichne den Spinner-Bogen
        padding = self.width + 2
        x0, y0 = padding, padding
        x1, y1 = self.size - padding, self.size - padding
        start = self._angle
        extent = 240  # Nur 240 Grad des Kreises zeichnen
        
        self.create_arc(x0, y0, x1, y1, start=start, extent=extent,
                       width=self.width, outline=self.color, tags="spinner")
        
        self._angle = (self._angle + self.speed) % 360
        self.after(20, self._spin_step)

class AddSoftwareDialog:
    def __init__(self, parent, callback):
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Software hinzufügen")
        self.window.geometry("400x500")
        self.window.configure(fg_color=THEME['bg_color'])
        self.callback = callback
        
        # Zentriere das Fenster
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'+{x}+{y}')
        
        # Container
        container = ctk.CTkFrame(self.window, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titel
        title = ctk.CTkLabel(
            container,
            text="Neue Software hinzufügen",
            font=("SF Pro Display", 24, "bold"),
            text_color=THEME['text_color']
        )
        title.pack(pady=(0, 20))
        
        # Formular
        form = ctk.CTkFrame(container, fg_color=THEME['card_bg'])
        form.pack(fill="x", pady=10)
        
        # Name
        name_label = ctk.CTkLabel(
            form,
            text="Software Name:",
            font=("SF Pro Display", 14),
            text_color=THEME['text_color']
        )
        name_label.pack(padx=20, pady=(20, 5), anchor="w")
        
        self.name_entry = ctk.CTkEntry(
            form,
            font=("SF Pro Display", 14),
            fg_color=THEME['button_color'],
            text_color=THEME['text_color'],
            border_color=THEME['border_color']
        )
        self.name_entry.pack(padx=20, fill="x")
        
        # Kategorie
        category_label = ctk.CTkLabel(
            form,
            text="Kategorie:",
            font=("SF Pro Display", 14),
            text_color=THEME['text_color']
        )
        category_label.pack(padx=20, pady=(20, 5), anchor="w")
        
        self.category_entry = ctk.CTkEntry(
            form,
            font=("SF Pro Display", 14),
            fg_color=THEME['button_color'],
            text_color=THEME['text_color'],
            border_color=THEME['border_color']
        )
        self.category_entry.pack(padx=20, fill="x")
        
        # Icon
        icon_label = ctk.CTkLabel(
            form,
            text="Icon (Emoji):",
            font=("SF Pro Display", 14),
            text_color=THEME['text_color']
        )
        icon_label.pack(padx=20, pady=(20, 5), anchor="w")
        
        self.icon_entry = ctk.CTkEntry(
            form,
            font=("SF Pro Display", 14),
            fg_color=THEME['button_color'],
            text_color=THEME['text_color'],
            border_color=THEME['border_color']
        )
        self.icon_entry.pack(padx=20, fill="x")
        
        # Download URL
        url_label = ctk.CTkLabel(
            form,
            text="Download URL:",
            font=("SF Pro Display", 14),
            text_color=THEME['text_color']
        )
        url_label.pack(padx=20, pady=(20, 5), anchor="w")
        
        self.url_entry = ctk.CTkEntry(
            form,
            font=("SF Pro Display", 14),
            fg_color=THEME['button_color'],
            text_color=THEME['text_color'],
            border_color=THEME['border_color']
        )
        self.url_entry.pack(padx=20, fill="x", pady=(0, 20))
        
        # Buttons
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)
        
        # Abbrechen Button
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="Abbrechen",
            font=("SF Pro Display", 14),
            fg_color=THEME['button_color'],
            text_color=THEME['text_color'],
            hover_color=THEME['button_hover'],
            command=self.window.destroy
        )
        cancel_btn.pack(side="left", padx=5)
        
        # Hinzufügen Button
        add_btn = ctk.CTkButton(
            button_frame,
            text="Hinzufügen",
            font=("SF Pro Display", 14),
            fg_color=THEME['accent_color'],
            text_color=THEME['text_color'],
            hover_color=THEME['accent_hover'],
            command=self.add_software
        )
        add_btn.pack(side="right", padx=5)
    
    def add_software(self):
        """Fügt die neue Software hinzu"""
        name = self.name_entry.get().strip()
        category = self.category_entry.get().strip()
        icon = self.icon_entry.get().strip()
        url = self.url_entry.get().strip()
        
        if name and category and icon and url:
            self.callback({
                "name": name,
                "info": {
                    "icon": icon,
                    "category": category,
                    "download_url": url
                }
            })
            self.window.destroy()

class CircularProgressBar(ctk.CTkFrame):
    def __init__(self, parent, size=120, fg_color="#2196F3", bg_color="#1E1E1E", width=8):
        super().__init__(parent, width=size, height=size, fg_color="black")
        
        self.size = size
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.width = width
        self.value = 0
        self.target_value = 0
        self.animation_speed = 0.15

        # Erstelle normales tkinter Canvas
        self.canvas = tkinter.Canvas(
            self,
            width=size,
            height=size,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack(expand=True)
        
        # Label für den Wert
        self.value_label = ctk.CTkLabel(
            self,
            text="0%",
            font=("SF Pro Display", int(size/3), "bold"),
            text_color=fg_color
        )
        self.value_label.place(relx=0.5, rely=0.5, anchor="center")
        
        self._draw()

    def _draw(self):
        """Zeichnet die Fortschrittsanzeige"""
        self.canvas.delete("all")
        
        # Berechne die Koordinaten für den Kreis
        padding = self.width + 2
        x0 = padding
        y0 = padding
        x1 = self.size - padding
        y1 = self.size - padding

        # Zeichne den Hintergrundkreis
        self.canvas.create_arc(
            x0, y0, x1, y1,
            start=0, extent=359.999,
            width=self.width,
            outline=self.bg_color,
            style="arc"
        )

        if self.value > 0:
            # Zeichne den Fortschrittsbalken
            self.canvas.create_arc(
                x0, y0, x1, y1,
                start=90,
                extent=-self.value * 3.6,
                width=self.width,
                outline=self.fg_color,
                style="arc"
            )
            
            # Aktualisiere Label
            self.value_label.configure(text=f"{int(self.value)}%")

    def set_value(self, value):
        """Setzt den Wert mit Animation"""
        self.target_value = min(max(value, 0), 100)
        self._animate()

    def _animate(self):
        """Animiert die Wertänderung"""
        if abs(self.target_value - self.value) > 0.1:
            diff = self.target_value - self.value
            self.value += diff * self.animation_speed
            self._draw()
            self.after(16, self._animate)
        else:
            self.value = self.target_value
            self._draw()

class SoftwareMonitor(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize dictionaries
        self.category_buttons = {}
        self.software_cards = {}
        
        # Fenster-Einstellungen
        self.title("Software Monitor")
        self.geometry("1400x750")  # Noch kompakteres Fenster
        self.configure(fg_color=THEME['bg_color'])
        
        # Hauptcontainer
        self.main_container = ctk.CTkFrame(self, fg_color=THEME['bg_color'])
        self.main_container.pack(fill="both", expand=True, padx=8, pady=8)
        
        # Standard-Ansicht laden
        self.show_software_monitor()

    def create_menu(self):
        """Erstellt die Menüleiste mit verschiedenen Funktionen"""
        menu_frame = ctk.CTkFrame(self, fg_color=THEME['bg_color'], height=50)
        menu_frame.pack(fill="x", padx=20, pady=10)
        menu_frame.pack_propagate(False)
        
        # Menü-Buttons
        buttons = [
            ("Software Monitor", self.show_software_monitor)
        ]
        
        for text, command in buttons:
            btn = ctk.CTkButton(
                menu_frame,
                text=text,
                command=command,
                font=("SF Pro Display", 12),
                fg_color=THEME['button_color'],
                text_color=THEME['text_color'],
                hover_color=THEME['button_hover'],
                width=120,
                height=32
            )
            btn.pack(side="left", padx=5)

    def clear_main_container(self):
        """Leert den Hauptcontainer"""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_software_monitor(self):
        """Zeigt die Software-Monitor-Ansicht"""
        self.clear_main_container()
        
        # Software-Frame erstellen
        self.software_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.software_frame.pack(fill="both", expand=True)
        
        # Header mit Buttons in einer Zeile
        header = ctk.CTkFrame(self.software_frame, fg_color="transparent", height=40)
        header.pack(fill="x", pady=(0, 8))
        header.pack_propagate(False)
        
        # Linke Seite mit Software-Button
        left_side = ctk.CTkFrame(header, fg_color="transparent")
        left_side.pack(side="left", fill="y")
        
        add_button = ctk.CTkButton(
            left_side,
            text="+ Software",
            font=("SF Pro Display", 12),
            fg_color=THEME['button_color'],
            text_color=THEME['text_color'],
            hover_color=THEME['button_hover'],
            width=100,
            height=28,
            command=self.show_add_dialog
        )
        add_button.pack(side="left")
        
        # Filter-Buttons rechts
        filter_frame = ctk.CTkFrame(header, fg_color="transparent")
        filter_frame.pack(side="right")
        
        categories = ["Alle", "Browser", "Entwicklung", "Multimedia", "Spiele", "Andere"]
        for category in categories:
            btn = ctk.CTkButton(
                filter_frame,
                text=category,
                font=("SF Pro Display", 12),
                fg_color=THEME['button_color'],
                text_color=THEME['text_color'],
                hover_color=THEME['button_hover'],
                width=85,  # Noch schmalere Buttons
                height=28
            )
            btn.pack(side="left", padx=2)
            self.category_buttons[category] = btn
            btn.configure(command=lambda c=category: self.filter_category(c))
        
        # Content Frame für Software-Karten
        self.content = ctk.CTkFrame(self.software_frame, fg_color="transparent")
        self.content.pack(fill="both", expand=True)
        
        # Footer
        self.footer = ctk.CTkFrame(self.software_frame, fg_color="transparent", height=30)
        self.footer.pack(fill="x", side="bottom", pady=(8, 0))
        self.footer.pack_propagate(False)
        
        # Footer Content
        footer_content = ctk.CTkFrame(self.footer, fg_color="transparent")
        footer_content.pack(fill="both", expand=True)
        
        # Status Label
        self.status_label = ctk.CTkLabel(
            footer_content,
            text="",
            font=("SF Pro Display", 12),
            text_color=THEME['text_color']
        )
        self.status_label.pack(side="left")
        
        # Letzte Prüfung
        self.last_check = datetime.now()
        self.last_check_label = ctk.CTkLabel(
            footer_content,
            text=f"Letzte Prüfung: {self.last_check.strftime('%H:%M:%S')}",
            font=("SF Pro Display", 12),
            text_color=THEME['text_secondary']
        )
        self.last_check_label.pack(side="right")
        
        # Update Button
        self.update_button = ctk.CTkButton(
            footer_content,
            text="Jetzt aktualisieren",
            font=("SF Pro Display", 12),
            fg_color=THEME['accent_color'],
            text_color=THEME['text_color'],
            hover_color=THEME['accent_hover'],
            width=120,
            height=28,
            command=self.start_version_check
        )
        self.update_button.pack(side="right", padx=10)
        
        # Initialisiere die Software-Liste
        self.initialize_ui()

    def initialize_ui(self):
        """Initialisiert die Software-Liste mit Erkennungsinformationen"""
        self.software_list = {
            "Chrome": {
                "icon": "🌐",
                "category": "Browser",
                "registry_path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
                "exe_path": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                "version_args": ["--version"],
                "version_pattern": r"\d+\.\d+\.\d+\.\d+",
                "api_url": "https://omahaproxy.appspot.com/all.json",
                "version_key": "current_version",
                "download_url": "https://www.google.com/chrome/"
            },
            "Firefox": {
                "icon": "🦊",
                "category": "Browser",
                "registry_path": r"SOFTWARE\Mozilla\Mozilla Firefox",
                "exe_path": r"C:\Program Files\Mozilla Firefox\firefox.exe",
                "version_args": ["-v"],
                "version_pattern": r"\d+\.\d+(\.\d+)?",
                "api_url": "https://product-details.mozilla.org/1.0/firefox_versions.json",
                "version_key": "LATEST_FIREFOX_VERSION",
                "download_url": "https://www.mozilla.org/firefox/new/"
            },
            "VS Code": {
                "icon": "📝",
                "category": "Development",
                "registry_path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{EA457B21-F73E-494C-ACAB-524FDE069978}_is1",
                "exe_path": r"C:\Users\myswo\AppData\Local\Programs\Microsoft VS Code\Code.exe",
                "version_args": ["--version"],
                "version_pattern": r"\d+\.\d+\.\d+",
                "github_repo": "microsoft/vscode",
                "download_url": "https://code.visualstudio.com/download"
            },
            "Spotify": {
                "icon": "🎵",
                "category": "Multimedia",
                "registry_path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Spotify",
                "exe_path": r"C:\Users\myswo\AppData\Roaming\Spotify\Spotify.exe",
                "version_pattern": r"\d+\.\d+\.\d+\.\d+",
                "download_url": "https://www.spotify.com/download/"
            },
            "Steam": {
                "icon": "🎮",
                "category": "Gaming",
                "registry_path": r"SOFTWARE\Valve\Steam",
                "exe_path": r"C:\Program Files (x86)\Steam\Steam.exe",
                "download_url": "https://store.steampowered.com/about/"
            },
            "Discord": {
                "icon": "💬",
                "category": "Kommunikation",
                "registry_path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Discord",
                "exe_path": r"C:\Users\myswo\AppData\Local\Discord\Update.exe",
                "version_pattern": r"\d+\.\d+\.\d+",
                "download_url": "https://discord.com/download"
            }
        }

        # Hauptcontainer
        self.software_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.software_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header
        header = ctk.CTkFrame(self.software_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        header.pack_propagate(False)

        # Header Content
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True)

        # Titel links
        title_left = ctk.CTkFrame(header_content, fg_color="transparent")
        title_left.pack(side="left", fill="y")

        title_label = ctk.CTkLabel(
            title_left,
            text="Software Monitor",
            font=("SF Pro Display", 24, "bold"),
            text_color=THEME['text_color']
        )
        title_label.pack(side="left")

        # Hinzufügen-Button
        add_button = ctk.CTkButton(
            title_left,
            text="+ Software",
            font=("SF Pro Display", 12),
            fg_color=THEME['button_color'],
            text_color=THEME['text_color'],
            hover_color=THEME['button_hover'],
            width=100,
            height=28,
            command=self.show_add_dialog
        )
        add_button.pack(side="left", padx=20)

        # Rechte Seite
        title_right = ctk.CTkFrame(header_content, fg_color="transparent")
        title_right.pack(side="right", fill="y")

        # Kategorie-Filter
        self.category_buttons = {"Alle": None}
        self.current_category = "Alle"

        # Footer
        self.footer = ctk.CTkFrame(self.software_frame, fg_color="transparent", height=50)
        self.footer.pack(fill="x", side="bottom", pady=(20, 0))
        self.footer.pack_propagate(False)

        # Footer Content
        footer_content = ctk.CTkFrame(self.footer, fg_color="transparent")
        footer_content.pack(fill="both", expand=True)

        # Status Label
        self.status_label = ctk.CTkLabel(
            footer_content,
            text="",
            font=("SF Pro Display", 12),
            text_color=THEME['text_color']
        )
        self.status_label.pack(side="left")

        # Letzte Prüfung
        self.last_check = datetime.now()
        self.last_check_label = ctk.CTkLabel(
            footer_content,
            text=f"Letzte Prüfung: {self.last_check.strftime('%H:%M:%S')}",
            font=("SF Pro Display", 12),
            text_color=THEME['text_color']
        )
        self.last_check_label.pack(side="left", padx=20)

        # Update Button
        self.update_button = ctk.CTkButton(
            footer_content,
            text="Jetzt aktualisieren",
            font=("SF Pro Display", 14),
            fg_color=THEME['accent_color'],
            text_color=THEME['text_color'],
            hover_color=THEME['accent_hover'],
            command=self.start_version_check
        )
        self.update_button.pack(side="right")

        # Refresh Button Container
        self.refresh_frame = ctk.CTkFrame(footer_content, fg_color="transparent")
        self.refresh_frame.pack(side="right", padx=10)

        # Konfiguriere das Grid für 4 Spalten
        self.software_frame.grid_columnconfigure((0,1,2,3), weight=1, uniform="column")

        # Software Grid
        self.software_frames = {}
        self.update_software_grid()
        
        # Starte initiale Versionsprüfung
        self.start_version_check()

    def start_version_check(self):
        """Startet die Versionsprüfung für alle Software"""
        # UI-Status aktualisieren
        self.update_button.configure(
            text="Prüfe Updates...",
            state="disabled",
            fg_color=THEME['button_color']
        )
        
        # Fortschrittsanzeige
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ctk.CTkProgressBar(
            self.footer,
            variable=self.progress_var,
            mode='determinate',
            height=2,
            progress_color=THEME['accent_color']
        )
        self.progress_bar.pack(fill='x', pady=(5, 0))
        self.progress_bar.set(0)
        total_software = len(self.software_list)
        
        def check_all_versions():
            try:
                for i, (name, info) in enumerate(self.software_list.items()):
                    # Fortschritt aktualisieren
                    progress = (i + 1) / total_software
                    self.after(0, lambda p=progress: self.progress_var.set(p))
                    
                    # Version prüfen
                    self.check_software_version(name)
                    
                # Prüfung abgeschlossen
                self.after(0, self.version_check_complete)
                
            except Exception as e:
                print(f"Fehler bei der Versionsprüfung: {str(e)}")
                self.after(0, self.version_check_complete)
        
        # Starte Prüfung in separatem Thread
        threading.Thread(target=check_all_versions, daemon=True).start()

    def update_software_grid(self):
        """Aktualisiert das Grid mit gefilterten Software-Karten"""
        # Lösche bestehende Karten
        for widget in self.content.winfo_children():
            widget.destroy()
        
        # Füge Software-Karten hinzu
        row = 0
        col = 0
        max_cols = 5
        
        for software_name, info in self.software_list.items():
            if self.current_category == "Alle" or info.get("category") == self.current_category:
                self.create_software_card(self.content, software_name, info, row, col)
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1

    def create_software_card(self, parent, software_name, info, row, col):
        """Erstellt eine Karte für die Software mit modernem Design"""
        # Erstelle den Kartenrahmen
        card = ctk.CTkFrame(parent, fg_color=THEME['card_bg'])
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        
        # Konfiguriere die Kartengröße
        card.configure(width=220, height=135)  # Noch kompaktere Kartengröße
        
        # Header mit Icon und Name
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=8, pady=(8, 3))
        
        # Icon und Name in einem Frame
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True)
        
        icon_label = ctk.CTkLabel(
            title_frame,
            text=info["icon"],
            font=("Segoe UI Emoji", 16),
            text_color=THEME['text_color']
        )
        icon_label.pack(side="left")
        
        name_label = ctk.CTkLabel(
            title_frame,
            text=software_name,
            font=("SF Pro Display", 12, "bold"),
            text_color=THEME['text_color']
        )
        name_label.pack(side="left", padx=5)
        
        # Status-Dot mit modernem Design
        status_frame = ctk.CTkFrame(
            header,
            fg_color=THEME['button_color'],
            corner_radius=10,
            width=20,
            height=20
        )
        status_frame.pack(side="right")
        status_frame.pack_propagate(False)
        
        status_dot = ctk.CTkLabel(
            status_frame,
            text="●",
            font=("SF Pro Display", 14),
            text_color=THEME['success_color']
        )
        status_dot.place(relx=0.5, rely=0.5, anchor="center")
        
        # Kategorie-Label mit modernem Design
        category_frame = ctk.CTkFrame(
            card,
            fg_color=THEME['button_color'],
            corner_radius=10,
            height=22
        )
        category_frame.pack(fill="x", padx=8, pady=(0, 8))
        
        # Zentriere das Kategorie-Label
        category_label = ctk.CTkLabel(
            category_frame,
            text=info["category"],
            font=("SF Pro Display", 11),
            text_color=THEME['text_color']
        )
        category_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Version Info
        version_frame = ctk.CTkFrame(card, fg_color="transparent")
        version_frame.pack(fill="x", padx=8, pady=(0, 8))
        
        # Version Labels
        version_info = ctk.CTkFrame(version_frame, fg_color="transparent")
        version_info.pack(fill="x", expand=True)
        
        self.software_frames[software_name] = {
            "card": card,
            "status_dot": status_dot,
            "current_version": ctk.CTkLabel(
                version_info,
                text="Wird geprüft...",
                font=("SF Pro Display", 12),
                text_color=THEME['text_color']
            ),
            "latest_version": ctk.CTkLabel(
                version_info,
                text="",
                font=("SF Pro Display", 12),
                text_color=THEME['text_color']
            ),
            "update_info": ctk.CTkLabel(
                version_info,
                text="",
                font=("SF Pro Display", 12),
                text_color=THEME['text_color']
            )
        }
        
        self.software_frames[software_name]["current_version"].pack(anchor="w")
        self.software_frames[software_name]["latest_version"].pack(anchor="w")
        self.software_frames[software_name]["update_info"].pack(anchor="w")
        
        # Button Container für Zentrierung
        button_container = ctk.CTkFrame(version_frame, fg_color="transparent")
        button_container.pack(fill="x", pady=(8, 0))
        
        # Update Button mit modernem Design
        download_button = ctk.CTkButton(
            button_container,
            text="Update",
            font=("SF Pro Display", 11),
            fg_color=THEME['accent_color'],
            text_color=THEME['text_color'],
            hover_color=THEME['accent_hover'],
            height=28,
            width=100,  # Kleinere Breite
            corner_radius=14,
            border_width=1,
            border_color=THEME['border_color']
        )
        download_button.pack(pady=(4, 0))
        self.software_frames[software_name]["download_button"] = download_button

    def check_software_version(self, software_name):
        """Prüft die Version einer Software und aktualisiert die UI"""
        try:
            info = self.software_list[software_name]
            
            # Status auf "Prüfe..." setzen
            self.after(0, lambda: self.update_software_status(
                software_name, 
                "Prüfe...", 
                THEME['warning_color']
            ))
            
            # Lokale Version abrufen
            current_version = self.get_local_version(software_name)
            if not current_version:
                self.after(0, lambda: self.update_software_status(
                    software_name,
                    "Nicht installiert",
                    THEME['error_color']
                ))
                return
            
            # Aktuelle Version anzeigen
            self.after(0, lambda: self.software_frames[software_name]["current_version"].configure(
                text=f"Installierte Version: {current_version}"
            ))
            
            # Online Version abrufen
            latest_version = self.get_online_version(software_name)
            if not latest_version:
                self.after(0, lambda: self.update_software_status(
                    software_name,
                    "Fehler beim Prüfen",
                    THEME['error_color']
                ))
                return
                
            # Neueste Version anzeigen
            self.after(0, lambda: self.software_frames[software_name]["latest_version"].configure(
                text=f"Neueste Version: {latest_version}"
            ))
            
            # Versionen vergleichen
            try:
                current_parts = [int(x) for x in current_version.split('.')]
                latest_parts = [int(x) for x in latest_version.split('.')]
                
                needs_update = False
                for current, latest in zip(current_parts, latest_parts):
                    if latest > current:
                        needs_update = True
                        break
                    elif current > latest:
                        break
                
                if needs_update:
                    self.after(0, lambda: self.update_software_status(
                        software_name,
                        "Update verfügbar",
                        THEME['warning_color']
                    ))
                    self.after(0, lambda: self.show_download_button(software_name, True))
                else:
                    self.after(0, lambda: self.update_software_status(
                        software_name,
                        "Auf neuestem Stand",
                        THEME['success_color']
                    ))
                    self.after(0, lambda: self.show_download_button(software_name, False))
            except ValueError:
                # Fallback für nicht-numerische Versionen
                if current_version != latest_version:
                    self.after(0, lambda: self.update_software_status(
                        software_name,
                        "Update verfügbar",
                        THEME['warning_color']
                    ))
                    self.after(0, lambda: self.show_download_button(software_name, True))
                else:
                    self.after(0, lambda: self.update_software_status(
                        software_name,
                        "Auf neuestem Stand",
                        THEME['success_color']
                    ))
                    self.after(0, lambda: self.show_download_button(software_name, False))
                    
        except Exception as e:
            print(f"Fehler bei {software_name}: {str(e)}")
            self.after(0, lambda: self.update_software_status(
                software_name,
                "Fehler beim Prüfen",
                THEME['error_color']
            ))

    def get_local_version(self, software_name):
        """Ermittelt die lokale Version einer Software ohne dass Programme laufen müssen"""
        try:
            if software_name == "Chrome":
                try:
                    # Chrome Version aus dem Installationsverzeichnis lesen
                    chrome_paths = [
                        r"C:\Program Files\Google\Chrome\Application",
                        r"C:\Program Files (x86)\Google\Chrome\Application"
                    ]
                    for base_path in chrome_paths:
                        if os.path.exists(base_path):
                            try:
                                # Suche nach Version in Unterverzeichnissen
                                version_dirs = [d for d in os.listdir(base_path) if re.match(r'\d+\.\d+\.\d+\.\d+', d)]
                                if version_dirs:
                                    return max(version_dirs)  # Neueste Version zurückgeben
                            except Exception as e:
                                print(f"Fehler beim Lesen des Chrome-Verzeichnisses: {str(e)}")
                
                except:
                    # Alternative: Registry-Methode
                    try:
                        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon", 0, winreg.KEY_READ)
                        version = winreg.QueryValueEx(key, "version")[0]
                        winreg.CloseKey(key)
                        return version
                    except Exception as e:
                        print(f"Fehler beim Lesen der Chrome-Registry: {str(e)}")

            elif software_name == "Firefox":
                try:
                    # Firefox Version aus der Registry
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Mozilla\Mozilla Firefox", 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
                    version = winreg.QueryValue(key, "CurrentVersion")
                    winreg.CloseKey(key)
                    return version
                except Exception as e:
                    print(f"Fehler beim Lesen der Firefox-Registry: {str(e)}")

                # Alternative: Version aus Installationsverzeichnis
                try:
                    firefox_path = r"C:\Program Files\Mozilla Firefox"
                    if os.path.exists(firefox_path):
                        with open(os.path.join(firefox_path, "application.ini"), "r") as f:
                            for line in f:
                                if line.startswith("Version="):
                                    return line.split("=")[1].strip()
                except Exception as e:
                    print(f"Fehler beim Lesen der Firefox Version: {str(e)}")

            elif software_name == "VS Code":
                # VS Code Version aus der Registry
                keys = [
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{EA457B21-F73E-494C-ACAB-524FDE069978}_is1",
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\VSCode"
                ]
                for reg_path in keys:
                    try:
                        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
                        version = winreg.QueryValueEx(key, "DisplayVersion")[0]
                        winreg.CloseKey(key)
                        return version
                    except Exception as e:
                        print(f"Fehler beim Lesen der VS Code Registry {reg_path}: {str(e)}")
                        continue

                # Alternative: Version aus product.json
                try:
                    vscode_path = os.path.join(os.getenv('LOCALAPPDATA'), "Programs", "Microsoft VS Code")
                    if os.path.exists(vscode_path):
                        product_json = os.path.join(vscode_path, "resources", "app", "product.json")
                        if os.path.exists(product_json):
                            with open(product_json, "r") as f:
                                data = json.load(f)
                                return data.get("version")
                except Exception as e:
                    print(f"Fehler beim Lesen der VS Code Version: {str(e)}")

            elif software_name == "Spotify":
                # Spotify Version aus der Registry
                keys = [
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Spotify"),
                    (winreg.HKEY_CURRENT_USER, r"Software\Spotify")
                ]
                for hkey, reg_path in keys:
                    try:
                        key = winreg.OpenKey(hkey, reg_path, 0, winreg.KEY_READ)
                        version = winreg.QueryValueEx(key, "DisplayVersion")[0]
                        winreg.CloseKey(key)
                        return version
                    except Exception as e:
                        print(f"Fehler beim Lesen der Spotify Registry {reg_path}: {str(e)}")
                        continue

                # Alternative: Version aus Spotify.exe
                try:
                    spotify_path = os.path.join(os.getenv('APPDATA'), "Spotify")
                    if os.path.exists(spotify_path):
                        spotify_exe = os.path.join(spotify_path, "Spotify.exe")
                        if os.path.exists(spotify_exe):
                            info = win32api.GetFileVersionInfo(spotify_exe, "\\")
                            ms = info['FileVersionMS']
                            ls = info['FileVersionLS']
                            version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
                            return version
                except Exception as e:
                    print(f"Fehler beim Lesen der Spotify.exe Version: {str(e)}")

            elif software_name == "Steam":
                # Steam Version aus der Registry
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam", 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
                    steam_path = winreg.QueryValue(key, "InstallPath")
                    winreg.CloseKey(key)
                    if steam_path and os.path.exists(steam_path):
                        # Steam versteckt die Version, aber wir können das Installationsdatum verwenden
                        steam_exe = os.path.join(steam_path, "Steam.exe")
                        if os.path.exists(steam_exe):
                            return "Installiert"
                except Exception as e:
                    print(f"Fehler beim Lesen der Steam Registry: {str(e)}")

                # Alternative: Standard-Installationspfade prüfen
                steam_paths = [
                    r"C:\Program Files (x86)\Steam",
                    r"C:\Program Files\Steam"
                ]
                for path in steam_paths:
                    if os.path.exists(os.path.join(path, "Steam.exe")):
                        return "Installiert"

            elif software_name == "Discord":
                # Discord Version aus dem AppData Verzeichnis
                try:
                    discord_path = os.path.join(os.getenv('LOCALAPPDATA'), "Discord")
                    if os.path.exists(discord_path):
                        app_dirs = glob.glob(os.path.join(discord_path, "app-*"))
                        if app_dirs:
                            latest_dir = max(app_dirs, key=os.path.getctime)
                            return os.path.basename(latest_dir).replace("app-", "")
                except Exception as e:
                    print(f"Fehler beim Lesen des Discord Verzeichnisses: {str(e)}")

                # Alternative: Registry-Methode
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\Discord", 0, winreg.KEY_READ)
                    version = winreg.QueryValueEx(key, "DisplayVersion")[0]
                    winreg.CloseKey(key)
                    return version
                except Exception as e:
                    print(f"Fehler beim Lesen der Discord Registry: {str(e)}")

            return None
            
        except Exception as e:
            print(f"Fehler beim Ermitteln der lokalen Version von {software_name}: {str(e)}")
            return None

    def get_online_version(self, software_name):
        """Ermittelt die neueste online verfügbare Version einer Software"""
        try:
            info = self.software_list[software_name]
            
            if software_name == "Chrome":
                try:
                    response = requests.get("https://versionhistory.googleapis.com/v1/chrome/platforms/win64/channels/stable/versions", timeout=5)
                    if response.status_code == 200:
                        return response.json()["versions"][0]["version"]
                except:
                    pass
            
            elif software_name == "Firefox":
                try:
                    response = requests.get("https://product-details.mozilla.org/1.0/firefox_versions.json", timeout=5)
                    if response.status_code == 200:
                        return response.json()["LATEST_FIREFOX_VERSION"]
                except:
                    pass
            
            elif software_name == "VS Code":
                try:
                    response = requests.get("https://api.github.com/repos/microsoft/vscode/releases/latest", timeout=5)
                    if response.status_code == 200:
                        return response.json()["tag_name"].strip("v")
                except:
                    pass
            
            elif software_name == "Spotify":
                # Spotify hat keine öffentliche API für Versionen
                return self.get_local_version(software_name)
            
            elif software_name == "Steam":
                # Steam versteckt die Version
                return "Verfügbar"
            
            elif software_name == "Discord":
                try:
                    response = requests.get("https://discord.com/api/updates/distributions/app/manifests/latest?channel=stable&platform=win&arch=x86", timeout=5)
                    if response.status_code == 200:
                        return response.json()["full_name"]
                except:
                    pass

            # Fallback auf lokale Version
            return self.get_local_version(software_name)
            
        except Exception as e:
            print(f"Fehler beim Ermitteln der Online-Version von {software_name}: {str(e)}")
            return None

    def update_software(self, software_name):
        """Führt ein Update der Software durch, indem entweder der Installer direkt heruntergeladen 
        und ausgeführt wird oder – falls nicht möglich – der Download-Link im Browser geöffnet wird."""
        try:
            print(f"Starte Update für {software_name}")
            info = self.software_list[software_name]
            installer_url = info.get("download_url")
        
            # Branching je nach Software
            if software_name == "Chrome":
                installer_url = "https://dl.google.com/chrome/install/latest/chrome_installer.exe"
            elif software_name == "Firefox":
                installer_url = "https://download.mozilla.org/?product=firefox-latest&os=win64&lang=de"
            elif software_name == "VS Code" and "github_repo" in info:
                repo = info["github_repo"]
                api_url = f"https://api.github.com/repos/{repo}/releases/latest"
                r = requests.get(api_url, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    assets = data.get("assets", [])
                    installer_url = None
                    for asset in assets:
                        asset_name = asset.get("name", "").lower()
                        if "setup" in asset_name and asset_name.endswith(".exe"):
                            installer_url = asset.get("browser_download_url")
                            break
                    if not installer_url:
                        installer_url = info.get("download_url")
                else:
                    installer_url = info.get("download_url")
        
            print(f"Installer URL: {installer_url}")
        
            if installer_url:
                if installer_url.lower().endswith(".exe"):
                    self.status_label.configure(text=f"Update für {software_name} wird heruntergeladen...")
                    temp_file = os.path.join(tempfile.gettempdir(), installer_url.split("/")[-1])
                    with requests.get(installer_url, stream=True, timeout=30) as r:
                        r.raise_for_status()
                        with open(temp_file, "wb") as f:
                            shutil.copyfileobj(r.raw, f)
                    self.status_label.configure(text=f"Update für {software_name} wird installiert...")
                    print(f"Starte den Installer für {software_name} von {temp_file}")
                    subprocess.Popen([temp_file], shell=True)
                    self.show_notification("Update gestartet", f"Update für {software_name} wird installiert.")
                else:
                    print(f"Öffne den Installer-Link im Browser: {installer_url}")
                    webbrowser.open(installer_url)
                    self.show_notification("Download gestartet", f"Der Download von {software_name} wurde im Browser geöffnet.")
                    self.status_label.configure(text=f"Download für {software_name} gestartet")
            else:
                print(f"Keine gültige Installer-URL für {software_name} gefunden.")
        
        except Exception as e:
            print(f"Fehler beim Update von {software_name}: {str(e)}")
            self.status_label.configure(text=f"Fehler beim Update von {software_name}")

    def version_check_complete(self):
        """Wird aufgerufen, wenn die Versionsprüfung abgeschlossen ist"""
        # UI zurücksetzen
        self.update_button.configure(
            text="Jetzt aktualisieren",
            state="normal",
            fg_color=THEME['accent_color']
        )
        
        # Fortschrittsanzeige entfernen
        if hasattr(self, 'progress_bar'):
            self.progress_bar.destroy()
            
        # Benachrichtigung anzeigen
        self.show_notification(
            "Update-Prüfung abgeschlossen",
            "Alle Software-Versionen wurden überprüft."
        )
        
        # Zeit der letzten Prüfung aktualisieren
        self.last_check = datetime.now()
        self.update_last_check_label()

    def show_notification(self, title, message):
        """Zeigt eine Benachrichtigung"""
        notification.notify(
            title=title,
            message=message,
            app_icon=None,  # Hier könntest du ein Icon hinzufügen
            timeout=10
        )

    def update_last_check_label(self):
        """Aktualisiert das Label mit der Zeit der letzten Prüfung"""
        self.last_check_label.configure(text=f"Letzte Prüfung: {self.last_check.strftime('%H:%M:%S')}")

    def show_add_dialog(self):
        """Zeigt den Dialog zum Hinzufügen neuer Software"""
        AddSoftwareDialog(self, self.add_new_software)
    
    def add_new_software(self, data):
        """Fügt neue Software zur Liste hinzu"""
        name = data["name"]
        info = data["info"]
        
        # Füge zur Software-Liste hinzu
        self.software_list[name] = info
        
        # Aktualisiere Kategorien
        if info["category"] not in self.category_buttons:
            self.category_buttons[info["category"]] = None
            self.current_category = "Alle"
            
            # Füge neuen Kategorie-Button hinzu
            btn = ctk.CTkButton(
                self.footer,
                text=info["category"],
                font=("SF Pro Display", 12),
                fg_color="transparent",
                text_color=THEME['text_color'],
                hover_color=THEME['accent_hover'],
                command=lambda c=info["category"]: self.filter_category(c)
            )
            btn.pack(side="left", padx=5)
            self.category_buttons[info["category"]] = btn
        
        # Aktualisiere Grid
        self.update_software_grid()
        
        # Zeige Benachrichtigung
        self.show_notification(
            "Neue Software hinzugefügt!",
            f"{name} wurde zur Überwachung hinzugefügt."
        )

    def update_software_status(self, software_name, status, color):
        """Aktualisiert den Status der Software in der UI"""
        self.software_frames[software_name]["update_info"].configure(text=status)
        self.software_frames[software_name]["status_dot"].configure(text_color=color)

    def show_download_button(self, software_name, show):
        """Zeigt oder versteckt den Download-Button"""
        if show:
            self.software_frames[software_name]["download_button"].pack(pady=(5, 0))
        else:
            self.software_frames[software_name]["download_button"].pack_forget()

    def filter_category(self, category):
        """Filtert die Software-Karten nach Kategorie"""
        self.current_category = category
        
        # Aktualisiere Button-Farben
        for cat, btn in self.category_buttons.items():
            btn.configure(
                fg_color=THEME['accent_color'] if cat == category else "transparent"
            )
        
        # Aktualisiere Grid
        self.update_software_grid()

if __name__ == "__main__":
    monitor = SoftwareMonitor()
    monitor.mainloop()
