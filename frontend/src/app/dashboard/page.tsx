import { Metadata } from 'next'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Plus, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Search,
  Upload,
  Calendar,
  Users,
  BarChart3
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'Dashboard',
  description: 'View and manage your meetings',
}

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="border-b bg-white dark:bg-gray-800">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Dashboard
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Manage your meetings and insights
              </p>
            </div>
            <div className="flex items-center gap-4">
              <Link href="/search" asChild>
                <Button variant="outline">
                  <Search className="mr-2 h-4 w-4" />
                  Search
                </Button>
              </Link>
              <Link href="/meetings/new" asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  New Meeting
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="mb-8 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Meetings</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">24</div>
              <p className="text-xs text-muted-foreground">
                +4 from last month
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Processing</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">3</div>
              <p className="text-xs text-muted-foreground">
                Currently being analyzed
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Completed</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">21</div>
              <p className="text-xs text-muted-foreground">
                Ready for insights
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Hours</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">127</div>
              <p className="text-xs text-muted-foreground">
                Hours of meetings analyzed
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="mb-4 text-lg font-semibold">Quick Actions</h2>
          <div className="grid gap-4 md:grid-cols-3">
            <Card className="cursor-pointer transition-all hover:shadow-md">
              <Link href="/meetings/new">
                <CardHeader>
                  <Upload className="h-8 w-8 text-blue-600" />
                  <CardTitle className="text-lg">Upload Meeting</CardTitle>
                  <CardDescription>
                    Upload audio files and get instant transcription and insights
                  </CardDescription>
                </CardHeader>
              </Link>
            </Card>

            <Card className="cursor-pointer transition-all hover:shadow-md">
              <Link href="/search">
                <CardHeader>
                  <Search className="h-8 w-8 text-green-600" />
                  <CardTitle className="text-lg">Search Meetings</CardTitle>
                  <CardDescription>
                    Find specific discussions and decisions across all meetings
                  </CardDescription>
                </CardHeader>
              </Link>
            </Card>

            <Card className="cursor-pointer transition-all hover:shadow-md">
              <Link href="/analytics">
                <CardHeader>
                  <BarChart3 className="h-8 w-8 text-purple-600" />
                  <CardTitle className="text-lg">View Analytics</CardTitle>
                  <CardDescription>
                    Analyze meeting patterns and team collaboration metrics
                  </CardDescription>
                </CardHeader>
              </Link>
            </Card>
          </div>
        </div>

        {/* Recent Meetings */}
        <div>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Recent Meetings</h2>
            <Link href="/meetings" asChild>
              <Button variant="outline" size="sm">
                View All
              </Button>
            </Link>
          </div>

          <div className="space-y-4">
            {/* Mock meeting cards */}
            {[
              {
                id: '1',
                title: 'Weekly Team Standup',
                date: '2024-01-15T10:00:00Z',
                duration: '32 minutes',
                participants: 5,
                status: 'completed',
                insights: 12
              },
              {
                id: '2',
                title: 'Product Planning Review',
                date: '2024-01-14T14:30:00Z',
                duration: '1h 15m',
                participants: 8,
                status: 'processing',
                insights: 0
              },
              {
                id: '3',
                title: 'Client Discovery Call',
                date: '2024-01-12T09:00:00Z',
                duration: '45 minutes',
                participants: 3,
                status: 'completed',
                insights: 8
              }
            ].map((meeting) => (
              <Card key={meeting.id} className="meeting-card">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="font-semibold text-gray-900 dark:text-white">
                          {meeting.title}
                        </h3>
                        <span className={`processing-indicator ${meeting.status}`}>
                          {meeting.status === 'completed' && <CheckCircle className="h-3 w-3" />}
                          {meeting.status === 'processing' && <Clock className="h-3 w-3" />}
                          {meeting.status === 'failed' && <AlertCircle className="h-3 w-3" />}
                          {meeting.status}
                        </span>
                      </div>
                      <div className="mt-2 flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                        <span className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" />
                          {new Date(meeting.date).toLocaleDateString()}
                        </span>
                        <span className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          {meeting.duration}
                        </span>
                        <span className="flex items-center gap-1">
                          <Users className="h-4 w-4" />
                          {meeting.participants} participants
                        </span>
                      </div>
                      {meeting.insights > 0 && (
                        <div className="mt-2">
                          <span className="text-sm text-blue-600 dark:text-blue-400">
                            {meeting.insights} insights generated
                          </span>
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <Link href={`/meetings/${meeting.id}`} asChild>
                        <Button variant="outline" size="sm">
                          View Details
                        </Button>
                      </Link>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}