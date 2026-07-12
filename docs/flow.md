# 週間ニュースフロー

収集した記事を「情報源 → 用途領域 → 開発段階」の順に配置します。線は、その組み合わせに該当する記事が存在することを表し、太さは記事数です。

一つの記事が複数の用途領域を持つ場合は、それぞれに1本ずつ数えます。そのため、線の合計は記事総数と一致しない場合があります。

<style>
#flow-tools { margin: 16px 0; }
#flow-tools select { padding: 7px 10px; font: inherit; }
#flow-wrap { overflow-x: auto; border: 1px solid #d0d7de; border-radius: 8px; background: #fff; }
#flow-svg { display: block; width: 100%; min-width: 850px; height: 560px; }
.flow-link { fill: none; stroke: #8c959f; opacity: .32; cursor: pointer; }
.flow-link:hover, .flow-link.active { opacity: .8; stroke: #0969da; }
.flow-node { cursor: pointer; }
.flow-node rect { stroke: #fff; stroke-width: 2; rx: 7; }
.flow-node:hover rect, .flow-node.active rect { stroke: #1f2328; stroke-width: 3; }
.flow-node text { fill: #fff; font: 12px sans-serif; pointer-events: none; }
.flow-col-title { fill: #57606a; font: bold 14px sans-serif; }
#flow-detail { margin-top: 16px; border: 1px solid #d0d7de; border-radius: 8px; padding: 16px; min-height: 80px; }
#flow-detail h2 { font-size: 17px; margin-top: 0; }
#flow-detail li { margin: 9px 0; }
</style>

<div id="flow-tools"><label>収集週: <select id="flow-week"></select></label></div>
<div id="flow-wrap"><svg id="flow-svg" viewBox="0 0 1000 560" role="img" aria-label="情報源から用途領域、開発段階への週間ニュースフロー"></svg></div>
<section id="flow-detail"><h2>ノードまたは線を選択してください</h2><p>該当する記事をここに固定表示します。</p></section>

<script>
(function () {
  var NS="http://www.w3.org/2000/svg", svg=document.getElementById("flow-svg"), select=document.getElementById("flow-week"), detail=document.getElementById("flow-detail"), DATA;
  var COLORS={source:"#0969da",domain:"#8250df",status:"#1a7f37"}, X={source:55,domain:405,status:755}, WIDTH=190;
  function esc(s){return String(s).replace(/[&<>"']/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});}
  function el(name,attrs){var n=document.createElementNS(NS,name);Object.keys(attrs||{}).forEach(function(k){n.setAttribute(k,attrs[k]);});return n;}
  function show(title,ids,articles){var by={};articles.forEach(function(a){by[a.id]=a;});detail.innerHTML='<h2>'+esc(title)+'</h2><ul>'+ids.map(function(id){var a=by[id];return '<li><a href="'+esc(a.url)+'" target="_blank" rel="noopener noreferrer">'+esc(a.title)+'</a><br><small>'+esc(a.date)+' — '+esc(a.summary)+'</small></li>';}).join('')+'</ul>';}
  function layout(nodes,kind){var list=nodes.filter(function(n){return n.kind===kind;}).sort(function(a,b){return b.value-a.value||a.label.localeCompare(b.label);}),gap=18,top=65,available=455,total=list.reduce(function(s,n){return s+Math.max(38,26+n.value*7);},0)+gap*Math.max(0,list.length-1),scale=Math.min(1,available/Math.max(total,1)),y=top;list.forEach(function(n){n.h=Math.max(32,(26+n.value*7)*scale);n.x=X[kind];n.y=y;y+=n.h+gap;});}
  function render(week){
    while(svg.firstChild)svg.removeChild(svg.firstChild);var nodes=week.nodes.map(function(n){return Object.assign({},n);}),by={};nodes.forEach(function(n){by[n.id]=n;});["source","domain","status"].forEach(function(k){layout(nodes,k);});
    [["source","情報源"],["domain","用途領域"],["status","開発段階"]].forEach(function(x){var t=el("text",{x:X[x[0]],y:32,class:"flow-col-title"});t.textContent=x[1];svg.appendChild(t);});
    week.links.forEach(function(link){var a=by[link.source],b=by[link.target],path=el("path",{d:"M "+(a.x+WIDTH)+" "+(a.y+a.h/2)+" C "+(a.x+WIDTH+90)+" "+(a.y+a.h/2)+", "+(b.x-90)+" "+(b.y+b.h/2)+", "+b.x+" "+(b.y+b.h/2),class:"flow-link","stroke-width":Math.max(3,link.value*7)});path.addEventListener("click",function(){svg.querySelectorAll(".active").forEach(function(n){n.classList.remove("active");});path.classList.add("active");show(by[link.source].label+" → "+by[link.target].label,link.articles,week.articles);});svg.appendChild(path);});
    nodes.forEach(function(n){var g=el("g",{class:"flow-node"}),r=el("rect",{x:n.x,y:n.y,width:WIDTH,height:n.h,fill:COLORS[n.kind]}),t=el("text",{x:n.x+10,y:n.y+n.h/2+4});t.textContent=(n.label.length>24?n.label.slice(0,23)+"…":n.label)+"  "+n.value;g.appendChild(r);g.appendChild(t);g.addEventListener("click",function(){svg.querySelectorAll(".active").forEach(function(x){x.classList.remove("active");});g.classList.add("active");show(n.group+": "+n.label,n.articles,week.articles);});svg.appendChild(g);});
    detail.innerHTML='<h2>'+esc(week.start+' 〜 '+week.end)+'</h2><p>'+week.articles.length+'件の記事を表示しています。ノードまたは線をクリックすると、該当記事を確認できます。</p>';
  }
  fetch("weekly-flow.json").then(function(r){return r.json();}).then(function(data){DATA=data;data.weeks.forEach(function(w,i){var o=document.createElement("option");o.value=i;o.textContent=w.start+" 〜 "+w.end;select.appendChild(o);});select.addEventListener("change",function(){render(data.weeks[Number(select.value)]);});if(data.weeks.length)render(data.weeks[0]);});
})();
</script>
