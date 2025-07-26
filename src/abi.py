WPLUME_ABI = [
    {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "", "type": "bool"}], "stateMutability": "nonpayable", "type": "function"},
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "stateMutability": "view", "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "stateMutability": "view", "type": "function"},
    {"inputs": [], "name": "deposit", "outputs": [], "stateMutability": "payable", "type": "function"},
    {"inputs": [{"internalType": "uint256", "name": "wad", "type": "uint256"}], "name": "withdraw", "outputs": [], "stateMutability": "nonpayable", "type": "function"}
]

ERC20_ABI = [
    {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
    {
        "inputs": [
            {"internalType": "address", "name": "owner", "type": "address"},
            {"internalType": "address", "name": "spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "spender", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]
PUSD_ABI = ERC20_ABI

RELAY_ROUTER_ABI = [
    {
        "inputs": [
            { "components": [
                { "internalType": "address", "name": "target", "type": "address" },
                { "internalType": "bool", "name": "allowFailure", "type": "bool" },
                { "internalType": "uint256", "name": "value", "type": "uint256" },
                { "internalType": "bytes", "name": "callData", "type": "bytes" }
            ], "internalType": "struct Call3Value[]", "name": "calls", "type": "tuple[]" },
            { "internalType": "address", "name": "refundTo", "type": "address" },
            { "internalType": "address", "name": "nftRecipient", "type": "address" }
        ],
        "name": "multicall",
        "outputs": [
            { "components": [
                { "internalType": "bool", "name": "success", "type": "bool" },
                { "internalType": "bytes", "name": "returnData", "type": "bytes" }
            ], "internalType": "struct Result[]", "name": "returnData", "type": "tuple[]" }
        ],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address[]", "name": "tokens", "type": "address[]"},
            {"internalType": "address[]", "name": "recipients", "type": "address[]"},
            {"internalType": "uint256[]", "name": "minimumAmounts", "type": "uint256[]"}
        ],
        "name": "cleanupErc20s",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

MAVERICK_V2_ROUTER_ABI = [
    {
        "inputs": [
            { "internalType": "address", "name": "recipient", "type": "address" },
            { "internalType": "address", "name": "pool", "type": "address" },
            { "internalType": "bool", "name": "tokenAIn", "type": "bool" },
            { "internalType": "uint256", "name": "amountIn", "type": "uint256" },
            { "internalType": "uint256", "name": "amountOutMinimum", "type": "uint256" }
        ],
        "name": "exactInputSingle",
        "outputs": [
            { "internalType": "uint256", "name": "amountOut", "type": "uint256" }
        ],
        "stateMutability": "payable",
        "type": "function" 
    },
    { 
        "inputs": [
            {"internalType": "bytes[]", "name": "data", "type": "bytes[]"}
        ],
        "name": "multicall",
        "outputs": [
            {"internalType": "bytes[]", "name": "results", "type": "bytes[]"}
        ],
        "stateMutability": "nonpayable", 
        "type": "function"
    }
]

MAVERICK_V2_POOL_ABI = [
    {
        "inputs": [],
        "name": "tokenA",
        "outputs": [
            {"internalType": "contract IERC20", "name": "", "type": "address"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "tokenB",
        "outputs": [
            {"internalType": "contract IERC20", "name": "", "type": "address"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {"internalType": "uint8", "name": "", "type": "uint8"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

APPROVAL_PROXY_ABI = [
    {
        "inputs": [
            { "internalType": "address[]", "name": "tokens", "type": "address[]" },
            { "internalType": "uint256[]", "name": "amounts", "type": "uint256[]" },
            { "components": [
                { "internalType": "address", "name": "target", "type": "address" },
                { "internalType": "bool", "name": "allowFailure", "type": "bool" },
                { "internalType": "uint256", "name": "value", "type": "uint256" },
                { "internalType": "bytes", "name": "callData", "type": "bytes" }
            ], "internalType": "struct Call3Value[]", "name": "calls", "type": "tuple[]" },
            { "internalType": "address", "name": "refundTo", "type": "address" },
            { "internalType": "address", "name": "nftRecipient", "type": "address" }
        ],
        "name": "transferAndMulticall",
        "outputs": [
            { "internalType": "bytes[]", "name": "returnData", "type": "bytes[]" }
        ],
        "stateMutability": "payable",
        "type": "function"
    }
]

PLUME_STAKING_ABI = [
    {
        "inputs": [
            {
                "internalType": "uint16",
                "name": "validatorId",
                "type": "uint16"
            }
        ],
        "name": "stake",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
]