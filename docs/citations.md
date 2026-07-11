# 引用・情報伝播グラフ

記事本文で確認できた引用・参照リンクを有向グラフとして表示します。矢印は「記事 → 参照先」を表します。ページ内のナビゲーション、広告、SNS共有、単なる製品リンクは除外します。

「未調査」と「調査済みだが引用なし」は区別しています。未調査の記事を、引用を持たない一次資料とは判定しません。

<style>
#cite-tools { display:flex; flex-wrap:wrap; gap:12px; align-items:center; margin:14px 0; }
#cite-tools select { padding:7px 10px; font:inherit; }
#cite-stage { position:relative; border:1px solid #d0d7de; border-radius:8px; }
#cite-canvas { width:100%; height:65vh; min-height:460px; display:block; }
#cite-card { position:absolute; top:12px; right:12px; width:270px; padding:12px; background:#fff; border:1px solid #d0d7de; border-radius:8px; display:none; font-size:13px; }
#cite-card.show { display:block; }
.cite-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:20px; margin-top:22px; }
.cite-panel { border:1px solid #d0d7de; border-radius:8px; padding:15px; }
.cite-panel h2 { font-size:17px; margin-top:0; }
.cite-panel ol { padding-left:22px; }
#cite-legend { font-size:12px; color:#57606a; }
</style>

<div id="cite-tools"><label>収集週: <select id="cite-week"></select></label><span id="cite-legend">青: 収集記事 / 灰: 外部参照先 / 破線: 背景・技術資料</span></div>
<div id="cite-stage"><canvas id="cite-canvas"></canvas><div id="cite-card"></div></div>
<div class="cite-grid">
  <section class="cite-panel"><h2>被引用数の多い記事</h2><ol id="most-cited"></ol></section>
  <section class="cite-panel"><h2>一次資料候補</h2><p>調査済みで、他記事から参照され、自身は外部記事を引用していない記事です。</p><ol id="root-candidates"></ol></section>
  <section class="cite-panel"><h2>循環引用</h2><div id="cycles"></div></section>
</div>

<script>
(function () {
  var cv=document.getElementById("cite-canvas"), ctx=cv.getContext("2d"), card=document.getElementById("cite-card"), select=document.getElementById("cite-week"), DATA;
  var W,H,nodes=[],edges=[],hovered=null;
  function esc(s){return String(s).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});}
  function weekStart(s){var d=new Date(s+"T00:00:00Z"), day=(d.getUTCDay()+6)%7;d.setUTCDate(d.getUTCDate()-day);return d.toISOString().slice(0,10);}
  function resize(){var r=cv.getBoundingClientRect(),dpr=window.devicePixelRatio||1;W=r.width;H=r.height;cv.width=W*dpr;cv.height=H*dpr;ctx.setTransform(dpr,0,0,dpr,0,0);layout();draw();}
  function layout(){var cx=W/2,cy=H/2,rad=Math.min(W,H)*0.35;nodes.forEach(function(n,i){var a=i/nodes.length*Math.PI*2;n.x=cx+Math.cos(a)*rad;n.y=cy+Math.sin(a)*rad;n.r=7+Math.sqrt(n.cited_by||0)*3;});}
  function drawArrow(a,b,e){var dx=b.x-a.x,dy=b.y-a.y,d=Math.sqrt(dx*dx+dy*dy)||1,ux=dx/d,uy=dy/d,ex=b.x-ux*(b.r+2),ey=b.y-uy*(b.r+2);ctx.strokeStyle=e.type==="reference"?"#8c959f":"#57606a";ctx.setLineDash(e.type==="reference"?[5,4]:[]);ctx.beginPath();ctx.moveTo(a.x+ux*a.r,a.y+uy*a.r);ctx.lineTo(ex,ey);ctx.stroke();ctx.setLineDash([]);ctx.fillStyle=ctx.strokeStyle;ctx.beginPath();ctx.moveTo(ex,ey);ctx.lineTo(ex-ux*9-uy*4,ey-uy*9+ux*4);ctx.lineTo(ex-ux*9+uy*4,ey-uy*9-ux*4);ctx.fill();}
  function draw(){ctx.clearRect(0,0,W,H);var by={};nodes.forEach(function(n){by[n.id]=n;});edges.forEach(function(e){if(by[e.source]&&by[e.target])drawArrow(by[e.source],by[e.target],e);});nodes.forEach(function(n){ctx.fillStyle=n.external?"#8c959f":"#0969da";ctx.beginPath();ctx.arc(n.x,n.y,n.r,0,Math.PI*2);ctx.fill();if(n===hovered){ctx.strokeStyle="#1f2328";ctx.lineWidth=2;ctx.stroke();}ctx.fillStyle="#1f2328";ctx.font="11px sans-serif";ctx.textAlign="center";ctx.fillText(n.title.slice(0,28),n.x,n.y+n.r+13);});}
  function show(n){if(!n){card.className="";return;}card.innerHTML='<b>'+esc(n.title)+'</b><p>'+esc(n.source)+'<br>被引用 '+n.cited_by+' / 参照 '+n.cites+'<br>引用調査: '+esc(n.scan_status)+'</p><a href="'+esc(n.url)+'">原文を開く</a>';card.className="show";}
  function list(id,values){document.getElementById(id).innerHTML=values.map(function(n){return '<li><a href="'+esc(n.url)+'">'+esc(n.title)+'</a> ('+n.cited_by+')</li>';}).join("")||"<li>該当なし</li>";}
  function filter(week){
    var selected=DATA.nodes.filter(function(n){return n.collected_at&&weekStart(n.collected_at)===week;}),ids={},incoming={},outgoing={};
    selected.forEach(function(n){ids[n.id]=1;});DATA.edges.forEach(function(e){if(ids[e.source])ids[e.target]=1;});
    nodes=DATA.nodes.filter(function(n){return ids[n.id];});edges=DATA.edges.filter(function(e){return ids[e.source]&&ids[e.target];});
    edges.forEach(function(e){incoming[e.target]=(incoming[e.target]||0)+1;outgoing[e.source]=(outgoing[e.source]||0)+1;});
    nodes.forEach(function(n){n.cited_by=incoming[n.id]||0;n.cites=outgoing[n.id]||0;});
    var ranked=nodes.filter(function(n){return n.cited_by;}).sort(function(a,b){return b.cited_by-a.cited_by;});
    list("most-cited",ranked.slice(0,10));
    list("root-candidates",ranked.filter(function(n){return n.scan_status==="scanned"&&!n.cites;}).slice(0,10));
    var cycles=DATA.cycles.filter(function(c){return c.every(function(id){return ids[id];});});
    var by={};nodes.forEach(function(n){by[n.id]=n;});document.getElementById("cycles").innerHTML=cycles.length?cycles.map(function(c){return '<p>'+c.map(function(v){return esc(by[v]?by[v].title:v);}).join(' → ')+'</p>';}).join(""):"循環引用は検出されていません。";
    layout();draw();
  }
  cv.addEventListener("mousemove",function(ev){var r=cv.getBoundingClientRect(),x=ev.clientX-r.left,y=ev.clientY-r.top,n=nodes.find(function(v){var dx=x-v.x,dy=y-v.y;return dx*dx+dy*dy<(v.r+6)*(v.r+6);});if(n!==hovered){hovered=n;show(n);draw();}});
  fetch("citation-graph.json").then(function(r){return r.json();}).then(function(data){DATA=data;var weeks=Array.from(new Set(data.nodes.filter(function(n){return n.collected_at;}).map(function(n){return weekStart(n.collected_at);}))).sort().reverse();weeks.forEach(function(w){var o=document.createElement("option");o.value=w;o.textContent=w;select.appendChild(o);});select.addEventListener("change",function(){filter(select.value);});if(weeks.length)filter(weeks[0]);resize();});
  window.addEventListener("resize",resize);
})();
</script>
