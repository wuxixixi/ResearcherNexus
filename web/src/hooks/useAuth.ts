"use client";

import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [username, setUsername] = useState<string>("");
  const [role, setRole] = useState<string>("");
  const [dailyLimit, setDailyLimit] = useState<number>(0);
  const [usedToday, setUsedToday] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const router = useRouter();

  useEffect(() => {
    // 检查本地存储中的认证状态
    const authStatus = localStorage.getItem("isAuthenticated");
    const storedUsername = localStorage.getItem("username");
    const storedRole = localStorage.getItem("userRole");
    const storedDailyLimit = localStorage.getItem("dailyLimit");
    const storedUsedToday = localStorage.getItem("usedToday");
    
    if (authStatus === "true" && storedUsername) {
      setIsAuthenticated(true);
      setUsername(storedUsername);
      setRole(storedRole ?? "user");
      setDailyLimit(parseInt(storedDailyLimit ?? "10"));
      setUsedToday(parseInt(storedUsedToday ?? "0"));
    }
    
    setIsLoading(false);
  }, []);

  const login = (userData: {
    username: string;
    role: string;
    daily_limit: number;
    used_today: number;
  }) => {
    localStorage.setItem("isAuthenticated", "true");
    localStorage.setItem("username", userData.username);
    localStorage.setItem("userRole", userData.role);
    localStorage.setItem("dailyLimit", userData.daily_limit.toString());
    localStorage.setItem("usedToday", userData.used_today.toString());
    
    setIsAuthenticated(true);
    setUsername(userData.username);
    setRole(userData.role);
    setDailyLimit(userData.daily_limit);
    setUsedToday(userData.used_today);
  };

  const logout = () => {
    localStorage.removeItem("isAuthenticated");
    localStorage.removeItem("username");
    localStorage.removeItem("userRole");
    localStorage.removeItem("dailyLimit");
    localStorage.removeItem("usedToday");
    
    setIsAuthenticated(false);
    setUsername("");
    setRole("");
    setDailyLimit(0);
    setUsedToday(0);
    router.push("/auth/login");
  };

  const updateUsage = (newUsedToday: number) => {
    setUsedToday(newUsedToday);
    localStorage.setItem("usedToday", newUsedToday.toString());
  };

  // 刷新使用次数的函数
  const refreshUsage = () => {
    const storedUsedToday = localStorage.getItem("usedToday");
    if (storedUsedToday) {
      setUsedToday(parseInt(storedUsedToday));
    }
  };

  const getRemainingUsage = () => {
    return Math.max(0, dailyLimit - usedToday);
  };

  const canUseService = () => {
    return usedToday < dailyLimit;
  };

  return {
    isAuthenticated,
    username,
    role,
    dailyLimit,
    usedToday,
    isLoading,
    login,
    logout,
    updateUsage,
    refreshUsage,
    getRemainingUsage,
    canUseService,
  };
} 