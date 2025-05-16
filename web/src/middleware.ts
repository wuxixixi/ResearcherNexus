import { NextResponse, type NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // Get the path name
  const path = request.nextUrl.pathname;

  // Define public paths that don't need authentication
  const isPublicPath = 
    path === "/login" || 
    path === "/" || 
    path.startsWith("/_next") || 
    path.startsWith("/api") ||
    path.startsWith("/images") ||
    path.startsWith("/favicon");

  // Get auth cookie
  const authTokenCookie = request.cookies.get("researchernexus_current_user");
  const hasAuthToken = !!authTokenCookie?.value;

  // If user is on a protected route and not authenticated, redirect to login
  if (!isPublicPath && !hasAuthToken) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  
  // 如果用户在登录页但已经认证，重定向到聊天页
  if (path === "/login" && hasAuthToken) {
    return NextResponse.redirect(new URL("/chat", request.url));
  }
  
  // 保护管理页面，只允许管理员访问（这部分会在后端API层进一步验证）
  if (path.startsWith("/admin") && hasAuthToken) {
    try {
      // 后端API已经负责验证权限，这里只做基本检查
      return NextResponse.next();
    } catch (error) {
      // 如果解析失败，重定向到登录页
      return NextResponse.redirect(new URL("/login", request.url));
    }
  }

  return NextResponse.next();
}

// Configure middleware to run only on specific paths
export const config = {
  matcher: [
    /*
     * Match all request paths except for:
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico (favicon)
     */
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
}; 