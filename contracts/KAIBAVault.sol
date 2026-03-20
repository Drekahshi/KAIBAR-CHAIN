// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IHTS {
    function transferToken(address token, address sender, address receiver, int64 amount) external returns (int64);
}

contract KAIBAVault {
    address public owner;
    address public agentAddress;
    
    struct VaultPosition {
        uint256 deposited;
        uint256 shares;
        uint256 depositTime;
    }

    mapping(address => VaultPosition) public positions;
    mapping(address => uint256) public tokenBalances;
    
    uint256 public totalShares;
    uint256 public currentAPY;
    uint256 public lastRebalance;
    
    string public vaultName;
    string public vaultType; // "yield", "liquidity", "moneymarket"

    event Deposited(address indexed user, uint256 amount, uint256 shares);
    event Withdrawn(address indexed user, uint256 amount);
    event Rebalanced(uint256 newAPY, uint256 timestamp);
    event AgentAction(string action, uint256 timestamp);

    modifier onlyOwnerOrAgent() {
        require(msg.sender == owner || msg.sender == agentAddress, "Unauthorized");
        _;
    }

    constructor(string memory _name, string memory _type, address _agent) {
        owner = msg.sender;
        vaultName = _name;
        vaultType = _type;
        agentAddress = _agent;
        currentAPY = 1200; // 12% APY in basis points
    }

    function deposit(uint256 amount) external {
        require(amount > 0, "Amount must be > 0");
        uint256 shares = totalShares == 0 ? amount : (amount * totalShares) / getTotalValue();
        positions[msg.sender].deposited += amount;
        positions[msg.sender].shares += shares;
        positions[msg.sender].depositTime = block.timestamp;
        totalShares += shares;
        emit Deposited(msg.sender, amount, shares);
    }

    function withdraw(uint256 shares) external {
        require(positions[msg.sender].shares >= shares, "Insufficient shares");
        uint256 amount = (shares * getTotalValue()) / totalShares;
        positions[msg.sender].shares -= shares;
        totalShares -= shares;
        emit Withdrawn(msg.sender, amount);
    }

    function rebalance(uint256 newAPY) external onlyOwnerOrAgent {
        currentAPY = newAPY;
        lastRebalance = block.timestamp;
        emit Rebalanced(newAPY, block.timestamp);
    }

    function agentExecute(string calldata action) external onlyOwnerOrAgent {
        emit AgentAction(action, block.timestamp);
    }

    function getTotalValue() public view returns (uint256) {
        return totalShares > 0 ? totalShares : 1;
    }

    function getPosition(address user) external view returns (uint256 deposited, uint256 shares, uint256 depositTime) {
        VaultPosition memory p = positions[user];
        return (p.deposited, p.shares, p.depositTime);
    }
}
