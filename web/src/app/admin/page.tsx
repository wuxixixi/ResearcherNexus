"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import { ArrowLeft, Users, Settings } from "lucide-react";

import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "~/components/ui/table";
import { ProtectedRoute } from "~/components/auth/ProtectedRoute";

import { useAuth } from "~/hooks/useAuth";

interface User {
  username: string;
  role: string;
  daily_limit: number;
  used_today: number;
  last_used_date: string;
}

function AdminContent() {
  const { username, logout } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editingUser, setEditingUser] = useState<string | null>(null);
  const [newLimit, setNewLimit] = useState("");
  const router = useRouter();

  // 检查是否为管理员
  useEffect(() => {
    const userRole = localStorage.getItem("userRole");
    if (userRole !== "admin") {
      router.push("/chat");
    }
  }, [router]);

  // 获取用户列表
  const fetchUsers = async () => {
    try {
      const response = await fetch("/api/admin/users");
      const data = await response.json();
      
      if (response.ok) {
        setUsers(data.users);
      } else {
        setError(data.error ?? "获取用户列表失败");
      }
    } catch {
      setError("网络错误，请重试");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchUsers();
  }, []);

  // 更新用户限制
  const updateUserLimit = async (targetUsername: string, newDailyLimit: number) => {
    try {
      const response = await fetch("/api/admin/update-limit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          username: targetUsername, 
          daily_limit: newDailyLimit 
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setUsers(users.map(user => 
          user.username === targetUsername 
            ? { ...user, daily_limit: newDailyLimit }
            : user
        ));
        setEditingUser(null);
        setNewLimit("");
      } else {
        setError(data.error ?? "更新失败");
      }
    } catch {
      setError("网络错误，请重试");
    }
  };

  // 重置用户今日使用次数
  const resetUserUsage = async (targetUsername: string) => {
    try {
      const response = await fetch("/api/admin/reset-usage", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username: targetUsername }),
      });

      const data = await response.json();

      if (response.ok) {
        setUsers(users.map(user => 
          user.username === targetUsername 
            ? { ...user, used_today: 0 }
            : user
        ));
      } else {
        setError(data.error ?? "重置失败");
      }
    } catch {
      setError("网络错误，请重试");
    }
  };

  // 删除用户
  const deleteUser = async (targetUsername: string) => {
    if (!confirm(`确定要删除用户 "${targetUsername}" 吗？此操作不可撤销。`)) {
      return;
    }

    try {
      const response = await fetch("/api/admin/delete-user", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username: targetUsername }),
      });

      const data = await response.json();

      if (response.ok) {
        setUsers(users.filter(user => user.username !== targetUsername));
      } else {
        setError(data.error ?? "删除失败");
      }
    } catch {
      setError("网络错误，请重试");
    }
  };

  const handleEditLimit = (targetUsername: string, currentLimit: number) => {
    setEditingUser(targetUsername);
    setNewLimit(currentLimit.toString());
  };

  const handleSaveLimit = (targetUsername: string) => {
    const limit = parseInt(newLimit);
    if (isNaN(limit) || limit < 0) {
      setError("请输入有效的数字");
      return;
    }
    void updateUserLimit(targetUsername, limit);
  };

  if (loading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p>加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-4">
      {/* 导航栏 */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" asChild>
            <Link href="/chat" className="flex items-center gap-2">
              <ArrowLeft className="h-4 w-4" />
              返回聊天
            </Link>
          </Button>
          <div className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            <h1 className="text-2xl font-bold">管理员面板</h1>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">
            管理员: {username}
          </span>
          <Button variant="outline" size="sm" onClick={logout}>
            登出
          </Button>
        </div>
      </div>

      {/* 用户管理卡片 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            用户管理
          </CardTitle>
          <CardDescription>
            管理用户的每日使用限制和使用情况
          </CardDescription>
        </CardHeader>
        <CardContent>
          {error && (
            <div className="text-sm text-red-600 mb-4 p-3 bg-red-50 rounded">
              {error}
            </div>
          )}

          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>用户名</TableHead>
                <TableHead>角色</TableHead>
                <TableHead>每日限制</TableHead>
                <TableHead>今日已用</TableHead>
                <TableHead>剩余次数</TableHead>
                <TableHead>最后使用</TableHead>
                <TableHead>重置操作</TableHead>
                <TableHead>删除操作</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.username}>
                  <TableCell className="font-medium">{user.username}</TableCell>
                  <TableCell>
                    <span className={`px-2 py-1 rounded text-xs ${
                      user.role === 'admin' 
                        ? 'bg-red-100 text-red-800' 
                        : 'bg-blue-100 text-blue-800'
                    }`}>
                      {user.role === 'admin' ? '管理员' : '普通用户'}
                    </span>
                  </TableCell>
                  <TableCell>
                    {editingUser === user.username ? (
                      <div className="flex items-center gap-2">
                        <Input
                          type="number"
                          value={newLimit}
                          onChange={(e) => setNewLimit(e.target.value)}
                          className="w-20"
                          min="0"
                        />
                        <Button 
                          size="sm" 
                          onClick={() => handleSaveLimit(user.username)}
                        >
                          保存
                        </Button>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => setEditingUser(null)}
                        >
                          取消
                        </Button>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <span>{user.daily_limit}</span>
                        <Button 
                          size="sm" 
                          variant="ghost"
                          onClick={() => handleEditLimit(user.username, user.daily_limit)}
                        >
                          编辑
                        </Button>
                      </div>
                    )}
                  </TableCell>
                  <TableCell>{user.used_today}</TableCell>
                  <TableCell>{user.daily_limit - user.used_today}</TableCell>
                  <TableCell>{user.last_used_date || "从未使用"}</TableCell>
                  <TableCell>
                    <Button 
                      size="sm" 
                      variant="outline"
                      onClick={() => resetUserUsage(user.username)}
                      disabled={user.used_today === 0}
                    >
                      重置今日使用
                    </Button>
                  </TableCell>
                  <TableCell>
                    <Button 
                      size="sm" 
                      variant="destructive"
                      onClick={() => deleteUser(user.username)}
                      disabled={user.role === 'admin'}
                      className={user.role === 'admin' ? 'opacity-50 cursor-not-allowed' : ''}
                    >
                      {user.role === 'admin' ? '不可删除' : '删除用户'}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

export default function AdminPage() {
  return (
    <ProtectedRoute>
      <AdminContent />
    </ProtectedRoute>
  );
} 