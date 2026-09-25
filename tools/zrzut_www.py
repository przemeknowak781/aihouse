#!/usr/bin/env python3
"""Zrzut ekranu strony (lokalny serwer) w headless Chromium — do kontroli jakości www i raportów.
Użycie: python3 tools/zrzut_www.py URL WYJ.png [szer wys] [czekaj_ms]
Chromium ufa wyłącznie certyfikatom CA proxy sesji (SPKI z /root/.ccr/ca-bundle.crt) — potrzebne do CDN przez proxy."""
import os, sys, subprocess
from playwright.sync_api import sync_playwright

def spki_list():
    out, pem, hashes = [], [], []
    for line in open('/root/.ccr/ca-bundle.crt'):
        pem.append(line)
        if 'END CERTIFICATE' in line:
            txt = ''.join(pem); pem = []
            subj = subprocess.run(['openssl', 'x509', '-noout', '-subject'], input=txt, capture_output=True, text=True).stdout
            if 'Anthropic' in subj:
                pub = subprocess.run(['openssl', 'x509', '-pubkey', '-noout'], input=txt, capture_output=True, text=True).stdout
                der = subprocess.run(['openssl', 'pkey', '-pubin', '-outform', 'der'], input=pub.encode(), capture_output=True).stdout
                h = subprocess.run(['openssl', 'dgst', '-sha256', '-binary'], input=der, capture_output=True).stdout
                hashes.append(subprocess.run(['base64'], input=h, capture_output=True).stdout.decode().strip())
    return ','.join(hashes)

def main():
    url, out = sys.argv[1], sys.argv[2]
    w, h = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (1600, 1000)
    wait = int(sys.argv[5]) if len(sys.argv) > 5 else 6000
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium',
                              proxy={"server": os.environ.get("HTTPS_PROXY", ""), "bypass": "localhost,127.0.0.1"},
                              args=["--use-gl=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist",
                                    f"--ignore-certificate-errors-spki-list={spki_list()}"])
        pg = b.new_page(viewport={'width': w, 'height': h})
        errs = []
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(url, wait_until="networkidle", timeout=90000)
        pg.wait_for_timeout(wait)
        pg.screenshot(path=out, full_page=('--full' in sys.argv))
        print("błędy konsoli:", errs[:10])
        b.close()

if __name__ == "__main__":
    main()
