// State
let tasks = [];
let currentFilter = 'all';

// DOM Elements
const todoForm = document.getElementById('todo-form');
const todoInput = document.getElementById('todo-input');
const todoList = document.getElementById('todo-list');
const taskCount = document.getElementById('task-count');
const clearCompletedBtn = document.getElementById('clear-completed-btn');
const filterButtons = document.querySelectorAll('.filter-btn');
const copyrightCard = document.getElementById('copyright-card');

// Default starter tasks
const DEFAULT_TASKS = [
  {
    id: "t1a2b3c4",
    text: "Explore TaskFlow To-Do List Application",
    completed: true
  },
  {
    id: "t5d6e7f8",
    text: "Add your first custom task above",
    completed: false
  }
];

// LocalStorage helpers for seamless offline/serverless persistence
function saveLocalBackup() {
  try {
    localStorage.setItem('taskflow_tasks', JSON.stringify(tasks));
  } catch (e) {}
}

function loadLocalBackup() {
  try {
    const raw = localStorage.getItem('taskflow_tasks');
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed;
    }
  } catch (e) {}
  return DEFAULT_TASKS;
}

// Pop Animation Trigger via JS
function triggerPopAnimation() {
  if (!copyrightCard) return;
  copyrightCard.classList.remove('is-popping');
  // Trigger DOM reflow to restart CSS3 animation
  void copyrightCard.offsetWidth;
  copyrightCard.classList.add('is-popping');
}

// Add click listener to pop on demand
if (copyrightCard) {
  copyrightCard.addEventListener('click', triggerPopAnimation);
}

// Fetch tasks (Hybrid: API sync with localStorage fallback)
async function loadTasks() {
  try {
    const res = await fetch('/api/tasks');
    if (res.ok) {
      const data = await res.json();
      if (data && Array.isArray(data.tasks) && data.tasks.length > 0) {
        tasks = data.tasks;
        saveLocalBackup();
        renderTasks();
        return;
      }
    }
  } catch (error) {
    // API not reachable in pure static CDN environment
  }
  tasks = loadLocalBackup();
  renderTasks();
}

// Add new task
todoForm.addEventListener('submit', async function (e) {
  e.preventDefault();
  const text = todoInput.value.trim();
  if (!text) return;

  const newTask = {
    id: 't_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 4),
    text: text,
    completed: false
  };

  tasks.unshift(newTask);
  todoInput.value = '';
  saveLocalBackup();
  renderTasks();
  triggerPopAnimation();

  // Sync to API in background if online
  try {
    const res = await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text })
    });
    if (res.ok) {
      const data = await res.json();
      if (data.task && data.task.id) {
        newTask.id = data.task.id;
        saveLocalBackup();
      }
    }
  } catch (e) {
    // Seamlessly saved in localStorage
  }
});

// Toggle task completed
async function toggleTask(id) {
  const task = tasks.find(t => String(t.id) === String(id));
  if (!task) return;

  task.completed = !task.completed;
  saveLocalBackup();
  renderTasks();

  try {
    await fetch(`/api/tasks/${id}/toggle`, { method: 'POST' });
  } catch (e) {}
}

// Delete task
async function deleteTask(id) {
  tasks = tasks.filter(t => String(t.id) !== String(id));
  saveLocalBackup();
  renderTasks();

  try {
    await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
  } catch (e) {}
}

// Clear completed tasks
clearCompletedBtn.addEventListener('click', async function () {
  tasks = tasks.filter(t => !t.completed);
  saveLocalBackup();
  renderTasks();

  try {
    await fetch('/api/tasks/clear-completed', { method: 'DELETE' });
  } catch (e) {}
});

// Filter tabs
filterButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    filterButtons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentFilter = btn.dataset.filter;
    renderTasks();
  });
});

// Render tasks list
function renderTasks() {
  const filteredTasks = tasks.filter(task => {
    if (currentFilter === 'active') return !task.completed;
    if (currentFilter === 'completed') return task.completed;
    return true;
  });

  todoList.innerHTML = '';

  if (filteredTasks.length === 0) {
    const emptyLi = document.createElement('li');
    emptyLi.className = 'empty-message';
    emptyLi.textContent = currentFilter === 'all' ? 'No tasks yet. Add one above!' : 'No tasks in this view.';
    todoList.appendChild(emptyLi);
  } else {
    filteredTasks.forEach(task => {
      const li = document.createElement('li');
      li.className = `todo-item ${task.completed ? 'completed' : ''}`;

      const leftDiv = document.createElement('div');
      leftDiv.className = 'todo-item-left';

      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.className = 'todo-checkbox';
      checkbox.checked = !!task.completed;
      checkbox.addEventListener('change', () => toggleTask(task.id));

      const span = document.createElement('span');
      span.className = 'todo-text';
      span.textContent = task.text;

      leftDiv.appendChild(checkbox);
      leftDiv.appendChild(span);

      const delBtn = document.createElement('button');
      delBtn.className = 'delete-btn';
      delBtn.textContent = 'Delete';
      delBtn.addEventListener('click', () => deleteTask(task.id));

      li.appendChild(leftDiv);
      li.appendChild(delBtn);
      todoList.appendChild(li);
    });
  }

  // Update remaining count
  const activeCount = tasks.filter(t => !t.completed).length;
  taskCount.textContent = `${activeCount} task${activeCount === 1 ? '' : 's'} left`;
}

// Initial load
loadTasks();
