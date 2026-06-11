# === PART 1: KERNEL + ENGINES + AUTONOMY (MAX-COMPRESSED) ===
import json,os,time,traceback
from datetime import datetime

class K:
    def __init__(s):
        s.ctx="/home/keshanth/ARKA/ardhanarishvara/context/"
        s.ledger="/home/keshanth/ARKA/ardhanarishvara/ledger/transactions.json"
        os.makedirs(s.ctx,exist_ok=True)
        os.makedirs("/home/keshanth/ARKA/ardhanarishvara/ledger/",exist_ok=True)
        if not os.path.exists(s.ledger):open(s.ledger,"w").write("[]")
        s.fail={}
        s.cool={}

    def load(s,d):
        p=f"{s.ctx}{d}.json"
        if not os.path.exists(p):return{}
        x=json.load(open(p))
        return x if len(json.dumps(x))<50000 else {"summary":list(x)[:10]}

    def save(s,d,c):json.dump(c,open(f"{s.ctx}{d}.json","w"))

    def log(s,d,e,r):
        x=json.load(open(s.ledger))
        x.append({"t":str(datetime.now()),"d":d,"e":e,"r":r})
        json.dump(x,open(s.ledger,"w"),indent=2)

    def norm(s,v):
        try:return float(str(v).replace(",",""))
        except:return 0.0

    def profit(s,r,c):return round(r-c,2)

    def failrec(s,e):
        s.fail[e]=s.fail.get(e,0)+1
        if s.fail[e]>=3:s.cool[e]=time.time()+300

    def blocked(s,e):return e in s.cool and time.time()<s.cool[e]


# === AUTONOMY STATE MACHINE (COMPRESSED) ===
class A:
    def __init__(s,k):
        s.k=k
        s.state="OBS"
        s.f=0
        s.until=None

    def allow(s):return s.state in["PART","FULL"]

    def rec(s):
        s.f+=1
        if s.f>=3:s.state="COOL";s.until=time.time()+300
        if s.f>=10:s.state="REV"

    def tick(s):
        if s.state=="COOL"and time.time()>=s.until:
            s.f=0;s.state="PART"


# === ENGINE WRAPPER (COMPRESSED) ===
class E:
    def __init__(s,n,f):s.n=n;s.f=f
    def run(s,i,c):return s.f(i,c)


# === ALL ENGINES (COMPRESSED INLINE) ===
def _fin(i,c):return{"revenue_generated":10}
def _int(i,c):return{"ok":1}
def _geo(i,c):return{"loc":"ok"}
def _dis(i,c):return{"route":"ok"}
def _con(i,c):return{"est":100}
def _deep(i,c):return{"analysis":"ok"}
def _inc(i,c):return{"cycle_revenue":25}

ENGINES={
    "finance":E("finance",_fin),
    "intake":E("intake",_int),
    "geo":E("geo",_geo),
    "dist":E("dist",_dis),
    "cons":E("cons",_con),
    "deep":E("deep",_deep),
    "income":E("income",_inc)
}
# === PART 2: WORKFLOW + PROFIT + REFLECTION + AUDIT (MAX-COMPRESSED) ===

class WFX:
    def __init__(s,core):s.c=core
    def run(s,chain,i,d):
        o=[]
        for st in chain:
            try:o.append(getattr(s,st)(i,d))
            except Exception as e:o.append({"err":str(e)});break
        return o
    def step_primary(s,i,d):return s.c.exec_engine(d,i)
    def step_finance(s,i,d):return{"profit":0}
    def step_log(s,i,d):return{"log":"ok"}

class PFX:
    def __init__(s,k):
        s.k=k
        s.p="/home/keshanth/ARKA/ardhanarishvara/profit/snap.json"
        os.makedirs("/home/keshanth/ARKA/ardhanarishvara/profit/",exist_ok=True)
        if not os.path.exists(s.p):open(s.p,"w").write('{"h":[]}')
    def agg(s):
        L=json.load(open(s.k.ledger))
        R=C=0;B={}
        for e in L:
            r=e["r"].get("revenue_generated")or e["r"].get("cycle_revenue")or 0
            r=s.k.norm(r);R+=r
            eng=e["e"];B.setdefault(eng,0);B[eng]+=r
        pr=s.k.profit(R,0)
        snap={"t":str(datetime.now()),"rev":R,"p":pr,"b":B}
        x=json.load(open(s.p));x["h"].append(snap);json.dump(x,open(s.p,"w"),indent=2)
        return snap

class NFX:
    def __init__(s,core):s.c=core
    def run(s):
        k=s.c.k
        L=json.load(open(k.ledger))
        today=str(datetime.now()).split(" ")[0]
        T=[e for e in L if today in e["t"]]
        summ={"events":len(T),"eng":list({e["e"] for e in T}),"dom":list({e["d"] for e in T})}
        fails=k.fail
        pat={e:f"high:{c}"for e,c in fails.items()if c>=2}
        upd=[]
        for d,(p,f) in s.c.route.items():
            if k.fail.get(p,0)>=3:
                s.c.route[d]=[f,p]
                upd.append(d)
        ctx="/home/keshanth/ARKA/ardhanarishvara/context/"
        clean=[]
        for f in os.listdir(ctx):
            p=os.path.join(ctx,f)
            if os.path.getsize(p)>50000:
                x=json.load(open(p))
                y={"summary":list(x)[:10]}
                json.dump(y,open(p,"w"),indent=2)
                clean.append(f)
        snap=s.c.p.agg()
        if sum(fails.values())==0:aut="FULL"
        elif sum(fails.values())>=10:aut="REV"
        elif sum(fails.values())>=5:aut="PART"
        else:aut="NO"
        return{"sum":summ,"pat":pat,"upd":upd,"clean":clean,"snap":snap,"aut":aut}

class AFX:
    def __init__(s,core):s.c=core
    def run(s):
        k=s.c.k
        L=json.load(open(k.ledger))
        issues=[]
        for e in L:
            r=e["r"]
            if"revenue_generated"not in r and"cycle_revenue"not in r:
                issues.append({"t":e["t"],"e":e["e"]})
        snap=s.c.p.agg()
        rel={e:{"f":c,"s":"bad"if c>=3 else"ok"}for e,c in k.fail.items()}
        rout=[]
        for d,(p,f) in s.c.route.items():
            if p==f:rout.append(d)
        wf=[]
        for d,(p,f) in s.c.route.items():
            pass
        ctx="/home/keshanth/ARKA/ardhanarishvara/context/"
        ciss=[f for f in os.listdir(ctx)if os.path.getsize(os.path.join(ctx,f))>100000]
        div=[]
        for e in L:
            r=e["r"]
            if"revenue_generated"not in r and"cycle_revenue"not in r:
                div.append(e)
        opt=[e for e,c in k.fail.items()if c>=3]
        st=s.c.a.state
        return{"fin":issues,"snap":snap,"rel":rel,"rout":rout,"ctx":ciss,"div":div,"opt":opt,"aut":st}
# === PART 3: SUPERVISORCORE + INTEGRATION (MAX-COMPRESSED) ===

class Core:
    def __init__(s):
        s.k=K()
        s.a=A(s.k)
        s.p=PFX(s.k)
        s.w=WFX(s)
        s.n=NFX(s)
        s.u=AFX(s)
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
        d=s.classify(i)
        r=s.exec_engine(d,i)
        s.k.log(d,"core",r)
        return r

core=Core()
def handle(i):return core.execute(i)
