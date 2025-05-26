import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // 获取当前路径
  const { pathname } = request.nextUrl;

  // 如果是登录页面或API路由，直接通过
  if (
    pathname.startsWith("/auth/login") ||
    pathname.startsWith("/api/") ||
    pathname.startsWith("/_next/") ||
    pathname.startsWith("/favicon.ico") ||
    pathname === "/"
  ) {
    return NextResponse.next();
  }

  // 对于其他受保护的路由（如/chat），检查认证状态
  // 注意：在中间件中无法访问localStorage，所以这里只是一个基本的重定向
  // 实际的认证检查在客户端组件中进行
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * 匹配所有请求路径，除了以下开头的：
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
}; 