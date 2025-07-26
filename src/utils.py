import json, random, base64
from src.logger import Logger
from colorama import Fore, Style, init

init(autoreset=True)

def plume_mainnet_banner_v2():
    banner_art = r"""
 █████  ██ ██████  ██████        ███████ ███████ ██████  ██    ██ 
██   ██ ██ ██   ██ ██   ██       ██      ██      ██   ██ ██    ██ 
███████ ██ ██████  ██   ██ █████ ███████ █████   ██████  ██    ██ 
██   ██ ██ ██   ██ ██   ██            ██ ██      ██   ██  ██  ██  
██   ██ ██ ██   ██ ██████        ███████ ███████ ██   ██   ████                                                                     
==============[ PLUME MAINNET :: SEASON 2 ]================                                               
"""
    print(Fore.CYAN + Style.BRIGHT + banner_art + Style.RESET_ALL)
    print(f"{Fore.YELLOW}>> A Project by {Style.BRIGHT}AirdropServices {Fore.GREEN}[FREE VERSION]{Style.NORMAL} {Style.RESET_ALL}")
    print(f"{Fore.WHITE}>> Blockchain & Crypto Automation Specialist{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}Source: https://github.com/airdropservices/plumee-mainnet-services{Style.RESET_ALL}\n")
    print(Fore.MAGENTA + "-----------------------------------------------------------------------" + Style.RESET_ALL)
    print(f"{Fore.BLUE}  Status: {Style.BRIGHT}ACTIVE{Style.NORMAL} | Phase: {Style.BRIGHT}Mainnet Airdrop{Style.NORMAL} {Style.RESET_ALL}")
    print(Fore.MAGENTA + "-----------------------------------------------------------------------" + Style.RESET_ALL)

def str_to_bool(val):
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.strip().lower() in ['true', '1', 'yes']
    return False

def _parse_random_value(value_str, default=5.0):
    if isinstance(value_str, (int, float)):
        return float(value_str)

    if isinstance(value_str, str):
        value_str = value_str.strip()
        if value_str.startswith('[') and value_str.endswith(']'):
            try:
                parts = value_str.strip('[]').split(',')
                min_val = float(parts[0].strip())
                max_val = float(parts[1].strip())
                if min_val > max_val:
                    min_val, max_val = max_val, min_val
                return random.uniform(min_val, max_val)
            except (ValueError, IndexError):
                Logger.warning(f"Invalid range format: '{value_str}'. Using default: {default}")
                return default

        try:
            return float(value_str)
        except (ValueError, TypeError):
            Logger.warning(f"Invalid float value: '{value_str}'. Using default: {default}")
            return default

    Logger.warning(f"Unsupported value type: {type(value_str)}. Using default: {default}")
    return default

def _uni_random(min_value, max_value, decimals=2):
    if min_value > max_value:
        min_value, max_value = max_value, min_value
    return round(random.uniform(min_value, max_value), decimals)
