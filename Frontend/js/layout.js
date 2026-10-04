const NAV_CONFIG = {
  student: [
    { label: "Dashboard", href: "student-dashboard.html", icon: "⌂" },
    { label: "Profile", href: "profile.html", icon: "👤" },
    { label: "Placement Drives", href: "student-drives.html", icon: "▣" },
    { label: "Applications", href: "student-applications.html", icon: "🗂" },
    { label: "Interviews", href: "student-interviews.html", icon: "🎤" },
    { label: "Offers", href: "student-offers.html", icon: "🎁" },
    { label: "Notifications", href: "notifications.html", icon: "🔔" },
  ],

  recruiter: [
    { label: "Dashboard", href: "recruiter-dashboard.html", icon: "⌂" },
    { label: "Company Profile", href: "recruiter-company-profile.html", icon: "🏢" },
    { label: "Drives", href: "recruiter-drives.html", icon: "📋" },
    { label: "Applicants", href: "recruiter-applicants.html", icon: "👥" },
    { label: "Interviews", href: "recruiter-interviews.html", icon: "🎤" },
    { label: "Offers", href: "recruiter-offers.html", icon: "🎁" },
    { label: "Documents", href: "recruiter-documents.html", icon: "📄" },
    { label: "Notifications", href: "notifications.html", icon: "🔔" },
  ],

  placement_officer: [
    { label: "Dashboard", href: "officer-dashboard.html", icon: "⌂" },
    { label: "Students", href: "officer-students.html", icon: "🎓" },
    { label: "Recruiters", href: "officer-recruiters.html", icon: "🏢" },
    { label: "Drives", href: "officer-drives.html", icon: "📋" },
    { label: "Applications", href: "officer-applications.html", icon: "🗂" },
    { label: "Interviews", href: "officer-interviews.html", icon: "🎤" },
    { label: "Offers", href: "officer-offers.html", icon: "🎁" },
    { label: "Documents", href: "officer-documents.html", icon: "📄" },
    { label: "Analytics", href: "officer-analytics.html", icon: "📈" },
    { label: "Notifications", href: "notifications.html", icon: "🔔" },
  ],
};

function getTopbarMeta(activePage) {
  const metaMap = {
    "student-dashboard.html": {
      label: "Dashboard",
      subtitle: "Placement overview",
    },
    "profile.html": {
      label: "Profile",
      subtitle: "Student profile",
    },
    "student-drives.html": {
      label: "Placement Drives",
      subtitle: "Open opportunities",
    },
    "student-applications.html": {
      label: "Applications",
      subtitle: "My applications",
    },
    "student-interviews.html": {
      label: "Interviews",
      subtitle: "Upcoming interviews",
    },
    "student-offers.html": {
      label: "Offers",
      subtitle: "Offer pipeline",
    },
    "notifications.html": {
      label: "Notifications",
      subtitle: "Latest updates",
    },

    "recruiter-dashboard.html": {
      label: "Dashboard",
      subtitle: "Hiring overview",
    },
    "recruiter-company-profile.html": {
      label: "Company Profile",
      subtitle: "Organization profile",
    },
    "recruiter-drives.html": {
      label: "Drives",
      subtitle: "Drive pipeline",
    },
    "recruiter-applicants.html": {
      label: "Applicants",
      subtitle: "Candidate pipeline",
    },
    "recruiter-interviews.html": {
      label: "Interviews",
      subtitle: "Interview schedule",
    },
    "recruiter-offers.html": {
      label: "Offers",
      subtitle: "Offer management",
    },
    "recruiter-documents.html": {
      label: "Documents",
      subtitle: "Candidate documents",
    },

    "officer-dashboard.html": {
      label: "Dashboard",
      subtitle: "Operations overview",
    },
    "officer-students.html": {
      label: "Students",
      subtitle: "Student records",
    },
    "officer-recruiters.html": {
      label: "Recruiters",
      subtitle: "Partner network",
    },
    "officer-drives.html": {
      label: "Drives",
      subtitle: "Drive monitoring",
    },
    "officer-applications.html": {
      label: "Applications",
      subtitle: "Application review",
    },
    "officer-interviews.html": {
      label: "Interviews",
      subtitle: "Interview flow",
    },
    "officer-offers.html": {
      label: "Offers",
      subtitle: "Offers overview",
    },
    "officer-documents.html": {
      label: "Documents",
      subtitle: "Verification queue",
    },
    "officer-analytics.html": {
      label: "Analytics",
      subtitle: "Platform metrics",
    },

    "settings.html": {
      label: "Settings",
      subtitle: "Account preferences",
    },
  };

  return (
    metaMap[activePage] || {
      label: "Dashboard",
      subtitle: "Overview",
    }
  );
}

function applyAppearancePreference() {
  const compact = localStorage.getItem("campuslink_compact_mode") === "true";
  document.body.classList.toggle("compact-mode", compact);
}

function renderShell(user, activePage) {
  const shell = document.getElementById("app-shell");
  const pageContent = document.getElementById("page-content");

  const navItems = NAV_CONFIG[user.role] || [];
  const meta = getTopbarMeta(activePage);

  const initials =
    user.name
      .split(" ")
      .filter(Boolean)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase() || "")
      .join("") || "U";

  const navHtml = navItems
    .map((item) => {
      const isNotifications = item.href === "notifications.html";

      const badge = isNotifications
        ? `<span id="unreadBadge" class="unread-badge" style="display:none;">0</span>`
        : "";

      return `
        <a href="${item.href}" class="nav-link ${item.href === activePage ? "active" : ""
        }">
          <span class="nav-icon">${item.icon}</span>
          <span class="nav-label">${item.label}</span>
          ${badge}
        </a>
      `;
    })
    .join("");

  shell.innerHTML = `
    <aside class="sidebar">
      <div class="sidebar-brand">
        <div class="brand-mark">CL</div>

        <div class="brand-copy">
          <span class="brand-name">CampusLink</span>
          <span class="brand-subtitle">Placement Intelligence</span>
        </div>
      </div>

      <nav class="sidebar-nav" aria-label="Main navigation">
        ${navHtml}
      </nav>

      <div class="sidebar-settings">
        <a
          href="settings.html"
          class="nav-link ${activePage === "settings.html" ? "active" : ""
    }"
        >
          <span class="nav-icon">⚙</span>
          <span class="nav-label">Settings</span>
        </a>
      </div>
    </aside>

    <div class="shell-main">
      <header class="topbar">

        <div class="topbar-left">
          <div class="topbar-context">${meta.label}</div>
          <div class="topbar-subtitle">${meta.subtitle}</div>
        </div>

        <div class="topbar-user">

          <button
            type="button"
            class="notification-button"
            aria-label="Notifications"
          >
            <span class="notification-icon">🔔</span>
            <span class="notification-dot"></span>
          </button>

          <button
            type="button"
            class="user-chip"
            aria-label="Profile"
          >
            <div class="user-avatar">${initials}</div>

            <div class="user-meta">
              <span class="user-name">${user.name}</span>
              <span class="user-role">${user.role.replace("_", " ")}</span>
            </div>
          </button>

          <button id="logoutBtn" class="logout-btn">
            Logout
          </button>

        </div>
      </header>

      <main class="content-area" id="content-mount"></main>
    </div>
  `;

  document
    .getElementById("content-mount")
    .appendChild(pageContent);

  pageContent.style.display = "block";

  // Logout
  document
    .getElementById("logoutBtn")
    .addEventListener("click", logout);

  // Notification button
  document.querySelector(".notification-button").onclick = () => {
    window.location.href = "notifications.html";
  };

  // Profile button
  document.querySelector(".user-chip").onclick = () => {
    window.location.href = "profile.html";
  };
  // Load unread notification count
  loadUnreadBadge();
  applyAppearancePreference();;
}

async function loadUnreadBadge() {
  const badge = document.getElementById("unreadBadge");

  if (!badge) return;

  try {
    const res = await apiFetch("/api/notifications/unread-count");

    const count = res.data.count;

    if (count > 0) {
      badge.textContent = count;
      badge.style.display = "inline-flex";
    }
  } catch (err) {
    // Non-fatal — badge stays hidden
  }
}