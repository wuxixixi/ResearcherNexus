# ResearcherNexus 登录系统使用指南

## 概述

我们为 ResearcherNexus 项目添加了一个简单的登录系统，使用 CSV 文件存储用户凭据。

## 功能特性

- 🔐 简单的用户名/密码认证
- 📁 CSV 文件存储用户数据
- 🛡️ 路由保护（保护 `/chat` 页面）
- 🚪 登录/登出功能
- 💾 本地存储认证状态

## 默认用户账户

系统预设了以下测试账户：

| 用户名 | 密码     |
|--------|----------|
| admin  | admin123 |
| user   | password |
| test   | test123  |
| demo   | demo456  |

## 使用流程

1. **访问主页**: 打开 `http://localhost:3000`
2. **点击"开始研究"**: 会跳转到登录页面 `/auth/login`
3. **输入凭据**: 使用上述任一账户登录
4. **访问聊天页面**: 登录成功后自动跳转到 `/chat`
5. **登出**: 在聊天页面点击右上角的登出按钮

## 文件结构

```
web/
├── users.csv                           # 用户数据文件
├── src/
│   ├── app/
│   │   ├── auth/
│   │   │   └── login/
│   │   │       └── page.tsx            # 登录页面
│   │   ├── api/
│   │   │   └── auth/
│   │   │       ├── login/
│   │   │       │   └── route.ts        # 登录API
│   │   │       └── logout/
│   │   │           └── route.ts        # 登出API
│   │   └── chat/
│   │       └── page.tsx                # 受保护的聊天页面
│   ├── components/
│   │   └── auth/
│   │       └── ProtectedRoute.tsx      # 路由保护组件
│   ├── hooks/
│   │   └── useAuth.ts                  # 认证Hook
│   └── middleware.ts                   # 路由中间件
```

## 添加新用户

要添加新用户，只需编辑 `web/users.csv` 文件：

```csv
username,password
admin,admin123
user,password
newuser,newpassword
```

## 安全说明

⚠️ **重要**: 这是一个简化的登录系统，仅用于演示目的。在生产环境中，请考虑以下安全措施：

- 使用加密的密码存储
- 实现 JWT 或 session 管理
- 添加 HTTPS
- 实现密码复杂度要求
- 添加登录尝试限制
- 使用专业的认证服务

## 技术实现

- **前端**: React + Next.js 15
- **状态管理**: React Hooks + localStorage
- **路由保护**: 客户端组件 + useEffect
- **数据存储**: CSV 文件 + Node.js fs API
- **UI组件**: 基于项目现有的 UI 组件库

## 故障排除

### 登录失败
- 检查用户名和密码是否正确
- 确认 `users.csv` 文件存在且格式正确

### 页面无法访问
- 确保开发服务器正在运行
- 检查浏览器控制台是否有错误信息

### 登录状态丢失
- 检查浏览器的 localStorage 是否被清除
- 刷新页面重新验证登录状态 