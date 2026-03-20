// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract KAIBAInsurance {
    address public owner;
    
    struct Policy {
        address holder;
        uint256 stakedAmount;
        uint256 coverageAmount;
        uint256 premium;       // APY-funded premium
        uint256 startTime;
        uint256 endTime;
        bool active;
    }

    mapping(address => Policy) public policies;
    mapping(address => uint256) public stakedBalances;

    event PolicyCreated(address indexed holder, uint256 coverage, uint256 startTime);
    event PremiumPaid(address indexed holder, uint256 amount, uint256 timestamp);
    event PolicyClaimed(address indexed holder, uint256 payout);

    constructor() {
        owner = msg.sender;
    }

    // Stake tokens and create an insurance policy funded by APY
    function stakeAndInsure(uint256 stakeAmount, uint256 durationDays) external {
        require(stakeAmount > 0, "Must stake > 0");
        uint256 coverage = stakeAmount * 2;
        uint256 duration = durationDays * 86400;
        
        stakedBalances[msg.sender] += stakeAmount;
        policies[msg.sender] = Policy({
            holder: msg.sender,
            stakedAmount: stakeAmount,
            coverageAmount: coverage,
            premium: (stakeAmount * 12) / 100, // 12% APY as premium
            startTime: block.timestamp,
            endTime: block.timestamp + duration,
            active: true
        });

        emit PolicyCreated(msg.sender, coverage, block.timestamp);
    }

    function getPolicy(address holder) external view returns (Policy memory) {
        return policies[holder];
    }

    function isPolicyActive(address holder) external view returns (bool) {
        Policy memory p = policies[holder];
        return p.active && block.timestamp <= p.endTime;
    }
}
