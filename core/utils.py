# utils.py

import logging
import subprocess
from colorama import Fore, init
import pygame
import os
import time
from datetime import datetime, timedelta

init(autoreset=True)


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(message)s",
    )


def get_git_info():
    try:
        branch = (
            subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
            .strip()
            .decode("utf-8")
        )
        commit_hash = (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .strip()
            .decode("utf-8")
        )
        return branch, commit_hash
    except Exception as e:
        logging.error(Fore.RED + f"Error retrieving Git info: {e}")
        return "unknown", "unknown"


def play_music(sound, loops=0, volume=1, fade_in=1000):
    try:
        sound_path = f"sound/{sound}.wav"

        if not os.path.exists(sound_path):
            logging.error(Fore.RED + f"Sound file not found: {sound_path}")
            return

        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops=loops, fade_ms=fade_in)

    except Exception as e:
        logging.error(Fore.RED + f"Error playing sound '{sound}': {e}")


def stop_music(fade_out=2000):
    pygame.mixer.music.fadeout(fade_out)


def get_current_time():
    return time.time()


def calculate_wait_time(target_second=0):
    now = datetime.now()
    next_time = now.replace(second=target_second, microsecond=0)

    if now.second >= target_second:
        next_time += timedelta(minutes=1)

    wait_time = (next_time - now).total_seconds()
    return wait_time


def allowed_trading_time(start_minute=10, end_minute=50):
    current_minute = datetime.now().minute
    if start_minute < current_minute < end_minute:
        return True
    else:
        logging.info(
            Fore.YELLOW
            + f"🚫 Trading is not allowed: \n\nCurrent minute {current_minute} is outside the allowed range ({start_minute} - {end_minute}).\n"
            + "----------------------------------------\n"
        )
        return False
