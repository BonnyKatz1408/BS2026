// SPDX-License-Identifier: MIT

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
//
// 1. The above copyright notice and this permission notice shall be included
// in all copies or substantial portions of the Software.
//
// 2. Any use, reproduction, or distribution of this Software, in whole or in part,
// must include clear and appropriate attribution to @0xStef as the original author.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

// ██╗   ██╗██╗  ████████╗██╗    ██╗███████╗    ██╗   ██╗███╗   ██╗██╗ ██████╗ ██╗   ██╗███████╗
// ██║   ██║██║  ╚══██╔══╝██║    ██║██╔════╝    ██║   ██║████╗  ██║██║██╔═══██╗██║   ██║██╔════╝
// ██║   ██║██║     ██║   ██║    ██║███████╗    ██║   ██║██╔██╗ ██║██║██║   ██║██║   ██║█████╗
// ██║   ██║██║     ██║   ██║    ██║╚════██║    ██║   ██║██║╚██╗██║██║██║▄▄ ██║██║   ██║██╔══╝
// ╚██████╔╝███████╗██║   ██║    ██║███████║    ╚██████╔╝██║ ╚████║██║╚██████╔╝╚██████╔╝███████╗
//  ╚═════╝ ╚══════╝╚═╝   ╚═╝    ╚═╝╚══════╝     ╚═════╝ ╚═╝  ╚═══╝╚═╝ ╚══▀▀═╝  ╚═════╝ ╚══════╝

// ██╗   ██╗██╗  ████████╗██╗    ██╗███████╗    ███████╗ ██████╗ ██████╗     ███████╗██╗   ██╗███████╗██████╗ ██╗   ██╗ ██████╗ ███╗   ██╗███████╗
// ██║   ██║██║  ╚══██╔══╝██║    ██║██╔════╝    ██╔════╝██╔═══██╗██╔══██╗    ██╔════╝██║   ██║██╔════╝██╔══██╗╚██╗ ██╔╝██╔═══██╗████╗  ██║██╔════╝
// ██║   ██║██║     ██║   ██║    ██║███████╗    █████╗  ██║   ██║██████╔╝    █████╗  ██║   ██║█████╗  ██████╔╝ ╚████╔╝ ██║   ██║██╔██╗ ██║█████╗
// ██║   ██║██║     ██║   ██║    ██║╚════██║    ██╔══╝  ██║   ██║██╔══██╗    ██╔══╝  ╚██╗ ██╔╝██╔══╝  ██╔══██╗  ╚██╔╝  ██║   ██║██║╚██╗██║██╔══╝
// ╚██████╔╝███████╗██║   ██║    ██║███████║    ██║     ╚██████╔╝██║  ██║    ███████╗ ╚████╔╝ ███████╗██║  ██║   ██║   ╚██████╔╝██║ ╚████║███████╗
//  ╚═════╝ ╚══════╝╚═╝   ╚═╝    ╚═╝╚══════╝    ╚═╝      ╚═════╝ ╚═╝  ╚═╝    ╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚══════╝

// ██╗   ██╗██╗  ████████╗██╗    ██╗███████╗     ██╗ ██╗ ██████╗ ██╗   ██╗██████╗ ███████╗██████╗ ███████╗███████╗██╗
// ██║   ██║██║  ╚══██╔══╝██║    ██║██╔════╝    ████████╗██╔══██╗██║   ██║██╔══██╗██╔════╝██╔══██╗██╔════╝██╔════╝██║
// ██║   ██║██║     ██║   ██║    ██║███████╗    ╚██╔═██╔╝██████╔╝██║   ██║██████╔╝█████╗  ██║  ██║█████╗  █████╗  ██║
// ██║   ██║██║     ██║   ██║    ██║╚════██║    ████████╗██╔═══╝ ██║   ██║██╔══██╗██╔══╝  ██║  ██║██╔══╝  ██╔══╝  ██║
// ╚██████╔╝███████╗██║   ██║    ██║███████║    ╚██╔═██╔╝██║     ╚██████╔╝██║  ██║███████╗██████╔╝███████╗██║     ██║
//  ╚═════╝ ╚══════╝╚═╝   ╚═╝    ╚═╝╚══════╝     ╚═╝ ╚═╝ ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝╚═╝     ╚═╝

// ULTI IS UNIQUE, ULTI IS FOR EVERYONE, ULTI IS #PureDeFi

// @author: @0xStef
pragma solidity 0.8.28;

// OpenZeppelin contracts
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import {EnumerableSet} from "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";
import {EnumerableMap} from "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";
import {Math} from "@openzeppelin/contracts/utils/math/Math.sol";

// Uniswap V3 interfaces and libraries
import {IUniswapV3Factory} from "@uniswap/v3-core/contracts/interfaces/IUniswapV3Factory.sol";
import {IUniswapV3Pool} from "@uniswap/v3-core/contracts/interfaces/IUniswapV3Pool.sol";
import {ISwapRouter} from "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";

// Modified Uniswap V3 interfaces and libraries to reconcile compatibility issues
import {INonfungiblePositionManager} from "./lib/uniswap/INonfungiblePositionManager.sol";
import {TickMath} from "./lib/uniswap/TickMath.sol";
import {OracleLibrary} from "./lib/uniswap/Oracle.sol";
import {LiquidityAmounts} from "./lib/uniswap/LiquidityAmounts.sol";

// Third-party interfaces
import {IWrappedNative} from "./interfaces/IWrappedNative.sol";

import {ULTIShared} from "./ULTIShared.sol";

// Custom errors
error LiquidityPoolAlreadyExists();
error LiquidityPositionAlreadyExists();
error LiquidityPositionNotInitialized();
error DepositExpired();
error DepositCooldownActive();
error DepositNativeNotSupported();
error DepositInsufficientAmount();
error DepositCannotReferSelf();
error DepositCircularReferral();
error DepositInsufficientUltiAllocation();
error DepositLiquidityInsufficientEthAmount();
error DepositLiquidityInsufficientUltiAmount();
error ClaimUltiCooldownActive();
error ClaimUltiEmpty();
error PumpCooldownActive();
error PumpOnlyForTopContributors();
error PumpMaxPumpsReached();
error PumpInsufficientInputTokenAmount();
error PumpInsufficientMinimumUltiAmount();
error PumpInsufficientUltiOutput();
error PumpExpired();
error ClaimAllBonusesCooldownActive();
error ClaimAllBonusesEmpty();
error SnipingProctectionInvalidDayInCycle(uint8 dayInCycle);
error TWAPCalculationFailed();

/// @custom:security-contact security@ulti.org
contract ULTI is ERC20, Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;
    using EnumerableSet for EnumerableSet.AddressSet;
    using EnumerableMap for EnumerableMap.AddressToUintMap;

    // ===============================================
    // State Variables
    // ===============================================

    /// @notice Instance of the Uniswap V3 Factory contract
    IUniswapV3Factory public immutable uniswapFactory;

    /// @notice Instance of the Uniswap V3 SwapRouter contract
    ISwapRouter public immutable uniswapRouter;

    /// @notice Instance of the Uniswap V3 NonfungiblePositionManager contract
    INonfungiblePositionManager public immutable nonfungiblePositionManager;

    /// @notice Address of the input token (e.g. WETH, DAI, etc.)
    address public immutable inputTokenAddress;

    /// @notice Address of the wrapped native token (e.g. WETH, WBNB, etc.) to optionally enable depositNative()
    address public immutable wrappedNativeTokenAddress;

    /// @notice Flag indicating if ULTI is token0 in the liquidity pool
    bool public immutable isUltiToken0;

    /// @notice Initial ratio ULTI:INPUT_TOKEN
    /// @dev This value is scaled by the input token's decimals in the constructor
    uint256 public immutable initialRatio;

    /// @notice Minimum amount required for a deposit to be valid
    /// @dev Economic considerations for minimum deposit:
    /// - Consider future price appreciation of the input token vs. stable coins (USD) to prevent excluding users globally
    /// - Avoid setting it too low to prevent the streak bonus being easily gamed
    uint256 public immutable minimumDepositAmount;

    /// @notice Minimum number of observations required for TWAP calculation
    /// @dev This provides granularity for the 18m9s (1089s) TWAP window.
    /// For reference:
    /// - At 12s blocks: stores 1,152s (19.2 min) of price history (Ethereum mainnet case)
    /// - At 1s blocks: stores 96s (1.6 min) of price history
    /// - At 0.2s blocks: stores 19.2s of price history
    /// Even with partial coverage for fast networks, multiple observations still provide manipulation resistance
    uint16 public immutable minimumTwapObservations;

    /// @notice Uniswap V3 pool for the liquidity. Immutable pool held by the contract
    IUniswapV3Pool public liquidityPool;

    /// @notice Token ID of the Uniswap V3 position
    uint256 public liquidityPositionTokenId;

    /// @notice Timestamp when ULTI was launched
    uint64 public launchTimestamp;

    /// @notice Timestamp of the last pump action
    uint64 public nextPumpTimestamp;

    // ===============================================
    // Mappings
    // ===============================================

    /// @notice Stores the allocated amount of ULTI tokens claimable by each user
    /// @dev User address => Allocated ULTI to claim in the future
    mapping(address user => uint256 allocatedAmount) public claimableUlti;

    /// @notice Stores the amount of all allocated bonuses for claim in the future for each user (including referral, top contributor, and streak bonuses)
    /// @dev User address => Total claimable bonuses
    mapping(address user => uint256 bonuses) public claimableBonuses;

    /// @notice Tracks the next allowed timestamp for ULTI claim or deposit for each user
    /// @dev User address => Next allowed claim or deposit timestamp
    mapping(address user => uint256 nextDepositOrClaimTimestamp) public nextDepositOrClaimTimestamp;

    /// @notice Stores the referrer address for each user
    /// @dev User address => Referrer address
    mapping(address user => address referrer) public referrers;

    /// @notice Stores the timestamp of the next bonuses claim for each user
    /// @dev User address => Last claim timestamp
    mapping(address user => uint256 nextAllBonusesClaimTimestamp) public nextAllBonusesClaimTimestamp;

    /// @notice Stores the total ULTI ever allocated to a user during deposits to calculate the Skin-in-the-Game cap (excluding top contributor and referral bonuses)
    /// @dev User address => Total allocated ULTI
    mapping(address user => uint256 totalUltiAllocatedEver) public totalUltiAllocatedEver;

    /// @notice Stores the amount of referral bonuses accumulated by each user
    /// @dev User address => Total referral bonuses accumulated
    mapping(address user => uint256 referralBonuses) public accumulatedReferralBonuses;

    /// @notice Stores the amount of input token deposited by each user for each cycle
    /// @dev Cycle => User address => input token deposited
    mapping(uint32 cycle => mapping(address user => uint256 inputTokenDeposited)) public totalInputTokenDeposited;

    /// @notice Stores the amount of input token referred by each user for each cycle
    /// @dev Cycle => User address => input token referred
    mapping(uint32 cycle => mapping(address user => uint256 inputTokenReferred)) public totalInputTokenReferred;

    /// @notice Stores the amount of ULTI minted for each user for each cycle
    /// @dev Cycle => User address => ULTI minted
    mapping(uint32 cycle => mapping(address user => uint256 ultiAllocated)) public totalUltiAllocated;

    /// @notice Stores the streak count for each user for each cycle
    /// @dev Cycle => User address => Streak count
    /// @dev Note: For the current cycle, the streak count is loosely tracked and depends on the user making a deposit.
    ///      The count is only finalized and confirmed when the user makes their first deposit in the next cycle.
    ///      This means a user could technically have participated in the previous cycle but if they haven't deposited
    ///      in the current cycle yet, their streak value will remain 0 until they do.
    mapping(uint32 cycle => mapping(address user => uint32 streakCount)) public streakCounts;

    /// @notice Stores the discounted contribution for each user for each cycle
    /// @dev Cycle => User address => Discounted ULTI contribution
    mapping(uint32 cycle => mapping(address user => uint256 discountedContribution)) public discountedContributions;

    /// @notice Stores the top contributors and their discounted contributions for each cycle
    /// @dev Cycle => Map of top contributors and their respective discounted contribution
    mapping(uint32 cycle => EnumerableMap.AddressToUintMap topContributors) private topContributors;

    /// @notice Stores the address of the minimum contributor for each cycle
    /// @dev Cycle => Address of the minimum contributor
    mapping(uint32 cycle => address minContributorAddress) public minContributorAddress;

    /// @notice Stores the minimum discounted contribution for top contributors for each cycle
    /// @dev Cycle => Minimum discounted contribution
    mapping(uint32 cycle => uint256 minDiscountedContribution) public minDiscountedContribution;

    /// @notice Stores the total bonuses for top contributors for each cycle
    /// @dev Cycle => Total bonuses for top contributors
    mapping(uint32 cycle => uint256 topContributorsBonuses) public topContributorsBonuses;

    /// @notice Indicates whether top contributors' bonuses have been allocated for a given cycle
    /// @dev Cycle => Whether bonuses have been allocated
    mapping(uint32 cycle => bool isTopContributorsBonusAllocated) public isTopContributorsBonusAllocated;

    /// @notice Stores the set of addresses that have pumped for each cycle
    /// @dev Cycle => Set of addresses that have pumped
    mapping(uint32 cycle => EnumerableSet.AddressSet pumpers) private pumpers;

    /// @notice Stores the number of pumps performed by each user for each cycle
    /// @dev Cycle => User address => Number of pumps performed
    mapping(uint32 cycle => mapping(address user => uint16 pumpCount)) public pumpCounts;

    // ===============================================
    // Events
    // ===============================================

    /// @notice Emitted when the ULTI token is launched
    /// @param founderGiveaway Amount of input token given away by the founder
    /// @param lpAddress Address of the created liquidity pool
    event Launched(uint256 founderGiveaway, address lpAddress);

    /// @notice Emitted when a user deposits input token and receives ULTI tokens
    /// @param cycle The current cycle number
    /// @param user The address of the user who made the deposit
    /// @param referrer The address of the user's referrer (if any)
    /// @param inputTokenDeposited The amount of input token deposited
    /// @param inputTokenForLP The amount of input token tokens deposited into the liquidity position
    /// @param ultiForLP The amount of ULTI tokens to mint for the liquidity position
    /// @param ultiForUser The amount of ULTI tokens to mint for the user without bonus
    /// @param streakBonus The amount of ULTI tokens awarded as streak bonus
    /// @param streakCount The number of consecutive cycles the user has deposited
    /// @param referrerBonus The amount of ULTI tokens awarded to the referrer
    /// @param referredBonus The amount of ULTI tokens awarded to the referred user
    /// @param autoClaimed Whether the ULTI tokens were automatically claimed as part of the deposit
    /// @param cycleContribution The discounted contribution of the user for the cycle
    event Deposited(
        uint32 indexed cycle,
        address indexed user,
        address indexed referrer,
        uint256 inputTokenDeposited,
        uint256 inputTokenForLP,
        uint256 ultiForLP,
        uint256 ultiForUser,
        uint256 streakBonus,
        uint32 streakCount,
        uint256 referrerBonus,
        uint256 referredBonus,
        bool autoClaimed,
        uint256 cycleContribution
    );

    /// @notice Emitted when a user claims their ULTI tokens
    /// @param cycle The current cycle number
    /// @param user The address of the user claiming tokens
    /// @param amount The amount of ULTI tokens claimed
    event Claimed(uint32 indexed cycle, address indexed user, uint256 amount);

    /// @notice Emitted when a pump action is executed
    /// @param cycle The current cycle number
    /// @param user The address of the user who executed the pump
    /// @param inputTokenToSwap The amount of input token used for the pump
    /// @param ultiBurned The amount of ULTI tokens burned during the pump
    /// @param pumpCount The number of times the user has pumped in this cycle
    /// @param twap The current ULTI/INPUT_TOKEN TWAP during the pump
    event Pumped(
        uint32 indexed cycle,
        address indexed user,
        uint256 inputTokenToSwap,
        uint256 ultiBurned,
        uint16 pumpCount,
        uint256 twap
    );

    /// @notice Emitted when a top contributor is added, updated, or replaced in a cycle
    /// @dev This event tracks changes to the top contributors list, including:
    ///      - When a new contributor is added (up to MAX_TOP_CONTRIBUTORS)
    ///      - When an existing contributor's contribution is updated
    ///      - When a contributor replaces another in the top contributors list
    /// @param cycle The cycle number in which the top contributor change occurred
    /// @param contributorAddress The address of the contributor being added or updated
    /// @param removedContributorAddress The address of the contributor that was removed (address(0) if no removal)
    /// @param contribution The new total discounted contribution amount for this contributor
    event TopContributorsUpdated(
        uint32 indexed cycle,
        address indexed contributorAddress,
        address indexed removedContributorAddress,
        uint256 contribution
    );

    /// @notice Emitted when top contributor bonuses are distributed for a cycle
    /// @param cycle The cycle number for which bonuses are distributed
    /// @param ultiAmount The total amount of ULTI tokens distributed as bonuses
    event TopContributorBonusesDistributed(uint32 indexed cycle, uint256 ultiAmount);

    /// @notice Emitted when liquidity fees are collected and processed
    /// @param cycle The current cycle number
    /// @param inputTokenEarned The amount of input token earned from fees
    /// @param ultiBurned The amount of ULTI tokens burned from fees
    event LiquidityFeesProcessed(uint32 indexed cycle, uint256 inputTokenEarned, uint256 ultiBurned);

    /// @notice Emitted when a user claims all their accumulated bonuses
    /// @param cycle The current cycle number
    /// @param user The address of the user claiming the bonuses
    /// @param ultiAmount The total amount of ULTI tokens claimed as bonuses
    event AllBonusesClaimed(uint32 indexed cycle, address indexed user, uint256 ultiAmount);

    // ===============================================
    // Modifiers
    // ===============================================

    /**
     * @dev Modifier to ensure that the function can only be called after the liquidity position is initialized.
     * This modifier is used to prevent certain functions from being called before the ULTI token is fully launched.
     */
    modifier unstoppable() {
        if (liquidityPositionTokenId == 0) revert LiquidityPositionNotInitialized();
        _;
    }

    // ===============================================
    // Core Contract Setup
    // ===============================================

    /**
     * @notice Initializes the ULTI token contract with Uniswap V3 integration and token configuration
     * @dev Sets up the ULTI token contract by:
     *      1. Initializing Uniswap V3 interfaces (router, factory, position manager)
     *      2. Setting input token address
     *      3. Setting wrapped native token address for native deposits
     *      4. Determining token ordering for Uniswap pool
     *      5. Setting initial ratio
     *      6. Setting minimum deposit amount
     *      7. Setting minimum TWAP observations
     *      8. Setting unlimited approvals for Uniswap interactions
     * @param _name The name of the token
     * @param _symbol The symbol/tag of the token
     * @param uniswapRouterAddress The address of the Uniswap V3 Router
     * @param uniswapFactoryAddress The address of the Uniswap V3 Factory
     * @param nonfungiblePositionManagerAddress The address of the Uniswap V3 NonfungiblePositionManager
     * @param _inputTokenAddress The address of the input token (e.g. WETH, DAI, etc.)
     * @param _wrappedNativeTokenAddress The address of the wrapped native token (e.g. WETH, WBNB, etc.) to optionally enable depositNative()
     * @param _initialRatio The initial ratio of ULTI to input token
     * @param _minimumDepositAmount The minimum amount required for a deposit to be valid
     */
    constructor(
        string memory _name,
        string memory _symbol,
        address uniswapRouterAddress,
        address uniswapFactoryAddress,
        address nonfungiblePositionManagerAddress,
        address _inputTokenAddress,
        address _wrappedNativeTokenAddress,
        uint256 _initialRatio,
        uint256 _minimumDepositAmount,
        uint16 _minimumTwapObservations
    ) ERC20(_name, _symbol) Ownable(msg.sender) {
        // 1. Initialize Uniswap V3 interfaces
        uniswapRouter = ISwapRouter(uniswapRouterAddress);
        uniswapFactory = IUniswapV3Factory(uniswapFactoryAddress);
        nonfungiblePositionManager = INonfungiblePositionManager(nonfungiblePositionManagerAddress);

        // 2. Set input token address
        inputTokenAddress = _inputTokenAddress;

        // 3. Set wrapped native token address
        wrappedNativeTokenAddress = _wrappedNativeTokenAddress;

        // 4. Determine token ordering
        isUltiToken0 = address(this) < inputTokenAddress;

        // 5. Set initial ratio
        initialRatio = _initialRatio;

        // 6. Set minimum deposit amount
        minimumDepositAmount = _minimumDepositAmount;

        // 7. Set minimum TWAP observations
        minimumTwapObservations = _minimumTwapObservations;

        // 8. Set unlimited approvals
        _approve(address(this), address(nonfungiblePositionManager), type(uint256).max);
        _approve(address(this), address(uniswapRouter), type(uint256).max);
        IERC20(inputTokenAddress).forceApprove(address(nonfungiblePositionManager), type(uint256).max);
        IERC20(inputTokenAddress).forceApprove(address(uniswapRouter), type(uint256).max);

        // SECURITY NOTE: Unlimited approvals are granted to trusted Uniswap V3 contracts.
        // These contracts are well-audited and battle-tested but represent a theoretical risk if compromised.
    }

    /**
     * @notice Accepts native token deposits and wraps them into WETH, WBNB, etc.
     * @dev Automatically wraps received native tokens into their wrapped version
     *      This allows the contract to accept direct native token transfers
     *      which get added to the long-term reserve
     *      Handles direct native token transfers with empty msg.data
     */
    receive() external payable {
        if (inputTokenAddress != wrappedNativeTokenAddress) revert DepositNativeNotSupported();
        IWrappedNative(wrappedNativeTokenAddress).deposit{value: msg.value}();
    }

    /**
     * @notice Fallback function that accepts native token deposits and wraps them
     * @dev Automatically wraps received native tokens into their wrapped version
     *      This allows the contract to accept direct native token transfers
     *      which get added to the long-term reserve
     *      Catches and handles:
     *      - Native token transfers with non-empty msg.data
     *      - Calls to undefined functions
     *      - Incorrectly encoded function calls
     */
    fallback() external payable {
        if (inputTokenAddress != wrappedNativeTokenAddress) revert DepositNativeNotSupported();
        IWrappedNative(wrappedNativeTokenAddress).deposit{value: msg.value}();
    }

    /**
     * @notice Starts the ULTI token by creating the initial trading pool. Can only be called once by the owner with at least 33 units of input token.
     * @dev Launches the ULTI token by:
     *      1. Verifying the liquidity position doesn't exist
     *      2. Transferring input tokens from owner to contract
     *      3. Setting initial launch and pump timestamps
     *      4. Creating initial liquidity position with input tokens
     *      5. Renouncing contract ownership
     *      6. Emitting launch event
     * @param founderGiveaway Amount of input tokens to initialize liquidity position with
     */
    function launch(uint256 founderGiveaway) external onlyOwner {
        // 1. Verify the liquidity position doesn't exist and validating minimum input token amount
        if (liquidityPositionTokenId != 0) revert LiquidityPositionAlreadyExists();

        // 2. Transfer input tokens from owner
        IERC20(inputTokenAddress).safeTransferFrom(msg.sender, address(this), founderGiveaway);

        // 3. Set initial timestamps
        launchTimestamp = uint64(block.timestamp);
        nextPumpTimestamp = uint64(block.timestamp + ULTIShared.PUMP_INTERVAL);

        // 4. Create initial liquidity position
        _createLiquidity(founderGiveaway, block.timestamp);

        // 5. Renounce ownership
        renounceOwnership();

        // 6. Emit launch event
        emit Launched(founderGiveaway, address(liquidityPool));
    }

    // ===============================================
    // Price & Liquidity
    // ===============================================

    /**
     * @notice Gets the current price of ULTI tokens in input token
     * @dev External wrapper function to retrieve the current spot price from the Uniswap V3 pool. The result is scaled by 1e18, so 1e18 represents 1 input token per ULTI
     * @return spotPrice The current spot price in ULTI/INPUT_TOKEN format (how much input token is needed to buy 1 ULTI)
     */
    function getSpotPrice() external view returns (uint256) {
        return _getSpotPrice();
    }

    /**
     * @notice Gets the current exchange rate between ULTI tokens and input token from the liquidity pool
     * @dev Uses UniswapV3's OracleLibrary approach for price calculation. Safely calculates spot price using multi-step computation to prevent overflow.
     *      Uses OpenZeppelin's Math.mulDiv for safe multiplication and division with overflow protection:
     *      1. For token0 (ULTI): price = (sqrtPrice^2 * 1e18) / 2^192
     *      2. For token1 (ULTI): price = (2^192 * 1e18) / sqrtPrice^2
     * @return spotPrice The current price ratio between ULTI and input token (input token needed to buy 1 ULTI)
     */
    function _getSpotPrice() internal view returns (uint256 spotPrice) {
        // 1. Get square root price from pool slot0
        (uint160 sqrtPriceX96,,,,,,) = liquidityPool.slot0();
        uint256 sqrtPrice = uint256(sqrtPriceX96);

        if (isUltiToken0) {
            // 2. When ULTI is token0:
            // First step: Calculate (sqrtPrice * sqrtPrice) / 2^96
            // This reduces the intermediate value by 2^96 early to prevent overflow
            uint256 priceX96 = Math.mulDiv(sqrtPrice, sqrtPrice, 1 << 96);

            // Second step: Calculate (priceX96 * 1e18) / 2^96
            // This completes the calculation while maintaining precision
            spotPrice = Math.mulDiv(priceX96, 1e18, 1 << 96);
        } else {
            // When ULTI is token1:
            // First step: Calculate (2^96 * 1e18) / sqrtPrice
            // This keeps intermediate values manageable
            uint256 invPriceX96 = Math.mulDiv(1 << 96, 1e18, sqrtPrice);

            // Second step: Calculate (invPriceX96 * 2^96) / sqrtPrice
            // This completes the inverse price calculation
            spotPrice = Math.mulDiv(invPriceX96, 1 << 96, sqrtPrice);
        }
    }

    /**
     * @notice Gets the average price of ULTI tokens over a recent time period
     * @dev External wrapper that returns the current Time-Weighted Average Price (TWAP).
     * Always calculates fresh TWAP value to avoid returning stale data.
     * @return currentTwap The current time-weighted average price
     */
    function getTWAP() external view returns (uint256 currentTwap) {
        return _calculateTWAP();
    }

    /**
     * @notice Calculates the time-weighted average price (TWAP) of ULTI tokens in input token
     * @dev Main execution steps:
     *      1. Returns initial ratio if minimum TWAP time hasn't elapsed since launch
     *      2. Sets up observation window parameters for Uniswap oracle:
     *         - Uses MIN_TWAP_INTERVAL for window size
     *         - Gets observations at start and end of window
     *      3. Attempts to calculate TWAP from Uniswap observations:
     *         - Gets cumulative ticks from pool
     *         - Calculates average tick over window
     *         - Converts tick to price quote with ULTI as base token
     *      4. Revert if TWAP calculation fails
     * @return twap The time-weighted average price in input token per ULTI (scaled by 1e18)
     */
    function _calculateTWAP() internal view returns (uint256 twap) {
        // 1. Return initial ratio if minimum TWAP time hasn't elapsed
        if (block.timestamp < launchTimestamp + ULTIShared.MIN_TWAP_INTERVAL) {
            return 1e18 / initialRatio;
        }

        // 2. Set up observation window parameters
        uint32[] memory secondsAgos = new uint32[](2);
        secondsAgos[0] = ULTIShared.MIN_TWAP_INTERVAL; // observation window
        secondsAgos[1] = 0;

        // 3. Get cumulative ticks and compute average
        try liquidityPool.observe(secondsAgos) returns (int56[] memory tickCumulatives, uint160[] memory) {
            // 3a. Calculate time-weighted average tick
            int56 tickCumulativeDelta = tickCumulatives[1] - tickCumulatives[0];
            int24 timeWeightedAverageTick = int24(tickCumulativeDelta / int32(secondsAgos[0]));

            // Adjust for negative tickCumulativeDelta to handle truncation correctly
            if (tickCumulativeDelta < 0 && (tickCumulativeDelta % int56(uint56(secondsAgos[0])) != 0)) {
                timeWeightedAverageTick--;
            }

            // 3b. Convert tick to price quote
            // Always pass ULTI as base token (amount of 1e18 = 1 ULTI) and input token as quote token
            // This ensures we get the price in INPUT_TOKEN/ULTI format consistently
            twap = OracleLibrary.getQuoteAtTick(
                timeWeightedAverageTick,
                1e18, // amountIn: 1 ULTI token (18 decimals)
                address(this), // base token (ULTI)
                inputTokenAddress // quote token (INPUT_TOKEN)
            );
        } catch {
            // 4. Revert if TWAP calculation fails
            revert TWAPCalculationFailed();
        }

        return twap;
    }

    /**
     * @notice Creates the initial trading pool for ULTI and input token on Uniswap
     * @dev Main execution steps:
     *      1. Verifies no pool exists yet by checking Uniswap factory
     *      2. Creates new Uniswap V3 pool and stores instance if none exists. Uses existing pool otherwise
     *      3. Calculates initial square root price based on `initialRatio`
     *      4. Initializes pool with calculated price
     *      5. Increases observation cardinality to prevent TWAP manipulation
     *      6. Mints ULTI tokens to match input token amount at initial ratio
     *      7. Creates full range liquidity position with both tokens
     *      8. Stores position token ID for future operations
     *      9. Keeps any leftover tokens in contract for future use
     * @param inputTokenForLP Amount of input token to add to the liquidity position
     * @param deadline The timestamp after which the transaction will revert
     */
    function _createLiquidity(uint256 inputTokenForLP, uint256 deadline) private {
        // 1. Check if the Uniswap pool already exists
        address liquidityPoolAddress = uniswapFactory.getPool(address(this), inputTokenAddress, ULTIShared.LP_FEE);

        // 2. Create and store pool if it doesn't exist
        if (liquidityPoolAddress == address(0)) {
            liquidityPoolAddress = uniswapFactory.createPool(address(this), inputTokenAddress, ULTIShared.LP_FEE);
            liquidityPool = IUniswapV3Pool(liquidityPoolAddress);
        } else {
            // SECURITY NOTE: DoS risk if a pool with the same parameters is created before `launch` is executed.
            // This risk is accepted due to its low impact (cost of deploying ULTI) and very low likelihood of happening.
            revert LiquidityPoolAlreadyExists();
        }

        // 3. Calculate the square root price to initialize the pool
        uint160 initialSqrtPriceX96;
        if (isUltiToken0) {
            uint256 sqrtPrice = Math.sqrt((1 << 192) / initialRatio);
            initialSqrtPriceX96 = uint160(sqrtPrice);
        } else {
            uint256 sqrtPrice = Math.sqrt(uint256(initialRatio) << 192);
            initialSqrtPriceX96 = uint160(sqrtPrice);
        }

        // 4. Initialize the Uniswap pool with the calculated price
        IUniswapV3Pool(liquidityPoolAddress).initialize(initialSqrtPriceX96);

        // 5. Increase observation cardinality to prevent TWAP manipulation
        IUniswapV3Pool(liquidityPoolAddress).increaseObservationCardinalityNext(minimumTwapObservations);

        // 6. Calculate and mint ULTI tokens for liquidity
        uint256 ultiForLP = inputTokenForLP * initialRatio;
        _mint(address(this), ultiForLP);

        // 7. Create full range liquidity position
        INonfungiblePositionManager.MintParams memory mintParams = INonfungiblePositionManager.MintParams({
            token0: isUltiToken0 ? address(this) : inputTokenAddress,
            token1: isUltiToken0 ? inputTokenAddress : address(this),
            fee: ULTIShared.LP_FEE,
            tickLower: ULTIShared.LP_MIN_TICK,
            tickUpper: ULTIShared.LP_MAX_TICK,
            amount0Desired: isUltiToken0 ? ultiForLP : inputTokenForLP,
            amount1Desired: isUltiToken0 ? inputTokenForLP : ultiForLP,
            amount0Min: 0,
            amount1Min: 0,
            recipient: address(this),
            deadline: deadline
        });

        // 8. Store position token ID
        (uint256 tokenId,,,) = nonfungiblePositionManager.mint(mintParams);
        liquidityPositionTokenId = tokenId;

        // 9. Keeps any leftover tokens in contract for future use:
        // If there are any leftover input token, keep in the contract: it will be used for future pumps
        // If there are any leftover ULTI, keep in the contract and do nothing
    }

    /**
     * @notice Tries to add more liquidity to the trading pool to make trading easier and more stable for everyone
     * @dev Main execution steps:
     *      1. Validates input amounts are non-zero
     *      2. Mints new ULTI tokens to this contract for liquidity
     *      3. Calculates minimum amounts with 0.33% slippage tolerance
     *      4. Constructs parameters for increasing liquidity
     *      5. Calls position manager and tries to increase liquidity.
     *      6. Keeps any leftover tokens in contract for future use
     * @param inputTokenForLP Amount of input token to add to the liquidity position
     * @param ultiForLP Amount of ULTI to add to the liquidity position
     * @param deadline The timestamp after which the transaction will revert
     */
    function _tryIncreaseLiquidity(uint256 inputTokenForLP, uint256 ultiForLP, uint256 deadline) private {
        // 1. Validate input amounts are non-zero
        if (inputTokenForLP == 0) revert DepositLiquidityInsufficientEthAmount();
        if (ultiForLP == 0) revert DepositLiquidityInsufficientUltiAmount();

        // 2. Mint ULTI tokens to this contract for liquidity provision
        _mint(address(this), ultiForLP);

        // 3. Calculate minimum amounts for ULTI and input token, accounting for slippage
        // Ensures liquidity provision won't lose more than MAX_ADD_LP_SLIPPAGE_BPS due to slippage
        uint256 minUltiAmount = (ultiForLP * (10000 - ULTIShared.MAX_ADD_LP_SLIPPAGE_BPS)) / 10000;
        uint256 minInputTokenAmount = (inputTokenForLP * (10000 - ULTIShared.MAX_ADD_LP_SLIPPAGE_BPS)) / 10000;

        // 4. Construct parameters for increasing liquidity
        INonfungiblePositionManager.IncreaseLiquidityParams memory increaseParams = INonfungiblePositionManager
            .IncreaseLiquidityParams({
            tokenId: liquidityPositionTokenId,
            amount0Desired: isUltiToken0 ? ultiForLP : inputTokenForLP,
            amount1Desired: isUltiToken0 ? inputTokenForLP : ultiForLP,
            amount0Min: isUltiToken0 ? minUltiAmount : minInputTokenAmount,
            amount1Min: isUltiToken0 ? minInputTokenAmount : minUltiAmount,
            deadline: deadline
        });

        // 5. Call position manager to increase liquidity
        // Note: In most cases liquidity is expected to be added but in very volatile markets, this step will be skipped.
        // This occurs when deposits are made following significant price changes, where the difference
        // between the TWAP and current spot price exceeds the pool's slippage limits
        try nonfungiblePositionManager.increaseLiquidity(increaseParams) {}
        catch {
            // Skip, failing to add liquidity should never block deposits
            // The input token dedicated to liquidity will instead be used to pump
        }

        // 6. Keeps any leftover tokens in contract for future use:
        // If there are any leftover input token, keep in the contract: it will be used for future pumps
        // If there are any leftover ULTI, keep in the contract and do nothing
    }

    /**
     * @notice Collects and processes fees earned from providing liquidity, burning ULTI fees and keeping input token fees in the contract
     * @dev Main execution steps:
     *      1. Prepares collection parameters to collect all accumulated fees
     *      2. Calls position manager to collect fees into this contract
     *      3. Based on token ordering:
     *         - Burns collected ULTI fees by calling _burn()
     *         - Keeps collected input token fees in contract
     *      4. Emits event with amounts processed
     * @dev Requires liquidityPositionTokenId to be set and contract to have sufficient balance
     */
    function _collectAndProcessLiquidityFees() private {
        // 1. Prepare collection parameters
        INonfungiblePositionManager.CollectParams memory params = INonfungiblePositionManager.CollectParams({
            tokenId: liquidityPositionTokenId,
            recipient: address(this),
            amount0Max: type(uint128).max, // Collect all ULTI fees
            amount1Max: type(uint128).max // Collect all input token fees
        });

        // 2. Collect the fees
        (uint256 amount0, uint256 amount1) = nonfungiblePositionManager.collect(params);

        uint256 inputTokenEarned;
        uint256 ultiBurned;

        // 3. Burn ULTI fees, keep the input token in the contract
        if (isUltiToken0) {
            if (amount0 > 0) {
                _burn(address(this), amount0);
                ultiBurned = amount0;
            }
            if (amount1 > 0) {
                inputTokenEarned = amount1;
            }
        } else {
            if (amount1 > 0) {
                _burn(address(this), amount1);
                ultiBurned = amount1;
            }
            if (amount0 > 0) {
                inputTokenEarned = amount0;
            }
        }

        // 4. Emits event with amounts processed
        emit LiquidityFeesProcessed(getCurrentCycle(), inputTokenEarned, ultiBurned);
    }

    /**
     * @notice Gets how much input token and ULTI tokens are currently in the liquidity position and total in the pool
     * @dev Calculates token amounts in the Uniswap V3 pool through these steps:
     *      1. Get liquidity of the contract's position
     *      2. Retrieve pool's current price and tick boundaries
     *      3. Compute token amounts based on current price and boundaries
     *      4. Map token0/token1 to ULTI/INPUT_TOKEN based on pool token ordering flag
     *      5. Get total token balances in the pool
     * @return inputTokenAmountInPosition The amount of input token in the current liquidity position
     * @return ultiAmountInPosition The amount of ULTI in the current liquidity position
     * @return inputTokenAmountInPool The total amount of input token in the liquidity pool
     * @return ultiAmountInPool The total amount of ULTI in the liquidity pool
     */
    function getLiquidityAmounts()
        external
        view
        returns (
            uint256 inputTokenAmountInPosition,
            uint256 ultiAmountInPosition,
            uint256 inputTokenAmountInPool,
            uint256 ultiAmountInPool
        )
    {
        // 1. Get liquidity of the contract's position
        (,,,,,,, uint128 liquidity,,,,) = nonfungiblePositionManager.positions(liquidityPositionTokenId);

        // 2. Retrieve pool's current price and tick boundaries
        (uint160 sqrtPriceX96,,,,,,) = liquidityPool.slot0();
        uint160 sqrtRatioAX96 = TickMath.getSqrtRatioAtTick(ULTIShared.LP_MIN_TICK);
        uint160 sqrtRatioBX96 = TickMath.getSqrtRatioAtTick(ULTIShared.LP_MAX_TICK);

        // 3. Compute token amounts based on current price and boundaries
        (uint256 amount0, uint256 amount1) =
            LiquidityAmounts.getAmountsForLiquidity(sqrtPriceX96, sqrtRatioAX96, sqrtRatioBX96, liquidity);

        // 4. Map token0/token1 to ULTI/INPUT_TOKEN based on ordering
        if (isUltiToken0) {
            ultiAmountInPosition = amount0;
            inputTokenAmountInPosition = amount1;
        } else {
            inputTokenAmountInPosition = amount0;
            ultiAmountInPosition = amount1;
        }

        // 5. Get total token balances in the pool
        inputTokenAmountInPool = IERC20(inputTokenAddress).balanceOf(address(liquidityPool));
        ultiAmountInPool = IERC20(address(this)).balanceOf(address(liquidityPool));
    }

    // ===============================================
    // Deposit & Claims
    // ===============================================

    /**
     * @notice Allows users to deposit native currency (ETH, BNB, etc.) to receive ULTI tokens after a waiting period
     * @dev Main execution steps:
     *      1. Validates input token address matches wrapped native token
     *      2. Validates non-zero native currency amount sent
     *      3. Calls internal _deposit() with native flag set to true
     * @param referrer The address that referred this deposit
     * @param minUltiToAllocate Minimum ULTI tokens to receive to prevent slippage
     * @param deadline Timestamp when transaction expires
     * @param autoClaim Whether to claim pending ULTI before depositing
     */
    function depositNative(address referrer, uint256 minUltiToAllocate, uint256 deadline, bool autoClaim)
        external
        payable
        nonReentrant
        unstoppable
    {
        if (inputTokenAddress != wrappedNativeTokenAddress) revert DepositNativeNotSupported();

        // Passing `true` flag for native deposit
        _deposit(msg.value, referrer, minUltiToAllocate, deadline, autoClaim, true);
    }

    /**
     * @notice Allows users to deposit a ERC20 input tokens to receive ULTI tokens after a waiting period
     * @param inputTokenAmount Amount of input token to deposit
     * @param referrer The address that referred this deposit
     * @param minUltiToAllocate Minimum ULTI tokens to receive to prevent slippage
     * @param deadline Timestamp when transaction expires
     * @param autoClaim Whether to claim pending ULTI before depositing
     */
    function deposit(
        uint256 inputTokenAmount,
        address referrer,
        uint256 minUltiToAllocate,
        uint256 deadline,
        bool autoClaim
    ) external nonReentrant unstoppable {
        // Passing `false` flag for ERC20 token deposit
        _deposit(inputTokenAmount, referrer, minUltiToAllocate, deadline, autoClaim, false);
    }

    /**
     * @notice Processes a user's deposit of input tokens or native currency to receive ULTI tokens
     * @dev Processes deposits:
     *      1. Validates deposit requirements:
     *         - Checks input amount is non-zero
     *         - Validates referrer address
     *         - Verifies cooldown period has passed
     *      2. Auto-claims pending ULTI if:
     *         - Auto-claim flag is true
     *         - Cooldown period has passed
     *         - User has pending ULTI
     *      3. Transfers tokens from user to contract:
     *         - For native: wraps received native currency into its corresponding wrapped token
     *         - For tokens: transfers input tokens from user
     *      4. Processes allocation:
     *         - Calculates ULTI amounts for user and liquidity position
     *         - Adds liquidity to Uniswap pool
     *      5. Calculates and adds streak bonus based on allocated ULTI
     *      6. Updates user's total lifetime ULTI allocation
     *      7. Processes referral bonuses for referrer and referred user
     *      8. Updates contributor rankings with new allocation
     *      9. Resets deposit/claim cooldown cooldown
     *      10. Initializes bonus claim timer if first deposit
     *      11. Emits detailed deposit event
     * @param inputTokenAmount Amount of input token to deposit
     * @param referrer The address that referred this deposit
     * @param minUltiToAllocate Minimum ULTI tokens to receive to prevent slippage
     * @param deadline Timestamp when transaction expires
     * @param autoClaim Whether to claim pending ULTI before depositing
     * @param isNative Whether the deposit is made with native currency
     */
    function _deposit(
        uint256 inputTokenAmount,
        address referrer,
        uint256 minUltiToAllocate,
        uint256 deadline,
        bool autoClaim,
        bool isNative
    ) private {
        // 1. Validate deposit requirements
        if (inputTokenAmount < minimumDepositAmount) revert DepositInsufficientAmount();
        if (referrer == msg.sender) revert DepositCannotReferSelf();
        if (referrers[referrer] == msg.sender) revert DepositCircularReferral();
        if (block.timestamp > deadline) revert DepositExpired();
        if (block.timestamp < nextDepositOrClaimTimestamp[msg.sender]) revert DepositCooldownActive();

        // 2. Auto-claim pending ULTI if requested
        bool autoClaimed;
        if (autoClaim && claimableUlti[msg.sender] > 0) {
            _claimUlti();
            autoClaimed = true;
        }

        // 3. Transfer input tokens from user to contract
        if (isNative) {
            // Convert native to wrapped native (e.g. ETH to WETH)
            IWrappedNative(wrappedNativeTokenAddress).deposit{value: msg.value}();
        } else {
            IERC20(inputTokenAddress).safeTransferFrom(msg.sender, address(this), inputTokenAmount);
        }

        // 4. Process deposit allocation
        (uint256 ultiForUser, uint256 ultiForLP, uint256 inputTokenForLP) =
            _allocateDeposit(inputTokenAmount, minUltiToAllocate, deadline);

        uint32 cycle = getCurrentCycle();

        // 5. Calculate the streak bonus and allocate it based on the ULTI just allocated to the user
        (uint256 streakBonus, uint32 streakCount) = _updateStreakBonus(msg.sender, inputTokenAmount, ultiForUser, cycle);

        // 6. Update total ULTI ever allocated for user to increase their Skin-in-the-Game cap (includes streak bonus, excludes other bonuses)
        uint256 ultiForUserWithStreakBonus = ultiForUser + streakBonus;
        totalUltiAllocatedEver[msg.sender] += ultiForUserWithStreakBonus;

        // 7. Calculate referral bonus and allocate it based on the ULTI just allocated to the user including the streak bonus
        (address effectiveReferrer, uint256 referrerBonus, uint256 referredBonus) =
            _updateReferrals(referrer, inputTokenAmount, ultiForUserWithStreakBonus, cycle);

        // 8. Update contributors and top contributors rankings based on total ULTI just allocated including the streak bonus
        uint256 cycleContribution =
            _updateContributors(cycle, msg.sender, inputTokenAmount, 0, ultiForUserWithStreakBonus);

        // 9. Reset deposit/claim cooldown cooldown
        nextDepositOrClaimTimestamp[msg.sender] = block.timestamp + ULTIShared.DEPOSIT_CLAIM_INTERVAL;

        // 10. Initialize next bonus claim timestamp if not already set
        if (nextAllBonusesClaimTimestamp[msg.sender] == 0) {
            nextAllBonusesClaimTimestamp[msg.sender] = block.timestamp + ULTIShared.ALL_BONUSES_CLAIM_INTERVAL;
        }

        // 11. Emit deposit event
        emit Deposited(
            cycle,
            msg.sender,
            effectiveReferrer,
            inputTokenAmount,
            inputTokenForLP,
            ultiForLP,
            ultiForUser,
            streakBonus,
            streakCount,
            referrerBonus,
            referredBonus,
            autoClaimed,
            cycleContribution
        );
    }

    /**
     * @notice Processes a user's deposit of input tokens and allocates ULTI tokens in return
     * @dev Processes deposit allocation:
     *      1. Get TWAP
     *      2. Calculates ULTI tokens to give user based on early bird or TWAP price
     *      3. Verifies user gets at least their minimum requested ULTI amount
     *      4. Calculates input token and ULTI portions for liquidity position using the deposit price
     *      5. Try adding calculated amounts to the liquidity position
     *      6. Updates user's ULTI allocation
     * @param inputTokenAmount Amount of input tokens being deposited
     * @param minUltiToAllocate Minimum ULTI tokens to receive to prevent slippage
     * @param deadline Timestamp when transaction expires
     * @return ultiForUser Amount of ULTI tokens allocated to user without bonus
     * @return ultiForLP Amount of ULTI tokens allocated to liquidity position
     * @return inputTokenForLP Amount of input tokens allocated to liquidity position
     */
    function _allocateDeposit(uint256 inputTokenAmount, uint256 minUltiToAllocate, uint256 deadline)
        private
        returns (uint256 ultiForUser, uint256 ultiForLP, uint256 inputTokenForLP)
    {
        // 1. Get TWAP
        uint256 twap = _calculateTWAP();

        // 2. Calculates ULTI tokens to give user based on early bird or TWAP price
        if (block.timestamp < launchTimestamp + ULTIShared.EARLY_BIRD_PRICE_DURATION) {
            ultiForUser = inputTokenAmount * initialRatio;
        } else {
            ultiForUser = 1e18 * inputTokenAmount / twap;
        }

        // 3. Verify user gets at least their minimum requested ULTI amount
        if (ultiForUser < minUltiToAllocate) revert DepositInsufficientUltiAllocation();

        // 4. Calculate INPUT and ULTI portions for liquidity position using the current spot price to prevent slippage issues
        inputTokenForLP = (inputTokenAmount * ULTIShared.LP_CONTRIBUTION_PERCENTAGE) / 100;
        ultiForLP = 1e18 * inputTokenForLP / twap;

        // 5. Try adding calculated amounts to the liquidity position
        _tryIncreaseLiquidity(inputTokenForLP, ultiForLP, deadline);

        // 6. Updates user's ULTI allocation
        claimableUlti[msg.sender] += ultiForUser;

        return (ultiForUser, ultiForLP, inputTokenForLP);
    }

    /**
     * @notice Claim pending ULTI tokens
     * @dev Calls internal _claimUlti function to process the claim
     */
    function claimUlti() external nonReentrant unstoppable {
        _claimUlti();
    }

    /**
     * @notice Allows users to claim their pending ULTI tokens
     * @dev Processes ULTI token claims:
     *      1. Validates the 24h cooldown period has passed
     *      2. Validates user has ULTI tokens available to claim
     *      3. Records the claimable amount and resets user's allocation
     *      4. Mints the ULTI tokens to the user
     *      5. Emits claim event with details
     */
    function _claimUlti() private {
        // 1. Validate cooldown period
        if (block.timestamp < nextDepositOrClaimTimestamp[msg.sender]) revert ClaimUltiCooldownActive();

        // 2. Validate claimable amount
        if (claimableUlti[msg.sender] == 0) revert ClaimUltiEmpty();

        // 3. Record amount and reset allocation
        uint256 ultiToClaim = claimableUlti[msg.sender];
        claimableUlti[msg.sender] = 0;

        // 4. Mint tokens to user
        _mint(msg.sender, ultiToClaim);

        // 5. Emit claim event
        emit Claimed(getCurrentCycle(), msg.sender, ultiToClaim);
    }

    /**
     * @notice Claims all earned bonuses in one go after the cooldown period
     * @dev Processes bonus claims through these steps:
     *      1. Validate cooldown period has passed
     *      2. Get and validate user's allocated bonuses
     *      3. Reset allocated bonuses to 0
     *      4. Reset accumulated referral bonuses to 0 (reset skin in the game buffer)
     *      5. Mint bonus tokens to user
     *      6. Set next claim timestamp
     *      7. Emit claim event
     */
    function claimAllBonuses() external nonReentrant unstoppable {
        // 1. Validate cooldown period has passed
        if (block.timestamp < nextAllBonusesClaimTimestamp[msg.sender]) revert ClaimAllBonusesCooldownActive();

        // 2. Get and validate user's allocated bonuses
        uint256 bonuses = claimableBonuses[msg.sender];
        if (bonuses == 0) revert ClaimAllBonusesEmpty();

        // 3. Reset allocated bonuses to 0
        claimableBonuses[msg.sender] = 0;

        // 4. Reset accumulated referral bonuses to 0 (reset skin in the game buffer)
        accumulatedReferralBonuses[msg.sender] = 0;

        // 5. Mint bonus tokens to user
        _mint(msg.sender, bonuses);

        // 6. Set next claim timestamp
        nextAllBonusesClaimTimestamp[msg.sender] = block.timestamp + ULTIShared.ALL_BONUSES_CLAIM_INTERVAL;

        // 7. Emit claim event
        emit AllBonusesClaimed(getCurrentCycle(), msg.sender, bonuses);
    }

    // ===============================================
    // Pump Mechanism
    // ===============================================

    /**
     * @notice Checks if an address is an active pumper for a given cycle
     * @dev Active pumpers must have at least MIN_PUMPS_FOR_ACTIVE_PUMPERS pumps, 11 in a cycle
     * @param cycle The cycle to check
     * @param pumper The address to check
     * @return bool True if address is an active pumper
     */
    function _isActivePumper(uint32 cycle, address pumper) internal view returns (bool) {
        return pumpCounts[cycle][pumper] >= ULTIShared.MIN_PUMPS_FOR_ACTIVE_PUMPERS;
    }

    /**
     * @notice Allows top contributors to increase ULTI token value
     * @dev Main execution steps:
     *      1. Validates transaction requirements:
     *         - Checks deadline not passed
     *         - Checks pump cooldown period elapsed
     *         - Verifies caller is top contributor
     *         - Verifies pump count is less than max allowed
     *      2. Performs cycle maintenance if needed
     *      3. Updates time-weighted average price (TWAP)
     *      4. Calculates input token amount for pump:
     *         - Takes 0.00419061% of contract balance per pump
     *         - Equivalent to ~3.55% per cycle and ~33% per year
     *      5. Calculate minimum ULTI output based on user's max price
     *      6. Swaps input tokens for ULTI via Uniswap
     *      7. Burns received ULTI tokens
     *      8. Increments pump count for current cycle
     *      9. Sets next pump timestamp
     * @param maxInputTokenPerUlti The maximum amount of input token per ULTI to use for a pump
     * @param deadline The timestamp after which the transaction will revert
     * @return inputTokenToSwap The amount of input token used for the pump
     * @return ultiToBurn The amount of ULTI tokens burned in the process
     */
    function pump(uint256 maxInputTokenPerUlti, uint256 deadline)
        external
        nonReentrant
        unstoppable
        returns (uint256 inputTokenToSwap, uint256 ultiToBurn)
    {
        // 1. Validate transaction requirements
        if (block.timestamp > deadline) revert PumpExpired();
        if (block.timestamp < nextPumpTimestamp) revert PumpCooldownActive();
        uint32 cycle = getCurrentCycle();
        if (!topContributors[cycle].contains(msg.sender)) revert PumpOnlyForTopContributors();
        if (pumpCounts[cycle][msg.sender] >= ULTIShared.MAX_PUMPS_FOR_ACTIVE_PUMPERS) revert PumpMaxPumpsReached();

        // 2. Perform cycle maintenance if needed
        if (cycle > 1 && !isTopContributorsBonusAllocated[cycle - 1]) {
            _allocateTopContributorsBonuses(cycle - 1);
            _collectAndProcessLiquidityFees();
        }

        // 3. Update time-weighted average price
        uint256 twap = _calculateTWAP();

        // 4. Calculate input token amount to use for pump:
        // 0.00419061% per pump, equivalent to ~3.55% per cycle and ~33% per year
        uint256 inputTokenBalance = IERC20(inputTokenAddress).balanceOf(address(this));
        inputTokenToSwap = inputTokenBalance * ULTIShared.PUMP_FACTOR_NUMERATOR / ULTIShared.PUMP_FACTOR_DENOMINATOR;

        // 5. Calculate minimum ULTI output based on user's max price
        uint256 minUltiAmount = inputTokenToSwap * 1e18 / maxInputTokenPerUlti;

        // 6. Swap input token for ULTI tokens
        ultiToBurn = _swapInputTokenForUlti(inputTokenToSwap, minUltiAmount, twap, deadline);

        // 7. Burn received ULTI tokens
        _burn(msg.sender, ultiToBurn);

        // 8. Increment pump count for current cycle
        _updatePumpCount(cycle, msg.sender);

        // 9. Set next allowed pump timestamp
        nextPumpTimestamp = uint64(block.timestamp + ULTIShared.PUMP_INTERVAL);

        emit Pumped(cycle, msg.sender, inputTokenToSwap, ultiToBurn, pumpCounts[cycle][msg.sender], twap);
    }

    /**
     * @notice Swaps input tokens for ULTI tokens using Uniswap with slippage protection
     * @dev Main execution steps:
     *      1. Validates input parameters are non-zero
     *      2. Calculates expected ULTI output based on provided TWAP
     *      3. Determines effective minimum ULTI amount using max of:
     *         - User specified minimum amount
     *         - Internal slippage protection (MAX_SWAP_SLIPPAGE_BPS)
     *      4. Executes swap via Uniswap exactInputSingle
     *      5. Validates received ULTI amount meets minimum requirements
     * @param inputAmountToSwap Amount of input token to swap
     * @param minUltiAmount Minimum amount of ULTI tokens to receive
     * @param twap Current time-weighted average price used for calculations
     * @param deadline The timestamp after which the transaction will revert
     * @return ultiAmount The amount of ULTI tokens received from the swap
     */
    function _swapInputTokenForUlti(uint256 inputAmountToSwap, uint256 minUltiAmount, uint256 twap, uint256 deadline)
        private
        returns (uint256 ultiAmount)
    {
        if (inputAmountToSwap == 0) revert PumpInsufficientInputTokenAmount();
        if (minUltiAmount == 0) revert PumpInsufficientMinimumUltiAmount();

        // 2. Calculate expected output without slippage
        uint256 expectedUltiAmountWithoutSlippage = inputAmountToSwap * 1e18 / twap;

        // 3. Choose the higher minimum amount between user-specified and internal slippage protection
        uint256 minUltiAmountInternal =
            (expectedUltiAmountWithoutSlippage * (10000 - ULTIShared.MAX_SWAP_SLIPPAGE_BPS)) / 10000;
        uint256 effectiveMinUltiAmount = minUltiAmount > minUltiAmountInternal ? minUltiAmount : minUltiAmountInternal;

        // 4. Execute swap
        ISwapRouter.ExactInputSingleParams memory params = ISwapRouter.ExactInputSingleParams({
            tokenIn: inputTokenAddress,
            tokenOut: address(this),
            fee: ULTIShared.LP_FEE,
            recipient: msg.sender,
            deadline: deadline,
            amountIn: inputAmountToSwap,
            amountOutMinimum: effectiveMinUltiAmount,
            sqrtPriceLimitX96: 0
        });

        ultiAmount = uniswapRouter.exactInputSingle(params);

        // 5. Validate output amount
        if (ultiAmount < effectiveMinUltiAmount) {
            revert PumpInsufficientUltiOutput();
        }

        return ultiAmount;
    }

    /**
     * @notice Keeps track of how many times a user has pumped in a cycle
     * @dev Adds pumper to set if not present and increments their pump count.
     *      Using unchecked is safe since pump counts are limited by MAX_PUMPS_FOR_ACTIVE_PUMPERS.
     *      For new pumpers, incrementing from 0 gives us 1.
     *      For existing pumpers, we increment their current count.
     * @param cycle The current cycle number
     * @param pumper The address of the user who performed the pump
     */
    function _updatePumpCount(uint32 cycle, address pumper) private {
        pumpers[cycle].add(pumper);
        unchecked {
            pumpCounts[cycle][pumper]++;
        }
    }

    /**
     * @notice Gets a list of all addresses that have participated in pumping during a specific cycle
     * @dev Retrieves pumper addresses as an array from EnumerableSet
     * @param cycle The cycle number to get pumpers for
     * @return An array of addresses representing all pumpers in the specified cycle
     */
    function getPumpers(uint32 cycle) external view returns (address[] memory) {
        return pumpers[cycle].values();
    }

    /**
     * @notice Gets a list of all active pumpers (those who met minimum pump threshold) for a specific cycle
     * @dev Active pumpers must have at least MIN_PUMPS_FOR_ACTIVE_PUMPERS pumps
     * @param cycle The cycle number to get active pumpers for
     * @return Array of addresses representing active pumpers in the specified cycle
     */
    function getActivePumpers(uint32 cycle) external view returns (address[] memory) {
        EnumerableSet.AddressSet storage cyclePumpers = pumpers[cycle];
        uint256 totalPumpers = cyclePumpers.length();

        // First pass: count active pumpers
        uint32 activeCount = 0;
        for (uint32 i = 0; i < totalPumpers; i++) {
            address pumper = cyclePumpers.at(i);
            if (_isActivePumper(cycle, pumper)) {
                activeCount++;
            }
        }

        // Second pass: populate active pumpers array
        address[] memory activePumpers = new address[](activeCount);
        uint32 currentIndex = 0;
        for (uint32 i = 0; i < totalPumpers; i++) {
            address pumper = cyclePumpers.at(i);
            if (_isActivePumper(cycle, pumper)) {
                activePumpers[currentIndex] = pumper;
                currentIndex++;
            }
        }

        return activePumpers;
    }

    // ===============================================
    // Contributors Management
    // ===============================================

    /**
     * @notice Updates a contributor's activity and rewards for the current cycle
     * @dev Executes the following steps:
     *      1. Updates contributor's total deposits and referrals for the cycle
     *      2. Updates top contributors ranking with new contribution
     *      3. Calculates and increments the total top contributor bonus based on the current ULTI allocated + streak bonus
     * @param cycle The current cycle number
     * @param contributorAddress The address of the contributor
     * @param inputTokenDeposited Amount of input token deposited by the contributor
     * @param inputTokenReferred Amount of input token referred by the contributor
     * @param ultiAllocated Amount of ULTI allocated for the contributor
     * @return cycleContribution The discounted contribution of the user for the cycle
     */
    function _updateContributors(
        uint32 cycle,
        address contributorAddress,
        uint256 inputTokenDeposited,
        uint256 inputTokenReferred,
        uint256 ultiAllocated
    ) private returns (uint256 cycleContribution) {
        // 1. Update contributor's total deposits and referrals for the cycle
        totalInputTokenDeposited[cycle][contributorAddress] += inputTokenDeposited;
        totalInputTokenReferred[cycle][contributorAddress] += inputTokenReferred;
        totalUltiAllocated[cycle][contributorAddress] += ultiAllocated;

        // 2. Calculate discounted contribution with sniping protection
        uint256 currentContribution =
            (ultiAllocated * _getSnipingProtectionFactor(getCurrentDayInCycle())) / ULTIShared.PRECISION_FACTOR_1E6;

        // 3. Update total discounted contribution
        cycleContribution = discountedContributions[cycle][contributorAddress] + currentContribution;
        discountedContributions[cycle][contributorAddress] = cycleContribution;

        // 2. Update top contributors ranking with new contribution
        _updateTopContributors(cycle, contributorAddress, cycleContribution);

        // 3. Calculate and add bonus rewards: 3% of allocation size
        uint256 tcBonus = ultiAllocated * ULTIShared.TOP_CONTRIBUTOR_BONUS_PERCENTAGE / 100;
        topContributorsBonuses[cycle] += tcBonus;
    }

    /**
     * @notice Updates the list of top contributors for a cycle for any contribution being made (direct or for referrer)
     * @dev Processes the update through the following steps:
     *      1. Gets the current top contributors mapping for the cycle
     *      2. Calculates the updated discounted contribution for the contributor
     *      3. Caches minimum contribution
     *      4. If less than max contributors (33):
     *         - Adds or updates the contributor directly
     *         - Updates minimum contribution tracking if needed
     *      5. Most common case: early exits if contribution not higher than minimum
     *      6. Try to set the new contributor or update the existing contribution
     *      7. Finds new minimum contributor by iterating through all contributors
     *      8. Updates minimum tracking variables
     * @param cycle The current cycle number
     * @param contributorAddress The address of the contributor to update or add
     * @param cycleContribution The discounted contribution of the user for the cycle
     */
    function _updateTopContributors(uint32 cycle, address contributorAddress, uint256 cycleContribution) private {
        // 1. Get current top contributors mapping
        EnumerableMap.AddressToUintMap storage _topContributors = topContributors[cycle];
        uint256 length = _topContributors.length();

        // 3. Cache minimum contribution
        uint256 minContribution = minDiscountedContribution[cycle];

        // 4. Handle case when below max contributors
        if (length < ULTIShared.MAX_TOP_CONTRIBUTORS) {
            _topContributors.set(contributorAddress, cycleContribution);

            // Update min contribution if this is the first entry or new minimum
            if (length == 0 || cycleContribution < minContribution) {
                minDiscountedContribution[cycle] = cycleContribution;
                minContributorAddress[cycle] = contributorAddress;
            }

            // Emit event for new or updated contributor
            emit TopContributorsUpdated(cycle, contributorAddress, address(0), cycleContribution);
            return;
        }

        // 5. Most common case: early exit if contribution is not higher than current minimum
        // Note: In case of ties (equal discounted contributions), existing minimum top contributors maintain their position
        if (cycleContribution <= minContribution) {
            return;
        }

        // 6. Try to set the new contributor or update the existing contribution
        address removedContributorAddress;
        if (_topContributors.set(contributorAddress, cycleContribution)) {
            // Only remove minContributor if contributorAddress is a new entry
            _topContributors.remove(minContributorAddress[cycle]);
            removedContributorAddress = minContributorAddress[cycle];
        }

        // 7. Find new minimum contributor by iterating through all contributors
        uint256 newMinContribution = type(uint256).max;
        address newMinContributor = address(0);
        length = _topContributors.length();
        for (uint8 i = 0; i < length; i++) {
            (address currentContributor, uint256 currentContribution) = _topContributors.at(i);
            if (currentContribution < newMinContribution) {
                newMinContribution = currentContribution;
                newMinContributor = currentContributor;
            }
        }

        // 8. Update minimum tracking variables
        minDiscountedContribution[cycle] = newMinContribution;
        minContributorAddress[cycle] = newMinContributor;

        // Emit event for the update
        emit TopContributorsUpdated(cycle, contributorAddress, removedContributorAddress, cycleContribution);
    }

    /**
     * @notice Distributes bonus ULTI tokens to the top contributors from a past cycle
     * @dev Processes bonus distribution through these steps:
     *      1. Gets total bonus amount allocated for cycle and skips if 0 or future cycle
     *      2. Calculates total contribution across all top contributors
     *      3. For each top contributor:
     *         - Calculates proportional bonus based on their contribution
     *         - Adds 3.3% extra if they were an active pumper (>= 10 pumps)
     *         - Adds bonus to their claimable amount
     *      4. Marks cycle bonuses as distributed
     *      5. Emits event with distribution details
     * @param cycle The cycle for which to distribute bonuses
     */
    function _allocateTopContributorsBonuses(uint32 cycle) private {
        // 1. Get the total bonus amount allocated for this cycle
        uint256 topContributorsBonusAmount = topContributorsBonuses[cycle];

        // Skip if no bonuses amount were allocated for this cycle
        if (topContributorsBonusAmount == 0) {
            isTopContributorsBonusAllocated[cycle] = true;
            return;
        }

        // Skip if trying to distribute bonuses for current or future cycles
        if (cycle >= getCurrentCycle()) {
            return;
        }

        // 2. Calculate total contribution
        EnumerableMap.AddressToUintMap storage _topContributors = topContributors[cycle];
        uint256 totalTopContributorsContribution = 0;
        uint256 length = _topContributors.length();
        for (uint8 i = 0; i < length; i++) {
            (, uint256 contribution) = _topContributors.at(i);
            totalTopContributorsContribution += contribution;
        }

        // 3. Calculate and allocate bonuses for each top contributor
        for (uint8 i = 0; i < length; i++) {
            (address contributor, uint256 relativeContribution) = _topContributors.at(i);

            // Calculate base bonus proportional to contribution
            uint256 bonus = (topContributorsBonusAmount * relativeContribution) / totalTopContributorsContribution;

            // Apply active pumper bonus if they qualify
            if (_isActivePumper(cycle, contributor) && bonus > 0) {
                bonus = bonus * (100 + ULTIShared.ACTIVE_PUMPERS_BONUS_PERCENTAGE) / 100;
            }

            if (bonus > 0) {
                claimableBonuses[contributor] += bonus;
            }
        }

        // 4. Mark as distributed
        isTopContributorsBonusAllocated[cycle] = true;

        // 5. Emit event
        emit TopContributorBonusesDistributed(cycle, topContributorsBonusAmount);
    }

    /**
     * @notice Checks if a given address is a top contributor for a specific cycle
     * @dev External wrapper function that calls internal _isTopContributor
     * @param cycle The cycle number to check
     * @param user The address to check
     * @return bool True if the address is a top contributor for the specified cycle
     */
    function isTopContributor(uint32 cycle, address user) public view returns (bool) {
        return _isTopContributor(cycle, user);
    }

    /**
     * @notice Internal function to check if an address is a top contributor
     * @dev Uses EnumerableMap's contains function to efficiently check if the address exists in the top contributors mapping
     * @param cycle The cycle number to check
     * @param user The address to check
     * @return bool True if the address is a top contributor for the specified cycle
     */
    function _isTopContributor(uint32 cycle, address user) internal view returns (bool) {
        return topContributors[cycle].contains(user);
    }

    /**
     * @notice Gets the list of top contributors for a specific cycle
     * @dev Retrieves the top contributors list by calling _getTopContributors to fetch the data
     * @param cycle The cycle number to get the top contributors for
     * @return An array of TopContributor structs representing the top contributors
     */
    function getTopContributors(uint32 cycle) external view returns (ULTIShared.TopContributor[] memory) {
        return _getTopContributors(cycle);
    }

    /**
     * @notice Gets a list of all top contributors and their contribution details for a given cycle
     * @dev Function execution steps:
     *      1. Get the mapping of top contributors for the specified cycle
     *      2. Create a new array to store the top contributors data
     *      3. For each top contributor:
     *         - Get their address and discounted contribution amount
     *         - Fetch their full contribution details (input token deposited/referred, ULTI allocated, pump count)
     *         - Store all data in the array
     *      4. Return the populated array
     * @param cycle The cycle number to get the top contributors for
     * @return An array of TopContributor structs representing the top contributors
     */
    function _getTopContributors(uint32 cycle) private view returns (ULTIShared.TopContributor[] memory) {
        // 1. Get mapping of top contributors for this cycle
        EnumerableMap.AddressToUintMap storage _topContributors = topContributors[cycle];
        uint256 length = _topContributors.length();

        // 2. Create array to store top contributors data
        ULTIShared.TopContributor[] memory topContributorsArray = new ULTIShared.TopContributor[](length);

        // 3. Populate array with each top contributor's full details
        for (uint8 i = 0; i < length; i++) {
            (address contributorAddress, uint256 discountedContribution) = _topContributors.at(i);
            topContributorsArray[i] = ULTIShared.TopContributor({
                contributorAddress: contributorAddress,
                inputTokenDeposited: totalInputTokenDeposited[cycle][contributorAddress],
                inputTokenReferred: totalInputTokenReferred[cycle][contributorAddress],
                ultiAllocated: totalUltiAllocated[cycle][contributorAddress],
                discountedContribution: discountedContribution,
                pumpCount: pumpCounts[cycle][contributorAddress]
            });
        }

        // 4. Return the populated array
        return topContributorsArray;
    }

    // ===============================================
    // Referral System
    // ===============================================

    /**
     * @notice Processes referral bonuses (2-way) when a user makes a deposit
     * @dev Execution steps:
     *      1. Gets effective referrer (stored or provided)
     *      2. Updates referrer mapping if not already set and valid referrer provided
     *      3. If valid referrer exists:
     *         a. Cap referral bonus based on skin-in-game limit
     *         b. Initialize next bonus claim timestamp for referrer if needed
     *         c. Update referrer's allocated bonuses and contributions
     *         d. Calculate and allocate referred user bonus (33% of referrer bonus)
     * @param referrer The address of the referrer
     * @param inputTokenReferred The amount of input token deposited by user (referred by referrer)
     * @param ultiToMint The amount of ULTI tokens to mint for the depositor before calculating the referral bonuses
     * @param cycle The current cycle number
     * @return effectiveReferrer The actual referrer used (stored or provided)
     * @return referrerBonus The amount of bonus tokens allocated to the referrer
     * @return referredBonus The amount of bonus tokens allocated to the referred user
     */
    function _updateReferrals(address referrer, uint256 inputTokenReferred, uint256 ultiToMint, uint32 cycle)
        private
        returns (address effectiveReferrer, uint256 referrerBonus, uint256 referredBonus)
    {
        // 1. Get effective referrer - use stored if available, otherwise use provided
        effectiveReferrer = referrers[msg.sender] != address(0) ? referrers[msg.sender] : referrer;

        // 2. Update referrer mapping if not already set and valid referrer provided: not set, not zero. Not circular already checked in `_deposit`
        if (referrers[msg.sender] == address(0) && referrer != address(0)) {
            referrers[msg.sender] = referrer;
        }

        // 3. Calculate referrer bonus if valid effective referrer exists
        if (effectiveReferrer != address(0)) {
            referrerBonus = (ultiToMint * _getReferralBonusPercentage(cycle)) / (100 * ULTIShared.PRECISION_FACTOR_1E6);

            // 3a. Cap referral bonus based on skin-in-game limit (10X of total ULTI allocated ever)
            // Note: if the cap is reached, no referrer and referred bonuses will be accumulated.
            uint256 skinInAGameCap =
                totalUltiAllocatedEver[effectiveReferrer] * ULTIShared.REFERRAL_SKIN_IN_THE_GAME_CAP_MULTIPLIER;
            uint256 remainingBonusAllowance = skinInAGameCap > accumulatedReferralBonuses[effectiveReferrer]
                ? skinInAGameCap - accumulatedReferralBonuses[effectiveReferrer]
                : 0;
            referrerBonus = referrerBonus > remainingBonusAllowance ? remainingBonusAllowance : referrerBonus;

            if (referrerBonus > 0) {
                // 3b. Initialize next bonus claim timestamp for referrer if not already set
                if (nextAllBonusesClaimTimestamp[effectiveReferrer] == 0) {
                    nextAllBonusesClaimTimestamp[effectiveReferrer] =
                        block.timestamp + ULTIShared.ALL_BONUSES_CLAIM_INTERVAL;
                }

                // 3c. Update referrer's allocated bonuses and contributions
                claimableBonuses[effectiveReferrer] += referrerBonus;
                accumulatedReferralBonuses[effectiveReferrer] += referrerBonus;
                _updateContributors(cycle, effectiveReferrer, 0, inputTokenReferred, referrerBonus);

                // 3d. Calculate and allocate referred user bonus
                referredBonus = (referrerBonus * ULTIShared.REFERRAL_BONUS_FOR_REFERRED_PERCENTAGE) / 100;
                claimableBonuses[msg.sender] += referredBonus;
                // The bonus for referred users encourages the use of referral links over independent deposits.
                // This increases confidence in the referral program's effectiveness among referrers.
                // Note that this small additional bonus is excluded from the depositor's total contribution.
            }
        }

        return (effectiveReferrer, referrerBonus, referredBonus);
    }

    // ===============================================
    // Streak Management
    // ===============================================

    /**
     * @notice Calculates bonus rewards for users who consistently deposit across multiple cycles
     * @dev Calculates streak bonus through following steps:
     *      1. Updates user's streak count based on deposit history
     *      2. Checks if streak is long enough for bonus (min 4 cycles)
     *      3. Calculates bonus percentage based on streak length:
     *         - Uses formula: maxBonus + 1 - (1/streakCount)
     *         - Scales values by precision factor
     *      4. Applies bonus percentage to base ULTI amount
     * @param user The address of the user
     * @param inputTokenDeposited The amount of input token deposited
     * @param ultiToMintWithoutBonus The amount of ULTI to be minted for the deposit without bonus
     * @param cycle The current cycle number
     * @return The streak bonus amount allocated
     * @return The streak count
     */
    function _updateStreakBonus(address user, uint256 inputTokenDeposited, uint256 ultiToMintWithoutBonus, uint32 cycle)
        private
        returns (uint256, uint32)
    {
        // 1. Update streak count
        uint32 streakCount = _updateStreakCount(cycle, user, inputTokenDeposited);

        // 2. Check minimum streak count requirement
        if (streakCount < ULTIShared.STREAK_BONUS_COUNT_START) {
            return (0, streakCount);
        }

        // 3. Calculate streak bonus percentage
        uint256 streakBonusPercentage =
            ULTIShared.STREAK_BONUS_MAX_PLUS_ONE_SCALED - (ULTIShared.PRECISION_FACTOR_1E6 / streakCount); // scaled by 1e6

        // 4. Calculate final bonus amount
        uint256 streakBonus = ultiToMintWithoutBonus * streakBonusPercentage / ULTIShared.PRECISION_FACTOR_1E6;

        claimableBonuses[msg.sender] += streakBonus;

        return (streakBonus, streakCount);
    }

    /**
     * @notice Updates a user's streak of consecutive cycles with deposits
     * @dev Main execution steps:
     *      1. Handle first cycle as special case:
     *         - Set streak count to 1 since no previous cycle exists
     *      2. For subsequent cycles:
     *         - Get previous cycle's total deposits
     *         - Calculate current cycle's total deposits including new deposit
     *         - Get previous streak count
     *         - Check if current deposits are within valid range (1X-10X of previous)
     *         - Increment streak if valid, reset to 1 if invalid
     *      3. Store and return new streak count
     * @param cycle The current cycle number
     * @param user The address of the user
     * @param inputTokenDeposited The amount of input token being deposited
     * @return The updated streak count for the user
     */
    function _updateStreakCount(uint32 cycle, address user, uint256 inputTokenDeposited) private returns (uint32) {
        // Cache storage reads
        uint32 newStreakCount;

        // 1. Handle first cycle as special case: no previous cycle to look up
        if (cycle == 1) {
            newStreakCount = 1;
        } else {
            // 2. Calculate total deposits for current and previous cycles
            uint256 previousCycleDeposits = totalInputTokenDeposited[cycle - 1][user];
            uint256 currentCycleDeposits = totalInputTokenDeposited[cycle][user] + inputTokenDeposited;

            // Compute streak validity in a single condition
            bool validStreak =
                currentCycleDeposits >= previousCycleDeposits && currentCycleDeposits <= 10 * previousCycleDeposits;

            // Update streak count based on validity: increment if valid, reset to 1 if invalid (break the streak)
            newStreakCount = validStreak ? streakCounts[cycle - 1][user] + 1 : 1;
        }

        // 3. Store and return new streak count
        streakCounts[cycle][user] = newStreakCount;
        return newStreakCount;
    }

    // ===============================================
    // Cycle & Time Management
    // ===============================================

    /**
     * @notice Returns the current cycle number
     * @dev Calculates the current cycle number through these steps:
     *      1. Gets time elapsed since launch by subtracting launch timestamp from current time
     *      2. Divides elapsed time by cycle duration to get number of completed cycles
     *      3. Adds 1 to account for current ongoing cycle
     *      4. Converts result to uint32 for storage efficiency
     * @return The current cycle number
     */
    function getCurrentCycle() public view returns (uint32) {
        return uint32((block.timestamp - launchTimestamp) / ULTIShared.CYCLE_INTERVAL) + 1;
    }

    /**
     * @notice Returns which day we are currently in within the cycle (1-33)
     * @dev Uses modulo to get elapsed time within current cycle, then converts to days
     * @return The current day number (1-33) within the cycle
     */
    function getCurrentDayInCycle() public view returns (uint8) {
        return uint8(((block.timestamp - launchTimestamp) % ULTIShared.CYCLE_INTERVAL) / 1 days + 1);
    }

    /**
     * @notice Retrieves the referral bonus percentage value for a specific cycle
     * @dev Provides external access to the internal referral bonus percentage values
     * @param cycle The cycle number to fetch the percentage for
     * @return The referral bonus percentage value for the specified cycle
     */
    function getReferralBonusPercentage(uint32 cycle) external pure returns (uint32) {
        return _getReferralBonusPercentage(cycle);
    }

    /// @notice Referral Bonus Percentage Array - used to normalize down the weight of bonuses and soften inflation overtime
    /// @dev This array represents the exponentially decaying referral percentage for each cycle.
    /// It starts at 33% for cycle 1, reaches 3% by cycle 33, then remains at 3% forever.
    /// Mathematical formula: A(i) = max(33% * (3% / 33%)^(i / 32), 3%)
    /// Array contains discrete values for cycles 1 to 33
    /// Each value is scaled by 10^6 for precision (33% => 33,000,000)
    /// Usage:
    /// - Index 0 corresponds to cycle 1
    /// - Index 32 corresponds to cycle 33
    /// - To apply percentage: actualValue = (originalValue * _getReferralBonusPercentage(cycleNumber)) / 100_000_000
    /// @param cycle The cycle number to get the percentage for
    /// @return The referral bonus percentage value for the specified cycle, scaled by 10^6
    function _getReferralBonusPercentage(uint32 cycle) internal pure returns (uint32) {
        if (cycle <= ULTIShared.ULTI_NUMBER) {
            // Pre-computed values for cycles 1-33
            uint32[33] memory percentages = [
                33000000,
                30617548,
                28407099,
                26356235,
                24453433,
                22688006,
                21050034,
                19530316,
                18120316,
                16812110,
                15598352,
                14472221,
                13427392,
                12457995,
                11558584,
                10724106,
                9949874,
                9231538,
                8565062,
                7946703,
                7372987,
                6840691,
                6346824,
                5888612,
                5463480,
                5069042,
                4703080,
                4363538,
                4048511,
                3756226,
                3485044,
                3233439,
                3000000
            ];
            return percentages[cycle - 1];
        } else {
            return 3000000; // 3% for all cycles after 33
        }
    }

    /**
     * @notice Retrieves the sniping protection factor for a given day within the current cycle
     * @dev Uses the internal _getSnipingProtectionFactor function to fetch the factor
     * @param dayInCycle The day number within the current cycle (1-33)
     * @return The sniping protection factor for the given day, scaled by 10^6
     */
    function getSnipingProtectionFactor(uint8 dayInCycle) external pure returns (uint32) {
        return _getSnipingProtectionFactor(dayInCycle);
    }

    /// @notice Sniping Protection Factor Array - used as last minute snipping protection when updating top contributors
    /// @dev This array represents a logistic function that creates a sharply falling curve.
    /// It smoothly transitions from 100% protection at the start of the cycle
    /// to approximately ~1% protection at the end of the cycle.
    /// Mathematical formula: f(d) = 3 / (1 + exp(0.4 * (d - 35) + 0.09)) - 2
    /// Where:
    ///   d: day of the cycle (1 to 33)
    ///   f(d): discounting factor for day d
    /// Array contains discrete values for d = [1, 33]
    /// Each value is scaled by 10^6 for precision (~1X =>  999,996)
    /// Usage:
    /// - Input 1 corresponds to day 1 of the cycle
    /// - Input 33 corresponds to day 33 of the cycle
    /// - To apply discount: actualValue = (originalValue * getSnipingProtectionFactor(dayOfCycle)) / 100_000_000
    /// @param dayInCycle The day number within the current cycle (1-33)
    /// @return The sniping protection factor for the given day, scaled by 10^6
    function _getSnipingProtectionFactor(uint8 dayInCycle) internal pure returns (uint32) {
        if (dayInCycle < 1 || dayInCycle > ULTIShared.ULTI_NUMBER) {
            revert SnipingProctectionInvalidDayInCycle(dayInCycle);
        }

        uint32[33] memory factors = [
            uint32(999996),
            uint32(999994),
            uint32(999991),
            uint32(999986),
            uint32(999980),
            uint32(999970),
            uint32(999955),
            uint32(999933),
            uint32(999900),
            uint32(999851),
            uint32(999778),
            uint32(999668),
            uint32(999505),
            uint32(999262),
            uint32(998899),
            uint32(998358),
            uint32(997551),
            uint32(996348),
            uint32(994556),
            uint32(991885),
            uint32(987911),
            uint32(982000),
            uint32(973227),
            uint32(960234),
            uint32(941060),
            uint32(912913),
            uint32(871910),
            uint32(812842),
            uint32(729106),
            uint32(613057),
            uint32(457184),
            uint32(256387),
            uint32(11203)
        ];
        return factors[dayInCycle - 1];
    }
}
