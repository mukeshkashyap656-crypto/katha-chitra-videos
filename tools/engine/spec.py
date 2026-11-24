"""Katha Chitra scene engine: the episode.json format, its checks, and shared helpers.

Used by draw.py / build.py (to make the video) and by tools/ramayan_ai.py (to reject a bad
episode.json BEFORE it is pushed). check(epi) returns a list of problems in plain words.
"""
import hashlib, json, re

BGS = {"morning": "subah ka jungle", "cloudvan": "pahad ke paas baadal jaisa van", "divine": "sunehra divya aakash",
       "ghorvan": "ghana andhera jungle (rakshas wala)", "ashram": "rishiyon ka ashram + yagya kund",
       "river": "nadi ka kinara (Ganga/Sarayu/Shon)", "palace": "raj-darbar (gaddi + chhatra)"}
POSES = {"stand": "khada", "namaste": "haath jode", "talk": "baat karte hue haath", "bless": "aashirvaad ka haath",
         "point": "haath se ishara", "raise": "haath upar", "walk": "chalna (to_x tak)", "sit": "baitha (paalthi)",
         "bow": "jhuk kar pranam", "angry": "gusse mein haath"}
FACES = ["neutral", "smile", "joy", "sad", "worry", "angry", "firm", "stern", "shock"]
CAMS = ["auto", "wide", "speaker", "two"]
MOODS = ["none", "joy", "sorrow", "anger", "fear", "wonder", "night"]
FX = {"astra": "chamakta baan/astra: from -> to, result: thrown (door ud jaana) | fall (gir jaana) | none",
      "rain": "barish (color: laal = rakt varsha)"}
NEWCHAR_META = {"name", "big", "glow", "rakshas"}

# built-in cast: id -> (drawing-kit name, Hindi name, meta)
CAST = {
    "ram": ("ram", "श्रीराम", {}),
    "lakshman": ("lakshman", "लक्ष्मण", {}),
    "vishwamitra": ("vishwamitra2", "महर्षि विश्वामित्र", {}),
    "vasishtha": ("vasishtha", "गुरु वसिष्ठ", {}),
    "dasharatha": ("dasharatha", "महाराज दशरथ", {}),
    "rishi1": ("rishi_saffron", "ऋषि", {}),
    "rishi2": ("rishi_white", "ऋषि", {}),
    "mantri": ("mantri2", "मंत्री", {}),
    "darbari1": ("darbari", "दरबारी", {}), "darbari2": ("darbari2", "दरबारी", {}),
    "darbari3": ("darbari3", "दरबारी", {}), "darbari4": ("darbari4", "दरबारी", {}),
    "maricha": ("maricha", "मारीच", {"big": True, "glow": "dark", "rakshas": True}),
    "subahu": ("subahu", "सुबाहु", {"big": True, "glow": "dark", "rakshas": True}),
}
SPEAKER_PREFIX = [("ram", "ram"), ("lak", "lakshman"), ("vm", "vishwamitra"), ("vas", "vasishtha"), ("dash", "dasharatha")]
KIT_COLOURS = {"kind", "skin", "hair", "tunic", "sash", "upper", "lower", "hem", "fw", "fh", "build", "tall", "eye", "nose",
               "crown", "jewel", "bare", "skirt", "mous", "beard", "age", "belly", "browt", "halo", "ajina", "jata", "child",
               "saree", "blouse", "border", "stoop", "hook", "jowl", "eyeh", "browcol", "bandcol", "pagdi", "pagdi2",
               "beardlen", "jatabun", "tilak", "mala", "kamandalu"}


def load(path):
    epi = json.load(open(path, encoding="utf-8"))
    epi.setdefault("SPEAKER", {}); epi.setdefault("KEYWORDS", {}); epi.setdefault("NEW_CHARS", {})
    if "COVER" not in epi:
        sh = next((s for s in epi["SHOTS"] if s.get("cast")), epi["SHOTS"][0])
        epi["COVER"] = {"bg": sh["bg"], "cast": sh.get("cast", [])[:2], "tag": ""}
    epi["COVER"].setdefault("cast", []); epi["COVER"].setdefault("tag", "")
    return epi


def kit_name(who):
    return CAST[who][0] if who in CAST else who


def hindi_name(who, epi):
    if who in CAST: return CAST[who][1]
    return epi.get("NEW_CHARS", {}).get(who, {}).get("name", who)


def char_meta(kit_or_id, epi):
    for cid, (kit, _, meta) in CAST.items():
        if kit_or_id in (cid, kit): return meta
    nc = epi.get("NEW_CHARS", {}).get(kit_or_id, {})
    return {k: nc[k] for k in ("big", "glow", "rakshas") if k in nc}


def speaker(line, epi):
    if line in epi.get("SPEAKER", {}): return epi["SPEAKER"][line]
    if re.match(r"^n\d*$", line) or line.startswith("n_"): return None
    for p, who in SPEAKER_PREFIX:
        if line.startswith(p): return who
    return None


def look_value(entry, shot, epi):
    lk = entry.get("look", "auto")
    if lk in ("left", "right", "front"): return {"left": -0.8, "right": 0.8, "front": 0.0}[lk]
    sp = speaker(shot["line"], epi); cast = shot.get("cast", [])
    others = [c for c in cast if c is not entry]
    if not others: return 0.0
    if sp and sp != entry["who"]:
        tgt = next((c for c in cast if c["who"] == sp), None)
    else:
        tgt = min(others, key=lambda c: abs(c["x"] - entry["x"]))
    if tgt is None: tgt = min(others, key=lambda c: abs(c["x"] - entry["x"]))
    return 0.8 if tgt["x"] > entry["x"] else -0.8


LAYER_POSES = ("stand", "talk", "bless", "point", "raise", "namaste", "angry")   # arms are separate pieces (rotate smoothly)
HAND_BY_POSE = {"stand": "relaxed", "talk": "relaxed", "bless": "relaxed", "point": "point", "raise": "open", "namaste": "join", "angry": "fist"}


def layered(entry, shot):
    """True if this person is drawn as body + separately rotating arms (not for walking, sitting, bowing, shadows, cover)."""
    return (entry.get("pose", "stand") in LAYER_POSES and not entry.get("shadow") and shot.get("line") != "_cover")


def hand_styles(entry):
    return sorted({"relaxed", "open", HAND_BY_POSE.get(entry.get("pose", "stand"), "relaxed")})


def arm_states(entry, shot, epi):
    """Picture keys for the arm pieces of a layered person -> drawing params."""
    kit = kit_name(entry["who"]); out = {}
    if not layered(entry, shot): return out
    for sd in ("L", "R"):
        out[f"arm_{kit}_u{sd}"] = {"who": kit, "part": "u" + sd}
        for st in hand_styles(entry):
            out[f"arm_{kit}_f{sd}_{st}"] = {"who": kit, "part": "f" + sd, "hstyle": st}
    return out


def state_base(entry, shot, epi):
    """Parameters that define one look of one character in one shot."""
    p = {"who": kit_name(entry["who"]), "pose": entry.get("pose", "stand"), "face": entry.get("face", "neutral"),
         "look": look_value(entry, shot, epi), "shadow": bool(entry.get("shadow", False))}
    if layered(entry, shot):
        p["pose"] = "stand"; p["part"] = "body"        # the arms are drawn separately (arm_states); same body for every layered pose
    h = hashlib.md5(json.dumps(p, sort_keys=True).encode()).hexdigest()[:6]
    return f"{entry['who']}_{h}", p


def shot_states(entry, shot, epi):
    """All picture keys this cast entry needs in this shot -> drawing params."""
    base, p = state_base(entry, shot, epi); out = {}
    if p["pose"] == "walk":
        for i, ph in enumerate((0, 1.5708, 3.1416, 4.7124)):
            out[f"{base}_walk{i}"] = dict(p, walk=ph + (sum(map(ord, entry["who"])) % 7) * 0.4)
        return out
    if layered(entry, shot):                    # body (no head, no arms) + head as its own picture: head turns / nods / blinks / talks on its own
        out[base] = dict(p); hb = f"{base}_h"; ph = dict(p, part="head")
        out[hb] = ph; out[f"{hb}_blink"] = dict(ph, blink=True)
        if speaker(shot["line"], epi) == entry["who"] and not p["shadow"]:
            for m in ("A", "B", "E", "O", "M"): out[f"{hb}_{m}"] = dict(ph, mouth=m)
        return out
    out[base] = dict(p); out[f"{base}_blink"] = dict(p, blink=True)
    if speaker(shot["line"], epi) == entry["who"] and not p["shadow"]:
        for m in ("A", "B", "E", "O", "M"): out[f"{base}_{m}"] = dict(p, mouth=m)
    return out


def all_states(epi):
    out = {}
    for sh in epi["SHOTS"]:
        for e in sh.get("cast", []): out.update(shot_states(e, sh, epi)); out.update(arm_states(e, sh, epi))
    for e in epi["COVER"]["cast"]:
        out.update(shot_states(e, {"line": "_cover", "cast": epi["COVER"]["cast"]}, epi))
    return out


def check(epi):
    """Problems in plain Hinglish (empty list = ok)."""
    P = []
    for k in ("NAME", "COVER_NAME", "QUESTION", "BHAG", "LINES", "SHOTS"):
        if k not in epi: P.append(f"{k} zaroori hai")
    if P: return P
    lines = epi["LINES"]
    if not isinstance(lines, dict) or not lines: return ["LINES khaali hai"]
    for k, v in lines.items():
        if not re.match(r"^[a-z][a-z0-9_]*$", k): P.append(f"line id '{k}' sirf chhote angrezi akshar/ank ho")
        if not (isinstance(v, list) and len(v) == 3 and all(isinstance(x, str) for x in v)):
            P.append(f"LINES[{k}] = [hindi text, rate jaise '+0%', pitch jaise '+0Hz']"); continue
        if not re.match(r"^[+-]\d+%$", v[1]) or not re.match(r"^[+-]\d+Hz$", v[2]):
            P.append(f"LINES[{k}] rate/pitch galat ('+0%', '-12%', '+10Hz' jaisa likho)")
        if not re.search(r"[ऀ-ॿ]", v[0]): P.append(f"LINES[{k}] Hindi (Devanagari) mein ho")
    known = set(CAST) | set(epi.get("NEW_CHARS", {}))
    for cid, nc in epi.get("NEW_CHARS", {}).items():
        if cid in CAST: P.append(f"NEW_CHARS: '{cid}' pehle se hai, naya naam do")
        bad = set(nc) - KIT_COLOURS - NEWCHAR_META
        if bad: P.append(f"NEW_CHARS[{cid}]: ye cheezein samajh nahi aati: {sorted(bad)}")
        if nc.get("kind") not in ("m", "f"): P.append(f"NEW_CHARS[{cid}]: kind 'm' ya 'f' ho")
        if "name" not in nc: P.append(f"NEW_CHARS[{cid}]: Hindi 'name' do")
        if nc.get("glow") not in (None, "gold", "dark"): P.append(f"NEW_CHARS[{cid}]: glow sirf 'gold' (devta) ya 'dark' (rakshas)")
    shots = epi["SHOTS"]
    if not isinstance(shots, list) or not shots: return P + ["SHOTS khaali hai"]
    order = list(lines)
    seen, last_idx = set(), -1
    for i, sh in enumerate(shots, 1):
        ln = sh.get("line")
        if ln not in lines: P.append(f"shot {i}: line '{ln}' LINES mein nahi hai"); continue
        idx = order.index(ln)
        if idx < last_idx: P.append(f"shot {i}: lines LINES ke kram (order) mein hi aayein")
        last_idx = idx; seen.add(ln)
        if sh.get("bg") not in BGS: P.append(f"shot {i}: bg '{sh.get('bg')}' nahi hai; inme se chuno: {list(BGS)}")
        if sh.get("cam", "auto") not in CAMS: P.append(f"shot {i}: cam inme se: {CAMS}")
        if sh.get("mood", "none") not in MOODS: P.append(f"shot {i}: mood inme se: {MOODS}")
        if len(str(sh.get("chip", ""))) > 22: P.append(f"shot {i}: chip 2-3 shabd ka ho")
        if "at_word" in sh and sh["at_word"] not in lines[ln][0]: P.append(f"shot {i}: at_word '{sh['at_word']}' us line mein nahi hai")
        cast = sh.get("cast", [])
        whos = {e.get("who") for e in cast}
        for fx in sh.get("fx", []):
            if fx.get("type") not in FX: P.append(f"shot {i}: fx type inme se: {list(FX)}"); continue
            if fx["type"] == "astra":
                if fx.get("from") not in whos or fx.get("to") not in whos: P.append(f"shot {i}: astra ka from/to us shot ke cast mein ho")
                if fx.get("result", "none") not in ("thrown", "fall", "none"): P.append(f"shot {i}: astra result: thrown | fall | none")
            if "at_word" in fx and fx["at_word"] not in lines[ln][0]: P.append(f"shot {i}: fx at_word '{fx['at_word']}' us line mein nahi hai")
        if len(cast) > 4: P.append(f"shot {i}: ek shot mein 4 se zyada log nahi")
        for e in cast:
            w = e.get("who")
            if w not in known: P.append(f"shot {i}: '{w}' koi character nahi; ye hain: {sorted(known)} (naya ho to NEW_CHARS mein banao)"); continue
            if not isinstance(e.get("x"), (int, float)) or not 150 <= e["x"] <= 1210: P.append(f"shot {i}: {w} ka x 150 se 1210 ke beech ho")
            if e.get("pose", "stand") not in POSES: P.append(f"shot {i}: {w} ka pose inme se: {list(POSES)}")
            if e.get("face", "neutral") not in FACES: P.append(f"shot {i}: {w} ka face inme se: {FACES}")
            if not 0 <= e.get("lift", 0) <= 400: P.append(f"shot {i}: {w} ka lift 0-400 ho (aasmaan mein udna)")
            if e.get("pose") == "walk" and not isinstance(e.get("to_x"), (int, float)): P.append(f"shot {i}: {w} walk kar raha hai to to_x do")
        xs = sorted((e["x"], e["who"]) for e in cast if isinstance(e.get("x"), (int, float)) and e.get("who") in known)
        for (x1, w1), (x2, w2) in zip(xs, xs[1:]):
            gap = 330 if (char_meta(w1, epi).get("big") or char_meta(w2, epi).get("big")) else 260
            if x2 - x1 < gap: P.append(f"shot {i}: {w1} aur {w2} bahut paas hain (kam se kam {gap} ka faasla), ek doosre par chadh jaayenge")
    for ln in order:
        if ln not in seen: P.append(f"line '{ln}' kisi shot mein nahi hai")
    for k, sp in epi.get("SPEAKER", {}).items():
        if sp is not None and sp not in known: P.append(f"SPEAKER[{k}] = '{sp}' koi character nahi")
    cv = epi.get("COVER", {})
    if cv:
        if cv.get("bg") not in BGS: P.append("COVER.bg galat")
        for e in cv.get("cast", []):
            if e.get("who") not in known: P.append(f"COVER: '{e.get('who')}' koi character nahi")
    # Hook rule (24 Nov 2026, VIRAL.md section 1): log pehle ~6 sec mein swipe kar rahe the, isliye
    # Bhag 8 se pehli line chhoti ho. Purane episodes (Bhag 7 tak) par ye jaanch nahi lagti.
    try:
        bhag = int(epi.get("BHAG", 0))
    except (TypeError, ValueError):
        bhag = 0
    if bhag >= 8:
        first = order[0]; words = len(lines[first][0].split())
        if words > 12:
            P.append(f"HOOK: pehli line '{first}' {words} shabd ki hai; 12 shabd se chhoti karo — chaunkane wali baat ya sawaal "
                     f"pehle shabdon mein (jaise 'Sirf 3 kadam mein tinon lok naap liye? Kisne?'), peechhe ki baat baad mein")
    # Scene = awaaz niyam (24 Nov 2026, owner ka hukm): jo line mein bola/hona hai wahi dikhe, bhaav ke saath.
    # Bhag 9 se. Bhag 8 (alag chat mein ban raha hai) par ye jaanch nahi lagti.
    if bhag >= 9:
        entries = 0; neutral = 0; sigs = []
        for i, sh in enumerate(shots, 1):
            if len(str(sh.get("show", "")).strip()) < 8:
                P.append(f"shot {i}: 'show' likho — is line mein jo bola ja raha hai/ho raha hai wo screen par kya dikhega "
                         f"(kaun kya kar raha hai, chehre/sharir ka bhaav, kaunsi cheez) — scene awaaz se mele, sirf khade-khade nahi")
            sig = tuple(sorted((e.get("who"), e.get("pose", "stand"), e.get("face", "neutral")) for e in sh.get("cast", [])))
            sigs.append(sig)
            for e in sh.get("cast", []):
                entries += 1; neutral += e.get("face", "neutral") == "neutral"
            if i >= 3 and sig and sig == sigs[-2] == sigs[-3]:
                P.append(f"shot {i}: lagatar 3 shot mein wahi pose+chehra — kahani ke hisaab se action/bhaav badlo")
        if entries and neutral / entries > 0.5:
            P.append(f"BHAAV: {neutral}/{entries} jagah chehra 'neutral' hai; har pal ka bhaav chehre aur sharir se dikhao (dar, gussa, dukh, khushi, hairani)")
    return P


if __name__ == "__main__":
    import sys
    pr = check(load(sys.argv[1]))
    print("\n".join(pr) or "OK"); sys.exit(1 if pr else 0)
