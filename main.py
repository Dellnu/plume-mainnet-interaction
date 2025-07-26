import random, os, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Event, Manager

from src.config import settings
from src.core import PlumeSwapBot
from src.logger import Logger
from src import utils as _utls

def run_bot_for_account(parameter, account_idx, min_delay, max_delay, stop_flag):
    local_logger = Logger()
    delay_seconds = random.uniform(min_delay, max_delay)
    local_logger.info(f"Account {account_idx} will start trading after delay of {delay_seconds:.2f} seconds.", account_index=account_idx)
    
    waited = 0
    while waited < delay_seconds:
        if stop_flag.is_set():
            local_logger.warning(f"Account {account_idx} start delay interrupted by stop signal. Aborting.", account_index=account_idx)
            return
        time.sleep(0.5)
        waited += 0.5

    try:
        bot_instance = PlumeSwapBot(parameter=parameter, account_index=account_idx)
        bot_instance.execute_trade()
        local_logger.success(f"Bot successfully completed its trading cycle for Account {account_idx}.", account_index=account_idx)
    
    except KeyboardInterrupt:
        stop_flag.set()
    except Exception as e:
        local_logger.critical(f"A critical error occurred for Account {account_idx}, skipping: {e}", account_index=account_idx)

if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    _utls.plume_mainnet_banner_v2()
    main_logger = Logger()
    parameter_list = PlumeSwapBot._load_parameter_keys("private_key.txt")

    if not parameter_list:
        main_logger.critical("No private keys found in private_key.txt. Exiting program.")
        sys.exit(1)

    max_workers = int(settings.get("MAX_WORKERS", 4))
    WAIT_TIME_FOR_LOOP = float(settings.get("WAIT_TIME_FOR_LOOP", 3600))
    MIN_START_DELAY = float(settings.get("MIN_START_DELAY", 0))
    MAX_START_DELAY = float(settings.get("MAX_START_DELAY", 30))

    with Manager() as manager:
        stop_flag = manager.Event()

        main_logger.info(f"Starting bot for {len(parameter_list)} accounts with max {max_workers} concurrent workers.")

        while True:
            stop_flag.clear()
            try:
                with ProcessPoolExecutor(max_workers=max_workers) as executor:
                    futures = []
                    for idx, key in enumerate(parameter_list):
                        account_idx = idx + 1
                        futures.append(
                            executor.submit(run_bot_for_account, key, account_idx, MIN_START_DELAY, MAX_START_DELAY, stop_flag)
                        )

                    for future in as_completed(futures):
                        try:
                            future.result()
                        except KeyboardInterrupt:
                            main_logger.warning("KeyboardInterrupt caught in a process. Setting stop flag and exiting.")
                            stop_flag.set()
                            executor.shutdown(wait=False)
                            sys.exit(0)
                        except Exception as e:
                            main_logger.critical(f"Exception in bot process: {e}")

            except KeyboardInterrupt:
                main_logger.warning("KeyboardInterrupt caught in main loop. Setting stop flag and exiting.")
                stop_flag.set()
                sys.exit(0)

            main_logger.info(f"All accounts processed in this cycle. Waiting {WAIT_TIME_FOR_LOOP} seconds before next loop.")
            waited = 0
            while waited < WAIT_TIME_FOR_LOOP:
                if stop_flag.is_set():
                    main_logger.warning("Stop signal received during global wait. Exiting.")
                    sys.exit(0)
                time.sleep(1)
                waited += 1
