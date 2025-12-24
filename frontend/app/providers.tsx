'use client'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { useState } from 'react'
import { Toaster } from '@/components/ui/toaster'
import { ThemeProvider } from '@/components/theme-provider'

// Coaching Query Config from contracts/api-client.ts
export const coachingQueryConfig = {
  defaultOptions: {
    queries: {
      networkMode: 'offlineFirst' as const,
      gcTime: 1000 * 60 * 5, // 5 minutes
      retry: 2,
    },
    mutations: {
      networkMode: 'always' as const,
      retry: 3,
    },
  },
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(() => new QueryClient(coachingQueryConfig))

  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <QueryClientProvider client={queryClient}>
        {children}
        {process.env.NEXT_PUBLIC_ENABLE_DEVTOOLS === 'true' && (
          <ReactQueryDevtools initialIsOpen={false} />
        )}
        <Toaster />
      </QueryClientProvider>
    </ThemeProvider>
  )
}
