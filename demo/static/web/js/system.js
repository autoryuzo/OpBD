window.WebUI = (() => {
  const pages = document.querySelectorAll(".page");
  const sidebarButtons = document.querySelectorAll(".sidebar button");

  function showPage(pageId) {
    pages.forEach(p => p.classList.remove("active"));
    document.getElementById(pageId).classList.add("active");
    document.getElementById("current_page_title").textContent = document.querySelector(`button[data-page="${pageId}"]`).textContent;
  }

  sidebarButtons.forEach(btn => {
    btn.addEventListener("click", () => showPage(btn.dataset.page));
  });

  return { showPage };
})();