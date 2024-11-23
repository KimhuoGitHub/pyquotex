# quotex_bot.py

import asyncio
import pandas as pd
import talib
import sys
import signal
import logging
from colorama import Fore
from core.api_client import QuotexClient
from core.notifier import Notifier

FAST_EMA_PERIOD = 5
SLOW_EMA_PERIOD = 12
RSI_PERIOD = 9
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30


class QuotexBot:
    def __init__(self, email, password, config, telegram_token, telegram_chat_id):
        self.api_client = QuotexClient(email, password)
        self.notifier = Notifier(telegram_token, telegram_chat_id)
        self.config = config
        self.running = True
        self.asset = None
        self.timeframe = 1
        self.base_bet = 1.0
        self.current_bet = self.base_bet
        self.total_profit = 0.0
        self.profit_target = 50.0
        self.stop_loss_limit = -50.0
        self.martingale_step = 0
        self.max_martingale_steps = 5
        self.payout_threshold = 70
        signal.signal(signal.SIGINT, self.signal_handler)

    async def connect(self) -> bool:
        check = await self.api_client.connect()
        if check:
            self.notifier.log_generic(
                f"\n\n🤖 BOT STARTED\n" + "----------------------------------------\n",
                Fore.WHITE,
            )
            return True
        return False

    async def fetch_candles(self):
        candles = await self.api_client.get_realtime_candles(
            self.asset, self.timeframe * 60
        )
        return pd.DataFrame.from_dict(candles, orient="index")

    def apply_indicators(self, df):
        df["fast_ema"] = talib.EMA(df["close"], timeperiod=FAST_EMA_PERIOD)
        df["slow_ema"] = talib.EMA(df["close"], timeperiod=SLOW_EMA_PERIOD)
        df["rsi"] = talib.RSI(df["close"], timeperiod=RSI_PERIOD)
        return df

    def generate_signal(self, df):
        if len(df) < max(FAST_EMA_PERIOD, SLOW_EMA_PERIOD, RSI_PERIOD):
            return None

        last_row = df.iloc[-1]
        second_last_row = df.iloc[-2]

        if (
            second_last_row["fast_ema"] < second_last_row["slow_ema"]
            and last_row["fast_ema"] > last_row["slow_ema"]
            and last_row["rsi"] > RSI_OVERSOLD
        ):
            return "buy"
        elif (
            second_last_row["fast_ema"] > second_last_row["slow_ema"]
            and last_row["fast_ema"] < last_row["slow_ema"]
            and last_row["rsi"] < RSI_OVERBOUGHT
        ):
            return "sell"
        return None

    async def execute_trade(self, signal):
        direction = "call" if signal == "buy" else "put"
        emoji = "🟩" if signal == "buy" else "🟥"
        status, buy_info = await self.api_client.place_trade(
            self.current_bet, self.asset, direction, 60
        )

        payout = self.api_client.get_asset_payout(self.asset)
        if payout < self.payout_threshold:
            self.notifier.log_generic(
                f"⚠️ Skipped trade: {self.asset} payout {payout}% is below threshold {self.payout_threshold}%.",
                Fore.YELLOW,
            )
            return

        if status:
            self.message_id = self.notifier.log_generic(
                f"{emoji} {signal.upper()}: {self.current_bet:.2f} `[{self.martingale_step}/{self.max_martingale_steps}]`",
                Fore.WHITE,
            )
            await self.check_win(buy_info["id"])
        else:
            logging.error("Trade failed to execute.")

    async def check_win(self, order_id):
        logging.info(Fore.CYAN + "🕐 Waiting for result...")
        win_status = await self.api_client.check_win(order_id)
        emoji = "🟢" if win_status else "🔴"
        profit = self.api_client.get_profit()
        self.total_profit += profit
        self.notifier.log_generic(
            f"\n\n{emoji} P/L: {profit:.2f} `[{self.martingale_step}/{self.max_martingale_steps}]` | 💰 Profit: {self.total_profit:.2f} USD\n",
            Fore.WHITE,
            self.message_id,
        )

        if win_status:
            self.current_bet = self.base_bet
            self.martingale_step = 0
        else:
            self.martingale_step += 1
            if self.martingale_step > self.max_martingale_steps:
                self.notifier.log_generic(
                    "⚠️ Maximum Martingale steps reached. Stopping bot.", Fore.RED
                )
                self.shutdown_trading()
            else:
                self.current_bet *= 2.5

        if self.total_profit >= self.profit_target:
            self.notifier.log_generic(
                "🎉 Profit target reached. Stopping bot.", Fore.CYAN
            )
            self.shutdown_trading()
        elif self.total_profit <= self.stop_loss_limit:
            self.notifier.log_generic(
                "🚨 Stop loss limit reached. Stopping bot.", Fore.RED
            )
            self.shutdown_trading()

    def signal_handler(self, signum, frame):
        self.notifier.log_generic(
            "\n\n⚠️ BOT STOPPED by user\n"
            + "----------------------------------------\n",
            Fore.YELLOW,
        )
        self.shutdown_trading()

    def shutdown_trading(self):
        self.api_client.disconnect()
        self.running = False
        logging.info(Fore.YELLOW + "🛑 BOT is shutting down...")
        sys.exit(0)

    async def run(self):
        while self.running:
            try:
                self.asset, _ = await self.api_client.get_available_asset("EURUSD")
                df = await self.fetch_candles()
                df = self.apply_indicators(df)
                signal = self.generate_signal(df)
                if signal:
                    await self.execute_trade(signal)
                await asyncio.sleep(1)
            except Exception as e:
                # logging.error(f"Error in main loop: {e}")
                # await asyncio.sleep(10)
                self.notifier.log_generic(
                    "⚠️ Connection is already closed.", Fore.YELLOW
                )
                self.shutdown_trading()
