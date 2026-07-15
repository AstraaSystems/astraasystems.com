// Astraa shared site header — inject on every page except index
(function(){
  var css = ""
  + ".astraa-site-header{position:sticky;top:0;z-index:9999;background:rgba(255,255,255,0.85);backdrop-filter:blur(16px);border-bottom:1px solid #e2e8f0;width:100%;}"
  + ".astraa-site-nav{max-width:1200px;margin:0 auto;padding:14px 24px;display:flex;justify-content:space-between;align-items:center;gap:20px;width:100%;}"
  + ".astraa-site-brand{display:flex;align-items:center;gap:12px;font-weight:900;text-decoration:none;}"
  + ".astraa-site-brand img{width:34px;height:34px;object-fit:contain;}"
  + ".astraa-site-brand span{display:block;font-size:15px;color:#03050a;font-weight:800;}"
  + ".astraa-site-links{display:flex;align-items:center;gap:28px;color:#475569;font-size:14px;font-weight:600;}"
  + ".astraa-site-links a{transition:color .2s;text-decoration:none;color:#475569;}"
  + ".astraa-site-links a:hover{color:#1d4ed8;}"
  + ".astraa-site-links a.active{color:#1d4ed8;font-weight:800;}"
  + ".astraa-action-pack{display:flex;align-items:center;gap:14px;}"
  + ".astraa-space-btn{color:#475569;text-decoration:none;font-size:14px;font-weight:600;}"
  + ".astraa-space-btn:hover{color:#1d4ed8;}"
  + ".astraa-site-cta{background:#03050a;color:#fff;text-decoration:none;padding:9px 18px;border-radius:9px;font-size:14px;font-weight:800;}"
  + ".astraa-site-cta:hover{background:#1d4ed8;}"
  + "@media(max-width:900px){.astraa-site-links{display:none;}}";

  var page = (location.pathname.split("/").pop() || "index.html").toLowerCase();
  function act(f){ return page===f ? " class=\"active\"" : ""; }

  var html = ""
  + "'+LT+'header class=\"astraa-site-header\"'+GT+'"
  + "'+LT+'nav class=\"astraa-site-nav\"'+GT+'"
  + "'+LT+'a href=\"index.html\" class=\"astraa-site-brand\"'+GT+'"
  + "'+LT+'img src=\"assets/images/astraa_logo.png\" alt=\"Astraa Systems\" onerror=\"this.style.display=&#39;none&#39;\"/'+GT+'"
  + "'+LT+'span'+GT+'Astraa Systems'+LT+'/span'+GT+''+LT+'/a'+GT+'"
  + "'+LT+'div class=\"astraa-site-links\"'+GT+'"
  + "'+LT+'a href=\"index.html\"'+GT+'Home'+LT+'/a'+GT+'"
  + "'+LT+'a href=\"tools.html\""+act("tools.html")+"'+GT+'Tools'+LT+'/a'+GT+'"
  + "'+LT+'a href=\"pricing.html\""+act("pricing.html")+"'+GT+'Pricing'+LT+'/a'+GT+'"
  + "'+LT+'a href=\"faq.html\""+act("faq.html")+"'+GT+'FAQ / Support'+LT+'/a'+GT+'"
  + "'+LT+'a href=\"contact.html\""+act("contact.html")+"'+GT+'Custom Packages'+LT+'/a'+GT+'"
  + "'+LT+'/div'+GT+'"
  + "'+LT+'div class=\"astraa-action-pack\"'+GT+'"
  + "'+LT+'a href=\"astraaspace/login.html\" class=\"astraa-space-btn\"'+GT+'Astraa Space'+LT+'/a'+GT+'"
  + "'+LT+'a class=\"astraa-site-cta\" href=\"pricing.html\"'+GT+'Buy Now'+LT+'/a'+GT+'"
  + "'+LT+'/div'+GT+''+LT+'/nav'+GT+''+LT+'/header'+GT+'";

  var st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
  var wrap = document.createElement("div"); wrap.innerHTML = html;
  document.body.insertBefore(wrap.firstChild, document.body.firstChild);
})();