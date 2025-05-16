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

  // Get user token from cookie
  const authTokenCookie = request.cookies.get("researchernexus_current_user");
  const authToken = authTokenCookie?.value;

  // If user is on a protected route and not authenticated, redirect to login
  if (!isPublicPath && !authToken) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  
  // If user is on login page but already authenticated, redirect to chat
  if (path === "/login" && authToken) {
    return NextResponse.redirect(new URL("/chat", request.url));
  }
  
  // 保护管理页面，只允许管理员访问
  if (path.startsWith("/admin") && authToken) {
    try {
      // 解析用户信息
      const userData = JSON.parse(authToken);
      
      // 如果不是管理员，重定向到首页
      if (userData.role !== 'admin') {
        return NextResponse.redirect(new URL("/", request.url));
      }
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