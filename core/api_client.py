# api_client.py

import asyncio
from pathlib import Path
import logging
from quotexapi.stable_api import Quotex
from core.notifier import Notifier
from colorama import Fore


class QuotexClient:
    def __init__(self, email, password):
        self.client = Quotex(email, password)

    async def connect(self, max_retries=1000):
        attempt = 0
        while attempt < max_retries:
            check, reason = await self.client.connect()
            if check:
                return True, reason

            attempt += 1
            logging.warning(Fore.YELLOW + f"⚠️ Attempt ▶ {attempt}/{max_retries}")
            if Path("session.json").is_file():
                Path("session.json").unlink()

            await asyncio.sleep(5)

        return False

    async def get_available_asset(self, asset, force_open=True):
        return await self.client.get_available_asset(asset, force_open)

    async def get_balance(self):
        return await self.client.get_balance()

    async def get_realtime_candles(self, asset_name, interval):
        return await self.client.get_realtime_candles(asset_name, interval)

    async def place_trade(self, amount, asset, direction, duration):
        return await self.client.buy(amount, asset, direction, duration)

    async def check_win(self, order_id):
        return await self.client.check_win(order_id)

    def get_profit(self):
        return self.client.get_profit()

    def get_asset_payout(self, asset):
        formatted_asset = f"{asset[:3]}/{asset[3:]}"
        all_data = self.client.get_payment()
        if formatted_asset in all_data:
            return all_data[formatted_asset]["profit"]["1M"]
        return 0

    def disconnect(self):
        self.client.close()
