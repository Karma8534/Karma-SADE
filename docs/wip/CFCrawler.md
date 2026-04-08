# CFCrawler

*Converted from: CFCrawler.PDF*



---
*Page 1*


Open in app
1
Search Write
Coding Nexus
Member-only story
Cloudflare One
crawl:
API Call That Crawls an
Entire Website
Sonu Yadav Following 4 min read · Mar 11, 2026
12
Web scraping used to require a whole setup. Spin
up Playwright or Puppeteer, manage browser
instances, handle pagination, deal with JavaScript-
rendered pages, write retry logic, and parse the
HTML yourself. Half a day of work before you’ve
scraped a single page.


---
*Page 2*


Cloudflare just collapsed all of that into one API
call.
What’s New
Cloudflare’s Browser Rendering now has a /crawl
endpoint in open beta. You give it a URL. It crawls
the whole site. It returns the content in whatever
format you need — HTML, Markdown, or
structured JSON.
No browser management. No scripts. No
infrastructure to babysit.


---
*Page 3*


This is available on both the Workers Free and Paid
plans.
The Basics
Two requests. That’s the whole workflow.
Start the crawl:
# Initiate a crawl
curl -X POST 'https://api.cloudflare.com/client/v4/ac
-H 'Authorization: Bearer <apiToken>' \
-H 'Content-Type: application/json' \
-d '{
"url": "https://blog.cloudflare.com/"
}'
You get back a job ID. The crawl runs
asynchronously in the background.
Check the results:
# Check results
curl -X GET 'https://api.cloudflare.com/client/v4/acc


---
*Page 4*


-H 'Authorization: Bearer <apiToken>'
When it’s done, the response looks like this:
{
"total": 10,
"finished": 10,
"records": [{
"url": "https://blog.cloudflare.com/",
"metadata": { "title": "...", "status": 200 },
"html": "<!DOCTYPE html>..."
}]
}
Every page returns its URL, title, HTTP status, and
full content. Clean.


---
*Page 5*


Why This Actually Matters
The obvious use cases are the ones Cloudflare
mentions — training data for models, RAG
pipelines, content monitoring. All of those require
bulk content extraction from sites, and until now
that meant either paying for a scraping service or
maintaining your own.
But there’s a subtler thing here too. This runs in a
headless browser. That means JavaScript-heavy


---
*Page 6*


sites — single-page apps, React sites, anything that
requires JS to render — get properly rendered
before the content is returned. Most scrapers can’t
do that without significant setup.
You’re not getting raw HTML that’s half-empty
because the content loads dynamically. You’re
getting what a real browser sees.
The Controls Worth Knowing
The endpoint has optional parameters for when a
basic crawl isn’t enough.
Crawl depth and page limits — set how deep you
want to go and cap the total pages. Useful when
you only want the top-level content and don’t need
to go five links deep.
Wildcard URL patterns — include or exclude
specific paths. Say you only want /blog/ content
and want to skip /docs/. You can set that.


---
*Page 7*


URL discovery source — the crawler finds new
pages either from sitemaps, from links on each
page, or both. You pick.
Incremental crawling — this is the practical one.
Use modifiedSince or maxAge to skip pages that
haven't changed since your last crawl. If you're
running this on a recurring schedule to monitor a
site, you're only fetching what's actually new.
Static mode — set render: false and the crawler
skips the headless browser entirely, just fetching
raw HTML. Much faster for static sites that don't
need JavaScript rendering.
It Respects robots.txt
The crawler honors robots.txt directives,
including crawl-delay. It's designed to behave like
a well-mannered bot rather than a hammer.
Cloudflare has documentation on best practices


---
*Page 8*


for robots.txt and sitemaps to help your crawls go
smoothly from the start.
When You’d Actually Use This
A few scenarios where this replaces a lot of custom
work:
Building a RAG system over a documentation site.
Point the crawler at the docs, get everything back
in Markdown, chunk it, embed it. The Markdown
output in particular is clean enough to feed
directly into most pipelines without preprocessing.
Monitoring competitor content. Run an
incremental crawl weekly with modifiedSince set to
your last run date. Only changed pages come back.
You see exactly what's new.
Creating training data. Crawl sites in bulk, collect
HTML or structured JSON, feed into your data


---
*Page 9*


pipeline. The async job model handles large sites
without timing out.
One-off research. Sometimes you just need
everything from a site without writing a script for
it. This is that.
Where to Go From Here
The full list of optional parameters is at
developers.cloudflare.com/browser-
rendering/rest-api/crawl-endpoint. Crawl depth,
caching, URL sources, wildcard patterns — it’s all
there.
robots.txt best practices are at
developers.cloudflare.com/browser-
rendering/reference/robots-txt.
The endpoint is currently in open beta. Free plan
users can try it without any paid commitment.


---
*Page 10*


Two curl commands to crawl a whole site. That’s
where we are now.
😭😂


---
*Page 11*


API Cloudflare Openclaw Web Crawler Claude Code


---
*Page 12*


Published in Coding Nexus
Following
19.1K followers · Last published 2 days ago
Coding Nexus is a community of developers, tech
enthusiasts, and aspiring coders. Whether you’re
exploring the depths of Python, diving into data
science, mastering web development, or staying
updated on the latest trends in AI, Coding Nexus has
something for you.
Written by Sonu Yadav
Following
461 followers · 6 following
I simplify programming concepts and make coding
accessible for everyone!
No responses yet
To respond to this story,
get the free Medium app.


---
*Page 13*


More from Sonu Yadav and Coding Nexus
Sonu Yadav Code Pulse
Claude Can Now Draw Google Just Shipped a
Di (A d Th CLI f All f G l
I’ve been asking AI to create If you’ve ever had to write curl
di f Th ll i t G l ’ REST
Feb 24 Mar 4
Jatin Prasad Sonu Yadav
Unlock Claude AI’s How I Built a Bot That
S ith 10 T d P l k t
Transform Your Workflow with Three AI agents. One
B ttl T t d P ti di ti k t Z
Feb 11 Mar 19


---
*Page 14*


See all from Sonu Yadav See all from Coding Nexus
Recommended from Medium
Amit Kumar In by
Write A Catal… 𝐍𝐀𝐉𝐄𝐄𝐁…
How to Build Beautiful
6 Boring Micro SaaS
W b it ith Cl d
Ni h Th t C ld
AI can generate websites very
The overlooked business
i kl t d B t t AI
i h h i l ft
Feb 21 Mar 22
In by In by
Activated… Adi Insights and… The Startup Kevin Gabeci


---
*Page 15*


I Ignored 40+ We Built an AI Platform
O F Alt ti Whil W ki 9 t 5
Everyone is building agent No funding. No quitting our
f k M t P th j b J t t d l
Mar 21 Feb 5
Rost Glukhov In by
The Hackers Ma… 𝐍𝐀𝐉𝐄𝐄…
Best LLMs for Ollama
5 High-Ticket AI
16GB VRAM GPU
A t ti S ll
Running large language
I used to think I understood
d l l ll i
h t ll b i t
Feb 21 Mar 9
See more recommendations