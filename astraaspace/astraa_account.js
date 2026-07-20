// Astraa Space — Account dropdown (profile, billing, change card, cancel, reset key)
(function(){
  "use strict";
  var API = (typeof ASTRAA_API_BASE!=='undefined')?ASTRAA_API_BASE:(window.ASTRAA_API_BASE||"");
  function H(){return {"Content-Type":"application/json","ngrok-skip-browser-warning":"true"};}
  function sess(){try{return JSON.parse(localStorage.getItem('astraa_session')||'{}');}catch(e){return {};}}
  function email(){return (sess().email||"").trim();}

  var HT_ORIGIN="https://www3.moneris.com", HT_TARGET="https://www3.moneris.com/HPPtoken/index.php";

  function prettyProduct(p){
    var m={estimator_basic:"Estimator · Basic",estimator_pro:"Estimator · Professional",
      business_basic:"Business · Basic",business_pro:"Business · Professional",
      finance_basic:"Finance · Basic",finance_pro:"Finance · Professional",
      essentials:"Astraa Essentials",professional_suite:"Astraa Professional Suite"};
    return m[p]||p||"—";
  }

  function injectStyles(){
    if(document.getElementById('astraa-acct-css')) return;
    var s=document.createElement('style'); s.id='astraa-acct-css';
    s.textContent=`
      #acct-wrap{position:relative;}
      #acct-btn{display:flex;align-items:center;gap:7px;padding:9px 14px;border-radius:10px;
        border:1px solid #e2e8f0;background:#f8fafc;color:#0f172a;font-size:0.9rem;font-weight:700;cursor:pointer;}
      #acct-btn:hover{border-color:#1d4ed8;}
      #acct-panel{position:absolute;right:0;top:48px;width:300px;background:#fff;border:1px solid #e2e8f0;
        border-radius:14px;box-shadow:0 12px 34px rgba(15,23,42,.14);padding:16px;z-index:100;display:none;}
      #acct-panel.open{display:block;}
      #acct-panel .em{font-size:.8rem;color:#64748b;word-break:break-all;margin-bottom:10px;}
      #acct-panel .plan{background:#f8fafc;border:1px solid #eef2f7;border-radius:10px;padding:12px;margin-bottom:12px;}
      #acct-panel .plan .name{font-weight:800;color:#0f172a;font-size:.95rem;}
      #acct-panel .plan .meta{font-size:.8rem;color:#64748b;margin-top:3px;}
      #acct-panel .badge{display:inline-block;padding:2px 9px;border-radius:999px;font-size:.72rem;font-weight:800;margin-top:6px;}
      #acct-panel .badge.active{background:#e7f6ee;color:#128a5b;}
      #acct-panel .badge.canceled{background:#fdeaed;color:#c8324a;}
      #acct-panel .badge.past_due{background:#fdf3e3;color:#b7791f;}
      #acct-panel .item{width:100%;text-align:left;background:none;border:0;padding:10px 8px;border-radius:8px;
        font-size:.88rem;font-weight:600;color:#0f172a;cursor:pointer;display:flex;gap:8px;align-items:center;}
      #acct-panel .item:hover{background:#f1f5f9;}
      #acct-panel .item.danger{color:#c8324a;}
      #acct-msg{font-size:.8rem;margin-top:8px;padding:8px 10px;border-radius:8px;display:none;}
      #acct-msg.ok{display:block;background:#e7f6ee;color:#128a5b;}
      #acct-msg.err{display:block;background:#fdeaed;color:#c8324a;}
      #acct-msg.info{display:block;background:#eef3fd;color:#173f9e;}
      .acct-modal-bg{position:fixed;inset:0;background:rgba(15,23,42,.5);z-index:200;display:none;align-items:center;justify-content:center;}
      .acct-modal-bg.open{display:flex;}
      .acct-modal{background:#fff;border-radius:16px;padding:24px;width:440px;max-width:92vw;}
      .acct-modal h3{margin:0 0 4px;color:#0f172a;font-size:1.15rem;}
      .acct-modal p.sub{color:#64748b;font-size:.85rem;margin:0 0 16px;}
      #acctFrame{width:100%;height:300px;border:1px solid #e2e8f0;border-radius:10px;}
      .acct-modal .mbtn{width:100%;padding:12px;border:0;border-radius:10px;font-weight:700;font-size:.95rem;cursor:pointer;margin-top:12px;}
      .acct-modal .mbtn.primary{background:#1d4ed8;color:#fff;}
      .acct-modal .mbtn.link{background:none;color:#1d4ed8;text-decoration:underline;}
      .acct-spin{display:inline-block;width:13px;height:13px;border:2px solid rgba(29,78,216,.3);border-top-color:#1d4ed8;border-radius:50%;animation:acsp .7s linear infinite;vertical-align:-2px;margin-right:6px;}
      @keyframes acsp{to{transform:rotate(360deg);}}
    `;
    document.head.appendChild(s);
  }

  function msg(type,txt){var m=document.getElementById('acct-msg');m.className=type;m.innerHTML=txt;}

  function buildUI(){
    injectStyles();
    var right=document.querySelector('#astraa-topbar .right');
    if(!right||document.getElementById('acct-wrap')) return;

    var wrap=document.createElement('div'); wrap.id='acct-wrap';
    wrap.innerHTML=
      '<button id="acct-btn">👤 Account ▾</button>'+
      '<div id="acct-panel">'+
        '<div class="em" id="acct-email"></div>'+
        '<div class="plan" id="acct-plan"><div class="name">Loading…</div></div>'+
        '<button class="item" id="acct-change">💳 Change payment method</button>'+
        '<button class="item" id="acct-reset">🔑 Reset access key</button>'+
        '<button class="item danger" id="acct-cancel">❌ Cancel subscription</button>'+
        '<div id="acct-msg"></div>'+
      '</div>';
    // insert before logout button
    var logout=document.getElementById('logout-btn');
    right.insertBefore(wrap, logout);

    // modal for card change
    var modal=document.createElement('div'); modal.className='acct-modal-bg'; modal.id='acct-modal';
    modal.innerHTML=
      '<div class="acct-modal">'+
        '<h3>Update payment method</h3>'+
        '<p class="sub">Enter your new card. Astraa never sees or stores your card number.</p>'+
        '<iframe id="acctFrame" title="Secure card entry" frameborder="0"></iframe>'+
        '<button class="mbtn primary" id="acctSaveCard" disabled>Loading secure form…</button>'+
        '<button class="mbtn link" id="acctCloseModal">Cancel</button>'+
        '<div id="acct-modal-msg" style="font-size:.8rem;margin-top:10px;"></div>'+
      '</div>';
    document.body.appendChild(modal);

    wire();
    loadStatus();
  }

  function wire(){
    var btn=document.getElementById('acct-btn'), panel=document.getElementById('acct-panel');
    btn.onclick=function(e){e.stopPropagation();panel.classList.toggle('open');};
    document.addEventListener('click',function(e){
      if(!document.getElementById('acct-wrap').contains(e.target)) panel.classList.remove('open');
    });
    document.getElementById('acct-change').onclick=openCardModal;
    document.getElementById('acct-cancel').onclick=doCancel;
    document.getElementById('acct-reset').onclick=doResetKey;
    document.getElementById('acctCloseModal').onclick=function(){document.getElementById('acct-modal').classList.remove('open');};
    document.getElementById('acctSaveCard').onclick=function(){
      document.getElementById('acct-modal-msg').innerHTML='<span class="acct-spin"></span>Securing card…';
      this.disabled=true; this.textContent="Processing…";
      document.getElementById('acctFrame').contentWindow.postMessage("tokenize",HT_TARGET);
    };
    window.addEventListener("message",function(ev){
      if(ev.origin.indexOf("moneris.com")<0) return;
      var d; try{d=(typeof ev.data==="string")?JSON.parse(ev.data):ev.data;}catch(e){try{d=eval("("+ev.data+")");}catch(e2){return;}}
      if(!d) return;
      var rc=d.responseCode; if(Array.isArray(rc))rc=rc[0]; rc=String(rc);
      if((rc==="1"||rc==="001")&&d.dataKey){ saveCard(d.dataKey); }
      else { var b=document.getElementById('acctSaveCard'); b.disabled=false; b.textContent="Save new card";
             document.getElementById('acct-modal-msg').innerHTML='❌ '+(d.errorMessage||"Card error. Check details."); }
    },false);
  }

  function loadStatus(){
    document.getElementById('acct-email').innerText=email();
    fetch(API+"/api/subscription/status",{method:"POST",headers:H(),body:JSON.stringify({email:email()})})
      .then(function(r){return r.json();})
      .then(function(d){
        var el=document.getElementById('acct-plan');
        if(d.ok&&d.found){
          var sc=d.status==="active"?"active":(d.status==="canceled"?"canceled":"past_due");
          el.innerHTML='<div class="name">'+prettyProduct(d.product)+'</div>'+
            '<div class="meta">$'+Number(d.amount).toFixed(2)+' '+(d.currency||'CAD')+'/mo · Next: '+(d.next_bill_date||'—')+'</div>'+
            '<span class="badge '+sc+'">'+d.status+'</span>';
          if(d.status==="canceled"){
            document.getElementById('acct-cancel').style.display='none';
          }
        } else {
          el.innerHTML='<div class="name">No active subscription</div><div class="meta">Visit Pricing to subscribe.</div>';
          document.getElementById('acct-change').style.display='none';
          document.getElementById('acct-cancel').style.display='none';
        }
      })
      .catch(function(){document.getElementById('acct-plan').innerHTML='<div class="name">Could not load plan</div>';});
  }

  function openCardModal(){
    document.getElementById('acct-panel').classList.remove('open');
    var modal=document.getElementById('acct-modal'); modal.classList.add('open');
    document.getElementById('acct-modal-msg').innerHTML='';
    fetch(API+"/api/moneris/ht-config",{headers:{"ngrok-skip-browser-warning":"true"}})
      .then(function(r){return r.json();})
      .then(function(cfg){
        if(!cfg.ok||!cfg.profileId) throw new Error("HT not configured");
        HT_TARGET=cfg.iframeBase; HT_ORIGIN=cfg.env==="production"?"https://www3.moneris.com":"https://esqa.moneris.com";
        document.getElementById('acctFrame').src=cfg.iframeBase+"?id="+encodeURIComponent(cfg.profileId)+"&pmmsg=true&enable_exp=1&enable_cvd=1&display_labels=1&css_body=font-family:sans-serif;margin:8px;&css_textbox=border:1px solid %23ccc;border-radius:6px;padding:10px;font-size:15px;width:90%25;margin:6px 0;&css_input_label=display:block;font-size:12px;color:%230b1f3a;margin-top:8px;";
        document.getElementById('acctFrame').onload=function(){var b=document.getElementById('acctSaveCard');b.disabled=false;b.textContent="Save new card";};
      })
      .catch(function(e){document.getElementById('acct-modal-msg').innerHTML='Could not load form. '+(e.message||'');});
  }

  function saveCard(token){
    document.getElementById('acct-modal-msg').innerHTML='<span class="acct-spin"></span>Updating…';
    fetch(API+"/api/subscription/change-card",{method:"POST",headers:H(),body:JSON.stringify({email:email(),temp_token:token})})
      .then(function(r){return r.json();})
      .then(function(d){
        if(d.ok){
          document.getElementById('acct-modal-msg').innerHTML='✅ '+(d.message||"Card updated!");
          setTimeout(function(){document.getElementById('acct-modal').classList.remove('open');loadStatus();},1400);
        } else {
          var b=document.getElementById('acctSaveCard');b.disabled=false;b.textContent="Save new card";
          document.getElementById('acct-modal-msg').innerHTML='❌ '+(d.error&&d.error.error||d.error||"Update failed.");
        }
      })
      .catch(function(e){document.getElementById('acct-modal-msg').innerHTML='Error: '+(e.message||'');});
  }

  function doCancel(){
    if(!confirm("Cancel your subscription? You'll keep access until your paid period ends.")) return;
    msg('info','<span class="acct-spin"></span>Canceling…');
    fetch(API+"/api/subscription/cancel",{method:"POST",headers:H(),body:JSON.stringify({email:email()})})
      .then(function(r){return r.json();})
      .then(function(d){
        if(d.ok){ msg('ok','✅ '+(d.message||'Canceled.')); loadStatus(); }
        else { msg('err', d.error||'Cancel failed.'); }
      })
      .catch(function(e){msg('err','Error: '+(e.message||''));});
  }

  function doResetKey(){
    msg('info','To reset your access key, email support@astraasystems.com from your account email. We\'ll verify and reset it.');
  }

  if(document.readyState==="loading") document.addEventListener('DOMContentLoaded',buildUI);
  else buildUI();
})();
