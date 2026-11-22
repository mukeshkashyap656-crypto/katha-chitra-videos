"""Instagram Promo Reel Generator for Katha Chitra episodes.
Usage: EPDIR=episodes/bhag6 python3 tools/make_promo.py
Generates a short, high-energy Instagram promo Reel config/script from episode.json.
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "engine")
sys.path.insert(0, ENGINE)

import spec as SP

def create_promo_config(ep_dir):
    epi_path = os.path.join(ep_dir, "episode.json")
    if not os.path.exists(epi_path):
        raise FileNotFoundError(f"Episode file not found: {epi_path}")
    
    epi = SP.load(epi_path)
    bhag = epi.get("BHAG", 1)
    q = epi.get("QUESTION", "")
    lines = epi.get("LINES", {})
    
    line_keys = list(lines.keys())
    promo_lines = line_keys[:3] if len(line_keys) >= 3 else line_keys
    
    promo_data = {
        "title": f"Promo - Bhag {bhag}",
        "type": "instagram_reel",
        "duration_target": 15.0,
        "question": q,
        "teaser_lines": {k: lines[k] for k in promo_lines},
        "cta": "Poora episode dekhein YouTube channel @kathachitra_123 par! #ValmikiRamayan #Shorts",
        "cover": epi.get("COVER", {})
    }
    
    promo_out = os.path.join(ep_dir, "promo_reel.json")
    with open(promo_out, "w", encoding="utf-8") as f:
        json.dump(promo_data, f, ensure_ascii=False, indent=2)
    print(f"Promo Reel config generated: {promo_out}")
    return promo_data

if __name__ == "__main__":
    epdir = os.environ.get("EPDIR", "episodes/bhag6")
    create_promo_config(epdir)
