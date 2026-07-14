const $ = (selector) => document.querySelector(selector);
const charts = {};
let summaryCache = null;
const loadedPages = new Set(["dashboard", "analytics"]);

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

function setSearchState(target, message, type = "loading") {
  target.innerHTML = `<div class="search-state ${type}">${message}</div>`;
}

function setButtonBusy(button, busy, busyText = "查询中") {
  const label = button.querySelector("span");
  if (busy) {
    button.dataset.label = label.textContent;
    label.textContent = busyText;
  } else if (button.dataset.label) {
    label.textContent = button.dataset.label;
  }
  button.disabled = busy;
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
  const rawName = $("#authorInput").value.trim();
  const button = $("#authorSearch");
  const target = $("#authorResult");
  if (!rawName) {
    setSearchState(target, "请输入学者姓名后再查询。", "error");
    return;
  }
  setButtonBusy(button, true, "查询中");
  setSearchState(target, `正在查询 ${rawName} 的学者画像...`);
  try {
    renderAuthor(await getJson(`/api/authors/${encodeURIComponent(rawName)}`));
  } catch (error) {
    setSearchState(target, "学者查询失败，请稍后重试。", "error");
  } finally {
    setButtonBusy(button, false);
  }
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
  const rawQuery = $("#vectorInput").value.trim();
  const button = $("#vectorSearch");
  const target = $("#vectorResults");
  if (!rawQuery) {
    setSearchState(target, "请输入论文主题或关键词后再检索。", "error");
    return;
  }
  setButtonBusy(button, true, "检索中");
  setSearchState(target, "正在计算论文语义相似度...");
  try {
    const data = await getJson(`/api/vector/papers?q=${encodeURIComponent(rawQuery)}&top_k=10`);
    $("#vectorEngine").textContent = `engine: ${data.engine}`;
    target.innerHTML = data.results.length ? data.results.map((item) => `
      <div class="result-item">
        <strong>${item.title}</strong>
        <span>相似度 ${item.score} · ${item.year || ""} · ${item.journal || ""}</span>
        <span>${item.keywords.join(" / ")}</span>
      </div>
    `).join("") : `<div class="search-state">没有找到相关论文，请更换关键词。</div>`;
  } catch (error) {
    setSearchState(target, "论文检索失败，请稍后重试。", "error");
  } finally {
    setButtonBusy(button, false);
  }
}

async function searchSimilarAuthor() {
  const rawName = $("#similarAuthorInput").value.trim();
  const button = $("#similarAuthorSearch");
  const target = $("#similarAuthorResults");
  if (!rawName) {
    setSearchState(target, "请输入学者姓名后再检索。", "error");
    return;
  }
  setButtonBusy(button, true, "检索中");
  setSearchState(target, "正在构建作者研究画像并计算相似度...");
  try {
    const data = await getJson(`/api/vector/authors?name=${encodeURIComponent(rawName)}&top_k=10`);
    if (!data.found) {
      target.innerHTML = (data.candidates || []).length
        ? data.candidates.map((name) => `<div class="result-item"><strong>${name}</strong><span>候选学者</span></div>`).join("")
        : `<div class="search-state">未找到该学者，请输入数据中的完整英文姓名。</div>`;
      return;
    }
    target.innerHTML = data.results.map((item) => `
      <div class="result-item"><strong>${item.author}</strong><span>相似度 ${item.score}</span></div>
    `).join("");
  } catch (error) {
    setSearchState(target, "相似学者检索失败，请稍后重试。", "error");
  } finally {
    setButtonBusy(button, false);
  }
}

function bindNavigation() {
  document.querySelectorAll(".nav-btn").forEach((button) => {
    button.addEventListener("click", async () => {
      document.querySelectorAll(".nav-btn").forEach((item) => item.classList.remove("active"));
      document.querySelectorAll(".page").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      const page = button.dataset.page;
      document.getElementById(page).classList.add("active");
      if (!loadedPages.has(page)) {
        loadedPages.add(page);
        if (page === "author") await loadAuthor();
        if (page === "graph") await renderGraph("coauthor");
        if (page === "vector") {
          await searchVector();
          await searchSimilarAuthor();
        }
      }
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
  bindGraphTabs();
  $("#refreshBtn").addEventListener("click", loadSummary);
  $("#authorSearchForm").addEventListener("submit", (event) => {
    event.preventDefault();
    loadAuthor();
  });
  $("#vectorSearchForm").addEventListener("submit", (event) => {
    event.preventDefault();
    searchVector();
  });
  $("#similarAuthorSearchForm").addEventListener("submit", (event) => {
    event.preventDefault();
    searchSimilarAuthor();
  });
  window.addEventListener("resize", () => Object.values(charts).forEach((item) => item.resize()));
}

init().catch((err) => {
  document.body.innerHTML = `<main class="main" style="margin:0"><h1>系统启动失败</h1><p>${err.message}</p></main>`;
});
