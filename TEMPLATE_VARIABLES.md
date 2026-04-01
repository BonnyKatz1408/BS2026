# Token Risk Report — Template Variable Reference

All placeholders follow the pattern `{{VARIABLE_NAME}}` and are safe to replace
with a simple string.replace() / regex substitution in any language.

---

## HEADER / META
| Placeholder              | Example Value                                  | Notes |
|--------------------------|------------------------------------------------|-------|
| {{TOKEN_NAME}}           | Yakushima Inu                                  | Full name |
| {{TOKEN_SYMBOL}}         | YAKUSHIMA                                      | Ticker |
| {{TOKEN_CHAIN}}          | ETHEREUM                                       | Network name |
| {{CONTRACT_ADDRESS}}     | 0xAbCd…1234                                    | Full address |
| {{GENERATION_DATE}}      | 2026-03-27                                     | ISO date |
| {{PREPARED_BY}}          | RiskBot v2.1                                   | Author / system |
| {{REPORT_BRAND}}         | RUGSCAN                                        | Footer brand name |

---

## RISK BADGE (top-right of page 1)
| Placeholder              | Allowed Values                                 |
|--------------------------|------------------------------------------------|
| {{OVERALL_RISK_CLASS}}   | critical / high / medium / low                 |
| {{OVERALL_RISK_LABEL}}   | CRITICAL / HIGH / MEDIUM / LOW                 |

---

## SCORE CARDS
| Placeholder              | Example | Notes |
|--------------------------|---------|-------|
| {{OVERALL_RISK_SCORE}}   | 88/100  | Displayed in big mono font |
| {{OVERALL_SCORE_CLASS}}  | danger / warn / ok | Controls top bar color |
| {{OVERALL_RISK_DESC}}    | Identified as critical… | Short sentence |
| {{RUGPULL_SCORE}}        | 90/100  | |
| {{RUGPULL_SCORE_CLASS}}  | danger  | |
| {{RUGPULL_SCORE_DESC}}   | High potential for… | |
| {{HONEYPOT_SCORE}}       | 85/100  | |
| {{HONEYPOT_SCORE_CLASS}} | danger  | |
| {{HONEYPOT_SCORE_DESC}}  | Significant vulnerability… | |
| {{CONFIDENCE_PCT}}       | 100%    | |
| {{CONFIDENCE_DESC}}      | High confidence in… | |

---

## ABSTRACT / ALERT
| Placeholder           | Notes |
|-----------------------|-------|
| {{ABSTRACT_TEXT}}     | 2-3 sentence summary paragraph |
| {{RISK_ALERT_TEXT}}   | Text inside the red alert box |

---

## RISK VECTORS (bars on page 1)
For each vector (RUGPULL, HONEYPOT, CONTRACT, LIQUIDITY, TAX, OWNERSHIP):

| Placeholder                 | Example         | Notes |
|-----------------------------|-----------------|-------|
| {{RUGPULL_BAR_CLASS}}       | danger          | danger / warn / ok |
| {{RUGPULL_BAR_WIDTH}}       | 90              | Numeric 0-100 (no % sign) |
| {{RUGPULL_BAR_COLOR}}       | danger          | Used as CSS var name |
| (same pattern for others)   |                 | |

---

## TOKEN SPEC TABLE (page 2)
| Placeholder                 | Example |
|-----------------------------|---------|
| {{TOKEN_NAME_INTERP}}       | Used to label the asset in interfaces… |
| {{TOKEN_SYMBOL_INTERP}}     | Compact shorthand for trading… |
| {{TOKEN_CHAIN_INTERP}}      | Indicates ERC-20 compatibility… |
| {{TOKEN_TOTAL_SUPPLY}}      | 1,000,000,000 |
| {{TOKEN_SUPPLY_INTERP}}     | Defines total tokens at deployment… |
| {{TOKEN_DECIMALS}}          | 9 |
| {{TOKEN_DECIMALS_INTERP}}   | Determines divisibility… |
| {{CONTRACT_ADDRESS_INTERP}} | Verified on Etherscan |

---

## KEY FINDINGS (page 2 — 8 findings)
For each finding N (01 through 08):

| Placeholder           | Example |
|-----------------------|---------|
| {{FINDING_N_RISK}}    | RED / YELLOW / GREEN |
| {{FINDING_N_TEXT}}    | Short description sentence |

CSS class on the pill is auto-derived from the risk word (lowercase). Make sure
you use exactly: `red`, `yellow`, or `green` as the value.

---

## HOLDER DISTRIBUTION (page 2)
| Placeholder              | Example | Notes |
|--------------------------|---------|-------|
| {{DIST_TOP10_PCT}}       | 30      | Numeric only (no %) |
| {{DIST_TOP10_FLEX}}      | 30      | Same as PCT for equal bar |
| {{DIST_TOP1_PCT}}        | 15      | |
| {{DIST_TOP1_FLEX}}       | 15      | |
| {{DIST_REST_PCT}}        | 55      | |
| {{DIST_REST_FLEX}}       | 55      | |
| {{DIST_TOP10_ANALYSIS}}  | A coordinated action… | Card body text |
| {{DIST_TOP1_ANALYSIS}}   | A single wallet… | |
| {{DIST_REST_ANALYSIS}}   | Remaining majority… | |

---

## DETAILED RISK ANALYSIS (page 3 — 4 risk types)
For each type (HONEYPOT, RUGPULL, LIQUIDITY, TOKENAGE):

| Placeholder                        | Notes |
|------------------------------------|-------|
| {{DETAIL_HONEYPOT_OVERVIEW}}       | 1-2 sentence overview |
| {{DETAIL_HONEYPOT_TECHNICAL}}      | Technical concerns paragraph |
| {{DETAIL_HONEYPOT_INVESTOR}}       | Investor implications paragraph |
| (same pattern for RUGPULL, LIQUIDITY, TOKENAGE) | |

---

## RECOMMENDATIONS (page 3)
For users (R1–R4) and developers (D1–D4):

| Placeholder     | Example |
|-----------------|---------|
| {{REC_USER_1}}  | Avoid investment until… |
| {{REC_USER_2}}  | Do not deploy capital… |
| {{REC_USER_3}}  | If exposure is held… |
| {{REC_USER_4}}  | Require evidence of… |
| {{REC_DEV_1}}   | Remediate vulnerabilities… |
| {{REC_DEV_2}}   | Strengthen liquidity protections… |
| {{REC_DEV_3}}   | Improve trust through audits… |
| {{REC_DEV_4}}   | Establish governance procedures… |

---

## CONCLUSION / DISCLAIMER
| Placeholder                | Notes |
|----------------------------|-------|
| {{FINAL_CONCLUSION_TEXT}}  | 1-2 sentence bottom-line verdict |
| {{DISCLAIMER_TEXT}}        | Legal disclaimer paragraph |

---

## Quick Python Example

```python
import re

def fill_template(template_html: str, data: dict) -> str:
    def replacer(match):
        key = match.group(1)
        return data.get(key, match.group(0))  # leave unchanged if key missing
    return re.sub(r'\{\{(\w+)\}\}', replacer, template_html)

with open("token_risk_report_template.html") as f:
    html = f.read()

report = fill_template(html, {
    "TOKEN_NAME": "Yakushima Inu",
    "TOKEN_SYMBOL": "YAKUSHIMA",
    "TOKEN_CHAIN": "ETHEREUM",
    "OVERALL_RISK_LABEL": "CRITICAL",
    "OVERALL_RISK_CLASS": "critical",
    "OVERALL_RISK_SCORE": "88/100",
    # ... rest of values
})

with open("report_output.html", "w") as f:
    f.write(report)
```
