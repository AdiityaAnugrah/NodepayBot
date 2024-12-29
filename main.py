import asyncio
import time
import uuid
from datetime import datetime
from curl_cffi import requests
import colorama
from colorama import Fore, Style
from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel
from rich.text import Text

colorama.init(autoreset=True)
console = Console()

def log(level, message, color=Fore.WHITE):
    """Menambahkan elemen estetika dan format ke log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if level == "INFO":
        level_text = Text(f"[INFO]", style="bold green")
        emoji = "?"
    elif level == "ERROR":
        level_text = Text(f"[ERROR]", style="bold red")
        emoji = "?"
    elif level == "WARNING":
        level_text = Text(f"[WARNING]", style="bold yellow")
        emoji = "??"
    else:
        level_text = Text(f"[{level}]", style="bold white")
        emoji = "??"
    styled_message = Text(f"{emoji} [{timestamp}] ", style="cyan") + level_text + Text(f" {message}", style=color)
    console.print(Panel(styled_message, title="Log Output", title_align="left", padding=(1, 2)))

def show_warning():
    """Mempercantik tampilan peringatan saat program dimulai"""
    warning_message = """
[bold yellow]       /\        /\       [/bold yellow]
[bold yellow]      /  \      /  \      [/bold yellow]
[bold yellow]     / /\ \    / /\ \     [/bold yellow]
[bold yellow]    / ____ \  / ____ \    [/bold yellow]
[bold yellow]   /_/    \_\/_/    \_\   [/bold yellow]
[bold green]          AA-Code by https://github.com/AdiityaAnugrah[/bold green]
    """
    console.print(Panel(warning_message, title="Peringatan", style="bold red", padding=(1, 2)))
    log("INFO", "Program dimulai...", Fore.LIGHTBLUE_EX)

async def show_loading_animation(task_name):
    """Menambahkan progres bar untuk menunjukkan status aplikasi."""
    with Progress() as progress:
        task = progress.add_task(f"[green]{task_name}...", total=100)
        while not progress.finished:
            progress.update(task, advance=1)
            await asyncio.sleep(0.05)

PING_INTERVAL = 60
RETRIES = 60

DOMAIN_API = {
    "SESSION": "http://api.nodepay.ai/api/auth/session",
    "PING": "https://nw.nodepay.ai/api/network/ping"
}

CONNECTION_STATES = {
    "CONNECTED": 1,
    "DISCONNECTED": 2,
    "NONE_CONNECTION": 3
}

proxy_browser_ids = {}

def uuidv4():
    return str(uuid.uuid4())
    
def valid_resp(resp):
    if not resp or "code" not in resp or resp["code"] < 0:
        raise ValueError("Respon tidak valid")
    return resp

def parse_proxy(proxy_str):
    if '://' not in proxy_str:
        proxy_str = f'http://{proxy_str}'
    
    try:
        from urllib.parse import urlparse
        parsed = urlparse(proxy_str)
        
        proxy_dict = {
            'http': proxy_str,
            'https': proxy_str
        }
        
        if parsed.scheme in ['socks4', 'socks5']:
            proxy_dict['http'] = proxy_str
            proxy_dict['https'] = proxy_str
        
        return proxy_dict
    except Exception as e:
        log("ERROR", f"Format proxy tidak valid: {proxy_str}. Kesalahan: {e}", Fore.LIGHTRED_EX)
        return None
    
async def render_profile_info(proxy, token):
    global proxy_browser_ids

    try:
        if proxy not in proxy_browser_ids:
            proxy_browser_ids[proxy] = uuidv4()

        np_session_info = load_session_info(proxy)

        if not np_session_info:
            response = await call_api(DOMAIN_API["SESSION"], {}, proxy, token)
            valid_resp(response)
            account_info = response["data"]
            if account_info.get("uid"):
                save_session_info(proxy, account_info)
                await start_ping(proxy, token, account_info)
            else:
                handle_logout(proxy)
        else:
            account_info = np_session_info
            await start_ping(proxy, token, account_info)
    except Exception as e:
        log("ERROR", f"Kesalahan dalam render_profile_info untuk proxy {proxy}: {e}", Fore.LIGHTRED_EX)
        error_message = str(e)
        if any(phrase in error_message for phrase in [
            "sent 1011 (internal error) keepalive ping timeout; no close frame received",
            "500 Internal Server Error"
        ]):
            log("WARNING", f"Menghapus proxy error dari daftar: {proxy}", Fore.LIGHTYELLOW_EX)
            remove_proxy_from_list(proxy)
            return None
        else:
            log("ERROR", f"Kesalahan koneksi: {e}", Fore.LIGHTRED_EX)
            return proxy

async def call_api(url, data, proxy, token):
    parsed_proxies = parse_proxy(proxy)
    if not parsed_proxies:
        raise ValueError(f"Proxy tidak valid: {proxy}")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, seperti Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
        "Accept": "application/json",
        "Accept-Language": "id-ID,id;q=0.9",
        "Origin": "chrome-extension://lgmpfmgeabnnlemejacfljbmonaomfmm",
    }

    try:
        response = requests.post(
            url, 
            json=data, 
            headers=headers, 
            proxies=parsed_proxies,
            timeout=30,
            impersonate="chrome110"
        )

        return valid_resp(response.json())
    except Exception as e:
        log("ERROR", f"Kesalahan selama panggilan API: {e}", Fore.LIGHTRED_EX)
        raise ValueError(f"Gagal memanggil API ke {url}")

async def start_ping(proxy, token, account_info):
    try:
        while True:
            await ping(proxy, token, account_info)
            await asyncio.sleep(PING_INTERVAL)
    except asyncio.CancelledError:
        log("INFO", f"Tugas ping untuk proxy {proxy} dibatalkan", Fore.LIGHTBLUE_EX)
    except Exception as e:
        log("ERROR", f"Kesalahan dalam start_ping untuk proxy {proxy}: {e}", Fore.LIGHTRED_EX)

async def get_real_ip(proxy):
    parsed_proxies = parse_proxy(proxy)
    if not parsed_proxies:
        return "N/A"
    
    try:
        response = requests.get(
            "https://api64.ipify.org/", 
            proxies=parsed_proxies,
            timeout=10
        )
        return response.text.strip()
    except Exception as e:
        log("ERROR", f"Gagal mendapatkan IP nyata melalui proxy {proxy}: {e}", Fore.LIGHTRED_EX)
        return "N/A"

async def ping(proxy, token, account_info):
    console.log(f":satellite: [green]Ping berjalan untuk proxy {proxy} dan akun {account_info.get('email', 'N/A')}[/green]")
    global proxy_browser_ids, RETRIES, CONNECTION_STATES

    current_time = time.time()

    try:
        data = {
            "id": account_info.get("uid"),
            "browser_id": proxy_browser_ids[proxy],
            "timestamp": int(time.time()),
            "version":"2.2.7"
        }

        response = await call_api(DOMAIN_API["PING"], data, proxy, token)
        if response["code"] == 0:
            ip_score = response.get('data', {}).get('ip_score', 'N/A')
            real_ip = await get_real_ip(proxy)
            log("INFO", 
                f"Akun: {Fore.LIGHTGREEN_EX}{account_info.get('email', 'N/A')}{Style.RESET_ALL} | " + 
                f"ID Browser: {Fore.LIGHTMAGENTA_EX}{proxy_browser_ids[proxy]}{Style.RESET_ALL} | " +
                f"IP: {Fore.LIGHTYELLOW_EX}{real_ip}{Style.RESET_ALL} | " + 
                f"Skor IP: {Fore.LIGHTRED_EX}{ip_score}{Style.RESET_ALL}", 
                Fore.LIGHTCYAN_EX)
            RETRIES = 0
        else:
            handle_ping_fail(proxy, response)
    except Exception as e:
        log("ERROR", f"Ping gagal melalui proxy {proxy}: {e}", Fore.LIGHTRED_EX)
        handle_ping_fail(proxy, None)

def handle_ping_fail(proxy, response):
    global RETRIES

    RETRIES += 1
    if response and response.get("code") == 403:
        handle_logout(proxy)

def handle_logout(proxy):
    global proxy_browser_ids

    if proxy in proxy_browser_ids:
        del proxy_browser_ids[proxy]
    save_status(proxy, None)
    log("WARNING", f"Keluar dan membersihkan informasi sesi untuk proxy {proxy}", Fore.LIGHTYELLOW_EX)

def load_proxies(proxy_file):
    try:
        with open(proxy_file, 'r') as file:
            proxies = file.read().splitlines()
        return [p for p in proxies if p.strip()]
    except Exception as e:
        log("ERROR", f"Gagal memuat proxy: {e}", Fore.LIGHTRED_EX)
        raise SystemExit("Keluar karena kegagalan memuat proxy")

def save_status(proxy, status):
    pass  

def save_session_info(proxy, data):
    pass

def load_session_info(proxy):
    return {}  

def is_valid_proxy(proxy):
    return parse_proxy(proxy) is not None

def remove_proxy_from_list(proxy):
    pass  

async def multi_account_mode(all_tokens, all_proxies):
    valid_proxies = [proxy for proxy in all_proxies if is_valid_proxy(proxy)]
    
    token_tasks = []
    
    for index, token in enumerate(all_tokens, 1):
        start_proxy = ((index - 1) * 3)
        end_proxy = start_proxy + 3
        token_proxies = valid_proxies[start_proxy:end_proxy]
        
        if not token_proxies:
            log("WARNING", f"Tidak ada proxy yang tersedia untuk Token {index}", Fore.LIGHTYELLOW_EX)
            continue
        
        log("INFO", f"Token {index} dengan Proxy: {token_proxies}", Fore.LIGHTBLUE_EX)
        
        task = asyncio.create_task(process_token(token, token_proxies))
        token_tasks.append(task)
    
    if token_tasks:
        await asyncio.gather(*token_tasks)

async def process_token(token, proxies):
    tasks = {asyncio.create_task(render_profile_info(
        proxy, token)): proxy for proxy in proxies}

    while tasks:
        done, pending = await asyncio.wait(tasks.keys(), return_when=asyncio.FIRST_COMPLETED)
        for task in done:
            failed_proxy = tasks[task]
            if task.result() is None:
                log("INFO", f"Menghapus dan mengganti proxy yang gagal untuk token {token[:10]}...: {failed_proxy}", Fore.LIGHTYELLOW_EX)
                proxies.remove(failed_proxy)
            tasks.pop(task)

        for proxy in set(proxies) - set(tasks.values()):
            new_task = asyncio.create_task(
                render_profile_info(proxy, token))
            tasks[new_task] = proxy
        
        if not tasks:
            break
        
        await asyncio.sleep(3)
    
    await asyncio.sleep(10)

async def main():
    while True:
        try:
            await show_loading_animation("Memuat Aplikasi")
            all_proxies = load_proxies('proxy.txt')
            
            try:
                with open('tokens.txt', 'r') as file:
                    all_tokens = [line.strip() for line in file if line.strip()]
                
                if not all_tokens:
                    log("ERROR", "Tidak ada token yang ditemukan di tokens.txt", Fore.LIGHTRED_EX)
                    exit()
                
                await multi_account_mode(all_tokens, all_proxies)
            
            except FileNotFoundError:
                log("ERROR", "tokens.txt tidak ditemukan. Harap buat file dengan token.", Fore.LIGHTRED_EX)
                exit()
        except Exception as e:
            log("ERROR", f"Terjadi kesalahan: {e}. Memulai ulang program...", Fore.LIGHTRED_EX)

if __name__ == '__main__':
    show_warning()
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print(Fore.LIGHTRED_EX + "Program dihentikan oleh pengguna.")
