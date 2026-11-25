"""Har free AI raaste ko ek chhota sawaal bhejkar dekhta hai ki chalta hai ya nahi. Kuch likhta/post nahi karta, keys nahi chhapta."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ramayan_ai as R

ROUTES = [("Gemini", lambda p: R.gemini(p, False)), ("OpenRouter", lambda p: R.openrouter(p, False))]
for name in ("cloudflare", "groq", "cerebras", "mistral", "sambanova", "nvidia", "cohere", "huggingface", "zai", "ovh", "kilo"):
    ROUTES.append((name, lambda p, f=getattr(R, name): f(p, False)))

rows = []
for name, fn in ROUTES:
    try:
        txt = fn("Reply with only the word OK.")
        rows.append((name, "CHALU", (R.USED[-1] if R.USED else txt)[:80]))
    except Exception as e:
        rows.append((name, "BAND", str(e).replace("\n", " ")[:220]))
print("\n===== NATIJA =====")
for r in rows:
    print(" | ".join(r))
out = os.environ.get("GITHUB_STEP_SUMMARY")
if out:
    with open(out, "a", encoding="utf-8") as f:
        f.write("| Raasta | Haal | Baat |\n|---|---|---|\n" + "".join("| " + " | ".join(c.replace("|", "/") for c in r) + " |\n" for r in rows))
