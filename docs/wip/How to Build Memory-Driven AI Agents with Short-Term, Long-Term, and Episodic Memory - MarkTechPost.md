# How to Build Memory-Driven AI Agents with Short-Term, Long-Term, and Episodic Memory - MarkTechPost

*Converted from: How to Build Memory-Driven AI Agents with Short-Term, Long-Term, and Episodic Memory - MarkTechPost.PDF*



---
*Page 1*


 
Home  Editors Pick  Agentic AI  How to Build Memory-Driven AI Agents with Short-Term, Long-Term, and Episodic Memory
Editors Pick Agentic AI AI Agents Staff Tutorials
How to Build Memory-Driven AI Agents with Short-
Term, Long-Term, and Episodic Memory
By Asif Razzaq- February 1, 2026


---
*Page 2*


In this tutorial, we build a memory-engineering layer for an AI agent that separates short-term working
context from long-term vector memory and episodic traces. We implement semantic storage using
embeddings and FAISS for fast similarity search, and we add episodic memory that captures what worked,
what failed, and why, so the agent can reuse successful patterns rather than reinvent them. We also define
practical policies for what gets stored (salience + novelty + pinned constraints), how retrieval is ranked
(hybrid semantic + episodic with usage decay), and how short-term messages are consolidated into
durable memories. Check out the Full Codes here.
COPY CODE
iimmppoorrtt ooss,, rree,, jjssoonn,, ttiimmee,, mmaatthh,, uuuuiidd
ffrroomm ddaattaaccllaasssseess iimmppoorrtt ddaattaaccllaassss,, aassddiicctt
ffrroomm ttyyppiinngg iimmppoorrtt LLiisstt,, DDiicctt,, AAnnyy,, OOppttiioonnaall,, TTuuppllee
ffrroomm ddaatteettiimmee iimmppoorrtt ddaatteettiimmee


---
*Page 3*


iimmppoorrtt ssyyss,, ssuubbpprroocceessss
ddeeff ppiipp__iinnssttaallll((ppkkggss:: LLiisstt[[ssttrr]]))::
ssuubbpprroocceessss..cchheecckk__ccaallll(([[ssyyss..eexxeeccuuttaabbllee,, ""--mm"",, ""ppiipp"",, ""iinnssttaallll"",,
ppiipp__iinnssttaallll(([[
""sseenntteennccee--ttrraannssffoorrmmeerrss>>==22..66..00"",,
""ffaaiissss--ccppuu>>==11..88..00"",,
""nnuummppyy"",,
""ppaannddaass"",,
""sscciikkiitt--lleeaarrnn""
]]))
iimmppoorrtt nnuummppyy aass nnpp
iimmppoorrtt ppaannddaass aass ppdd
iimmppoorrtt ffaaiissss
ffrroomm sseenntteennccee__ttrraannssffoorrmmeerrss iimmppoorrtt SSeenntteenncceeTTrraannssffoorrmmeerr
ffrroomm sskklleeaarrnn..pprreepprroocceessssiinngg iimmppoorrtt mmiinnmmaaxx__ssccaallee
UUSSEE__OOPPEENNAAII == FFaallssee
OOPPEENNAAII__MMOODDEELL == ooss..eennvviirroonn..ggeett((""OOPPEENNAAII__MMOODDEELL"",, ""ggpptt--44oo--mmiinnii""))
ttrryy::
ffrroomm ggeettppaassss iimmppoorrtt ggeettppaassss
iiff nnoott ooss..ggeetteennvv((""OOPPEENNAAII__AAPPII__KKEEYY""))::
kk == ggeettppaassss((""OOppttiioonnaall:: EEnntteerr OOPPEENNAAII__AAPPII__KKEEYY ffoorr bbeetttteerr LLLLMM
iiff kk::
ooss..eennvviirroonn[[""OOPPEENNAAII__AAPPII__KKEEYY""]] == kk
iiff ooss..ggeetteennvv((""OOPPEENNAAII__AAPPII__KKEEYY""))::
ppiipp__iinnssttaallll(([[""ooppeennaaii>>==11..4400..00""]]))
ffrroomm ooppeennaaii iimmppoorrtt OOppeennAAII
cclliieenntt == OOppeennAAII(())
UUSSEE__OOPPEENNAAII == TTrruuee


---
*Page 4*


eexxcceepptt EExxcceeppttiioonn::
UUSSEE__OOPPEENNAAII == FFaallssee
We set up the execution environment and ensure all required libraries are available. We handle optional
OpenAI integration while keeping the notebook fully runnable without any API keys. We establish the base
imports and configuration that the rest of the memory system builds upon. Check out the Full Codes here.
COPY CODE
@@ddaattaaccllaassss
ccllaassss SShhoorrttTTeerrmmIItteemm::
ttss:: ssttrr
rroollee:: ssttrr
ccoonntteenntt:: ssttrr
mmeettaa:: DDiicctt[[ssttrr,, AAnnyy]]
@@ddaattaaccllaassss
ccllaassss LLoonnggTTeerrmmIItteemm::
mmeemm__iidd:: ssttrr
ttss:: ssttrr
kkiinndd:: ssttrr
tteexxtt:: ssttrr
ttaaggss:: LLiisstt[[ssttrr]]
ssaalliieennccee:: ffllooaatt
uussaaggee:: iinntt
mmeettaa:: DDiicctt[[ssttrr,, AAnnyy]]
@@ddaattaaccllaassss
ccllaassss EEppiissooddee::
eepp__iidd:: ssttrr
ttss:: ssttrr
ttaasskk:: ssttrr
ccoonnssttrraaiinnttss:: DDiicctt[[ssttrr,, AAnnyy]]
ppllaann:: LLiisstt[[ssttrr]]


---
*Page 5*


aaccttiioonnss:: LLiisstt[[DDiicctt[[ssttrr,, AAnnyy]]]]
rreessuulltt:: ssttrr
oouuttccoommee__ssccoorree:: ffllooaatt
lleessssoonnss:: LLiisstt[[ssttrr]]
ffaaiilluurree__mmooddeess:: LLiisstt[[ssttrr]]
ttaaggss:: LLiisstt[[ssttrr]]
mmeettaa:: DDiicctt[[ssttrr,, AAnnyy]]
ccllaassss VVeeccttoorrIInnddeexx::
ddeeff ____iinniitt____((sseellff,, ddiimm:: iinntt))::
sseellff..ddiimm == ddiimm
sseellff..iinnddeexx == ffaaiissss..IInnddeexxFFllaattIIPP((ddiimm))
sseellff..iidd__mmaapp:: LLiisstt[[ssttrr]] == [[]]
sseellff..__vveeccttoorrss == NNoonnee
ddeeff aadddd((sseellff,, iiddss:: LLiisstt[[ssttrr]],, vveeccttoorrss:: nnpp..nnddaarrrraayy))::
aasssseerrtt vveeccttoorrss..nnddiimm ==== 22 aanndd vveeccttoorrss..sshhaappee[[11]] ==== sseellff..ddiimm
sseellff..iinnddeexx..aadddd((vveeccttoorrss..aassttyyppee((nnpp..ffllooaatt3322))))
sseellff..iidd__mmaapp..eexxtteenndd((iiddss))
iiff sseellff..__vveeccttoorrss iiss NNoonnee::
sseellff..__vveeccttoorrss == vveeccttoorrss..aassttyyppee((nnpp..ffllooaatt3322))
eellssee::
sseellff..__vveeccttoorrss == nnpp..vvssttaacckk(([[sseellff..__vveeccttoorrss,, vveeccttoorrss..aassttyypp
ddeeff sseeaarrcchh((sseellff,, qquueerryy__vveecc:: nnpp..nnddaarrrraayy,, kk:: iinntt == 66)) -->> LLiisstt[[TTuupp
iiff sseellff..iinnddeexx..nnttoottaall ==== 00::
rreettuurrnn [[]]
iiff qquueerryy__vveecc..nnddiimm ==== 11::
qquueerryy__vveecc == qquueerryy__vveecc[[NNoonnee,, ::]]
DD,, II == sseellff..iinnddeexx..sseeaarrcchh((qquueerryy__vveecc..aassttyyppee((nnpp..ffllooaatt3322)),, kk))
hhiittss == [[]]
ffoorr iiddxx,, ssccoorree iinn zziipp((II[[00]]..ttoolliisstt(()),, DD[[00]]..ttoolliisstt(())))::
iiff iiddxx ==== --11::
ccoonnttiinnuuee
hhiittss..aappppeenndd((((sseellff..iidd__mmaapp[[iiddxx]],, ffllooaatt((ssccoorree))))))
rreettuurrnn hhiittss


---
*Page 6*


We define clear data structures for short-term, long-term, and episodic memory using typed schemas. We
implement a vector index backed by FAISS to enable fast semantic similarity search over stored memories.
It lays the foundation for efficiently storing, indexing, and retrieving memory. Check out the Full Codes here.
COPY CODE


---
*Page 7*


ccllaassss MMeemmoorryyPPoolliiccyy::
ddeeff ____iinniitt____((sseellff,,
sstt__mmaaxx__iitteemmss:: iinntt == 1188,,
llttmm__mmaaxx__iitteemmss:: iinntt == 22000000,,
mmiinn__ssaalliieennccee__ttoo__ssttoorree:: ffllooaatt == 00..3355,,
nnoovveellttyy__tthhrreesshhoolldd:: ffllooaatt == 00..8822,,
ttooppkk__sseemmaannttiicc:: iinntt == 66,,
ttooppkk__eeppiissooddiicc:: iinntt == 33))::
sseellff..sstt__mmaaxx__iitteemmss == sstt__mmaaxx__iitteemmss
sseellff..llttmm__mmaaxx__iitteemmss == llttmm__mmaaxx__iitteemmss
sseellff..mmiinn__ssaalliieennccee__ttoo__ssttoorree == mmiinn__ssaalliieennccee__ttoo__ssttoorree
sseellff..nnoovveellttyy__tthhrreesshhoolldd == nnoovveellttyy__tthhrreesshhoolldd
sseellff..ttooppkk__sseemmaannttiicc == ttooppkk__sseemmaannttiicc
sseellff..ttooppkk__eeppiissooddiicc == ttooppkk__eeppiissooddiicc
ddeeff ssaalliieennccee__ssccoorree((sseellff,, tteexxtt:: ssttrr,, mmeettaa:: DDiicctt[[ssttrr,, AAnnyy]])) -->> ffll
tt == tteexxtt..ssttrriipp(())
iiff nnoott tt::
rreettuurrnn 00..00
lleennggtthh == mmiinn((lleenn((tt)) // 442200..00,, 11..00))
hhaass__nnuummbbeerrss == 11..00 iiff rree..sseeaarrcchh((rr""\\bb\\dd++((\\..\\dd++))??\\bb"",, tt)) eellssee
hhaass__ccaappiittaalliizzeedd == 11..00 iiff rree..sseeaarrcchh((rr""\\bb[[AA--ZZ]][[aa--zz]]++((??::\\ss++[[AA--
kkiinndd == ((mmeettaa..ggeett((""kkiinndd"")) oorr """"))..lloowweerr(())
kkiinndd__bboooosstt == 00..00
iiff kkiinndd iinn {{""pprreeffeerreennccee"",, ""pprroocceedduurree"",, ""ccoonnssttrraaiinntt"",, ""ddeeffiinn
kkiinndd__bboooosstt == 00..2200
iiff mmeettaa..ggeett((""ppiinnnneedd""))::
kkiinndd__bboooosstt ++== 00..2200
ggeenneerriicc__ppeennaallttyy == 00..1155 iiff lleenn((tt..sspplliitt(()))) << 66 aanndd kkiinndd nnoott ii
ssccoorree == 00..4455**lleennggtthh ++ 00..2200**hhaass__nnuummbbeerrss ++ 00..1155**hhaass__ccaappiittaalliizz
rreettuurrnn ffllooaatt((nnpp..cclliipp((ssccoorree,, 00..00,, 11..00))))
ddeeff sshhoouulldd__ssttoorree__llttmm((sseellff,, ssaalliieennccee:: ffllooaatt,, nnoovveellttyy:: ffllooaatt,, mmeett


---
*Page 8*


iiff mmeettaa..ggeett((""ppiinnnneedd""))::
rreettuurrnn TTrruuee
iiff ssaalliieennccee >>== sseellff..mmiinn__ssaalliieennccee__ttoo__ssttoorree aanndd nnoovveellttyy >>== ssee
rreettuurrnn TTrruuee
rreettuurrnn FFaallssee
ddeeff eeppiissooddiicc__vvaalluuee((sseellff,, oouuttccoommee__ssccoorree:: ffllooaatt,, ttaasskk:: ssttrr)) -->> ffll
ttaasskk__lleenn == mmiinn((lleenn((ttaasskk)) // 224400..00,, 11..00))
vvaall == 00..5555**((11 -- aabbss((00..6655 -- oouuttccoommee__ssccoorree)))) ++ 00..2255**ttaasskk__lleenn
rreettuurrnn ffllooaatt((nnpp..cclliipp((vvaall,, 00..00,, 11..00))))
ddeeff rraannkk__rreettrriieevveedd((sseellff,,
sseemmaannttiicc__hhiittss:: LLiisstt[[TTuuppllee[[ssttrr,, ffllooaatt]]]],,
eeppiissooddiicc__hhiittss:: LLiisstt[[TTuuppllee[[ssttrr,, ffllooaatt]]]],,
llttmm__iitteemmss:: DDiicctt[[ssttrr,, LLoonnggTTeerrmmIItteemm]],,
eeppiissooddeess:: DDiicctt[[ssttrr,, EEppiissooddee]])) -->> DDiicctt[[ssttrr,, AA
sseemm == [[]]
ffoorr mmiidd,, ssiimm iinn sseemmaannttiicc__hhiittss::
iitt == llttmm__iitteemmss..ggeett((mmiidd))
iiff nnoott iitt::
ccoonnttiinnuuee
ffrreesshhnneessss == 11..00
uussaaggee__ppeennaallttyy == 11..00 // ((11..00 ++ 00..1155**iitt..uussaaggee))
ssccoorree == ssiimm ** ((00..5555 ++ 00..4455**iitt..ssaalliieennccee)) ** uussaaggee__ppeennaallttyy
sseemm..aappppeenndd((((mmiidd,, ffllooaatt((ssccoorree))))))
eepp == [[]]
ffoorr eeiidd,, ssiimm iinn eeppiissooddiicc__hhiittss::
ee == eeppiissooddeess..ggeett((eeiidd))
iiff nnoott ee::
ccoonnttiinnuuee
ssccoorree == ssiimm ** ((00..66 ++ 00..44**ee..oouuttccoommee__ssccoorree))
eepp..aappppeenndd((((eeiidd,, ffllooaatt((ssccoorree))))))
sseemm..ssoorrtt((kkeeyy==llaammbbddaa xx:: xx[[11]],, rreevveerrssee==TTrruuee))
eepp..ssoorrtt((kkeeyy==llaammbbddaa xx:: xx[[11]],, rreevveerrssee==TTrruuee))
rreettuurrnn {{


---
*Page 9*


""sseemmaannttiicc__iiddss"":: [[mm ffoorr mm,, __ iinn sseemm[[::sseellff..ttooppkk__sseemmaannttiicc]]
""eeppiissooddiicc__iiddss"":: [[ee ffoorr ee,, __ iinn eepp[[::sseellff..ttooppkk__eeppiissooddiicc]]]]
""sseemmaannttiicc__ssccoorreedd"":: sseemm[[::sseellff..ttooppkk__sseemmaannttiicc]],,
""eeppiissooddiicc__ssccoorreedd"":: eepp[[::sseellff..ttooppkk__eeppiissooddiicc]],,
}}
We encode the rules that decide what is worth remembering and how retrieval should be ranked. We
formalize salience, novelty, usage decay, and outcome-based scoring to avoid noisy or repetitive memory
recall. This policy layer ensures memory growth remains controlled and useful rather than bloated. Check
out the Full Codes here.
COPY CODE
ccllaassss MMeemmoorryyEEnnggiinnee::
ddeeff ____iinniitt____((sseellff,,
eemmbbeedd__mmooddeell:: ssttrr == ""sseenntteennccee--ttrraannssffoorrmmeerrss//aallll--MMiinnii
ppoolliiccyy:: OOppttiioonnaall[[MMeemmoorryyPPoolliiccyy]] == NNoonnee))::
sseellff..ppoolliiccyy == ppoolliiccyy oorr MMeemmoorryyPPoolliiccyy(())
sseellff..eemmbbeeddddeerr == SSeenntteenncceeTTrraannssffoorrmmeerr((eemmbbeedd__mmooddeell))
sseellff..ddiimm == sseellff..eemmbbeeddddeerr..ggeett__sseenntteennccee__eemmbbeeddddiinngg__ddiimmeennssiioonn(())
sseellff..sshhoorrtt__tteerrmm:: LLiisstt[[SShhoorrttTTeerrmmIItteemm]] == [[]]
sseellff..llttmm:: DDiicctt[[ssttrr,, LLoonnggTTeerrmmIItteemm]] == {{}}
sseellff..eeppiissooddeess:: DDiicctt[[ssttrr,, EEppiissooddee]] == {{}}
sseellff..llttmm__iinnddeexx == VVeeccttoorrIInnddeexx((sseellff..ddiimm))
sseellff..eeppiissooddee__iinnddeexx == VVeeccttoorrIInnddeexx((sseellff..ddiimm))
ddeeff __nnooww((sseellff)) -->> ssttrr::
rreettuurrnn ddaatteettiimmee..uuttccnnooww(())..iissooffoorrmmaatt(()) ++ ""ZZ""


---
*Page 10*


ddeeff __eemmbbeedd((sseellff,, tteexxttss:: LLiisstt[[ssttrr]])) -->> nnpp..nnddaarrrraayy::
vv == sseellff..eemmbbeeddddeerr..eennccooddee((tteexxttss,, nnoorrmmaalliizzee__eemmbbeeddddiinnggss==TTrruuee,,
rreettuurrnn nnpp..aarrrraayy((vv,, ddttyyppee==nnpp..ffllooaatt3322))
ddeeff sstt__aadddd((sseellff,, rroollee:: ssttrr,, ccoonntteenntt:: ssttrr,, ****mmeettaa))::
sseellff..sshhoorrtt__tteerrmm..aappppeenndd((SShhoorrttTTeerrmmIItteemm((ttss==sseellff..__nnooww(()),, rroollee==rr
iiff lleenn((sseellff..sshhoorrtt__tteerrmm)) >> sseellff..ppoolliiccyy..sstt__mmaaxx__iitteemmss::
sseellff..sshhoorrtt__tteerrmm == sseellff..sshhoorrtt__tteerrmm[[--sseellff..ppoolliiccyy..sstt__mmaaxx__ii
ddeeff llttmm__aadddd((sseellff,, kkiinndd:: ssttrr,, tteexxtt:: ssttrr,, ttaaggss:: OOppttiioonnaall[[LLiisstt[[ssttrr
ttaaggss == ttaaggss oorr [[]]
mmeettaa == ddiicctt((mmeettaa))
mmeettaa[[""kkiinndd""]] == kkiinndd
ssaall == sseellff..ppoolliiccyy..ssaalliieennccee__ssccoorree((tteexxtt,, mmeettaa))
nnoovveellttyy == 11..00
iiff lleenn((sseellff..llttmm)) >> 00::
qq == sseellff..__eemmbbeedd(([[tteexxtt]]))[[00]]
hhiittss == sseellff..llttmm__iinnddeexx..sseeaarrcchh((qq,, kk==mmiinn((88,, sseellff..llttmm__iinnddeexx
iiff hhiittss::
mmaaxx__ssiimm == mmaaxx((ss ffoorr __,, ss iinn hhiittss))
nnoovveellttyy == 11..00 -- ffllooaatt((mmaaxx__ssiimm))
nnoovveellttyy == ffllooaatt((nnpp..cclliipp((nnoovveellttyy,, 00..00,, 11..00))))
iiff nnoott sseellff..ppoolliiccyy..sshhoouulldd__ssttoorree__llttmm((ssaall,, nnoovveellttyy,, mmeettaa))::
rreettuurrnn NNoonnee
mmeemm__iidd == ""mmeemm__"" ++ uuuuiidd..uuuuiidd44(())..hheexx[[::1122]]
iitteemm == LLoonnggTTeerrmmIItteemm((
mmeemm__iidd==mmeemm__iidd,,
ttss==sseellff..__nnooww(()),,
kkiinndd==kkiinndd,,
tteexxtt==tteexxtt..ssttrriipp(()),,
ttaaggss==ttaaggss,,


---
*Page 11*


ssaalliieennccee==ffllooaatt((ssaall)),,
uussaaggee==00,,
mmeettaa==mmeettaa
))
sseellff..llttmm[[mmeemm__iidd]] == iitteemm
vveecc == sseellff..__eemmbbeedd(([[iitteemm..tteexxtt]]))
sseellff..llttmm__iinnddeexx..aadddd(([[mmeemm__iidd]],, vveecc))
iiff lleenn((sseellff..llttmm)) >> sseellff..ppoolliiccyy..llttmm__mmaaxx__iitteemmss::
sseellff..__llttmm__pprruunnee(())
rreettuurrnn mmeemm__iidd
ddeeff __llttmm__pprruunnee((sseellff))::
iitteemmss == lliisstt((sseellff..llttmm..vvaalluueess(())))
ccaannddiiddaatteess == [[iitt ffoorr iitt iinn iitteemmss iiff nnoott iitt..mmeettaa..ggeett((""ppiinnnneedd
iiff nnoott ccaannddiiddaatteess::
rreettuurrnn
ccaannddiiddaatteess..ssoorrtt((kkeeyy==llaammbbddaa xx:: ((xx..ssaalliieennccee,, xx..uussaaggee))))
ddrroopp__nn == mmaaxx((11,, lleenn((sseellff..llttmm)) -- sseellff..ppoolliiccyy..llttmm__mmaaxx__iitteemmss))
ttoo__ddrroopp == sseett(([[iitt..mmeemm__iidd ffoorr iitt iinn ccaannddiiddaatteess[[::ddrroopp__nn]]]]))
ffoorr mmiidd iinn ttoo__ddrroopp::
sseellff..llttmm..ppoopp((mmiidd,, NNoonnee))
sseellff..__rreebbuuiilldd__llttmm__iinnddeexx(())
ddeeff __rreebbuuiilldd__llttmm__iinnddeexx((sseellff))::
sseellff..llttmm__iinnddeexx == VVeeccttoorrIInnddeexx((sseellff..ddiimm))
iiff nnoott sseellff..llttmm::
rreettuurrnn
iiddss == lliisstt((sseellff..llttmm..kkeeyyss(())))
vveeccss == sseellff..__eemmbbeedd(([[sseellff..llttmm[[ii]]..tteexxtt ffoorr ii iinn iiddss]]))
sseellff..llttmm__iinnddeexx..aadddd((iiddss,, vveeccss))
ddeeff eeppiissooddee__aadddd((sseellff,,
ttaasskk:: ssttrr,,
ccoonnssttrraaiinnttss:: DDiicctt[[ssttrr,, AAnnyy]],,


---
*Page 12*


ppllaann:: LLiisstt[[ssttrr]],,
aaccttiioonnss:: LLiisstt[[DDiicctt[[ssttrr,, AAnnyy]]]],,
rreessuulltt:: ssttrr,,
oouuttccoommee__ssccoorree:: ffllooaatt,,
lleessssoonnss:: LLiisstt[[ssttrr]],,
ffaaiilluurree__mmooddeess:: LLiisstt[[ssttrr]],,
ttaaggss:: OOppttiioonnaall[[LLiisstt[[ssttrr]]]] == NNoonnee,,
****mmeettaa)) -->> OOppttiioonnaall[[ssttrr]]::
ttaaggss == ttaaggss oorr [[]]
eepp__iidd == ""eepp__"" ++ uuuuiidd..uuuuiidd44(())..hheexx[[::1122]]
eepp == EEppiissooddee((
eepp__iidd==eepp__iidd,,
ttss==sseellff..__nnooww(()),,
ttaasskk==ttaasskk,,
ccoonnssttrraaiinnttss==ccoonnssttrraaiinnttss,,
ppllaann==ppllaann,,
aaccttiioonnss==aaccttiioonnss,,
rreessuulltt==rreessuulltt,,
oouuttccoommee__ssccoorree==ffllooaatt((nnpp..cclliipp((oouuttccoommee__ssccoorree,, 00..00,, 11..00)))),,
lleessssoonnss==lleessssoonnss,,
ffaaiilluurree__mmooddeess==ffaaiilluurree__mmooddeess,,
ttaaggss==ttaaggss,,
mmeettaa==ddiicctt((mmeettaa)),,
))
kkeeeepp == sseellff..ppoolliiccyy..eeppiissooddiicc__vvaalluuee((eepp..oouuttccoommee__ssccoorree,, eepp..ttaasskk
iiff kkeeeepp << 00..1188 aanndd nnoott eepp..mmeettaa..ggeett((""ppiinnnneedd""))::
rreettuurrnn NNoonnee
sseellff..eeppiissooddeess[[eepp__iidd]] == eepp
ccaarrdd == sseellff..__eeppiissooddee__ccaarrdd((eepp))
vveecc == sseellff..__eemmbbeedd(([[ccaarrdd]]))
sseellff..eeppiissooddee__iinnddeexx..aadddd(([[eepp__iidd]],, vveecc))
rreettuurrnn eepp__iidd
ddeeff __eeppiissooddee__ccaarrdd((sseellff,, eepp:: EEppiissooddee)) -->> ssttrr::


---
*Page 13*


lleessssoonnss == "";; ""..jjooiinn((eepp..lleessssoonnss[[::88]]))
ffaaiillss == "";; ""..jjooiinn((eepp..ffaaiilluurree__mmooddeess[[::66]]))
ppllaann == "" || ""..jjooiinn((eepp..ppllaann[[::1100]]))
rreettuurrnn ((
ff""TTaasskk:: {{eepp..ttaasskk}}\\nn""
ff""CCoonnssttrraaiinnttss:: {{jjssoonn..dduummppss((eepp..ccoonnssttrraaiinnttss,, eennssuurree__aasscciiii
ff""PPllaann:: {{ppllaann}}\\nn""
ff""OOuuttccoommeeSSccoorree:: {{eepp..oouuttccoommee__ssccoorree::..22ff}}\\nn""
ff""LLeessssoonnss:: {{lleessssoonnss}}\\nn""
ff""FFaaiilluurreeMMooddeess:: {{ffaaiillss}}\\nn""
ff""RReessuulltt:: {{eepp..rreessuulltt[[::440000]]}}""
))..ssttrriipp(())
We implement a main-memory engine that integrates embeddings, storage, pruning, and indexing into a
single system. We manage short-term buffers, long-term vector memory, and episodic traces while
enforcing size limits and pruning strategies. Check out the Full Codes here.
COPY CODE
ddeeff ccoonnssoolliiddaattee((sseellff))::
rreecceenntt == sseellff..sshhoorrtt__tteerrmm[[--mmiinn((lleenn((sseellff..sshhoorrtt__tteerrmm)),, 1100))::]]
tteexxttss == [[ff""{{iitt..rroollee}}:: {{iitt..ccoonntteenntt}}""..ssttrriipp(()) ffoorr iitt iinn rreecceenn
bblloobb == ""\\nn""..jjooiinn((tteexxttss))..ssttrriipp(())
iiff nnoott bblloobb::
rreettuurrnn {{""ssttoorreedd"":: [[]]}}
eexxttrraacctteedd == [[]]
ffoorr mm iinn rree..ffiinnddaallll((rr""\\bb((??::pprreeffeerr||lliikkeess??||aavvooiidd||ddoonn[[''’’]]tt wwaann
iiff mm..ssttrriipp(())::
eexxttrraacctteedd..aappppeenndd((((""pprreeffeerreennccee"",, mm..ssttrriipp(()),, [[""pprreeffeerr
ffoorr mm iinn rree..ffiinnddaallll((rr""\\bb((??::mmuusstt||sshhoouulldd||nneeeedd ttoo||ccoonnssttrraaiinntt))\\


---
*Page 14*


iiff mm..ssttrriipp(())::
eexxttrraacctteedd..aappppeenndd((((""ccoonnssttrraaiinntt"",, mm..ssttrriipp(()),, [[""ccoonnssttrr
pprroocc__ccaannddiiddaatteess == [[]]
ffoorr lliinnee iinn bblloobb..sspplliittlliinneess(())::
iiff rree..sseeaarrcchh((rr""\\bb((sstteepp||ffiirrsstt||tthheenn||ffiinnaallllyy))\\bb"",, lliinnee,, ffll
pprroocc__ccaannddiiddaatteess..aappppeenndd((lliinnee..ssttrriipp(())))
iiff pprroocc__ccaannddiiddaatteess::
eexxttrraacctteedd..aappppeenndd((((""pprroocceedduurree"",, "" || ""..jjooiinn((pprroocc__ccaannddiiddaatt
iiff nnoott eexxttrraacctteedd::
eexxttrraacctteedd..aappppeenndd((((""nnoottee"",, bblloobb[[--990000::]],, [[""nnoottee""]]))))
ssttoorreedd__iiddss == [[]]
ffoorr kkiinndd,, tteexxtt,, ttaaggss iinn eexxttrraacctteedd::
mmiidd == sseellff..llttmm__aadddd((kkiinndd==kkiinndd,, tteexxtt==tteexxtt,, ttaaggss==ttaaggss))
iiff mmiidd::
ssttoorreedd__iiddss..aappppeenndd((mmiidd))
rreettuurrnn {{""ssttoorreedd"":: ssttoorreedd__iiddss}}
ddeeff rreettrriieevvee((sseellff,, qquueerryy:: ssttrr,, ffiilltteerrss:: OOppttiioonnaall[[DDiicctt[[ssttrr,, AAnnyy]]
ffiilltteerrss == ffiilltteerrss oorr {{}}
qqvv == sseellff..__eemmbbeedd(([[qquueerryy]]))[[00]]
sseemm__hhiittss == sseellff..llttmm__iinnddeexx..sseeaarrcchh((qqvv,, kk==mmaaxx((sseellff..ppoolliiccyy..ttooppkk
eepp__hhiittss == sseellff..eeppiissooddee__iinnddeexx..sseeaarrcchh((qqvv,, kk==mmaaxx((sseellff..ppoolliiccyy..tt
ppaacckk == sseellff..ppoolliiccyy..rraannkk__rreettrriieevveedd((sseemm__hhiittss,, eepp__hhiittss,, sseellff..ll
ffoorr mmiidd iinn ppaacckk[[""sseemmaannttiicc__iiddss""]]::
iiff mmiidd iinn sseellff..llttmm::
sseellff..llttmm[[mmiidd]]..uussaaggee ++== 11


---
*Page 15*


rreettuurrnn ppaacckk
ddeeff bbuuiilldd__ccoonntteexxtt((sseellff,, qquueerryy:: ssttrr,, ppaacckk:: DDiicctt[[ssttrr,, AAnnyy]])) -->> sstt
sstt == sseellff..sshhoorrtt__tteerrmm[[--mmiinn((lleenn((sseellff..sshhoorrtt__tteerrmm)),, 88))::]]
sstt__bblloocckk == ""\\nn""..jjooiinn(([[ff""[[SSTT]] {{iitt..rroollee}}:: {{iitt..ccoonntteenntt}}"" ffoorr ii
sseemm__bblloocckk == """"
iiff ppaacckk[[""sseemmaannttiicc__iiddss""]]::
sseemm__lliinneess == [[]]
ffoorr mmiidd iinn ppaacckk[[""sseemmaannttiicc__iiddss""]]::
iitt == sseellff..llttmm[[mmiidd]]
sseemm__lliinneess..aappppeenndd((ff""[[LLTTMM::{{iitt..kkiinndd}}]] {{iitt..tteexxtt}} ((ssaalliiee
sseemm__bblloocckk == ""\\nn""..jjooiinn((sseemm__lliinneess))
eepp__bblloocckk == """"
iiff ppaacckk[[""eeppiissooddiicc__iiddss""]]::
eepp__lliinneess == [[]]
ffoorr eeiidd iinn ppaacckk[[""eeppiissooddiicc__iiddss""]]::
ee == sseellff..eeppiissooddeess[[eeiidd]]
lleessssoonnss == "";; ""..jjooiinn((ee..lleessssoonnss[[::88]])) iiff ee..lleessssoonnss eellss
ffaaiillss == "";; ""..jjooiinn((ee..ffaaiilluurree__mmooddeess[[::66]])) iiff ee..ffaaiilluurree
eepp__lliinneess..aappppeenndd((
ff""[[EEPP]] TTaasskk=={{ee..ttaasskk}} || ssccoorree=={{ee..oouuttccoommee__ssccoorree::..
ff"" LLeessssoonnss=={{lleessssoonnss}}\\nn""
ff"" AAvvooiidd=={{ffaaiillss}}""
))
eepp__bblloocckk == ""\\nn""..jjooiinn((eepp__lliinneess))
rreettuurrnn ((
""====== AAGGEENNTT MMEEMMOORRYY CCOONNTTEEXXTT ======\\nn""
ff""QQuueerryy:: {{qquueerryy}}\\nn\\nn""
""-------- SShhoorrtt--TTeerrmm ((wwoorrkkiinngg)) --------\\nn""
ff""{{sstt__bblloocckk oorr ''((eemmppttyy))''}}\\nn\\nn""
""-------- LLoonngg--TTeerrmm ((vveeccttoorr)) --------\\nn""
ff""{{sseemm__bblloocckk oorr ''((nnoonnee))''}}\\nn\\nn""
""-------- EEppiissooddiicc ((wwhhaatt wwoorrkkeedd llaasstt ttiimmee)) --------\\nn""
ff""{{eepp__bblloocckk oorr ''((nnoonnee))''}}\\nn""
""==========================================================\\nn""
))


---
*Page 16*


ddeeff llttmm__ddff((sseellff)) -->> ppdd..DDaattaaFFrraammee::
iiff nnoott sseellff..llttmm::
rreettuurrnn ppdd..DDaattaaFFrraammee((ccoolluummnnss==[[""mmeemm__iidd"",,""ttss"",,""kkiinndd"",,""tteexxtt
rroowwss == [[]]
ffoorr iitt iinn sseellff..llttmm..vvaalluueess(())::
rroowwss..aappppeenndd(({{
""mmeemm__iidd"":: iitt..mmeemm__iidd,,
""ttss"":: iitt..ttss,,
""kkiinndd"":: iitt..kkiinndd,,
""tteexxtt"":: iitt..tteexxtt,,
""ttaaggss"":: "",,""..jjooiinn((iitt..ttaaggss)),,
""ssaalliieennccee"":: iitt..ssaalliieennccee,,
""uussaaggee"":: iitt..uussaaggee
}}))
ddff == ppdd..DDaattaaFFrraammee((rroowwss))..ssoorrtt__vvaalluueess(([[""ssaalliieennccee"",,""uussaaggee""]],, aa
rreettuurrnn ddff
ddeeff eeppiissooddeess__ddff((sseellff)) -->> ppdd..DDaattaaFFrraammee::
iiff nnoott sseellff..eeppiissooddeess::
rreettuurrnn ppdd..DDaattaaFFrraammee((ccoolluummnnss==[[""eepp__iidd"",,""ttss"",,""ttaasskk"",,""oouuttccoo
rroowwss == [[]]
ffoorr ee iinn sseellff..eeppiissooddeess..vvaalluueess(())::
rroowwss..aappppeenndd(({{
""eepp__iidd"":: ee..eepp__iidd,,
""ttss"":: ee..ttss,,
""ttaasskk"":: ee..ttaasskk[[::112200]],,
""oouuttccoommee__ssccoorree"":: ee..oouuttccoommee__ssccoorree,,
""lleessssoonnss"":: "" || ""..jjooiinn((ee..lleessssoonnss[[::66]])),,
""ffaaiilluurree__mmooddeess"":: "" || ""..jjooiinn((ee..ffaaiilluurree__mmooddeess[[::66]])),,
""ttaaggss"":: "",,""..jjooiinn((ee..ttaaggss)),,
}}))
ddff == ppdd..DDaattaaFFrraammee((rroowwss))..ssoorrtt__vvaalluueess(([[""oouuttccoommee__ssccoorree"",,""ttss""]],,
rreettuurrnn ddff
We show how recent interactions are consolidated from short-term memory into durable long-term entries.
We implement a hybrid retrieval that combines semantic recall with episodic lessons learned from past


---
*Page 17*


tasks. This allows the agent to answer new queries using both factual memory and prior experience. Check
out the Full Codes here.
COPY CODE
ddeeff ooppeennaaii__cchhaatt((ssyysstteemm:: ssttrr,, uusseerr:: ssttrr)) -->> ssttrr::
rreesspp == cclliieenntt..cchhaatt..ccoommpplleettiioonnss..ccrreeaattee((
mmooddeell==OOPPEENNAAII__MMOODDEELL,,
mmeessssaaggeess==[[
{{""rroollee"":: ""ssyysstteemm"",, ""ccoonntteenntt"":: ssyysstteemm}},,
{{""rroollee"":: ""uusseerr"",, ""ccoonntteenntt"":: uusseerr}},,
]],,
tteemmppeerraattuurree==00..33
))
rreettuurrnn rreesspp..cchhooiicceess[[00]]..mmeessssaaggee..ccoonntteenntt
ddeeff hheeuurriissttiicc__rreessppoonnddeerr((ccoonntteexxtt:: ssttrr,, qquueessttiioonn:: ssttrr)) -->> ssttrr::
lleessssoonnss == rree..ffiinnddaallll((rr""LLeessssoonnss==((..**))"",, ccoonntteexxtt))
aavvooiidd == rree..ffiinnddaallll((rr""AAvvooiidd==((..**))"",, ccoonntteexxtt))
llttmm__lliinneess == [[llnn ffoorr llnn iinn ccoonntteexxtt..sspplliittlliinneess(()) iiff llnn..ssttaarrttsswwiitthh
sstteeppss == [[]]
iiff lleessssoonnss::
ffoorr cchhuunnkk iinn lleessssoonnss[[::22]]::
ffoorr ss iinn [[xx..ssttrriipp(()) ffoorr xx iinn cchhuunnkk..sspplliitt(("";;"")) iiff xx..ssttrrii
sstteeppss..aappppeenndd((ss))
ffoorr llnn iinn llttmm__lliinneess::
iiff ""[[LLTTMM::pprroocceedduurree]]"" iinn llnn..lloowweerr(())::
pprroocc == rree..ssuubb((rr""^^\\[[LLTTMM::pprroocceedduurree\\]]\\ss**"",, """",, llnn,, ffllaaggss==rr
pprroocc == pprroocc..sspplliitt((""((ssaalliieennccee==""))[[00]]..ssttrriipp(())
ffoorr ppaarrtt iinn [[pp..ssttrriipp(()) ffoorr pp iinn pprroocc..sspplliitt((""||"")) iiff pp..sstt
sstteeppss..aappppeenndd((ppaarrtt))
sstteeppss == sstteeppss[[::88]] iiff sstteeppss eellssee [[""CCllaarriiffyy tthhee ttaarrggeett oouuttccoommee aann
ppiittffaallllss == [[]]


---
*Page 18*


iiff aavvooiidd::
ffoorr cchhuunnkk iinn aavvooiidd[[::22]]::
ffoorr ss iinn [[xx..ssttrriipp(()) ffoorr xx iinn cchhuunnkk..sspplliitt(("";;"")) iiff xx..ssttrrii
ppiittffaallllss..aappppeenndd((ss))
ppiittffaallllss == ppiittffaallllss[[::66]]
pprreeffss == [[llnn ffoorr llnn iinn llttmm__lliinneess iiff ""[[LLTTMM::pprreeffeerreennccee]]"" iinn llnn..llooww
ffaaccttss == [[llnn ffoorr llnn iinn llttmm__lliinneess iiff ""[[LLTTMM::ffaacctt]]"" iinn llnn..lloowweerr(()) oo
oouutt == [[]]
oouutt..aappppeenndd((""AAnnsswweerr ((mmeemmoorryy--iinnffoorrmmeedd,, oofffflliinnee ffaallllbbaacckk))\\nn""))
iiff pprreeffss::
oouutt..aappppeenndd((""RReelleevvaanntt pprreeffeerreenncceess//ccoonnssttrraaiinnttss rreemmeemmbbeerreedd::""))
ffoorr llnn iinn ((pprreeffss ++ ffaaccttss))[[::66]]::
oouutt..aappppeenndd(("" -- "" ++ llnn..sspplliitt((""]] "",,11))[[11]]..sspplliitt(("" ((ssaalliieenncc
oouutt..aappppeenndd((""""))
oouutt..aappppeenndd((""RReeccoommmmeennddeedd aapppprrooaacchh::""))
ffoorr ii,, ss iinn eennuummeerraattee((sstteeppss,, 11))::
oouutt..aappppeenndd((ff"" {{ii}}.. {{ss}}""))
iiff ppiittffaallllss::
oouutt..aappppeenndd((""\\nnPPiittffaallllss ttoo aavvooiidd ((ffrroomm eeppiissooddiicc ttrraacceess))::""))
ffoorr pp iinn ppiittffaallllss::
oouutt..aappppeenndd(("" -- "" ++ pp))
oouutt..aappppeenndd((""\\nn((IIff yyoouu aadddd aann AAPPII kkeeyy,, tthhee ssaammee mmeemmoorryy ccoonntteexxtt ww
rreettuurrnn ""\\nn""..jjooiinn((oouutt))..ssttrriipp(())
ccllaassss MMeemmoorryyAAuuggmmeenntteeddAAggeenntt::
ddeeff ____iinniitt____((sseellff,, mmeemm:: MMeemmoorryyEEnnggiinnee))::
sseellff..mmeemm == mmeemm
ddeeff aannsswweerr((sseellff,, qquueessttiioonn:: ssttrr)) -->> DDiicctt[[ssttrr,, AAnnyy]]::
ppaacckk == sseellff..mmeemm..rreettrriieevvee((qquueessttiioonn))
ccoonntteexxtt == sseellff..mmeemm..bbuuiilldd__ccoonntteexxtt((qquueessttiioonn,, ppaacckk))
ssyysstteemm == ((
""YYoouu aarree aa mmeemmoorryy--aauuggmmeenntteedd aaggeenntt.. UUssee tthhee pprroovviiddeedd mmeemm
""PPrriioorriittiizzee::\\nn""
""11)) EEppiissooddiicc lleessssoonnss ((wwhhaatt wwoorrkkeedd bbeeffoorree))\\nn""


---
*Page 19*


""22)) LLoonngg--tteerrmm ffaaccttss//pprreeffeerreenncceess//pprroocceedduurreess\\nn""
""33)) SShhoorrtt--tteerrmm ccoonnvveerrssaattiioonn ssttaattee\\nn""
""BBee ccoonnccrreettee aanndd sstteeppwwiissee.. IIff mmeemmoorryy ccoonnfflliiccttss,, ssttaattee tt
))
iiff UUSSEE__OOPPEENNAAII::
rreeppllyy == ooppeennaaii__cchhaatt((ssyysstteemm==ssyysstteemm,, uusseerr==ccoonntteexxtt ++ ""\\nn\\nn
eellssee::
rreeppllyy == hheeuurriissttiicc__rreessppoonnddeerr((ccoonntteexxtt==ccoonntteexxtt,, qquueessttiioonn==qq
sseellff..mmeemm..sstt__aadddd((""uusseerr"",, qquueessttiioonn,, kkiinndd==""mmeessssaaggee""))
sseellff..mmeemm..sstt__aadddd((""aassssiissttaanntt"",, rreeppllyy,, kkiinndd==""mmeessssaaggee""))
rreettuurrnn {{""rreeppllyy"":: rreeppllyy,, ""ppaacckk"":: ppaacckk,, ""ccoonntteexxtt"":: ccoonntteexxtt}}
mmeemm == MMeemmoorryyEEnnggiinnee(())
aaggeenntt == MMeemmoorryyAAuuggmmeenntteeddAAggeenntt((mmeemm))
mmeemm..llttmm__aadddd((kkiinndd==""pprreeffeerreennccee"",, tteexxtt==""PPrreeffeerr ccoonncciissee,, ssttrruuccttuurreedd aann
mmeemm..llttmm__aadddd((kkiinndd==""pprreeffeerreennccee"",, tteexxtt==""PPrreeffeerr ssoolluuttiioonnss tthhaatt rruunn oonn
mmeemm..llttmm__aadddd((kkiinndd==""pprroocceedduurree"",, tteexxtt==""WWhheenn bbuuiillddiinngg aaggeenntt mmeemmoorryy:: eemm
mmeemm..llttmm__aadddd((kkiinndd==""ccoonnssttrraaiinntt"",, tteexxtt==""IIff nnoo AAPPII kkeeyy iiss aavvaaiillaabbllee,, pp
mmeemm..eeppiissooddee__aadddd((
ttaasskk==""BBuuiilldd aann aaggeenntt mmeemmoorryy llaayyeerr ffoorr ttrroouubblleesshhoooottiinngg PPyytthhoonn eerr
ccoonnssttrraaiinnttss=={{""oofffflliinnee__ookk"":: TTrruuee,, ""ssiinnggllee__nnootteebbooookk"":: TTrruuee}},,
ppllaann==[[
""CCaappttuurree sshhoorrtt--tteerrmm cchhaatt ccoonntteexxtt"",,
""SSttoorree dduurraabbllee ccoonnssttrraaiinnttss//pprreeffeerreenncceess iinn lloonngg--tteerrmm vveeccttoorr
""AAfftteerr ssoollvviinngg,, eexxttrraacctt lleessssoonnss iinnttoo eeppiissooddiicc ttrraacceess"",,
""OOnn nneeww ttaasskkss,, rreettrriieevvee ttoopp eeppiissooddiicc lleessssoonnss ++ sseemmaannttiicc ffaacc
]],,
aaccttiioonnss==[[
{{""ttyyppee""::""aannaallyyssiiss"",, ""ddeettaaiill""::""IIddeennttiiffiieedd rreeccuurrrriinngg ffaaiilluurree::
{{""ttyyppee""::""aaccttiioonn"",, ""ddeettaaiill""::""AAddddeedd ppiipp iinnssttaallll bblloocckk ++ mmiinniimm
{{""ttyyppee""::""aaccttiioonn"",, ""ddeettaaiill""::""AAddddeedd mmeemmoorryy ppoolliiccyy:: ppiinn ccoonnssttrr
]],,


---
*Page 20*


rreessuulltt==""NNootteebbooookk bbeeccaammee rroobbuusstt:: rruunnss wwiitthh oorr wwiitthhoouutt eexxtteerrnnaall kk
oouuttccoommee__ssccoorree==00..9900,,
lleessssoonnss==[[
""AAllwwaayyss iinncclluuddee aa ppiipp iinnssttaallll cceellll ffoorr nnoonn--ssttaannddaarrdd ddeeppss.."",,
""PPiinn hhaarrdd ccoonnssttrraaiinnttss ((ee..gg..,, oofffflliinnee ffaallllbbaacckk)) iinnttoo lloonngg--ttee
""SSttoorree aa ppoosstt--ttaasskk ''lleessssoonn lliisstt'' aass aann eeppiissooddiicc ttrraaccee ffoorr rr
]],,
ffaaiilluurree__mmooddeess==[[
""AAssssuummiinngg aann AAPPII kkeeyy eexxiissttss aanndd ccrraasshhiinngg wwhheenn aabbsseenntt.."",,
""SSttoorriinngg ttoooo mmuucchh nnooiissee iinnttoo lloonngg--tteerrmm mmeemmoorryy ccaauussiinngg iirrrreell
]],,
ttaaggss==[[""ccoollaabb"",,""rroobbuussttnneessss"",,""mmeemmoorryy""]]
))
pprriinntt((""✅✅ MMeemmoorryy eennggiinnee iinniittiiaalliizzeedd..""))
pprriinntt((ff"" LLTTMM iitteemmss:: {{lleenn((mmeemm..llttmm))}} || EEppiissooddeess:: {{lleenn((mmeemm..eeppiissooddeess
qq11 == ""II wwaanntt ttoo bbuuiilldd mmeemmoorryy ffoorr aann aaggeenntt iinn CCoollaabb.. WWhhaatt sshhoouulldd II
oouutt11 == aaggeenntt..aannsswweerr((qq11))
pprriinntt((""\\nn"" ++ ""==""**9900))
pprriinntt((""QQ11 RREEPPLLYY\\nn""))
pprriinntt((oouutt11[[""rreeppllyy""]][[::11880000]]))
qq22 == ""HHooww ddoo II aavvooiidd mmyy aaggeenntt rreeppeeaattiinngg tthhee ssaammee mmeemmoorryy oovveerr aanndd oo
oouutt22 == aaggeenntt..aannsswweerr((qq22))
pprriinntt((""\\nn"" ++ ""==""**9900))
pprriinntt((""QQ22 RREEPPLLYY\\nn""))
pprriinntt((oouutt22[[""rreeppllyy""]][[::11880000]]))
ddeeff ssiimmppllee__oouuttccoommee__eevvaall((tteexxtt:: ssttrr)) -->> ffllooaatt::
hhiittss == 00
ffoorr kkww iinn [[""ddeeccaayy"",, ""uussaaggee"",, ""ppeennaallttyy"",, ""nnoovveellttyy"",, ""pprruunnee"",, ""rree
iiff kkww iinn tteexxtt..lloowweerr(())::
hhiittss ++== 11
rreettuurrnn ffllooaatt((nnpp..cclliipp((hhiittss//88..00,, 00..00,, 11..00))))
ssccoorree22 == ssiimmppllee__oouuttccoommee__eevvaall((oouutt22[[""rreeppllyy""]]))
mmeemm..eeppiissooddee__aadddd((


---
*Page 21*


ttaasskk==""PPrreevveenntt rreeppeettiittiivvee rreeccaallll iinn aa mmeemmoorryy--aauuggmmeenntteedd aaggeenntt"",,
ccoonnssttrraaiinnttss=={{""mmuusstt__bbee__ssiimmppllee"":: TTrruuee,, ""rruunnss__iinn__ccoollaabb"":: TTrruuee}},,
ppllaann==[[
""TTrraacckk uussaaggee ccoouunnttss ppeerr mmeemmoorryy iitteemm"",,
""AAppppllyy uussaaggee--bbaasseedd ppeennaallttyy dduurriinngg rraannkkiinngg"",,
""BBoooosstt nnoovveellttyy dduurriinngg ssttoorraaggee ttoo rreedduuccee dduupplliiccaatteess"",,
""OOppttiioonnaallllyy pprruunnee llooww--ssaalliieennccee mmeemmoorriieess""
]],,
aaccttiioonnss==[[
{{""ttyyppee""::""ddeessiiggnn"",, ""ddeettaaiill""::""AAddddeedd uussaaggee--bbaasseedd ppeennaallttyy 11//((11++
{{""ttyyppee""::""ddeessiiggnn"",, ""ddeettaaiill""::""UUsseedd nnoovveellttyy == 11 -- mmaaxx__ssiimmiillaarrii
]],,
rreessuulltt==oouutt22[[""rreeppllyy""]][[::660000]],,
oouuttccoommee__ssccoorree==ssccoorree22,,
lleessssoonnss==[[
""PPeennaalliizzee oovveerruusseedd mmeemmoorriieess dduurriinngg rraannkkiinngg ((uussaaggee ddeeccaayy)).."",,
""EEnnffoorrccee nnoovveellttyy tthhrreesshhoolldd aatt ssttoorraaggee ttiimmee ttoo pprreevveenntt dduuppllii
""KKeeeepp eeppiissooddiicc lleessssoonnss ddiissttiilllleedd ttoo aavvooiidd bbllooaatteedd rreeccaallll ccoo
]],,
ffaaiilluurree__mmooddeess==[[
""NNoo uussaaggee ttrraacckkiinngg,, ccaauussiinngg oonnee hhiigghh--ssiimmiillaarriittyy mmeemmoorryy ttoo dd
""SSttoorriinngg rraaww cchhaatt llooggss aass LLTTMM iinnsstteeaadd ooff ddiissttiilllleedd ssuummmmaarriiee
]],,
ttaaggss==[[""rraannkkiinngg"",,""ddeeccaayy"",,""ppoolliiccyy""]]
))
ccoonnss == mmeemm..ccoonnssoolliiddaattee(())
pprriinntt((""\\nn"" ++ ""==""**9900))
pprriinntt((""CCOONNSSOOLLIIDDAATTIIOONN RREESSUULLTT::"",, ccoonnss))
pprriinntt((""\\nn"" ++ ""==""**9900))
pprriinntt((""LLTTMM ((ttoopp rroowwss))::""))
ddiissppllaayy((mmeemm..llttmm__ddff(())..hheeaadd((1122))))
pprriinntt((""\\nn"" ++ ""==""**9900))
pprriinntt((""EEPPIISSOODDEESS ((ttoopp rroowwss))::""))
ddiissppllaayy((mmeemm..eeppiissooddeess__ddff(())..hheeaadd((1122))))
ddeeff ddeebbuugg__rreettrriieevvaall((qquueerryy:: ssttrr))::


---
*Page 22*


ppaacckk == mmeemm..rreettrriieevvee((qquueerryy))
ccttxx == mmeemm..bbuuiilldd__ccoonntteexxtt((qquueerryy,, ppaacckk))
sseemm == [[]]
ffoorr mmiidd,, sscc iinn ppaacckk[[""sseemmaannttiicc__ssccoorreedd""]]::
iitt == mmeemm..llttmm[[mmiidd]]
sseemm..aappppeenndd(({{""mmeemm__iidd"":: mmiidd,, ""ssccoorree"":: sscc,, ""kkiinndd"":: iitt..kkiinndd,, ""ss
eepp == [[]]
ffoorr eeiidd,, sscc iinn ppaacckk[[""eeppiissooddiicc__ssccoorreedd""]]::
ee == mmeemm..eeppiissooddeess[[eeiidd]]
eepp..aappppeenndd(({{""eepp__iidd"":: eeiidd,, ""ssccoorree"":: sscc,, ""oouuttccoommee"":: ee..oouuttccoommee__
rreettuurrnn ccttxx,, ppdd..DDaattaaFFrraammee((sseemm)),, ppdd..DDaattaaFFrraammee((eepp))
pprriinntt((""\\nn"" ++ ""==""**9900))
ccttxx,, sseemm__ddff,, eepp__ddff == ddeebbuugg__rreettrriieevvaall((""HHooww ddoo II ddeessiiggnn aann aaggeenntt mmeemm
pprriinntt((ccttxx[[::11660000]]))
pprriinntt((""\\nnTToopp sseemmaannttiicc hhiittss::""))
ddiissppllaayy((sseemm__ddff))
pprriinntt((""\\nnTToopp eeppiissooddiicc hhiittss::""))
ddiissppllaayy((eepp__ddff))
pprriinntt((""\\nn✅✅ DDoonnee.. YYoouu nnooww hhaavvee wwoorrkkiinngg sshhoorrtt--tteerrmm,, lloonngg--tteerrmm vveeccttoo
We wrap the memory engine inside a simple memory-augmented agent and run end-to-end queries. We
demonstrate how episodic memory influences responses, how outcomes are evaluated, and how new
episodes are written back into memory. It closes the loop and shows how the agent continuously learns
from its own behavior.
In conclusion, we have a complete memory stack that lets our agent remember facts and preferences in
long-term vector memory, retain distilled “lessons learned” as episodic traces, and keep only the most
relevant recent context in short-term memory. We demonstrated how hybrid retrieval improves responses,
how usage-based penalties reduce repetition, and how consolidation turns noisy interaction logs into
compact, reusable knowledge. With this foundation, we can extend the system toward production-grade
agent behavior by adding stricter budgets, richer extraction, better evaluators, and task-specific memory
schemas while keeping the same core idea: we store less, store smarter, and retrieve what actually helps.


---
*Page 23*


Check out the Full Codes here. Also, feel free to follow us on Twitter and don’t forget to join our 100k+ ML
SubReddit and Subscribe to our Newsletter. Wait! are you on telegram? now you can join us on telegram
as well.
🧵🧵 Recommended Open Source AI: Meet CopilotKit- Framework for building agent-native applications
with Generative UI.
Previous article Next article
A Coding and Experimental Analysis of Decentralized NVIDIA AI Brings Nemotron-3-Nano-30B to NVFP4
Federated Learning with Gossip Protocols and with Quantization Aware Distillation (QAD) for Efficient
Differential Privacy Reasoning Inference
RELATED ARTICLES
ByteDance Releases Protenix-v1: A New Open-Source Model Achieving
AF3-Level Performance in...
Asif Razzaq-February 8, 2026
How to Design Production-Grade Mock Data Pipelines Using Polyfactory
with Dataclasses,...
Asif Razzaq-February 8, 2026
Google AI Introduces PaperBanana: An Agentic Framework that Automates
Publication Ready...
Asif Razzaq-February 7, 2026
How to Build a Production-Grade Agentic AI System with Hybrid
Retrieval,...
Asif Razzaq-February 6, 2026
NVIDIA AI releases C-RADIOv4 vision backbone unifying SigLIP2, DINOv3,
SAM3 for...
Asif Razzaq-February 6, 2026
A Coding, Data-Driven Guide to Measuring, Visualizing, and Enforcing
Cognitive Complexity...


---
*Page 24*


Asif Razzaq-February 6, 2026


---
*Page 26*


ABOUT US
Marktechpost is a California-based AI News Platform providing easy-to-consume, byte size updates in
machine learning, deep learning, and data science research.
Contact us: Asif@marktechpost.com
FOLLOW US
   
© Copyright reserved @2025 Marktechpost AI Media Inc | Please note that we do make a small profit through our
affiliates/referrals via product promotion in the articles
Privacy & Cookies Policy
Exit mobile version