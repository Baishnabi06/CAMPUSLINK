/**
 * Redirects the user to their role's dashboard.
 */
function goToDashboard(role) {
  const routes = {
    student: "student-dashboard.html",
    recruiter: "recruiter-dashboard.html",
    placement_officer: "officer-dashboard.html",
  };
  window.location.href = routes[role] || "login.html";
}

/**
 * Call this at the top of every protected page.
 * allowedRoles: array of role strings, e.g. ["student"]. Pass [] to just
 * require login (any role).
 */
function requireAuth(allowedRoles = []) {
  const token = getToken();
  const user = getUser();

  if (!token || !user) {
    window.location.href = "login.html";
    return null;
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role)) {
    goToDashboard(user.role);
    return null;
  }

  return user;
}

function logout() {
  clearAuth();
  window.location.href = "login.html";
}

function initLoginForm() {
  const form = document.getElementById("loginForm");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const errorEl = document.getElementById("authError");
    errorEl.textContent = "";

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;

    try {
      const result = await apiFetch("/api/auth/login", {
        method: "POST",
        body: { email, password },
      });
      setAuth(result.data.access_token, result.data.user);
      goToDashboard(result.data.user.role);
    } catch (err) {
      errorEl.textContent = err.message;
    }
  });
}

function initRegisterForm() {
  const form = document.getElementById("registerForm");
  if (!form) return;

  const roleSelect = document.getElementById("role");
  const branchGroup = document.getElementById("branchGroup");
  const companyGroup = document.getElementById("companyGroup");
  const departmentGroup = document.getElementById("departmentGroup");

  function updateVisibleFields() {
    branchGroup.style.display = roleSelect.value === "student" ? "block" : "none";
    companyGroup.style.display = roleSelect.value === "recruiter" ? "block" : "none";
    departmentGroup.style.display = roleSelect.value === "placement_officer" ? "block" : "none";
  }
  roleSelect.addEventListener("change", updateVisibleFields);
  updateVisibleFields();

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const errorEl = document.getElementById("authError");
    errorEl.textContent = "";

    const payload = {
      name: document.getElementById("name").value.trim(),
      email: document.getElementById("email").value.trim(),
      password: document.getElementById("password").value,
      role: roleSelect.value,
      branch: document.getElementById("branch").value || null,
      company_name: document.getElementById("company_name").value || null,
      department: document.getElementById("department").value || null,
    };

    try {
      await apiFetch("/api/auth/register", { method: "POST", body: payload });
      window.location.href = "login.html?registered=1";
    } catch (err) {
      errorEl.textContent = err.message;
    }
  });
}