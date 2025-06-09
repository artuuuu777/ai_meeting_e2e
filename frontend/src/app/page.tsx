import { Metadata } from 'next'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Mic, 
  Search, 
  Brain, 
  Zap, 
  Shield, 
  BarChart3,
  ArrowRight,
  Upload,
  MessageSquare
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'Meeting AI - AI-Powered Meeting Intelligence',
  description: 'Transform your meetings with AI-powered transcription, analysis, and insights. Upload audio, get transcripts, and extract actionable insights automatically.',
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Navigation */}
      <nav className="border-b bg-white/80 backdrop-blur-sm dark:bg-gray-900/80">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Brain className="h-8 w-8 text-blue-600" />
              <span className="text-xl font-bold">Meeting AI</span>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/dashboard" asChild>
                <Button variant="outline">Dashboard</Button>
              </Link>
              <Link href="/meetings/new" asChild>
                <Button>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Meeting
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 text-center">
        <div className="mx-auto max-w-4xl">
          <h1 className="mb-6 text-5xl font-bold tracking-tight text-gray-900 dark:text-white">
            Transform Your Meetings with{' '}
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              AI Intelligence
            </span>
          </h1>
          <p className="mb-8 text-xl text-gray-600 dark:text-gray-300">
            Upload meeting recordings and get instant transcripts, key insights, action items, 
            and searchable knowledge base. Never miss important decisions again.
          </p>
          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link href="/meetings/new" asChild>
              <Button size="lg" className="text-lg">
                <Upload className="mr-2 h-5 w-5" />
                Upload Your First Meeting
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="/dashboard" asChild>
              <Button variant="outline" size="lg" className="text-lg">
                <BarChart3 className="mr-2 h-5 w-5" />
                View Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="mb-12 text-center">
          <h2 className="mb-4 text-3xl font-bold text-gray-900 dark:text-white">
            Powerful Features
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-300">
            Everything you need to make your meetings more productive
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <Mic className="h-10 w-10 text-blue-600" />
              <CardTitle>AI Transcription</CardTitle>
              <CardDescription>
                High-accuracy speech-to-text with speaker identification and timestamps
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
                <li>• 95%+ accuracy with OpenAI Whisper</li>
                <li>• Speaker diarization</li>
                <li>• Multiple audio format support</li>
                <li>• Real-time processing</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Brain className="h-10 w-10 text-indigo-600" />
              <CardTitle>Smart Analysis</CardTitle>
              <CardDescription>
                Extract key insights, action items, and decisions automatically
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
                <li>• Action items with owners</li>
                <li>• Key decisions and outcomes</li>
                <li>• Risk identification</li>
                <li>• Meeting sentiment analysis</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Search className="h-10 w-10 text-green-600" />
              <CardTitle>Semantic Search</CardTitle>
              <CardDescription>
                Find any information across all your meetings instantly
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
                <li>• Vector-based search</li>
                <li>• Natural language queries</li>
                <li>• Cross-meeting insights</li>
                <li>• Advanced filtering</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <MessageSquare className="h-10 w-10 text-purple-600" />
              <CardTitle>Ask Questions</CardTitle>
              <CardDescription>
                Chat with your meeting data using natural language
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
                <li>• RAG-powered Q&A</li>
                <li>• Context-aware responses</li>
                <li>• Source citations</li>
                <li>• Follow-up questions</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Shield className="h-10 w-10 text-red-600" />
              <CardTitle>Enterprise Security</CardTitle>
              <CardDescription>
                Bank-grade security with complete data privacy
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
                <li>• End-to-end encryption</li>
                <li>• SOC 2 compliant</li>
                <li>• On-premise deployment</li>
                <li>• GDPR/CCPA ready</li>
              </ul>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Zap className="h-10 w-10 text-yellow-600" />
              <CardTitle>Fast Processing</CardTitle>
              <CardDescription>
                Get insights in minutes, not hours
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
                <li>• Sub-30 second processing</li>
                <li>• Parallel analysis pipeline</li>
                <li>• Real-time updates</li>
                <li>• Scalable infrastructure</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-blue-600 dark:bg-blue-800">
        <div className="container mx-auto px-4 py-16 text-center">
          <h2 className="mb-4 text-3xl font-bold text-white">
            Ready to Transform Your Meetings?
          </h2>
          <p className="mb-8 text-xl text-blue-100">
            Join thousands of teams already using Meeting AI to boost productivity
          </p>
          <Link href="/meetings/new" asChild>
            <Button size="lg" variant="secondary" className="text-lg">
              <Upload className="mr-2 h-5 w-5" />
              Get Started Now
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t bg-white dark:bg-gray-900">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Brain className="h-6 w-6 text-blue-600" />
              <span className="font-semibold">Meeting AI</span>
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              © 2024 Meeting AI. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}