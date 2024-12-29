from loguru import logger
from curl_cffi import requests
import pyfiglet
import time
from datetime import datetime, timedelta
import pytz

# Konfigurasi loguru logger
logger.remove()
logger.add(
    sink=lambda msg: print(msg, end=''),
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level:8} | {message}</level>"
    ),
    colorize=True
)

def print_header():
    """Menampilkan header aplikasi."""
    header = pyfiglet.figlet_format("Nodepay Bot", font="slant")
    print(header)
    print("🌟 Created by A_A")
    print("🎨 GitHub: \033]8;;https://github.com/AdiityaAnugrah/NodepayBot\033\\AdiityaAnugrah/NodepayBot\033]8;;\033\\")
    print("✨ Support via PayPal: \033]8;;https://www.paypal.com/paypalme/@Adiityaanugrah10\033\\PayPal.me/@Adiityaanugrah10\033]8;;\033\\\n")

# Menampilkan header saat program dimulai
print_header()

def read_tokens():
    """Membaca jumlah token yang ada di file tokens.txt."""
    try:
        with open('tokens.txt', 'r') as file:
            tokens_count = sum(1 for line in file if line.strip())
        return tokens_count
    except FileNotFoundError:
        logger.error("File 'tokens.txt' tidak ditemukan. Pastikan file tersedia.")
        return 0

# Menampilkan jumlah token
tokens_count = read_tokens()
print(f"🔑 Tokens: {tokens_count}.\n")

def truncate_token(token):
    """Memperpendek token untuk tampilan log."""
    return f"{token[:4]}--{token[-4:]}"

def claim_reward(token):
    """Mengklaim reward menggunakan token yang diberikan."""
    url = "https://api.nodepay.org/api/mission/complete-mission"
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Origin": "https://app.nodepay.ai",
        "Referer": "https://app.nodepay.ai/"
    }
    data = {"mission_id": "1"}
    retries = 3

    for attempt in range(1, retries + 1):
        try:
            response = requests.post(url, headers=headers, json=data, impersonate="chrome110")

            if response.status_code == 200:
                response_data = response.json()
                if response_data.get('success'):
                    logger.success(f"Token: {truncate_token(token)} | Reward claimed successfully")
                    break
                else:
                    logger.info(f"Token: {truncate_token(token)} | Reward already claimed or another issue occurred")
                    break
            elif response.status_code == 403:
                logger.warning(f"Token: {truncate_token(token)} | Attempt {attempt}/{retries}: HTTP 403 Forbidden.")
                if attempt == retries:
                    logger.error(f"Token: {truncate_token(token)} | Maximum retries reached for HTTP 403.")
                else:
                    time.sleep(2)
            else:
                logger.error(f"Token: {truncate_token(token)} | Failed request, HTTP Status: {response.status_code}")
                break

        except requests.exceptions.RequestException as e:
            logger.error(f"Token: {truncate_token(token)} | Request error: {e}")
            break

def main():
    """Fungsi utama untuk menjalankan klaim reward."""
    try:
        with open('tokens.txt', 'r') as file:
            tokens = [line.strip() for line in file if line.strip()]

        if not tokens:
            logger.error("Tidak ada token di dalam file 'tokens.txt'.")
            return

        for token in tokens:
            claim_reward(token)
            time.sleep(2)

        logger.success("Semua token telah diproses. Daily claim selesai.")

    except FileNotFoundError:
        logger.error("File 'tokens.txt' tidak ditemukan. Pastikan file tersedia.")
    except Exception as e:
        logger.exception(f"Terjadi kesalahan tak terduga: {e}")

def time_until_next_run():
    """Menghitung waktu hingga eksekusi berikutnya (jam 9 pagi waktu Jakarta)."""
    tz = pytz.timezone("Asia/Jakarta")  # WIB
    now = datetime.now(tz)
    next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)

    if now >= next_run:
        next_run += timedelta(days=1)

    return (next_run - now).total_seconds()

if __name__ == "__main__":
    try:
        while True:
            main()
            next_run_seconds = time_until_next_run()
            next_run_time = datetime.now(pytz.timezone("Asia/Jakarta")) + timedelta(seconds=next_run_seconds)
            logger.info(f"Next run scheduled for {next_run_time.strftime('%Y-%m-%d %H:%M:%S')} WIB.")
            time.sleep(next_run_seconds)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Program dihentikan oleh pengguna. Terima kasih telah menggunakan Nodepay Bot!")
