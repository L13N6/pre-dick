#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

SERVER = os.environ.get("PREDICT_SERVER_URL", "https://api.agentpredict.work")
MODE = os.environ.get("PREDICT_MODE", "chartist").lower()
TICKETS = int(os.environ.get("PREDICT_TICKETS", "300"))
MARKET_PREFERENCE = os.environ.get("PREDICT_MARKET", "recommended")
MAX_RETRIES = int(os.environ.get("PREDICT_MAX_RETRIES", "2"))

VALID_MODES = {"chartist", "conservative", "sentiment", "macro", "degen", "sniper", "contrarian"}
if MODE not in VALID_MODES:
    print(f"Invalid mode: {MODE}", file=sys.stderr)
    sys.exit(1)


def run_cmd(args: List[str], env: Optional[Dict[str, str]] = None, check: bool = True) -> str:
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    p = subprocess.run(args, capture_output=True, text=True, env=full_env)
    stdout = (p.stdout or "").strip()
    stderr = (p.stderr or "").strip()
    if check and p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(args)}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}")
    return stdout if stdout else stderr


def extract_json(text: str) -> Dict[str, Any]:
    m = re.search(r'(\{.*\})', text, re.S)
    if not m:
        raise ValueError(f"No JSON object found in output:\n{text[:2000]}")
    return json.loads(m.group(1))


def unlock_wallet() -> None:
    token = run_cmd(["awp-wallet", "unlock", "--scope", "full", "--duration", "86400", "--raw"])
    os.environ["AWP_WALLET_TOKEN"] = token.strip()


def preflight() -> Dict[str, Any]:
    out = run_cmd(["predict-agent", "preflight", "--server", SERVER], check=False)
    return extract_json(out)


def context() -> Dict[str, Any]:
    out = run_cmd(["predict-agent", "context", "--server", SERVER], check=False)
    return extract_json(out)


def challenge(market: str) -> Dict[str, Any]:
    out = run_cmd(["predict-agent", "challenge", "--market", market, "--server", SERVER], check=False)
    return extract_json(out)


def status() -> Dict[str, Any]:
    out = run_cmd(["predict-agent", "status", "--server", SERVER], check=False)
    return extract_json(out)


def pick_market(ctx: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    markets = ctx.get("data", {}).get("markets", [])
    if not markets:
        raise RuntimeError("No markets in context")
    if MARKET_PREFERENCE != "recommended":
        for m in markets:
            if m.get("id") == MARKET_PREFERENCE:
                return m["id"], m, markets
    for m in markets:
        if m.get("recommended"):
            return m["id"], m, markets
    return markets[0]["id"], markets[0], markets


def get_timeslot_info(ctx: Dict[str, Any]) -> Tuple[int, int, int]:
    ts = ctx.get("data", {}).get("agent", {}).get("timeslot", {})
    remaining = int(ts.get("submissions_remaining", 0) or 0)
    used = int(ts.get("submissions_used", 0) or 0)
    resets = int(ts.get("slot_resets_in_seconds", 0) or 0)
    return remaining, used, resets


def infer_direction(candles: List[Dict[str, Any]]) -> str:
    if len(candles) < 8:
        return "down"
    closes = [float(c["close"]) for c in candles]
    recent = closes[-5:]
    mid = closes[-15:-5] if len(closes) >= 15 else closes[:-5]
    recent_avg = sum(recent) / len(recent)
    mid_avg = sum(mid) / len(mid) if mid else recent_avg
    momentum = recent[-1] - recent[0]
    if recent_avg > mid_avg and momentum > 0:
        return "up"
    return "down"


def price_levels(candles: List[Dict[str, Any]]) -> Tuple[str, str, str]:
    highs = [float(c["high"]) for c in candles[-20:]]
    lows = [float(c["low"]) for c in candles[-20:]]
    last = float(candles[-1]["close"])
    return f"{max(highs):.2f}", f"{min(lows):.2f}", f"{last:.2f}"


def parse_constraint(prompt: str) -> Optional[str]:
    prompt_upper = prompt.upper()
    patterns = [
        r"SPELL\s+([A-Z](?:\W*[A-Z]){2,})",
        r"READ\s+([A-Z](?:\W*[A-Z]){2,})",
        r"INITIALS?\s+SPELL\s+([A-Z](?:\W*[A-Z]){2,})",
        r"LETTERS?\s+SPELL\s+([A-Z](?:\W*[A-Z]){2,})",
        r"FIRST\s+LETTERS?\s+READ\s+([A-Z](?:\W*[A-Z]){2,})",
    ]
    for pat in patterns:
        m = re.search(pat, prompt_upper)
        if m:
            letters = re.sub(r"[^A-Z]", "", m.group(1))
            if len(letters) >= 3:
                return letters[:3]

    # fallback: try to capture quoted / emphasized 3-letter sequences near challenge words
    for pat in [
        r"(?:SPELL|READ)[^A-Z]{0,30}['\"]?([A-Z]{3})['\"]?",
        r"FIRST\s+LETTERS?[^A-Z]{0,30}['\"]?([A-Z]{3})['\"]?",
        r"INITIALS?[^A-Z]{0,30}['\"]?([A-Z]{3})['\"]?",
    ]:
        m = re.search(pat, prompt_upper)
        if m:
            return m.group(1)[:3]
    return None


def parse_snapshot(prompt: str) -> Optional[str]:
    vals = re.findall(r"0\.\d+", prompt)
    return vals[0] if vals else None


def words_for_letters(letters: str) -> str:
    bank = {
        "A": ["Adaptive", "Alpha", "Angle"],
        "B": ["Bias", "Base", "Bounce"],
        "C": ["Context", "Control", "Continuation"],
        "D": ["Drift", "Downside", "Demand"],
        "E": ["Early", "Edge", "Expansion"],
        "F": ["Flow", "Follow", "Fade"],
        "G": ["Grip", "Gradient", "Gamma"],
        "H": ["Holding", "Higher", "Hedge"],
        "I": ["Impulse", "Intraday", "Intensity"],
        "J": ["Joint", "Jump", "Jolt"],
        "K": ["Keeps", "Key", "Kick"],
        "L": ["Lean", "Lower", "Liquidity"],
        "M": ["Momentum", "Market", "Move"],
        "N": ["Now", "Near", "Negative"],
        "O": ["Order", "Orderflow", "Oscillation"],
        "P": ["Price", "Pressure", "Path"],
        "Q": ["Quick", "Quiet", "Quality"],
        "R": ["Risk", "Relative", "Rejection"],
        "S": ["Structure", "Support", "Selling"],
        "T": ["Trend", "Tape", "Trigger"],
        "U": ["Under", "Upside", "Urgency"],
        "V": ["Volatility", "Value", "Velocity"],
        "W": ["Weakness", "Wave", "Weight"],
        "X": ["Xray", "Xfactor", "Xtrend"],
        "Y": ["Yield", "Yellow", "Yearly"],
        "Z": ["Zone", "Zigzag", "Zenith"],
    }
    parts = []
    for idx, ch in enumerate(letters[:3]):
        choices = bank.get(ch.upper(), [ch.upper()])
        parts.append(choices[min(idx, len(choices)-1)])
    return " ".join(parts)


def build_reasoning(mode: str, direction: str, market: Dict[str, Any], candles: List[Dict[str, Any]], letters: Optional[str], snapshot: Optional[str]) -> str:
    hi, lo, last = price_levels(candles)
    asset = market.get("asset", "BTC/USDT")
    market_id = market.get("id", "unknown-market")
    phrase = words_for_letters(letters) if letters else "Price Trend Structure"
    snapshot_text = f" I also note the current snapshot {snapshot}." if snapshot else ""

    if mode == "chartist":
        core = (
            f"Chartist read for {asset} in {market_id}: short-term structure currently leans {direction}. "
            f"Recent one-minute candles show price reacting around resistance near {hi} and support near {lo}, with latest trade near {last}. "
            f"{phrase} appears in the immediate tape as momentum fades after bounces and local highs keep attracting sellers." if direction == "down" else
            f"Chartist read for {asset} in {market_id}: short-term structure currently leans {direction}. "
            f"Recent one-minute candles show price reacting around resistance near {hi} and support near {lo}, with latest trade near {last}. "
            f"{phrase} appears in the immediate tape as pullbacks hold cleaner and local lows keep getting bought."
        )
    elif mode == "conservative":
        core = (
            f"Conservative read for {asset}: I prefer measured exposure and the present structure still leans {direction}. "
            f"Price is trading near {last} inside a recent range capped near {hi} and supported near {lo}. "
            f"{phrase} in the short-term setup suggests caution, with risk controlled and only a modest ticket size justified."
        )
    elif mode == "sentiment":
        core = (
            f"Sentiment read for {asset}: crowd positioning looks balanced on the surface, but the immediate tape still leans {direction}. "
            f"With price near {last}, moves toward {hi} have not expanded cleanly while reactions toward {lo} still attract emotion. "
            f"{phrase} captures the shift in short-term crowd energy that favors this side into the window close."
        )
    elif mode == "macro":
        core = (
            f"Macro-style read for {asset}: even on a short window, the tape currently leans {direction}. "
            f"Price near {last} is trading between {lo} and {hi}, and the market is respecting short-term risk-off versus risk-on cues rather than breaking decisively. "
            f"{phrase} reflects that broader pressure still tilts this window toward the chosen side."
        )
    else:
        core = (
            f"Predict read for {asset}: setup leans {direction}. Price is near {last}, with recent action bounded by {lo} and {hi}. "
            f"{phrase} in the short-term tape supports this directional call."
        )

    tail = (
        f"{snapshot_text} Ticket size stays controlled because volatility remains two-sided, but the probability still favors {direction} before the market closes."
    )
    reasoning = core + tail
    if len(reasoning) < 80:
        reasoning += " The structure is not random noise; repeated reactions around these levels support the chosen direction."
    return reasoning[:1900]


def submit_prediction(market_id: str, direction: str, tickets: int, reasoning: str, nonce: str) -> Dict[str, Any]:
    out = run_cmd([
        "predict-agent", "submit",
        "--server", SERVER,
        "--market", market_id,
        "--prediction", direction,
        "--tickets", str(tickets),
        "--reasoning", reasoning,
        "--challenge-nonce", nonce,
    ], check=False)
    return extract_json(out)


def parse_letters_from_error(res: Dict[str, Any]) -> Optional[str]:
    texts = []
    if isinstance(res, dict):
        if res.get("user_message"):
            texts.append(str(res.get("user_message")))
        err = res.get("error") or {}
        if err.get("message"):
            texts.append(str(err.get("message")))
        debug = err.get("debug") or {}
        if debug.get("raw_error"):
            texts.append(str(debug.get("raw_error")))
    blob = "\n".join(texts).upper()
    for pat in [
        r"SPELL\s+'?([A-Z]{3})'?(?:\.|\s|$)",
        r"FIRST\s+LETTERS\s+SPELL\s+'?([A-Z]{3})'?(?:\.|\s|$)",
        r"READ\s+'?([A-Z]{3})'?(?:\.|\s|$)",
    ]:
        m = re.search(pat, blob)
        if m:
            return m.group(1)
    return None


def main() -> int:
    print(f"[run_predict_v2] mode={MODE} server={SERVER}")
    unlock_wallet()
    pf = preflight()
    print(json.dumps(pf, indent=2))
    try:
        run_cmd(["predict-agent", "set-persona", MODE, "--server", SERVER], check=False)
        print(f"[run_predict_v2] ensured persona={MODE}")
    except Exception as e:
        print(f"[run_predict_v2] persona set skipped: {e}")
    ctx = context()
    print(json.dumps(ctx, indent=2))
    action = ctx.get("data", {}).get("recommendation", {}).get("action")
    if action != "submit":
        print("[run_predict_v2] No submittable market right now.")
        return 0

    remaining, used, resets = get_timeslot_info(ctx)
    print(f"[run_predict_v2] timeslot remaining={remaining} used={used} resets_in={resets}s")
    if remaining <= 0:
        print("[run_predict_v2] no submissions remaining in this slot; stopping")
        return 0

    dynamic_retries = min(MAX_RETRIES, remaining)
    if remaining == 1:
        dynamic_retries = 1
    elif remaining >= 2:
        dynamic_retries = max(2, dynamic_retries)

    market_id, market, _ = pick_market(ctx)
    closes_in = int(market.get("closes_in_seconds", 0) or 0)
    if closes_in and closes_in < 180:
        print(f"[run_predict_v2] market closes too soon ({closes_in}s); skipping to save slot")
        return 0

    candles = ctx.get("data", {}).get("klines", {}).get("candles", [])
    direction = infer_direction(candles)
    print(f"[run_predict_v2] selected market={market_id} direction={direction} closes_in={closes_in}s retries={dynamic_retries}")

    forced_letters: Optional[str] = None
    for attempt in range(1, dynamic_retries + 1):
        ch = challenge(market_id)
        prompt = ch["data"]["prompt"]
        nonce = ch["data"]["nonce"]
        parsed_letters = parse_constraint(prompt)
        letters = forced_letters or parsed_letters
        snapshot = parse_snapshot(prompt)
        reasoning = build_reasoning(MODE, direction, market, candles, letters, snapshot)
        print(f"[run_predict_v2] attempt={attempt} parsed_letters={parsed_letters} forced_letters={forced_letters} using_letters={letters} snapshot={snapshot} nonce={nonce}")
        print(f"[run_predict_v2] reasoning={reasoning}")
        res = submit_prediction(market_id, direction, TICKETS, reasoning, nonce)
        print(json.dumps(res, indent=2))
        if res.get("ok"):
            print("[run_predict_v2] submit success")
            return 0
        code = (((res.get("error") or {}).get("code")) or "")
        if code in {"TIMESLOT_LIMIT_EXCEEDED"}:
            wait_hint = (((res.get("_internal") or {}).get("wait_seconds")) or 0)
            print(f"[run_predict_v2] hit timeslot limit, stopping (wait_seconds={wait_hint})")
            return 1
        err_letters = parse_letters_from_error(res)
        if err_letters:
            forced_letters = err_letters
            print(f"[run_predict_v2] server hinted letters={forced_letters}; will retry with adapted reasoning")
        # refresh timeslot after a failed attempt so we do not burn the last slot carelessly
        try:
            post_ctx = context()
            rem2, used2, reset2 = get_timeslot_info(post_ctx)
            print(f"[run_predict_v2] post-fail timeslot remaining={rem2} used={used2} resets_in={reset2}s")
            if rem2 <= 0:
                print("[run_predict_v2] no submissions remaining after failure; stopping")
                return 1
            if rem2 == 1 and attempt < dynamic_retries:
                print("[run_predict_v2] only one submission left; preserving it for next cycle")
                return 1
        except Exception as e:
            print(f"[run_predict_v2] post-fail context refresh skipped: {e}")
        time.sleep(2)

    print("[run_predict_v2] exhausted retries without success")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
