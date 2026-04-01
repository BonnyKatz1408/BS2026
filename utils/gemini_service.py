import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Using Flash for the fastest response times on the frontend
MODEL_NAME = "gemini-2.5-flash"
MAX_POINTS = 3
MAX_CHARS = 300


def _compress_points(text: str) -> str:
    """
    Force concise output:
    - max 3 bullet points
    - max ~420 chars
    """
    if not text:
        return " - No clear AI summary generated."

    lines = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith(("•", "-", "*")):
            point = s.lstrip("•-* ").strip()
        else:
            point = s
        if point:
            lines.append(f"- {point}")
        if len(lines) >= MAX_POINTS:
            break

    if not lines:
        lines = [f"- {text.strip()}"]

    compact = "\n".join(lines)
    if len(compact) > MAX_CHARS:
        compact = compact[: MAX_CHARS - 3].rstrip() + "..."
    return compact


def _fallback_points(context_data: str) -> str:
    src = (context_data or "").lower()
    points = []
    if "honeypot" in src:
        points.append("- Honeypot indicators present; verify sellability and transfer restrictions before entry.")
    if "liquidity" in src:
        points.append("- Liquidity conditions may increase slippage and exit risk under volatility.")
    if "mint" in src or "owner" in src or "blacklist" in src:
        points.append("- Owner-control functions detected; monitor mint, pause, and blacklist permissions.")
    if "transaction" in src or "wash" in src:
        points.append("- Transaction patterns should be reviewed for bot-like or inorganic activity spikes.")
    if not points:
        points = ["- Mixed risk signals detected; verify contract, liquidity, and holder concentration manually."]
    return "\n".join(points[:MAX_POINTS])[:MAX_CHARS]

def generate_report(context_data: str) -> str:
    """
    Takes the raw JSON/dict data from the detectors and translates it 
    into a human-readable risk summary.
    """
    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY is missing from the .env file."

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        
        # PROMPT ENGINEERING: constrain length and output format for low token usage.
        system_instruction = (
            "You are an expert smart contract auditor and blockchain security analyst. "
            "Review the provided detector data and output EXACTLY 2 or 3 short bullet points. "
            "Each bullet must be <= 12 words, direct, and focused on highest-impact risks only. "
            "No intro, no conclusion, no paragraphs, no markdown headers, no extra formatting. "
            "Prefer concrete checks (honeypot, liquidity, ownership, taxes, tx anomalies)."
        )
        
        # Combine the instructions with the live data passed from main.py
        full_prompt = f"{system_instruction}\n\nData to analyze:\n{context_data}"
        
        # Call the API
        response = model.generate_content(
            full_prompt,
            generation_config={"max_output_tokens": 80, "temperature": 0.15},
        )
        compact = _compress_points(response.text.strip())
        if len(compact.replace("-", "").strip()) < 20:
            return _fallback_points(context_data)
        return compact

    except Exception as e:
        print(f"Gemini API Error: {e}")
        return _fallback_points(context_data)


def get_trading_prediction(token_data: dict) -> str:
    """
    Analyzes token market data and risk profile to return a trading signal.
    Returns: "BUY", "SELL", or "HOLD".
    """
    if not GEMINI_API_KEY:
        return "HOLD"

    try:
        model = genai.GenerativeModel(MODEL_NAME)

        prompt = (
            "You are an AI crypto trading bot. Analyze the following token data and risk profile. "
            "Decide if it's a 'BUY', 'SELL', or 'HOLD'. "
            "Return ONLY one of these three words. "
            f"Token Data: {token_data}"
        )

        response = model.generate_content(
            prompt,
            generation_config={"max_output_tokens": 10, "temperature": 0.1},
        )
        signal = response.text.strip().upper()
        if "BUY" in signal:
            return "BUY"
        if "SELL" in signal:
            return "SELL"
        return "HOLD"

    except Exception as e:
        print(f"Gemini Trading Prediction Error: {e}")
        return "HOLD"

# --- Quick Test Block ---
if __name__ == "__main__":
    print("Testing Gemini API Connection...\n")
    
    # Fake data that looks exactly like what main.py will eventually send
    mock_context = (
        "Score: 85/100 (High Risk). "
        "Detectors: {'honeypot': 'Pass', 'liquidity': 'Low liquidity detected - 90% in creator wallet', 'anomalies': 'Sell taxes hit 25%'}."
    )
    
    print("Sending mock detector data to Gemini...\n")
    result = generate_report(mock_context)
    
    print("✅ SUCCESS! Here is the AI Summary:\n")
    print(result)