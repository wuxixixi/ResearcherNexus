// Copyright (c) 2025 SASS and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { Suspense, useEffect } from "react";
import { useAuth } from "~/hooks/useAuth";

import { GithubOutlined, LogoutOutlined } from "@ant-design/icons";
import { Shield } from "lucide-react";
import dynamic from "next/dynamic";
import Link from "next/link";

import { Button } from "~/components/ui/button";
import { ProtectedRoute } from "~/components/auth/ProtectedRoute";
import { Logo } from "../../components/researchernexus/logo";
import { ThemeToggle } from "../../components/researchernexus/theme-toggle";
import { Tooltip } from "../../components/researchernexus/tooltip";

import { SettingsDialog } from "../settings/dialogs/settings-dialog";

const Main = dynamic(() => import("./main"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full w-full items-center justify-center">
      Loading ResearcherNexus...
    </div>
  ),
});

function ChatContent() {
  const { username, role, dailyLimit, getRemainingUsage, refreshUsage, logout } = useAuth();
  const remainingUsage = getRemainingUsage();

  // 监听localStorage变化，实时更新使用次数
  useEffect(() => {
    const handleStorageChange = () => {
      refreshUsage();
    };

    // 监听storage事件（跨标签页）
    window.addEventListener('storage', handleStorageChange);
    
    // 监听自定义事件（同一标签页内）
    window.addEventListener('usageUpdated', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('usageUpdated', handleStorageChange);
    };
  }, [refreshUsage]);

  return (
    <div className="flex h-screen w-screen justify-center overscroll-none">
      <header className="fixed top-0 left-0 flex h-12 w-full items-center justify-between px-4 bg-background/80 backdrop-blur-sm border-b">
        <Logo />
        <div className="flex items-center gap-2">
          <div className="flex flex-col items-end text-xs text-muted-foreground">
            <span>欢迎, {username}</span>
            <span>
              今日剩余: {remainingUsage}/{dailyLimit}
              {remainingUsage === 0 && (
                <span className="text-red-500 ml-1">已用完</span>
              )}
            </span>
          </div>
          
          {role === "admin" && (
            <Tooltip title="管理员面板">
              <Button variant="ghost" size="icon" asChild>
                <Link href="/admin">
                  <Shield />
                </Link>
              </Button>
            </Tooltip>
          )}
          
          <Tooltip title="登出">
            <Button variant="ghost" size="icon" onClick={logout}>
              <LogoutOutlined />
            </Button>
          </Tooltip>
          
          <Tooltip title="在GitHub给ResearcherNexus点赞">
            <Button variant="ghost" size="icon" asChild>
              <Link
                href="https://github.com/wuxixixi/ResearcherNexus"
                target="_blank"
              >
                <GithubOutlined />
              </Link>
            </Button>
          </Tooltip>
          
          <ThemeToggle />
          
          <Suspense>
            <SettingsDialog />
          </Suspense>
        </div>
      </header>
      <Main />
    </div>
  );
}

export default function ChatPage() {
  return (
    <ProtectedRoute>
      <ChatContent />
    </ProtectedRoute>
  );
}
