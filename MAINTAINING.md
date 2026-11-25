# Maintaining Proper BoltStack

How the site works and how to change it, without needing to touch the front-end code.

## How the pieces fit

| File | What it is | How often you'll touch it |
| --- | --- | --- |
| `data/accomplishments.json` | The list: vibes, series and every accomplishment. The only copy anywhere. | Any time the list changes |
| `scripts/check_list.py` | Checks the list for mistakes. GitHub runs it on every push. | Rarely |
| `scripts/smoke_test.py` | Loads the site in a real browser and checks the list, the rod, the filters and the proposal form. GitHub runs it after the list check. | Rarely |
| `index.html` | The page's wording and layout | When the copy changes |
| `app.js` | Loads the list, builds the vibe sections, sends proposals to Formspree | Rarely |

The site is GitHub Pages: whatever is on the `main` branch is live at https://properboltstack.github.io within a minute or two of a push. There's no build step.

## Changing the list

### The easy way: in the browser

1. Open `data/accomplishments.json` on GitHub and click the pencil icon.
2. Make the change and click **Commit changes**.
3. Wait a minute or two, then check the site.
4. If a red X shows up next to your commit, click it. "check" means the list has a mistake; "smoke" means the page itself broke. Either one says exactly what's wrong.

### On your computer

1. Edit `data/accomplishments.json` in VS Code (it highlights JSON mistakes as you type).
2. Run `python scripts/check_list.py`. If you changed `index.html` or `app.js`, also run `python scripts/smoke_test.py` (one-time setup: `pip install playwright` then `python -m playwright install chromium`).
3. Commit and push.

To preview the site locally, run `python -m http.server` in the repo folder and open http://localhost:8000. Opening `index.html` straight from the folder won't load the list, because browsers block that.

### What an entry looks like

```json
{
  "number": 30,
  "series": "core",
  "vibe": "stunts",
  "title": "Ride in an organized stunt show or exhibition",
  "proof": "Event lineup or organizer",
  "capstone": true,
  "status": "active",
  "added": "2026-11-24",
  "retired": null
}
```

- `true`, `false` and `null` have no quotes. Everything else that's text does.
- Every entry but the last needs a comma after its closing `}`.
- The order of entries in the file doesn't matter. The site sorts by number.

### Common changes

| Change | What to do |
| --- | --- |
| Add an approved proposal | New entry with the next unused number, today's date in `added`, `"retired": null` |
| Fix wording | Edit `title` or `proof`. Fine for typos; if the meaning changes after launch, retire it and add a new number instead |
| Retire one | Set `"status": "retired"` and put the date in `retired`. Never delete it: someone may have that washer |
| Season drop | Add the series to the `series` list first (e.g. `{"key": "2027-season", "name": "2027 season drop"}`), then add entries with that series |

### The one rule

Before launch, numbers can be swapped freely. After launch, never renumber or reuse a number: a washer stamped #037 has to mean the same thing forever. The checker catches duplicate numbers, but it can't tell that you renumbered something.

## Proposals

The form posts to Formspree (form ID `mgakrpob`, set at the top of `app.js`). Proposals arrive by email and on the Formspree dashboard. The free plan takes 50 a month.
