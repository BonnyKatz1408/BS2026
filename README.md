# 🔍 BlockSentinel — Token Security Analysis Platform

**BlockSentinel** is a comprehensive **Ethereum token contract risk analyzer** with a web dashboard, real-time security scanning, paper trading simulator, and historical scan tracking. It performs multi-layer static and dynamic analysis to detect honeypots, rug pulls, and suspicious contract behaviors.

---

##  Quick Start

### Prerequisites
- **Python 3.8+**
- **MySQL 5.7+** (optional, for scan history and user accounts)
- **Google Gemini API key** (optional, for AI-powered analysis)
- **Etherscan API key** (for contract source code retrieval)
- **Ethereum RPC endpoint** (Infura, Alchemy, or local node)

### Installation

1. **Clone and setup environment:**
   ```bash
   cd d:\PROTEX\pro\"New folder"
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or: source .venv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   Create a `.env` file in the project root with:
   ```env
   # Flask
   SECRET_KEY=your-secret-key-change-in-production
   FLASK_ENV=production
   
   # MySQL (optional - required for user accounts & scan history)
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your-password
   MYSQL_DATABASE=blocksentinel
   MYSQL_PORT=3306
   
   # APIs
   ETHERSCAN_API_KEY=your-etherscan-key
   ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/your-key
   GOOGLE_GEMINI_API_KEY=your-gemini-key
   ```

4. **Initialize MySQL database (optional):**
   ```bash
   python -c "import utils.scan_history_db; utils.scan_history_db.init_schema()"
   python -c "import core.auth_web as auth_web; auth_web._create_users_table()"
   ```

5. **Run Flask server:**
   ```bash
   python main.py
   ```
   Server will start at `http://127.0.0.1:5000`

---

## 📋 What BlockSentinel Does

### Core Features

| Feature | Description |
|---------|-------------|
| **Contract Analysis** | Submit an ERC-20 contract address and get a comprehensive risk assessment including honeypot detection, rugpull heuristics, liquidity analysis, tax calculations, and more |
| **Risk Scoring** | Unified 0-100 risk score combining 8+ specialized detectors (honeypot, rugpull, liquidity, holders, minting, taxes, transactions, age) |
| **Real-time Dashboard** | Interactive web UI with risk cards, probability bars, radar charts, holder distribution, token info, and live trade simulation |
| **Dynamic Simulation** | Test buy/sell scenarios on Uniswap to detect trading restrictions, tax traps, and honeypot signals |
| **Paper Trading** | Practice trading with virtual ETH balance; prices from Uniswap V2/V3 with DexScreener embeds |
| **Scan History** | Track all token analyses with historical risk trends and severity comparisons |
| **User Accounts** | Session-based authentication with profiles and avatar uploads |

### Analysis Detectors

1. **Honeypot Detector** - Identifies contracts that prevent token selling
2. **Rugpull Detector** - Detects liquidity lock/burn patterns and ownership risks
3. **Liquidity Analyzer** - Checks pool health, ETH depth, and lock status
4. **Holder Concentration** - Analyzes top 10 wallet distribution for centralization
5. **Tax Calculator** - Extracts hardcoded buy/sell tax rates from contract
6. **Minting/Admin Controls** - Detects owner privileges and contract upgrade paths
7. **Transaction Analyzer** - Reviews recent trading patterns and volume anomalies
8. **Age Detector** - Estimates contract creation date and age risk
9. **Slither Analysis** - Static security scan for contract vulnerabilities
10. **Gemini AI** - Semantic analysis of contract source code for malicious patterns

---

## 📁 Project Structure

```
d:\PROTEX\pro\New folder\
├── main.py                          # Flask entry point - routes & API endpoints
├── requirements.txt                 # Python dependencies
├── .env                             # Configuration (GIT IGNORED)
│
├── detectors/                       # Analysis modules
│   ├── honeypot_v1.py
│   ├── rugpull_v1.py
│   ├── liquidity_v1.py
│   ├── holder_v1.py
│   ├── minting_v1.py
│   ├── age_v1.py
│   ├── transaction_v1.py
│   ├── liquidity_history_v1.py
│
├── utils/                           # Utilities & services
│   ├── db_common.py                 # MySQL connection pooling
│   ├── scan_history_db.py           # Scan storage & retrieval
│   ├── etherscan_client.py          # Etherscan API client
│   ├── engine.py                    # Simulation engine (Web3)
│   ├── gemini_service.py            # AI analysis service
│   ├── scoring_engine.py            # Risk score calculation
│   ├── validator.py                 # Address validation
│   ├── tax_calc.py                  # Tax rate extraction
│
├── tools/                           # Feature modules
│   ├── paper_trading/
│   │   ├── paper_trading.py
│   │   ├── paper_trading_db.py
│   │   └── paper_trading_auto.py
│   └── scenarios.py
│
├── core/                            # Core services
│   └── auth_web.py                  # Authentication & user routes
│
├── templates/                       # Jinja2 templates
│   ├── dashboard.html               # Main dashboard (Chart.js visualizations)
│   ├── index.html                   # Home page
│   ├── login.html                   # Login/signup form
│   ├── profile.html                 # User profile page
│   └── Report.html                  # PDF report template
│
├── static/                          # Static files
│   └── uploads/avatars/             # User profile pictures
│
└── crytic-export/                   # Slither contract analysis cache
    └── etherscan-contracts/
```

---

## 🗄️ MySQL Database Schema

### Table 1: `users` (Authentication & Profiles)

Stores user account information and settings.

```sql
CREATE TABLE users (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  FirstName VARCHAR(100) NOT NULL,
  LastName VARCHAR(100) NOT NULL,
  username VARCHAR(255) NOT NULL UNIQUE,          -- Email address (login)
  password VARCHAR(255) NOT NULL,                  -- bcrypt hash
  mobile_number VARCHAR(20) NULL,
  bio TEXT NULL,
  country VARCHAR(100) NULL,
  profile_pic VARCHAR(500) NULL,                   -- Path to uploaded avatar
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Key Columns:**
- `username`: Email used for login (must be unique)
- `password`: Bcrypt hashed (never stored in plain text)
- `profile_pic`: Relative path to avatar (stored in `static/uploads/avatars/`)

---

### Table 2: `token_scan_snapshots` (Analysis History)

Stores all token analyses with snapshot data and full responses.

```sql
CREATE TABLE token_scan_snapshots (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  contract_address VARCHAR(42) NOT NULL,           -- ERC-20 token address (0x...)
  chain VARCHAR(32) NOT NULL DEFAULT 'ethereum',   -- Blockchain (ethereum, polygon, etc.)
  scanned_at DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
  analysis_mode VARCHAR(16) NOT NULL DEFAULT 'full',  -- 'full' or 'lite'
  numeric_score INT NOT NULL,                      -- 0-100 risk score
  risk_level VARCHAR(32) NOT NULL,                 -- 'safe', 'warning', 'danger'
  confidence_score INT NULL,                       -- 0-100 confidence in score
  honeypot_status VARCHAR(32) NULL,                -- 'pass', 'fail', 'warning'
  rugpull_status VARCHAR(32) NULL,
  liquidity_status VARCHAR(32) NULL,
  minting_status VARCHAR(32) NULL,
  sim_status VARCHAR(32) NULL,
  is_sellable TINYINT(1) NULL,                     -- 0: honeypot, 1: sellable, NULL: unknown
  token_symbol VARCHAR(64) NULL,
  token_name VARCHAR(255) NULL,
  scanned_by_username VARCHAR(255) NULL,
  snapshot_json JSON NOT NULL,
  full_response_json JSON NULL,
  
  INDEX idx_contract_scanned (contract_address, scanned_at),
  INDEX idx_scanned (scanned_at),
  INDEX idx_risk_level (risk_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Key Columns:**
- `contract_address`: Token contract address (primary search key)
- `numeric_score`: Final 0-100 risk score
- `snapshot_json`: Lightweight summary for display
- `full_response_json`: Complete detector results

---

## 🌐 API Endpoints

### Public Endpoints (No Authentication Required)

#### 1. **Analyze Token** (Full Analysis)
```http
POST /api/v1/analyze
Content-Type: application/json

{
  "contract_address": "0xBa25B2281214300E4e649feAd9A6d6acD25f1c0a"
}
```

**Response:**
```json
{
  "success": true,
  "contract_address": "0x...",
  "numeric_score": 45,
  "risk_level": "warning",
  "detectors": {
    "honeypot": { "score": 40, "status": "Warning" },
    "rugpull": { "score": 50, "status": "Warning" },
    "liquidity": { "score": 35, "status": "Pass" }
  },
  "token_metadata": {
    "name": "Tree",
    "symbol": "TREE",
    "decimals": 18,
    "holders": 12345
  }
}
```

#### 2. **Analyze Token** (Fast/Lite)
```http
POST /api/v1/analyze-lite
Content-Type: application/json

{
  "contract_address": "0x..."
}
```
*Runs lightweight detectors only; skips Slither/Gemini for speed.*

---

#### 3. **Simulate Trade**
```http
POST /api/v1/simulate
Content-Type: application/json

{
  "contract_address": "0x...",
  "eth_amount": 1.0,
  "claimed_tokens": 500000
}
```

**Response:**
```json
{
  "success": true,
  "expected_tokens_out_human": 489250,
  "slippage_pct": 2.15,
  "is_honeypot": false
}
```

---

## 🔑 Environment Configuration

Create `.env` file with these variables:

```env
# === Flask Settings ===
SECRET_KEY=your-random-secret-key-minimum-32-chars-
FLASK_ENV=production
DEBUG=false

# === MySQL Database (Optional) ===
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-secure-password
MYSQL_DATABASE=blocksentinel
MYSQL_PORT=3306

# === External APIs ===
ETHERSCAN_API_KEY=your-etherscan-key
ETHEREUM_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/your-key
GOOGLE_GEMINI_API_KEY=your-gemini-key
```

---

## 🚦 Running the Application

### Development

```bash
# Activate virtual environment
.venv\Scripts\activate

# Start Flask development server
python main.py
```

Server runs at **http://127.0.0.1:5000**

### Production

Use a production WSGI server:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main:app
```

---

## 📊 Analysis Flow

1. User submits contract address on dashboard
2. Frontend makes `POST /api/v1/analyze` request
3. Backend **Static Detectors** run in parallel:
   - Tax Calculator
   - Liquidity Analyzer
   - Holder Concentration
   - Minting Controls
   - Transaction Analyzer
   - Age Detector
4. **Dynamic Simulation** tests buy/sell on Uniswap
5. **Slither** static analysis (if available)
6. **Gemini AI** semantic analysis of source code
7. **Scoring Engine** combines all results → 0-100 risk score
8. Response cached in MySQL (if enabled)
9. Results displayed on dashboard with charts

---


