// RTK - Main JavaScript Utilities

/**
 * Theme Management
 */
class ThemeManager {
    constructor() {
        this.themes = ['auto', 'light', 'dark'];
        this.currentTheme = localStorage.getItem('theme') || 'auto';
        this.init();
    }

    init() {
        this.applyTheme(this.currentTheme);
        this.bindEvents();
    }

    applyTheme(theme) {
        if (!this.themes.includes(theme)) {
            theme = 'auto';
        }
        document.documentElement.classList.remove('theme-light', 'theme-dark', 'theme-auto');
        document.documentElement.classList.add(`theme-${theme}`);
        localStorage.setItem('theme', theme);
        // Also set a cookie so Django templates can read it for Monaco Editor
        const monacoTheme = theme === 'dark' || (theme === 'auto' && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'vs-dark' : 'vs';
        document.cookie = `rtk_theme=${monacoTheme}; path=/; max-age=31536000`;
        this.currentTheme = theme;
    }

    toggleTheme() {
        const index = this.themes.indexOf(this.currentTheme);
        const nextTheme = this.themes[(index + 1) % this.themes.length];
        this.applyTheme(nextTheme);
    }

    bindEvents() {
        const toggleBtn = document.getElementById('themeToggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggleTheme());
        }

        // Listen for system theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (this.currentTheme === 'auto') {
                this.applyTheme('auto');
            }
        });
    }
}

/**
 * CSRF Token Handling
 */
function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

function getCsrfHeader() {
    return { 'X-CSRFToken': getCsrfToken() };
}

/**
 * AJAX Helper Functions
 */
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            ...getCsrfHeader(),
        },
        credentials: 'same-origin',
    };

    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        },
    };

    try {
        const response = await fetch(url, mergedOptions);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API Request failed:', error);
        throw error;
    }
}

async function apiPost(url, data) {
    return apiRequest(url, {
        method: 'POST',
        body: JSON.stringify(data),
    });
}

async function apiGet(url) {
    return apiRequest(url, { method: 'GET' });
}

async function apiPut(url, data) {
    return apiRequest(url, {
        method: 'PUT',
        body: JSON.stringify(data),
    });
}

async function apiDelete(url) {
    return apiRequest(url, { method: 'DELETE' });
}

/**
 * Toast Notifications
 */
function showToast(message, type = 'info', duration = 5000) {
    const container = getToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    container.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast, { delay: duration });
    bsToast.show();
    toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

function getToastContainer() {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1055';
        document.body.appendChild(container);
    }
    return container;
}

function showSuccess(message) { showToast(message, 'success'); }
function showError(message) { showToast(message, 'danger'); }
function showWarning(message) { showToast(message, 'warning'); }
function showInfo(message) { showToast(message, 'info'); }

/**
 * Loading States
 */
function setLoading(button, loading = true) {
    if (loading) {
        button.disabled = true;
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>Loading...';
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || button.innerHTML;
    }
}

/**
 * Form Helpers
 */
function serializeForm(form) {
    const formData = new FormData(form);
    const data = {};
    for (const [key, value] of formData.entries()) {
        if (data[key]) {
            if (!Array.isArray(data[key])) {
                data[key] = [data[key]];
            }
            data[key].push(value);
        } else {
            data[key] = value;
        }
    }
    return data;
}

function clearFormErrors(form) {
    form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    form.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
}

function showFormErrors(form, errors) {
    clearFormErrors(form);
    for (const [field, messages] of Object.entries(errors)) {
        const input = form.querySelector(`[name="${field}"]`);
        if (input) {
            input.classList.add('is-invalid');
            const feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            feedback.textContent = Array.isArray(messages) ? messages[0] : messages;
            input.parentNode.appendChild(feedback);
        }
    }
}

/**
 * Copy to Clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showSuccess('Copied to clipboard!');
        return true;
    } catch (err) {
        showError('Failed to copy: ' + err.message);
        return false;
    }
}

/**
 * Monaco Editor Integration
 */
let monacoEditors = {};

async function initMonacoEditor(elementId, options = {}) {
    if (typeof monaco === 'undefined') {
        // Load Monaco dynamically
        await loadMonaco();
    }

    const defaultOptions = {
        theme: 'vs',
        automaticLayout: true,
        minimap: { enabled: false },
        fontSize: 14,
        lineNumbers: 'on',
        scrollBeyondLastLine: false,
    };

    const editor = monaco.editor.create(document.getElementById(elementId), {
        ...defaultOptions,
        ...options,
    });

    monacoEditors[elementId] = editor;
    return editor;
}

function getMonacoEditor(elementId) {
    return monacoEditors[elementId];
}

function disposeMonacoEditor(elementId) {
    if (monacoEditors[elementId]) {
        monacoEditors[elementId].dispose();
        delete monacoEditors[elementId];
    }
}

function loadMonaco() {
    return new Promise((resolve, reject) => {
        if (typeof monaco !== 'undefined') {
            resolve();
            return;
        }

        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs/loader.js';
        script.onload = () => {
            require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' } });
            require(['vs/editor/editor.main'], () => {
                resolve();
            });
        };
        script.onerror = () => reject(new Error('Failed to load Monaco Editor'));
        document.head.appendChild(script);
    });
}

/**
 * Prism.js Syntax Highlighting
 */
function highlightCode() {
    if (typeof Prism !== 'undefined') {
        Prism.highlightAll();
    }
}

/**
 * Chart.js Helpers
 */
function createChart(canvasId, config) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const defaultConfig = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim() || '#94a3b8',
                    font: { family: 'Inter, system-ui, sans-serif' },
                },
            },
            tooltip: {
                backgroundColor: getComputedStyle(document.documentElement).getPropertyValue('--card-bg').trim() || '#1e293b',
                titleColor: getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim() || '#f1f5f9',
                bodyColor: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim() || '#94a3b8',
                borderColor: getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim() || '#334155',
                borderWidth: 1,
            },
        },
        scales: {
            x: {
                grid: { color: getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim() || '#334155' },
                ticks: { color: getComputedStyle(document.documentElement).getPropertyValue('--text-muted').trim() || '#64748b' },
            },
            y: {
                grid: { color: getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim() || '#334155' },
                ticks: { color: getComputedStyle(document.documentElement).getPropertyValue('--text-muted').trim() || '#64748b' },
                beginAtZero: true,
            },
        },
    };

    return new Chart(ctx, {
        ...defaultConfig,
        ...config,
    });
}

/**
 * Debounce Utility
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle Utility
 */
function throttle(func, limit) {
    let inThrottle;
    return function executedFunction(...args) {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Sidebar Toggle for Mobile
 */
function initSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.querySelector('.sidebar-overlay');
    const toggle = document.getElementById('sidebarToggle');

    if (toggle && sidebar) {
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('show');
            if (overlay) overlay.classList.toggle('show');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', () => {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        });
    }
}

/**
 * Initialize on DOM Ready
 */
document.addEventListener('DOMContentLoaded', () => {
    // Initialize theme
    new ThemeManager();

    // Initialize sidebar
    initSidebar();

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Highlight code blocks
    highlightCode();

    // Add fade-in animation to cards
    document.querySelectorAll('.card').forEach((card, index) => {
        card.style.animationDelay = `${index * 50}ms`;
    });

    // Handle form submissions with loading states
    document.querySelectorAll('form[data-ajax="true"]').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const btn = form.querySelector('button[type="submit"]');
            setLoading(btn, true);

            try {
                const data = serializeForm(form);
                const response = await apiPost(form.action, data);
                if (response.success) {
                    showSuccess(response.message || 'Success!');
                    if (response.redirect) {
                        window.location.href = response.redirect;
                    }
                } else {
                    showFormErrors(form, response.errors || {});
                    showError(response.message || 'An error occurred');
                }
            } catch (err) {
                showError(err.message);
            } finally {
                setLoading(btn, false);
            }
        });
    });
});

/**
 * Export for global access
 */
window.RTK = {
    ThemeManager,
    apiRequest,
    apiPost,
    apiGet,
    apiPut,
    apiDelete,
    showToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    setLoading,
    serializeForm,
    clearFormErrors,
    showFormErrors,
    copyToClipboard,
    initMonacoEditor,
    getMonacoEditor,
    disposeMonacoEditor,
    highlightCode,
    createChart,
    debounce,
    throttle,
};