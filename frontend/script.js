const API_URL = "https://gestor-tareas-fbrm.onrender.com/api/tareas";

const taskForm = document.querySelector("#task-form");
const taskInput = document.querySelector("#task-input");
const deadlineInput = document.querySelector("#deadline-input");
const taskList = document.querySelector("#task-list");
const statusBox = document.querySelector("#status");
const reloadButton = document.querySelector("#reload-button");

function setStatus(message, isError = false) {
  statusBox.textContent = message;
  statusBox.style.color = isError ? "#9f2222" : "#9c4d18";
}

async function request(url, options = {}) {
  const response = await fetch(url, options);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Ocurrio un error en la solicitud.");
  }

  return data;
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

function createEditForm(tarea) {
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

  cancelButton.addEventListener("click", loadTasks);
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const fechaLimite = deadlineInputEdit.value || null;
    await updateTask(tarea.id, input.value, fechaLimite);
  });

  form.append(input, deadlineInputEdit, saveButton, cancelButton);
  return form;
}

function renderTasks(tareas) {
  taskList.innerHTML = "";

  if (!tareas.length) {
    const emptyState = document.createElement("li");
    emptyState.className = "empty-state";
    emptyState.textContent = "No hay tareas registradas.";
    taskList.appendChild(emptyState);
    return;
  }

  tareas.forEach((tarea) => {
    const item = document.createElement("li");
    item.className = "task-item";

    if (isOverdue(tarea.fecha_limite, tarea.completada)) {
      item.classList.add("overdue");
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

    if (tarea.fecha_limite) {
      const deadline = document.createElement("span");
      deadline.className = "task-deadline";
      deadline.textContent = formatDeadline(tarea.fecha_limite);
      if (isOverdue(tarea.fecha_limite, tarea.completada)) {
        deadline.classList.add("overdue-badge");
      }
      textContainer.appendChild(deadline);
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

async function loadTasks() {
  setStatus("Cargando tareas...");

  try {
    const data = await request(API_URL);
    renderTasks(data.tareas);
    setStatus("Tareas actualizadas.");
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function createTask(texto, fechaLimite = null) {
  try {
    const body = { texto };
    if (fechaLimite) {
      body.fecha_limite = fechaLimite;
    }

    const data = await request(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    taskInput.value = "";
    deadlineInput.value = "";
    setStatus(data.mensaje);
    await loadTasks();
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

    const data = await request(API_URL, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(body),
    });

    setStatus(data.mensaje);
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function toggleTask(id, completada) {
  try {
    const data = await request(API_URL, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ id, completada }),
    });

    setStatus(data.mensaje);
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function deleteTask(id) {
  try {
    const data = await request(API_URL, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ id }),
    });

    setStatus(data.mensaje);
    await loadTasks();
  } catch (error) {
    setStatus(error.message, true);
  }
}

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const texto = taskInput.value.trim();
  const fechaLimite = deadlineInput.value || null;
  await createTask(texto, fechaLimite);
});

reloadButton.addEventListener("click", loadTasks);

loadTasks();
