// SPDX-License-Identifier: BUSL-1.1

// This file is a modified copy of the official Uniswap Oracle library from @uniswap/v3-core/contracts/libraries/Oracle.sol
// The modifications were made to ensure compatibility with Solidity version 0.8.x, as the original library was designed for Solidity versions >=0.5.0.
// Modification: pragma version, valid imports, only kept `getQuoteAtTick` and remove all other functions

pragma solidity 0.8.28; // Modified: the pragma was changed from "pragma solidity >=0.5.0;"

// Modified: local import instead of @uniswap/v3-core/contracts/libraries/FullMath.sol
import "./FullMath.sol";

// Modified: local import instead of @uniswap/v3-core/contracts/libraries/FullMath.sol
import "./TickMath.sol";

import "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";

/// @title Oracle library
/// @notice Provides functions to integrate with V3 pool oracle
library OracleLibrary {
    // Modified: only kept the `getQuoteAtTick` compared to the orignal version

    /// @notice Given a tick and a token amount, calculates the amount of token received in exchange
    /// @param tick Tick value used to calculate the quote
    /// @param baseAmount Amount of token to be converted
    /// @param baseToken Address of an ERC20 token contract used as the baseAmount denomination
    /// @param quoteToken Address of an ERC20 token contract used as the quoteAmount denomination
    /// @return quoteAmount Amount of quoteToken received for baseAmount of baseToken
    function getQuoteAtTick(int24 tick, uint128 baseAmount, address baseToken, address quoteToken)
        internal
        pure
        returns (uint256 quoteAmount)
    {
        uint160 sqrtRatioX96 = TickMath.getSqrtRatioAtTick(tick);

        // Calculate quoteAmount with better precision if it doesn't overflow when multiplied by itself
        if (sqrtRatioX96 <= type(uint128).max) {
            uint256 ratioX192 = uint256(sqrtRatioX96) * sqrtRatioX96;
            quoteAmount = baseToken < quoteToken
                ? FullMath.mulDiv(ratioX192, baseAmount, 1 << 192)
                : FullMath.mulDiv(1 << 192, baseAmount, ratioX192);
        } else {
            uint256 ratioX128 = FullMath.mulDiv(sqrtRatioX96, sqrtRatioX96, 1 << 64);
            quoteAmount = baseToken < quoteToken
                ? FullMath.mulDiv(ratioX128, baseAmount, 1 << 128)
                : FullMath.mulDiv(1 << 128, baseAmount, ratioX128);
        }
    }
}
