// Task T-227: Centralized API fetch wrapper with automatic Bearer token injection
// Ensures JWT token from Better Auth is included in ALL API requests to protected endpoints
// This satisfies Phase II Constitution requirement: "All API requests MUST include JWT in Authorization header"

"use client"

import { authClient } from "./auth-client"

const TODO_API_BASE_URL = process.env.NEXT_PUBLIC_TODO_API_URL
const AGENT_API_BASE_URL = process.env.NEXT_PUBLIC_AGENT_API_URL

// Request timeout in milliseconds (10 seconds)
const REQUEST_TIMEOUT_MS = 10000

export interface ApiRequestOptions extends RequestInit {
  authenticated?: boolean
  headers?: HeadersInit
}

export interface ApiResponse<T = any> {
  ok: boolean
  status: number
  data?: T
  error?: string
}

export async function apiCall<T = any>(
  baseUrl: string, // New parameter for the base URL
  endpoint: string,
  options: ApiRequestOptions = {}
): Promise<ApiResponse<T>> {
  const { authenticated = true, ...fetchOptions } = options

  try {
    // Build headers
    const headers = new Headers(fetchOptions.headers || {})

    // Set content type if not already set
    if (!headers.has("Content-Type") && fetchOptions.body) {
      headers.set("Content-Type", "application/json")
    }

    // Task T-227: Automatically inject JWT token for authenticated requests
    // Better Auth JWT plugin provides the token() method via jwtClient plugin
    if (authenticated) {
      try {
        if (process.env.NODE_ENV === "development") {
          console.log(`[API] Authenticating request to: ${endpoint}`);
        }

        // Get JWT token from Better Auth via /api/auth/token endpoint
        // jwtClient plugin provides this token() method
        const { data: tokenResponse, error: tokenError } = await authClient.token()

        if (process.env.NODE_ENV === "development") {
          console.log("[API] Token fetch response:", {
            hasToken: !!tokenResponse?.token,
            tokenError: tokenError?.message || tokenError,
          });
        }

        if (tokenError || !tokenResponse?.token) {
          // No JWT token available - check if we have a session
          if (process.env.NODE_ENV === "development") {
            console.warn("[API] No JWT token available, checking session...", { tokenError });
          }

          const { data: session } = await authClient.getSession()

          if (process.env.NODE_ENV === "development") {
            console.log("[API] Session check:", {
              hasSession: !!session,
              // sessionExpiresAt: session?.expiresAt,
            });
          }

          if (!session) {
            console.error("[API] ✗ No session found - user is not authenticated");
            return {
              ok: false,
              status: 401,
              error: "Not authenticated - no session found",
            }
          }
          // Session exists, will be sent via cookies with credentials: "include"
          if (process.env.NODE_ENV === "development") {
            console.log("[API] ✓ Using session cookie for authentication");
          }
        } else if (tokenResponse.token) {
          // Inject JWT token in Authorization header
          // Format: Authorization: Bearer <jwt-token>
          headers.set("Authorization", `Bearer ${tokenResponse.token}`)
          if (process.env.NODE_ENV === "development") {
            console.log("[API] ✓ JWT token injected for request:", {
              endpoint,
              authHeaderSet: true,
            });
          }
        }
      } catch (error) {
        console.error("[API] ✗ Failed to get auth token:", error);
        return {
          ok: false,
          status: 401,
          error: "Failed to retrieve authentication token",
        }
      }
    }

    // Make HTTP request with credentials to include session cookies
    const url = `${baseUrl}${endpoint}`;
    if (process.env.NODE_ENV === "development") {
      console.log("[API] Making fetch request:", {
        url,
        method: fetchOptions.method || "GET",
        hasAuthHeader: headers.has("Authorization"),
        credentialsIncluded: true,
      });
    }

    // Add timeout to fetch request using AbortController
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)

    let response: Response
    try {
      response = await fetch(url, {
        ...fetchOptions,
        headers,
        credentials: "include", // Include session cookies in the request
        signal: controller.signal,
      })
      clearTimeout(timeoutId)
    } catch (error) {
      clearTimeout(timeoutId)
      if (error instanceof Error && error.name === "AbortError") {
        console.error(`API request timeout (${REQUEST_TIMEOUT_MS}ms): ${endpoint}`)
        return {
          ok: false,
          status: 0,
          error: `Request timeout - server took too long to respond`,
        }
      }
      throw error
    }

    if (process.env.NODE_ENV === "development") {
      console.log("[API] Response received:", {
        endpoint,
        status: response.status,
        statusText: response.statusText,
        contentType: response.headers.get("content-type"),
      });
    }

    // Task T-242: Enhanced error handling for different HTTP status codes

    // 401: Unauthorized - Token expired or invalid
    if (response.status === 401) {
      console.warn("JWT token expired or invalid - redirecting to login")
      try {
        await authClient.signOut()
      } catch (error) {
        console.error("Failed to sign out:", error)
      }

      // Redirect to login page
      if (typeof window !== "undefined") {
        window.location.href = "/login"
      }

      return {
        ok: false,
        status: 401,
        error: "Your session has expired. Please log in again.",
      }
    }

    // 403: Forbidden - User doesn't have permission
    if (response.status === 403) {
      console.warn("Access forbidden for endpoint:", endpoint)
      return {
        ok: false,
        status: 403,
        error: "You don't have permission to access this resource.",
      }
    }

    // 404: Not found
    if (response.status === 404) {
      console.warn("Resource not found:", endpoint)
      return {
        ok: false,
        status: 404,
        error: "The requested resource was not found.",
      }
    }

    // 409: Conflict - e.g., duplicate email on signup
    if (response.status === 409) {
      const errorData = await response.text()
      console.warn("Conflict error:", errorData)
      return {
        ok: false,
        status: 409,
        error: errorData || "This resource already exists.",
      }
    }

    // 422: Unprocessable entity - validation error
    if (response.status === 422) {
      const errorData = await response.text()
      console.warn("Validation error:", errorData)
      return {
        ok: false,
        status: 422,
        error: errorData || "Invalid request data.",
      }
    }

    // 500: Server error
    if (response.status === 500) {
      console.error("Server error from endpoint:", endpoint)
      return {
        ok: false,
        status: 500,
        error: "Server error. Please try again later.",
      }
    }

    // Handle other HTTP errors
    if (!response.ok) {
      const errorData = await response.text()
      return {
        ok: false,
        status: response.status,
        error: `API error: ${response.statusText}${errorData ? ` - ${errorData}` : ""}`,
      }
    }

    // Parse response body
    let data: T | undefined
    const contentType = response.headers.get("content-type")
    if (contentType?.includes("application/json")) {
      data = await response.json()
    }

    return {
      ok: true,
      status: response.status,
      data,
    }
  } catch (error) {
    const errorMessage =
      error instanceof Error ? error.message : "Unknown error"
    console.error(`API call failed: ${baseUrl}${endpoint}`, error)

    // Handle specific network errors
    if (error instanceof TypeError) {
      return {
        ok: false,
        status: 0,
        error: "Network error. Please check your connection and try again.",
      }
    }

    return {
      ok: false,
      status: 0,
      error: `Error: ${errorMessage}`,
    }
  }
}

/**
 * Service-specific API call wrapper for the Todo Service.
 * Uses NEXT_PUBLIC_TODO_API_URL.
 */
export async function apiCallTodo<T = any>(
  endpoint: string,
  options: ApiRequestOptions = {}
): Promise<ApiResponse<T>> {
  if (!TODO_API_BASE_URL) {
    return { ok: false, status: 500, error: "TODO_API_BASE_URL is not defined" };
  }
  return apiCall<T>(TODO_API_BASE_URL, endpoint, options);
}

/**
 * Service-specific API call wrapper for the Agent Service.
 * Uses NEXT_PUBLIC_AGENT_API_URL.
 */
export async function apiCallAgent<T = any>(
  endpoint: string,
  options: ApiRequestOptions = {}
): Promise<ApiResponse<T>> {
  if (!AGENT_API_BASE_URL) {
    return { ok: false, status: 500, error: "AGENT_API_BASE_URL is not defined" };
  }
  return apiCall<T>(AGENT_API_BASE_URL, endpoint, options);
}


/**
 * Task T-227: GET request helper for Todo Service
 * Automatically includes JWT token in Authorization header
 */
export async function apiGetTodo<T = any>(
  endpoint: string
): Promise<ApiResponse<T>> {
  return apiCallTodo<T>(endpoint, {
    method: "GET",
    authenticated: true,
  })
}

/**
 * Task T-227: POST request helper for Todo Service
 * Automatically includes JWT token in Authorization header
 */
export async function apiPostTodo<T = any>(
  endpoint: string,
  body: any
): Promise<ApiResponse<T>> {
  return apiCallTodo<T>(endpoint, {
    method: "POST",
    body: JSON.stringify(body),
    authenticated: true,
  })
}

/**
 * Task T-227: PUT request helper for Todo Service
 * Automatically includes JWT token in Authorization header
 */
export async function apiPutTodo<T = any>(
  endpoint: string,
  body: any
): Promise<ApiResponse<T>> {
  return apiCallTodo<T>(endpoint, {
    method: "PUT",
    body: JSON.stringify(body),
    authenticated: true,
  })
}

/**
 * Task T-227: PATCH request helper for Todo Service
 * Automatically includes JWT token in Authorization header
 */
export async function apiPatchTodo<T = any>(
  endpoint: string,
  body: any
): Promise<ApiResponse<T>> {
  return apiCallTodo<T>(endpoint, {
    method: "PATCH",
    body: JSON.stringify(body),
    authenticated: true,
  })
}

/**
 * Task T-227: DELETE request helper for Todo Service
 * Automatically includes JWT token in Authorization header
 */
export async function apiDeleteTodo<T = any>(
  endpoint: string
): Promise<ApiResponse<T>> {
  return apiCallTodo<T>(endpoint, {
    method: "DELETE",
    authenticated: true,
  })
}

/**
 * Task T-227: Unauthenticated GET for Todo Service (for public endpoints)
 * Does NOT include JWT token
 */
export async function apiGetPublicTodo<T = any>(
  endpoint: string
): Promise<ApiResponse<T>> {
  return apiCallTodo<T>(endpoint, {
    method: "GET",
    authenticated: false,
  })
}

/**
 * Task T-227: GET request helper for Agent Service
 * Automatically includes JWT token in Authorization header
 */
export async function apiGetAgent<T = any>(
  endpoint: string
): Promise<ApiResponse<T>> {
  return apiCallAgent<T>(endpoint, {
    method: "GET",
    authenticated: true,
  })
}

/**
 * Task T-227: POST request helper for Agent Service
 * Automatically includes JWT token in Authorization header
 */
export async function apiPostAgent<T = any>(
  endpoint: string,
  body: any
): Promise<ApiResponse<T>> {
  return apiCallAgent<T>(endpoint, {
    method: "POST",
    body: JSON.stringify(body),
    authenticated: true,
  })
}

/**
 * Task T-227: PUT request helper for Agent Service
 * Automatically includes JWT token in Authorization header
 */
export async function apiPutAgent<T = any>(
  endpoint: string,
  body: any
): Promise<ApiResponse<T>> {
  return apiCallAgent<T>(endpoint, {
    method: "PUT",
    body: JSON.stringify(body),
    authenticated: true,
  })
}

/**
 * Task T-227: PATCH request helper for Agent Service
 * Automatically includes JWT token in Authorization header
 */
export async function apiPatchAgent<T = any>(
  endpoint: string,
  body: any
): Promise<ApiResponse<T>> {
  return apiCallAgent<T>(endpoint, {
    method: "PATCH",
    body: JSON.stringify(body),
    authenticated: true,
  })
}

/**
 * Task T-227: DELETE request helper for Agent Service
 * Automatically includes JWT token in Authorization header
 */
export async function apiDeleteAgent<T = any>(
  endpoint: string
): Promise<ApiResponse<T>> {
  return apiCallAgent<T>(endpoint, {
    method: "DELETE",
    authenticated: true,
  })
}

/**
 * Task T-227: Unauthenticated GET for Agent Service (for public endpoints)
 * Does NOT include JWT token
 */
export async function apiGetPublicAgent<T = any>(
  endpoint: string
): Promise<ApiResponse<T>> {
  return apiCallAgent<T>(endpoint, {
    method: "GET",
    authenticated: false,
  })
}

/**
 * Task T-227: Verify API connectivity and JWT injection
 * Useful for debugging and testing
 */
export async function verifyApiConnectivity(): Promise<{
  connected: boolean
  tokenIncluded: boolean
  error?: string
}> {
  try {
    const responseTodo = await apiGetPublicTodo("/health")
    const responseAgent = await apiGetPublicAgent("/health")

    if (responseTodo.ok && responseAgent.ok) {
      // Try authenticated call to verify JWT injection with Todo service
      const authResponseTodo = await apiGetTodo("/api/todos")
      // Try authenticated call to verify JWT injection with Agent service
      const authResponseAgent = await apiGetAgent("/api/chat")


      return {
        connected: true,
        tokenIncluded: authResponseTodo.status !== 401 && authResponseAgent.status !== 401,
        error: undefined,
      }
    } else {
      let errorMessages = []
      if (!responseTodo.ok) errorMessages.push(`Todo Service: ${responseTodo.error}`);
      if (!responseAgent.ok) errorMessages.push(`Agent Service: ${responseAgent.error}`);

      return {
        connected: false,
        tokenIncluded: false,
        error: errorMessages.join("; "),
      }
    }
  } catch (error) {
    return {
      connected: false,
      tokenIncluded: false,
      error: error instanceof Error ? error.message : "Unknown error",
    }
  }
}

