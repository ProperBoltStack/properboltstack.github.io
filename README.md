# Proper BoltStack

Source for [properboltstack.github.io](https://properboltstack.github.io): the full list of Proper BoltStack accomplishments and a form for proposing new ones. Plain HTML, CSS and JavaScript, no build step.

- See `MAINTAINING.md` for how to change the list and check it.
- `data/accomplishments.json` is the source of truth for the list: the vibes, the series (core, season drops, local), and every accomplishment with its number, proof, capstone flag, status and dates. To add an approved proposal, add an entry with the next unused number. Numbers are permanent: to retire one, set its `status` to `retired` and fill in `retired` instead of deleting it.
- `app.js` renders the page and sends proposals to Formspree. Paste the form ID into `FORMSPREE_FORM_ID` at the top to switch the form on.
