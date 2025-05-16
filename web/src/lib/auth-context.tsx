"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import Cookies from 'js-cookie';

interface User {
  id: string;
  username: string;
  email: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: React.ReactNode;
}

// Mock user database for demonstration (in a real app, this would be a server-side database)
const USERS_STORAGE_KEY = "researchernexus_users";
const CURRENT_USER_KEY = "researchernexus_current_user";

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Load user from localStorage on initial render
  useEffect(() => {
    const storedUser = localStorage.getItem(CURRENT_USER_KEY);
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  // Initialize users database if it doesn't exist
  useEffect(() => {
    const users = localStorage.getItem(USERS_STORAGE_KEY);
    if (!users) {
      localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify([]));
    }
  }, []);

  const login = async (username: string, password: string) => {
    setLoading(true);
    setError(null);

    try {
      // Simulate API request delay
      await new Promise((resolve) => setTimeout(resolve, 500));

      const users = JSON.parse(localStorage.getItem(USERS_STORAGE_KEY) || "[]");
      const foundUser = users.find(
        (u: any) => u.username === username && u.password === password
      );

      if (!foundUser) {
        throw new Error("Invalid username or password");
      }

      // Create a user object without the password for storage in state
      const authenticatedUser = {
        id: foundUser.id,
        username: foundUser.username,
        email: foundUser.email,
      };

      // Store user in localStorage
      localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(authenticatedUser));
      
      // Set cookie for middleware authentication
      Cookies.set(CURRENT_USER_KEY, JSON.stringify(authenticatedUser), { 
        expires: 7, // Expires in 7 days
        path: '/', 
        secure: process.env.NODE_ENV === 'production', 
        sameSite: 'strict'
      });
      
      setUser(authenticatedUser);
    } catch (err) {
      setError((err as Error).message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (username: string, email: string, password: string) => {
    setLoading(true);
    setError(null);

    try {
      // Simulate API request delay
      await new Promise((resolve) => setTimeout(resolve, 500));

      const users = JSON.parse(localStorage.getItem(USERS_STORAGE_KEY) || "[]");
      
      // Check if username already exists
      if (users.some((u: any) => u.username === username)) {
        throw new Error("Username already exists");
      }

      // Check if email already exists
      if (users.some((u: any) => u.email === email)) {
        throw new Error("Email already exists");
      }

      // Create new user
      const newUser = {
        id: `user-${Date.now()}`,
        username,
        email,
        password, // In a real app, this would be hashed
      };

      // Add user to database
      users.push(newUser);
      localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(users));

      // Create a user object without the password for storage in state
      const authenticatedUser = {
        id: newUser.id,
        username: newUser.username,
        email: newUser.email,
      };

      // Store user in localStorage
      localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(authenticatedUser));
      
      // Set cookie for middleware authentication
      Cookies.set(CURRENT_USER_KEY, JSON.stringify(authenticatedUser), { 
        expires: 7, // Expires in 7 days
        path: '/', 
        secure: process.env.NODE_ENV === 'production', 
        sameSite: 'strict'
      });
      
      setUser(authenticatedUser);
    } catch (err) {
      setError((err as Error).message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem(CURRENT_USER_KEY);
    // Remove cookie
    Cookies.remove(CURRENT_USER_KEY, { path: '/' });
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        error,
        login,
        register,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}; 