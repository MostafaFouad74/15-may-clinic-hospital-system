document.getElementById("registerForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const payload = {
    username: document.getElementById("username").value,
    password: document.getElementById("password").value,
    first_name: document.getElementById("first_name").value,
    last_name: document.getElementById("last_name").value,
    age: parseInt(document.getElementById("age").value),
    phone: document.getElementById("phone").value,
    address: document.getElementById("address").value,
    gender: document.getElementById("gender").value,
    department: document.getElementById("department").value,
    email: document.getElementById("email").value || null
  };

  const response = await fetch("/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  const result = await response.json();
  const message = document.getElementById("registerMessage");

  if (response.ok) {
    message.textContent = "Registration successful. Go back to login.";
    document.getElementById("registerForm").reset();
  } else {
    message.textContent = result.detail || "Registration failed";
  }
});