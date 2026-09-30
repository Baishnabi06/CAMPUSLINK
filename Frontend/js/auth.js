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

/**
 * Email-code (OTP) login. Works alongside the password form: the login page
 * has two tabs, and this wires up the "Email code" tab.
 * Step 1: user enters email -> we request a code.
 * Step 2: user enters the 6-digit code -> we verify it and log them in.
 */
function initOtpLogin() {
  const passwordForm = document.getElementById("loginForm");
  const otpForm = document.getElementById("otpForm");
  if (!passwordForm || !otpForm) return;

  const tabPassword = document.getElementById("tabPassword");
  const tabOtp = document.getElementById("tabOtp");
  const emailStep = document.getElementById("otpEmailStep");
  const codeStep = document.getElementById("otpCodeStep");
  const errorEl = document.getElementById("authError");
  const infoEl = document.getElementById("authInfo");

  function showTab(which) {
    const isOtp = which === "otp";
    passwordForm.hidden = isOtp;
    otpForm.hidden = !isOtp;
    tabPassword.classList.toggle("active", !isOtp);
    tabOtp.classList.toggle("active", isOtp);
    errorEl.textContent = "";
    if (infoEl) infoEl.textContent = "";
  }
  tabPassword.addEventListener("click", () => showTab("password"));
  tabOtp.addEventListener("click", () => showTab("otp"));

  async function sendCode() {
    const email = document.getElementById("otpEmail").value.trim();
    const result = await apiFetch("/api/auth/request-otp", {
      method: "POST",
      body: { email },
    });
    emailStep.hidden = true;
    codeStep.hidden = false;
    if (infoEl) infoEl.textContent = result.message;
    document.getElementById("otpCode").focus();
  }

  otpForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.textContent = "";
    try {
      if (codeStep.hidden) {
        await sendCode();
      } else {
        const email = document.getElementById("otpEmail").value.trim();
        const otp = document.getElementById("otpCode").value.trim();
        const result = await apiFetch("/api/auth/verify-otp", {
          method: "POST",
          body: { email, otp },
        });
        setAuth(result.data.access_token, result.data.user);
        goToDashboard(result.data.user.role);
      }
    } catch (err) {
      errorEl.textContent = err.message;
    }
  });

  document.getElementById("resendOtpBtn").addEventListener("click", async () => {
    errorEl.textContent = "";
    try {
      await sendCode();
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