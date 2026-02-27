(function initSiteChrome() {
  const body = document.body;
  const base = body.getAttribute("data-base") || "./";
  const page = body.getAttribute("data-page") || "";

  const host = document.createElement("div");
  host.className = "site-shell";
  host.innerHTML = `
    <header class="site-header">
      <a class="site-brand" href="${base}">
        <svg class="site-logo" width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="2" y="2" width="28" height="28" stroke="currentColor" stroke-width="2" fill="none"/>
          <path d="M8 12 L16 8 L24 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M8 20 L16 16 L24 20" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M16 8 L16 24" stroke="currentColor" stroke-width="1.5" stroke-dasharray="2 2"/>
        </svg>
        <span>Application Intent Model</span>
      </a>
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