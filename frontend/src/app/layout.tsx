import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Providers } from './providers'
import { Toaster } from '@/components/ui/sonner'
import '@/styles/globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: {
    default: 'Meeting AI',
    template: '%s | Meeting AI',
  },
  description: 'AI-powered meeting transcription and analysis platform',
  keywords: [
    'meeting',
    'transcription',
    'AI',
    'analysis',
    'audio',
    'insights',
    'collaboration',
  ],
  authors: [
    {
      name: 'Meeting AI Team',
    },
  ],
  creator: 'Meeting AI Team',
  metadataBase: new URL('https://meeting-ai.com'),
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://meeting-ai.com',
    title: 'Meeting AI',
    description: 'AI-powered meeting transcription and analysis platform',
    siteName: 'Meeting AI',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Meeting AI',
    description: 'AI-powered meeting transcription and analysis platform',
    creator: '@meetingai',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <Providers>
          {children}
          <Toaster />
        </Providers>
      </body>
    </html>
  )
}