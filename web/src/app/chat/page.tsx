// Copyright (c) 2025 SASS and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { GithubOutlined } from "@ant-design/icons";
import dynamic from "next/dynamic";
import Link from "next/link";
import { Suspense } from "react";
import { Home } from "lucide-react";

import { Button } from "~/components/ui/button";
import { useAuth } from "~/lib/auth-context";

import { Logo } from "../../components/ResearcherNexus/logo";
import { ThemeToggle } from "../../components/ResearcherNexus/theme-toggle";
import { Tooltip } from "../../components/ResearcherNexus/tooltip";
import { SettingsDialog } from "../settings/dialogs/settings-dialog";

const Main = dynamic(() => import("./main"), { ssr: false });

export default function HomePage() {
  const { user } = useAuth();

  return (
    <div className="flex h-screen w-screen justify-center overscroll-none">
      <header className="fixed top-0 left-0 flex h-12 w-full items-center justify-between px-4">
        <div className="flex items-center">
          <Logo />
        </div>
        <div className="flex items-center">
          {user && (
            <span className="mr-3 text-sm font-medium">
              Welcome, {user.username}！
            </span>
          )}
          <Tooltip title="回到主页">
            <Button variant="ghost" size="icon" asChild>
              <Link href="/">
                <Home className="h-5 w-5" />
              </Link>
            </Button>
          </Tooltip>
          <Tooltip title="Star ResearcherNexus on GitHub">
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
      <Suspense fallback={<div>Loading ResearcherNexus...</div>}>
        <Main />
      </Suspense>
    </div>
  );
}
