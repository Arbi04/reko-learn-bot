# Bot Rekomendasi Konten Belajar untuk Mahasiswa

Bot Telegram yang dirancang untuk memberikan rekomendasi konten belajar yang dipersonalisasi berdasarkan preferensi dan kebutuhan mahasiswa.

## Deskripsi

Bot ini menggunakan sistem multi-agent untuk membantu mahasiswa menemukan bahan belajar yang relevan dengan bidang studi mereka. Bot dapat merekomendasikan video dari YouTube dan artikel dari web berdasarkan preferensi pengguna seperti bidang studi, topik, dan waktu belajar yang tersedia.

## Fitur

- Pengaturan profil belajar (bidang studi, topik, dan waktu belajar)
- Rekomendasi konten belajar yang dipersonalisasi
- Rekomendasi video dari YouTube
- Rekomendasi artikel dari berbagai sumber web
- Analisis preferensi menggunakan AI generatif (Google Gemini)

## Teknologi yang Digunakan

- Python
- python-telegram-bot
- Google Generative AI (Gemini)
- YouTube API
- SERP API
- Dotenv untuk manajemen variabel lingkungan

## Cara Instalasi

1. Clone repositori ini
2. Instal dependensi yang diperlukan: pip install -r requirements.txt
3. Salin file `.env.example` menjadi `.env` dan isi dengan kredensial API yang diperlukan:
4. Jalankan bot: python main.py

## Struktur Proyek

- `main.py` - Titik masuk utama aplikasi yang menjalankan bot Telegram
- `agents/` - Direktori berisi modul agent yang berbeda
  - `coordinator.py` - Mengkoordinasikan interaksi antar agent
  - `preference_agent.py` - Mengelola preferensi pengguna
  - `content_agent.py` - Mencari konten belajar dari berbagai sumber
  - `recommendation_agent.py` - Memfilter dan memberi peringkat konten berdasarkan preferensi
- `data/` - Direktori untuk menyimpan data pengguna

## Cara Menggunakan Bot

1. Mulai bot dengan mengirim perintah `/start`
2. Atur preferensi belajar dengan perintah `/profile`
3. Isi detail preferensi dengan format `/setprofile jurusan;topik;jam_belajar`
Contoh: `/setprofile Teknik Informatika;Machine Learning;2`
4. Minta rekomendasi konten belajar dengan perintah `/recommend`
5. Bot akan menampilkan rekomendasi yang disesuaikan dengan preferensi Anda

## Perintah Bot

- `/start` - Memulai bot
- `/profile` - Mengatur preferensi belajar
- `/setprofile` - Menyimpan preferensi (format: jurusan;topik;jam_belajar)
- `/recommend` - Mendapatkan rekomendasi konten belajar