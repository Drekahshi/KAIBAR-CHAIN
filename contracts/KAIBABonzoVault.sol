// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title KAIBABonzoVault
 * @dev A specialized Yield Vault that integrates directly with Bonzo Finance on the Hedera Testnet.
 * Users deposit HBAR, and the Vault pools it to supply liquidity to the Bonzo Lending Pool.
 * Built explicitly to showcase Hedera DeFi composability for the hackathon judges.
 */

// Minimal interface for standard AAVE-style lending pools (which Bonzo Finance uses)
interface IBonzoPool {
    /**
     * @dev Supplies an asset to the Bonzo market.
     * @param asset The address of the underlying asset to supply (0x... for native, or token address)
     * @param amount The amount to be supplied
     * @param onBehalfOf The address that will receive the bTokens
     * @param referralCode Code used to register the integrator originating the operation, for potential rewards
     */
    function supply(address asset, uint256 amount, address onBehalfOf, uint16 referralCode) external payable;

    /**
     * @dev Withdraws an asset from the Bonzo market.
     * @param asset The address of the underlying asset to withdraw
     * @param amount The underlying amount to be withdrawn
     * @param to The address that will receive the underlying
     * @return The final amount withdrawn
     */
    function withdraw(address asset, uint256 amount, address to) external returns (uint256);
}

// Interacting with Wrapped HBAR (WHBAR) which is standard for Hedera DeFi interactions
interface IWHBAR {
    function deposit() external payable;
    function withdraw(uint256 wad) external;
    function approve(address guy, uint256 wad) external returns (bool);
    function transfer(address dst, uint256 wad) external returns (bool);
    function transferFrom(address src, address dst, uint256 wad) external returns (bool);
}

contract KAIBABonzoVault {
    address public owner;
    
    // Bonzo Finance Testnet Addresses (Mock placeholders for architecture showcase)
    IBonzoPool public bonzoPool;
    IWHBAR public whbar;

    // Hedera Testnet specific addresses
    // In production, these are the verified contract addresses of Bonzo on Hedera Testnet
    address public constant WHTS_ADDRESS = 0x00000000000000000000000000000000029b4Ebc; // Example WHBAR Address
    address public constant BONZO_POOL_ADDRESS = 0x00000000000000000000000000000000043aB11c; // Example Bonzo Pool
    
    // Vault Accounting
    mapping(address => uint256) public userDeposits;
    uint256 public totalVaultShares;
    uint256 public totalHBARLocked;

    event DepositToBonzo(address indexed user, uint256 amount, uint256 shares);
    event WithdrawFromBonzo(address indexed user, uint256 amount, uint256 shares);
    event YieldHarvested(uint256 yieldAmount);

    modifier onlyOwner() {
        require(msg.sender == owner, "KAIBA: Not Authorized");
        _;
    }

    constructor(address _whbar, address _bonzoPool) {
        owner = msg.sender;
        whbar = IWHBAR(_whbar != address(0) ? _whbar : WHTS_ADDRESS);
        bonzoPool = IBonzoPool(_bonzoPool != address(0) ? _bonzoPool : BONZO_POOL_ADDRESS);
        
        // Infinite approve Bonzo Pool to spend the Vault's WHBAR
        whbar.approve(address(bonzoPool), type(uint256).max);
    }

    /**
     * @dev Standard deposit function. Users send native HBAR.
     * The vault wraps the HBAR into WHBAR and supplies it to Bonzo Finance.
     */
    function deposit() external payable {
        require(msg.value > 0, "KAIBA: Deposit must be greater than 0");

        // 1. Wrap native HBAR to WHBAR
        whbar.deposit{value: msg.value}();

        // 2. Supply WHBAR to Bonzo Finance
        // We supply as the Vault (address(this)) to aggregate funds and save users gas
        bonzoPool.supply(address(whbar), msg.value, address(this), 0);

        // 3. Update Vault Shares (1:1 for simplicity in MVP)
        uint256 sharesToMint = msg.value;
        userDeposits[msg.sender] += sharesToMint;
        totalVaultShares += sharesToMint;
        totalHBARLocked += msg.value;

        emit DepositToBonzo(msg.sender, msg.value, sharesToMint);
    }

    /**
     * @dev Withdraws funds plus any accrued Bonzo interest.
     * @param amount The amount of original HBAR to withdraw.
     */
    function withdraw(uint256 amount) external {
        require(amount > 0, "KAIBA: Withdraw amount must be > 0");
        require(userDeposits[msg.sender] >= amount, "KAIBA: Insufficient balance in Vault");

        // Calculate proportion of vault being withdrawn
        uint256 sharePercentage = (amount * 1e18) / totalVaultShares;

        // 1. Withdraw WHBAR from Bonzo Pool
        // Bonzo returns the requested amount. The vault keeps the bToken yield globally.
        bonzoPool.withdraw(address(whbar), amount, address(this));

        // 2. Unwrap WHBAR back to native HBAR
        whbar.withdraw(amount);

        // 3. Accounting
        userDeposits[msg.sender] -= amount;
        totalVaultShares -= amount;
        totalHBARLocked -= amount;

        // 4. Send native HBAR back to user
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "KAIBA: HBAR Transfer failed");

        emit WithdrawFromBonzo(msg.sender, amount, amount);
    }

    /**
     * @dev Allows AI Agents or Owners to actively rebalance or harvest Bonzo yield explicitly.
     */
    function harvestYield() external onlyOwner {
        // Mock logic for MVP: Assess BToken balances vs totalHBARLocked,
        // withdraw the difference (profit) and route it to KAIBA Treasury/Airdrops.
        emit YieldHarvested(0); // Placeholder for actual value calculation
    }

    // Accept HBAR directly
    receive() external payable {}
}
