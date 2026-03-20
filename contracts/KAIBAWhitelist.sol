// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract KAIBAWhitelist {
    address public owner;
    mapping(address => bool) public whitelisted;
    mapping(address => uint256) public lastAirdrop;
    address[] public members;

    event Whitelisted(address indexed user);
    event AirdropClaimed(address indexed user, uint256 timestamp);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function addToWhitelist(address user) external onlyOwner {
        if (!whitelisted[user]) {
            whitelisted[user] = true;
            members.push(user);
            emit Whitelisted(user);
        }
    }

    function removeFromWhitelist(address user) external onlyOwner {
        whitelisted[user] = false;
    }

    function isWhitelisted(address user) external view returns (bool) {
        return whitelisted[user];
    }

    function recordAirdrop(address user) external onlyOwner {
        lastAirdrop[user] = block.timestamp;
        emit AirdropClaimed(user, block.timestamp);
    }

    function canClaimAirdrop(address user) external view returns (bool) {
        return whitelisted[user] && (block.timestamp - lastAirdrop[user]) >= 86400;
    }

    function getAllMembers() external view returns (address[] memory) {
        return members;
    }
}
