// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract KAIBATrust {
    address public owner;

    struct Trust {
        address settlor;       // person creating trust
        address trustee;       // manager
        address beneficiary;   // receiver
        uint256 amount;
        uint256 releaseTime;   // Unix timestamp for scheduled release
        bool executed;
        string conditions;
    }

    mapping(uint256 => Trust) public trusts;
    uint256 public trustCount;

    event TrustCreated(uint256 indexed trustId, address settlor, address beneficiary, uint256 releaseTime);
    event TrustExecuted(uint256 indexed trustId, address beneficiary, uint256 amount);

    constructor() {
        owner = msg.sender;
    }

    function createTrust(
        address trustee,
        address beneficiary,
        uint256 releaseTime,
        string calldata conditions
    ) external payable returns (uint256) {
        require(releaseTime > block.timestamp, "Release must be in future");
        
        trustCount++;
        trusts[trustCount] = Trust({
            settlor: msg.sender,
            trustee: trustee,
            beneficiary: beneficiary,
            amount: msg.value,
            releaseTime: releaseTime,
            executed: false,
            conditions: conditions
        });

        emit TrustCreated(trustCount, msg.sender, beneficiary, releaseTime);
        return trustCount;
    }

    // Called by agent or Hedera Scheduled Service execution
    function executeTrust(uint256 trustId) external {
        Trust storage t = trusts[trustId];
        require(!t.executed, "Already executed");
        require(block.timestamp >= t.releaseTime, "Not yet time");
        require(msg.sender == t.trustee || msg.sender == owner, "Unauthorized");
        
        t.executed = true;
        payable(t.beneficiary).transfer(t.amount);
        emit TrustExecuted(trustId, t.beneficiary, t.amount);
    }

    function getTrust(uint256 trustId) external view returns (Trust memory) {
        return trusts[trustId];
    }
}
