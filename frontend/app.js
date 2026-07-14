const $ = (selector) => document.querySelector(selector);
const charts = {};
let summaryCache = null;

const sciPalette = ["#93C8ED", "#F7C1C1", "#AEDBD2", "#BC9CC8", "#D5E9C6", "#E4F0F7", "#D3DCF0", "#DE837D", "#A7C8F2", "#F4DDEB"];
const axisStyle = {
  axisLine: { lineStyle: { color: "#c8d5df" } },
  axisTick: { lineStyle: { color: "#c8d5df" } },
  axisLabel: { color: "#536575" },
  splitLine: { lineStyle: { color: "#e5edf3", type: "dashed" } },
};

async function getJson(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

function chart(id) {
  if (!charts[id]) charts[id] = echarts.init(document.getElementById(id));
  return charts[id];
}

function names(data) {
  return data.map((item) => item.name || item.year);
}

function counts(data, key = "count") {
  return data.map((item) => item[key]);
}

function renderDashboard(summary) {
  $("#mPapers").textContent = summary.total_papers.toLocaleString();
  $("#mAuthors").textContent = summary.total_authors.toLocaleString();
  $("#mKeywords").textContent = summary.total_keywords.toLocaleString();
  $("#mJournals").textContent = summary.total_journals.toLocaleString();
  $("#hotTopicText").textContent = summary.keyword_distribution.slice(0, 5).map((item) => item.name).join(" · ");
  $("#topSchoolText").textContent = summary.school_distribution.slice(0, 4).map((item) => item.name).join(" / ");

  chart("yearChart").setOption({
    animation: false,
    color: ["#93C8ED", "#F7C1C1"],
    backgroundColor: "#ffffff",
    tooltip: { trigger: "axis" },
    legend: { top: 8, textStyle: { color: "#536575" } },
    grid: { left: 50, right: 42, top: 58, bottom: 44 },
    xAxis: { type: "category", data: summary.year_distribution.map((item) => item.year), ...axisStyle },
    yAxis: [
      { type: "value", name: "论文", ...axisStyle },
      { type: "value", name: "被引", ...axisStyle },
    ],
    series: [
      {
        name: "发文量",
        type: "bar",
        data: counts(summary.year_distribution),
        barMaxWidth: 18,
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [{ offset: 0, color: "#93C8ED" }, { offset: 1, color: "#E4F0F7" }],
          },
        },
      },
      {
        name: "被引次数",
        type: "line",
        yAxisIndex: 1,
        smooth: true,
        symbol: "circle",
        symbolSize: 7,
        itemStyle: { borderColor: "#ffffff", borderWidth: 1.6 },
        lineStyle: { width: 2.2, color: "#F7C1C1" },
        data: counts(summary.citation_by_year, "citations"),
      },
    ],
  });

  chart("schoolChart").setOption({
    animation: false,
    color: ["#93C8ED"],
    tooltip: { trigger: "axis" },
    grid: { left: 126, right: 28, top: 30, bottom: 28 },
    xAxis: { type: "value", ...axisStyle },
    yAxis: { type: "category", data: names(summary.school_distribution.slice(0, 12)).reverse(), axisLabel: { width: 112, overflow: "truncate", color: "#536575" }, axisLine: { lineStyle: { color: "#c8d5df" } }, axisTick: { show: false } },
    series: [{
      type: "bar",
      data: counts(summary.school_distribution.slice(0, 12)).reverse(),
      barMaxWidth: 18,
      itemStyle: {
        borderRadius: [0, 4, 4, 0],
        color: {
          type: "linear",
          x: 0,
          y: 0,
          x2: 1,
          y2: 0,
          colorStops: [{ offset: 0, color: "#F7C1C1" }, { offset: 0.52, color: "#AEDBD2" }, { offset: 1, color: "#93C8ED" }],
        },
      },
    }],
  });
}

function renderAnalytics(summary) {
  chart("keywordChart").setOption({
    animation: false,
    color: ["#93C8ED"],
    tooltip: { trigger: "axis" },
    grid: { left: 146, right: 24, top: 24, bottom: 24 },
    xAxis: { type: "value", ...axisStyle },
    yAxis: { type: "category", data: names(summary.keyword_distribution.slice(0, 30)).reverse(), axisLabel: { width: 135, overflow: "truncate", color: "#536575" }, axisTick: { show: false } },
    series: [{ type: "bar", data: counts(summary.keyword_distribution.slice(0, 30)).reverse(), barMaxWidth: 13, itemStyle: { borderRadius: [0, 4, 4, 0], color: "#93C8ED" } }],
  });

  chart("journalChart").setOption({
    animation: false,
    color: ["#F7C1C1"],
    tooltip: { trigger: "axis" },
    grid: { left: 160, right: 24, top: 24, bottom: 24 },
    xAxis: { type: "value", ...axisStyle },
    yAxis: { type: "category", data: names(summary.journal_distribution.slice(0, 18)).reverse(), axisLabel: { width: 148, overflow: "truncate", color: "#536575" }, axisTick: { show: false } },
    series: [{ type: "bar", data: counts(summary.journal_distribution.slice(0, 18)).reverse(), barMaxWidth: 15, itemStyle: { borderRadius: [0, 4, 4, 0], color: "#F7C1C1" } }],
  });

  chart("categoryChart").setOption({
    animation: false,
    color: sciPalette,
    tooltip: { trigger: "item" },
    series: [{
      type: "pie",
      radius: ["42%", "72%"],
      center: ["50%", "52%"],
      data: summary.category_distribution.slice(0, 12).map((item) => ({ name: item.name, value: item.count })),
      itemStyle: { borderColor: "#fff", borderWidth: 2 },
      label: { overflow: "truncate", width: 130, color: "#536575" },
    }],
  });

  chart("coopChart").setOption({
    animation: false,
    color: ["#AEDBD2"],
    tooltip: { trigger: "axis" },
    grid: { left: 190, right: 24, top: 24, bottom: 24 },
    xAxis: { type: "value", ...axisStyle },
    yAxis: {
      type: "category",
      data: summary.cooperation_distribution.slice(0, 15).map((item) => `${item.source} - ${item.target}`).reverse(),
      axisLabel: { width: 178, overflow: "truncate", color: "#536575" },
      axisTick: { show: false },
    },
    series: [{ type: "bar", data: counts(summary.cooperation_distribution.slice(0, 15)).reverse(), barMaxWidth: 15, itemStyle: { borderRadius: [0, 4, 4, 0], color: "#AEDBD2" } }],
  });
}

function renderAuthor(profile) {
  const box = $("#authorResult");
  if (!profile || profile.found === false) {
    const candidates = profile?.candidates?.map((name) => `<span class="tag">${name}</span>`).join("") || "";
    box.innerHTML = `<div class="profile-box"><h2>未找到精确学者</h2><p>可尝试候选姓名。</p><div class="tag-cloud">${candidates}</div></div>`;
    return;
  }
  const tags = profile.top_keywords.map((item) => `<span class="tag">${item.name} ${item.count}</span>`).join("");
  const coauthors = profile.top_coauthors.map((item) => `<div class="result-item"><strong>${item.name}</strong><span>合作 ${item.count} 次</span></div>`).join("");
  const papers = profile.papers.map((paper) => `
    <div class="paper-item">
      <strong>${paper.title}</strong>
      <span>${paper.year || ""} · ${paper.journal || ""} · 被引 ${paper.times_cited}</span>
    </div>
  `).join("");
  box.innerHTML = `
    <div class="profile-box">
      <h2>${profile.author}</h2>
      <div class="stat-row">
        <div class="small-stat"><span>论文</span><strong>${profile.paper_count}</strong></div>
        <div class="small-stat"><span>被引</span><strong>${profile.citation_count}</strong></div>
        <div class="small-stat"><span>首篇年份</span><strong>${profile.first_year || "-"}</strong></div>
        <div class="small-stat"><span>学术年龄</span><strong>${profile.academic_age || "-"}</strong></div>
      </div>
      <div class="tag-cloud">${tags}</div>
      <h2 style="margin-top:18px">合作作者</h2>
      <div>${coauthors}</div>
    </div>
    <div class="paper-list">
      <h2>代表论文</h2>
      ${papers}
    </div>
  `;
}

async function loadAuthor() {
  const name = encodeURIComponent($("#authorInput").value.trim());
  if (!name) return;
  renderAuthor(await getJson(`/api/authors/${name}`));
}

async function renderGraph(view = "coauthor") {
  const data = await getJson(`/api/graph-preview?view=${encodeURIComponent(view)}&limit=80`);
  $("#graphTitle").textContent = data.title || "知识图谱展示";
  $("#graphDesc").textContent = data.description || "";
  $("#cypherBlock").textContent = data.cypher || "";
  chart("graphChart").setOption({
    animation: false,
    color: ["#93C8ED", "#F7C1C1", "#AEDBD2", "#BC9CC8", "#D5E9C6"],
    tooltip: {
      formatter: (params) => {
        if (params.dataType === "edge") return `${params.data.source} → ${params.data.target}<br/>${params.data.name || ""}`;
        return `${params.data.category}<br/>${params.data.name}`;
      },
    },
    legend: [{ data: data.categories || ["Author", "Paper", "Keyword", "School"], top: 8 }],
    series: [{
      type: "graph",
      layout: "force",
      roam: true,
      top: 44,
      force: { repulsion: view === "shortest_path" ? 420 : 120, edgeLength: view === "shortest_path" ? [120, 180] : [55, 150] },
      categories: (data.categories || ["Author", "Paper", "Keyword", "School"]).map((name) => ({ name })),
      data: data.nodes.map((node) => ({ ...node, symbolSize: Math.max(14, Math.min(54, Math.log2((node.value || 1) + 2) * 10)) })),
      links: data.links.map((link) => ({
        ...link,
        lineStyle: { width: Math.max(1, Math.min(6, Math.log2((link.value || 1) + 1))), opacity: 0.38 },
      })),
      label: { show: true, fontSize: 10, width: 90, overflow: "truncate" },
      edgeLabel: { show: false },
      lineStyle: { opacity: 0.35, color: "#b9c9d5" },
    }],
  });
}

function bindGraphTabs() {
  document.querySelectorAll(".graph-tab").forEach((button) => {
    button.addEventListener("click", async () => {
      document.querySelectorAll(".graph-tab").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      await renderGraph(button.dataset.graphView);
    });
  });
}

async function searchVector() {
  const q = encodeURIComponent($("#vectorInput").value.trim());
  if (!q) return;
  const data = await getJson(`/api/vector/papers?q=${q}&top_k=10`);
  $("#vectorEngine").textContent = `engine: ${data.engine}`;
  $("#vectorResults").innerHTML = data.results.map((item) => `
    <div class="result-item">
      <strong>${item.title}</strong>
      <span>相似度 ${item.score} · ${item.year || ""} · ${item.journal || ""}</span>
      <span>${item.keywords.join(" / ")}</span>
    </div>
  `).join("");
}

async function searchSimilarAuthor() {
  const name = encodeURIComponent($("#similarAuthorInput").value.trim());
  if (!name) return;
  const data = await getJson(`/api/vector/authors?name=${name}&top_k=10`);
  if (!data.found) {
    $("#similarAuthorResults").innerHTML = (data.candidates || []).map((name) => `<div class="result-item"><strong>${name}</strong><span>候选学者</span></div>`).join("");
    return;
  }
  $("#similarAuthorResults").innerHTML = data.results.map((item) => `
    <div class="result-item"><strong>${item.author}</strong><span>${item.score}</span></div>
  `).join("");
}

function bindNavigation() {
  document.querySelectorAll(".nav-btn").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".nav-btn").forEach((item) => item.classList.remove("active"));
      document.querySelectorAll(".page").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      document.getElementById(button.dataset.page).classList.add("active");
      setTimeout(() => Object.values(charts).forEach((item) => item.resize()), 60);
    });
  });
}

async function loadSummary() {
  summaryCache = await getJson("/api/summary");
  renderDashboard(summaryCache);
  renderAnalytics(summaryCache);
}

async function init() {
  bindNavigation();
  lucide.createIcons();
  await loadSummary();
  await loadAuthor();
  bindGraphTabs();
  await renderGraph("coauthor");
  await searchVector();
  await searchSimilarAuthor();
  $("#refreshBtn").addEventListener("click", loadSummary);
  $("#authorSearch").addEventListener("click", loadAuthor);
  $("#vectorSearch").addEventListener("click", searchVector);
  $("#similarAuthorSearch").addEventListener("click", searchSimilarAuthor);
  window.addEventListener("resize", () => Object.values(charts).forEach((item) => item.resize()));
}

init().catch((err) => {
  document.body.innerHTML = `<main class="main" style="margin:0"><h1>系统启动失败</h1><p>${err.message}</p></main>`;
});
