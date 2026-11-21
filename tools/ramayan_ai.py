def _openai_style(name, url, key, models, prompt_text, want_json):
    if not key:
        raise Busy(f"{name}: key nahi")
    last = None
    for m in models:
        try:
            r = requests.post(url, timeout=300, headers={"Authorization": f"Bearer {key}"},
                              json={"model": m, "temperature": 0.3,
                                    "messages": [{"role": "user", "content": prompt_text}],
                                    **({"response_format": {"type": "json_object"}} if want_json else {})})
            txt = r.json()["choices"][0]["message"]["content"].strip()
            if txt:
                print(f"Jawab ({name}):", m); USED.append(f"{name} {m}")
                return txt
        except Exception as e:
            last = e
            print(f"{name} {m} nahi chala: {str(e)[:160]}")
    raise Busy(f"{name}: {str(last)[:200]}")


def groq(p, j):
    return _openai_style("Groq", "https://api.groq.com/openai/v1/chat/completions",
                         os.environ.get("GROQ_API_KEY", "").strip(),
                         ["llama-3.3-70b-versatile", "qwen/qwen3-32b"], p, j)


def cerebras(p, j):
    return _openai_style("Cerebras", "https://api.cerebras.ai/v1/chat/completions",
                         os.environ.get("CEREBRAS_API_KEY", "").strip(), ["llama-3.3-70b"], p, j)


def mistral(p, j):
    return _openai_style("Mistral", "https://api.mistral.ai/v1/chat/completions",
                         os.environ.get("MISTRAL_API_KEY", "").strip(), ["mistral-small-latest"], p, j)


def ask(prompt_text, image=None, want_json=True):
    imgs = image if isinstance(image, (list, tuple)) else ([image] if image else [])
    contents = [types.Part.from_bytes(data=i, mime_type="image/jpeg") for i in imgs] + [prompt_text] if imgs else prompt_text
    chain = [("Gemini", lambda p: gemini(contents if p == prompt_text else p, want_json))]
    if not imgs:   # tasveer sirf Gemini dekh sakta hai
        chain += [("OpenRouter", lambda p: openrouter(p, want_json)),
                  ("GitHub", lambda p: github_models(p, want_json)),
                  ("Groq", lambda p: groq(p, want_json)),
                  ("Cerebras", lambda p: cerebras(p, want_json)),
                  ("Mistral", lambda p: mistral(p, want_json))]
    prompt, errs = prompt_text, []
    for _round in range(2):                      # poori list do baar
        for name, fn in chain:
            try:
                txt = fn(prompt)
            except Busy as e:
                errs.append(f"{name}: {str(e)[:60]}"); continue
            if not want_json:
                return txt
            try:
                mt = re.search(r"\{.*\}", txt, re.DOTALL)
                data = json.loads(mt.group(0) if mt else txt)
                if data.get("action") not in ("change", "none"):
                    raise ValueError("action galat")
                data.setdefault("files", []); data.setdefault("summary", ""); data.setdefault("render", False)
                return data
            except ValueError as e:
                errs.append(f"{name}: JSON tooti")
                prompt = (prompt_text + "\n\n# YOUR LAST ANSWER WAS NOT VALID JSON (" + str(e)[:120] +
                          "). Answer again with ONLY valid JSON; escape every double quote inside strings.")
    raise Busy("Saare raaste try kiye: " + " | ".join(errs)[-300:])
