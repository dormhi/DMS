# 🎬 DMS (Dormhi Media Server)

**Language Selection / Dil Seçimi:**
- [English Documentation](#english-documentation)
- [Türkçe Dokümantasyon](#türkçe-dokümantasyon)

---

<a name="english-documentation"></a>
# 🇺🇸 English Documentation

Welcome to **Dormhi Media Server (DMS)**! DMS is a powerful, self-hosted media automation platform designed for long-term use. It acts as a centralized brain for your media processing needs, so you never have to download videos directly to your own devices again.

## 🚀 Key Features

* **Smart Downloading**: Uses `yt-dlp` to download media from Kick, YouTube, Twitter, Facebook, TikTok, Twitch, and more. Optimized for long VODs (5+ hours) with HLS fragment handling and automatic retry.
* **Intelligent Auto-Repair**: Uses `ffprobe` and `ffmpeg` to automatically normalize video (h264) and audio (aac) codecs. It follows a "least destructive" principle — only transcoding what is necessary, preserving quality.
* **Telegram Bot (Private Mode)**: Fully private — only authorized user IDs can interact with the bot. Send `/download <url>` or upload a video directly. The bot handles downloading, repairing, and sends the optimized video back via chat.
* **Rate Limiting**: Built-in protection against command spam (3 commands per 60 seconds per user).
* **Premium Web Dashboard**: A modern, responsive React/Tailwind dashboard to submit URLs, monitor active jobs in real-time, and browse your media library with play, download, and delete controls.
* **Asynchronous Queue**: Powered by Celery and Redis, multiple downloads and intensive processing jobs are handled smoothly in the background.

## 🏗 Architecture & Tech Stack

* **Backend**: Python 3.11, FastAPI, SQLAlchemy
* **Database**: SQLite with WAL mode (Designed modularly for easy future migration to PostgreSQL if needed)
* **Message Broker & Worker**: Redis + Celery
* **Media Engines**: `yt-dlp` (latest), FFmpeg
* **Frontend**: React 19, TypeScript, TailwindCSS, Vite
* **Infrastructure**: 100% Dockerized via `docker-compose` (5 containers)

## 🔌 Plugin System
DMS is highly modular. Adding a new downloader is as simple as creating a short file inside `backend/app/plugins/downloaders/`. The factory automatically detects supported URLs using regular expressions and routes the job to the correct plugin.

## ⚙️ Installation & Usage

### 1. Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose installed on your system.
- A Telegram Bot Token. (Get one from [@BotFather](https://t.me/BotFather) on Telegram).
- Your Telegram User ID for private mode (see Step 4).

### 2. Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/dormhi/DMS.git
   cd DMS
   ```

2. Create the environment file:
   ```bash
   cp .env.example .env
   nano .env
   ```
   Fill in your `TELEGRAM_BOT_TOKEN`. Leave `TELEGRAM_ALLOWED_USER_IDS` empty for now — you will add it after finding your ID.

3. Start the system:
   ```bash
   docker-compose up -d --build
   ```

4. **Find your Telegram User ID** — The bot runs in **private mode** by default. It will not respond to anyone until you authorize your user ID:
   ```bash
   # Send any message to your bot on Telegram (it will not respond)
   # Then check the logs:
   docker-compose logs bot | grep "Unauthorized"
   ```
   The output will show: `Unauthorized user 123456789 tried to use the bot`
   Copy the number (`123456789` in this example) and add it to your `.env`:
   ```bash
   echo "TELEGRAM_ALLOWED_USER_IDS=123456789" >> .env
   docker-compose restart bot
   ```
   Your bot will now respond to you. To add more users later, separate IDs with commas: `123456789,987654321`.

### 3. Usage

* **Telegram Bot**: Send `/start` to your bot.
  - `/download <url>` — Download a video from any supported platform.
  - `/jobs` — Check the status of your active jobs.
  - `/help` — Display all available commands.
  - **Upload a video file** — Send any video file directly to the bot for repair/optimization.
  - The bot will send the processed MP4 back once the job completes (files over 50MB get a notification instead).

* **Web UI**: Visit `http://localhost:5173`
  - **Dashboard** — Submit download URLs and monitor job status in real-time.
  - **Library** — Browse completed videos with **Play** (stream in browser), **Download**, and **Delete** buttons.
  - **Login**: Default credentials are `admin` / `admin` (personal use — change in `backend/main.py` if needed).

* **Supported Platforms**: Kick (including long VODs), YouTube, Twitter/X, Facebook, TikTok, Twitch, and any site supported by yt-dlp.

---

<a name="türkçe-dokümantasyon"></a>
# 🇹🇷 Türkçe Dokümantasyon

**Dormhi Media Server (DMS)** projesine hoş geldiniz! DMS, uzun vadeli ve sürekli kullanım için tasarlanmış, self-hosted bir medya otomasyon platformudur. Artık kişisel cihazlarınıza doğrudan video indirmenize gerek kalmayacak; her işlemi merkeze devredeceksiniz!

## 🚀 Temel Özellikler

* **Akıllı İndirme**: Kick, YouTube, Twitter, Facebook, TikTok ve Twitch gibi platformlardan medya indirmek için güçlü `yt-dlp` altyapısını kullanır. Uzun VOD'lar (5+ saat) için optimize edilmiş HLS fragment yönetimi ve otomatik yeniden deneme.
* **Akıllı Otomatik Onarım**: Video dosyalarınızı `ffprobe` ile inceler. Uyumluluk sorunları varsa `ffmpeg` ile donanım dostu standart formata (h264/aac) sokar. "Minimum tahribat" prensibiyle sadece bozuk olan kısmı dönüştürür, kaliteyi korur.
* **Telegram Bot (Özel Mod)**: Sadece yetkilendirilmiş kullanıcı ID'leri bota erişebilir. `/download <link>` ile video indirin veya doğrudan bir video dosyası gönderin. Bot her şeyi halledip optimize edilmiş videoyu size geri gönderir.
* **Rate Limiting (Hız Sınırı)**: Komut spam'ına karşı yerleşik koruma (kullanıcı başına 60 saniyede 3 komut).
* **Premium Web Dashboard**: URL gönderme, işleri canlı takip etme ve kütüphanede **oynatma**, **indirme**, **silme** özellikli modern React/Tailwind paneli.
* **Asenkron İş Kuyruğu**: Celery ve Redis sayesinde çoklu indirme ve işlemci yoran görevler arka planda takılmadan yürütülür.

## 🏗 Mimari ve Teknoloji Yığını

* **Backend**: Python 3.11, FastAPI, SQLAlchemy
* **Veritabanı**: SQLite WAL modu (Modüler yapısı sayesinde ileride PostgreSQL'e uyumlu)
* **Mesaj Kuyruğu & Worker**: Redis + Celery
* **Medya Motorları**: `yt-dlp` (güncel sürüm), FFmpeg
* **Frontend**: React 19, TypeScript, TailwindCSS, Vite
* **Altyapı**: Tamamen Dockerize (5 container)

## 🔌 Eklenti (Plugin) Sistemi
Sistem son derece modülerdir. Yeni bir platform indirme desteği eklemek için `backend/app/plugins/downloaders/` klasörüne kısa bir Python dosyası eklemeniz yeterli. Sistem Regex aracılığıyla linki analiz eder ve doğru eklentiyi otomatik bulur.

## ⚙️ Kurulum ve Kullanım

### 1. Ön Gereksinimler
- Sunucunuzda veya bilgisayarınızda [Docker](https://docs.docker.com/get-docker/) ve Docker Compose kurulu olmalıdır.
- Bir Telegram Bot Token'ı. (Telegram'da [@BotFather](https://t.me/BotFather) üzerinden edinebilirsiniz).
- Özel mod için Telegram Kullanıcı ID'niz (Adım 4'e bakın).

### 2. Kurulum

1. Repoyu klonlayın:
   ```bash
   git clone https://github.com/dormhi/DMS.git
   cd DMS
   ```

2. Çevre değişkenleri dosyasını oluşturun:
   ```bash
   cp .env.example .env
   nano .env
   ```
   `TELEGRAM_BOT_TOKEN` değerinizi girin. `TELEGRAM_ALLOWED_USER_IDS` satırını şimdilik boş bırakın — ID'nizi bulduktan sonra ekleyeceksiniz.

3. Sistemi başlatın:
   ```bash
   docker-compose up -d --build
   ```

4. **Telegram Kullanıcı ID'nizi bulun** — Bot varsayılan olarak **özel modda** çalışır. Siz yetki verene kadar hiç kimseye cevap vermez:
   ```bash
   # Bot'a Telegram'dan bir mesaj atın (cevap gelmeyecek)
   # Log'dan ID'nizi görün:
   docker-compose logs bot | grep "Unauthorized"
   ```
   Çıktı şöyle olacak: `Unauthorized user 123456789 tried to use the bot`
   Buradaki numarayı (örnekte `123456789`) `.env` dosyanıza ekleyin:
   ```bash
   echo "TELEGRAM_ALLOWED_USER_IDS=123456789" >> .env
   docker-compose restart bot
   ```
   Artık bot size cevap verecektir. Daha sonra başka kullanıcı eklemek için ID'leri virgülle ayırın: `123456789,987654321`.

### 3. Kullanım

* **Telegram Bot**: Botunuza `/start` yazın.
  - `/download <link>` — Desteklenen platformlardan video indirir.
  - `/jobs` — Aktif işlerinizin durumunu gösterir.
  - `/help` — Tüm komutları listeler.
  - **Video dosyası gönderme** — Herhangi bir video dosyasını doğrudan bota gönderin, onarım/optimizasyon başlasın.
  - İşlem bittiğinde bot videoyu sohbetten geri atar (50MB üstü dosyalar için bilgilendirme mesajı gönderir).

* **Web Arayüzü**: Tarayıcıdan `http://localhost:5173` adresine gidin.
  - **Dashboard** — URL göndererek indirme başlatın, tüm işlerin durumunu canlı takip edin.
  - **Kütüphane (Library)** — Tamamlanmış videoları görüntüleyin. Her video için **Oynat**, **İndir** ve **Sil** butonları mevcut.
  - **Giriş**: Varsayılan kullanıcı adı ve şifre `admin` / `admin`'dir (kişisel kullanım — değiştirmek için `backend/main.py` dosyasını düzenleyin).

* **Desteklenen Platformlar**: Kick (uzun VOD'lar dahil), YouTube, Twitter/X, Facebook, TikTok, Twitch ve yt-dlp'nin desteklediği tüm siteler.
