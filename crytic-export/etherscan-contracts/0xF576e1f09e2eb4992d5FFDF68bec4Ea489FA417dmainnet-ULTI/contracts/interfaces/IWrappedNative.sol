// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

/**
 * @title IWrappedNative
 * @dev Interface for wrapped native currency (e.g., ETH => WETH, BNB => WBNB, etc.)
 * @notice Based on the canonical WETH9 implementation
 * @notice See: https://github.com/Uniswap/v2-periphery/blob/master/contracts/interfaces/IWETH.sol
 */
interface IWrappedNative {
    /// @notice Deposit native currency (e.g., ETH) to get wrapped tokens (e.g., WETH)
    function deposit() external payable;

    /// @notice Withdraw native currency (e.g., ETH) by burning wrapped tokens (e.g., WETH)
    function withdraw(uint256) external;
}
