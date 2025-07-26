import os
import random
from dotenv import load_dotenv
from .utils import _parse_random_value

load_dotenv()

settings = {
    "RPC_URL": os.getenv("RPC_URL", "https://rpc.plume.org"),
    "EXPLORER_URL": os.getenv("EXPLORER_URL", "https://explorer.plume.org/address/0x"),
    "WPLUME_ADDRESS": os.getenv("WPLUME_ADDRESS", "0xEa237441c92CAe6FC17Caaf9a7acB3f953be4bd1"),
    "PUSD_ADDRESS": os.getenv("PUSD_ADDRESS", "0xdddd73f5df1f0dc31373357beac77545dc5a6f3f"),
    
    "PERMIT_ROUTER_ADDRESS": os.getenv("PERMIT_ROUTER_ADDRESS", "0x000000000022D473030F116dDEE9F6B43aC78BA3"),
    "SWAP_ROUTER_ADDRESS": os.getenv("SWAP_ROUTER_ADDRESS", "0x35e44dc4702Fd51744001E248B49CBf9fcc51f0C"),
    "RELAY_ROUTER_ADDRESS": os.getenv("RELAY_ROUTER_ADDRESS", "0xF5042e6fFAC5A625d4e7848E0b01373D8Eb9E222"),
    "APPROVAL_PROXY_ADDRESS": os.getenv("APPROVAL_PROXY_ADDRESS", "0xBBbfD134E9b44BfB5123898BA36b01dE7ab93d98"),
    "MAVERICK_POOL_WPLUME_PUSD": os.getenv("MAVERICK_POOL_WPLUME_PUSD", "0x39ba3C1Dbe665452E86fde9C71FC64C78aa2445C"),
    "PLUME_STAKING_CONTRACT_ADDRESS": os.getenv("PLUME_STAKING_CONTRACT_ADDRESS", "0x30c791E4654EdAc575FA1700eD8633CB2FEDE871"),

    "AMOUNT_TO_WRAP_PLUME": _parse_random_value(os.getenv("AMOUNT_TO_WRAP_PLUME", "0.01")),
    "AMOUNT_TO_UNWRAP_WPLUME": _parse_random_value(os.getenv("AMOUNT_TO_UNWRAP_WPLUME", "0.01")),
    "AMOUNT_TO_SWAP_WPLUME_PUSD": _parse_random_value(os.getenv("AMOUNT_TO_SWAP_WPLUME_PUSD", "0.01")),
    "AMOUNT_TO_SWAP_PUSD_WPLUME": _parse_random_value(os.getenv("AMOUNT_TO_SWAP_PUSD_WPLUME", "0.01")),
    "AMOUNT_TO_STAKE_PLUME": _parse_random_value(os.getenv("AMOUNT_TO_STAKE_PLUME", "0.01")),
    "MIN_PUSD_EXPECTED": _parse_random_value(os.getenv("MIN_PUSD_EXPECTED", "0.012")),
    "MIN_WPLUME_EXPECTED": _parse_random_value(os.getenv("MIN_WPLUME_EXPECTED", "0.009")),
    "SLIPPAGE_TOLERANCE": _parse_random_value(os.getenv("SLIPPAGE_TOLERANCE", "0.01")),
    "DELAY_BETWEEN_INTERACTIONS_SEC": _parse_random_value(os.getenv("DELAY_BETWEEN_INTERACTIONS_SEC", "10")),
    "DELAY_START_BOT": _parse_random_value(os.getenv("DELAY_START_BOT", "0.009")),    

    "NUM_REPETITIONS": int(os.getenv("NUM_REPETITIONS", "1")),
    "WRAP_TO_WPLUME": os.getenv("WRAP_TO_WPLUME", "False").lower() == 'true',
    "UNWRAP_TO_PLUME": os.getenv("UNWRAP_TO_PLUME", "False").lower() == 'true',
    "SWAP_TO_PUSD": os.getenv("SWAP_TO_PUSD", "True").lower() == 'true',
    "SWAP_PUSD_TO_WPLUME": os.getenv("SWAP_PUSD_TO_WPLUME", "True").lower() == 'true',
    "ENABLE_STAKING": os.getenv("ENABLE_STAKING", "True").lower() == 'true',

    "STAKE_VALIDATOR_ID": int(os.getenv("STAKE_VALIDATOR_ID", "1")),
    "TX_TIMEOUT": int(os.getenv("TX_TIMEOUT", "300")),
    "MAX_RETRIES": int(os.getenv("MAX_RETRIES", "3")),
    "MAX_WORKERS": int(os.getenv("MAX_WORKERS", "3")),
    "RETRY_DELAY_SEC": _parse_random_value(os.getenv("RETRY_DELAY_SEC", "5")),
    "WAIT_TIME_FOR_LOOP": _parse_random_value(os.getenv("WAIT_TIME_FOR_LOOP", "5")),
    "MIN_START_DELAY": _parse_random_value(os.getenv("MIN_START_DELAY", 0)),
    "MAX_START_DELAY": _parse_random_value(os.getenv("MAX_START_DELAY", 30)),
}