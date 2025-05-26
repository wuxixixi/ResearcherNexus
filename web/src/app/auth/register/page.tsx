"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

import { ArrowLeft } from "lucide-react";

import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Label } from "~/components/ui/label";
import { Logo } from "~/components/researchernexus/logo";

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");
    setSuccess("");

    // 客户端验证
    if (password !== confirmPassword) {
      setError("两次输入的密码不一致");
      setIsLoading(false);
      return;
    }

    if (password.length < 6) {
      setError("密码长度至少为6位");
      setIsLoading(false);
      return;
    }

    if (username.length < 3) {
      setError("用户名长度至少为3位");
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        setSuccess("注册成功！3秒后跳转到登录页面...");
        setTimeout(() => {
          router.push("/auth/login");
        }, 3000);
      } else {
        setError(data.error ?? "注册失败");
      }
    } catch {
      setError("网络错误，请重试");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="absolute top-4 left-4">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/" className="flex items-center gap-2">
            <ArrowLeft className="h-4 w-4" />
            返回主页
          </Link>
        </Button>
      </div>

      <div className="w-full max-w-md space-y-8 p-8">
        <div className="text-center">
          <Logo className="mx-auto h-12 w-auto" />
          <h2 className="mt-6 text-3xl font-bold tracking-tight">
            注册 ResearcherNexus
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            创建您的账户以开始使用
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <Label htmlFor="username">用户名</Label>
              <Input
                id="username"
                name="username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="请输入用户名（至少3位）"
                className="mt-1"
                minLength={3}
              />
            </div>
            
            <div>
              <Label htmlFor="password">密码</Label>
              <Input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="请输入密码（至少6位）"
                className="mt-1"
                minLength={6}
              />
            </div>

            <div>
              <Label htmlFor="confirmPassword">确认密码</Label>
              <Input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="请再次输入密码"
                className="mt-1"
                minLength={6}
              />
            </div>
          </div>

          {error && (
            <div className="text-sm text-red-600 text-center">{error}</div>
          )}

          {success && (
            <div className="text-sm text-green-600 text-center">{success}</div>
          )}

          <Button
            type="submit"
            className="w-full"
            disabled={isLoading}
          >
            {isLoading ? "注册中..." : "注册"}
          </Button>

          <div className="text-center">
            <p className="text-sm text-muted-foreground">
              已有账户？{" "}
              <Link 
                href="/auth/login" 
                className="font-medium text-primary hover:text-primary/80"
              >
                立即登录
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
} 