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
  const authToken = request.cookies.get("researchernexus_current_user")?.value;

  // If user is on a protected route and not authenticated, redirect to login
  if (!isPublicPath && !authToken) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  
  // If user is on login page but already authenticated, redirect to chat
  if (path === "/login" && authToken) {
    return NextResponse.redirect(new URL("/chat", request.url));
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