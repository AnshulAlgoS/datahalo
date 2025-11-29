// Firebase Configuration and Initialization
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyD3vcgqOaH9V3-2WxIoRHqWic4zgsiEmdM",
  authDomain: "datahalo-a44cd.firebaseapp.com",
  projectId: "datahalo-a44cd",
  storageBucket: "datahalo-a44cd.firebasestorage.app",
  messagingSenderId: "896405020542",
  appId: "1:896405020542:web:a93b1f1ed53520b756dd2f",
  measurementId: "G-E0ERNE0T69"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const auth = getAuth(app);
const db = getFirestore(app);

export { app, analytics, auth, db };
