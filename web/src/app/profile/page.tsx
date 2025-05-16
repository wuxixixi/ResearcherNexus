"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Home, User, Mail, KeyRound, Calendar, BarChart, MessageSquare, Lock, Eye, EyeOff, AlertCircle } from "lucide-react";
import Link from "next/link";

import { useAuth } from "~/lib/auth-context";
import { Button } from "~/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from "~/components/ui/card";
import { Progress } from "~/components/ui/progress";
import { Input } from "~/components/ui/input";
import { Alert, AlertDescription } from "~/components/ui/alert";

export default function ProfilePage() {
  const { user, isAuthenticated, getRemainingUsage, changePassword, error, loading } = useAuth();
  const router = useRouter();
  
  // 用户使用情况状态
  const [usageInfo, setUsageInfo] = useState<{ used: number; limit: number; remaining: number }>(
    { used: 0, limit: 0, remaining: 0 }
  );
  
  // 密码表单状态
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });
  const [formError, setFormError] = useState("");
  const [formSuccess, setFormSuccess] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // 检查用户是否已登录
  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    } else if (user) {
      // 如果用户已认证，获取其使用情况
      const fetchUsage = async () => {
        try {
          const currentUsage = await getRemainingUsage();
          setUsageInfo(currentUsage);
        } catch (err) {
          console.error("获取用户使用情况失败:", err);
          // 可以选择设置一个默认的错误状态或提示
        }
      };
      fetchUsage();
    }
  }, [isAuthenticated, router, user, getRemainingUsage]);

  if (!user) {
    return null; // 如果没有用户数据，不显示内容
  }

  // 格式化创建时间
  const formattedCreatedAt = user.created_at 
    ? new Date(user.created_at).toLocaleDateString("zh-CN", {
        year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
      })
    : "未知";
  
  // 处理密码表单输入变化
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setPasswordForm((prev) => ({ ...prev, [name]: value }));
    
    // 清除之前的错误和成功消息
    setFormError("");
    setFormSuccess("");
  };
  
  // 处理密码修改提交
  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 表单验证
    if (!passwordForm.currentPassword) {
      setFormError("请输入当前密码");
      return;
    }
    
    if (!passwordForm.newPassword) {
      setFormError("请输入新密码");
      return;
    }
    
    if (passwordForm.newPassword.length < 6) {
      setFormError("新密码长度不能少于6个字符");
      return;
    }
    
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setFormError("两次输入的新密码不一致");
      return;
    }
    
    if (passwordForm.currentPassword === passwordForm.newPassword) {
      setFormError("新密码不能与当前密码相同");
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      await changePassword(
        user.id,
        passwordForm.currentPassword,
        passwordForm.newPassword
      );
      
      // 重置表单
      setPasswordForm({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      });
      
      setFormSuccess("密码修改成功！");
    } catch (err) {
      setFormError(error || "密码修改失败，请重试");
    } finally {
      setIsSubmitting(false);
    }
  };

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
                <p>创建时间: {formattedCreatedAt}</p>
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
                  {usageInfo.used} / {usageInfo.limit} 条消息
                </p>
              </div>
              <Progress value={usageInfo.limit > 0 ? (usageInfo.used / usageInfo.limit) * 100 : 0} className="h-2" />
              <p className="text-xs text-muted-foreground">
                {usageInfo.remaining === 0 
                  ? "您已达到今日使用上限，请明天再试" 
                  : `您今日还可以发送 ${usageInfo.remaining} 条消息`}
              </p>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
                <p>每日消息限制: {usageInfo.limit} 条</p>
              </div>
              <div className="flex items-center gap-2">
                <BarChart className="h-4 w-4 text-muted-foreground" />
                <p>今日已使用: {usageInfo.used} 条</p>
              </div>
            </div>

            {user.role === 'admin' && (
              <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-950 rounded-md">
                <p className="text-sm">作为管理员，您没有使用限制。</p>
              </div>
            )}
          </CardContent>
        </Card>
        
        {/* 修改密码卡片 */}
        <Card className="md:col-span-2 mt-6">
          <CardHeader>
            <CardTitle>修改密码</CardTitle>
            <CardDescription>更新您的账户密码</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handlePasswordSubmit} className="space-y-4">
              {/* 当前密码 */}
              <div className="space-y-2">
                <label htmlFor="currentPassword" className="text-sm font-medium">
                  当前密码
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="currentPassword"
                    name="currentPassword"
                    type={showPasswords.current ? "text" : "password"}
                    value={passwordForm.currentPassword}
                    onChange={handlePasswordChange}
                    className="pl-9 pr-9"
                    placeholder="请输入当前密码"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPasswords(prev => ({ ...prev, current: !prev.current }))}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                  >
                    {showPasswords.current ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>
              
              {/* 新密码 */}
              <div className="space-y-2">
                <label htmlFor="newPassword" className="text-sm font-medium">
                  新密码
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="newPassword"
                    name="newPassword"
                    type={showPasswords.new ? "text" : "password"}
                    value={passwordForm.newPassword}
                    onChange={handlePasswordChange}
                    className="pl-9 pr-9"
                    placeholder="请输入新密码"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPasswords(prev => ({ ...prev, new: !prev.new }))}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                  >
                    {showPasswords.new ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>
              
              {/* 确认新密码 */}
              <div className="space-y-2">
                <label htmlFor="confirmPassword" className="text-sm font-medium">
                  确认新密码
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="confirmPassword"
                    name="confirmPassword"
                    type={showPasswords.confirm ? "text" : "password"}
                    value={passwordForm.confirmPassword}
                    onChange={handlePasswordChange}
                    className="pl-9 pr-9"
                    placeholder="请再次输入新密码"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPasswords(prev => ({ ...prev, confirm: !prev.confirm }))}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                  >
                    {showPasswords.confirm ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>
              
              {/* 错误消息 */}
              {formError && (
                <Alert variant="destructive" className="bg-red-50 text-red-600 border-red-200">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{formError}</AlertDescription>
                </Alert>
              )}
              
              {/* 成功消息 */}
              {formSuccess && (
                <Alert className="bg-green-50 text-green-600 border-green-200">
                  <AlertDescription>{formSuccess}</AlertDescription>
                </Alert>
              )}
              
              <CardFooter className="px-0 pt-2">
                <Button type="submit" disabled={isSubmitting} className="w-full">
                  {isSubmitting ? "提交中..." : "修改密码"}
                </Button>
              </CardFooter>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 