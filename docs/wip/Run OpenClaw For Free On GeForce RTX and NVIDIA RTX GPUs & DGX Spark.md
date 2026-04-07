# Run OpenClaw For Free On GeForce RTX and NVIDIA RTX GPUs & DGX Spark

*Converted from: Run OpenClaw For Free On GeForce RTX and NVIDIA RTX GPUs & DGX Spark.PDF*



---
*Page 1*


Visit your regional NVIDIA website for local content, pricing and where to buy partners specific to your location. 
United States  Continue
Main Menu  Sign In
EU
 Sign In
EU
GeForce
Shop Drivers Support
In This Article
Run OpenClaw For Free On GeForce
RTX and NVIDIA RTX GPUs & DGX
Spark
By Abhishek Gore on February 13, 2026 | Guides, RTX AI PCs, Featured
Stories
OpenClaw (formerly Clawdbot and Moltbot) is a "local-first" AI Agent that
lives on your computer. It’s going viral for how it combines different
capabilities to be a useful assistant, remembering your conversations and
adjusting itself accordingly, running continuously on your local machine,
using context from your files and apps, and leveraging new ‘skills’ to
expand its capabilities.
Here are some popular use cases:
1. Personal Secretary: With access to your inbox, calendar and files,
OpenClaw can help you manage your schedule autonomously. It drafts
replies to emails using context from your files and previous mails,
sends reminders you have asked for, before time, arranges meetings
finding open slots on your calendar.
2. Proactive Project Management: OpenClaw can check up regularly on
the status of a project over the email or messaging channels you use,
send you status checks, and follow up / send reminders as needed
3. Research Agent: With personalized context from your apps, OpenClaw
can create reports combining search from the internet and your files
OpenClaw is powered by Large Language Models (LLMs) that can be run
locally or on cloud. Cloud LLMs can incur significant costs due to the


---
*Page 2*


always-on nature of OpenClaw. And they require you to upload your
Visit your regional NVIDIA website for local content, pricing and where to buy partners specific to your location.
personal data.
 Continue
In this guide, we’ll show you how you can run OpenClaw and the LLMs
completely locally on NVIDIA RTX GPUs and DGX S  parkS itgon sInave money and
EU
ensure your data stays private.
 Sign In
EU
NVIDIA RTX GPUs provide the best performance for this kind of workflow
GeForce
Shop Drivers Support
thanks to the Tensor Cores in the GPU, which accelerate AI operations,
and the CUDA accelerations for all the tools required to run OpenClaw -
In This Article
including Ollama and Llama.cpp. DGX Spark is a particularly good option
as it’s built to be always on, and has 128GB of memory, allowing you to run
larger local models which will provide the best accuracy and results.
Important Notice Before You Begin


---
*Page 3*


Visit your regioYnoaul N sVhIDoIuA lwde bbesi taew foarr leo coafl ctohnete rnits, kpsri coinfg A aIn Ad gwehnertes to b auyn pda ertxneerrsc isspee ccifiacu ttoio ynou tro location.
minimize them. Check out OpenClaw’s website for more information.
 Continue
These are the 2 main risks in this kind of agent:
 Sign In
EU
1. Your personal information or files may be leaked or stolen.
 Sign In
2. The agent on its own, or the tools you connect to the bot, may exposEeU
you to malicious code or cyber attacks.
GeForce
Shop Drivers Support
There’s no way to completely protect against all risk, so proceed at your
own risk. These are some of the measures we took when testing
In This Article
OpenClaw:
> Run OpenClaw on a separate, clean PC with no personal data, or a
virtual machine. Then copy the data you want the agent to have access
to.
> Don’t give it access to your accounts. Instead, create dedicated
accounts for the agent and share specific information or access with
it.
> Be careful with what skills you enable, ideally limiting testing to those
that have been vetted by the community.
> Ensure any channels you use to access your OpenClaw assistant, like
the web UI or messaging channels, are not accessible without
authorization over local networks or the internet.
> If possible for your use case, limit internet access.
Getting Started Guide
To install OpenClaw on Windows, we’ll use Windows Subsystem for Linux
(or WSL for short). Native installation in Powershell is possible, but it’s
discouraged by the developer as it’s unstable.
If you’re using a DGX Spark, you can skip to section 2.
1. Windows Subsystem for Linux installation:


---
*Page 4*


Visit your regioInf ayl oNuV IhDaIAv we eWbsSiteL fionrs lotacallle cdon, tyeonut, cpraicnin sgk aipnd t woh tehree t no ebxuyt pOaprtennerCs lsapwec Iinfics ttoa lylaoutiro loncation.
section. To install WSL (Link for reference):
 Continue
1.1. Press the Windows Key, type PowerShell, right-click the result,
 Sign In
EU
and select Run as Administrator.
 Sign In
EU
1.2. Paste the following command and press Enter:
GeForce
Shop Drivers Support
In This Artiwcslel --install
1.3. Run the following command to check whether WSL is installed
correctly. You should see output similar to the following screenshot:
wsl --version


---
*Page 5*


Visit your regional NVIDIA website for local content, pricing and where to buy partners specific to your location.
 Continue
 Sign In
EU
 Sign In
EU
GeForce
Shop Drivers Support
In This Article
1.4. Open WSL by searching Powershell from the Windows Search
Bar, selecting “run as admin”, and typing in:
wsl
2. OpenClaw Installation:
2.1. Run the following command in your WSL window:
curl -fsSL https://openclaw.ai/install.sh | bash
This will install OpenClaw and all required dependencies onto your


---
*Page 6*


machine. After some necessary packages have been downloaded,
Visit your regional NVIDIA website for local content, pricing and where to buy partners specific to your location.
OpenClaw will prompt you with a security warning:
 Continue
 Sign In
EU
 Sign In
EU
GeForce
Shop Drivers Support
In This Article
2.2. Please read the security risks. If you are ok to continue, navigate
with the arrow keys to ‘Yes’ and press enter.
2.3. You’ll be prompted to choose the Quickstart or Manual
onboarding mode. Choose Quickstart.


---
*Page 7*


Visit your regional NVIDIA website for local content, pricing and where to buy partners specific to your location.
 Continue
 Sign In
EU
 Sign In
EU
GeForce
Shop Drivers Support
In This Article
2.4. A list will appear for configuring the model provider. If you want
to run a local model, Navigate to the very bottom of the list and
select “Skip for now” as we’ll configure it later. If you want to
connect a cloud model you can select one and follow the
instructions.


---
*Page 8*


Visit your regional NVIDIA website for local content, pricing and where to buy partners specific to your location.
 Continue
 Sign In
EU
 Sign In
EU
GeForce
Shop Drivers Support
In This Article
2.5. Another list prompt will appear for Filtering models by provider.
Select “‘All Providers”’,. On the following prompt for picking your
default model, choose “‘Keep Current”’.


---
*Page 9*


Visit your regional NVIDIA website for local content, pricing and where to buy partners specific to your location.
 Continue
 Sign In
EU
 Sign In
EU
GeForce
Shop Drivers Support
In This Article


---
*Page 10*


Visit your regional NVIDIA website for local content, pricing and where to buy partners specific to your location.
 Continue
 Sign In
EU
 Sign In
EU
GeForce
Shop Drivers Support
In This Article
2.6. You will be offered to connect a communication channel to
interact with your bot while you are away from the PC. You can
select one here, or select “Skip for Now” and set it up later.


---
*Page 11*


Visit your regional NVIDIA website for local content, pricing and where to buy partners specific to your location.
 Continue
 Sign In
EU
 Sign In
EU
GeForce
Shop Drivers Support
In This Article
2.7. Next you’ll be prompted with the skills configuration - these are
the abilities that the bot will have. We recommend selecting “No” for
now to proceed with the setup. You can always add skills later once
you experiment with it and identify the skills you need for your use-
case.


---
*Page 12*


Visit your regional NVIDIA website for local content, pricing and where to buy partners specific to your location.
 Continue
 Sign In
EU
 Sign In
EU
GeForce
Shop Drivers Support
In This Article
2.8. Next, OpenClaw will prompt you to install the homebrew
package - select “No”, this is needd for Mac setups but not for
Windows.


---
*Page 13*


Visit your regional NVIDIA website for local content, pricing and where to buy partners specific to your location.
 Continue
 Sign In
EU
 Sign In
EU
GeForce
Shop Drivers Support
In This Article
2.9. The next prompt will be to install Hooks. We recommend
selecting all 3 for a better experience. But consider if you are
comfortable with having your data logged locally.


---
*Page 14*


Visit your regional NVIDIA website for local content, pricing and where to buy partners specific to your location.
 Continue
 Sign In
EU
 Sign In
EU
GeForce
Shop Drivers Support
In This Article
2.10. The resulting terminal output will present a URL for accessing
your OpenClaw dashboard. Save this address as you’ll need it to load
the UI.


---
*Page 15*


Visit your regional NVIDIA website for local content, pricing and where to buy partners specific to your location.
 Continue
 Sign In
EU
 Sign In
EU
GeForce
Shop Drivers Support
In This Article
2.11. Finally, select “Yes” on the last prompt to complete the
OpenClaw installation.


---
*Page 16*


Visit your regional NVIDIA website for local content, pricing and where to buy partners specific to your location.
 Continue
 Sign In
EU
 Sign In
EU
GeForce
Shop Drivers Support
In This Article
2.12. You can now access OpenClaw via the dashboard link provided
with the access token.
3. Local Model configuration:
You can power OpenClaw with an LLM running locally on your RTX GPU, or
with a cloud LLM. In this section we’ll show you how to configure
OpenClaw to run locally with LM Studio or Ollama.
The quality of answers depends on the size and quality of the LLM. You’ll
want to make sure that you free up as much VRAM and as possible (e.g.
don’t run other workloads on the GPU, only load the skills you need to
minimize context, etc.) so we can use a large LLM that has access to the
majority of your GPU.
3.1. Select the backend of your choice:


---
*Page 17*


Visit your regional NVIDIA we3b.s1i.t1e. LfoMr l oSctaul cdoinot eisn tt, hpreic rinegc oanmd mwheenred teod b buya pcakretnnedrs f sopre rcaifiwc to your location.
performance, as they use Llama.cpp to run the LLM.
 Continue
3.1.2. Ollama offers additional developer tools to facilitate
 Sign In
EU
deployment.
 Sign In
EU
3.2 If you are in Windows, open another WSL window by searching
GeForce Powershell from the Windows Search Bar, selecting “run as admin”,
Shop Drivers Support
and typing in. (skip this step on DGX Spark)
In This Article
wsl
3.3. Download and install LM Studio or Ollama:
3.3. Download and install LM Studio or Ollama:
LM Studio Ollama
curl -fsSL curl -fsSL
https://lmstudio.ai/install.sh https://ollama.com/instal
| bash | sh
3.4. elect the LLM of your choice: We recommend the following
models depending on your GPU:
> 8-12GB GPUs: qwen3-4B-Thinking-2507
> 16GB GPUs: gpt-oss-20b
> 24-48GB GPUs: Nemotron-3-Nano-30B-A3B
> 96-128GB GPUs: gpt-oss-120b
3.5. Download the model:
LM Studio Ollama
lms get openai/gpt-oss- ollama pull gpt-oss:20b


---
*Page 18*


20b
Visit your regional NVIDIA website for local content, pricing and where to buy partners specific to your location.
 Continue
3.6. Run the model, and set the context window to 32K tokens or
 Sign In
EU
more so it can run well with OpenClaw.
 Sign In
EU
GeForce LM Studio Ollama
Shop Drivers Support
In This Articllems load openai/gpt-oss- ollama run gpt-oss:20b
20b --context-length /set parameter num_ctx
32768 32768
3.7. Configure OpenClaw to use LM Studio or Ollama, and start
gateway:
LM Studio Ollama
Navigate to the OpenClaw config file by
ollama launch
running: openclaw #If the
gateway is already
running, it will
.explorer
auto-reload the
configuration #You
Then open the folder titled ‘.openclaw’
can add "--config"
and open the file ‘openclaw.json’. Edit
to configure
and paste the following snippet
without launching
the openclaw
"models": { gateway yet
"mode": "merge",
"providers": {
"lmstudio": {
"baseUrl":
"http://localhost:1234/v1",
"apiKey": "lmstudio",
"api": "openai-
responses",
"models": [


---
*Page 19*


{
Visit your regional NVIDIA website for local content, pricing and where to buy partners specific to your location.
"id":
"openai/gpt-oss-20bC"o,ntinue
"name":
"openai/gpt-oss-20b",  Sign In
EU
"reasoning":
false,
 Sign In
EU
"input": [
"text"
GeForce
Shop Drivers Support
],
"cost": {
In This Articl e "input": 0,
"output": 0,
"cacheRead": 0,
"cacheWrite": 0
},
"contextWindow":
32768,
"maxTokens": 4096
}
]
}
}
},
Conclusion
And you are good to go! To check if everything is set up correctly, open a
browser window and paste the OpenClaw URL with the access token. Click
on new, and try typing in something. If you get a response back, you’re all
set up! You can also ask OpenClaw what model it’s using and can even
switch between models by typing /model MODEL_NAME in the gateway
chat UI.
To learn more about how to use OpenClaw, visit the OpenClaw website.
One thing you may want to look into is adding new skills. Remember that
these introduce additional risk, so be careful with which ones you add. To
add a new skill:
> Ask OpenClaw to configure itself with a skill