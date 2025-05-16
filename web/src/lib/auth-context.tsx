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
    date: string; // 格式YYYY-MM-DD
    count: number;
  }[];
  dailyLimit: number;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isAdmin: boolean;
  getAllUsers: () => any[];
  updateUser: (userId: string, userData: Partial<any>) => Promise<void>;
  deleteUser: (userId: string) => Promise<void>;
  updateUserLimit: (userId: string, newLimit: number) => Promise<void>;
  incrementUsage: () => Promise<{success: boolean, message?: string}>;
  getRemainingUsage: () => {used: number, limit: number, remaining: number};
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: React.ReactNode;
}

// 用户数据存储的键名
const USERS_STORAGE_KEY = "researchernexus_users";
const CURRENT_USER_KEY = "researchernexus_current_user";

// 默认管理员用户
const DEFAULT_ADMIN = {
  id: `admin-${Date.now()}`,
  username: 'admin',
  email: 'admin@researchernexus.com',
  password: 'admin123', // 实际应用中应该使用加密密码
  role: 'admin' as const,
  usage: [],
  dailyLimit: 9999,
};

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // 从localStorage加载当前用户
  useEffect(() => {
    const storedUser = localStorage.getItem(CURRENT_USER_KEY);
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (e) {
        console.error("Failed to parse stored user:", e);
        localStorage.removeItem(CURRENT_USER_KEY);
      }
    }
    setLoading(false);
  }, []);

  // 确保用户数据库初始化且包含管理员账号
  useEffect(() => {
    // 读取现有用户
    let users: any[] = [];
    try {
      const storedUsers = localStorage.getItem(USERS_STORAGE_KEY);
      users = storedUsers ? JSON.parse(storedUsers) : [];
    } catch (e) {
      console.error("Failed to parse stored users:", e);
      users = [];
    }

    let needsUpdate = false;

    // 确保所有用户都有必要的字段
    users = users.map(user => {
      let updated = false;
      
      if (!user.role) {
        user.role = user.username === 'admin' ? 'admin' : 'user';
        updated = true;
      }
      
      if (!user.usage) {
        user.usage = [];
        updated = true;
      }
      
      if (!user.dailyLimit) {
        user.dailyLimit = user.role === 'admin' ? 9999 : 10;
        updated = true;
      }

      if (updated) {
        needsUpdate = true;
      }
      
      return user;
    });

    // 检查管理员账户是否存在
    const adminExists = users.some(u => u.username === 'admin' && u.role === 'admin');
    
    // 如果没有管理员账户，添加默认管理员
    if (!adminExists) {
      users.push({...DEFAULT_ADMIN});
      needsUpdate = true;
    } else {
      // 确保admin账户的密码正确
      const adminIndex = users.findIndex(u => u.username === 'admin');
      if (adminIndex !== -1 && users[adminIndex].password !== DEFAULT_ADMIN.password) {
        users[adminIndex].password = DEFAULT_ADMIN.password;
        needsUpdate = true;
      }
    }

    // 保存更新后的用户数据
    if (needsUpdate) {
      localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(users));
      console.log("用户数据已更新，管理员账户已确保存在");
    }
  }, []);

  const login = async (username: string, password: string) => {
    setLoading(true);
    setError(null);

    try {
      // 模拟API请求延迟
      await new Promise((resolve) => setTimeout(resolve, 500));

      // 从localStorage获取用户数据
      let users: any[] = [];
      try {
        const storedUsers = localStorage.getItem(USERS_STORAGE_KEY);
        users = storedUsers ? JSON.parse(storedUsers) : [];
      } catch (e) {
        console.error("Failed to parse stored users:", e);
        throw new Error("系统错误，请稍后再试");
      }

      // 查找匹配的用户
      const foundUser = users.find(
        (u: any) => u.username === username && u.password === password
      );

      if (!foundUser) {
        throw new Error("Invalid username or password");
      }

      // 创建不包含密码的用户对象保存到状态中
      const authenticatedUser: User = {
        id: foundUser.id,
        username: foundUser.username,
        email: foundUser.email,
        role: (foundUser.role || 'user') as 'user' | 'admin',
        usage: foundUser.usage || [],
        dailyLimit: foundUser.dailyLimit || 10,
      };

      // 存储到 localStorage
      localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(authenticatedUser));
      
      // 设置 cookie 用于中间件认证
      Cookies.set(CURRENT_USER_KEY, JSON.stringify(authenticatedUser), { 
        expires: 7, // 7天后过期
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
      // 模拟API请求延迟
      await new Promise((resolve) => setTimeout(resolve, 500));

      // 读取现有用户
      let users: any[] = [];
      try {
        const storedUsers = localStorage.getItem(USERS_STORAGE_KEY);
        users = storedUsers ? JSON.parse(storedUsers) : [];
      } catch (e) {
        console.error("Failed to parse stored users:", e);
        users = [];
      }
      
      // 检查用户名是否已存在
      if (users.some((u: any) => u.username === username)) {
        throw new Error("Username already exists");
      }

      // 检查邮箱是否已存在
      if (users.some((u: any) => u.email === email)) {
        throw new Error("Email already exists");
      }

      // 创建新用户
      const newUser = {
        id: `user-${Date.now()}`,
        username,
        email: email ?? "", // 使用空字符串作为备选
        password, // 实际应用中应该使用加密密码
        role: 'user' as const,
        usage: [],
        dailyLimit: 10,
      };

      // 添加用户到数据库
      users.push(newUser);
      localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(users));

      // 创建不包含密码的用户对象保存到状态中
      const authenticatedUser: User = {
        id: newUser.id,
        username: newUser.username,
        email: newUser.email,
        role: newUser.role,
        usage: newUser.usage,
        dailyLimit: newUser.dailyLimit,
      };

      // 存储到 localStorage
      localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(authenticatedUser));
      
      // 设置 cookie 用于中间件认证
      Cookies.set(CURRENT_USER_KEY, JSON.stringify(authenticatedUser), { 
        expires: 7, // 7天后过期
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
    // 删除 cookie
    Cookies.remove(CURRENT_USER_KEY, { path: '/' });
    setUser(null);
  };

  // 获取所有用户
  const getAllUsers = () => {
    try {
      const users = JSON.parse(localStorage.getItem(USERS_STORAGE_KEY) || "[]");
      // 不返回密码
      return users.map((user: any) => ({
        ...user,
        password: undefined
      }));
    } catch (e) {
      console.error("Failed to get users:", e);
      return [];
    }
  };

  // 更新用户信息
  const updateUser = async (userId: string, userData: Partial<any>) => {
    try {
      const users = JSON.parse(localStorage.getItem(USERS_STORAGE_KEY) || "[]");
      const userIndex = users.findIndex((u: any) => u.id === userId);
      
      if (userIndex === -1) {
        throw new Error("User not found");
      }

      // 更新用户数据，但保持密码不变
      const updatedUser = { ...users[userIndex], ...userData };
      users[userIndex] = updatedUser;
      
      // 保存更新后的用户数据
      localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(users));
      
      // 如果更新的是当前用户，也更新状态
      if (user && user.id === userId) {
        const updatedCurrentUser = {
          ...user,
          ...userData,
        } as User;
        setUser(updatedCurrentUser);
        localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(updatedCurrentUser));
        
        // 更新cookie
        Cookies.set(CURRENT_USER_KEY, JSON.stringify(updatedCurrentUser), { 
          expires: 7,
          path: '/', 
          secure: process.env.NODE_ENV === 'production', 
          sameSite: 'strict'
        });
      }
    } catch (error) {
      console.error("Failed to update user:", error);
      throw error;
    }
  };

  // 删除用户
  const deleteUser = async (userId: string) => {
    try {
      // 检查是否是试图删除管理员账号
      const users = JSON.parse(localStorage.getItem(USERS_STORAGE_KEY) || "[]");
      const userToDelete = users.find((u: any) => u.id === userId);
      
      if (!userToDelete) {
        throw new Error("User not found");
      }
      
      if (userToDelete.role === 'admin') {
        throw new Error("Cannot delete admin user");
      }
      
      // 删除用户
      const updatedUsers = users.filter((u: any) => u.id !== userId);
      localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(updatedUsers));
      
      // 如果删除的是当前登录用户，则登出
      if (user && user.id === userId) {
        logout();
      }
    } catch (error) {
      console.error("Failed to delete user:", error);
      throw error;
    }
  };

  // 更新用户每日使用限制
  const updateUserLimit = async (userId: string, newLimit: number) => {
    if (newLimit < 0) {
      throw new Error("Limit cannot be negative");
    }
    
    await updateUser(userId, { dailyLimit: newLimit });
  };

  // 增加用户当日使用次数
  const incrementUsage = async () => {
    if (!user) {
      return { success: false, message: "No user logged in" };
    }
    
    // 获取当前日期
    const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    
    // 如果是管理员，不限制使用
    if (user.role === 'admin') {
      return { success: true };
    }
    
    // 获取当天使用情况
    const todayUsage = user.usage.find(u => u.date === today);
    
    // 如果已达到每日使用限制，则返回错误
    if (todayUsage && todayUsage.count >= user.dailyLimit) {
      return { 
        success: false, 
        message: `您今日的使用次数已达上限(${user.dailyLimit}次)，请明天再试或联系管理员增加配额`
      };
    }
    
    // 更新用户使用情况
    const updatedUsage = [...user.usage];
    
    if (todayUsage) {
      // 更新现有的使用记录
      const index = updatedUsage.findIndex(u => u.date === today);
      updatedUsage[index] = { ...todayUsage, count: todayUsage.count + 1 };
    } else {
      // 添加新的使用记录
      updatedUsage.push({ date: today, count: 1 });
    }
    
    const updatedUser = { ...user, usage: updatedUsage } as User;
    
    // 更新状态
    setUser(updatedUser);
    localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(updatedUser));
    Cookies.set(CURRENT_USER_KEY, JSON.stringify(updatedUser), { 
      expires: 7,
      path: '/', 
      secure: process.env.NODE_ENV === 'production', 
      sameSite: 'strict'
    });
    
    // 同时更新用户数据库
    try {
      const users = JSON.parse(localStorage.getItem(USERS_STORAGE_KEY) || "[]");
      const userIndex = users.findIndex((u: any) => u.id === user.id);
      
      if (userIndex !== -1) {
        users[userIndex] = {
          ...users[userIndex],
          usage: updatedUsage
        };
        localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(users));
      }
    } catch (error) {
      console.error("Failed to update usage in users database:", error);
    }
    
    return { success: true };
  };

  // 获取用户剩余使用次数
  const getRemainingUsage = () => {
    if (!user) {
      return { used: 0, limit: 0, remaining: 0 };
    }
    
    if (user.role === 'admin') {
      return { used: 0, limit: 9999, remaining: 9999 };
    }
    
    const today = new Date().toISOString().split('T')[0];
    const todayUsage = user.usage.find(u => u.date === today);
    const used = todayUsage ? todayUsage.count : 0;
    const limit = user.dailyLimit;
    const remaining = Math.max(0, limit - used);
    
    return { used, limit, remaining };
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