const loginForm = document.querySelector("#login-form");
const registerForm = document.querySelector("#register-form");
const taskForm = document.querySelector("#task-form");
const taskInput = document.querySelector("#task-input");
const deadlineInput = document.querySelector("#deadline-input");
const taskList = document.querySelector("#task-list");
const statusBox = document.querySelector("#status");
const reloadButton = document.querySelector("#reload-button");
const logoutButton = document.querySelector("#logout-button");

const authPanel = document.querySelector("#auth-panel");
const tasksPanel = document.querySelector("#tasks-panel");

const loginFormContainer = document.querySelector("#login-form-container");
const registerFormContainer = document.querySelector("#register-form-container");
const showRegister = document.querySelector("#show-register");
const showLogin = document.querySelector("#show-login");
const authError = document.querySelector("#auth-error");
const authErrorText = document.querySelector("#auth-error-text");
const userName = document.querySelector("#user-name");
const pendingCount = document.querySelector("#pending-count");
const completedCount = document.querySelector("#completed-count");
const overdueCount = document.querySelector("#overdue-count");
const completionRate = document.querySelector("#completion-rate");
const overviewNote = document.querySelector("#overview-note");
const searchInput = document.querySelector("#task-search");
const filterPills = document.querySelector("#filter-pills");
const focusRing = document.querySelector(".focus-ring");

const passwordKey = "contrase\u00f1a";
const AUTO_REFRESH_MS = 15000;

let allTasks = [];
let activeFilter = "all";
let searchTerm = "";
let refreshTimer = null;
let isSyncing = false;

function setStatus(message, isError = false) {
  statusBox.textContent = message;
  statusBox.style.color = isError ? "#ff9d9d" : "#ffd7b3";
}

function setAuthError(message) {
  authErrorText.textContent = message;
  authError.classList.remove("hidden");
}

function clearAuthError() {
  authError.classList.add("hidden");
  authErrorText.textContent = "";
}

function showPanel(panelId) {
  if (panelId === "tasks") {
    authPanel.classList.add("hidden");
    tasksPanel.classList.remove("hidden");
  } else {
    tasksPanel.classList.add("hidden");
    authPanel.classList.remove("hidden");
  }
}

function toggleAuthForm(formId) {
  if (formId === "register") {
    loginFormContainer.classList.add("hidden");
    registerFormContainer.classList.remove("hidden");
  } else {
    registerFormContainer.classList.add("hidden");
    loginFormContainer.classList.remove("hidden");
  }
  clearAuthError();
}

function formatDeadline(fechaLimite) {
  if (!fechaLimite) return null;

  const date = new Date(fechaLimite);
  return date.toLocaleString("es-ES", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function isOverdue(fechaLimite, completada) {
  if (!fechaLimite || completada) return false;
  return new Date(fechaLimite) < new Date();
}

function getFilteredTasks(tareas) {
  return tareas.filter((tarea) => {
    const matchesSearch = tarea.texto
      .toLowerCase()
      .includes(searchTerm.toLowerCase());

    if (!matchesSearch) {
      return false;
    }

    if (activeFilter === "pending") {
      return !tarea.completada;
    }

    if (activeFilter === "completed") {
      return tarea.completada;
    }

    if (activeFilter === "overdue") {
      return isOverdue(tarea.fecha_limite, tarea.completada);
    }

    return true;
  });
}

function updateCounters(tareas) {
  const pendientes = tareas.filter((t) => !t.completada).length;
  const completadas = tareas.filter((t) => t.completada).length;
  const vencidas = tareas.filter((t) => isOverdue(t.fecha_limite, t.completada)).length;
  const total = tareas.length;
  const porcentaje = total ? Math.round((completadas / total) * 100) : 0;

  pendingCount.textContent = pendientes;
  completedCount.textContent = completadas;
  overdueCount.textContent = vencidas;
  completionRate.textContent = `${porcentaje}%`;
  focusRing?.style.setProperty("--progress", `${porcentaje}%`);

  if (!total) {
    overviewNote.textContent = "Aun no hay tareas registradas.";
    return;
  }

  if (vencidas > 0) {
    overviewNote.textContent = `Tienes ${vencidas} tarea${vencidas === 1 ? "" : "s"} vencida${vencidas === 1 ? "" : "s"} que requieren atencion.`;
    return;
  }

  if (pendientes > 0) {
    overviewNote.textContent = `Vas bien: ${completadas} completadas y ${pendientes} pendiente${pendientes === 1 ? "" : "s"}.`;
    return;
  }

  overviewNote.textContent = "Todo esta completo. Buen cierre de tablero.";
}

function sortTasks(tareas) {
  return [...tareas].sort((a, b) => {
    if (!a.fecha_limite && !b.fecha_limite) {
      return a.id - b.id;
    }

    if (!a.fecha_limite) {
      return 1;
    }

    if (!b.fecha_limite) {
      return -1;
    }

    const dateDiff = new Date(a.fecha_limite) - new Date(b.fecha_limite);
    if (dateDiff !== 0) {
      return dateDiff;
    }

    return a.id - b.id;
  });
}

function tasksAreEqual(currentTasks, nextTasks) {
  if (currentTasks.length !== nextTasks.length) {
    return false;
  }

  return currentTasks.every((task, index) => {
    const nextTask = nextTasks[index];
    return (
      task.id === nextTask.id &&
      task.texto === nextTask.texto &&
      task.completada === nextTask.completada &&
      task.fecha_limite === nextTask.fecha_limite
    );
  });
}

function applyTasks(tareas, { forceRender = false } = {}) {
  const sortedTasks = sortTasks(tareas);
  const changed = !tasksAreEqual(allTasks, sortedTasks);
  allTasks = sortedTasks;

  if (forceRender || changed) {
    renderTasks(allTasks);
  }
}

function upsertTask(task) {
  const currentIndex = allTasks.findIndex((item) => item.id === task.id);

  if (currentIndex === -1) {
    applyTasks([...allTasks, task]);
    return;
  }

  const nextTasks = [...allTasks];
  nextTasks[currentIndex] = task;
  applyTasks(nextTasks);
}

function removeTaskFromState(taskId) {
  applyTasks(allTasks.filter((item) => item.id !== taskId));
}

function startAutoRefresh() {
  stopAutoRefresh();
  refreshTimer = window.setInterval(() => {
    if (document.hidden) return;
    syncTasks({ silent: true });
  }, AUTO_REFRESH_MS);
}

function stopAutoRefresh() {
  if (!refreshTimer) return;
  window.clearInterval(refreshTimer);
  refreshTimer = null;
}

function createEditForm(tarea) {
  stopAutoRefresh();
  const form = document.createElement("form");
  form.className = "task-edit";

  const input = document.createElement("input");
  input.type = "text";
  input.value = tarea.texto;
  input.required = true;

  const deadlineInputEdit = document.createElement("input");
  deadlineInputEdit.type = "datetime-local";
  deadlineInputEdit.value = tarea.fecha_limite ? tarea.fecha_limite.slice(0, 16) : "";

  const saveButton = document.createElement("button");
  saveButton.type = "submit";
  saveButton.className = "success";
  saveButton.textContent = "Guardar";

  const cancelButton = document.createElement("button");
  cancelButton.type = "button";
  cancelButton.className = "secondary";
  cancelButton.textContent = "Cancelar";

  cancelButton.addEventListener("click", async () => {
    await loadTasks();
    startAutoRefresh();
  });
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const fechaLimite = deadlineInputEdit.value || null;
    await updateTask(tarea.id, input.value, fechaLimite);
    if (!document.body.contains(form)) {
      startAutoRefresh();
    }
  });

  form.append(input, deadlineInputEdit, saveButton, cancelButton);
  return form;
}

function renderTasks(tareas) {
  taskList.innerHTML = "";
  updateCounters(tareas);

  if (!tareas.length) {
    const emptyState = document.createElement("li");
    emptyState.className = "empty-state";
    emptyState.textContent = "No hay tareas registradas.";
    taskList.appendChild(emptyState);
    return;
  }

  const tareasFiltradas = getFilteredTasks(tareas);

  if (!tareasFiltradas.length) {
    const emptyState = document.createElement("li");
    emptyState.className = "empty-state";
    emptyState.textContent = "No hay tareas que coincidan con el filtro actual.";
    taskList.appendChild(emptyState);
    return;
  }

  tareasFiltradas.forEach((tarea) => {
    const item = document.createElement("li");
    item.className = "task-item";

    if (isOverdue(tarea.fecha_limite, tarea.completada)) {
      item.classList.add("overdue");
    }

    if (tarea.completada) {
      item.classList.add("completed-task");
    }

    const mainRow = document.createElement("div");
    mainRow.className = "task-main";

    const label = document.createElement("label");
    label.className = "task-label";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "task-checkbox";
    checkbox.checked = tarea.completada;
    checkbox.addEventListener("change", async () => {
      await toggleTask(tarea.id, checkbox.checked);
    });

    const textContainer = document.createElement("div");
    textContainer.className = "task-text-container";

    const text = document.createElement("span");
    text.className = "task-text";

    if (tarea.completada) {
      text.classList.add("completed");
    }

    text.textContent = tarea.texto;
    textContainer.appendChild(text);

    const meta = document.createElement("div");
    meta.className = "task-meta";

    if (tarea.fecha_limite) {
      const deadline = document.createElement("span");
      deadline.className = "task-chip deadline-chip";
      deadline.textContent = formatDeadline(tarea.fecha_limite);

      if (isOverdue(tarea.fecha_limite, tarea.completada)) {
        deadline.classList.add("overdue-badge");
      }

      meta.appendChild(deadline);
    }

    if (tarea.completada) {
      const doneChip = document.createElement("span");
      doneChip.className = "task-chip completed-chip";
      doneChip.textContent = "Completada";
      meta.appendChild(doneChip);
    }

    if (meta.childNodes.length) {
      textContainer.appendChild(meta);
    }

    label.append(checkbox, textContainer);

    const actions = document.createElement("div");
    actions.className = "task-actions";

    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.className = "secondary";
    editButton.textContent = "Editar";

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "danger";
    deleteButton.textContent = "Eliminar";

    editButton.addEventListener("click", () => {
      item.replaceChildren(createEditForm(tarea));
    });

    deleteButton.addEventListener("click", async () => {
      await deleteTask(tarea.id);
    });

    actions.append(editButton, deleteButton);
    mainRow.append(label, actions);
    item.append(mainRow);
    taskList.appendChild(item);
  });
}

async function checkSession() {
  try {
    const response = await fetch("/api/sesion");
    const data = await response.json();

    if (data.autenticado) {
      userName.textContent = data.nombre;
      showPanel("tasks");
      startAutoRefresh();
      loadTasks();
    } else {
      showPanel("auth");
    }
  } catch (error) {
    showPanel("auth");
  }
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Ocurrio un error.");
  }

  return data;
}

async function loadTasks() {
  await syncTasks();
}

async function syncTasks({ silent = false } = {}) {
  if (isSyncing) return;
  isSyncing = true;

  if (!silent) {
    setStatus("Cargando tareas...");
  }

  try {
    const data = await apiRequest("/api/tareas");
    applyTasks(data.tareas);
    if (!silent) {
      setStatus("Tareas actualizadas.");
    }
  } catch (error) {
    if (error.message.includes("No autenticado")) {
      showPanel("auth");
      stopAutoRefresh();
      return;
    }

    if (!silent) {
      setStatus(error.message, true);
    }
  } finally {
    isSyncing = false;
  }
}

async function createTaskTask(texto, fechaLimite = null) {
  try {
    const body = { texto };

    if (fechaLimite) {
      body.fecha_limite = fechaLimite;
    }

    const data = await apiRequest("/api/tareas", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    taskInput.value = "";
    deadlineInput.value = "";
    upsertTask(data.tarea);
    setStatus(data.mensaje);
    syncTasks({ silent: true });
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function updateTask(id, texto, fechaLimite = null) {
  try {
    const body = { id, texto };

    if (fechaLimite) {
      body.fecha_limite = fechaLimite;
    }

    const data = await apiRequest("/api/tareas", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    upsertTask(data.tarea);
    setStatus(data.mensaje);
    syncTasks({ silent: true });
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function toggleTask(id, completada) {
  const existingTask = allTasks.find((task) => task.id === id);
  if (!existingTask) return;

  upsertTask({ ...existingTask, completada });

  try {
    const data = await apiRequest("/api/tareas", {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, completada }),
    });

    upsertTask(data.tarea);
    setStatus(data.mensaje);
    syncTasks({ silent: true });
  } catch (error) {
    upsertTask(existingTask);
    setStatus(error.message, true);
  }
}

async function deleteTask(id) {
  const existingTask = allTasks.find((task) => task.id === id);
  if (!existingTask) return;

  removeTaskFromState(id);

  try {
    const data = await apiRequest("/api/tareas", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id }),
    });

    setStatus(data.mensaje);
    syncTasks({ silent: true });
  } catch (error) {
    upsertTask(existingTask);
    setStatus(error.message, true);
  }
}

showRegister.addEventListener("click", () => toggleAuthForm("register"));
showLogin.addEventListener("click", () => toggleAuthForm("login"));

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearAuthError();

  const usuario = document.querySelector("#login-usuario").value.trim();
  const contrasena = document.querySelector("#login-contrasena").value;

  try {
    const data = await apiRequest("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ usuario, [passwordKey]: contrasena }),
    });

    userName.textContent = data.nombre;
    showPanel("tasks");
    startAutoRefresh();
    loadTasks();
    loginForm.reset();
  } catch (error) {
    setAuthError(error.message);
  }
});

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearAuthError();

  const nombre = document.querySelector("#register-nombre").value.trim();
  const usuario = document.querySelector("#register-usuario").value.trim();
  const contrasena = document.querySelector("#register-contrasena").value;

  try {
    const data = await apiRequest("/api/registro", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nombre, usuario, [passwordKey]: contrasena }),
    });

    userName.textContent = data.nombre;
    showPanel("tasks");
    startAutoRefresh();
    loadTasks();
    registerForm.reset();
  } catch (error) {
    setAuthError(error.message);
  }
});

logoutButton.addEventListener("click", async () => {
  try {
    await apiRequest("/api/logout", { method: "POST" });
    showPanel("auth");
    stopAutoRefresh();
    allTasks = [];
    applyTasks(allTasks, { forceRender: true });
  } catch (error) {
    setStatus(error.message, true);
  }
});

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const texto = taskInput.value.trim();
  const fechaLimite = deadlineInput.value || null;
  await createTaskTask(texto, fechaLimite);
});

reloadButton.addEventListener("click", loadTasks);

searchInput.addEventListener("input", (event) => {
  searchTerm = event.target.value.trim();
  renderTasks(allTasks);
});

filterPills.addEventListener("click", (event) => {
  const button = event.target.closest("[data-filter]");
  if (!button) return;

  activeFilter = button.dataset.filter;

  document.querySelectorAll(".filter-pill").forEach((pill) => {
    pill.classList.toggle("active", pill === button);
  });

  renderTasks(allTasks);
});

document.addEventListener("visibilitychange", () => {
  if (document.hidden) return;
  syncTasks({ silent: true });
});

window.addEventListener("focus", () => {
  syncTasks({ silent: true });
});

checkSession();
