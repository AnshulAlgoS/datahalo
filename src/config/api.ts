// API Configuration for DataHalo
// Handles both development (localhost) and production URLs

export const getApiBaseUrl = () => {
  // Check if we're in development environment
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    
    // Development environments
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://127.0.0.1:8000';
    }
    
    // Vercel preview deployments or other development URLs
    if (hostname.includes('localhost') || hostname.includes('127.0.0.1')) {
      return 'http://127.0.0.1:8000';
    }
  }
  
  // Check if we have environment variables (for build-time configuration)
  if (typeof process !== 'undefined' && process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  
  // Production URL (fallback)
  return 'https://datahalo.onrender.com';
};

export const API_BASE_URL = getApiBaseUrl();

// API endpoints
export const API_ENDPOINTS = {
  // News endpoints
  NEWS: '/news',
  REFRESH_NEWS: '/refresh-news',
  SAVED_NEWS: '/saved-news',
  SMART_FEED: '/smart-feed',
  
  // Journalist endpoints
  ANALYZE: '/analyze',
  FETCH: '/fetch',
  
  // Health
  HEALTH: '/health',
  ROOT: '/',
} as const;

// Helper function to build full API URLs
export const buildApiUrl = (endpoint: string, params?: URLSearchParams | Record<string, string>) => {
  const baseUrl = getApiBaseUrl();
  let url = `${baseUrl}${endpoint}`;
  
  if (params) {
    const searchParams = params instanceof URLSearchParams ? params : new URLSearchParams(params);
    url += `?${searchParams.toString()}`;
  }
  
  return url;
};

// Configuration object
export const API_CONFIG = {
  baseUrl: getApiBaseUrl(),
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
} as const;

export default {
  getApiBaseUrl,
  API_BASE_URL,
  API_ENDPOINTS,
  buildApiUrl,
  API_CONFIG,
};