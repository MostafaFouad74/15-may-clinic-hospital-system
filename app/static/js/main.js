const API_BASE_URL = "";

function getToken() {
  return localStorage.getItem("token");
}

function getRole() {
  return localStorage.getItem("role");
}

function setAuth(token, role) {
  localStorage.setItem("token", token);
  localStorage.setItem("role", role);
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("role");
  window.location.href = "/login-page";
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = "/login-page";
  }
}

function requireRole(role) {
  requireAuth();
  if (getRole() !== role) {
    redirectByRole(getRole());
  }
}

function redirectByRole(role) {
  if (role === "patient") {
    window.location.href = "/patient-dashboard-page";
  } else if (role === "doctor") {
    window.location.href = "/doctor-dashboard-page";
  } else if (role === "admin") {
    window.location.href = "/admin-dashboard-page";
  } else {
    window.location.href = "/login-page";
  }
}

async function fetchAPI(endpoint, options = {}) {
  const token = getToken();

  const headers = {
    ...(options.headers || {})
  };

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message = data.detail || data.message || "Request failed";
    if (response.status === 401) {
      logout();
    }
    throw new Error(message);
  }

  return data;
}

function showToast(message, type = "success") {
  const oldToast = document.querySelector(".toast");
  if (oldToast) oldToast.remove();

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.textContent = message;

  document.body.appendChild(toast);

  setTimeout(() => toast.classList.add("show"), 50);

  setTimeout(() => {
    toast.classList.remove("show");
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

function scrollToSection(id) {
  const section = document.getElementById(id);
  if (section) section.scrollIntoView({ behavior: "smooth", block: "start" });
}

function formatDateTime(value) {
  const d = new Date(value);
  return `${d.toLocaleDateString()} ${d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
}

function statusClass(status) {
  if (status === "Completed") return "success";
  if (status === "Cancelled") return "danger";
  return "info";
}

/* =========================
   LOGIN
========================= */

function initLoginPage() {
  if (getToken() && getRole()) {
    redirectByRole(getRole());
    return;
  }

  const form = document.getElementById("loginForm");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const submitBtn = form.querySelector("button[type='submit']");
    const originalText = submitBtn.textContent;

    submitBtn.disabled = true;
    submitBtn.textContent = "Signing in...";

    try {
      const formData = new FormData(form);

      const data = await fetchAPI("/login", {
        method: "POST",
        body: formData
      });

      setAuth(data.access_token, data.role);
      showToast(`Logged in as ${data.role}`, "success");

      setTimeout(() => redirectByRole(data.role), 700);
    } catch (err) {
      showToast(err.message, "error");
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  });
}

/* =========================
   REGISTER
========================= */

function initRegisterPage() {
  if (getToken() && getRole()) {
    redirectByRole(getRole());
    return;
  }

  const form = document.getElementById("registerForm");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const submitBtn = form.querySelector("button[type='submit']");
    const originalText = submitBtn.textContent;

    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    payload.age = parseInt(payload.age);
    payload.email = payload.email || null;

    submitBtn.disabled = true;
    submitBtn.textContent = "Creating account...";

    try {
      await fetchAPI("/register", {
        method: "POST",
        body: JSON.stringify(payload)
      });

      showToast("Account created successfully. Please login.", "success");

      setTimeout(() => {
        window.location.href = "/login-page";
      }, 1200);
    } catch (err) {
      showToast(err.message, "error");
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  });
}

/* =========================
   PATIENT DASHBOARD
========================= */

async function initPatientDashboard() {
  requireRole("patient");

  const today = new Date().toISOString().split("T")[0];
  const dateInput = document.getElementById("appointmentDate");
  if (dateInput) {
    dateInput.min = today;
    dateInput.value = today;
  }

  await loadPatientProfile();
  await loadPatientAppointments();

  document.getElementById("departmentSelect").addEventListener("change", loadDoctorsByDepartment);
  document.getElementById("doctorSelect").addEventListener("change", loadAvailableSlots);
  document.getElementById("appointmentDate").addEventListener("change", loadAvailableSlots);
}

async function loadPatientProfile() {
  const profileBox = document.getElementById("profileBox");
  const greeting = document.getElementById("patientGreeting");

  try {
    const data = await fetchAPI("/patient/me");

    greeting.textContent = `Welcome, ${data.patient.first_name} ${data.patient.last_name}`;

    profileBox.innerHTML = `
      <div><strong>Username:</strong> ${data.username}</div>
      <div><strong>Role:</strong> ${data.role}</div>
      <div><strong>Phone:</strong> ${data.patient.phone}</div>
      <div><strong>Email:</strong> ${data.patient.email || "N/A"}</div>
    `;
  } catch (err) {
    profileBox.textContent = err.message;
    showToast(err.message, "error");
  }
}

async function loadDoctorsByDepartment() {
  const department = document.getElementById("departmentSelect").value;
  const doctorSelect = document.getElementById("doctorSelect");
  const slotSelect = document.getElementById("slotSelect");

  doctorSelect.innerHTML = `<option value="">Select doctor</option>`;
  slotSelect.innerHTML = `<option value="">Select slot</option>`;

  if (!department) return;

  try {
    const doctors = await fetchAPI(`/doctor/by-department/${encodeURIComponent(department)}`);

    if (!doctors.length) {
      doctorSelect.innerHTML = `<option value="">No doctors found</option>`;
      return;
    }

    doctors.forEach((doctor) => {
      const option = document.createElement("option");
      option.value = doctor.id;
      option.textContent = `${doctor.full_name} - ${doctor.specialty}`;
      doctorSelect.appendChild(option);
    });
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function loadAvailableSlots() {
  const doctorId = document.getElementById("doctorSelect").value;
  const date = document.getElementById("appointmentDate").value;
  const slotSelect = document.getElementById("slotSelect");

  slotSelect.innerHTML = `<option value="">Select slot</option>`;

  if (!doctorId || !date) return;

  try {
    const data = await fetchAPI(`/doctor/${doctorId}/available-slots?target_date=${date}`);

    if (!data.available_slots.length) {
      slotSelect.innerHTML = `<option value="">No available slots</option>`;
      return;
    }

    data.available_slots.forEach((slot) => {
      const option = document.createElement("option");
      option.value = slot;
      option.textContent = new Date(slot).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
      slotSelect.appendChild(option);
    });
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function bookPatientAppointment() {
  const doctorId = document.getElementById("doctorSelect").value;
  const slot = document.getElementById("slotSelect").value;
  const notes = document.getElementById("notes").value;

  if (!doctorId || !slot) {
    showToast("Please select doctor, date, and slot.", "error");
    return;
  }

  try {
    await fetchAPI("/patient/appointments", {
      method: "POST",
      body: JSON.stringify({
        doctor_id: parseInt(doctorId),
        appointment_date: slot,
        notes: notes || null
      })
    });

    showToast("Appointment booked successfully.", "success");
    document.getElementById("notes").value = "";

    await loadAvailableSlots();
    await loadPatientAppointments();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function loadPatientAppointments() {
  const container = document.getElementById("patientAppointments");

  try {
    const appointments = await fetchAPI("/patient/appointments/my");

    if (!appointments.length) {
      container.innerHTML = `<div class="empty-state">No appointments yet.</div>`;
      return;
    }

    container.innerHTML = appointments.map((appt) => `
      <article class="data-card">
        <div>
          <h3>Doctor #${appt.doctor_id}</h3>
          <p>${formatDateTime(appt.appointment_date)}</p>
          <p>${appt.notes || "No notes"}</p>
        </div>
        <div class="card-actions">
          <span class="badge ${statusClass(appt.status)}">${appt.status}</span>
          ${
            appt.status === "Scheduled"
              ? `<button class="btn danger small" onclick="cancelPatientAppointment(${appt.id})">Cancel</button>`
              : ""
          }
        </div>
      </article>
    `).join("");
  } catch (err) {
    container.innerHTML = `<div class="empty-state">${err.message}</div>`;
  }
}

async function cancelPatientAppointment(id) {
  if (!confirm("Cancel this appointment?")) return;

  try {
    await fetchAPI(`/patient/appointments/${id}`, {
      method: "DELETE"
    });

    showToast("Appointment cancelled.", "success");
    await loadPatientAppointments();
  } catch (err) {
    showToast(err.message, "error");
  }
}

/* =========================
   DOCTOR DASHBOARD
========================= */

async function initDoctorDashboard() {
  requireRole("doctor");
  await loadDoctorAppointments();
}

async function loadDoctorAppointments() {
  const container = document.getElementById("doctorAppointments");

  try {
    const appointments = await fetchAPI("/doctor/appointments/me");

    if (!appointments.length) {
      container.innerHTML = `<div class="empty-state">No appointments assigned yet.</div>`;
      return;
    }

    container.innerHTML = appointments.map((appt) => `
      <article class="data-card">
        <div>
          <h3>Appointment #${appt.id}</h3>
          <p><strong>Patient ID:</strong> ${appt.patient_id}</p>
          <p><strong>Date:</strong> ${formatDateTime(appt.appointment_date)}</p>
          <p><strong>Notes:</strong> ${appt.notes || "No notes"}</p>
        </div>

        <div class="card-actions">
          <span class="badge ${statusClass(appt.status)}">${appt.status}</span>

          ${
            appt.status === "Scheduled"
              ? `
                <button class="btn success small" onclick="updateDoctorAppointmentStatus(${appt.id}, 'Completed')">Complete</button>
                <button class="btn danger small" onclick="updateDoctorAppointmentStatus(${appt.id}, 'Cancelled')">Cancel</button>
              `
              : ""
          }
        </div>
      </article>
    `).join("");
  } catch (err) {
    container.innerHTML = `<div class="empty-state">${err.message}</div>`;
    showToast(err.message, "error");
  }
}

async function updateDoctorAppointmentStatus(id, status) {
  try {
    await fetchAPI(`/doctor/appointments/${id}/status`, {
      method: "PUT",
      body: JSON.stringify({ status })
    });

    showToast(`Appointment marked as ${status}.`, "success");
    await loadDoctorAppointments();
  } catch (err) {
    showToast(err.message, "error");
  }
}

/* =========================
   ADMIN DASHBOARD
========================= */

async function initAdminDashboard() {
  requireRole("admin");

  const form = document.getElementById("createDoctorForm");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    payload.work_start_hour = parseInt(payload.work_start_hour);
    payload.work_end_hour = parseInt(payload.work_end_hour);
    payload.email = payload.email || null;

    try {
      await fetchAPI("/admin/create-doctor", {
        method: "POST",
        body: JSON.stringify(payload)
      });

      showToast("Doctor created successfully.", "success");
      form.reset();
      await loadAdminData();
    } catch (err) {
      showToast(err.message, "error");
    }
  });

  await loadAdminData();
}

async function loadAdminData() {
  await Promise.all([
    loadAdminDoctors(),
    loadAdminPatients(),
    loadAdminAppointments()
  ]);
}

async function loadAdminDoctors() {
  const container = document.getElementById("adminDoctors");

  try {
    const doctors = await fetchAPI("/doctor/all");

    if (!doctors.length) {
      container.innerHTML = `<div class="empty-state">No doctors found.</div>`;
      return;
    }

    container.innerHTML = doctors.map((doctor) => `
      <article class="data-card">
        <div>
          <h3>${doctor.full_name}</h3>
          <p>${doctor.specialty}</p>
          <p>Hours: ${doctor.work_start_hour}:00 - ${doctor.work_end_hour}:00</p>
        </div>
        <div class="card-actions">
          <span class="badge info">${doctor.availability_status}</span>
          <button class="btn danger small" onclick="deleteAdminDoctor(${doctor.id})">Delete</button>
        </div>
      </article>
    `).join("");
  } catch (err) {
    container.innerHTML = `<div class="empty-state">${err.message}</div>`;
  }
}

async function deleteAdminDoctor(id) {
  if (!confirm("Delete this doctor?")) return;

  try {
    await fetchAPI(`/admin/doctors/${id}`, {
      method: "DELETE"
    });

    showToast("Doctor deleted.", "success");
    await loadAdminDoctors();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function loadAdminPatients() {
  const container = document.getElementById("adminPatients");

  try {
    const patients = await fetchAPI("/admin/patients");

    if (!patients.length) {
      container.innerHTML = `<div class="empty-state">No patients found.</div>`;
      return;
    }

    container.innerHTML = patients.map((patient) => `
      <article class="data-card">
        <div>
          <h3>${patient.first_name} ${patient.last_name}</h3>
          <p><strong>Username:</strong> ${patient.username}</p>
          <p><strong>Phone:</strong> ${patient.phone}</p>
          <p><strong>Gender:</strong> ${patient.gender}</p>
        </div>
        <div class="card-actions">
          <button class="btn danger small" onclick="deleteAdminPatient(${patient.id})">Delete</button>
        </div>
      </article>
    `).join("");
  } catch (err) {
    container.innerHTML = `<div class="empty-state">${err.message}</div>`;
  }
}

async function deleteAdminPatient(id) {
  if (!confirm("Delete this patient?")) return;

  try {
    await fetchAPI(`/admin/patients/${id}`, {
      method: "DELETE"
    });

    showToast("Patient deleted.", "success");
    await loadAdminPatients();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function loadAdminAppointments() {
  const container = document.getElementById("adminAppointments");

  try {
    const appointments = await fetchAPI("/admin/appointments");

    if (!appointments.length) {
      container.innerHTML = `<div class="empty-state">No appointments found.</div>`;
      return;
    }

    container.innerHTML = appointments.map((appt) => `
      <article class="data-card">
        <div>
          <h3>Appointment #${appt.id}</h3>
          <p><strong>Doctor ID:</strong> ${appt.doctor_id}</p>
          <p><strong>Patient ID:</strong> ${appt.patient_id}</p>
          <p><strong>Date:</strong> ${formatDateTime(appt.appointment_date)}</p>
        </div>
        <div class="card-actions">
          <span class="badge ${statusClass(appt.status)}">${appt.status}</span>
          <button class="btn danger small" onclick="deleteAdminAppointment(${appt.id})">Delete</button>
        </div>
      </article>
    `).join("");
  } catch (err) {
    container.innerHTML = `<div class="empty-state">${err.message}</div>`;
  }
}

async function deleteAdminAppointment(id) {
  if (!confirm("Delete this appointment?")) return;

  try {
    await fetchAPI(`/admin/appointments/${id}`, {
      method: "DELETE"
    });

    showToast("Appointment deleted.", "success");
    await loadAdminAppointments();
  } catch (err) {
    showToast(err.message, "error");
  }
}