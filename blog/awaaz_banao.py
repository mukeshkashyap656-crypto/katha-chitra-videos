#!/usr/bin/env python3
"""khabaradda ke assistant ki har baat ki recording (sirf Piper 'pratham' awaaz).
Blog ki feed padhta hai; jis line ki mp3 nahi hai wahi banata hai.
Chalana: python awaaz_banao.py OUT_DIR MODEL.onnx MODEL.json   (--ginti = sirf kitni baaki)
Awaaz ki shart: CC BY-NC-SA 4.0 (bina kamai wala istemaal)."""
import sys, os, re, json, wave, subprocess, tempfile, unicodedata, urllib.request
from html.parser import HTMLParser

FEED = 'https://mukeshnewsdaily.blogspot.com/feeds/posts/default?alt=json&max-results=150'
# gadget (khabar_saathi.html) ke tay jawab; wahan badlo to yahan bhi
TAY = [
    'इस बारे में हमारे ब्लॉग पर अभी मुझे कुछ नहीं मिला। मैं सिर्फ़ इसी ब्लॉग के लेखों से जवाब देता हूँ।',
    'हमारे लेख में लिखा है:', 'इससे जुड़े लेख नीचे हैं।', 'अभी लेख खोल नहीं पाया। थोड़ी देर बाद फिर पूछिए।',
    'इस हिस्से में अभी कोई लेख नहीं है।', 'सबसे नया लेख है:', 'कोई लेख खोलिए, फिर मैं उसके बारे में बता दूँगा।',
    'इस लेख की शुरुआत:', 'मैं खबर साथी हूँ, khabaradda का अपने-आप चलने वाला सहायक।',
    'यह khabaradda ब्लॉग है। यहाँ लेख MUKESH News के नाम से छपते हैं।', 'संपर्क का पन्ना नीचे है।',
    'थोड़ा और साफ़ पूछिए, जैसे: मोबाइल की नई खबर।', 'माइक से आवाज़ नहीं मिली। आप लिखकर पूछ सकते हैं।',
    'मैं ठीक हूँ सर, धन्यवाद। बताइए, क्या पढ़ना है?', 'आपका स्वागत है सर। और कुछ पूछना हो तो बताइए।', 'ठीक है सर, आपका दिन अच्छा रहे।',
    'मैं ताज़ा खबर बता सकता हूँ, खुला लेख सुना सकता हूँ, और इस ब्लॉग के लेखों से सवाल का जवाब दे सकता हूँ।',
]
BOLNA = [('khabaradda', 'खबर अड्डा'), ('MUKESH News', 'मुकेश न्यूज़'), ('WhatsApp', 'व्हाट्सऐप')]

def sentences(text):
    t = re.sub(r'([।?!]|\.(?=\s+[^\d\s]))\s+', '\\1\n', text)
    return [s.strip() for s in t.split('\n') if key(s)]

def key(s):
    return ''.join(c for c in s.lower() if unicodedata.category(c)[0] in 'LMN')

def fnv(s):
    h = 0x811c9dc5
    for c in key(s):
        h = ((h ^ ord(c)) * 0x01000193) & 0xffffffff
    return '%08x' % h

class Text(HTMLParser):
    VOID = {'br', 'img', 'hr', 'input', 'meta', 'link', 'source', 'wbr', 'area', 'base', 'col', 'embed'}
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.stack = [], []
    def handle_starttag(self, tag, attrs):
        if tag == 'br':
            self.out.append('\n')
        if tag in self.VOID:
            return
        skip = tag in ('script', 'style', 'figure', 'small') or (tag == 'table' and 'tr-caption-container' in (dict(attrs).get('class') or ''))
        self.stack.append((tag, skip))
    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break
        if tag in ('td', 'th'):
            self.out.append(' ')
        if tag in ('p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div', 'tr'):
            self.out.append('\n')
    def handle_data(self, d):
        if not any(s for _, s in self.stack):
            self.out.append(d.replace('\xa0', ' '))

def wanted():
    req = urllib.request.Request(FEED, headers={'User-Agent': 'khabaradda-awaaz'})
    feed = json.load(urllib.request.urlopen(req, timeout=60))['feed']
    lines = []
    for t in TAY:
        lines += sentences(t)
    for e in feed.get('entry', []):
        lines += sentences(e['title']['$t'])
        p = Text()
        p.feed((e.get('content') or e.get('summary') or {'$t': ''})['$t'])
        lines += sentences(''.join(p.out))
    out = {}
    for s in lines:
        out.setdefault(fnv(s), s)
    return out

def main():
    outdir = sys.argv[1]
    os.makedirs(os.path.join(outdir, 's'), exist_ok=True)
    need = {h: s for h, s in wanted().items() if not os.path.exists(os.path.join(outdir, 's', h + '.mp3'))}
    print('nayi line:', len(need))
    if '--ginti' in sys.argv or not need:
        return
    from piper import PiperVoice, SynthesisConfig
    voice = PiperVoice.load(sys.argv[2], config_path=sys.argv[3])
    cfg = SynthesisConfig(length_scale=1.05)
    with tempfile.TemporaryDirectory() as tmp:
        w = os.path.join(tmp, 'a.wav')
        for h, s in need.items():
            for a, b in BOLNA:
                s = re.sub(re.escape(a), b, s, flags=re.I)
            with wave.open(w, 'wb') as f:
                voice.synthesize_wav(s, f, syn_config=cfg)
            mp3 = os.path.join(outdir, 's', h + '.mp3')
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', w, '-af', 'loudnorm=I=-16:TP=-1.5', '-ar', '44100', '-ac', '1', '-b:a', '48k', mp3 + '.tmp.mp3'], check=True)
            os.replace(mp3 + '.tmp.mp3', mp3)

if __name__ == '__main__':
    main()
