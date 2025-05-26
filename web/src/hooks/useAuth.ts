"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [username, setUsername] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const router = useRouter();

  useEffect(() => {
    // 检查本地存储中的认证状态
    const authStatus = localStorage.getItem("isAuthenticated");
    const storedUsername = localStorage.getItem("username");
    
    if (authStatus === "true" && storedUsername) {
      setIsAuthenticated(true);
      setUsername(storedUsername);
    }
    
    setIsLoading(false);
  }, []);

  const login = (username: string) => {
    localStorage.setItem("isAuthenticated", "true");
    localStorage.setItem("username", username);
    setIsAuthenticated(true);
    setUsername(username);
  };

  const logout = () => {
    localStorage.removeItem("isAuthenticated");
    localStorage.removeItem("username");
    setIsAuthenticated(false);
    setUsername("");
    router.push("/auth/login");
  };

  return {
    isAuthenticated,
    username,
    isLoading,
    login,
    logout,
  };
} 