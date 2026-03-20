// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title KAIBASaucerSwap
 * @dev Integration contract to seamlessly route user / treasury liquidity directly into SaucerSwap (the leading DEX on Hedera).
 * Uses the Hedera Token Service (HTS) to manage Token A + Token B and interact with the SaucerSwap V2 Router.
 * Built for the Hedera Hackathon.
 */

interface ISaucerSwapRouter {
    /**
     * @dev Adds liquidity to an ERC-20⇄ERC-20 pool.
     */
    function addLiquidity(
        address tokenA,
        address tokenB,
        uint amountADesired,
        uint amountBDesired,
        uint amountAMin,
        uint amountBMin,
        address to,
        uint deadline
    ) external returns (uint amountA, uint amountB, uint liquidity);

    /**
     * @dev Adds liquidity to an ERC-20⇄HBAR pool.
     */
    function addLiquidityHBAR(
        address token,
        uint amountTokenDesired,
        uint amountTokenMin,
        uint amountHBARMin,
        address to,
        uint deadline
    ) external payable returns (uint amountToken, uint amountHBAR, uint liquidity);
}

interface IERC20 {
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
}

contract KAIBASaucerSwap {
    address public owner;

    // Hedera Testnet SaucerSwap Router V2 address
    address public constant SAUCERSWAP_ROUTER = 0x000000000000000000000000000000000005F9A6;
    ISaucerSwapRouter public router;

    event LiquidityAddedHBAR(address indexed provider, address token, uint amountToken, uint amountHBAR, uint liquidityTokens);
    event LiquidityAddedTokens(address indexed provider, address tokenA, address tokenB, uint liquidityTokens);

    modifier onlyOwner() {
        require(msg.sender == owner, "KAIBA: Not Authorized");
        _;
    }

    constructor(address _routerAddress) {
        owner = msg.sender;
        router = ISaucerSwapRouter(_routerAddress != address(0) ? _routerAddress : SAUCERSWAP_ROUTER);
    }

    /**
     * @dev Supplies Token + Native HBAR to SaucerSwap.
     * Takes Token from the user, requires them to send msg.value HBAR concurrently.
     */
    function provideLiquidityHBAR(
        address token,
        uint amountTokenDesired,
        uint amountTokenMin,
        uint amountHBARMin,
        uint deadline
    ) external payable {
        require(msg.value > 0, "KAIBA: Must send native HBAR");
        require(amountTokenDesired > 0, "KAIBA: Must send tokens");

        // 1. Transfer the token from user to this integration contract
        // (User must have called Hedera Token Associate and ERC20 approve first)
        IERC20(token).transferFrom(msg.sender, address(this), amountTokenDesired);

        // 2. Approve SaucerSwap Router to sweep the token
        IERC20(token).approve(address(router), amountTokenDesired);

        // 3. Deposit to SaucerSwap Liquidity Pool
        (uint amountTokenAdded, uint amountHBARAdded, uint liquidity) = router.addLiquidityHBAR{value: msg.value}(
            token,
            amountTokenDesired,
            amountTokenMin,
            amountHBARMin,
            msg.sender, // The LP tokens go directly back to the user's wallet
            deadline
        );

        // 4. Refund unspent native HBAR (if any slippage occurred)
        if (msg.value > amountHBARAdded) {
            (bool success, ) = msg.sender.call{value: msg.value - amountHBARAdded}("");
            require(success, "KAIBA: HBAR Refund Failed");
        }

        emit LiquidityAddedHBAR(msg.sender, token, amountTokenAdded, amountHBARAdded, liquidity);
    }

    /**
     * @dev Supplies Token A + Token B to SaucerSwap.
     */
    function provideLiquidityTokens(
        address tokenA,
        address tokenB,
        uint amountADesired,
        uint amountBDesired,
        uint amountAMin,
        uint amountBMin,
        uint deadline
    ) external {
        
        // 1. Transfer both tokens into the contract
        IERC20(tokenA).transferFrom(msg.sender, address(this), amountADesired);
        IERC20(tokenB).transferFrom(msg.sender, address(this), amountBDesired);

        // 2. Infinite approve the Router
        IERC20(tokenA).approve(address(router), amountADesired);
        IERC20(tokenB).approve(address(router), amountBDesired);

        // 3. Provide liquidity via SaucerSwap
        (,, uint liquidity) = router.addLiquidity(
            tokenA,
            tokenB,
            amountADesired,
            amountBDesired,
            amountAMin,
            amountBMin,
            msg.sender,
            deadline
        );

        emit LiquidityAddedTokens(msg.sender, tokenA, tokenB, liquidity);
    }

    // Accept HBAR directly
    receive() external payable {}
}
