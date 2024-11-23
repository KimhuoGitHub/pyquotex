# notifier.py

import logging
import requests
from colorama import Fore


class Notifier:
    def __init__(self, telegram_token: str, telegram_chat_id: str):
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id

    def send_telegram_message(self, message: str) -> int:
        url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {
            "chat_id": self.telegram_chat_id,
            "text": message,
            "parse_mode": "Markdown",
        }
        try:
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                message_id = response.json().get("result", {}).get("message_id")
                return message_id
            else:
                logging.error(
                    Fore.RED
                    + f"Failed to send Telegram message: {response.status_code}"
                )
        except Exception as e:
            logging.error(Fore.RED + f"Error sending Telegram message: {e}")
        return None

    def edit_telegram_message(self, message_id: int, new_message: str):
        url = f"https://api.telegram.org/bot{self.telegram_token}/editMessageText"
        payload = {
            "chat_id": self.telegram_chat_id,
            "message_id": message_id,
            "text": new_message,
            "parse_mode": "Markdown",
        }
        try:
            response = requests.post(url, data=payload)
            if response.status_code != 200:
                logging.error(
                    Fore.RED
                    + f"Failed to edit Telegram message: {response.status_code}"
                )
        except Exception as e:
            logging.error(Fore.RED + f"Error editing Telegram message: {e}")

    def log_generic(
        self, message: str, color: str = Fore.WHITE, message_id: int = None
    ):
        logging.info((color + message).replace("`", ""))  # Remove backticks for logging
        if message_id:
            self.edit_telegram_message(message_id, message)
        else:
            return self.send_telegram_message(message)
            pass
