"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Eye, EyeOff, UserCircle, Lock, Mail } from "lucide-react";

import { Button } from "~/components/ui/button";
import { Input } from "~/components/ui/input";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "~/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "~/components/ui/tabs";
import { useAuth } from "~/lib/auth-context";
import { FlickeringGrid } from "~/components/magicui/flickering-grid";

export default function LoginPage() {
  const router = useRouter();
  const { login, register, error, loading, isAdmin, isAuthenticated } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [activeTab, setActiveTab] = useState("login");

  // 登录后自动导航到相应页面
  useEffect(() => {
    if (isAuthenticated) {
      if (isAdmin) {
        router.push("/admin"); // 管理员跳转到后台
      } else {
        router.push("/chat"); // 普通用户跳转到聊天页面
      }
    }
  }, [isAuthenticated, isAdmin, router]);

  // Login form state
  const [loginForm, setLoginForm] = useState({
    username: "",
    password: "",
  });

  // Register form state
  const [registerForm, setRegisterForm] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  // Form validation errors
  const [validationErrors, setValidationErrors] = useState<{
    login?: { [key: string]: string };
    register?: { [key: string]: string };
  }>({});

  // Handle login form submission
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    const errors: { [key: string]: string } = {};
    if (!loginForm.username) errors.username = "用户名不能为空";
    if (!loginForm.password) errors.password = "密码不能为空";
    
    if (Object.keys(errors).length > 0) {
      setValidationErrors({ login: errors });
      return;
    }
    
    try {
      await login(loginForm.username, loginForm.password);
      // 登录成功后，由useEffect负责导航
    } catch (err) {
      // Error is handled by the auth context
    }
  };

  // Handle register form submission
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    const errors: { [key: string]: string } = {};
    if (!registerForm.username) errors.username = "用户名不能为空";
    if (!registerForm.email) errors.email = "邮箱不能为空";
    if (!registerForm.password) errors.password = "密码不能为空";
    if (registerForm.password !== registerForm.confirmPassword) {
      errors.confirmPassword = "两次输入的密码不一致";
    }
    
    if (Object.keys(errors).length > 0) {
      setValidationErrors({ register: errors });
      return;
    }
    
    try {
      await register(registerForm.username, registerForm.email, registerForm.password);
      // 注册成功后，由useEffect负责导航
    } catch (err) {
      // Error is handled by the auth context
    }
  };

  // Handle login form input changes
  const handleLoginChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setLoginForm((prev) => ({ ...prev, [name]: value }));
    
    // Clear validation error for this field
    if (validationErrors.login && validationErrors.login[name]) {
      setValidationErrors({
        ...validationErrors,
        login: {
          ...validationErrors.login,
          [name]: "",
        },
      });
    }
  };

  // Handle register form input changes
  const handleRegisterChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setRegisterForm((prev) => ({ ...prev, [name]: value }));
    
    // Clear validation error for this field
    if (validationErrors.register && validationErrors.register[name]) {
      setValidationErrors({
        ...validationErrors,
        register: {
          ...validationErrors.register,
          [name]: "",
        },
      });
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4">
      <FlickeringGrid
        id="login-hero-bg"
        className={`absolute inset-0 z-0 [mask-image:radial-gradient(800px_circle_at_center,white,transparent)]`}
        squareSize={4}
        gridGap={4}
        color="#60A5FA"
        maxOpacity={0.133}
        flickerChance={0.1}
      />

      <div className="absolute top-6 left-6 text-xl font-medium">
        <Link href="/" className="flex items-center gap-2">
          <span className="mr-1 text-2xl">🔍</span>
          <span>ResearcherNexus</span>
        </Link>
      </div>

      <Card className="z-10 w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl">欢迎使用 ResearcherNexus</CardTitle>
          <CardDescription>
            深度研究的个人助手，助力您的学术探索
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs 
            defaultValue="login" 
            value={activeTab} 
            onValueChange={setActiveTab}
            className="w-full"
          >
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login">登录</TabsTrigger>
              <TabsTrigger value="register">注册</TabsTrigger>
            </TabsList>
            
            {/* Login Form */}
            <TabsContent value="login">
              <form onSubmit={handleLogin} className="space-y-4 pt-4">
                {/* 显示错误信息 */}
                {error && (
                  <div className="rounded-md bg-red-50 p-3">
                    <p className="text-sm text-red-600">{error}</p>
                    <button
                      type="button"
                      className="mt-2 text-xs text-blue-600 hover:underline"
                      onClick={() => {
                        localStorage.removeItem("researchernexus_users");
                        localStorage.removeItem("researchernexus_current_user");
                        window.location.reload();
                      }}
                    >
                      重置系统（遇到登录问题时点击）
                    </button>
                  </div>
                )}

                <div className="space-y-2">
                  <div className="relative">
                    <UserCircle className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                    <Input
                      name="username"
                      value={loginForm.username}
                      onChange={handleLoginChange}
                      className="pl-10"
                      placeholder="用户名"
                    />
                  </div>
                  {validationErrors.login?.username && (
                    <p className="text-sm text-red-500">{validationErrors.login.username}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                    <Input
                      name="password"
                      type={showPassword ? "text" : "password"}
                      value={loginForm.password}
                      onChange={handleLoginChange}
                      className="pl-10 pr-10"
                      placeholder="密码"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5" />
                      ) : (
                        <Eye className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                  {validationErrors.login?.password && (
                    <p className="text-sm text-red-500">{validationErrors.login.password}</p>
                  )}
                </div>

                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? "登录中..." : "登录"}
                </Button>
              </form>
            </TabsContent>
            
            {/* Register Form */}
            <TabsContent value="register">
              <form onSubmit={handleRegister} className="space-y-4 pt-4">
                <div className="space-y-2">
                  <div className="relative">
                    <UserCircle className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                    <Input
                      name="username"
                      value={registerForm.username}
                      onChange={handleRegisterChange}
                      className="pl-10"
                      placeholder="用户名"
                    />
                  </div>
                  {validationErrors.register?.username && (
                    <p className="text-sm text-red-500">{validationErrors.register.username}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                    <Input
                      name="email"
                      type="email"
                      value={registerForm.email}
                      onChange={handleRegisterChange}
                      className="pl-10"
                      placeholder="邮箱"
                    />
                  </div>
                  {validationErrors.register?.email && (
                    <p className="text-sm text-red-500">{validationErrors.register.email}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                    <Input
                      name="password"
                      type={showPassword ? "text" : "password"}
                      value={registerForm.password}
                      onChange={handleRegisterChange}
                      className="pl-10 pr-10"
                      placeholder="密码"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5" />
                      ) : (
                        <Eye className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                  {validationErrors.register?.password && (
                    <p className="text-sm text-red-500">{validationErrors.register.password}</p>
                  )}
                </div>

                <div className="space-y-2">
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                    <Input
                      name="confirmPassword"
                      type={showPassword ? "text" : "password"}
                      value={registerForm.confirmPassword}
                      onChange={handleRegisterChange}
                      className="pl-10 pr-10"
                      placeholder="确认密码"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5" />
                      ) : (
                        <Eye className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                  {validationErrors.register?.confirmPassword && (
                    <p className="text-sm text-red-500">{validationErrors.register.confirmPassword}</p>
                  )}
                </div>

                {error && <p className="text-sm text-red-500">{error}</p>}

                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? "注册中..." : "注册"}
                </Button>
              </form>
            </TabsContent>
          </Tabs>
        </CardContent>
        <CardFooter className="flex justify-center text-sm">
          <span className="text-muted-foreground">
            {activeTab === "login" ? "还没有账号？" : "已有账号？"}
          </span>
          <button
            type="button"
            onClick={() => setActiveTab(activeTab === "login" ? "register" : "login")}
            className="ml-1 text-primary hover:underline"
          >
            {activeTab === "login" ? "立即注册" : "立即登录"}
          </button>
        </CardFooter>
      </Card>
    </div>
  );
} 