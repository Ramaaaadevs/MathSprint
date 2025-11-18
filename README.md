# MathSprint — Game Edukasi Aritmetika

MathSprint adalah game edukasi sederhana dibuat dengan Python dan Pygame untuk melatih kecepatan berhitung operasi aritmetika dasar (tambah, kurang, kali, bagi) dalam mode Time Attack.

## Fitur
- Tiga tingkat kesulitan: Mudah, Sedang, Sulit (berbeda jenis soal dan durasi).
- Sesi permainan berbasis waktu (Time Attack).
- Umpan balik visual (warna), audio (suara), dan animasi karakter untuk jawaban benar/salah.
- Timer countdown sesi.
- Sistem skor berdasarkan kesulitan.
- Tombol Pause (`P`).
- Penyimpanan 5 skor tertinggi secara lokal (`scores.json`).
- Antarmuka dan komentar kode dalam Bahasa Indonesia.

## Persyaratan
- Python 3.8+  
- Pygame (tercantum di `requirements.txt`)

## Struktur proyek
Pastikan struktur folder seperti berikut agar program berjalan benar:
```
/NamaFolderProyek
├── main.py
├── requirements.txt
├── README.md
├── scores.json        # akan dibuat otomatis jika belum ada
└── assets/
    ├── correct.wav    # WAJIB (suara benar)
    ├── wrong.wav      # WAJIB (suara salah)
    └── font.ttf       # OPSIONAL (font kustom)
```

## Instalasi
1. Clone atau salin seluruh file ke satu folder.
2. (Opsional tapi disarankan) Buat dan aktifkan virtual environment:
   - Linux/Mac:
     ```
     python -m venv venv
     source venv/bin/activate
     ```
   - Windows:
     ```
     python -m venv venv
     venv\Scripts\activate
     ```
3. Instal dependensi:
```
pip install -r requirements.txt
```
4. Buat folder `assets` dan masukkan file audio `correct.wav` dan `wrong.wav`. Jika tidak tersedia, game tetap bisa berjalan tanpa suara.

## Menjalankan game
Jalankan:
```
python main.py
```
Catatan: Secara default game berjalan di mode fullscreen. Ubah pengaturan di `__init__` atau pada bagian konfigurasi di `main.py` jika ingin resolusi tetap.

## Pengaturan Dasar
Anda dapat mengubah pengaturan kesulitan langsung di bagian atas `main.py`. Contoh format:
```python
PENGATURAN_KESULITAN = {
    KESULITAN_MUDAH: [90, 10],
    KESULITAN_SEDANG: [60, 15],
    KESULITAN_SULIT: [45, 20]
}
```

## Penyimpanan Skor
- Skor tertinggi disimpan di `scores.json` (5 entri tertinggi).
- File tersebut akan dibuat otomatis saat pertama kali game menyimpan skor.

## Catatan
- Pastikan file audio berformat WAV dan memiliki nama sesuai (`correct.wav`, `wrong.wav`).
- Jika menggunakan font kustom, letakkan `font.ttf` di folder `assets` dan atur dalam `main.py`.

Jika memerlukan bantuan pengaturan atau perbaikan kode, sertakan isi `main.py` atau pesan kesalahan yang muncul.
