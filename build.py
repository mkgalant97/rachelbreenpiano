#!/usr/bin/env python3
"""Build the Rachel Breen website.

Edit the files in data/ (most often data/events.json), then run:

    python3 build.py

The finished site is written to the docs/ folder. That folder is what gets published.
To build and preview it locally, run:  python3 build.py --serve
"""
import html
import json
import shutil
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).parent
OUT = ROOT / "docs"
DATA = ROOT / "data"
SITE_URL = "https://www.rachelbreenpiano.com"
YEAR = datetime.now().year

# Where the site lives. While it's a preview at https://mkgalant97.github.io/rachelbreenpiano/
# this is "/rachelbreenpiano". When the real domain is switched over, set it to "" and set
# CUSTOM_DOMAIN to "www.rachelbreenpiano.com".
BASE_PATH = "/rachelbreenpiano"
CUSTOM_DOMAIN = ""

# Contact form endpoint. Paste the Formspree (or similar) URL here once you've set one up,
# e.g. "https://formspree.io/f/abcdwxyz". While it's empty, the form opens the
# visitor's email app with the message pre-filled, addressed to CONTACT_EMAIL.
FORM_ENDPOINT = ""
CONTACT_EMAIL = "rachel@rachelbreenpiano.com"

e = html.escape


def load(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


# ---------------------------------------------------------------- layout

NAV = [
    ("About", "/about/", [("Also About", "/also-about/")]),
    ("News", "/news/", []),
    ("Concerts", "/concerts/", [("Past Performances", "/past-performances/")]),
    ("Media", "/media-1/", []),
    ("Contact", "/contact/", []),
]

ICONS = {
    "youtube": '<svg viewBox="0 0 24 24"><path fill="#f00" d="M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.6 12 3.6 12 3.6s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2 31 31 0 0 0 0 12a31 31 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.5 9.4.5 9.4.5s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1A31 31 0 0 0 24 12a31 31 0 0 0-.5-5.8z"/><path fill="#fff" d="M9.6 15.6 15.8 12 9.6 8.4z"/></svg>',
    "facebook": '<svg viewBox="0 0 24 24"><path fill="#fff" d="M13.5 22v-8.2h2.8l.4-3.2h-3.2V8.5c0-.9.3-1.6 1.6-1.6h1.7V4.1c-.3 0-1.3-.1-2.5-.1-2.5 0-4.2 1.5-4.2 4.3v2.4H7.3v3.2h2.8V22z"/></svg>',
    "instagram": '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.4" cy="6.6" r="1" fill="#fff" stroke="none"/></svg>',
}
SOCIAL = [
    ("youtube", "YouTube", "https://www.youtube.com/channel/UCu1uxYTKnoaKhYGljCEK-sQ"),
    ("facebook", "Facebook", "https://www.facebook.com/rachelbreenpiano/"),
    ("instagram", "Instagram", "https://www.instagram.com/rachelbreenpiano"),
]


def header(active):
    items = []
    for label, href, subs in NAV:
        cls = ' class="active"' if active in (href, *[s[1] for s in subs]) else ""
        sub = ""
        if subs:
            sub = '<ul class="sub">' + "".join(
                f'<li><a href="{h}"{" class=\"active\"" if active == h else ""}>{e(l)}</a></li>' for l, h in subs
            ) + "</ul>"
        items.append(f'<li><a href="{href}"{cls}>{e(label)}</a>{sub}</li>')
    social = "".join(
        f'<a href="{u}" target="_blank" rel="noopener" aria-label="{n}">{ICONS[k]}</a>' for k, n, u in SOCIAL
    )
    return f"""<header class="site-header">
  <a class="home-link" href="/">Home</a>
  <button class="menu-toggle" aria-label="Menu" onclick="this.parentNode.classList.toggle('open')">&#9776;</button>
  <nav><ul>{''.join(items)}</ul><div class="social">{social}</div></nav>
</header>"""


def page(path, title, body, active=None, description="", extra_head="", scripts=""):
    full_title = "Rachel Breen, Pianist" if title is None else f"{title} | Rachel Breen"
    desc = description or "Official website of American pianist Rachel Breen."
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE_URL}{path}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{SITE_URL}/assets/images/og.jpg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
{extra_head}</head>
<body>
{header(active or path)}
<main>
{body}
</main>
<footer class="site-footer">Copyright &copy; {YEAR}, Rachel Breen. All Rights Reserved.</footer>
{scripts}</body>
</html>
"""
    dest = OUT / path.strip("/") / "index.html" if path != "/" else OUT / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(with_base(doc), encoding="utf-8")


def with_base(doc):
    """Prefix site-internal links (href="/...", src="/...", url(/...)) with BASE_PATH."""
    if not BASE_PATH:
        return doc
    for a in ('href="/', 'src="/', 'url(/'):
        doc = doc.replace(a, a[:-1] + BASE_PATH + "/")
    return doc


def img(name, alt="", cls="", loading="lazy"):
    c = f' class="{cls}"' if cls else ""
    return f'<img src="/assets/images/{name}" alt="{e(alt)}"{c} loading="{loading}">'


def paras(text):
    return "".join(f"<p>{line}</p>" for line in text.split("\n\n"))


# ---------------------------------------------------------------- events

def parse(dt):
    return datetime.fromisoformat(dt)


def fmt_time(d):
    return d.strftime("%I:%M %p").lstrip("0")


def fmt_range(ev):
    s, f = parse(ev["start"]), parse(ev["end"])
    start = f"{s.strftime('%b %d, %Y')}, {fmt_time(s)}"
    if s.date() == f.date():
        return f"{start} – {fmt_time(f)}"
    return f"{start} – {f.strftime('%b %d, %Y')}, {fmt_time(f)}"


def event_row(ev):
    s = parse(ev["start"])
    url = f"/event-details-registration/{ev['slug']}/"
    label = ev.get("button", "Details")
    return f"""<li data-end="{ev['end']}">
  <div class="info">
    <div class="date">{s.strftime('%a, %b %d')}</div>
    <div class="title"><a href="{url}">{e(ev['title'])}</a> / <span class="loc">{e(ev['venue'])}</span></div>
  </div>
  <a class="btn" href="{url}">{e(label)}</a>
</li>"""


def build_events(events):
    now = datetime.now()
    upcoming = sorted([x for x in events if parse(x["end"]) >= now], key=lambda x: x["start"])
    past = sorted([x for x in events if parse(x["end"]) < now], key=lambda x: x["start"], reverse=True)

    note = '<p class="note">Please note: tickets cannot be purchased through this website. See vendor websites, or contact Rachel for more information.</p>'
    # Hides an upcoming event automatically once it has ended, even if nobody rebuilds the site.
    hide_past = """<script>document.querySelectorAll('.event-list.upcoming li').forEach(function(li){if(new Date(li.dataset.end)<new Date())li.remove()});</script>"""

    rows = "".join(event_row(x) for x in upcoming) or '<li class="empty">No upcoming events at the moment.</li>'
    page("/concerts/", "Concerts", f"""<section class="concerts">
  <div class="tabs"><a href="/concerts/">Upcoming Performances</a><a class="inactive" href="/past-performances/">Past Performances</a></div>
  {note}
  <ul class="event-list upcoming">{rows}</ul>
</section>""", extra_head='<style>main{background:#1b1c1e url(/assets/images/concerts-bg.jpg) center/cover fixed}</style>\n', scripts=hide_past)

    rows = "".join(event_row(x) for x in past)
    page("/past-performances/", "Past Performances", f"""<section class="concerts">
  <div class="tabs"><a class="inactive" href="/concerts/">Upcoming Performances</a><a href="/past-performances/">Past Performances</a></div>
  <ul class="event-list">{rows}</ul>
</section>""", active="/past-performances/")

    for ev in events:
        url = f"{SITE_URL}/event-details-registration/{ev['slug']}"
        s = parse(ev["start"])
        links = "".join(f'<p><a class="btn" href="{e(l["url"])}" target="_blank" rel="noopener">{e(l["label"])}</a></p>' for l in ev.get("links", []))
        share = (
            f'<a href="https://www.facebook.com/sharer/sharer.php?u={quote(url)}" target="_blank" rel="noopener">Facebook</a>'
            f'<a href="https://twitter.com/intent/tweet?url={quote(url)}&text={quote("Check out this event. Hope to see you there!")}" target="_blank" rel="noopener">X / Twitter</a>'
            f'<a href="https://www.linkedin.com/shareArticle?mini=true&url={quote(url)}" target="_blank" rel="noopener">LinkedIn</a>'
        )
        picture = img(ev["image"], ev["title"], "hero-img") if ev.get("image") else ""
        desc = paras(e(ev.get("description", "")).replace("\n\n", "\n\n")) if ev.get("description") else ""
        desc = desc.replace("\n", "<br>")
        page(f"/event-details-registration/{ev['slug']}/", ev["title"], f"""<article class="event">
  <a class="back" href="/concerts/">&larr; See other events</a>
  <h1>{e(ev['title'])}</h1>
  <div class="when">{s.strftime('%a, %b %d')} &nbsp;|&nbsp; {e(ev['venue'])}</div>
  <div class="desc">{desc}</div>
  {links}
  {picture}
  <h2>Time &amp; Location</h2>
  <p>{fmt_range(ev)}<br>{e(ev['address'])}</p>
  <h2>Share this event</h2>
  <div class="share">{share}</div>
</article>""", active="/concerts/", description=f"{ev['title']} – {fmt_range(ev)}, {ev['address']}")


# ---------------------------------------------------------------- other pages

def build_home():
    page("/", None, """<section class="hero" style="background-image:url(/assets/images/home-hero.jpg)">
  <h1 class="name">Rachel Breen</h1>
  <p class="role">PIANIST</p>
</section>""", active="/")


def build_about(c):
    bio = paras(c["biography"])
    quotes = "".join(
        f'<div><div class="mark">&ldquo;</div><h3>{e(q["source"])}</h3><p>"{e(q["quote"])}"</p></div>' for q in c["quotes"]
    )
    page("/about/", "About", f"""<section class="about">
  <div class="bio"><h1>Biography</h1>{bio}</div>
  <div class="photos">{img("about-1.jpg", "Rachel Breen")}<div class="rule"></div>{img("about-2.jpg", "Rachel Breen performing")}</div>
</section>
<section class="quotes">{quotes}</section>""", description="Biography of American pianist Rachel Breen, laureate of the 2025 Queen Elisabeth Competition.")


def build_also_about(c):
    page("/also-about/", "Also About ", f"""<section class="also">
  <div><h1>Also a Biography</h1>{paras(c["also_biography"])}<p class="pull">{e(c["also_quote"])}</p></div>
  <div class="photos">{img("also-1.jpg", "")}{img("also-2.jpg", "")}{img("also-3.jpg", "")}</div>
</section>""", extra_head='<style>main{background:#1b1c1e url(/assets/images/also-bg.jpg) center/cover fixed}</style>\n')


def build_news(items):
    # Each news image is a screenshot that already shows the article headline, so no caption is added.
    cards = [
        f'<a class="news-card" href="{e(n["url"])}" target="_blank" rel="noopener">{img(n["image"], n.get("title", ""))}</a>'
        for n in items
    ]
    page("/news/", "News", f"""<section class="news"><h1>News</h1><div class="news-grid">{''.join(cards)}</div></section>""")


def build_media(m):
    # Real YouTube players, so each video shows YouTube's own title bar, Share,
    # Watch later and "Watch on YouTube" controls, as on the original site.
    videos = "".join(
        f'<div class="yt"><iframe src="https://www.youtube.com/embed/{v["id"]}" title="{e(v["title"])}" loading="lazy" '
        f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" '
        f'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>'
        for v in m["videos"]
    )
    photos = "".join(img(p, "") for p in m["photos"])
    script = """<div class="lightbox" onclick="this.classList.remove('open')"><img alt=""></div>
<script>
var lb=document.querySelector('.lightbox');
document.querySelectorAll('.photo-grid img').forEach(function(i){i.addEventListener('click',function(){lb.querySelector('img').src=i.src;lb.classList.add('open');});});
</script>
"""
    page("/media-1/", "Media", f"""<section class="media"><h1>Videos</h1><div class="video-grid">{videos}</div></section>
<div class="photos-band"><section class="media"><h1>Photos</h1><div class="photo-grid">{photos}</div></section></div>""", scripts=script)


def build_contact():
    if FORM_ENDPOINT:
        form_attrs = f'action="{FORM_ENDPOINT}" method="POST"'
        handler = """<script>
document.querySelector('.contact form').addEventListener('submit',function(ev){ev.preventDefault();var f=ev.target;
fetch(f.action,{method:'POST',body:new FormData(f),headers:{Accept:'application/json'}}).then(function(r){if(r.ok){f.reset();f.querySelector('.thanks').style.display='inline';}else{alert('Sorry, something went wrong. Please email rachel@rachelbreenpiano.com.');}});});
</script>
"""
    else:
        form_attrs = 'action="#"'
        handler = f"""<script>
document.querySelector('.contact form').addEventListener('submit',function(ev){{ev.preventDefault();var f=ev.target;
var body='Name: '+f.first.value+' '+f.last.value+'\\nEmail: '+f.email.value+'\\nPhone: '+f.phone.value+'\\n\\n'+f.message.value;
location.href='mailto:{CONTACT_EMAIL}?subject='+encodeURIComponent('Website message from '+f.first.value+' '+f.last.value)+'&body='+encodeURIComponent(body);
f.querySelector('.thanks').style.display='inline';}});
</script>
"""
    page("/contact/", "Contact", f"""<section class="contact bg-photo" style="background-image:url(/assets/images/contact-bg.jpg)">
  <div class="intro">
    <h1>Contact</h1>
    <p>To contact Rachel directly, please use the contact form on this page, or write to <a href="mailto:rachel@rachelbreenpiano.com">rachel@rachelbreenpiano.com</a>.</p>
    <p>For Inquiries through National Federation of Music Clubs, please contact Starla Blair at: <a href="mailto:blair.starla@sbcglobal.net">blair.starla@sbcglobal.net</a></p>
  </div>
  <form {form_attrs}>
    <label>First Name<input name="first" autocomplete="given-name"></label>
    <label>Last Name<input name="last" autocomplete="family-name"></label>
    <label>Email *<input name="email" type="email" required autocomplete="email"></label>
    <label>Phone<input name="phone" type="tel" autocomplete="tel"></label>
    <label class="full">Leave us a message...<textarea name="message"></textarea></label>
    <input type="text" name="_gotcha" style="display:none" tabindex="-1" autocomplete="off">
    <div class="submit-row"><span class="thanks">Thanks for submitting!</span><button type="submit">Submit</button></div>
  </form>
</section>""", scripts=handler)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    if CUSTOM_DOMAIN:
        (OUT / "CNAME").write_text(CUSTOM_DOMAIN + "\n")
    (OUT / ".nojekyll").write_text("")

    content = load("content.json")
    build_home()
    build_about(content)
    build_also_about(content)
    build_news(load("news.json"))
    build_events(load("events.json"))
    build_media(load("media.json"))
    build_contact()
    print(f"Built site in {OUT}")


def serve(port=8000):
    """Preview the built site locally at the same address layout as the live site."""
    import functools, http.server, sys, tempfile
    root = Path(tempfile.mkdtemp())
    if BASE_PATH:
        (root / BASE_PATH.strip("/")).symlink_to(OUT.resolve())
    else:
        root = OUT
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
    print(f"Preview at http://localhost:{port}{BASE_PATH}/  (Ctrl+C to stop)")
    http.server.ThreadingHTTPServer(("", port), handler).serve_forever()


if __name__ == "__main__":
    import sys
    main()
    if "--serve" in sys.argv:
        serve()
