document.getElementById("loginForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);

  const response = await fetch("/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: formData
  });

  const result = await response.json();
  const message = document.getElementById("loginMessage");

  if (response.ok) {
    localStorage.setItem("token", result.access_token);
    localStorage.setItem("role", result.role);

    message.textContent = "Login successful";

    if (result.role === "patient") {
      window.location.href = "/patient-dashboard-page";
    } else {
      message.textContent = `Logged in as ${result.role}. Frontend page for this role will be added next.`;
    }
  } else {
    message.textContent = result.detail || "Login failed";
  }
});