# 🎬 DMS (Dormhi Media Server)

**Language Selection / Dil Seçimi:**
- [English Documentation](#english-documentation)
- [Türkçe Dokümantasyon](#türkçe-dokümantasyon)

---

<a name="english-documentation"></a>
# 🇺🇸 English Documentation

Welcome to **Dormhi Media Server (DMS)**! DMS is a powerful, self-hosted media automation platform designed for long-term use. It acts as a centralized brain for your media processing needs, so you never have to download videos directly to your own devices again.

## 🚀 Key Features

* **Smart Downloading**: Uses `yt-dlp` to download media from Kick, YouTube, Twitter, Facebook, TikTok, Twitch, and more.
* **Intelligent Auto-Repair**: Uses `ffprobe` and `ffmpeg` to automatically normalize video (h264) and audio (aac) codecs. It follows a "least destructive" principle—only transcoding what is necessary, preserving quality.
* **Telegram Bot Integration**: Send a URL or upload a video directly via Telegram. The bot will automatically handle the rest and send the optimized video back to you via chat.
* **Premium Web Dashboard**: A modern, responsive React/Tailwind dashboard to monitor active jobs, queue, and browse your media library in real-time.
* **Asynchronous Queue**: Powered by Celery and Redis, multiple downloads and intensive processing jobs are handled smoothly in the background.

## 🏗 Architecture & Tech Stack

* **Backend**: Python 3.11, FastAPI, SQLAlchemy
* **Database**: SQLite (Designed modularly for easy future migration to PostgreSQL if needed)
* **Message Broker & Worker**: Redis + Celery
* **Media Engines**: `yt-dlp`, FFmpeg
* **Frontend**: React, TypeScript, TailwindCSS, Vite
* **Infrastructure**: 100% Dockerized via `docker-compose`

## 🔌 Plugin System
DMS is highly modular. Adding a new downloader is as simple as creating a short file inside `backend/app/plugins/downloaders/`. The factory automatically detects supported URLs using regular expressions and routes the job to the correct plugin.

## ⚙️ Installation & Usage

### 1. Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose installed on your system.
- A Telegram Bot Token. (You can get one from [@BotFather](https://t.me/BotFather) on Telegram).

### 2. Setup
1. Clone this repository to your server/local machine:
   ```bash
   git clone https://github.com/dormhi/DMS.git
   cd DMS
   ```
2. Copy the example environment file and fill in your details:
   ```bash
   cp .env.example .env
   nano .env
   ```
   Add your `TELEGRAM_BOT_TOKEN`, choose an `ADMIN_USER` and `ADMIN_PASS` for the Web UI, and set a random `JWT_SECRET_KEY`.
3. Start the system:
   ```bash
   docker-compose up -d --build
   ```

### 3. Usage
* **Telegram Bot**: Send `/start` to your bot.
  - Type `/download <url>` to download a video.
  - Simply forward or upload any video file to the bot to trigger the `Repair / Optimize` pipeline.
  - The bot will reply with the MP4 file once the job completes.
* **Web UI**: Visit `http://localhost:5173` (or port 3000 depending on configuration) to view the real-time queue and media library.

---

<a name="türkçe-dokümantasyon"></a>
# 🇹🇷 Türkçe Dokümantasyon

**Dormhi Media Server (DMS)** projesine hoş geldiniz! DMS, uzun vadeli ve sürekli kullanım için tasarlanmış, self-hosted bir medya otomasyon platformudur. Artık kişisel cihazlarınıza doğrudan video indirmenize gerek kalmayacak; her işlemi merkeze devredeceksiniz!

## 🚀 Temel Özellikler

* **Akıllı İndirme**: Kick, YouTube, Twitter, Facebook, TikTok ve Twitch gibi platformlardan medya indirmek için güçlü `yt-dlp` altyapısını kullanır.
* **Akıllı Otomatik Onarım**: Video dosyalarınızı `ffprobe` ile inceler. Uyumluluk sorunları varsa `ffmpeg` ile donanım dostu standart formata (h264/aac) sokar. Bu işlemi "minimum tahribat" prensibiyle yapar, sadece bozuk olan kısmı dönüştürüp görüntü kalitesini korur.
* **Telegram Bot Entegrasyonu**: Bota sadece bir link gönderin veya galerinizden bozuk bir video yükleyin. Bot her şeyi halledip optimize edilmiş videoyu sohbetten size geri gönderecektir.
* **Premium Web Dashboard**: Kuyruğu, aktif işleri ve kütüphaneyi anlık olarak takip edebilmeniz için modern, duyarlı (responsive) React & TailwindCSS paneli.
* **Asenkron İş Kuyruğu**: Celery ve Redis sayesinde ağ ve işlemci yoran görevler arka planda takılma olmadan yürütülür.

## 🏗 Mimari ve Teknoloji Yığını

* **Backend**: Python 3.11, FastAPI, SQLAlchemy
* **Veritabanı**: SQLite (Tek dosya taşıma kolaylığı, modüler yapısı sayesinde ileride PostgreSQL'e uyumlu)
* **Mesaj Kuyruğu & Worker**: Redis + Celery
* **Medya Motorları**: `yt-dlp`, FFmpeg
* **Frontend**: React, TypeScript, TailwindCSS, Vite
* **Altyapı**: Tamamen Dockerize edilmiştir (`docker-compose`).

## 🔌 Eklenti (Plugin) Sistemi
Sistem son derece modülerdir (Clean Code). Yeni bir platform indirme desteği eklemek isterseniz, tek yapmanız gereken `backend/app/plugins/downloaders/` klasörüne kısa bir Python dosyası açmaktır. Sistem, Regex (düzenli ifade) aracılığıyla linki analiz eder ve doğru eklentiyi kendi bulur.

## ⚙️ Kurulum ve Kullanım

### 1. Ön Gereksinimler
- Sunucunuzda veya bilgisayarınızda [Docker](https://docs.docker.com/get-docker/) ve Docker Compose kurulu olmalıdır.
- Bir Telegram Bot Token'ına ihtiyacınız var. (Telegram'da [@BotFather](https://t.me/BotFather) üzerinden edinebilirsiniz).

### 2. Kurulum
1. Repoyu sunucunuza klonlayın:
   ```bash
   git clone https://github.com/dormhi/DMS.git
   cd DMS
   ```
2. Örnek çevre değişkenleri (environment) şablonunu kopyalayıp kendi bilgilerinizi girin:
   ```bash
   cp .env.example .env
   nano .env
   ```
   İçine `TELEGRAM_BOT_TOKEN` bilginizi, siteye girmek için istediğiniz `ADMIN_USER` ile `ADMIN_PASS` şifrenizi ve rastgele bir `JWT_SECRET_KEY` girip kaydedin.
3. Sistemi ayağa kaldırın:
   ```bash
   docker-compose up -d --build
   ```

### 3. Kullanım
* **Telegram Bot**: Botunuza gidip `/start` komutunu verin.
  - Video indirmek için `/download <link>` yazın.
  - Arızalı veya optimize edilmesi gereken bir videoyu doğrudan sohbetten bota gönderin.
  - İşlem (indirme ve onarım) bittiğinde bot videoyu size sohbetten geri atacaktır.
* **Web UI (Arayüz)**: Canlı durum takibi ve arşivlenmiş medyalara erişmek için tarayıcınızdan `http://localhost:5173` adresine gidebilirsiniz.
