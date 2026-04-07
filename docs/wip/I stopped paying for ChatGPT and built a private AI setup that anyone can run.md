# I stopped paying for ChatGPT and built a private AI setup that anyone can run

*Converted from: I stopped paying for ChatGPT and built a private AI setup that anyone can run.PDF*



---
*Page 1*


 
I stopped paying for ChatGPT and built a
private AI setup that anyone can run
CCrreeddiitt:: RRaagghhaavv SSeetthhii//MMaakkeeUUsseeOOff
  
Follow Like Thread Add us on
–
By Raghav Sethi Feb 19, 2026, 9:30 AM EST
I’ve really gotten into running LLMs locally lately, and after seeing all the cool things
you can with MCP tools, I figured it was time to upgrade my own setup a bit.


---
*Page 2*


Ad
Link copied to clipboard
Ad
I initially jumped on the hype train when DeepSeek R1 launched, but since then, a
ton of new models have come out. With how quickly everything is changing, I
thought it only made sense to refine my workflow as well.
LM Studio
LM Studio is a desktop app that lets you download, manage, and run large language models directly on
your computer. It even has a GUI to chat with models locally without relying on cloud services.
See at LM Studio
LM Studio is the best local LLM app I’ve used
(yet)
Ollama is good, but I like this better


---
*Page 3*


  
Ad
Link copied to clipboard
Ad
✕ Remove Ads
Ad
I first started experimenting with local LLMs last year using Ollama. It worked well
enough, but my poor MacBook Air with just 8GB of unified memory definitely wasn’t
built to handle that kind of workload. I still wanted to try something different, partly
out of curiosity and partly to see if I could squeeze out more performance.
That's why I decided to give LM Studio a shot. It's an app that lets you download and
run LLMs locally on your machine, and has a clean UI to go along with it too. Since I
am on a Mac, MLX support for me was a big deal. If you're unfamiliar, MLX is
Apple's machine learning framework designed specifically for Apple silicon.
✕ Remove Ads
Ad


---
*Page 4*


Ad
Link copied to clipboard
Ad
It essentially allows models to run more efficiently using the GPU. But still, I wanted
to put these words into numbers, so I compared Ollama to LMStudio head-to-head,
with the same model.
CCrreeddiitt:: RRaagghhaavv SSeetthhii//MMaakkeeUUsseeOOff
I was getting higher tokens per second with LM Studio, but the difference was small
enough that it didn’t really change the overall experience. Still, I’ll take any extra
performance I can get.
That said, I don’t think it makes a huge difference whether you choose Ollama or LM
Studio, especially since both rely on similar underlying frameworks to run models
locally.
✕ Remove Ads


---
*Page 5*


Ad
Link copied to clipboard
Ad
Ad
My main complaint when I first started was the lack of multimodal support. But
that’s no longer really an issue. Both Ollama and LM Studio now support multimodal
models, and there are a few solid options out there that can handle text and images
surprisingly well on local hardware.
RELATED
Sep 7, 2025
I now use this offline AI assistant instead of
cloud chatbots
Even with cloud-based chatbots, I'll always use this offline AI
assistant I found.
By Jayric Maning |  1
Choosing the right model can be a bit tricky
It can be an expensive hobby


---
*Page 6*


Ad
Link copied to clipboard
Ad
✕ Remove Ads
Ad
When you first install LM Studio, the very first thing you’ll need to do is pick a model.
That can feel a bit overwhelming if you’re new to this, because there isn’t a clear-cut
“just use this one” answer. The right choice really depends on your hardware.
If you open the Model Search menu in LM Studio, you'll see a list of the most
popular models. A simple way to understand how demanding a model will be is to
look at the number right before the "B" in its name.


---
*Page 7*


That "B" stands for billions of parameters. In general, the higher that number, the
Ad
Link copied to clipboard
more capable the model tends to be. ThisA adlso means it will require more resources.
On a Mac with 8GB of Unified Memory, I feel like anywhere from 3 to 4B parameters
is the sweet spot. Things can get a little more confusing on a PC. Instead of regular
system RAM, the amount of VRAM you have matters more.
✕ Remove Ads
Ad
If you have 8GB of VRAM, you can comfortably experiment with 7B parameter
models, especially in lighter quantizations. In my experience, the best approach is to
start with a smaller model and gradually move up until you find the sweet spot.
Personally, I have gravitated more towards the Gemma 3 4B model, which is built on
the same foundation as Google's Gemini models. That said, I would still recommend
trying the Qwen models as well. Depending on what you're doing, they might be
much better for you.
You can even add web search to your local LLM
DuckDuckGo comes to the rescue


---
*Page 8*


Ad
Link copied to clipboard
Ad
✕ Remove Ads
Ad
One of the biggest complaints I’ve seen about local LLMs is how limited they can
feel compared to cloud ones like ChatGPT when it comes to web search. It's not
very helpful if you ask about the latest iPhone, and the LLM starts yapping about the
iPhone 14. That's one area where cloud models have usually had the upper hand.
LM Studio has a built-in plugin system, and adding web search is pretty
straightforward. Just head over to the DuckDuckGo plugin page, and select Run in


---
*Page 9*


LM Studio.
Ad
Link copied to clipboard
Ad
MUO Report: Subscribe and never miss what matters
Stay updated with the latest tech trends, expert tips, and product reviews in the world of
technology with MUO's Newsletters.
Email Address
 Subscribe
By subscribing, you agree to receive newsletter and marketing emails, and accept our Terms of Use and Privacy Policy.
You can unsubscribe anytime.
Once enabled, whenever you run a model, you’ll see an option below the chat box
asking whether you want to invoke DuckDuckGo for your query. If you toggle it on,
LM Studio will fetch live search results and feed them into the model before it
generates a response.
✕ Remove Ads
Ad


---
*Page 10*


Ad
Link copied to clipboard
Ad
That's not all you can do with plugins, though. The LM Studio team has built a few
plugins which are super useful too. For example, they have a Wikipedia plugin which
allows your LLM to read and search for articles from Wikipedia (duh).
There is also a JavaScript Sandbox plugin, which can be super helpful if you're into
vibe-coding and want to get a rough idea quickly built. But I wouldn't say it is
worthwhile enough to create something production-ready.
✕ Remove Ads
Ad
RELATED


---
*Page 11*


Ad
Link copied to clipboard Sep 30, 2025
Ad
I’ll never pay for AI again
AI doesn’t have to cost you a dime—local models are fast, private,
and finally worth switching to.
By Yadullah Abidi |  7
Ditch the corporations
You can set up LM Studio so you can access your LLM from your phone, but if you
want to move all the inference directly onto your phone, that’s possible too. You can
run smaller LLMs on an Android phone, although they won’t be as powerful as what
you’d get on your Mac.
Still, these lightweight models are improving at a crazy rapid pace. And with
hardware costs expected to rise, I wouldn’t be surprised if companies like OpenAI or
Google increased their subscription prices. It feels reassuring to have a setup that
isn’t affected by any of that.
✕ Remove Ads
___
Ad
Productivity Artificial… ChatGPT
  
Follow Like Share


---
*Page 12*


 THREAD Ad
Link copied to clipboard
Ad
We want to hear from you! Share your opinions in the thread below and remember to keep it respectful.

Be the first to post

This thread is open for discussion.
Be the first to post your thoughts.
Terms |Privacy |Feedback
✕ Remove Ads
Ad

RECOMMENDED


---
*Page 13*


3 days ago 3 days ago 4 days ago
Ad
Link copied to clipboard
Android 17 beta 1 is here OpenClaw'sA crdeator has Your router has this
— 5 changes worth trying joined OpenAI — here's setting disabled by
first why that's a big deal default, and it's slowing…
Ad
Join Our Team
Our Audience
About Us
Press & Events
Media Coverage
Contact Us
Follow Us
     


---
*Page 14*


Advertising
Ad
Link copied to clipboard Careers
Ad
Terms
Privacy
Policies
MUO is part of the Valnet Publishing Group
Copyright © 2026 Valnet Inc.