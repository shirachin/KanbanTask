/**
 * Common API client utility
 * Provides unified error handling, loading state management, and request/response processing
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface ApiError {
  message: string
  status?: number
  detail?: string
}

/**
 * Parse error response from API
 */
async function parseErrorResponse(response: Response): Promise<string> {
  try {
    const data = await response.json()
    return data.detail || data.message || `HTTP error! status: ${response.status}`
  } catch {
    return `HTTP error! status: ${response.status}`
  }
}

/**
 * Create user-friendly error message
 */
function createErrorMessage(error: unknown, defaultMessage: string): string {
  if (error instanceof Error) {
    return error.message
  }
  if (typeof error === 'string') {
    return error
  }
  return defaultMessage
}

/**
 * Make API request with unified error handling
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  if (!response.ok) {
    const errorMessage = await parseErrorResponse(response)
    const error: ApiError = {
      message: errorMessage,
      status: response.status,
    }
    throw error
  }

  // Handle empty responses (e.g., 204 No Content)
  if (response.status === 204 || response.headers.get('content-length') === '0') {
    return {} as T
  }

  return await response.json()
}

/**
 * GET request helper
 */
export async function apiGet<T>(endpoint: string): Promise<T> {
  return apiRequest<T>(endpoint, { method: 'GET' })
}

/**
 * POST request helper
 */
export async function apiPost<T>(endpoint: string, data?: unknown): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
  })
}

/**
 * PUT request helper
 */
export async function apiPut<T>(endpoint: string, data?: unknown): Promise<T> {
  return apiRequest<T>(endpoint, {
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
  })
}

/**
 * DELETE request helper
 */
export async function apiDelete<T>(endpoint: string): Promise<T> {
  return apiRequest<T>(endpoint, { method: 'DELETE' })
}

/**
 * Handle API errors with user-friendly messages
 */
export function handleApiError(error: unknown, defaultMessage: string): string {
  if (error && typeof error === 'object' && 'message' in error) {
    const apiError = error as ApiError
    return apiError.message || defaultMessage
  }
  return createErrorMessage(error, defaultMessage)
}
