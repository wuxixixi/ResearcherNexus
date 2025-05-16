"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Home, User, Mail, KeyRound, Calendar, BarChart, MessageSquare } from "lucide-react";
import Link from "next/link";

import { useAuth } from "~/lib/auth-context";
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";
import { Progress } from "~/components/ui/progress";

export default function ProfilePage() {
  const { user, isAuthenticated, getRemainingUsage } = useAuth();
  const router = useRouter();
  
  // 获取用户使用情况
  const { used, limit, remaining } = getRemainingUsage();
  const usagePercentage = limit > 0 ? (used / limit) * 100 : 0;
  
  // 检查用户是否已登录
  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  if (!user) {
    return null; // 如果没有用户数据，不显示内容
  }

  // 计算账户创建时间（从用户ID中提取）
  const createdAt = (() => {
    // 假设ID格式是 user-{timestamp}
    const timestampMatch = user.id.match(/\d+/);
    if (timestampMatch) {
      const timestamp = parseInt(timestampMatch[0]);
      return new Date(timestamp).toLocaleDateString("zh-CN");
    }
    return "未知";
  })();

  return (
    <div className="container mx-auto p-6">
      <header className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold mb-2">个人信息</h1>
          <p className="text-muted-foreground">查看和管理您的账户信息</p>
        </div>
        <Link href="/">
          <Button variant="outline" className="flex items-center gap-2">
            <Home className="h-4 w-4" />
            返回主页
          </Button>
        </Link>
      </header>

      <div className="grid gap-6 md:grid-cols-2">
        {/* 基本信息卡片 */}
        <Card>
          <CardHeader>
            <CardTitle>账户信息</CardTitle>
            <CardDescription>您的基本账户信息</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                <User className="h-8 w-8 text-primary" />
              </div>
              <div>
                <p className="text-2xl font-medium">{user.username}</p>
                <p className="text-sm text-muted-foreground">
                  {user.role === 'admin' ? '管理员' : '普通用户'}
                </p>
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-muted-foreground" />
                <p>{user.email}</p>
              </div>
              <div className="flex items-center gap-2">
                <KeyRound className="h-4 w-4 text-muted-foreground" />
                <p>账户ID: <span className="font-mono text-xs">{user.id}</span></p>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <p>创建时间: {createdAt}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 使用情况卡片 */}
        <Card>
          <CardHeader>
            <CardTitle>使用情况</CardTitle>
            <CardDescription>您当前的使用情况和限制</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <div className="flex justify-between">
                <p className="text-sm text-muted-foreground">今日使用量</p>
                <p className="text-sm font-medium">
                  {used} / {limit} 条消息
                </p>
              </div>
              <Progress value={usagePercentage} className="h-2" />
              <p className="text-xs text-muted-foreground">
                {remaining === 0 
                  ? "您已达到今日使用上限，请明天再试" 
                  : `您今日还可以发送 ${remaining} 条消息`}
              </p>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
                <p>每日消息限制: {limit} 条</p>
              </div>
              <div className="flex items-center gap-2">
                <BarChart className="h-4 w-4 text-muted-foreground" />
                <p>今日已使用: {used} 条</p>
              </div>
            </div>

            {user.role === 'admin' && (
              <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-950 rounded-md">
                <p className="text-sm">作为管理员，您没有使用限制。</p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 