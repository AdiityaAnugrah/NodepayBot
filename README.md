# NodepayBot

A bot designed to connect via multiple HTTP proxies and manage Nodepay accounts using a multi-account setup.

## Installation

1. **Prepare the Environment**\
   Update your system and install Python:

   ```bash
   sudo apt update -y && apt install -y python3 python3-venv python3-pip
   ```

2. **Clone the Repository**\
   Download and set up the bot:

   ```bash
   git clone https://github.com/AdiityaAnugrah/NodepayBot.git && cd NodepayBot
   python3 -m venv venv && source venv/bin/activate
   ```

3. **Install Dependencies**\
   Install all necessary dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Bot**\
   Start the bot with:

   ```bash
   python main.py
   ```

   Alternatively, run the bot without using a proxy (if preferred):

   ```bash
   python main2.py
   ```

## Token Setup

- **Haven't registered yet?** Use this referral link: ([REGISTER NODEPAY)](https://app.nodepay.ai/register?ref=pF44YFTQOyjOB5I).
- **How to Obtain Your Token?**
  1. Log in to your account at [Nodepay Dashboard](https://app.nodepay.ai/dashboard).
  2. Open Developer Tools in your browser (F12) and navigate to the "Console" tab.
  3. Enter the following command:
     ```javascript
     localStorage.getItem('np_token')
     ```
  4. Copy the result and paste it into the `tokens.txt` file.
  5. If you manage multiple accounts, add each token on a new line:
     ```
     token1
     token2
     token3
     ```

## Proxy Setup

- Fill the `proxy.txt` file with proxies in the following format:
  ```
  protocol://user:pass@host:port
  ```
  Example:
  ```
  http://username:password@123.123.123.123:8080
  socks5://username:password@123.123.123.123:1080
  ```

## Need a Proxy?

1. Sign up at [Proxies.fo](https://app.proxies.fo/ref/d6c7352f-4d34-35df-dc1c-770edf36b920).
2. Go to [Plans](https://app.proxies.fo/plans) and purchase the "ISP plan" (Residential plans are not compatible).
3. Top up your balance or directly purchase a plan.
4. Configure your proxy as:
   ```
   protocol://username:password@hostname:port
   ```
5. Paste the generated proxies into `proxy.txt`.

## Running the Bot

1. To start the bot:
   ```bash
   python main.py
   ```
2. Alternatively, run the bot without using a proxy:
   ```bash
   python main2.py
   ```
3. (Optional) Run the daily claim script:
   ```bash
   python dailyclaim.py
   ```

## Features

- Multi-account management.
- Proxy and non-proxy support.
- Seamless Nodepay interactions.
- Lightweight and easy to use.

## Donations

Support my work:

- **PayPal**: [Paypal.me/@Adiityaanugrah10](https://www.paypal.com/paypalme/@Adiityaanugrah10)
- **Solana**: `GghXB5Qqx1RjJgRM1GHxngzipsNWifcBTkbxfM8VHnRK`

---

