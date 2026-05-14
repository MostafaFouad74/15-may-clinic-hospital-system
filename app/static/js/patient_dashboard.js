const token = localStorage.getItem("token");

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("role");
  window.location.href = "/login-page";
}

document.getElementById("departmentSelect").addEventListener("change", async function () {
  const department = this.value;
  const doctorSelect = document.getElementById("doctorSelect");
  const slotSelect = document.getElementById("slotSelect");

  doctorSelect.innerHTML = '<option value="">Select Doctor</option>';
  slotSelect.innerHTML = '<option value="">Available Slots</option>';

  if (!department) return;

  const response = await fetch(`/doctor/by-department/${encodeURIComponent(department)}`);
  const doctors = await response.json();

  doctors.forEach(doctor => {
    const option = document.createElement("option");
    option.value = doctor.id;
    option.textContent = `${doctor.full_name} (${doctor.specialty})`;
    doctorSelect.appendChild(option);
  });
});

document.getElementById("appointmentDate").addEventListener("change", loadAvailableSlots);
document.getElementById("doctorSelect").addEventListener("change", loadAvailableSlots);

async function loadAvailableSlots() {
  const doctorId = document.getElementById("doctorSelect").value;
  const date = document.getElementById("appointmentDate").value;
  const slotSelect = document.getElementById("slotSelect");

  slotSelect.innerHTML = '<option value="">Available Slots</option>';

  if (!doctorId || !date) return;

  const response = await fetch(`/doctor/${doctorId}/available-slots?target_date=${date}`);
  const result = await response.json();

  result.available_slots.forEach(slot => {
    const option = document.createElement("option");
    option.value = slot;
    option.textContent = new Date(slot).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    slotSelect.appendChild(option);
  });
}

async function bookAppointment() {
  const doctorId = document.getElementById("doctorSelect").value;
  const slot = document.getElementById("slotSelect").value;
  const notes = document.getElementById("notes").value;
  const message = document.getElementById("bookingMessage");

  if (!token) {
    message.textContent = "Please login again.";
    return;
  }

  if (!doctorId || !slot) {
    message.textContent = "Please select department, doctor, and available slot.";
    return;
  }

  const response = await fetch("/patient/appointments", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({
      doctor_id: parseInt(doctorId),
      appointment_date: slot,
      notes: notes || null
    })
  });

  const result = await response.json();

  if (response.ok) {
    message.textContent = "Your appointment has been booked successfully. We are waiting for you.";
    document.getElementById("notes").value = "";
    loadAvailableSlots();
  } else {
    message.textContent = result.detail || "Booking failed.";
  }
}