# 🎬 DMS (Dormhi Media Server)

**Language Selection / Dil Seçimi:**
- [English Documentation](#english-documentation)
- [Türkçe Dokümantasyon](#türkçe-dokümantasyon)

---

<a name="english-documentation"></a>
# 🇺🇸 English Documentation

Welcome to **Dormhi Media Server (DMS)**! DMS is a self-hosted media automation platform for one owner’s personal library. It downloads and optionally repairs media on your own server, so you do not need to download videos directly to your personal devices.

> **Personal-use design:** DMS is not a public, multi-tenant, or general-purpose download service. Keep it under your control and grant Telegram access only to people you explicitly trust.

## 🚀 Key Features

* **Smart Downloading**: Uses `yt-dlp` to download media from Kick, YouTube, Twitter, Facebook, TikTok, Twitch, and more. Optimized for long VODs (5+ hours) with HLS fragment handling and automatic retry.
* **Intelligent Auto-Repair**: Uses `ffprobe` and `ffmpeg` to automatically normalize video (h264) and audio (aac) codecs. It follows a "least destructive" principle — only transcoding what is necessary, preserving quality.
* **Telegram Bot (Private Mode)**: Only IDs listed in `TELEGRAM_ALLOWED_USER_IDS` can interact with the bot. Send `/download <url>` or upload a video directly. The bot handles downloading, repairing, and sends the optimized video back via chat.
* **Rate Limiting**: Built-in protection against command spam (3 commands per 60 seconds per user).
* **Premium Web Dashboard**: A modern, responsive React/Tailwind dashboard to submit URLs, monitor active jobs in real-time, and browse your media library with play, download, and delete controls.
* **Asynchronous Queue**: Powered by Celery and Redis, multiple downloads and intensive processing jobs are handled smoothly in the background.
* **Automatic Archive Management**: Finished jobs are retained for 7 days. Completed media is capped at 5 GB; when the limit is exceeded, the oldest media is removed first.

## 🏗 Architecture & Tech Stack

* **Backend**: Python 3.11, FastAPI, SQLAlchemy
* **Database**: SQLite with WAL mode — a deliberate, sufficient choice for one owner and low-concurrency personal use. PostgreSQL is only needed for a future multi-user or higher-concurrency deployment.
* **Message Broker & Worker**: Redis + Celery
* **Media Engines**: `yt-dlp` (latest), FFmpeg
* **Frontend**: React 19, TypeScript, TailwindCSS, Vite
* **Infrastructure**: 100% Dockerized via `docker-compose` (6 services: backend, worker, beat scheduler, bot, Redis, and frontend)

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
   # Replace the empty TELEGRAM_ALLOWED_USER_IDS value in .env with your ID.
   # For example: TELEGRAM_ALLOWED_USER_IDS=123456789
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

### 4. Personal VDS Deployment

If you run DMS on a VDS and access the web panel through its external IP, treat it as a private administration tool:

* Redis is intentionally available only inside the Docker network; do not publish it or expose it to the internet.
* Restrict web-panel access to your trusted IP addresses with a firewall. Put a reverse proxy with HTTPS in front of it when accessing it over the internet.
* Change the default web login credentials in `backend/main.py` before exposing the panel beyond your local network.
* You are responsible for the media you download and for complying with the terms and policies of each source platform.

---

<a name="türkçe-dokümantasyon"></a>
# 🇹🇷 Türkçe Dokümantasyon

**Dormhi Media Server (DMS)** projesine hoş geldiniz! DMS, tek sahibin kişisel medya kütüphanesi için tasarlanmış self-hosted bir medya otomasyon platformudur. Medyayı kendi sunucunuzda indirir ve gerekirse onarır; böylece kişisel cihazlarınıza doğrudan video indirmeniz gerekmez.

> **Kişisel kullanım tasarımı:** DMS herkese açık, çok kullanıcılı veya genel amaçlı bir indirme servisi değildir. Sistemi kendi kontrolünüzde tutun ve Telegram erişimini yalnızca güvendiğiniz kişilere verin.

## 🚀 Temel Özellikler

* **Akıllı İndirme**: Kick, YouTube, Twitter, Facebook, TikTok ve Twitch gibi platformlardan medya indirmek için güçlü `yt-dlp` altyapısını kullanır. Uzun VOD'lar (5+ saat) için optimize edilmiş HLS fragment yönetimi ve otomatik yeniden deneme.
* **Akıllı Otomatik Onarım**: Video dosyalarınızı `ffprobe` ile inceler. Uyumluluk sorunları varsa `ffmpeg` ile donanım dostu standart formata (h264/aac) sokar. "Minimum tahribat" prensibiyle sadece bozuk olan kısmı dönüştürür, kaliteyi korur.
* **Telegram Bot (Özel Mod)**: Yalnızca `TELEGRAM_ALLOWED_USER_IDS` içinde tanımlı ID'ler botla etkileşime geçebilir. `/download <link>` ile video indirin veya doğrudan bir video dosyası gönderin. Bot her şeyi halledip optimize edilmiş videoyu size geri gönderir.
* **Rate Limiting (Hız Sınırı)**: Komut spam'ına karşı yerleşik koruma (kullanıcı başına 60 saniyede 3 komut).
* **Premium Web Dashboard**: URL gönderme, işleri canlı takip etme ve kütüphanede **oynatma**, **indirme**, **silme** özellikli modern React/Tailwind paneli.
* **Asenkron İş Kuyruğu**: Celery ve Redis sayesinde çoklu indirme ve işlemci yoran görevler arka planda takılmadan yürütülür.
* **Otomatik Arşiv Yönetimi**: Bitmiş işler 7 gün saklanır. Tamamlanmış medya toplamda 5 GB ile sınırlıdır; limit aşılırsa en eski medya önce silinir.

## 🏗 Mimari ve Teknoloji Yığını

* **Backend**: Python 3.11, FastAPI, SQLAlchemy
* **Veritabanı**: SQLite WAL modu — tek sahipli, düşük eşzamanlılıklı kişisel kullanım için bilinçli ve yeterli tercihtir. PostgreSQL ancak ileride çok kullanıcılı veya daha yüksek eşzamanlılıklı bir kurulum gerekirse anlamlıdır.
* **Mesaj Kuyruğu & Worker**: Redis + Celery
* **Medya Motorları**: `yt-dlp` (güncel sürüm), FFmpeg
* **Frontend**: React 19, TypeScript, TailwindCSS, Vite
* **Altyapı**: Tamamen Dockerize (6 servis: backend, worker, beat zamanlayıcısı, bot, Redis ve frontend)

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
   # .env içindeki boş TELEGRAM_ALLOWED_USER_IDS değerini kendi ID'nizle değiştirin.
   # Örnek: TELEGRAM_ALLOWED_USER_IDS=123456789
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

### 4. Kişisel VDS Kurulumu

DMS'i bir VDS üzerinde çalıştırıp web paneline dış IP üzerinden erişecekseniz, sistemi kişisel bir yönetim aracı olarak ele alın:

* Redis yalnızca Docker ağı içinde erişilebilir olacak şekilde yapılandırılmıştır; Redis'i internete açmayın veya host portu olarak yayınlamayın.
* Web paneline erişimi firewall ile yalnızca güvendiğiniz IP adreslerine sınırlayın. İnternet üzerinden erişimde önüne HTTPS kullanan bir reverse proxy koyun.
* Paneli yerel ağınızın dışına açmadan önce `backend/main.py` içindeki varsayılan web giriş bilgilerini değiştirin.
* İndirdiğiniz içeriklerden ve her kaynak platformun kullanım koşulları ile politikalarına uymaktan siz sorumlusunuz.
