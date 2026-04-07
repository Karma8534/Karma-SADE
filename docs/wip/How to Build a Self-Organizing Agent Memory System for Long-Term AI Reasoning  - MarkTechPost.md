# How to Build a Self-Organizing Agent Memory System for Long-Term AI Reasoning  - MarkTechPost

*Converted from: How to Build a Self-Organizing Agent Memory System for Long-Term AI Reasoning  - MarkTechPost.PDF*



---
*Page 1*


 
Home  Editors Pick  Agentic AI  How to Build a Self-Organizing Agent Memory System for Long-Term AI Reasoning
Editors Pick Agentic AI AI Agents Technology AI Shorts Artificial Intelligence Applications Tech News Tutorials
How to Build a Self-Organizing Agent Memory
System for Long-Term AI Reasoning
By Asif Razzaq- February 14, 2026


---
*Page 2*


In this tutorial, we build a self-organizing memory system for an agent that goes beyond storing raw
conversation history and instead structures interactions into persistent, meaningful knowledge units. We
design the system so that reasoning and memory management are clearly separated, allowing a dedicated
component to extract, compress, and organize information. At the same time, the main agent focuses on
responding to the user. We use structured storage with SQLite, scene-based grouping, and summary
consolidation, and we show how an agent can maintain useful context over long horizons without relying
on opaque vector-only retrieval.
COPY CODE
iimmppoorrtt ssqqlliittee33
iimmppoorrtt jjssoonn
iimmppoorrtt rree
ffrroomm ddaatteettiimmee iimmppoorrtt ddaatteettiimmee


---
*Page 3*


ffrroomm ttyyppiinngg iimmppoorrtt LLiisstt,, DDiicctt
ffrroomm ggeettppaassss iimmppoorrtt ggeettppaassss
ffrroomm ooppeennaaii iimmppoorrtt OOppeennAAII
OOPPEENNAAII__AAPPII__KKEEYY == ggeettppaassss((""EEnntteerr yyoouurr OOppeennAAII AAPPII kkeeyy:: ""))..ssttrriipp(())
cclliieenntt == OOppeennAAII((aappii__kkeeyy==OOPPEENNAAII__AAPPII__KKEEYY))
ddeeff llllmm((pprroommpptt,, tteemmppeerraattuurree==00..11,, mmaaxx__ttookkeennss==550000))::
rreettuurrnn cclliieenntt..cchhaatt..ccoommpplleettiioonnss..ccrreeaattee((
mmooddeell==""ggpptt--44oo--mmiinnii"",,
mmeessssaaggeess==[[{{""rroollee"":: ""uusseerr"",, ""ccoonntteenntt"":: pprroommpptt}}]],,
tteemmppeerraattuurree==tteemmppeerraattuurree,,
mmaaxx__ttookkeennss==mmaaxx__ttookkeennss
))..cchhooiicceess[[00]]..mmeessssaaggee..ccoonntteenntt..ssttrriipp(())
We set up the core runtime by importing all required libraries and securely collecting the API key at
execution time. We initialize the language model client and define a single helper function that
standardizes all model calls. We ensure that every downstream component relies on this shared interface
for consistent generation behavior.
COPY CODE
ccllaassss MMeemmoorryyDDBB::
ddeeff ____iinniitt____((sseellff))::
sseellff..ddbb == ssqqlliittee33..ccoonnnneecctt((""::mmeemmoorryy::""))
sseellff..ddbb..rrooww__ffaaccttoorryy == ssqqlliittee33..RRooww
sseellff..__iinniitt__sscchheemmaa(())
ddeeff __iinniitt__sscchheemmaa((sseellff))::
sseellff..ddbb..eexxeeccuuttee((""""""
CCRREEAATTEE TTAABBLLEE mmeemm__cceellllss ((
iidd IINNTTEEGGEERR PPRRIIMMAARRYY KKEEYY,,


---
*Page 4*


sscceennee TTEEXXTT,,
cceellll__ttyyppee TTEEXXTT,,
ssaalliieennccee RREEAALL,,
ccoonntteenntt TTEEXXTT,,
ccrreeaatteedd__aatt TTEEXXTT
))
""""""))
sseellff..ddbb..eexxeeccuuttee((""""""
CCRREEAATTEE TTAABBLLEE mmeemm__sscceenneess ((
sscceennee TTEEXXTT PPRRIIMMAARRYY KKEEYY,,
ssuummmmaarryy TTEEXXTT,,
uuppddaatteedd__aatt TTEEXXTT
))
""""""))
sseellff..ddbb..eexxeeccuuttee((""""""
CCRREEAATTEE VVIIRRTTUUAALL TTAABBLLEE mmeemm__cceellllss__ffttss
UUSSIINNGG ffttss55((ccoonntteenntt,, sscceennee,, cceellll__ttyyppee))
""""""))
ddeeff iinnsseerrtt__cceellll((sseellff,, cceellll))::
sseellff..ddbb..eexxeeccuuttee((
""IINNSSEERRTT IINNTTOO mmeemm__cceellllss VVAALLUUEESS((NNUULLLL,,??,,??,,??,,??,,??))"",,
((
cceellll[[""sscceennee""]],,
cceellll[[""cceellll__ttyyppee""]],,
cceellll[[""ssaalliieennccee""]],,
jjssoonn..dduummppss((cceellll[[""ccoonntteenntt""]])),,
ddaatteettiimmee..uuttccnnooww(())..iissooffoorrmmaatt(())
))
))
sseellff..ddbb..eexxeeccuuttee((
""IINNSSEERRTT IINNTTOO mmeemm__cceellllss__ffttss VVAALLUUEESS((??,,??,,??))"",,
((
jjssoonn..dduummppss((cceellll[[""ccoonntteenntt""]])),,
cceellll[[""sscceennee""]],,
cceellll[[""cceellll__ttyyppee""]]
))


---
*Page 5*


))
sseellff..ddbb..ccoommmmiitt(())


---
*Page 6*


We define a structured memory database that persists information across interactions. We create tables
for atomic memory units, higher-level scenes, and a full-text search index to enable symbolic retrieval. We


---
*Page 7*


also implement the logic to insert new memory entries in a normalized and queryable form.
COPY CODE
ddeeff ggeett__sscceennee((sseellff,, sscceennee))::
rreettuurrnn sseellff..ddbb..eexxeeccuuttee((
""SSEELLEECCTT ** FFRROOMM mmeemm__sscceenneess WWHHEERREE sscceennee==??"",, ((sscceennee,,))
))..ffeettcchhoonnee(())
ddeeff uuppsseerrtt__sscceennee((sseellff,, sscceennee,, ssuummmmaarryy))::
sseellff..ddbb..eexxeeccuuttee((""""""
IINNSSEERRTT IINNTTOO mmeemm__sscceenneess VVAALLUUEESS((??,,??,,??))
OONN CCOONNFFLLIICCTT((sscceennee)) DDOO UUPPDDAATTEE SSEETT
ssuummmmaarryy==eexxcclluuddeedd..ssuummmmaarryy,,
uuppddaatteedd__aatt==eexxcclluuddeedd..uuppddaatteedd__aatt
"""""",, ((sscceennee,, ssuummmmaarryy,, ddaatteettiimmee..uuttccnnooww(())..iissooffoorrmmaatt(())))))
sseellff..ddbb..ccoommmmiitt(())
ddeeff rreettrriieevvee__sscceennee__ccoonntteexxtt((sseellff,, qquueerryy,, lliimmiitt==66))::
ttookkeennss == rree..ffiinnddaallll((rr""[[aa--zzAA--ZZ00--99]]++"",, qquueerryy))
iiff nnoott ttookkeennss::
rreettuurrnn [[]]
ffttss__qquueerryy == "" OORR ""..jjooiinn((ttookkeennss))
rroowwss == sseellff..ddbb..eexxeeccuuttee((""""""
SSEELLEECCTT sscceennee,, ccoonntteenntt FFRROOMM mmeemm__cceellllss__ffttss
WWHHEERREE mmeemm__cceellllss__ffttss MMAATTCCHH ??
LLIIMMIITT ??
"""""",, ((ffttss__qquueerryy,, lliimmiitt))))..ffeettcchhaallll(())
iiff nnoott rroowwss::
rroowwss == sseellff..ddbb..eexxeeccuuttee((""""""
SSEELLEECCTT sscceennee,, ccoonntteenntt FFRROOMM mmeemm__cceellllss
OORRDDEERR BBYY ssaalliieennccee DDEESSCC


---
*Page 8*


LLIIMMIITT ??
"""""",, ((lliimmiitt,,))))..ffeettcchhaallll(())
rreettuurrnn rroowwss
ddeeff rreettrriieevvee__sscceennee__ssuummmmaarryy((sseellff,, sscceennee))::
rrooww == sseellff..ggeett__sscceennee((sscceennee))
rreettuurrnn rrooww[[""ssuummmmaarryy""]] iiff rrooww eellssee """"
We focus on memory retrieval and scene maintenance logic. We implement safe full-text search by
sanitizing user queries and adding a fallback strategy when no lexical matches are found. We also expose
helper methods to fetch consolidated scene summaries for long-horizon context building.
COPY CODE
ccllaassss MMeemmoorryyMMaannaaggeerr::
ddeeff ____iinniitt____((sseellff,, ddbb:: MMeemmoorryyDDBB))::
sseellff..ddbb == ddbb
ddeeff eexxttrraacctt__cceellllss((sseellff,, uusseerr,, aassssiissttaanntt)) -->> LLiisstt[[DDiicctt]]::
pprroommpptt == ff""""""
CCoonnvveerrtt tthhiiss iinntteerraaccttiioonn iinnttoo ssttrruuccttuurreedd mmeemmoorryy cceellllss..
RReettuurrnn JJSSOONN aarrrraayy wwiitthh oobbjjeeccttss ccoonnttaaiinniinngg::
-- sscceennee
-- cceellll__ttyyppee ((ffaacctt,, ppllaann,, pprreeffeerreennccee,, ddeecciissiioonn,, ttaasskk,, rriisskk))
-- ssaalliieennccee ((00--11))
-- ccoonntteenntt ((ccoommpprreesssseedd,, ffaaccttuuaall))
UUsseerr:: {{uusseerr}}
AAssssiissttaanntt:: {{aassssiissttaanntt}}


---
*Page 9*


""""""
rraaww == llllmm((pprroommpptt))
rraaww == rree..ssuubb((rr""``````jjssoonn||``````"",, """",, rraaww))
ttrryy::
cceellllss == jjssoonn..llooaaddss((rraaww))
rreettuurrnn cceellllss iiff iissiinnssttaannccee((cceellllss,, lliisstt)) eellssee [[]]
eexxcceepptt EExxcceeppttiioonn::
rreettuurrnn [[]]
ddeeff ccoonnssoolliiddaattee__sscceennee((sseellff,, sscceennee))::
rroowwss == sseellff..ddbb..ddbb..eexxeeccuuttee((
""SSEELLEECCTT ccoonntteenntt FFRROOMM mmeemm__cceellllss WWHHEERREE sscceennee==?? OORRDDEERR BBYY ss
((sscceennee,,))
))..ffeettcchhaallll(())
iiff nnoott rroowwss::
rreettuurrnn
cceellllss == [[jjssoonn..llooaaddss((rr[[""ccoonntteenntt""]])) ffoorr rr iinn rroowwss]]
pprroommpptt == ff""""""
SSuummmmaarriizzee tthhiiss mmeemmoorryy sscceennee iinn uunnddeerr 110000 wwoorrddss..
KKeeeepp iitt ssttaabbllee aanndd rreeuussaabbllee ffoorr ffuuttuurree rreeaassoonniinngg..
CCeellllss::
{{cceellllss}}
""""""
ssuummmmaarryy == llllmm((pprroommpptt,, tteemmppeerraattuurree==00..0055))
sseellff..ddbb..uuppsseerrtt__sscceennee((sscceennee,, ssuummmmaarryy))
ddeeff uuppddaattee((sseellff,, uusseerr,, aassssiissttaanntt))::
cceellllss == sseellff..eexxttrraacctt__cceellllss((uusseerr,, aassssiissttaanntt))
ffoorr cceellll iinn cceellllss::


---
*Page 10*


sseellff..ddbb..iinnsseerrtt__cceellll((cceellll))
ffoorr sscceennee iinn sseett((cc[[""sscceennee""]] ffoorr cc iinn cceellllss))::
sseellff..ccoonnssoolliiddaattee__sscceennee((sscceennee))
We implement the dedicated memory management component responsible for structuring experience. We
extract compact memory representations from interactions, store them, and periodically consolidate them
into stable scene summaries. We ensure that memory evolves incrementally without interfering with the
agent’s response flow.
COPY CODE
ccllaassss WWoorrkkeerrAAggeenntt::
ddeeff ____iinniitt____((sseellff,, ddbb:: MMeemmoorryyDDBB,, mmeemm__mmaannaaggeerr:: MMeemmoorryyMMaannaaggeerr))::
sseellff..ddbb == ddbb
sseellff..mmeemm__mmaannaaggeerr == mmeemm__mmaannaaggeerr
ddeeff aannsswweerr((sseellff,, uusseerr__iinnppuutt))::
rreeccaalllleedd == sseellff..ddbb..rreettrriieevvee__sscceennee__ccoonntteexxtt((uusseerr__iinnppuutt))
sscceenneess == sseett((rr[[""sscceennee""]] ffoorr rr iinn rreeccaalllleedd))
ssuummmmaarriieess == ""\\nn""..jjooiinn((
ff""[[{{sscceennee}}]]\\nn{{sseellff..ddbb..rreettrriieevvee__sscceennee__ssuummmmaarryy((sscceennee))}}""
ffoorr sscceennee iinn sscceenneess
))
pprroommpptt == ff""""""
YYoouu aarree aann iinntteelllliiggeenntt aaggeenntt wwiitthh lloonngg--tteerrmm mmeemmoorryy..
RReelleevvaanntt mmeemmoorryy::


---
*Page 11*


{{ssuummmmaarriieess}}
UUsseerr:: {{uusseerr__iinnppuutt}}
""""""
aassssiissttaanntt__rreeppllyy == llllmm((pprroommpptt))
sseellff..mmeemm__mmaannaaggeerr..uuppddaattee((uusseerr__iinnppuutt,, aassssiissttaanntt__rreeppllyy))
rreettuurrnn aassssiissttaanntt__rreeppllyy
ddbb == MMeemmoorryyDDBB(())
mmeemmoorryy__mmaannaaggeerr == MMeemmoorryyMMaannaaggeerr((ddbb))
aaggeenntt == WWoorrkkeerrAAggeenntt((ddbb,, mmeemmoorryy__mmaannaaggeerr))
pprriinntt((aaggeenntt..aannsswweerr((""WWee aarree bbuuiillddiinngg aann aaggeenntt tthhaatt rreemmeemmbbeerrss pprroojjeecc
pprriinntt((aaggeenntt..aannsswweerr((""IItt sshhoouulldd oorrggaanniizzee ccoonnvveerrssaattiioonnss iinnttoo ttooppiiccss aa
pprriinntt((aaggeenntt..aannsswweerr((""TThhiiss mmeemmoorryy ssyysstteemm sshhoouulldd ssuuppppoorrtt ffuuttuurree rreeaassoo
ffoorr rrooww iinn ddbb..ddbb..eexxeeccuuttee((""SSEELLEECCTT ** FFRROOMM mmeemm__sscceenneess""))::
pprriinntt((ddiicctt((rrooww))))
We define the worker agent that performs reasoning while remaining memory-aware. We retrieve relevant
scenes, assemble contextual summaries, and generate responses grounded in long-term knowledge. We
then close the loop by passing the interaction back to the memory manager so the system continuously
improves over time.
In this tutorial, we demonstrated how an agent can actively curate its own memory and turn past
interactions into stable, reusable knowledge rather than ephemeral chat logs. We enabled memory to
evolve through consolidation and selective recall, which supports more consistent and grounded reasoning
across sessions. This approach provides a practical foundation for building long-lived agentic systems,
and it can be naturally extended with mechanisms for forgetting, richer relational memory, or graph-based
orchestration as the system grows in complexity.


---
*Page 12*


Check out the Full Codes. Also, feel free to follow us on Twitter and don’t forget to join our 100k+ ML
SubReddit and Subscribe to our Newsletter. Wait! are you on telegram? now you can join us on telegram
as well.
🧵🧵 Recommended Open Source AI: Meet CopilotKit- Framework for building agent-native applications
with Generative UI.
Previous article Next article
Exa AI Introduces Exa Instant: A Sub-200ms Neural Google AI Introduces the WebMCP to Enable Direct
Search Engine Designed to Eliminate Bottlenecks for and Structured Website Interactions for New AI Agents
Real-Time Agentic Workflows
RELATED ARTICLES
Meet ‘Kani-TTS-2’: A 400M Param Open Source Text-to-Speech Model that
Runs...
Michal Sutter-February 15, 2026
Getting Started with OpenClaw and Connecting It with WhatsApp
Arham Islam-February 14, 2026
Google AI Introduces the WebMCP to Enable Direct and Structured
Website...
Michal Sutter-February 14, 2026
Exa AI Introduces Exa Instant: A Sub-200ms Neural Search Engine
Designed...
Asif Razzaq-February 13, 2026
[In-Depth Guide] The Complete CTGAN + SDV Pipeline for High-Fidelity
Synthetic...
Michal Sutter-February 13, 2026
Kyutai Releases Hibiki-Zero: A3B Parameter Simultaneous Speech-to-
Speech Translation Model Using GRPO...


---
*Page 13*


Asif Razzaq-February 13, 2026
ABOUT US
Marktechpost is a California-based AI News Platform providing easy-to-consume, byte size updates in
machine learning, deep learning, and data science research.
Contact us: Asif@marktechpost.com


---
*Page 14*


FOLLOW US
   
© Copyright reserved @2025 Marktechpost AI Media Inc | Please note that we do make a small profit through our
affiliates/referrals via product promotion in the articles
Privacy & Cookies Policy
Exit mobile version