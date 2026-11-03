# Maintaining rachelbreenpiano.com

The easiest way to change the site is to open Claude Code in this folder and say what should change, for example "add a concert on March 3 in Berlin."

## How it's organized

| What | Where |
|---|---|
| Concerts (upcoming and past) | `data/events.json` |
| News cards | `data/news.json` |
| Videos and photos on the Media page | `data/media.json` |
| About and Also About text, press quotes | `data/content.json` |
| Colors, fonts, layout | `assets/style.css` |
| Photos | `assets/images/` |
| Page templates | `build.py` |

The site that gets published is generated into `docs/`. **Don't edit `docs/` by hand,** because every build replaces it.

## Making a change by hand

1. Edit a file in `data/`.
2. Run `python3 build.py`.
3. Preview the site: run `python3 -m http.server 8000 --directory docs`, then open http://localhost:8000.
4. Publish the change: `git add -A && git commit -m "Describe the change" && git push`. GitHub Pages updates the live site within about a minute.

The site is hosted on GitHub Pages from the `docs/` folder of https://github.com/mkgalant97/rachelbreenpiano. The preview address is https://mkgalant97.github.io/rachelbreenpiano/.

## Moving to the real domain

1. In `build.py`, set `BASE_PATH = ""` and `CUSTOM_DOMAIN = "www.rachelbreenpiano.com"`, then rebuild and push.
2. In the GitHub repo, go to Settings → Pages and enter the custom domain there too.
3. At the domain registrar, point `www` to `mkgalant97.github.io` with a CNAME record, and add GitHub's A records for the bare domain.

## Concerts

Each concert is one entry in `data/events.json`:

```json
{
  "slug": "recital-in-berlin",
  "title": "Recital in Berlin",
  "venue": "Berlin",
  "start": "2027-03-03T19:30", "end": "2027-03-03T21:30",
  "address": "Venue name, street, city, country",
  "description": "Program: Bach, Beethoven",
  "image": "events/2fb09f0d.jpg",
  "links": [{"label": "Tickets", "url": "https://..."}]
}
```

`description`, `image` and `links` are optional. A concert moves from Upcoming to Past Performances on its own once its end time passes. The Concerts page hides finished concerts even before the next rebuild.

## Contact form

Until a form service is connected, the Submit button opens the visitor's own email app with the message filled in.

To deliver messages straight to Rachel's inbox:
1. Create a free form at https://formspree.io.
2. Paste the form's URL into `FORM_ENDPOINT` near the top of `build.py`.
3. Rebuild.
