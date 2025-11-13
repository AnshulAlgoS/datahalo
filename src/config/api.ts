// API Configuration for DataHalo
// Handles both development (localhost) and production environments

// Environment detection
const isLocalhost = typeof window !== 'undefined' && 
  (window.location.hostname === 'localhost' || 
   window.location.hostname === '127.0.0.1' || 
   window.location.hostname === '::1');

// API Base URLs
const API_BASE_URLS = {
  development: 'http://127.0.0.1:8000',
  production: 'https://datahalo.onrender.com'
};

// Get the current API base URL
export const getApiBaseUrl = (): string => {
  // Check for environment variable override
  if (typeof process !== 'undefined' && process.env?.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  
  // Auto-detect environment
  return isLocalhost ? API_BASE_URLS.development : API_BASE_URLS.production;
};

// API Endpoints
export const API_ENDPOINTS = {
  NEWS: '/news',
  REFRESH_NEWS: '/refresh-news',
  SMART_FEED: '/smart-feed',
  ANALYZE: '/analyze',
  FETCH: '/fetch',
  HEALTH: '/health',
  SAVED_NEWS: '/saved-news',
  ROOT: '/'
} as const;

// Build complete API URL
export const buildApiUrl = (endpoint: string, params?: URLSearchParams | Record<string, string>) => {
  const baseUrl = getApiBaseUrl();
  let url = `${baseUrl}${endpoint}`;
  
  if (params) {
    const searchParams = params instanceof URLSearchParams ? params : new URLSearchParams(params);
    url += `?${searchParams.toString()}`;
  }
  
  console.log('🔗 Built API URL:', url);
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

// Debug function
export const debugApiConfig = () => {
  return {
    baseUrl: getApiBaseUrl(),
    hostname: typeof window !== 'undefined' ? window.location.hostname : 'server-side',
    isDevelopment: typeof window !== 'undefined' && (
      window.location.hostname === 'localhost' || 
      window.location.hostname === '127.0.0.1'
    ),
    envVar: typeof process !== 'undefined' ? process.env.NEXT_PUBLIC_API_URL : 'not available',
  };
};

export default {
  getApiBaseUrl,
  API_BASE_URL: getApiBaseUrl(),
  API_ENDPOINTS,
  buildApiUrl,
  API_CONFIG,
  debugApiConfig,
};