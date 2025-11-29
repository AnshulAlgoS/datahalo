// Authentication Context Provider
import React, { createContext, useContext, useEffect, useState } from "react";
import {
  User,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  GoogleAuthProvider,
  signInWithPopup,
  updateProfile
} from "firebase/auth";
import { doc, setDoc, getDoc } from "firebase/firestore";
import { auth, db } from "@/lib/firebase";

export type UserRole = "student" | "teacher" | "admin";

export interface UserProfile {
  uid: string;
  email: string;
  displayName: string;
  role: UserRole;
  institution?: string;
  department?: string;
  studentId?: string;
  teacherId?: string;
  createdAt: string;
  photoURL?: string;
}

interface AuthContextType {
  currentUser: User | null;
  userProfile: UserProfile | null;
  loading: boolean;
  signup: (email: string, password: string, displayName: string, role: UserRole, additionalInfo?: any) => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loginWithGoogle: (role: UserRole) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  // Fetch user profile from Firestore
  const fetchUserProfile = async (uid: string) => {
    try {
      const docRef = doc(db, "users", uid);
      const docSnap = await getDoc(docRef);
      
      if (docSnap.exists()) {
        setUserProfile(docSnap.data() as UserProfile);
      }
    } catch (error) {
      console.error("Error fetching user profile:", error);
    }
  };

  // Signup function
  const signup = async (
    email: string,
    password: string,
    displayName: string,
    role: UserRole,
    additionalInfo?: any
  ) => {
    try {
      console.log("Starting signup process...");
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      const user = userCredential.user;
      console.log("User created in Firebase Auth:", user.uid);

      // Update display name
      await updateProfile(user, { displayName });
      console.log("Display name updated");

      // Create user profile in Firestore
      const profile: UserProfile = {
        uid: user.uid,
        email: user.email!,
        displayName,
        role,
        createdAt: new Date().toISOString(),
        ...additionalInfo
      };

      console.log("Saving profile to Firestore:", profile);
      await setDoc(doc(db, "users", user.uid), profile);
      console.log("Profile saved successfully");
      setUserProfile(profile);
    } catch (error: any) {
      console.error("Signup error:", error);
      throw new Error(error.message || "Failed to create account");
    }
  };

  // Login function
  const login = async (email: string, password: string) => {
    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    // Fetch user profile immediately after login
    await fetchUserProfile(userCredential.user.uid);
  };

  // Logout function
  const logout = async () => {
    await signOut(auth);
    setUserProfile(null);
  };

  // Google Sign-In
  const loginWithGoogle = async (role: UserRole) => {
    const provider = new GoogleAuthProvider();
    const userCredential = await signInWithPopup(auth, provider);
    const user = userCredential.user;

    // Check if user profile exists
    const docRef = doc(db, "users", user.uid);
    const docSnap = await getDoc(docRef);

    if (!docSnap.exists()) {
      // Create new profile for first-time Google sign-in
      const profile: UserProfile = {
        uid: user.uid,
        email: user.email!,
        displayName: user.displayName || user.email!.split("@")[0],
        role,
        createdAt: new Date().toISOString(),
        photoURL: user.photoURL || undefined
      };

      await setDoc(docRef, profile);
      setUserProfile(profile);
    } else {
      // Fetch existing profile
      await fetchUserProfile(user.uid);
    }
  };

  // Listen to auth state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setCurrentUser(user);
      
      if (user) {
        await fetchUserProfile(user.uid);
      } else {
        setUserProfile(null);
      }
      
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const value: AuthContextType = {
    currentUser,
    userProfile,
    loading,
    signup,
    login,
    logout,
    loginWithGoogle
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
