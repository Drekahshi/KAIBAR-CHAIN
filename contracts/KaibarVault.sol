// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title KaibarVault
 * @dev A simple vault contract that accepts HBAR and simulates yield.
 * This is used for the Hedera Hackathon to showcase smart contract integration.
 */
contract KaibarVault {
    address public owner;
    uint256 public totalDeposits;
    mapping(address => uint256) public balances;
    mapping(address => uint256) public lastDepositTime;

    // Simulation of Yield (APY)
    uint256 public constant APY = 5; // 5% simulated yield

    event Deposit(address indexed user, uint256 amount);
    event Withdraw(address indexed user, uint256 amount);

    constructor() {
        owner = msg.sender;
    }

    /**
     * @dev Deposit HBAR into the vault.
     */
    function deposit() external payable {
        require(msg.value > 0, "Amount must be greater than zero");
        
        // Before updating, we could calculate yield here (mock)
        balances[msg.sender] += msg.value;
        totalDeposits += msg.value;
        lastDepositTime[msg.sender] = block.timestamp;

        emit Deposit(msg.sender, msg.value);
    }

    /**
     * @dev Withdraw HBAR from the vault.
     */
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        balances[msg.sender] -= amount;
        totalDeposits -= amount;
        
        payable(msg.sender).transfer(amount);

        emit Withdraw(msg.sender, amount);
    }

    /**
     * @dev Get the balance of the caller.
     */
    function getBalance() external view returns (uint256) {
        return balances[msg.sender];
    }

    /**
     * @dev Mock function to show simulated yield based on time.
     */
    function calculateSimulatedYield(address user) public view returns (uint256) {
        if (balances[user] == 0) return 0;
        
        uint256 duration = block.timestamp - lastDepositTime[user];
        // yieldVal = (balance * APY * duration) / (365 days * 100)
        uint256 yieldVal = (balances[user] * APY * duration) / (365 days * 100);
        return yieldVal;
    }

    // Function to allow owner to withdraw (for emergency, but for hackathon demo)
    function emergencyWithdraw() external {
        require(msg.sender == owner, "Only owner can withdraw");
        payable(owner).transfer(address(this).balance);
    }

    receive() external payable {
        // Handle direct transfers
    }
}
