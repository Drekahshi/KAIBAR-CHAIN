// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title KAIBAMoneyMarket
 * @dev Vault-based money market fund for Algorithmic yield optimisation managed by vault agents.
 */
contract KAIBAMoneyMarket {
    address public owner;
    address public agentAddress;

    struct MarketPosition {
        uint256 principal;
        uint256 entryTime;
        uint256 currentYield; // Tracks accrued yield from rebalances
    }

    mapping(address => MarketPosition) public positions;
    uint256 public totalLiquidity;
    uint256 public currentMarketApy;

    event Deposit(address indexed user, uint256 amount);
    event Withdraw(address indexed user, uint256 amount, uint256 earnedYield);
    event YieldRebalanced(uint256 newApy, uint256 timestamp);

    modifier onlyAgent() {
        require(msg.sender == owner || msg.sender == agentAddress, "Not authorized");
        _;
    }

    constructor(address _agentAddress) {
        owner = msg.sender;
        agentAddress = _agentAddress;
        currentMarketApy = 1800; // 18% base APY
    }

    function deposit() external payable {
        require(msg.value > 0, "Amount must be > 0");
        
        MarketPosition storage pos = positions[msg.sender];
        
        // If already invested, we'd normally accrue yield first here
        // For MVP, simplistic addition
        pos.principal += msg.value;
        if (pos.entryTime == 0) {
            pos.entryTime = block.timestamp;
        }

        totalLiquidity += msg.value;
        emit Deposit(msg.sender, msg.value);
    }

    function withdraw(uint256 amount) external {
        MarketPosition storage pos = positions[msg.sender];
        require(pos.principal >= amount, "Insufficient principal");

        // Calculate simple yield proportional to time spent
        uint256 timeInvested = block.timestamp - pos.entryTime;
        uint256 earnedYield = (amount * currentMarketApy * timeInvested) / (365 days * 10000);

        pos.principal -= amount;
        // Reset entry time if fully withdrawn
        if (pos.principal == 0) {
            pos.entryTime = 0;
            pos.currentYield = 0;
        }

        totalLiquidity -= amount;
        uint256 totalPayout = amount + earnedYield;
        
        payable(msg.sender).transfer(totalPayout);
        emit Withdraw(msg.sender, amount, earnedYield);
    }

    function agentRebalanceYield(uint256 newApy) external onlyAgent {
        currentMarketApy = newApy;
        emit YieldRebalanced(newApy, block.timestamp);
    }

    // Allow fund injection for yield payments
    receive() external payable {}
}
