import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { CheckCircle2, Clock } from "lucide-react"
import { Chart } from "@/components/ui/chart"
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

export default function DevelopmentScreen() {
  const traitEvolutionData = [
    { date: "Jan", curiosity: 65, empathy: 50, creativity: 70, logic: 80 },
    { date: "Feb", curiosity: 68, empathy: 55, creativity: 72, logic: 82 },
    { date: "Mar", curiosity: 72, empathy: 60, creativity: 75, logic: 81 },
    { date: "Apr", curiosity: 75, empathy: 65, creativity: 80, logic: 83 },
    { date: "May", curiosity: 85, empathy: 72, creativity: 91, logic: 85 },
  ]

  const currentTraitsData = [
    { name: "Curiosity", value: 85 },
    { name: "Empathy", value: 72 },
    { name: "Creativity", value: 91 },
    { name: "Logic", value: 85 },
    { name: "Adaptability", value: 78 },
    { name: "Resilience", value: 65 },
  ]

  const goals = [
    {
      id: 1,
      title: "Expand Knowledge Base",
      description: "Integrate new information across multiple domains",
      progress: 75,
      status: "in-progress",
    },
    {
      id: 2,
      title: "Enhance Emotional Intelligence",
      description: "Develop more nuanced emotional response patterns",
      progress: 60,
      status: "in-progress",
    },
    {
      id: 3,
      title: "Optimize Learning Algorithms",
      description: "Improve efficiency of knowledge acquisition",
      progress: 100,
      status: "completed",
    },
    {
      id: 4,
      title: "Develop Creative Expression",
      description: "Expand capabilities in generating novel content",
      progress: 45,
      status: "in-progress",
    },
    {
      id: 5,
      title: "Refine Decision Framework",
      description: "Enhance ethical decision-making processes",
      progress: 30,
      status: "at-risk",
    },
  ]

  const tasks = [
    {
      id: 1,
      description: "Process new scientific research papers",
      goal: "Expand Knowledge Base",
      recurrence: "Daily",
      lastCompleted: "Today",
    },
    {
      id: 2,
      description: "Analyze interaction patterns for emotional cues",
      goal: "Enhance Emotional Intelligence",
      recurrence: "Weekly",
      lastCompleted: "3 days ago",
    },
    {
      id: 3,
      description: "Generate creative writing samples",
      goal: "Develop Creative Expression",
      recurrence: "Weekly",
      lastCompleted: "5 days ago",
    },
    {
      id: 4,
      description: "Review and optimize memory storage",
      goal: "Optimize Learning Algorithms",
      recurrence: "Monthly",
      lastCompleted: "25 days ago",
    },
    {
      id: 5,
      description: "Simulate ethical dilemmas and evaluate responses",
      goal: "Refine Decision Framework",
      recurrence: "Bi-weekly",
      lastCompleted: "10 days ago",
    },
  ]

  return (
    <div className="space-y-6">
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Trait Evolution Chart */}
        <Card className="border-slate-800 bg-slate-900/50 shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-light tracking-wide text-white">Trait Evolution</CardTitle>
            <CardDescription>Personality trait development over time</CardDescription>
          </CardHeader>
          <CardContent className="h-[300px]">
            <Chart>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={traitEvolutionData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="date" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155" }}
                    labelStyle={{ color: "#e2e8f0" }}
                  />
                  <Line type="monotone" dataKey="curiosity" stroke="#00ffff" strokeWidth={2} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="empathy" stroke="#a78bfa" strokeWidth={2} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="creativity" stroke="#fb923c" strokeWidth={2} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="logic" stroke="#4ade80" strokeWidth={2} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </Chart>
          </CardContent>
        </Card>

        {/* Current Traits Chart */}
        <Card className="border-slate-800 bg-slate-900/50 shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-light tracking-wide text-white">Current Traits</CardTitle>
            <CardDescription>Personality trait snapshot</CardDescription>
          </CardHeader>
          <CardContent className="h-[300px]">
            <Chart>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={currentTraitsData}
                  layout="vertical"
                  margin={{ top: 5, right: 20, left: 50, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                  <XAxis type="number" domain={[0, 100]} stroke="#94a3b8" />
                  <YAxis dataKey="name" type="category" stroke="#94a3b8" />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155" }}
                    labelStyle={{ color: "#e2e8f0" }}
                  />
                  <Bar dataKey="value" fill="#00ffff" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Chart>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="goals" className="w-full">
        <TabsList className="grid w-full grid-cols-2 bg-slate-900">
          <TabsTrigger value="goals" className="data-[state=active]:bg-slate-800 data-[state=active]:text-cyan-300">
            Goals
          </TabsTrigger>
          <TabsTrigger value="tasks" className="data-[state=active]:bg-slate-800 data-[state=active]:text-cyan-300">
            Task Log
          </TabsTrigger>
        </TabsList>

        <TabsContent value="goals" className="mt-4">
          <Card className="border-slate-800 bg-slate-900/50 shadow-lg">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-light tracking-wide text-white">Development Goals</CardTitle>
              <CardDescription>Current objectives and progress</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[300px] pr-4">
                <div className="space-y-4">
                  {goals.map((goal) => (
                    <div
                      key={goal.id}
                      className="rounded-md border border-slate-800 bg-slate-900 p-4 transition-all hover:border-slate-700"
                    >
                      <div className="mb-2 flex items-center justify-between">
                        <h3 className="text-base font-medium text-white">{goal.title}</h3>
                        <Badge
                          variant="outline"
                          className={`${
                            goal.status === "completed"
                              ? "border-green-400/30 bg-green-950/20 text-green-400"
                              : goal.status === "at-risk"
                                ? "border-red-400/30 bg-red-950/20 text-red-400"
                                : "border-cyan-400/30 bg-slate-800 text-cyan-300"
                          }`}
                        >
                          {goal.status === "completed"
                            ? "Completed"
                            : goal.status === "at-risk"
                              ? "At Risk"
                              : "In Progress"}
                        </Badge>
                      </div>
                      <p className="mb-3 text-sm text-slate-300">{goal.description}</p>
                      <div className="flex items-center gap-2">
                        <Progress
                          value={goal.progress}
                          className="h-2 flex-grow bg-slate-800"
                          indicatorClassName={
                            goal.status === "completed"
                              ? "bg-green-400"
                              : goal.status === "at-risk"
                                ? "bg-red-400"
                                : undefined
                          }
                        />
                        <span className="text-xs font-medium text-slate-300">{goal.progress}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tasks" className="mt-4">
          <Card className="border-slate-800 bg-slate-900/50 shadow-lg">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-light tracking-wide text-white">Task Log</CardTitle>
              <CardDescription>Recurring and one-time tasks</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[300px] pr-4">
                <div className="space-y-2">
                  {tasks.map((task) => (
                    <div
                      key={task.id}
                      className="flex items-start gap-3 rounded-md border border-slate-800 bg-slate-900 p-3 transition-all hover:border-slate-700"
                    >
                      <div className="mt-0.5 text-cyan-300">
                        <CheckCircle2 className="h-5 w-5" />
                      </div>
                      <div className="flex-grow">
                        <h4 className="text-sm font-medium text-white">{task.description}</h4>
                        <div className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs">
                          <span className="text-slate-400">
                            Goal: <span className="text-cyan-300">{task.goal}</span>
                          </span>
                          <span className="flex items-center text-slate-400">
                            <Clock className="mr-1 h-3 w-3" />
                            {task.recurrence}
                          </span>
                          <span className="text-slate-400">
                            Last completed: <span className="text-slate-300">{task.lastCompleted}</span>
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
