"""khabar_saathi.html (padhne wali file) se Blogger mein chipkane wali ASCII file banata hai.
Blogger gadget ke script ke andar Hindi ko &#...; bana deta hai, isliye script mein \\uXXXX chahiye."""
import os, re
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "khabar_saathi.html"), encoding="utf-8").read()


def esc(c):
    b = c.encode("utf-16-be")
    return "".join("\\u%02x%02x" % (b[i], b[i + 1]) for i in range(0, len(b), 2))


head, rest = src.split("<script>", 1)
js, tail = rest.split("</script>", 1)
js = re.sub(r"/\*.*?\*/", "", js, flags=re.S)  # tippani hata do
js = "".join(c if ord(c) < 128 else esc(c) for c in js)
out = head + "<script>" + js + "</script>" + tail
out = out.encode("ascii").decode()  # kahin Hindi bachi ho to yahin ruk jaye
open(os.path.join(here, "khabar_saathi_blogger.txt"), "w").write(out)
