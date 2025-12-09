import type { Metadata } from 'next'
import './globals.css'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Mobile Legends Knowledge Graph',
  description: 'AI-powered Mobile Legends hero information system',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <nav className="bg-gradient-to-r from-purple-900 via-blue-900 to-purple-900 border-b border-purple-500/30">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center space-x-8">
                <Link href="/" className="flex items-center space-x-2">
                  <span className="text-2xl">⚔️</span>
                  <span className="font-bold text-xl text-white">ML Knowledge Graph</span>
                </Link>
                <div className="flex space-x-4">
                  <Link
                    href="/"
                    className="px-4 py-2 rounded-lg text-white hover:bg-white/10 transition-colors"
                  >
                    💬 Chatbot
                  </Link>
                  <Link
                    href="/draft"
                    className="px-4 py-2 rounded-lg text-white hover:bg-white/10 transition-colors"
                  >
                    🎯 Draft Pick
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  )
}
