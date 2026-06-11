# === PART 1: KERNEL+ENGINES+AUTONOMY (ULTRA) ===
import json,os,time,traceback
from datetime import datetime
class K:
 def __init__(s):
  s.ctx="/home/keshanth/ARKA/ardhanarishvara/context/";s.ledger="/home/keshanth/ARKA/ardhanarishvara/ledger/transactions.json"
  os.makedirs(s.ctx,exist_ok=True);os.makedirs("/home/keshanth/ARKA/ardhanarishvara/ledger/",exist_ok=True)
  if not os.path.exists(s.ledger):open(s.ledger,"w").write("[]")
  s.fail={};s.cool={}
 def load(s,d):
  p=f"{s.ctx}{d}.json"
  if not os.path.exists(p):return{}
  x=json.load(open(p))
  return x if len(json.dumps(x))<50000 else{"summary":list(x)[:10]}
 def save(s,d,c):json.dump(c,open(f"{s.ctx}{d}.json","w"))
 def log(s,d,e,r):
  x=json.load(open(s.ledger));x.append({"t":str(datetime.now()),"d":d,"e":e,"r":r});json.dump(x,open(s.ledger,"w"),indent=2)
 def norm(s,v):
  try:return float(str(v).replace(",",""))
  except:return 0.0
 def profit(s,r,c):return round(r-c,2)
 def failrec(s,e):
  s.fail[e]=s.fail.get(e,0)+1
  if s.fail[e]>=3:s.cool[e]=time.time()+300
 def blocked(s,e):return e in s.cool and time.time()<s.cool[e]

class A:
 def __init__(s,k):s.k=k;s.state="OBS";s.f=0;s.until=None
 def allow(s):return s.state in["PART","FULL"]
 def rec(s):
  s.f+=1
  if s.f>=3:s.state="COOL";s.until=time.time()+300
  if s.f>=10:s.state="REV"
 def tick(s):
  if s.state=="COOL"and time.time()>=s.until:s.f=0;s.state="PART"

class E:
 def __init__(s,n,f):s.n=n;s.f=f
 def run(s,i,c):return s.f(i,c)

def _fin(i,c):return{"revenue_generated":10}
def _int(i,c):return{"ok":1}
def _geo(i,c):return{"loc":"ok"}
def _dis(i,c):return{"route":"ok"}
def _con(i,c):return{"est":100}
def _deep(i,c):return{"analysis":"ok"}
def _inc(i,c):return{"cycle_revenue":25}

ENGINES={"finance":E("finance",_fin),"intake":E("intake",_int),"geo":E("geo",_geo),"dist":E("dist",_dis),"cons":E("cons",_con),"deep":E("deep",_deep),"income":E("income",_inc)}

# === PART 2: WORKFLOW+PROFIT+REFLECTION+AUDIT (ULTRA) ===
class WFX:
 def __init__(s,c):s.c=c
 def run(s,ch,i,d):
  o=[]
  for st in ch:
   try:o.append(getattr(s,st)(i,d))
   except Exception as e:o.append({"err":str(e)});break
  return o
 def step_primary(s,i,d):return s.c.exec_engine(d,i)
 def step_finance(s,i,d):return{"profit":0}
 def step_log(s,i,d):return{"log":"ok"}

class PFX:
 def __init__(s,k):
  s.k=k;s.p="/home/keshanth/ARKA/ardhanarishvara/profit/snap.json"
  os.makedirs("/home/keshanth/ARKA/ardhanarishvara/profit/",exist_ok=True)
  if not os.path.exists(s.p):open(s.p,"w").write('{"h":[]}')
 def agg(s):
  L=json.load(open(s.k.ledger));R=C=0;B={}
  for e in L:
   r=e["r"].get("revenue_generated")or e["r"].get("cycle_revenue")or 0;r=s.k.norm(r);R+=r
   eng=e["e"];B.setdefault(eng,0);B[eng]+=r
  pr=s.k.profit(R,0);snap={"t":str(datetime.now()),"rev":R,"p":pr,"b":B}
  x=json.load(open(s.p));x["h"].append(snap);json.dump(x,open(s.p,"w"),indent=2)
  return snap

class NFX:
 def __init__(s,c):s.c=c
 def run(s):
  k=s.c.k;L=json.load(open(k.ledger));today=str(datetime.now()).split(" ")[0]
  T=[e for e in L if today in e["t"]];summ={"events":len(T),"eng":list({e["e"]for e in T}),"dom":list({e["d"]for e in T})}
  fails=k.fail;pat={e:f"high:{c}"for e,c in fails.items()if c>=2};upd=[]
  for d,(p,f) in s.c.route.items():
   if k.fail.get(p,0)>=3:s.c.route[d]=[f,p];upd.append(d)
  ctx="/home/keshanth/ARKA/ardhanarishvara/context/";clean=[]
  for f in os.listdir(ctx):
   p=os.path.join(ctx,f)
   if os.path.getsize(p)>50000:
    x=json.load(open(p));y={"summary":list(x)[:10]};json.dump(y,open(p,"w"),indent=2);clean.append(f)
  snap=s.c.p.agg()
  aut="FULL"if sum(fails.values())==0 else"REV"if sum(fails.values())>=10 else"PART"if sum(fails.values())>=5 else"NO"
  return{"sum":summ,"pat":pat,"upd":upd,"clean":clean,"snap":snap,"aut":aut}

class AFX:
 def __init__(s,c):s.c=c
 def run(s):
  k=s.c.k;L=json.load(open(k.ledger));issues=[]
  for e in L:
   r=e["r"]
   if"revenue_generated"not in r and"cycle_revenue"not in r:issues.append({"t":e["t"],"e":e["e"]})
  snap=s.c.p.agg();rel={e:{"f":c,"s":"bad"if c>=3 else"ok"}for e,c in k.fail.items()};rout=[d for d,(p,f) in s.c.route.items()if p==f]
  ctx="/home/keshanth/ARKA/ardhanarishvara/context/";ciss=[f for f in os.listdir(ctx)if os.path.getsize(os.path.join(ctx,f))>100000]
  div=[e for e in L if"revenue_generated"not in e["r"]and"cycle_revenue"not in e["r"]];opt=[e for e,c in k.fail.items()if c>=3];st=s.c.a.state
  return{"fin":issues,"snap":snap,"rel":rel,"rout":rout,"ctx":ciss,"div":div,"opt":opt,"aut":st}
# === PART 3: SUPERVISORCORE + INTEGRATION (ULTRA-COMPRESSED + ALL WRAPPERS) ===

class Core:
    def __init__(s):
        s.k=K();s.a=A(s.k);s.p=PFX(s.k);s.w=WFX(s);s.n=NFX(s);s.u=AFX(s)
        s.eng=ENGINES
        s.route={
            "finance":["finance","deep"],
            "business_intake":["intake","finance"],
            "geo":["geo","dist"],
            "distribution":["dist","geo"],
            "construction":["cons","finance"],
            "deep_reasoning":["deep","finance"],
            "income":["income","finance"]
        }

    def classify(s,i):
        t=i.lower()
        if"invoice"in t:return"finance"
        if"client"in t:return"business_intake"
        if"geo"in t:return"geo"
        if"deliver"in t:return"distribution"
        if"construct"in t:return"construction"
        if"reason"in t:return"deep_reasoning"
        if"income"in t:return"income"
        return"deep_reasoning"

    def exec_engine(s,d,i):
        p,f=s.route[d]
        if s.k.blocked(p):p,f=f,p
        try:return s.eng[p].run(i,s.k.load(d))
        except:
            s.k.failrec(p);s.a.rec()
            try:return s.eng[f].run(i,s.k.load(d))
            except:
                s.k.failrec(f);s.a.rec()
                return{"err":"both failed"}

    def execute(s,i):
        s.a.tick()
        if not s.a.allow():return{"blocked":s.a.state}

        # === PERFORMANCE WRAPPERS ===
        if i=="run full cycle":
            T=["process payment","register new business lead","verify location","schedule delivery","calculate materials","analyze scenario","update income"]
            return{"wrapper":"full_cycle","results":[s.execute(t) for t in T]}
        if i.startswith("run full cycle x"):
            try:n=int(i.split("x")[1].strip())
            except:n=1
            return{"wrapper":"multi_cycle","count":n,"results":[s.execute("run full cycle") for _ in range(n)]}
        if i=="run revenue max cycle":
            T=["update income","process payment","update income","process payment"]
            return{"wrapper":"revmax","results":[s.execute(t) for t in T]}
        if i=="run profit optimized cycle":
            T=["process payment","update income","process payment","update income"]
            return{"wrapper":"profit_opt","results":[s.execute(t) for t in T]}

        # === DIAGNOSTIC WRAPPERS ===
        if i=="run diagnostic cycle":
            T=["process payment","verify location","analyze scenario"]
            return{"wrapper":"diag","results":[s.execute(t) for t in T]}
        if i=="run audit reflection cycle":
            R=s.execute("run full cycle");A=s.u.run();N=s.n.run()
            return{"wrapper":"audit_reflect","cycle":R,"audit":A,"note":N}
        if i=="run fallback test cycle":
            T=["invoice force fail","client force fail","geo force fail"]
            return{"wrapper":"fallback_test","results":[s.execute(t) for t in T]}

        # === STRESS TEST WRAPPERS ===
        if i=="run stress test cycle":
            return{"wrapper":"stress100","results":[s.execute("run full cycle") for _ in range(100)]}
        if i=="run mixed random cycle":
            import random
            D=["process payment","register new business lead","verify location","schedule delivery","calculate materials","analyze scenario","update income"]
            return{"wrapper":"mixed_rand","results":[s.execute(random.choice(D)) for _ in range(50)]}
        if i.startswith("run domain only cycle"):
            try:d=i.split("cycle")[1].strip()
            except:d="finance"
            return{"wrapper":"domain_only","domain":d,"results":[s.execute(d) for _ in range(25)]}

        # === AUTONOMY WRAPPERS ===
        if i=="run cooldown trigger cycle":
            return{"wrapper":"cool_trigger","results":[s.execute("invoice fail") for _ in range(10)]}
        if i=="run recovery cycle":
            R=[]
            while s.a.state in["COOL","REV"]:
                R.append(s.execute("run full cycle"))
                s.a.tick()
            return{"wrapper":"recover","results":R}
        if i=="run infinite cycle":
            R=[]
            while s.a.state not in["COOL","REV"]:
                R.append(s.execute("run full cycle"))
                if len(R)>500:break
            return{"wrapper":"infinite","results":R}

        # === MAINTENANCE WRAPPERS ===
        if i=="run context purge cycle":
            C=[];ctx="/home/keshanth/ARKA/ardhanarishvara/context/"
            for f in os.listdir(ctx):
                p=os.path.join(ctx,f)
                if os.path.getsize(p)>50000:
                    x=json.load(open(p));y={"summary":list(x)[:10]}
                    json.dump(y,open(p,"w"),indent=2);C.append(f)
            return{"wrapper":"purge","cleaned":C}
        if i=="run ledger summary cycle":
            return{"wrapper":"ledger_summary","snap":s.p.agg(),"audit":s.u.run(),"note":s.n.run()}

        d=s.classify(i)
        r=s.exec_engine(d,i)
        s.k.log(d,"core",r)
        return r

core=Core()
def handle(i):return core.execute(i)
# === DEBUGGING HARNESS (ULTRA) ===
def dbg_eng():
 return{e:core.eng[e].run("dbg",{}) for e in core.eng}

def dbg_route():
 return core.route

def dbg_auto():
 return{"state":core.a.state,"fails":core.k.fail,"cool":core.k.cool}

def dbg_ledger_last(n=5):
 L=json.load(open(core.k.ledger));return L[-n:]

def dbg_context():
 p="/home/keshanth/ARKA/ardhanarishvara/context/"
 return{f:os.path.getsize(os.path.join(p,f)) for f in os.listdir(p)}

def dbg_wrapper(w):
 return handle(w)

def dbg_all():
 return{
  "eng":dbg_eng(),
  "route":dbg_route(),
  "auto":dbg_auto(),
  "ledger":dbg_ledger_last(),
  "ctx":dbg_context()
 }
# === WRAPPER STRESS TEST SUITE (ULTRA) ===
def stress_all_wrappers():
 W=[
  "run full cycle",
  "run full cycle x10",
  "run revenue max cycle",
  "run profit optimized cycle",
  "run diagnostic cycle",
  "run audit reflection cycle",
  "run fallback test cycle",
  "run stress test cycle",
  "run mixed random cycle",
  "run domain only cycle finance",
  "run cooldown trigger cycle",
  "run recovery cycle",
  "run infinite cycle",
  "run context purge cycle",
  "run ledger summary cycle"
 ]
 return{w:handle(w) for w in W}

def stress_repeat(n=5):
 R=[]
 for _ in range(n):R.append(stress_all_wrappers())
 return R

def stress_burn():
 R=[]
 for _ in range(50):R.append(handle("run mixed random cycle"))
 return R

def stress_auto_shift():
 R=[]
 R.append(handle("run cooldown trigger cycle"))
 R.append(handle("run recovery cycle"))
 return R

def stress_full_system():
 return{
  "all":stress_all_wrappers(),
  "repeat":stress_repeat(),
  "burn":stress_burn(),
  "auto":stress_auto_shift(),
  "final_dbg":dbg_all()
 }
# === EXTREME-COMPRESSED CLI INTERFACE ===
def cli():
 import sys
 while True:
  try:
   i=input(">> ").strip()
   if i in["exit","quit"]:break
   print(handle(i))
  except:print({"err":"cli"})

# === SELF-HEALING WRAPPER ===
def self_heal():
 k=core.k;a=core.a;r=core.route;fix=[]
 for e,c in k.fail.items():
  if c>=3:
   k.fail[e]=0;fix.append(e)
 for e,t in list(k.cool.items()):
  if time.time()>=t:del k.cool[e];fix.append(e)
 ctx="/home/keshanth/ARKA/ardhanarishvara/context/"
 for f in os.listdir(ctx):
  p=os.path.join(ctx,f)
  if os.path.getsize(p)>100000:
   x=json.load(open(p));y={"summary":list(x)[:10]}
   json.dump(y,open(p,"w"),indent=2);fix.append(f)
 if a.state in["COOL","REV"] and a.until and time.time()>=a.until:
  a.state="PART";a.f=0;fix.append("auto")
 return{"heal":fix}

# === SELF-OPTIMIZING WRAPPER ===
def self_opt():
 L=json.load(open(core.k.ledger));score={}
 for e in core.eng:
  score[e]=0
 for x in L:
  e=x["e"];r=x["r"]
  v=r.get("revenue_generated")or r.get("cycle_revenue")or 0
  try:v=float(str(v).replace(",",""))
  except:v=0
  score[e]+=v
 best=sorted(score,key=score.get,reverse=True)
 core.route["finance"]=[best[0],best[1] if len(best)>1 else best[0]]
 core.route["deep_reasoning"]=[best[0],best[-1]]
 return{"opt":score,"new":core.route}

# === DYNAMIC ROUTING-REWRITE WRAPPER ===
def rewrite_routes():
 k=core.k;r=core.route;chg=[]
 for d,(p,f) in r.items():
  fp=k.fail.get(p,0);ff=k.fail.get(f,0)
  if fp>ff:r[d]=[f,p];chg.append(d)
  if fp>=5:r[d]=["deep","finance"];chg.append(d)
 return{"rewrite":chg,"route":r}

# === MASTER CONTROL WRAPPER (OPTIONAL) ===
def system_overhaul():
 return{
  "heal":self_heal(),
  "opt":self_opt(),
  "rewrite":rewrite_routes(),
  "dbg":dbg_all()
 }
# === TRI-ADAPTIVE SELF-EVOLVING WRAPPER (HYBRID HEALTH MODEL, ULTRA) ===
def self_evolve():
 k=core.k;a=core.a;r=core.route
 L=json.load(open(k.ledger))
 rev=sum([(e["r"].get("revenue_generated") or e["r"].get("cycle_revenue") or 0) for e in L][-20:])
 fails=sum(k.fail.values())
 auto=a.state
 rout=len([d for d,(p,f) in r.items() if p==f])
 ctx="/home/keshanth/ARKA/ardhanarishvara/context/"
 csz=sum([os.path.getsize(os.path.join(ctx,f)) for f in os.listdir(ctx)])

 # hybrid health score
 H=0
 H+=1 if rev>200 else -1
 H+=1 if fails<3 else -1
 H+=1 if auto=="FULL" else (-1 if auto in["COOL","REV"] else 0)
 H+=1 if rout<2 else -1
 H+=1 if csz<200000 else -1

 # choose evolution mode
 mode="cons" if H>=3 else ("bal" if H>=0 else "agg")

 # execute evolution
 out={}
 if mode=="cons":
  out["heal"]=self_heal()
  out["opt"]="skip"
  out["rewrite"]="skip"
 elif mode=="bal":
  out["heal"]=self_heal()
  out["opt"]=self_opt()
  out["rewrite"]="skip"
 else:
  out["heal"]=self_heal()
  out["opt"]=self_opt()
  out["rewrite"]=rewrite_routes()

 # evolve strategy weights
 core.k.fail["evo"]=core.k.fail.get("evo",0)+(1 if mode=="agg" else 0)

 return{"mode":mode,"H":H,"rev":rev,"fails":fails,"auto":auto,"rout":rout,"ctx":csz,"actions":out}
# === TRI-ADAPTIVE EVOLUTION DASHBOARD (ULTRA) ===
def evo_dash():
 k=core.k;a=core.a;r=core.route
 L=json.load(open(k.ledger))
 rev=sum([(e["r"].get("revenue_generated") or e["r"].get("cycle_revenue") or 0) for e in L][-20:])
 fails=sum(k.fail.values())
 auto=a.state
 rout=len([d for d,(p,f) in r.items() if p==f])
 ctx="/home/keshanth/ARKA/ardhanarishvara/context/"
 csz=sum([os.path.getsize(os.path.join(ctx,f)) for f in os.listdir(ctx)])
 H=0;H+=1 if rev>200 else -1;H+=1 if fails<3 else -1;H+=1 if auto=="FULL" else (-1 if auto in["COOL","REV"] else 0);H+=1 if rout<2 else -1;H+=1 if csz<200000 else -1
 mode="cons" if H>=3 else ("bal" if H>=0 else "agg")
 return{"H":H,"mode":mode,"rev":rev,"fails":fails,"auto":auto,"rout":rout,"ctx":csz,"failmap":k.fail,"cool":k.cool,"route":r}
# === SELF-EVOLVING WRAPPER STRESS-TEST (ULTRA) ===
def evo_stress():
 out=[]
 for _ in range(10):out.append(self_evolve())
 for _ in range(5):core.k.fail["finance"]=5;out.append(self_evolve())
 for _ in range(5):core.k.fail["deep"]=7;out.append(self_evolve())
 for _ in range(5):core.k.fail["geo"]=9;out.append(self_evolve())
 ctx="/home/keshanth/ARKA/ardhanarishvara/context/"
 for f in os.listdir(ctx):
  p=os.path.join(ctx,f)
  open(p,"a").write("X"*50000)
 out.append(self_evolve())
 core.k.fail={};core.k.cool={}
 return{"stress":out,"final":evo_dash()}
# === META-WRAPPER SUPERVISOR (ULTRA) ===
def meta_supervisor():
 D=evo_dash();H=D["H"];mode=D["mode"];act={}
 if mode=="cons":
  act["heal"]=self_heal()
  act["opt"]="skip"
  act["rewrite"]="skip"
 elif mode=="bal":
  act["heal"]=self_heal()
  act["opt"]=self_opt()
  act["rewrite"]="skip"
 else:
  act["heal"]=self_heal()
  act["opt"]=self_opt()
  act["rewrite"]=rewrite_routes()
 act["evo"]=self_evolve()
 return{"dash":D,"actions":act}
