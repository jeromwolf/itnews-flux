// Tech News Digest - Main JavaScript

const API_BASE = '/api';

// Utility: Fetch JSON with error handling
async function fetchJSON(url, options = {}) {
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || `HTTP ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Fetch error:', error);
    throw error;
  }
}

// Format date
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

// Format duration (seconds to MM:SS)
function formatDuration(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// Format cost
function formatCost(cost) {
  return `$${cost.toFixed(4)}`;
}

// Show toast notification
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 1rem 1.5rem;
    background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
    color: white;
    border-radius: 8px;
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    animation: slideIn 0.3s ease-out;
  `;

  document.body.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'slideOut 0.3s ease-in';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// News API
const NewsAPI = {
  async getNews(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    return await fetchJSON(`${API_BASE}/news/?${queryString}`);
  },

  async selectNews(newsIds) {
    return await fetchJSON(`${API_BASE}/news/select`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ news_ids: newsIds }),
    });
  },
};

// Videos API
const VideosAPI = {
  async createVideo(newsIds, uploadToYoutube = false, style = 'professional', voice = 'alloy') {
    return await fetchJSON(`${API_BASE}/videos/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        news_ids: newsIds,
        upload_to_youtube: uploadToYoutube,
        style,
        voice,
      }),
    });
  },

  async listVideos(limit = 10, status = null) {
    const params = { limit };
    if (status) params.status = status;
    const queryString = new URLSearchParams(params).toString();
    return await fetchJSON(`${API_BASE}/videos/?${queryString}`);
  },

  async getVideo(videoId) {
    return await fetchJSON(`${API_BASE}/videos/${videoId}`);
  },

  async deleteVideo(videoId) {
    return await fetchJSON(`${API_BASE}/videos/${videoId}`, {
      method: 'DELETE',
    });
  },
};

// Schedule API
const ScheduleAPI = {
  async getSchedule() {
    return await fetchJSON(`${API_BASE}/schedule/`);
  },

  async updateSchedule(config) {
    return await fetchJSON(`${API_BASE}/schedule/`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    });
  },

  async triggerNow() {
    return await fetchJSON(`${API_BASE}/schedule/trigger`, {
      method: 'POST',
    });
  },
};

// Analytics API
const AnalyticsAPI = {
  async getStats() {
    return await fetchJSON(`${API_BASE}/analytics/stats`);
  },

  async getCosts(days = 7) {
    return await fetchJSON(`${API_BASE}/analytics/costs?days=${days}`);
  },

  async getPerformance(days = 7) {
    return await fetchJSON(`${API_BASE}/analytics/performance?days=${days}`);
  },

  async getHistory(limit = 10) {
    return await fetchJSON(`${API_BASE}/analytics/history?limit=${limit}`);
  },
};

// DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  // Add CSS animations
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
    @keyframes slideOut {
      from {
        transform: translateX(0);
        opacity: 1;
      }
      to {
        transform: translateX(100%);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(style);

  // Highlight active nav link
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav a').forEach((link) => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });
});

// Export for use in HTML
window.API = {
  News: NewsAPI,
  Videos: VideosAPI,
  Schedule: ScheduleAPI,
  Analytics: AnalyticsAPI,
};

window.utils = {
  formatDate,
  formatDuration,
  formatCost,
  showToast,
};
