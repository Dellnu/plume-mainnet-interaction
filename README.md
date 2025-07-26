# plumeee Auto B0t - plumeee Airdrop Season 2 on mainnet
An automated trading b0t designed for the plumeee network, with capabilities including token wrapping, swapping, unwrapping, and staking. The bot supports parallel execution using ProcessPoolExecutor, featuring randomized start delays to reduce RPC node load and concurrency issues.

# Prerequisites
- **Python 3.8 or higher**
- **Stable internet connection to access plumeee RPC nodes**
- **A private_key.txt file in the root directory containing your Ethereum private keys (one per line)**
- **A configured .env file containing b0t parameters (sample provided below)**

# Key Features
- Support for multiple private key accounts `[ FREE / PRO VERSION ]`
- Wrap plumee to Wplumee and vice versa `[ FREE / PRO VERSION ]`
- Swap plumee <-> PUSD tokens via multicall `[ FREE / PRO VERSION ]`
- Swap plumee <-> pETH, WETH, USDC, USDT and vice versa `[ PRO VERSION ]`
- Swap plumee or Wplumee <-> nCREDIT, nALPHA, nELIXIR, nBASIS, nPAYFI and vice versa `[ PRO VERSION ]`
- Interaction with Relay.link and Rooster-protocol.xyz `[ FREE / PRO VERSION ]`
- Extended integration with Relay, RoosterProtocol, Ambient, Stargate, Izumi, and more `[ PRO VERSION ]`
- Automated staking on validators selected for optimal rates `[ PRO VERSION ]`
- Manual staking on specific validators `[ FREE / PRO VERSION ]`
- Cross-chain bridging from Ethereum, Arbitrum, Linea, Zero, Zora, Optimism, Binance Smart Chain, and Polygon `[ PRO VERSION ]`
- Bridging back to plumeee Network from ETH, Base, Linea, Optimism `[ PRO VERSION ]`
- Automatic daily spin and auto-use of raffle tickets on portal.plumee.org `[ PRO VERSION ]`
- Robust error handling with automatic retries `[ FREE / PRO VERSION ]`
- Randomized delays between steps and staggered start times for concurrency optimization `[ FREE / PRO VERSION ]`
- Detailed per-account and per-transaction logging `[ FREE / PRO VERSION ]`
- Graceful shutdown support on interrupt (Ctrl+C) leveraging multiprocessing events `[ FREE / PRO VERSION ]`

## Project Structure [ FREE VERSION ]
```yaml
├── main.py                 # Primary entry point to launch the b0t
├── src/
│   ├── core.py             # plumeeSwapB0t class and main logic
│   ├── logger.py           # Custom Logger module
│   ├── config.py           # Configuration and environment variable parsing
│   ├── abi.py              # Smart contract ABIs
│   └── utils.py            # Utility functions (e.g., random delays)
├── private_key.txt         # File containing one private key per line
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation (this file)
```

## Usage Instructions
### 1. Install / clone this repository:
```bash
git clone https://github.com/Dellnu/plume-mainnet-interaction.git
cd plume-mainnet-interaction
```
### 2. (Optional but recommended) Create a virtual environment:
```bash
python -m venv venv
```
Then activate the virtual environment:
#### Windows:
```bash
venv\Scripts\activate
```
#### macOS/Linux:
```bash
source venv/bin/activate
```
### 3. Install dependencies:
```bash
pip install -r requirements.txt
```
### 4. Prepare `private_key.txt`:
Store your Ethereum private keys here:
```text
0x8j64fda56d6778xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
0x8j64fda56d6778xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 5. Configure `.env` with your preferences:
```yaml
WRAP_TO_Wplume=false
UNWRAP_TO_plumee=false
SWAP_TO_PUSD=false
SWAP_PUSD_TO_Wplume=false
ENABLE_STAKING=false

AMOUNT_TO_WRAP_plume=[0.05, 0.15]
AMOUNT_TO_UNWRAP_Wplume=[0.01, 0.05]
AMOUNT_TO_SWAP_Wplumee_PUSD=[0.005, 0.01]
AMOUNT_TO_SWAP_PUSD_Wplume=[0.01, 0.05]
AMOUNT_TO_STAKE_plumee=1

MIN_PUSD_EXPECTED=0.000001
MIN_Wplume_EXPECTED=0.0000000001

STAKE_VALIDATOR_ID=3
NUM_REPETITIONS=1
SLIPPAGE_TOLERANCE=0.01

MIN_START_DELAY=5
MAX_START_DELAY=15
DELAY_BETWEEN_INTERACTIONS_SEC=[5, 10]
TX_TIMEOUT=300
MAX_RETRIES=3
RETRY_DELAY_SEC=5
WAIT_TIME_FOR_LOOP=100
MAX_WORKERS=4
```
#### Note: You can adjust these values to tailor the b0t behavior.

### 6. Run the b0t:
```bash
python main.py
```
The b0t will initiate each account's trading cycle with randomized start delays and operate in continuous looping cycles based on your configuration.

### Graceful Shutdown
The b0t supports safe interruption (Ctrl+C), terminating all threads/processes cleanly while preserving state if applicable.

## Development & Maintenance
> Modular codebase inside the src/ directory, 
> Custom Logger supports debug-level logging for detailed troubleshooting, 
> Extendable with PRO version features for advanced trading and bridging, 

## Why Upgrade to PRO Version?
Unlock the full power of plumeeSwapBot with the PRO Version and take your trading experience to the next level:

- 🚀 **Advanced Trading Pairs:** Gain access to swaps involving pETH, WETH, USDC, USDT, and exclusive token pairs like nCREDIT, nALPHA, nELIXIR, nBASIS, nPAYFI — providing deeper liquidity and better opportunities.

- 🔗 **Seamless Cross-Chain Bridges:** Easily bridge assets between Ethereum, Arbitrum, Linea, Zero, Zora, Optimism, Binance Smart Chain, Polygon, and more — all integrated for effortless multi-chain arbitrage and fund movement.

- 🤖 **Automated Validator Optimization:** Let the bot automatically select the best staking validators based on yield and performance metrics — maximize your staking rewards hands-free.

- 🎰 **Daily Automated Spin & Rewards:** Enjoy daily spinning bonus rewards and raffle tickets automation on portal.plume.org, boosting your passive income without lifting a finger!

- 🔧 **Enhanced Protocol Integrations:** Tap into Relay, RoosterProtocol, Ambient, Stargate, Izumi, and other platforms to unlock advanced defi features unavailable in the free version.

- ⚡ **Priority Support and Updates:** Get timely feature updates, optimizations, and priority support from the development team, ensuring you stay ahead in the fast-moving crypto space.

- Upgrade today and experience the unmatched power and versatility of the `plumeeSwapB0t PRO` — your trusted companion for next-level decentralized trading and staking.

# How to keep your PRO VERSION? Release Soon!

## License
This project is open-source and free to modify for personal use.
Use responsibly on live networks.
