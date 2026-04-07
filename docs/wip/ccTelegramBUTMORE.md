# ccTelegramBUTMORE

*Converted from: ccTelegramBUTMORE.pdf*



---
*Page 1*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Member-only story
How I’m Using (New) Claude Code
Telegram (To Run from Anywhere)
Joe Njenga Following 10 min read · 7 hours ago
119 2
Claude Code Telegram channel is the new native way to launch and monitor
Claude Code sessions right from your phone.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 1/44


---
*Page 2*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
In the last Claude Code Channels tutorial, I set up the Fakechat demo and
proved that Claude Code Channels works. Messages go in, Claude processes
them, and responses come back through the same channel.
Now it’s time to connect a real platform — Telegram.
In this article, I’ll walk you through connecting Telegram to Claude Code,
step by step.
If you are not a Paid Medium member, you can read
the full article here for FREE, but please consider
joining Medium to support my work — Thank you!
By the end, you’ll be sending coding tasks from your phone and getting
responses directly in Telegram.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 2/44


---
*Page 3*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 3/44


---
*Page 4*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Here’s what it looks like when it’s working:
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 4/44


---
*Page 5*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
This message is set to Claude Code responding, and
the task begins:
Open in app
Search Write
The setup takes a few minutes. You’ll need:
Claude Code v2.1.80 or later (we covered this in Part 1)
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 5/44


---
*Page 6*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Bun installed
A Telegram account
If you haven’t set up the prerequisites yet, go through the first Claude Code
channels tutorial.
Let’s start by creating the Telegram bot.
Creating the Telegram Bot
Telegram bots are created through BotFather, Telegram’s official bot
management tool.
The whole process takes about 2 minutes.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 6/44


---
*Page 7*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Step 1: Open BotFather
Open Telegram and search for @BotFather. Start a chat and send:
/newbot
BotFather asks for two things.
Step 2: Set the Bot Name
This is the display name shown in chat headers. It can be anything, spaces
allowed.
I named mine Claude Code Agent.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 7/44


---
*Page 8*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Step 3: Set the Bot Username
This is a unique handle that must end in bot. It becomes your bot's public
link.
For example: my_claude_code_bot gives you t.me/my_claude_code_bot
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 8/44


---
*Page 9*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
I chose the username as t.me/njenga_claude_code_bot
Step 4: Copy Your Token
BotFather replies with a token that looks like:
123456789:AAHfiqksKZ8WzXy...
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 9/44


---
*Page 10*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Copy the entire thing, including the leading number and colon. Store it
somewhere safe.
You’ll need this token in the next section to connect the bot to Claude Code.
What the Bot Looks Like Before Connecting
At this point, your bot exists on Telegram, but it’s empty.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 10/44


---
*Page 11*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
If you search for it and send a message, nothing happens. There’s no code
behind it yet.
That changes in the next step when we install the channel plugin and point it
at this bot.
Installing and Configuring the Plugin
Now we connect the bot to Claude Code.
This is where the Telegram bot goes from an empty shell to a live channel in
your coding session.
Step 1: Install the Telegram Plugin
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 11/44


---
*Page 12*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Start a Claude Code session in your project folder:
claude
Once loaded, run:
/plugin install telegram@claude-plugins-official
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 12/44


---
*Page 13*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
You’ll see the plugin installation options. Choose your preferred scope (User or
Project). After installation, you should see:
✓ Installed telegram. Run /reload-plugins to activate.
To confirm it’s installed, run /plugins and check the installed tab.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 13/44


---
*Page 14*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Step 2: Configure Your Token
Still in your Claude Code session, run:
/telegram:configure <your-bot-token-here>
Replace <your-bot-token-here> with the actual token from BotFather.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 14/44


---
*Page 15*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
This saves the token to .claude/channels/telegram/.env in your project
directory.
You can also set TELEGRAM_BOT_TOKEN in your shell environment before
launching Claude Code. Shell environment takes precedence over the .env
file.
When completed successfully, you should see this message :
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 15/44


---
*Page 16*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Token saved. Here's your current status:
---
Telegram Channel Status
Token: 8XXXXXXXXX:... (set)
Access: No access.json — defaults apply
- DM policy: pairing (anyone who DMs gets a code they can use to pair)
- Allowed senders: 0
- Pending pairings: 0
---
What next:
DM your bot on Telegram. It will reply with a pairing code — then approve yourself
/telegram:access pair <code>
Once you've done that, we'll lock the bot down to allowlist-only so nobody else ca
▎ Note: The token is read at server boot. If the Telegram channel server is alread
it (or run /reload-plugins) for the token to take effect.
 
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 16/44


---
*Page 17*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 17/44


---
*Page 18*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Step 3: Restart with the Channel Flag
The plugin won’t connect without the --channels flag. Exit your session:
/exit
Then restart with the flag:
claude --channels plugin:telegram@claude-plugins-official
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 18/44


---
*Page 19*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
You should see the familiar listening message, similar to what we saw with
Fakechat in Part 1.
The Telegram plugin is now polling for messages from your bot.
Step 4: Verify the Bot is Alive
Open Telegram and find your bot. You can search for the username you
created or open t.me/your_bot_username.
Send a quick message like “hello”.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 19/44


---
*Page 20*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 20/44


---
*Page 21*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
If the channel is working, the bot should respond with a pairing code. We’ll
handle that in the next section.
If nothing happens, check your terminal. Claude Code should show an
inbound event. If it doesn’t, the token might be wrong. Re-run
/telegram:configure <token> and restart.
Pairing, Security & Testing
Your bot is live, and Claude Code is listening.
Now we need to pair your Telegram account so your messages reach Claude.
Step 1: Trigger the Pairing Code
Open Telegram on your phone and find your bot. Send any message —
“hello” works.
The bot replies with a 6-character pairing code.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 21/44


---
*Page 22*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
If the bot doesn’t respond, make sure Claude Code is running with --channels
from the previous section.
Step 2: Pair Your Account
Back in your Claude Code terminal, run:
/telegram:access pair <code>
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 22/44


---
*Page 23*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Replace <code> with the 6-character code from Telegram.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 23/44


---
*Page 24*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Your account is now linked. The next message you send from Telegram goes
straight to Claude.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 24/44


---
*Page 25*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 25/44


---
*Page 26*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Step 3: Lock It Down
Pairing mode is only for capturing your user ID. Once you’re paired, switch
to allowlist mode:
/telegram:access policy allowlist
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 26/44


---
*Page 27*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 27/44


---
*Page 28*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Now, only your Telegram account can push messages into your Claude Code
session.
Testing with a Real Task
Time for the real test. Send a coding task from Telegram:
list all files in my working directory and tell me what this project does
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 28/44


---
*Page 29*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Watch your terminal while this happens. You’ll see the full flow:
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 29/44


---
*Page 30*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
The inbound message arriving as a <channel source="telegram"> event
Claude processing the request
The reply tool call going back to Telegram
A confirmation
The response appears in Telegram within seconds.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 30/44


---
*Page 31*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Try a more complex task to push it further:
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 31/44


---
*Page 32*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
create a simple database connection script in the working directory that we will
use to save the data for the app.
 
Claude should create the file and confirm through Telegram. Check your
project folder to verify the file exists.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 32/44


---
*Page 33*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 33/44


---
*Page 34*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Telegram-Specific Features
A few things worth knowing now that your channel is running.
Photos — You can send an image to your bot, and Claude can read it. Photos
get downloaded to ~/.claude/channels/telegram/inbox/. Note that Telegram
compresses photos. For full quality, long-press and select "Send as File".
Typing indicator — While Claude works on a response, your bot shows
“typing…” in Telegram. So you know it’s processing.
No message history — Telegram’s Bot API doesn’t expose message history or
search. The bot only sees messages as they arrive. If Claude needs earlier
context, it will ask you to paste or summarize.
Reply threading — Claude can reply to specific messages using Telegram’s
native threading.
Tools Claude Gets
When the Telegram channel is active, Claude has three tools:
reply — Send a message back to the chat. Supports file attachments up to
50MB. Images send as photos with inline preview, other files as documents.
react — Add an emoji reaction to a message. Only Telegram's fixed emoji
whitelist works
edit_message — Edit a message the bot previously sent. Useful for "working..."
to result progress updates.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 34/44


---
*Page 35*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Troubleshooting Common Issues
Here are the issues you’re most likely to hit during setup and how to fix
them.
1) The bot doesn’t respond to messages
This is usually one of two things. Either Claude Code isn’t running with the -
-channels flag, or the token is wrong.
Check your terminal first. If you don’t see any inbound event when you
message the bot, the plugin isn’t receiving messages. Re-run
/telegram:configure <token> with the correct token and restart with --
channels.
2) Auth conflict error on startup
If you see a warning about conflicting authentication methods, it means
Claude Code has both a login session and an environment variable set.
Run /logout to clear the stored login, then restart. Channels require claude.ai
login, so make sure you're authenticated with your claude.ai account, not an
API key.
3) Pairing code expired or doesn’t work
Send another message to the bot to get a fresh code. Type the code exactly as
shown — it’s case-sensitive.
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 35/44


---
*Page 36*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
4) Permission prompts pause the session
If Claude hits a permission prompt while processing a channel message, the
session pauses until you approve locally in the terminal.
For unattended use, --dangerously-skip-permissions bypasses prompts but
only use this in environments you fully trust.
5) Messages send but no response appears in Telegram
Check the terminal. If you see Claude processing the request and the reply
tool call shows “sent”, the message is on its way. Telegram sometimes has a
slight delay for longer responses.
If the terminal shows an error during the reply tool call, the response was too
long, or the bot lost connection. Try a simpler task to confirm the flow works.
6) Token issues
Make sure you copied the full token from BotFather, including the number
before the colon. Check .claude/channels/telegram/.env in your project
folder to verify it was saved.
If you accidentally expose your token, go to BotFather and send /revoke to
generate a new one.
Final Thoughts
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 36/44


---
*Page 37*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
The Telegram setup took about 5 minutes from creating the bot to sending
my first real task.
The pairing flow is smooth, and the allowlist security model is simple to
understand.
What’s Next
This is Article 2 of a 3-part series on Claude Code Channels.
Article 1 (if you missed it): Prerequisites, dependencies, and the Fakechat
localhost demo — I Tested (New) Claude Code Channels (Real OpenClaw
Killer)
Article 3: Connecting Discord to Claude Code. In the next article, I’ll walk
through the full Discord setup. Discord has a few more steps than
Telegram (developer portal, permissions, server invite), but it also gives
Claude extra tools that Telegram doesn’t have — message history and
attachment downloads.
Finally, I’ll cover running both channels simultaneously and an honest
comparison between Channels and OpenClaw.
Follow along so you don’t miss the upcoming tutorials, and if you have any
questions, let me know in the comments below.
Claude Code Masterclass Course
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 37/44


---
*Page 38*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Every day, I’m working hard to build the ultimate Claude Code course, which
demonstrates how to create workflows that coordinate multiple agents for
complex development tasks. It’s due for release soon.
It will take what you have learned from this article to the next level of
complete automation.
New features are added to Claude Code daily, and keeping up is tough.
The course explores Agents, Hooks, advanced workflows, and productivity
techniques that many developers may not be aware of.
Once you join, you’ll receive all the updates as new features are rolled out.
This course will cover:
Advanced subagent patterns and workflows
Production-ready hook configurations
MCP server integrations for external tools
Team collaboration strategies
Enterprise deployment patterns
Real-world case studies from my consulting work
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 38/44


---
*Page 39*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
If you’re interested in getting notified when the Claude Code course
launches, click here to join the early access list →
( Currently, I have 33,000+ already signed-up developers)
I’ll share exclusive previews, early access pricing, and bonus materials with
people on the list.
Let’s Connect!
If you are new to my content, my name is Joe Njenga
Join thousands of other software engineers, AI engineers, and solopreneurs who
read my content daily on Medium and on YouTube, where I review the latest AI
engineering tools and trends. If you are more curious about my projects and
want to receive detailed guides and tutorials, join thousands of other AI
enthusiasts in my weekly AI Software Engineer newsletter
If you would like to connect directly, you can reach out here:
One moment, please...
Edit description
njengah.com
Follow me on Medium | YouTube Channel | X | LinkedIn
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 39/44


---
*Page 40*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Claude Code Anthropic Claude Anthropic Claude Code Telegram Claude
Written by Joe Njenga
Following
19.4K followers · 97 following
Software & AI Automation Engineer, Tech Writer & Educator. Vision:
Enlighten, Educate, Entertain. One story at a time. Work with me:
mail.njengah@gmail.com
Responses (2)
Rae Steele
What are your thoughts?
Tauroluiseduardo
6 hours ago
I will give it a try, I really don't like openclaw because I receive a lot of "Model has reached the API rating limit"
and I think Claude code would be a better option
Reply
Sbayer
6 hours ago (edited)
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 40/44


---
*Page 41*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Great review. I used it all weekend on a Apple app dev that is hosted in google cloud. One problem is that even
with extensive allowlist bash commands the bot still hangs for every extended command. I tried multiple
claude.login.json changes to fix… more
Reply
More from Joe Njenga
InAI Software Engineer by Joe Njenga Joe Njenga
Why Claude Weekly Limits Are I Finally Tested Claude Code /voice
Making Everyone Angry (And… — It’s Faster than Typing (Don’t…
Yesterday, I finally hit my weekly Claude limit, Anthropic has now rolled out Claude Code
and I wasn't surprised, since I see dozens of… /voice to all users, and I have just tested it for …
Oct 19, 2025 705 62 Mar 13 214 4
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 41/44


---
*Page 42*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Joe Njenga InAI Software Engineer by Joe Njenga
Everything Claude Code: The Repo Anthropic Just Solved AI Agent
That Won Anthropic Hackathon… Bloat — 150K Tokens Down to 2K…
If you slept through this or missed out, Anthropic just released smartest way to build
Everything Claude Code hit 900,000 views o… scalable AI agents, cutting token use by 98%,…
Jan 22 526 4 Nov 6, 2025 947 55
See all from Joe Njenga
Recommended from Medium
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 42/44


---
*Page 43*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Gábor Mészáros InData Science Collectiveby Gao Dalie (高達烈)
CLAUDE.md Best Practices: 7 How to build Claude Skills 2.0
formatting rules for the Machine Better than 99% of People
Originally published at https://dev.to on March “It’s a pain to give the same instructions to the
3, 2026. AI every time…” “The AI never remembers th…
Mar 3 85 2 Mar 14 238 2
InStackademic by Usman Writes Sivabalan Balasubramanian
Your AI Is Useless Without These 8 Designing AI Workflows with
MCP Servers — Most Developers… Claude Code: From Prompts to…
Two engineers. The same AI model. One How AI workflows evolve from simple
copy-pastes files all day. The other connects… prompts into structured systems of skills,…
Feb 26 404 10 Mar 9 6
huizhou92 InGenerative AIby Adham Khaled
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 43/44


---
*Page 44*


3/23/26, 4:59 PM How I’m Using (New) Claude Code Telegram (To Run from Anywhere) | by Joe Njenga | Mar, 2026 | Medium
Which Programming Language Perplexity Computer Just Did in 7
Should You Use with Claude Code? Minutes What Took Me Hours
A benchmark across 13 languages reveals Perplexity Computer coordinates 19 AI
surprising patterns — and what it means for… models for real research tasks. Here’s what it…
Mar 11 673 41 Mar 16 1.2K 16
See more recommendations
https://medium.com/@joe.njenga/how-im-using-new-claude-code-telegram-channel-to-code-from-anywhere-0d8206867d1a 44/44