import logging
from datetime import datetime
from colorama import init, Fore, Style
import random

init(autoreset=True)

SUCCESS_LEVEL_NUM = 25
FAILED_LEVEL_NUM = 35

class Logger:
    DATETIME_WIDTH = 19
    LEVEL_WIDTH = 8
    ACCOUNT_INDEX_WIDTH = 3

    LEVEL_COLOR = {
        'INFO': Fore.LIGHTCYAN_EX,
        'DEBUG': Fore.LIGHTBLUE_EX,
        'WARNING': Fore.LIGHTYELLOW_EX,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.LIGHTMAGENTA_EX,
        'SUCCESS': Fore.LIGHTGREEN_EX,
        'FAILED': Fore.LIGHTRED_EX,
    }

    INDEX_COLORS = [
        Fore.LIGHTMAGENTA_EX,
        Fore.LIGHTBLUE_EX,
        Fore.LIGHTCYAN_EX,
        Fore.LIGHTGREEN_EX,
        Fore.LIGHTYELLOW_EX,
        Fore.LIGHTRED_EX,
        Fore.WHITE,
    ]

    def __init__(self, filename="bot.log"):
        logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")
        logging.addLevelName(FAILED_LEVEL_NUM, "FAILED")

        self.logger = logging.getLogger("PlumeSwapBotLogger")
        self.logger.setLevel(logging.DEBUG)

        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler = logging.FileHandler(filename)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        self.account_index = None
        self._index_color_map = {}

    def set_account_index(self, index: int):
        self.account_index = index
        if index not in self._index_color_map:
            available_colors = [c for c in self.INDEX_COLORS if c not in self._index_color_map.values()]
            if not available_colors:
                color = random.choice(self.INDEX_COLORS)
            else:
                color = random.choice(available_colors)
            self._index_color_map[index] = color

    def _format_field(self, text: str, width: int, align: str = 'left') -> str:
        if align == 'left':
            return text.ljust(width)
        elif align == 'right':
            return text.rjust(width)
        elif align == 'center':
            return text.center(width)
        return text

    def _print_to_console(self, level_name: str, message: str, account_index: int = None):
        dt_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        dt_field = self._format_field(dt_str, self.DATETIME_WIDTH, 'left')
        dt_colored = Fore.LIGHTBLACK_EX + dt_field + Style.RESET_ALL

        level_field = self._format_field(level_name, self.LEVEL_WIDTH, 'center')
        level_colored = self.LEVEL_COLOR.get(level_name, Fore.WHITE) + level_field + Style.RESET_ALL

        idx = account_index or self.account_index or "-"
        idx_field = self._format_field(str(idx), self.ACCOUNT_INDEX_WIDTH, 'center')

        index_color = self._index_color_map.get(idx, Fore.WHITE)
        index_colored = index_color + idx_field + Style.RESET_ALL

        console_line = f"{dt_colored} | {level_colored} | {index_colored} | {message}"
        print(console_line)

    def _log_message(self, level: int, message: str, account_index: int = None):
        level_name = logging.getLevelName(level)
        idx_for_file = str(account_index) if account_index is not None else (str(self.account_index) if self.account_index is not None else "-")
        file_message = f"{idx_for_file} | {message}"
        self.logger.log(level, file_message)

        self._print_to_console(level_name, message, account_index=account_index)

    def info(self, message: str, account_index: int = None):
        self._log_message(logging.INFO, message, account_index=account_index)

    def error(self, message: str, account_index: int = None):
        self._log_message(logging.ERROR, message, account_index=account_index)

    def debug(self, message: str, account_index: int = None):
        self._log_message(logging.DEBUG, message, account_index=account_index)

    def warning(self, message: str, account_index: int = None):
        self._log_message(logging.WARNING, message, account_index=account_index)

    def critical(self, message: str, account_index: int = None):
        self._log_message(logging.CRITICAL, message, account_index=account_index)

    def success(self, message: str, account_index: int = None):
        self._log_message(SUCCESS_LEVEL_NUM, message, account_index=account_index)

    def failed(self, message: str, account_index: int = None):
        self._log_message(FAILED_LEVEL_NUM, message, account_index=account_index)
