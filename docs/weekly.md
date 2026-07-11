# 週間ダッシュボード

収集日を基準に、1週間の追加件数、カテゴリ構成、開発段階、情報源、新規エンティティを表示します。記事の発表日ではなく、このWikiへ取り込んだ日を集計に使います。

<style>
.week-controls { margin: 16px 0; }
.week-controls select { padding: 7px 10px; font: inherit; }
.metric-grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(150px,1fr)); gap: 12px; margin: 16px 0 24px; }
.metric { border: 1px solid #d0d7de; border-radius: 8px; padding: 14px; }
.metric b { display: block; font-size: 25px; margin-top: 4px; }
.dash-grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(280px,1fr)); gap: 22px; }
.panel { border: 1px solid #d0d7de; border-radius: 8px; padding: 16px; }
.panel h2 { font-size: 17px; margin-top: 0; }
.bar-row { display: grid; grid-template-columns: minmax(100px,1fr) 3fr 35px; gap: 8px; align-items: center; margin: 7px 0; font-size: 13px; }
.bar-track { height: 12px; background: #f0f2f4; border-radius: 6px; overflow: hidden; }
.bar { height: 100%; background: #0969da; border-radius: 6px; }
.new-group { margin: 10px 0; }
.new-group b { display: block; font-size: 13px; }
.tag { display: inline-block; margin: 4px 4px 0 0; padding: 2px 7px; border-radius: 999px; background: #ddf4ff; font-size: 12px; }
</style>

<div class="week-controls"><label>対象週: <select id="week-select"></select></label></div>
<div id="week-metrics" class="metric-grid"></div>
<div class="dash-grid">
  <section class="panel"><h2>用途領域</h2><div id="domain-chart"></div></section>
  <section class="panel"><h2>開発・公開段階</h2><div id="status-chart"></div></section>
  <section class="panel"><h2>情報源種別</h2><div id="source-chart"></div></section>
  <section class="panel"><h2>頻出トピック</h2><div id="topic-chart"></div></section>
  <section class="panel"><h2>日別の収集数</h2><div id="daily-chart"></div></section>
  <section class="panel"><h2>今週初登場した項目</h2><div id="new-entities"></div></section>
</div>

<script>
(function () {
  var LABELS = { domains: "用途領域", companies: "企業", programs: "プログラム", aircraft: "機体", models: "世界モデル", simulators: "シミュレータ", topics: "トピック" };
  var select = document.getElementById("week-select");
  function esc(s) { return String(s).replace(/[&<>"']/g, function(c) { return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]; }); }
  function bars(id, values, limit) {
    var rows = Object.entries(values || {}).slice(0, limit || 20), max = Math.max.apply(null, rows.map(function(x){return x[1];}).concat([1]));
    document.getElementById(id).innerHTML = rows.length ? rows.map(function(x) {
      return '<div class="bar-row"><span>' + esc(x[0]) + '</span><div class="bar-track"><div class="bar" style="width:' + (x[1] / max * 100) + '%"></div></div><b>' + x[1] + '</b></div>';
    }).join("") : "該当なし";
  }
  function render(w) {
    var rate = w.count ? Math.round(w.primary / w.count * 100) : 0;
    document.getElementById("week-metrics").innerHTML = [
      ["新規記事", w.count + "件"], ["前週比", (w.change >= 0 ? "+" : "") + w.change],
      ["一次情報", rate + "%"], ["情報源", w.sources + "件"]
    ].map(function(x){ return '<div class="metric">' + x[0] + '<b>' + x[1] + '</b></div>'; }).join("");
    bars("domain-chart", w.domains); bars("status-chart", w.statuses); bars("source-chart", w.source_types);
    bars("topic-chart", w.topics, 12); bars("daily-chart", w.daily);
    var html = Object.entries(w.new_entities).map(function(x) {
      if (!x[1].length) return "";
      return '<div class="new-group"><b>' + esc(LABELS[x[0]] || x[0]) + '</b>' + x[1].map(function(v){return '<span class="tag">' + esc(v) + '</span>';}).join("") + '</div>';
    }).join("");
    document.getElementById("new-entities").innerHTML = html || "初登場項目なし";
  }
  fetch("weekly.json").then(function(r){return r.json();}).then(function(data){
    data.weeks.forEach(function(w, i){ var o=document.createElement("option"); o.value=i; o.textContent=w.start + " 〜 " + w.end; select.appendChild(o); });
    select.addEventListener("change", function(){render(data.weeks[Number(select.value)]);});
    if (data.weeks.length) render(data.weeks[0]);
  });
})();
</script>
