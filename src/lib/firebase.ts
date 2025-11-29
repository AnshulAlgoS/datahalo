// Firebase Configuration and Initialization
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

// Firebase configuration from environment variables (with fallback to hardcoded for backwards compatibility)
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyD3vcgqOaH9V3-2WxIoRHqWic4zgsiEmdM",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "datahalo-a44cd.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "datahalo-a44cd",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "datahalo-a44cd.firebasestorage.app",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "896405020542",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:896405020542:web:a93b1f1ed53520b756dd2f",
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || "G-E0ERNE0T69"
};

// Validate Firebase configuration
if (!firebaseConfig.apiKey || !firebaseConfig.projectId) {
  console.error("❌ Firebase configuration is missing required fields!");
  console.error("Make sure VITE_FIREBASE_* environment variables are set.");
}

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = typeof window !== 'undefined' ? getAnalytics(app) : null;
const auth = getAuth(app);
const db = getFirestore(app);

export { app, analytics, auth, db };
