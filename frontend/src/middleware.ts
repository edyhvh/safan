import type { NextRequest } from 'next/server'
import { proxy } from './proxy'

/**
 * Next.js middleware that uses proxy.ts for locale detection and routing
 */
export function middleware(request: NextRequest) {
  return proxy(request)
}

// Middleware config for Next.js
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - icon.svg (icon file)
     * - data (static JSON files)
     *
     * The pattern uses .*? to make the trailing part optional,
     * allowing it to match the root path '/' as well.
     */
    '/((?!api|_next/static|_next/image|favicon.ico|icon.svg|data).*)?',
  ],
}
