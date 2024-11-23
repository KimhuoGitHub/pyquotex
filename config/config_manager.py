# config_manager.py

import os
import json
from dotenv import load_dotenv
import logging
from colorama import Fore

# Load environment variables from .env file
load_dotenv()


class ConfigManager:
    def __init__(self, config_path=None):
        self.is_server = os.getenv("IS_SERVER") == "true"
        self.config_path = config_path or (
            "config/config.prod.json" if self.is_server else "config/config.dev.json"
        )
        self.config = self._load_config()
        self._initialize_parameters()

    def _initialize_parameters(self):
        self.base_trade_amount = self.config.get("base_trade_amount", 1)
        self.max_trade_risk = self.config.get("max_trade_risk", 50)
        self.dynamic_risk_management = self.config.get("dynamic_risk_management", True)
        self.martingale_multiplier = self.config.get("martingale_multiplier", 2.5)
        self.max_martingale_steps = self.config.get("max_martingale_steps", 5)
        self.daily_profit_target = self.config.get("daily_profit_target", 50)
        self.daily_loss_limit = self.config.get("daily_loss_limit", 50)
        self.base_cooldown_period = self.config.get("base_cooldown_period", 180)
        self.re_analyze_period = self.config.get("re_analyze_period", 600)
        self.interval = self.config.get("interval", 60)
        self.candle_count = self.config.get("candle_count", 100)
        self.max_cooldown = self.config.get("max_cooldown", 900)
        self.trade_duration = self.config.get("trade_duration", 1)
        self.asset_type = self.config.get("asset_type", "binary")
        self.volatility_threshold = 0.01
        self.trend_strength_threshold = 0.02

    def _load_config(self) -> dict:
        try:
            with open(self.config_path) as config_file:
                return json.load(config_file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file {self.config_path} not found.")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in configuration file.")

    def get_config(self) -> dict:
        return self.config

    def get_telegram_token(self) -> str:
        return os.getenv(
            "TELEGRAM_PROD_TOKEN" if self.is_server else "TELEGRAM_DEV_TOKEN"
        )

    def get_credentials(self) -> dict:
        return {
            "email": os.getenv("QUOTEX_EMAIL"),
            "password": os.getenv("QUOTEX_PASSWORD"),
            "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID"),
        }

    def init_audio(self):
        if not self.is_server:
            try:
                import pygame

                pygame.mixer.init()
                logging.info(
                    Fore.WHITE
                    + "\n\n🔉 Audio initialized successfully\n"
                    + "----------------------------------------\n"
                )
            except Exception as e:
                logging.warning(
                    Fore.YELLOW
                    + f"\n\n 🔇 Audio device not available: {e}\n"
                    + "----------------------------------------\n"
                )
        else:
            logging.info(
                Fore.YELLOW
                + "\n\n🔇 Running in server mode. Audio initialization skipped\n"
                + "----------------------------------------\n"
            )
