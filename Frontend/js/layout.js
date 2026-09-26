const NAV_CONFIG = {
  student: [
    { label: "Dashboard", href: "student-dashboard.html" },
    { label: "Profile", href: "profile.html" },
    { label: "Placement Drives", href: "student-drives.html" },
    { label: "Applications", href: "student-applications.html" },
    { label: "Interviews", href: "student-interviews.html" },
    { label: "Offers", href: "student-offers.html" },
    { label: "Notifications", href: "notifications.html" },
  ],
  recruiter: [
    { label: "Dashboard", href: "recruiter-dashboard.html" },
    { label: "Company Profile", href: "recruiter-company-profile.html" },
    { label: "Drives", href: "recruiter-drives.html" },
    { label: "Applicants", href: "recruiter-applicants.html" },
    { label: "Interviews", href: "recruiter-interviews.html" },
    { label: "Offers", href: "recruiter-offers.html" },
    { label: "Notifications", href: "notifications.html" },
  ],
  placement_officer: [
    { label: "Dashboard", href: "officer-dashboard.html" },
    { label: "Students", href: "officer-students.html" },
    { label: "Recruiters", href: "officer-recruiters.html" },
    { label: "Drives", href: "officer-drives.html" },
    { label: "Applications", href: "officer-applications.html" },
    { label: "Interviews", href: "officer-interviews.html" },
    { label: "Offers", href: "officer-offers.html" },
    { label: "Documents", href: "officer-documents.html" },
    { label: "Analytics", href: "officer-analytics.html" },
    { label: "Notifications", href: "notifications.html" },
  ],
};

/**
 * Renders the shared shell (sidebar + topbar) into #app-shell, and moves
 * the page's own content into the shell's main content area.
 * activePage: the href of the current page, used to highlight the nav link.
 */
function renderShell(user, activePage) {
  const shell = document.getElementById("app-shell");
  const pageContent = document.getElementById("page-content");
  const navItems = NAV_CONFIG[user.role] || [];

  const navHtml = navItems
    .map((item) => {
      const isNotifications = item.href === "notifications.html";
      const badge = isNotifications ? `<span id="unreadBadge" class="unread-badge" style="display:none;"></span>` : "";
      return `
        <a href="${item.href}" class="nav-link ${item.href === activePage ? "active" : ""}">
          ${item.label}${badge}
        </a>`;
    })
    .join("");

  shell.innerHTML = `
    <aside class="sidebar">
      <div class="sidebar-brand">CampusLink</div>
      <nav class="sidebar-nav">${navHtml}</nav>
      <div class="sidebar-settings">
        <a href="settings.html" class="nav-link ${activePage === "settings.html" ? "active" : ""}">Settings</a>
      </div>
    </aside>
    <div class="shell-main">
      <header class="topbar">
        <div class="topbar-role">${user.role.replace("_", " ")}</div>
        <div class="topbar-user">
          <span>${user.name}</span>
          <button id="logoutBtn" class="logout-btn">Logout</button>
        </div>
      </header>
      <main class="content-area" id="content-mount"></main>
    </div>
  `;

  document.getElementById("content-mount").appendChild(pageContent);
  pageContent.style.display = "block";
  document.getElementById("logoutBtn").addEventListener("click", logout);

  loadUnreadBadge();
}

async function loadUnreadBadge() {
  const badge = document.getElementById("unreadBadge");
  if (!badge) return;
  try {
    const res = await apiFetch("/api/notifications/unread-count");
    const count = res.data.count;
    if (count > 0) {
      badge.textContent = count;
      badge.style.display = "inline-block";
    }
  } catch (err) {
    // Non-fatal — badge just stays hidden
  }
}