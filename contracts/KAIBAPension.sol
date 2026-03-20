// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract KAIBAPension {
    address public owner;

    struct PensionAccount {
        address holder;
        uint256 balance;
        uint256 startTime;
        uint256 lockupPeriod;     // in seconds (e.g., 5 years = 157680000)
        uint256 apy;              // basis points
        bool active;
    }

    mapping(address => PensionAccount) public accounts;

    event PensionOpened(address indexed holder, uint256 amount, uint256 lockupYears);
    event PensionClaimed(address indexed holder, uint256 total);

    constructor() {
        owner = msg.sender;
    }

    function openPension(uint256 lockupYears) external payable {
        require(msg.value > 0, "Must deposit > 0");
        require(lockupYears >= 1, "Minimum 1 year lockup");

        uint256 apy = 1500 + (lockupYears * 100); // 15% + 1% per year bonus

        accounts[msg.sender] = PensionAccount({
            holder: msg.sender,
            balance: msg.value,
            startTime: block.timestamp,
            lockupPeriod: lockupYears * 365 * 86400,
            apy: apy,
            active: true
        });

        emit PensionOpened(msg.sender, msg.value, lockupYears);
    }

    function claimPension() external {
        PensionAccount storage acc = accounts[msg.sender];
        require(acc.active, "No active pension");
        require(block.timestamp >= acc.startTime + acc.lockupPeriod, "Still locked");

        uint256 years = acc.lockupPeriod / (365 * 86400);
        uint256 yieldAmount = (acc.balance * acc.apy * years) / 10000;
        uint256 total = acc.balance + yieldAmount;
        acc.active = false;
        
        payable(msg.sender).transfer(total);
        emit PensionClaimed(msg.sender, total);
    }

    function getAccount(address holder) external view returns (PensionAccount memory) {
        return accounts[holder];
    }
}
