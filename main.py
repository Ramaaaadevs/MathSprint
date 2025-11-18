# -*- coding: utf-8 -*-
"""
MathSprint: Game Edukasi Aritmetika
Dibuat sebagai contoh proyek sederhana menggunakan Pygame.

Struktur Proyek yang Diharapkan:
/MathSprint
    |-- main.py (File ini)
    |-- requirements.txt
    |-- README.md
    |-- scores.json (Akan dibuat otomatis)
    |-- /assets
        |-- correct.wav (File suara untuk jawaban benar)
        |-- wrong.wav (File suara untuk jawaban salah)
        |-- font.ttf (Opsional: font kustom)
"""

import pygame
import sys
import random
import time
import json
import datetime
import math

# --- PENGATURAN DAN KONSTANTA ---
# Ubah nilai-nilai ini untuk kustomisasi
LEBAR_LAYAR = 800
TINGGI_LAYAR = 600
FPS = 60
# TOTAL_SOAL_PER_SESI = 10 # Kita tidak lagi menggunakan total soal, tapi total waktu
# DEBUG_MODE = False  # Set True untuk random.seed yang konsisten

# # Jika True, random.seed akan diatur agar soal selalu sama (untuk testing)
# if DEBUG_MODE:
#     random.seed(42)

# Judul Game
JUDUL_GAME = "MathSprint"

# Definisi Warna (RGB)
WARNA_PUTIH = (255, 255, 255)
WARNA_HITAM = (0, 0, 0)
WARNA_ABU_ABU = (200, 200, 200)
WARNA_ABU_TUA = (100, 100, 100)
WARNA_BIRU_NAVY = (20, 30, 70)
WARNA_BIRU_TERANG = (70, 100, 200)
WARNA_HIJAU_BENAR = (60, 180, 90)
WARNA_MERAH_SALAH = (220, 50, 70)
WARNA_KUNING = (255, 200, 0)
WARNA_OVERLAY_PAUSE = (0, 0, 0, 180) # Transparan

# Status Game (Game States)
STATE_MENU_UTAMA = "MENU_UTAMA"
STATE_PILIH_KESULITAN = "PILIH_KESULITAN"
STATE_CARA_BERMAIN = "CARA_BERMAIN"
STATE_BERMAIN = "BERMAIN"
STATE_PAUSE = "PAUSE"
STATE_HASIL_AKHIR = "HASIL_AKHIR"

# Tingkat Kesulitan
KESULITAN_MUDAH = "MUDAH"
KESULITAN_SEDANG = "SEDANG"
KESULITAN_SULIT = "SULIT"

# Pengaturan per Kesulitan [Total Waktu Sesi (detik), Skor per Soal]
PENGATURAN_KESULITAN = {
    KESULITAN_MUDAH: [90, 10],  # Waktu 90 detik, 10 poin/soal
    KESULITAN_SEDANG: [60, 15], # Waktu 60 detik, 15 poin/soal
    KESULITAN_SULIT: [45, 20]  # Waktu 45 detik, 20 poin/soal
}

# Path File
FILE_SKOR_TERTINGGI = "scores.json"
PATH_FONT_KUSTOM = "assets/font.ttf"
PATH_SOUND_BENAR = "assets/correct.mp3"
PATH_SOUND_SALAH = "assets/wrong.mp3"
PATH_MUSIC_BGM = "assets/game.mp3" # <-- Tambahkan path untuk BGM


class MathSprintGame:
    """
    Kelas utama yang mengelola seluruh status dan logika game.
    """

    def __init__(self):
        """Inisialisasi Pygame, aset, dan variabel status game."""
        pygame.init()
        pygame.mixer.init()  # Inisialisasi mixer untuk suara

        self.lebar = LEBAR_LAYAR
        self.tinggi = TINGGI_LAYAR
        # self.layar = pygame.display.set_mode((self.lebar, self.tinggi)) # Ganti ke fullscreen
        self.layar = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.lebar, self.tinggi = self.layar.get_rect().size # Dapatkan ukuran layar penuh
        pygame.display.set_caption(JUDUL_GAME)
        self.clock = pygame.time.Clock()

        # Memuat font
        self.muat_font()

        # Memuat suara
        self.muat_suara()

        # Memuat dan memainkan musik latar (BGM)
        self.muat_musik()

        # Variabel status game
        self.status_game_sekarang = STATE_MENU_UTAMA
        self.kesulitan_terpilih = KESULITAN_MUDAH
        self.input_nama_pemain = "Player"
        self.input_nama_aktif = False

        # Variabel untuk loop permainan
        self.data_game_aktif = {}

        # Variabel untuk animasi karakter
        self.anim_state = 'idle'  # 'idle', 'jump', 'shake'
        self.anim_timer = 0.0
        # self.char_base_pos = (self.lebar // 2, self.tinggi // 2 + 50) # Pindahkan setelah self.lebar di-update
        
        # Variabel untuk data hasil akhir (disimpan saat game selesai)
        self.data_hasil_terakhir = {}

        # Update posisi karakter berdasarkan ukuran layar penuh
        self.char_base_pos = (self.lebar // 2, self.tinggi // 2 + 50)

    def muat_font(self):
        """Mencoba memuat font kustom, jika gagal, gunakan font default."""
        try:
            self.font_judul = pygame.font.Font(PATH_FONT_KUSTOM, 72)
            self.font_besar = pygame.font.Font(PATH_FONT_KUSTOM, 48)
            self.font_sedang = pygame.font.Font(PATH_FONT_KUSTOM, 30)
            self.font_kecil = pygame.font.Font(PATH_FONT_KUSTOM, 22)
            print(f"Berhasil memuat font kustom: {PATH_FONT_KUSTOM}")
        except FileNotFoundError:
            print(f"Warning: Font kustom '{PATH_FONT_KUSTOM}' tidak ditemukan. Menggunakan font default.")
            self.font_judul = pygame.font.Font(None, 80)
            self.font_besar = pygame.font.Font(None, 56)
            self.font_sedang = pygame.font.Font(None, 36)
            self.font_kecil = pygame.font.Font(None, 28)
        except pygame.error as e:
            print(f"Error memuat font: {e}. Menggunakan font default.")
            self.font_judul = pygame.font.Font(None, 80)
            self.font_besar = pygame.font.Font(None, 56)
            self.font_sedang = pygame.font.Font(None, 36)
            self.font_kecil = pygame.font.Font(None, 28)

    def muat_suara(self):
        """Mencoba memuat file suara, jika gagal, set ke None."""
        try:
            self.sound_benar = pygame.mixer.Sound(PATH_SOUND_BENAR)
            print(f"Berhasil memuat suara: {PATH_SOUND_BENAR}")
        except FileNotFoundError:
            print(f"Warning: File suara '{PATH_SOUND_BENAR}' tidak ditemukan. Mode senyap.")
            self.sound_benar = None
        except pygame.error as e:
            print(f"Error memuat suara {PATH_SOUND_BENAR}: {e}. Mode senyap.")
            self.sound_benar = None

        try:
            self.sound_salah = pygame.mixer.Sound(PATH_SOUND_SALAH)
            print(f"Berhasil memuat suara: {PATH_SOUND_SALAH}")
        except FileNotFoundError:
            print(f"Warning: File suara '{PATH_SOUND_SALAH}' tidak ditemukan. Mode senyap.")
            self.sound_salah = None
        except pygame.error as e:
            print(f"Error memuat suara {PATH_SOUND_SALAH}: {e}. Mode senyap.")
            self.sound_salah = None

    def muat_musik(self):
        """Mencoba memuat dan memainkan musik BGM secara looping."""
        try:
            pygame.mixer.music.load(PATH_MUSIC_BGM)
            pygame.mixer.music.set_volume(0.5) # Atur volume (0.0 - 1.0), 0.5 = 50%
            pygame.mixer.music.play(-1) # Mainkan secara looping (-1)
            print(f"Berhasil memuat musik: {PATH_MUSIC_BGM}")
        except FileNotFoundError:
            print(f"Warning: File musik '{PATH_MUSIC_BGM}' tidak ditemukan. Mode senyap (tanpa musik).")
        except pygame.error as e:
            print(f"Error memuat musik {PATH_MUSIC_BGM}: {e}. Mode senyap.")

    def main_loop(self):
        """Loop utama game yang mengelola perpindahan status game."""
        while True:
            # Menggambar layar berdasarkan status game
            if self.status_game_sekarang == STATE_MENU_UTAMA:
                self.tampil_menu_utama()
            elif self.status_game_sekarang == STATE_PILIH_KESULITAN:
                self.tampil_pilih_kesulitan()
            elif self.status_game_sekarang == STATE_CARA_BERMAIN:
                self.tampil_cara_bermain()
            elif self.status_game_sekarang == STATE_BERMAIN:
                self.loop_bermain()
            elif self.status_game_sekarang == STATE_PAUSE:
                self.tampil_pause()
            elif self.status_game_sekarang == STATE_HASIL_AKHIR:
                self.tampil_hasil_akhir()

            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)

    # --- FUNGSI TAMPILAN (LAYAR) ---

    def tampil_menu_utama(self):
        """Menampilkan layar menu utama dengan tombol-tombol."""
        self.layar.fill(WARNA_BIRU_NAVY)
        self.render_teks(JUDUL_GAME, self.font_judul, WARNA_KUNING, self.lebar // 2, 150)

        # Tombol
        tombol_mulai = self.gambar_tombol("Mulai Bermain", self.lebar // 2 - 150, 300, 300, 50)
        tombol_cara = self.gambar_tombol("Cara Bermain", self.lebar // 2 - 150, 370, 300, 50)
        tombol_keluar = self.gambar_tombol("Keluar", self.lebar // 2 - 150, 440, 300, 50)

        # Event handler untuk menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.keluar_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if tombol_mulai.collidepoint(event.pos):
                    self.status_game_sekarang = STATE_PILIH_KESULITAN
                elif tombol_cara.collidepoint(event.pos):
                    self.status_game_sekarang = STATE_CARA_BERMAIN
                elif tombol_keluar.collidepoint(event.pos):
                    self.keluar_game()

    def tampil_pilih_kesulitan(self):
        """Menampilkan layar pemilihan tingkat kesulitan."""
        self.layar.fill(WARNA_BIRU_NAVY)
        self.render_teks("Pilih Tingkat Kesulitan", self.font_besar, WARNA_PUTIH, self.lebar // 2, 150)

        # Tombol
        tombol_mudah = self.gambar_tombol("Mudah", self.lebar // 2 - 150, 250, 300, 50, WARNA_HIJAU_BENAR)
        tombol_sedang = self.gambar_tombol("Sedang", self.lebar // 2 - 150, 320, 300, 50, WARNA_KUNING)
        tombol_sulit = self.gambar_tombol("Sulit", self.lebar // 2 - 150, 390, 300, 50, WARNA_MERAH_SALAH)
        tombol_kembali = self.gambar_tombol("Kembali", self.lebar // 2 - 150, 480, 300, 50, WARNA_ABU_ABU)

        # Event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.keluar_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pilihan = None
                if tombol_mudah.collidepoint(event.pos):
                    pilihan = KESULITAN_MUDAH
                elif tombol_sedang.collidepoint(event.pos):
                    pilihan = KESULITAN_SEDANG
                elif tombol_sulit.collidepoint(event.pos):
                    pilihan = KESULITAN_SULIT
                elif tombol_kembali.collidepoint(event.pos):
                    self.status_game_sekarang = STATE_MENU_UTAMA

                if pilihan:
                    self.kesulitan_terpilih = pilihan
                    self.mulai_game_baru()
                    self.status_game_sekarang = STATE_BERMAIN

    def tampil_cara_bermain(self):
        """Menampilkan layar instruksi cara bermain."""
        self.layar.fill(WARNA_BIRU_NAVY)
        self.render_teks("Cara Bermain", self.font_besar, WARNA_PUTIH, self.lebar // 2, 100)

        instruksi = [
            "Jawab 10 soal aritmetika secepat mungkin.",
            "Ketik jawabanmu menggunakan angka di keyboard.",
            "Tekan 'Enter' untuk mengirim jawaban.",
            "Tekan 'Backspace' untuk menghapus.",
            "Setiap soal memiliki batas waktu.",
            "Jika waktu habis atau jawaban salah, skor tidak bertambah.",
            "Tekan 'P' selama bermain untuk Pause.",
        ]

        y_pos = 180
        for line in instruksi:
            self.render_teks(line, self.font_sedang, WARNA_PUTIH, self.lebar // 2, y_pos)
            y_pos += 40

        # Tombol
        tombol_kembali = self.gambar_tombol("Kembali ke Menu", self.lebar // 2 - 150, 500, 300, 50, WARNA_ABU_ABU)

        # Event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.keluar_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if tombol_kembali.collidepoint(event.pos):
                    self.status_game_sekarang = STATE_MENU_UTAMA

    def tampil_pause(self):
        """Menampilkan overlay pause di atas layar game."""
        # Gambar layar game terakhir (sudah digambar oleh loop_bermain)
        # Buat overlay transparan
        overlay = pygame.Surface((self.lebar, self.tinggi), pygame.SRCALPHA)
        overlay.fill(WARNA_OVERLAY_PAUSE)
        self.layar.blit(overlay, (0, 0))

        self.render_teks("PAUSED", self.font_judul, WARNA_KUNING, self.lebar // 2, 200)

        # Tombol
        tombol_resume = self.gambar_tombol("Lanjut (P)", self.lebar // 2 - 150, 300, 300, 50)
        tombol_menu = self.gambar_tombol("Kembali ke Menu", self.lebar // 2 - 150, 370, 300, 50)
        
        # Event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.keluar_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.resume_game() # Panggil fungsi resume
            if event.type == pygame.MOUSEBUTTONDOWN:
                if tombol_resume.collidepoint(event.pos):
                    self.resume_game()
                elif tombol_menu.collidepoint(event.pos):
                    self.status_game_sekarang = STATE_MENU_UTAMA

    def tampil_hasil_akhir(self):
        """Menampilkan layar statistik akhir dan skor tertinggi."""
        self.layar.fill(WARNA_BIRU_NAVY)
        self.render_teks("Permainan Selesai!", self.font_besar, WARNA_KUNING, self.lebar // 2, 80)

        # Statistik
        stats_y = 150
        self.render_teks(f"Total Skor: {self.data_hasil_terakhir['skor']}", self.font_sedang, WARNA_PUTIH, self.lebar // 2, stats_y)
        stats_y += 40
        self.render_teks(f"Jawaban Benar: {self.data_hasil_terakhir['benar']}", self.font_sedang, WARNA_HIJAU_BENAR, self.lebar // 2, stats_y)
        stats_y += 40
        self.render_teks(f"Jawaban Salah: {self.data_hasil_terakhir['salah']}", self.font_sedang, WARNA_MERAH_SALAH, self.lebar // 2, stats_y)
        stats_y += 40
        self.render_teks(f"Waktu Total: {self.data_hasil_terakhir['waktu_total']:.2f} detik", self.font_sedang, WARNA_PUTIH, self.lebar // 2, stats_y)
        stats_y += 60

        # Input Nama
        self.render_teks("Masukkan Nama:", self.font_sedang, WARNA_PUTIH, self.lebar // 2, stats_y)
        stats_y += 50
        
        # Kotak input nama
        input_rect = pygame.Rect(self.lebar // 2 - 150, stats_y - 10, 300, 50)
        warna_input_rect = WARNA_PUTIH if self.input_nama_aktif else WARNA_ABU_ABU
        pygame.draw.rect(self.layar, warna_input_rect, input_rect, 2, 5)
        self.render_teks(self.input_nama_pemain, self.font_sedang, WARNA_PUTIH, self.lebar // 2, stats_y + 15)

        stats_y += 60
        # Tombol Simpan & Menu
        tombol_simpan = self.gambar_tombol("Simpan Skor", self.lebar // 2 - 170, stats_y, 150, 50)
        tombol_menu = self.gambar_tombol("Menu Utama", self.lebar // 2 + 20, stats_y, 150, 50)
        
        # Event handler
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.keluar_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if tombol_simpan.collidepoint(event.pos):
                    # Simpan skor dan kembali ke menu
                    self.simpan_skor_tertinggi(self.input_nama_pemain, self.data_hasil_terakhir['skor'])
                    self.input_nama_aktif = False
                    self.status_game_sekarang = STATE_MENU_UTAMA
                elif tombol_menu.collidepoint(event.pos):
                    self.input_nama_aktif = False
                    self.status_game_sekarang = STATE_MENU_UTAMA
                elif input_rect.collidepoint(event.pos):
                    self.input_nama_aktif = True
                else:
                    self.input_nama_aktif = False
            
            if event.type == pygame.KEYDOWN and self.input_nama_aktif:
                if event.key == pygame.K_RETURN:
                    self.input_nama_aktif = False
                elif event.key == pygame.K_BACKSPACE:
                    self.input_nama_pemain = self.input_nama_pemain[:-1]
                else:
                    if len(self.input_nama_pemain) < 15: # Batas nama
                        self.input_nama_pemain += event.unicode
        
        # Tampilkan Skor Tertinggi
        # self.tampil_skor_tertinggi(300, stats_y + 80) # Tampilkan di layar hasil
        self.tampil_skor_tertinggi(self.lebar // 2, stats_y + 80) # Gunakan self.lebar
        
    def tampil_skor_tertinggi(self, x_center, y_start):
        """Helper untuk menampilkan daftar 5 skor tertinggi."""
        self.render_teks("Skor Tertinggi", self.font_sedang, WARNA_KUNING, x_center, y_start)
        skor = self.muat_skor_tertinggi()
        
        if not skor:
            self.render_teks("Belum ada skor", self.font_kecil, WARNA_PUTIH, x_center, y_start + 35)
            return

        y_pos = y_start + 35
        for i, entri in enumerate(skor):
            teks = f"{i+1}. {entri['nama']} - {entri['skor']} ({entri['tanggal']})"
            self.render_teks(teks, self.font_kecil, WARNA_PUTIH, x_center, y_pos)
            y_pos += 25

    # --- FUNGSI LOGIKA GAME ---

    def mulai_game_baru(self):
        """Reset semua variabel untuk sesi permainan baru."""
        self.data_game_aktif = {
            'skor': 0,
            'jumlah_benar': 0,
            'jumlah_salah': 0,
            'nomor_soal': 1,
            'input_jawaban': "",
            'soal_teks': "",
            'jawaban_benar': 0,
            'sedang_umpan_balik': False,
            'waktu_mulai_umpan_balik': 0,
            'info_umpan_balik': {}, # (teks, warna, durasi, jawaban_ditampilkan)
            'waktu_mulai_game': time.time(),
            # 'waktu_mulai_soal': time.time(), # Dihapus, kita pakai timer global
            'waktu_pause_dimulai': 0, # Untuk menghitung total waktu pause
            'total_waktu_pause': 0
        }
        
        # Set pengaturan berdasarkan kesulitan
        self.data_game_aktif['total_batas_waktu'] = PENGATURAN_KESULITAN[self.kesulitan_terpilih][0] # Ganti nama var
        self.data_game_aktif['skor_per_soal'] = PENGATURAN_KESULITAN[self.kesulitan_terpilih][1]

        # Buat soal pertama
        self.buat_soal_baru()
        
        # Reset animasi
        self.anim_state = 'idle'
        self.anim_timer = 0.0

    def loop_bermain(self):
        """Loop utama saat permainan sedang berlangsung."""
        
        # Cek event dulu
        self.handle_event_bermain()
        
        # Logika game
        if self.data_game_aktif['sedang_umpan_balik']:
            self.update_umpan_balik()
        else:
            # self.update_timer_soal() # Ganti ke timer sesi
            self.update_timer_sesi()
        
        # Menggambar
        self.gambar_layar_bermain()
        
    def handle_event_bermain(self):
        """Menangani input user selama permainan."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.keluar_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.status_game_sekarang = STATE_MENU_UTAMA
                elif event.key == pygame.K_p:
                    self.pause_game()
                
                # Hanya proses input jika tidak sedang umpan balik
                if not self.data_game_aktif['sedang_umpan_balik']:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        self.proses_jawaban()
                    elif event.key == pygame.K_BACKSPACE:
                        self.data_game_aktif['input_jawaban'] = self.data_game_aktif['input_jawaban'][:-1]
                    elif event.unicode.isdigit() or (event.key == pygame.K_MINUS and not self.data_game_aktif['input_jawaban']):
                        # Hanya terima angka, atau minus jika di awal
                        self.data_game_aktif['input_jawaban'] += event.unicode

    def update_timer_sesi(self):
        """Memeriksa apakah total waktu sesi permainan sudah habis."""
        # Hitung waktu berlalu dikurangi total waktu pause
        waktu_berlalu = (time.time() - self.data_game_aktif['waktu_mulai_game']) - self.data_game_aktif['total_waktu_pause']
        waktu_sisa = self.data_game_aktif['total_batas_waktu'] - waktu_berlalu
        
        if waktu_sisa <= 0:
            self.selesaikan_game() # Langsung selesaikan game
            
    def update_umpan_balik(self):
        """Memeriksa apakah durasi umpan balik (benar/salah) sudah selesai."""
        durasi = self.data_game_aktif['info_umpan_balik']['durasi']
        if time.time() - self.data_game_aktif['waktu_mulai_umpan_balik'] > durasi:
            self.data_game_aktif['sedang_umpan_balik'] = False
            self.lanjut_soal_berikutnya()

    def gambar_layar_bermain(self):
        """Menggambar semua elemen UI saat game berlangsung."""
        
        # Background default
        self.layar.fill(WARNA_BIRU_NAVY)

        # Jika sedang umpan balik, gambar background flash
        if self.data_game_aktif['sedang_umpan_balik']:
            warna_flash = self.data_game_aktif['info_umpan_balik']['warna']
            self.layar.fill(warna_flash)
            
            # Tampilkan teks umpan balik
            teks_umpan_balik = self.data_game_aktif['info_umpan_balik']['teks']
            self.render_teks(teks_umpan_balik, self.font_besar, WARNA_PUTIH, self.lebar // 2, self.tinggi // 2 - 100)
            
            # Tampilkan jawaban jika salah
            jawaban_ditampilkan = self.data_game_aktif['info_umpan_balik'].get('jawaban_ditampilkan')
            if jawaban_ditampilkan:
                self.render_teks(f"Jawaban: {jawaban_ditampilkan}", self.font_sedang, WARNA_PUTIH, self.lebar // 2, self.tinggi // 2 - 50)
        
        else:
            # --- UI Game Normal ---
            # Timer (Gunakan timer sesi)
            waktu_berlalu = (time.time() - self.data_game_aktif['waktu_mulai_game']) - self.data_game_aktif['total_waktu_pause']
            waktu_sisa = self.data_game_aktif['total_batas_waktu'] - waktu_berlalu
            warna_timer = WARNA_PUTIH if waktu_sisa > 10 else WARNA_MERAH_SALAH # Peringatan 10 detik
            self.render_teks(f"Waktu: {int(waktu_sisa)}s", self.font_sedang, warna_timer, self.lebar - 100, 50)

            # Indikator Soal (Hanya nomor soal)
            teks_soal = f"Soal ke-{self.data_game_aktif['nomor_soal']}"
            self.render_teks(teks_soal, self.font_sedang, WARNA_PUTIH, self.lebar // 2, 50)
            
            # Skor
            self.render_teks(f"Skor: {self.data_game_aktif['skor']}", self.font_sedang, WARNA_PUTIH, 100, 50)

            # Teks Soal
            self.render_teks(self.data_game_aktif['soal_teks'], self.font_besar, WARNA_PUTIH, self.lebar // 2, 200)

            # Kotak Input Jawaban
            input_rect = pygame.Rect(self.lebar // 2 - 150, 280, 300, 70)
            pygame.draw.rect(self.layar, WARNA_PUTIH, input_rect, 3, 5)
            
            # Teks Jawaban yang diketik
            self.render_teks(self.data_game_aktif['input_jawaban'], self.font_besar, WARNA_PUTIH, self.lebar // 2, 315)

        # Update dan gambar animasi karakter
        self.update_dan_gambar_animasi()

    def buat_soal_baru(self):
        """Membuat soal baru berdasarkan kesulitan dan menyimpannya."""
        kesulitan = self.kesulitan_terpilih
        op = '+'
        a, b = 0, 0
        jawaban = 0

        try:
            if kesulitan == KESULITAN_MUDAH:
                op = random.choice(['+', '-'])
                a = random.randint(0, 20)
                b = random.randint(0, 20)
                if op == '-' and a < b:
                    a, b = b, a  # Hindari jawaban negatif untuk Mudah
                
            elif kesulitan == KESULITAN_SEDANG:
                op = random.choice(['+', '-', '*'])
                a = random.randint(0, 50)
                b = random.randint(0, 50)
                if op == '-' and a < b:
                    a, b = b, a
                if op == '*':
                    a = random.randint(0, 12) # Perkalian sedang
                    b = random.randint(0, 12)

            elif kesulitan == KESULITAN_SULIT:
                op = random.choice(['+', '-', '*', '/'])
                if op == '+':
                    a = random.randint(10, 99)
                    b = random.randint(10, 99)
                elif op == '-':
                    a = random.randint(10, 99)
                    b = random.randint(10, 99)
                    if a < b:
                        a, b = b, a
                elif op == '*':
                    a = random.randint(2, 20)
                    b = random.randint(2, 20)
                elif op == '/':
                    # Buat pembagian yang menghasilkan bilangan bulat
                    # Tentukan hasil dulu, lalu pengali, baru dapat angka yg dibagi
                    hasil = random.randint(2, 10)
                    b = random.randint(2, 10)
                    a = hasil * b

            soal_teks = f"{a} {op} {b}"
            
            # eval() aman di sini karena kita yg mengontrol string (a, op, b)
            # Ganti / dengan // untuk pembagian integer
            jawaban = eval(soal_teks.replace('/', '//'))

            self.data_game_aktif['soal_teks'] = soal_teks
            self.data_game_aktif['jawaban_benar'] = jawaban
            
        except Exception as e:
            print(f"Error saat membuat soal: {e}. Membuat ulang...")
            self.buat_soal_baru() # Rekursif jika ada error (jarang terjadi)

    def proses_jawaban(self):
        """Memvalidasi jawaban yang di-submit oleh pemain."""
        if self.data_game_aktif['sedang_umpan_balik']:
            return # Jangan proses jika sedang umpan balik

        try:
            # Coba konversi input string ke integer
            jawaban_user = int(self.data_game_aktif['input_jawaban'])
        except ValueError:
            # Jika input kosong ("") atau non-numerik (misal "-")
            jawaban_user = None # Dianggap salah

        jawaban_benar = self.data_game_aktif['jawaban_benar']

        if jawaban_user == jawaban_benar:
            # --- Jawaban Benar ---
            self.data_game_aktif['skor'] += self.data_game_aktif['skor_per_soal']
            self.data_game_aktif['jumlah_benar'] += 1
            if self.sound_benar:
                self.sound_benar.play()
            
            # Set info umpan balik
            self.data_game_aktif['info_umpan_balik'] = {
                'teks': "Benar!",
                'warna': WARNA_HIJAU_BENAR,
                'durasi': 0.8,
                'jawaban_ditampilkan': None
            }
            self.mulai_animasi('jump')

        else:
            # --- Jawaban Salah ---
            self.data_game_aktif['jumlah_salah'] += 1
            if self.sound_salah:
                self.sound_salah.play()
                
            # Set info umpan balik
            self.data_game_aktif['info_umpan_balik'] = {
                'teks': "Salah!",
                'warna': WARNA_MERAH_SALAH,
                'durasi': 1.0,
                'jawaban_ditampilkan': jawaban_benar
            }
            self.mulai_animasi('shake')

        # Mulai timer umpan balik
        self.data_game_aktif['sedang_umpan_balik'] = True
        self.data_game_aktif['waktu_mulai_umpan_balik'] = time.time()
        
    # Fungsi ini tidak diperlukan lagi karena tidak ada timer per soal
    # def handle_waktu_habis(self): ...
    # (Kita hapus fungsi handle_waktu_habis)

    def lanjut_soal_berikutnya(self):
        """Pindah ke soal berikutnya."""
        # Tidak perlu cek TOTAL_SOAL_PER_SESI, game berlanjut sampai waktu habis
        
        # if self.data_game_aktif['nomor_soal'] < TOTAL_SOAL_PER_SESI:
        
        self.data_game_aktif['nomor_soal'] += 1
        self.data_game_aktif['input_jawaban'] = ""
        self.buat_soal_baru()
        # self.data_game_aktif['waktu_mulai_soal'] = time.time() # Hapus reset timer soal
        
        # else:
        #     # Sesi selesai (Logika ini pindah ke update_timer_sesi)
        #     self.selesaikan_game()

    def selesaikan_game(self):
        """Menyiapkan data untuk layar hasil akhir."""
        # Guard clause agar tidak dipanggil berkali-kali
        if self.status_game_sekarang != STATE_BERMAIN:
            return

        waktu_total = (time.time() - self.data_game_aktif['waktu_mulai_game']) - self.data_game_aktif['total_waktu_pause']
        
        # Simpan data statistik untuk ditampilkan di layar hasil
        self.data_hasil_terakhir = {
            'skor': self.data_game_aktif['skor'],
            'benar': self.data_game_aktif['jumlah_benar'],
            'salah': self.data_game_aktif['jumlah_salah'],
            'waktu_total': waktu_total
        }
        
        # Pindah ke layar hasil
        self.status_game_sekarang = STATE_HASIL_AKHIR
        self.input_nama_aktif = True # Otomatis aktifkan input nama
        self.input_nama_pemain = "Player" # Reset nama default

    def pause_game(self):
        """Mengaktifkan mode pause."""
        if self.status_game_sekarang == STATE_BERMAIN:
            pygame.mixer.music.pause() # Jeda musik
            self.status_game_sekarang = STATE_PAUSE
            # Catat waktu saat pause dimulai
            self.data_game_aktif['waktu_pause_dimulai'] = time.time()

    def resume_game(self):
        """Melanjutkan game dari mode pause."""
        if self.status_game_sekarang == STATE_PAUSE:
            pygame.mixer.music.unpause() # Lanjutkan musik
            # Hitung durasi pause
            durasi_pause = time.time() - self.data_game_aktif['waktu_pause_dimulai']
            # Tambahkan ke timer soal agar waktu tidak berkurang (DIHAPUS)
            # self.data_game_aktif['waktu_mulai_soal'] += durasi_pause
            # Tambahkan ke total waktu pause
            self.data_game_aktif['total_waktu_pause'] += durasi_pause
            
            self.status_game_sekarang = STATE_BERMAIN

    def keluar_game(self):
        """Keluar dari aplikasi Pygame."""
        pygame.mixer.music.stop() # Hentikan musik
        pygame.quit()
        sys.exit()

    # --- FUNGSI ANIMASI ---

    def mulai_animasi(self, tipe):
        """Memulai animasi karakter ('jump' atau 'shake')."""
        if tipe == 'jump':
            self.anim_state = 'jump'
            self.anim_timer = 0.5 # Durasi lompatan
        elif tipe == 'shake':
            self.anim_state = 'shake'
            self.anim_timer = 0.6 # Durasi geleng

    def update_dan_gambar_animasi(self):
        """Mengupdate posisi karakter berdasarkan status animasi."""
        dt = self.clock.get_time() / 1000.0 # Delta time
        pos_x, pos_y = self.char_base_pos

        if self.anim_state != 'idle':
            self.anim_timer -= dt
            if self.anim_timer <= 0:
                self.anim_state = 'idle'
                self.anim_timer = 0
            
            elif self.anim_state == 'jump':
                # Menggunakan rumus parabola sederhana
                # progress = 1 (awal) -> 0 (akhir)
                progress = self.anim_timer / 0.5 
                # y = -x^2 + 1 (parabola terbalik, 0..1)
                jump_height = (-4 * (progress**2) + 4 * progress) * 30 # Skala 30px
                pos_y -= jump_height

            elif self.anim_state == 'shake':
                # Menggunakan sinus untuk efek geleng
                shake_amount = math.sin(self.anim_timer * 50) * 15 # Frekuensi * Amplitudo
                pos_x += shake_amount

        # Gambar karakter (lingkaran kuning sederhana)
        pygame.draw.circle(self.layar, WARNA_KUNING, (int(pos_x), int(pos_y)), 25)
        # Mata
        pygame.draw.circle(self.layar, WARNA_HITAM, (int(pos_x) - 8, int(pos_y) - 5), 4)
        pygame.draw.circle(self.layar, WARNA_HITAM, (int(pos_x) + 8, int(pos_y) - 5), 4)


    # --- FUNGSI UTILITAS ---

    def render_teks(self, teks, font, warna, x, y, center=True):
        """Helper untuk me-render teks ke layar."""
        obj_teks = font.render(teks, True, warna)
        rect_teks = obj_teks.get_rect()
        if center:
            rect_teks.center = (x, y)
        else:
            rect_teks.topleft = (x, y)
        self.layar.blit(obj_teks, rect_teks)

    def gambar_tombol(self, teks, x, y, w, h, warna_default=WARNA_ABU_ABU, warna_hover=WARNA_BIRU_TERANG):
        """Menggambar tombol dan mendeteksi hover."""
        mouse_pos = pygame.mouse.get_pos()
        rect_tombol = pygame.Rect(x, y, w, h)
        
        warna = warna_default
        if rect_tombol.collidepoint(mouse_pos):
            warna = warna_hover
            
        pygame.draw.rect(self.layar, warna, rect_tombol, border_radius=10)
        self.render_teks(teks, self.font_sedang, WARNA_HITAM, x + w // 2, y + h // 2)
        
        return rect_tombol # Kembalikan rect untuk deteksi klik

    def muat_skor_tertinggi(self):
        """Memuat daftar skor tertinggi dari file JSON."""
        try:
            with open(FILE_SKOR_TERTINGGI, 'r') as f:
                skor = json.load(f)
            # Pastikan diurutkan berdasarkan skor (descending)
            skor.sort(key=lambda x: x['skor'], reverse=True)
            return skor
        except (FileNotFoundError, json.JSONDecodeError):
            # Jika file tidak ada atau rusak, kembalikan list kosong
            return []

    def simpan_skor_tertinggi(self, nama, skor):
        """Menyimpan skor baru ke file JSON."""
        if skor <= 0:
            return # Jangan simpan skor 0

        daftar_skor = self.muat_skor_tertinggi()
        tanggal_hari_ini = datetime.date.today().isoformat()
        
        entri_baru = {
            "nama": nama if nama else "Player",
            "skor": skor,
            "tanggal": tanggal_hari_ini
        }
        
        daftar_skor.append(entri_baru)
        # Urutkan lagi
        daftar_skor.sort(key=lambda x: x['skor'], reverse=True)
        # Ambil Top 5
        daftar_skor = daftar_skor[:5]
        
        try:
            with open(FILE_SKOR_TERTINGGI, 'w') as f:
                json.dump(daftar_skor, f, indent=4)
        except IOError as e:
            print(f"Error: Tidak bisa menyimpan skor ke {FILE_SKOR_TERTINGGI}: {e}")


# --- Titik Masuk Program ---

if __name__ == "__main__":
    game = MathSprintGame()
    game.main_loop()