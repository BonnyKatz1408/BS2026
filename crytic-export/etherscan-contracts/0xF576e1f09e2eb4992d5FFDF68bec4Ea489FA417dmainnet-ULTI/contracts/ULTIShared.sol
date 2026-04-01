// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

/// @title ULTI Protocol Constants
/// @notice Contains all constants used in the ULTI protocol
/// @author @0xStef
library ULTIShared {
    // ===============================================
    // Constants
    // ===============================================

    /// @notice The number associated with ULTI, used in various calculations
    uint256 public constant ULTI_NUMBER = 33;

    /// @notice Maximum number of top contributors that can be tracked per cycle (33)
    uint256 public constant MAX_TOP_CONTRIBUTORS = ULTI_NUMBER;

    // Time-related constants
    /// @notice Cycle interval in seconds (33 days in seconds)
    uint256 public constant CYCLE_INTERVAL = 2851200;

    /// @notice Minimum interval between ULTI claims or deposits (24 hours in seconds)
    uint256 public constant DEPOSIT_CLAIM_INTERVAL = 86400;

    /// @notice Duration of the early bird price period after launch (24 hours in seconds)
    uint256 public constant EARLY_BIRD_PRICE_DURATION = 86400;

    /// @notice Minimum time interval for Time-Weighted Average Price (TWAP) calculation
    uint32 public constant MIN_TWAP_INTERVAL = 1089; // 18 minutes and 9 seconds in seconds

    /// @notice Interval between all bonuses claims (99 days)
    uint256 public constant ALL_BONUSES_CLAIM_INTERVAL = 8553600; // 99 days in seconds

    // Liquidity pool constants
    /// @notice Percentage of contributions allocated to liquidity pool (3%)
    uint256 public constant LP_CONTRIBUTION_PERCENTAGE = 3;

    /// @notice The fee tier for the Uniswap V3 pool (1%)
    uint24 public constant LP_FEE = 10000;

    /// @notice The minimum tick value for Uniswap V3 pool at 1%
    int24 public constant LP_MIN_TICK = -887200;

    /// @notice The maximum tick value for Uniswap V3 pool at 1%
    int24 public constant LP_MAX_TICK = 887200;

    /// @notice Maximum allowed slippage for adding liquidity in basis points: 99 BPS (0.99%)
    uint256 public constant MAX_ADD_LP_SLIPPAGE_BPS = 99;

    /// @notice Maximum allowed slippage for swaps in basis points: 132 BPS (1.32%)
    uint256 public constant MAX_SWAP_SLIPPAGE_BPS = 132;

    // Bonus-related constants
    /// @notice Percentage of contributions allocated to top contributors (3%)
    uint256 public constant TOP_CONTRIBUTOR_BONUS_PERCENTAGE = 3;

    /// @notice Cycle number when streak bonus starts
    uint256 public constant STREAK_BONUS_COUNT_START = 4;

    /// @notice Streak bonus maximum percentage (33%)
    uint256 public constant STREAK_BONUS_MAX_PERCENTAGE = 33;

    /// @notice Precomputed value for streak bonus calculation: (STREAK_BONUS_MAX_PERCENTAGE + 1) * PRECISION_FACTOR_1E6 / 100
    uint256 public constant STREAK_BONUS_MAX_PLUS_ONE_SCALED = 340000; // (33 + 1) * 1e6 / 100 = 340000

    /// @notice Percentage of referrer's bonus given to the referred user (33%)
    uint256 public constant REFERRAL_BONUS_FOR_REFERRED_PERCENTAGE = 33;

    /// @notice Maximum multiplier for referrer's skin in the game cap (10x)
    uint256 public constant REFERRAL_SKIN_IN_THE_GAME_CAP_MULTIPLIER = 10;

    // Pump-related constants
    /// @notice Interval between pump actions: 3300 seconds (55 minutes)
    uint256 public constant PUMP_INTERVAL = (ULTI_NUMBER * 100 seconds);

    /// @notice Numerator for pump factor calculation
    uint256 public constant PUMP_FACTOR_NUMERATOR = 419061;

    /// @notice Denominator for pump factor calculation
    uint256 public constant PUMP_FACTOR_DENOMINATOR = 1e10;

    /// @notice Minimum number of pumps (11) required to be classified as an active pumper
    uint256 public constant MIN_PUMPS_FOR_ACTIVE_PUMPERS = 11;

    /// @notice Maximum number of pumps allowed per user per cycle (33)
    uint256 public constant MAX_PUMPS_FOR_ACTIVE_PUMPERS = 33;

    /// @notice Percentage bonus for active pumpers (3% of the top contributor bonus)
    uint256 public constant ACTIVE_PUMPERS_BONUS_PERCENTAGE = 3;

    // Utility constants
    /// @notice Precision factor used in various calculations
    uint256 public constant PRECISION_FACTOR_1E6 = 1e6;

    // ===============================================
    // Structs
    // ===============================================

    /// @notice Represents a top contributor's data for a given cycle
    /// @dev Used to track and rank contributors based on their contributions and pump activity
    struct TopContributor {
        /// @notice Address of the contributor
        address contributorAddress;
        /// @notice Amount of input token deposited by the contributor
        uint256 inputTokenDeposited;
        /// @notice Amount of input token referred by the contributor
        uint256 inputTokenReferred;
        /// @notice Amount of ULTI allocated for the contributor
        uint256 ultiAllocated;
        /// @notice Discounted contribution value used for ranking
        uint256 discountedContribution;
        /// @notice Number of pump actions performed by the contributor
        uint16 pumpCount;
    }
}
