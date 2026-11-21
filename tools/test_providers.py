"""Har free AI raaste ko ek chhota sawaal bhejta hai aur batata hai kaun chala (key kabhi print nahi hoti)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ramayan_ai as R

Q = 'Reply with ONLY this JSON: {"action":"none","summary":"ok"}'
for name in ["cloudflare", "nvidia", "cohere", "huggingface", "zai", "groq", "cerebras", "mistral"]:
    try:
        out = getattr(R, name)(Q, True)
        print(f"RESULT {name}: CHALA -> {out[:60]!r}")
    except R.Busy as e:
        print(f"RESULT {name}: nahi chala -> {str(e)[:160]}")
    except Exception as e:
        print(f"RESULT {name}: galti -> {type(e).__name__} {str(e)[:120]}")
