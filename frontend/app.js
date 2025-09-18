const API_BASE = "/api";
const REFRESH_INTERVAL = 5000;

const state = {
  token: localStorage.getItem("unet_token"),
  user: JSON.parse(localStorage.getItem("unet_user") || "null"),
  refreshHandle: null,
};

const loginView = document.getElementById("login-view");
const dashboardView = document.getElementById("dashboard-view");
const loginForm = document.getElementById("login-form");
const loginFeedback = document.getElementById("login-feedback");
const logoutButton = document.getElementById("logout-button");
const refreshButton = document.getElementById("refresh-button");
const taskForm = document.getElementById("task-form");
const taskFeedback = document.getElementById("task-feedback");

const metricGrid = document.getElementById("metric-grid");
const deviceTable = document.getElementById("device-table");
const taskTable = document.getElementById("task-table");
const alertTable = document.getElementById("alert-table");
const auditList = document.getElementById("audit-list");
const dashboardUpdated = document.getElementById("dashboard-updated");
const integrationPanel = document.getElementById("integration-panel");

const userName = document.getElementById("user-name");
const userRole = document.getElementById("user-role");
const userAvatar = document.getElementById("user-avatar");

loginForm.addEventListener("submit", handleLogin);
logoutButton.addEventListener("click", () => logout(true));
refreshButton.addEventListener("click", () => refreshData());
taskForm.addEventListener("submit", handleCreateTask);

document.addEventListener("visibilitychange", () => {
  if (!state.token) return;
  if (document.hidden) {
    stopAutoRefresh();
  } else {
    refreshData();
    startAutoRefresh();
  }
});

if (state.token && state.user) {
  showDashboard(state.user);
  refreshData();
  startAutoRefresh();
} else {
  showLogin();
}

async function handleLogin(event) {
  event.preventDefault();
  const formData = new FormData(loginForm);
  const payload = {
    username: formData.get("username")?.trim(),
    password: formData.get("password")?.trim(),
  };
  loginFeedback.textContent = "正在登录...";
  loginFeedback.classList.remove("success");

  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const { detail } = await response.json();
      throw new Error(detail || "登录失败");
    }

    const data = await response.json();
    state.token = data.token;
    state.user = {
      name: data.displayName,
      role: data.role,
      permissions: data.permissions,
      username: payload.username,
    };
    localStorage.setItem("unet_token", state.token);
    localStorage.setItem("unet_user", JSON.stringify(state.user));

    showDashboard(state.user);
    loginFeedback.textContent = "登录成功，正在跳转...";
    loginFeedback.classList.add("success");
    loginForm.reset();
    await refreshData();
    startAutoRefresh();
  } catch (error) {
    console.error(error);
    loginFeedback.textContent = error.message || "登录失败";
  }
}

function showLogin() {
  loginView.classList.add("active");
  dashboardView.classList.remove("active");
  stopAutoRefresh();
}

function showDashboard(user) {
  userName.textContent = user.name;
  userRole.textContent = user.role;
  userAvatar.textContent = user.name?.slice(0, 1)?.toUpperCase() || "U";
  loginView.classList.remove("active");
  dashboardView.classList.add("active");
}

function logout(manual = false) {
  state.token = null;
  state.user = null;
  localStorage.removeItem("unet_token");
  localStorage.removeItem("unet_user");
  showLogin();
  if (manual) {
    loginFeedback.textContent = "已退出，请重新登录";
  }
}

async function apiFetch(path, options = {}) {
  if (!state.token) {
    throw new Error("未登录");
  }
  const headers = {
    Authorization: `Bearer ${state.token}`,
    ...(options.headers || {}),
  };
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (response.status === 401) {
    logout(false);
    throw new Error("登录状态已过期，请重新登录");
  }
  if (!response.ok) {
    const message = await extractError(response);
    throw new Error(message);
  }
  return response.json();
}

async function refreshData() {
  if (!state.token) return;
  try {
    const [metrics, devices, tasks, alerts, audits, integrations] = await Promise.all([
      apiFetch("/dashboard/overview"),
      apiFetch("/monitoring/devices"),
      apiFetch("/tasks"),
      apiFetch("/alerts"),
      apiFetch("/audit/logs"),
      apiFetch("/integrations"),
    ]);
    renderMetrics(metrics);
    renderDevices(devices);
    renderTasks(tasks);
    renderAlerts(alerts);
    renderAudits(audits);
    renderIntegrations(integrations);
    dashboardUpdated.textContent = `最后更新时间：${formatTimestamp(metrics.lastUpdated)}`;
    taskFeedback.textContent = "";
    taskFeedback.classList.remove("success");
  } catch (error) {
    console.error("数据刷新失败", error);
    taskFeedback.textContent = error.message;
    taskFeedback.classList.remove("success");
  }
}

function startAutoRefresh() {
  stopAutoRefresh();
  state.refreshHandle = window.setInterval(refreshData, REFRESH_INTERVAL);
}

function stopAutoRefresh() {
  if (state.refreshHandle) {
    clearInterval(state.refreshHandle);
    state.refreshHandle = null;
  }
}

async function handleCreateTask(event) {
  event.preventDefault();
  const formData = new FormData(taskForm);
  const scheduledRaw = formData.get("scheduledAt");
  const payload = {
    materialCode: formData.get("materialCode")?.trim(),
    targetDevice: formData.get("targetDevice")?.trim(),
    quantity: Number(formData.get("quantity")) || 0,
    priority: formData.get("priority") || "medium",
    scheduledAt: scheduledRaw ? new Date(scheduledRaw).toISOString() : undefined,
    source: "Manual",
  };
  taskFeedback.textContent = "正在创建任务...";
  taskFeedback.classList.remove("success");
  try {
    await apiFetch("/tasks", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    taskFeedback.textContent = "任务创建成功，已进入队列";
    taskFeedback.classList.add("success");
    taskForm.reset();
    await refreshData();
  } catch (error) {
    taskFeedback.textContent = error.message || "任务创建失败";
    taskFeedback.classList.remove("success");
  }
}

function renderMetrics(metrics) {
  const metricConfigs = [
    { key: "activeTasks", label: "活跃任务", suffix: "项" },
    { key: "completedToday", label: "今日完成", suffix: "项" },
    { key: "equipmentOnline", label: "在线设备", suffix: "台" },
    { key: "alarmCount", label: "未处理报警", suffix: "条" },
    { key: "throughput", label: "瞬时产量", suffix: "kg/h" },
    { key: "energyUsage", label: "能耗估算", suffix: "kWh" },
  ];

  const cards = metricConfigs
    .map(({ key, label, suffix }) => {
      const value = metrics[key];
      const displayValue = typeof value === "number" ? value.toLocaleString("zh-CN") : value ?? "--";
      return `
        <article class="metric-card">
          <h5>${label}</h5>
          <div class="value">${displayValue}<small>${suffix}</small></div>
        </article>
      `;
    })
    .join("");

  const materials = Array.isArray(metrics.materialSummary)
    ? metrics.materialSummary
        .map((item) => {
          const trendClass = item.trend >= 0 ? "up" : "down";
          const trendSymbol = item.trend >= 0 ? "+" : "";
          const throughput = typeof item.throughput === "number" ? item.throughput.toFixed(1) : item.throughput;
          const trend = typeof item.trend === "number" ? `${trendSymbol}${item.trend.toFixed(1)}%` : item.trend;
          return `
            <div class="item">
              <span>${item.materialCode} · ${item.hopper}</span>
              <span>
                ${throughput} kg/h
                <span class="trend ${trendClass}">${trend}</span>
              </span>
            </div>
          `;
        })
        .join("")
    : "<p class=\"muted\">暂无数据</p>";

  metricGrid.innerHTML = `
    ${cards}
    <article class="metric-card">
      <h5>物料吞吐趋势</h5>
      <div class="metric-materials">${materials}</div>
    </article>
  `;
}

function renderDevices(devices) {
  deviceTable.innerHTML = devices
    .map((device) => {
      const alarms = device.alarms?.length ? device.alarms.join("、") : "--";
      return `
        <tr>
          <td>${device.name}</td>
          <td>${device.material || "--"}</td>
          <td><span class="status-pill ${device.status}">${translateStatus(device.status)}</span></td>
          <td>${device.temperature.toFixed(1)}</td>
          <td>${device.level}%</td>
          <td>${device.throughput.toFixed(1)}</td>
          <td>${formatTimestamp(device.lastHeartbeat)}</td>
          <td>${alarms}</td>
        </tr>
      `;
    })
    .join("");
}

function renderTasks(tasks) {
  taskTable.innerHTML = tasks
    .map((task) => {
      return `
        <tr>
          <td>${task.taskId}</td>
          <td>${task.materialCode}</td>
          <td>${task.targetDevice}</td>
          <td>${task.quantity}</td>
          <td class="priority ${task.priority}">${translatePriority(task.priority)}</td>
          <td>
            <div class="progress-bar"><span style="width:${task.progress}%"></span></div>
            <small>${task.progress}%</small>
          </td>
          <td>${translateStatus(task.status)}</td>
        </tr>
      `;
    })
    .join("");
}

function renderAlerts(alerts) {
  alertTable.innerHTML = alerts
    .map((alert) => {
      const severityClass = `severity-${alert.severity}`;
      const statusLabel = alert.acknowledged ? "已确认" : "待处理";
      return `
        <tr>
          <td>${formatTimestamp(alert.raisedAt)}</td>
          <td>${alert.deviceId}</td>
          <td><span class="badge ${severityClass}">${translateSeverity(alert.severity)}</span></td>
          <td>${alert.message}</td>
          <td>${statusLabel}</td>
        </tr>
      `;
    })
    .join("");
}

function renderAudits(audits) {
  auditList.innerHTML = audits
    .map((log) => {
      return `
        <li class="audit-item">
          <div>
            <strong>${log.category}</strong>
            <p>${log.description}</p>
          </div>
          <div class="meta">
            <div>${formatTimestamp(log.timestamp)}</div>
            <div>${log.actor}</div>
          </div>
        </li>
      `;
    })
    .join("");
}

function renderIntegrations(integrations) {
  integrationPanel.innerHTML = integrations
    .map((item) => {
      return `
        <article class="integration-card">
          <h4>${item.name}</h4>
          <p>${item.target}</p>
          <div class="status">
            <span class="badge ${item.status}">${translateStatus(item.status)}</span>
            <small>${item.latencyMs} ms · 更新于 ${formatTimestamp(item.lastUpdated)}</small>
          </div>
        </article>
      `;
    })
    .join("");
}

function translateStatus(status) {
  const map = {
    online: "在线",
    offline: "离线",
    maintenance: "维护",
    queued: "排队中",
    in_progress: "执行中",
    completed: "已完成",
    degraded: "性能下降",
  };
  return map[status] || status;
}

function translatePriority(priority) {
  const map = {
    high: "高",
    medium: "中",
    low: "低",
  };
  return map[priority] || priority;
}

function translateSeverity(severity) {
  const map = {
    critical: "紧急",
    warning: "警告",
    info: "信息",
  };
  return map[severity] || severity;
}

function formatTimestamp(value) {
  if (!value) return "--";
  try {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return value;
    }
    return date.toLocaleString("zh-CN", {
      hour12: false,
    });
  } catch (error) {
    return value;
  }
}

async function extractError(response) {
  try {
    const data = await response.json();
    return data.detail || data.message || response.statusText;
  } catch (error) {
    return response.statusText;
  }
}
