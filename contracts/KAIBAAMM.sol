// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract KAIBAAMM {
    address public owner;
    address public agentAddress;

    struct Pool {
        address tokenA;
        address tokenB;
        uint256 reserveA;
        uint256 reserveB;
        uint256 fee;           // basis points e.g. 30 = 0.3%
        bool active;
    }

    mapping(bytes32 => Pool) public pools;
    bytes32[] public poolIds;

    event PoolCreated(bytes32 indexed poolId, address tokenA, address tokenB);
    event LiquidityAdded(bytes32 indexed poolId, uint256 amountA, uint256 amountB);
    event SwapExecuted(bytes32 indexed poolId, address tokenIn, uint256 amountIn, uint256 amountOut);
    event AgentRebalance(bytes32 indexed poolId, uint256 newReserveA, uint256 newReserveB);

    modifier onlyAgent() {
        require(msg.sender == agentAddress || msg.sender == owner, "Not agent");
        _;
    }

    constructor(address _agent) {
        owner = msg.sender;
        agentAddress = _agent;
    }

    function createPool(address tokenA, address tokenB, uint256 fee) external onlyAgent returns (bytes32) {
        bytes32 poolId = keccak256(abi.encodePacked(tokenA, tokenB));
        pools[poolId] = Pool(tokenA, tokenB, 0, 0, fee, true);
        poolIds.push(poolId);
        emit PoolCreated(poolId, tokenA, tokenB);
        return poolId;
    }

    function addLiquidity(bytes32 poolId, uint256 amountA, uint256 amountB) external {
        Pool storage pool = pools[poolId];
        require(pool.active, "Pool not active");
        pool.reserveA += amountA;
        pool.reserveB += amountB;
        emit LiquidityAdded(poolId, amountA, amountB);
    }

    function getAmountOut(bytes32 poolId, bool aToB, uint256 amountIn) public view returns (uint256) {
        Pool memory pool = pools[poolId];
        uint256 reserveIn = aToB ? pool.reserveA : pool.reserveB;
        uint256 reserveOut = aToB ? pool.reserveB : pool.reserveA;
        uint256 amountInWithFee = amountIn * (10000 - pool.fee);
        return (amountInWithFee * reserveOut) / ((reserveIn * 10000) + amountInWithFee);
    }

    // Agent calls this to rebalance pool
    function agentRebalance(bytes32 poolId, uint256 newReserveA, uint256 newReserveB) external onlyAgent {
        Pool storage pool = pools[poolId];
        pool.reserveA = newReserveA;
        pool.reserveB = newReserveB;
        emit AgentRebalance(poolId, newReserveA, newReserveB);
    }

    function getPool(bytes32 poolId) external view returns (Pool memory) {
        return pools[poolId];
    }
}
