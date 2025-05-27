"use client";

import { Settings, Shield, Users } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/components/ui/card";

export default function IconDemoPage() {
  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">图标对比演示</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                设置页面
              </CardTitle>
              <CardDescription>
                使用 Settings 图标 - 用于系统设置和配置
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-center p-8 bg-muted rounded-lg">
                <Settings className="h-12 w-12 text-primary" />
              </div>
              <p className="text-sm text-muted-foreground mt-4">
                这个图标用于通用设置、配置选项、偏好设置等功能
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                管理员面板
              </CardTitle>
              <CardDescription>
                使用 Shield 图标 - 用于管理员功能和权限管理
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-center p-8 bg-muted rounded-lg">
                <Shield className="h-12 w-12 text-primary" />
              </div>
              <p className="text-sm text-muted-foreground mt-4">
                这个图标用于管理员权限、用户管理、系统管理等功能
              </p>
            </CardContent>
          </Card>

          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                其他相关图标
              </CardTitle>
              <CardDescription>
                管理员面板中使用的其他图标
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-center gap-8 p-8 bg-muted rounded-lg">
                <div className="text-center">
                  <Users className="h-8 w-8 text-primary mx-auto mb-2" />
                  <p className="text-sm">用户管理</p>
                </div>
                <div className="text-center">
                  <Shield className="h-8 w-8 text-primary mx-auto mb-2" />
                  <p className="text-sm">管理员面板</p>
                </div>
                <div className="text-center">
                  <Settings className="h-8 w-8 text-primary mx-auto mb-2" />
                  <p className="text-sm">系统设置</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="mt-8 p-4 bg-green-50 dark:bg-green-950 rounded-lg">
          <h3 className="font-semibold text-green-800 dark:text-green-200 mb-2">
            ✅ 图标区分的好处
          </h3>
          <ul className="text-sm text-green-700 dark:text-green-300 space-y-1">
            <li>• <strong>Shield</strong> 图标更直观地表示管理员权限和安全管理</li>
            <li>• <strong>Settings</strong> 图标专门用于用户个人设置和系统配置</li>
            <li>• 用户可以快速区分管理功能和设置功能</li>
            <li>• 提升了界面的可用性和用户体验</li>
          </ul>
        </div>
      </div>
    </div>
  );
} 