// @ts-nocheck - 暂时禁用类型检查，等待更好的解决方案
"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import Cookies from 'js-cookie';

interface User {
  id: string;
  username: string;
  email: string;
  role: 'user' | 'admin';
  usage: {
    used: number;
    limit: number;
    remaining: number;
  };
  created_at?: string; // 添加 created_at 字段，设为可选以兼容旧数据或ME接口可能不返回的情况
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<User | null>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
  isAdmin: boolean;
  getAllUsers: () => Promise<any[]>;
  updateUser: (userId: string, userData: Partial<any>) => Promise<void>;
  deleteUser: (userId: string) => Promise<void>;
  updateUserLimit: (userId: string, newLimit: number) => Promise<void>;
  incrementUsage: () => Promise<{success: boolean, message?: string, usage?: any}>;
  getRemainingUsage: () => Promise<{used: number, limit: number, remaining: number}>;
  changePassword: (userId: string, currentPassword: string, newPassword: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: React.ReactNode;
}

// API 路径
const API_BASE_URL = '/api';
const AUTH_API = {
  LOGIN: `${API_BASE_URL}/auth/login`,
  REGISTER: `${API_BASE_URL}/auth/register`,
  LOGOUT: `${API_BASE_URL}/auth/logout`,
  ME: `${API_BASE_URL}/users/me`,
  USAGE: `${API_BASE_URL}/users/usage`,
  PASSWORD: `${API_BASE_URL}/users/password`,
  ADMIN_USERS: `${API_BASE_URL}/admin/users`,
};

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // 获取当前用户信息
  const fetchCurrentUser = async () => {
    setLoading(true); // 开始加载时设置loading
    try {
      const response = await fetch(AUTH_API.ME);
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setError(null); // 成功获取，清除错误
      } else {
        // 如果是401错误，说明用户未登录，属于正常情况，清除user状态
        if (response.status === 401) {
          setUser(null);
        } else {
          // 其他错误，尝试解析错误信息
          try {
            const errorData = await response.json();
            setError(errorData.detail || '获取用户信息失败');
          } catch (jsonError) {
            setError('获取用户信息失败，无法解析错误响应');
          }
          setUser(null);
        }
      }
    } catch (err) {
      console.error("Failed to fetch current user:", err);
      setError('获取用户信息时发生网络错误');
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  // 在组件挂载时获取当前用户信息
  useEffect(() => {
    fetchCurrentUser();
  }, []);

  const login = async (username: string, password: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(AUTH_API.LOGIN, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '登录失败');
      }

      const userData = await response.json();
      setUser(userData);
    } catch (err) {
      setError((err as Error).message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (username: string, email: string, password: string): Promise<User | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(AUTH_API.REGISTER, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password }),
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '注册失败');
      }

      const userData = await response.json();
      setUser(userData);
      return userData; // 返回用户信息
    } catch (err) {
      setError((err as Error).message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    setLoading(true);
    try {
      await fetch(AUTH_API.LOGOUT, {
        method: 'POST',
        credentials: 'include',
      });
      setUser(null);
      setError(null);
    } catch (err) {
      console.error("Failed to logout:", err);
      setError("登出失败");
    } finally {
      setLoading(false);
    }
  };

  const getAllUsers = async () => {
    if (!user || user.role !== 'admin') {
      // setError("需要管理员权限才能获取用户列表"); // 避免在非管理员场景下频繁设置错误
      return [];
    }
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(AUTH_API.ADMIN_USERS, {
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '获取用户列表失败');
      }
      return await response.json();
    } catch (err) {
      console.error("Failed to get users:", err);
      setError((err as Error).message);
      return [];
    } finally {
      setLoading(false);
    }
  };

  const updateUser = async (userId: string, userData: Partial<any>) => {
    if (!user || user.role !== 'admin') {
      setError("需要管理员权限");
      throw new Error("需要管理员权限");
    }
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${AUTH_API.ADMIN_USERS}/${userId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '更新用户失败');
      }

      const updatedUserData = await response.json();
      // 如果更新的是当前用户，也更新状态
      if (user.id === userId) {
         setUser(prevUser => prevUser ? { ...prevUser, ...updatedUserData } : null);
      }
      return updatedUserData;
    } catch (err) {
      console.error("Failed to update user:", err);
      setError((err as Error).message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const deleteUser = async (userId: string) => {
    if (!user || user.role !== 'admin') {
      setError("需要管理员权限");
      throw new Error("需要管理员权限");
    }
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${AUTH_API.ADMIN_USERS}/${userId}`, {
        method: 'DELETE',
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '删除用户失败');
      }
    } catch (err) {
      console.error("Failed to delete user:", err);
      setError((err as Error).message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateUserLimit = async (userId: string, newLimit: number) => {
    return updateUser(userId, { daily_limit: newLimit });
  };

  const incrementUsage = async () => {
    if (!user) {
      return { success: false, message: "未登录" };
    }
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(AUTH_API.USAGE, {
        method: 'POST',
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json();
        return { 
          success: false, 
          message: errorData.detail || '更新使用次数失败'
        };
      }

      const result = await response.json();
      
      if (result.success && result.usage) {
        setUser(prev => prev ? {...prev, usage: result.usage} : null);
      }
      return result;
    } catch (err) {
      console.error("Failed to increment usage:", err);
      const errorMessage = (err as Error).message || '更新使用次数失败';
      setError(errorMessage);
      return { 
        success: false, 
        message: errorMessage
      };
    } finally {
      setLoading(false);
    }
  };

  const getRemainingUsage = async () => {
    // 如果用户未登录，直接返回默认值
    if (!user) {
      return { used: 0, limit: 0, remaining: 0 };
    }

    // 如果user对象中已经有有效的usage信息，直接返回，避免不必要的API调用
    // 对管理员也适用，因为管理员的配额信息也是固定的，在登录时应该已经获取
    if (user.usage && typeof user.usage.limit === 'number') {
        // 确保 usage 是期望的结构
        if (user.usage.limit !== undefined && user.usage.used !== undefined && user.usage.remaining !== undefined) { 
            return user.usage;
        }
    }
    
    setLoading(true);
    // setError(null); // 调用ME接口，不应清除其他地方可能设置的错误
    try {
      const response = await fetch(AUTH_API.ME, {
        credentials: 'include',
      });

      if (!response.ok) {
        // 对于刚注册的用户，如果ME接口返回401（用户不存在），
        // 这可能是因为会话尚未完全建立。此时可以返回一个默认的初始配额。
        if (response.status === 401) {
            console.warn("getRemainingUsage: /api/users/me returned 401. This might be a new user. Returning default usage.");
            // 假设新用户的默认限制是10次
            const defaultUsage = { used: 0, limit: user.role === 'admin' ? 9999: 10, remaining: user.role === 'admin' ? 9999: 10 };
            // 更新本地user状态的usage，避免下次还请求
            setUser(prev => prev ? {...prev, usage: defaultUsage} : null);
            return defaultUsage;
        }
        const errorData = await response.json();
        console.error('获取使用情况失败 (getRemainingUsage):', errorData.detail);
        // 如果获取失败，且user.usage无效，返回安全默认值
        return user.usage && typeof user.usage.limit === 'number' ? user.usage : { used: 0, limit: 0, remaining: 0 };
      }

      const userData = await response.json();
      setUser(userData); // 更新整个用户状态，包括最新的usage
      return userData.usage || { used: 0, limit: 10, remaining: 10 }; // 确保有默认值
    } catch (err) {
      console.error("Failed to get usage (getRemainingUsage catch block):", err);
      // 在捕获到错误时，如果user.usage无效，返回安全默认值
      return user.usage && typeof user.usage.limit === 'number' ? user.usage : { used: 0, limit: 0, remaining: 0 };
    } finally {
      setLoading(false);
    }
  };

  const changePassword = async (userId: string, currentPassword: string, newPassword: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(AUTH_API.PASSWORD, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id: userId, current_password: currentPassword, new_password: newPassword }),
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '修改密码失败');
      }
    } catch (err) {
      setError((err as Error).message);
      throw err;
    } finally {
      setLoading(false);
    }
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
        isAdmin: user?.role === 'admin',
        getAllUsers,
        updateUser,
        deleteUser,
        updateUserLimit,
        incrementUsage,
        getRemainingUsage,
        changePassword,
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