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

// Fetch tasks from Python Flask backend
async function loadTasks() {
  try {
    const res = await fetch('/api/tasks');
    if (!res.ok) throw new Error('Network error');
    const data = await res.json();
    tasks = data.tasks || [];
    renderTasks();
  } catch (error) {
    console.error('Error fetching tasks:', error);
  }
}

// Add new task
todoForm.addEventListener('submit', async function (e) {
  e.preventDefault();
  const text = todoInput.value.trim();
  if (!text) return;

  try {
    const res = await fetch('/api/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text })
    });

    if (res.ok) {
      const data = await res.json();
      if (data.task) {
        tasks.unshift(data.task);
        todoInput.value = '';
        renderTasks();
        triggerPopAnimation(); // Subtle pop trigger on task add
      }
    }
  } catch (error) {
    console.error('Failed to add task:', error);
    alert('Could not save task to backend.');
  }
});

// Toggle task completed
async function toggleTask(id) {
  const task = tasks.find(t => String(t.id) === String(id));
  if (!task) return;

  task.completed = !task.completed;
  renderTasks();

  try {
    await fetch(`/api/tasks/${id}/toggle`, { method: 'POST' });
  } catch (error) {
    console.error('Failed to toggle task:', error);
  }
}

// Delete task
async function deleteTask(id) {
  try {
    const res = await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
    if (res.ok) {
      tasks = tasks.filter(t => String(t.id) !== String(id));
      renderTasks();
    }
  } catch (error) {
    console.error('Failed to delete task:', error);
  }
}

// Clear completed tasks
clearCompletedBtn.addEventListener('click', async function () {
  const completedTasks = tasks.filter(t => t.completed);
  if (completedTasks.length === 0) return;

  try {
    const res = await fetch('/api/tasks/clear-completed', { method: 'DELETE' });
    if (res.ok) {
      tasks = tasks.filter(t => !t.completed);
      renderTasks();
    }
  } catch (error) {
    console.error('Failed to clear completed tasks:', error);
  }
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

// Periodic background check to stay in sync with tasks.json
setInterval(async () => {
  try {
    const res = await fetch('/api/tasks');
    if (res.ok) {
      const data = await res.json();
      if (JSON.stringify(data.tasks) !== JSON.stringify(tasks)) {
        tasks = data.tasks || [];
        renderTasks();
      }
    }
  } catch (e) {
    // Quiet fail on network loss
  }
}, 4000);

// Initial load
loadTasks();
