(function initSiteChrome() {
  const body = document.body;
  const base = body.getAttribute("data-base") || "./";
  const page = body.getAttribute("data-page") || "";

  const host = document.createElement("div");
  host.className = "site-shell";
  host.innerHTML = `
    <header class="site-header">
      <a class="site-brand" href="${base}">Application Intent Model</a>
      <nav class="site-nav" aria-label="Primary">
        <a data-nav="home" href="${base}">Home</a>
        <a data-nav="spec" href="${base}spec/">Specification</a>
        <a data-nav="registry" href="${base}registry/">Registry</a>
        <a data-nav="publish" href="${base}registry/publish.html">Publish</a>
      </nav>
    </header>
    <main class="content" id="content-root"></main>
  `;

  while (body.firstChild) {
    host.querySelector("#content-root").appendChild(body.firstChild);
  }
  body.appendChild(host);

  const active = host.querySelector(`[data-nav="${page}"]`);
  if (active) {
    active.classList.add("active");
  }
})();
