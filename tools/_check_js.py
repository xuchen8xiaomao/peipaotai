import re, subprocess, sys, os

NODE = r"C:\Users\24186\.workbuddy\binaries\node\versions\22.22.2-3\node.exe"
files = sys.argv[1:] or [r"site/chat.html", r"index.html"]

for f in files:
    if not os.path.exists(f):
        print(f"[SKIP] {f} not found"); continue
    html = open(f, encoding="utf-8").read()
    # find all <script>...</script> blocks, skip those with src=
    blocks = re.findall(r"<script\b([^>]*)>(.*?)</script>", html, re.S)
    ok = True
    for i, (attrs, code) in enumerate(blocks):
        if "src=" in attrs:
            continue  # external, nothing to check
        if not code.strip():
            continue
        tmp = f + f".block{i}.js"
        open(tmp, "w", encoding="utf-8").write(code)
        r = subprocess.run([NODE, "--check", tmp], capture_output=True, text=True)
        if r.returncode == 0:
            print(f"[OK]   {f} block{i} ({len(code)} chars)")
        else:
            ok = False
            print(f"[FAIL] {f} block{i}\n{r.stderr}")
        try: os.remove(tmp)
        except: pass
    if ok:
        print(f"  -> {f}: ALL_OK")
    print("")
