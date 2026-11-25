"""Smoke test: load the site in a real browser and make sure the main pieces work.

It checks that the page loads without script errors, the whole list shows up,
the rod has one washer per item, the vibe sections and filters work, and the
proposal form sends what it should. The form test never reaches Formspree:
the request is caught and answered locally, so no fake proposals land in your inbox.

Run it yourself:
    pip install playwright
    python -m playwright install chromium
    python scripts/smoke_test.py

GitHub runs it on every push (see .github/workflows/check-list.yml).
"""
import functools
import http.server
import json
import os
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "data" / "accomplishments.json").read_text(encoding="utf-8"))
active = [a for a in data["accomplishments"] if a["status"] == "active"]
vibes = data["vibes"]
capstones = [a for a in active if a["capstone"]]

failures = []
# Uses Playwright's own Chromium. Set CHROME_PATH to use a browser you already have instead.
LAUNCH = {"executable_path": os.environ["CHROME_PATH"]} if os.environ.get("CHROME_PATH") else {}


def check(label, ok, detail=""):
    print(("pass" if ok else "FAIL") + ": " + label + (f" ({detail})" if detail and not ok else ""))
    if not ok:
        failures.append(label)


# Serve the site the same way GitHub Pages does: plain files over HTTP.
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


handler = functools.partial(QuietHandler, directory=str(ROOT))
server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{server.server_address[1]}/"

with sync_playwright() as p:
    browser = p.chromium.launch(**LAUNCH)
    for width, name in [(1200, "desktop"), (390, "phone")]:
        print(f"--- {name} ---")
        page = browser.new_page(viewport={"width": width, "height": 900})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        sent = {}

        def fake_formspree(route):
            sent["url"] = route.request.url
            sent["body"] = route.request.post_data_buffer.decode(errors="ignore")
            route.fulfill(status=200, content_type="application/json", body='{"ok":true}')

        page.route("https://formspree.io/**", fake_formspree)
        page.set_default_timeout(5000)
        page.goto(url)
        try:
            page.wait_for_selector("details.vibe", timeout=10000)
        except Exception:
            check("page builds the list", False,
                  "; ".join(errors) or "the vibe sections never appeared; app.js or the JSON file is probably broken")
            page.close()
            continue

        check("no script errors on load", not errors, "; ".join(errors))
        count = page.locator("#count").inner_text()
        check(f"list shows all {len(active)} active items", count == f"Showing all {len(active)}.", count)
        check("one vibe section per vibe", page.locator("details.vibe").count() == len(vibes))
        check("vibe sections start closed", page.locator("details.vibe[open]").count() == 0)
        check("rod has one washer per item", page.locator("#rod .washer").count() == len(active))
        check("capstones stand out on the rod", page.locator("#rod .washer.cap").count() == len(capstones))
        check("page doesn't scroll sideways",
              page.evaluate("document.documentElement.scrollWidth <= window.innerWidth"))

        # Tapping a washer opens that item in the list.
        first = min(active, key=lambda a: a["number"])
        page.locator("#rod .washer").first.click()
        check("tapping a washer opens its item", page.locator(f"#p-{first['number']}").is_visible())

        # Filtering to one vibe shows just that vibe, open.
        page.locator("#chips .chip").nth(2).click()
        check("vibe filter shows one open vibe",
              page.locator("details.vibe").count() == 1 and page.locator("details.vibe[open]").count() == 1)
        page.locator("#chips .chip").first.click()

        # Search narrows the list.
        page.fill("#search", "zzzz-nothing-matches")
        check("search with no matches says so", page.locator(".empty").count() == 1)
        page.fill("#search", "")

        # Proposal form: opens from the link, sends the right fields, shows a thank-you.
        page.click('a[href="#propose"]')
        check("Propose link opens the form", page.locator("#propose-fold").evaluate("e => e.open"))
        form_on = page.locator("#form-off").is_hidden()
        check("form is switched on", form_on, "FORMSPREE_FORM_ID in app.js is empty")
        if not form_on:
            page.close()
            continue
        check("vibe dropdown lists every vibe",
              page.locator("#vibe-select option").count() == len(vibes) + 2)
        page.fill("input[name=accomplishment]", "Smoke test proposal")
        page.select_option("#vibe-select", vibes[0]["name"])
        page.fill("textarea[name=proof]", "Smoke test")
        page.click("button.submit")
        page.wait_for_function("document.querySelector('#form-status').textContent.length > 12")
        body = sent.get("body", "")
        check("form posts to Formspree", sent.get("url", "").startswith("https://formspree.io/f/"))
        for field in ["accomplishment", "vibe", "proof", "handle", "email", "_gotcha"]:
            check(f"form sends '{field}'", f'name="{field}"' in body)
        check("form shows the thank-you message",
              "thanks" in page.locator("#form-status").inner_text().lower())
        page.close()
    browser.close()

server.shutdown()
if failures:
    print(f"\n{len(failures)} check(s) failed.")
    sys.exit(1)
print("\nAll smoke checks passed.")
