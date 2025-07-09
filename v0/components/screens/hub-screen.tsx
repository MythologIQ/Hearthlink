import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Brain, Heart, Zap, Lightbulb } from "lucide-react"

export default function HubScreen() {
  const traits = [
    { name: "Curiosity", value: 85, icon: Brain },
    { name: "Empathy", value: 72, icon: Heart },
    { name: "Energy", value: 64, icon: Zap },
    { name: "Creativity", value: 91, icon: Lightbulb },
  ]

  const alerts = [
    { id: 1, message: "New memory fragment analyzed", time: "2 hours ago", priority: "low" },
    { id: 2, message: "Emotional pattern detected", time: "5 hours ago", priority: "medium" },
    { id: 3, message: "Goal progress milestone reached", time: "Yesterday", priority: "high" },
    { id: 4, message: "New interaction pattern identified", time: "2 days ago", priority: "medium" },
    { id: 5, message: "Memory consolidation complete", time: "3 days ago", priority: "low" },
  ]

  const goals = [
    { id: 1, title: "Knowledge Expansion", progress: 75 },
    { id: 2, title: "Emotional Intelligence", progress: 60 },
    { id: 3, title: "Creative Expression", progress: 45 },
    { id: 4, title: "Adaptive Learning", progress: 90 },
  ]

  return (
    <div className="space-y-6">
      {/* Status Card */}
      <Card className="border-slate-800 bg-slate-900/50 shadow-lg">
        <CardHeader className="pb-2">
          <CardTitle className="text-xl font-light tracking-wide text-white">Active Construct</CardTitle>
          <CardDescription>Current status and emotional state</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div>
              <h3 className="text-2xl font-light text-white">Alden</h3>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="border-cyan-400/30 text-cyan-300">
                  Curious
                </Badge>
                <span className="text-sm text-slate-400">v2.4.7</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Traits */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {traits.map((trait) => (
          <Card key={trait.name} className="border-slate-800 bg-slate-900/50 shadow-lg">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <trait.icon className="h-5 w-5 text-cyan-300" />
                  <h3 className="text-sm font-medium text-white">{trait.name}</h3>
                </div>
                <span className="text-sm text-cyan-300">{trait.value}%</span>
              </div>
              <Progress value={trait.value} className="mt-2 h-1 bg-slate-800" />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Alerts */}
      <Card className="border-slate-800 bg-slate-900/50 shadow-lg">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg font-light tracking-wide text-white">Priority Alerts</CardTitle>
          <CardDescription>Recent feedback and notifications</CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-40 pr-4">
            <div className="space-y-2">
              {alerts.map((alert) => (
                <div
                  key={alert.id}
                  className="flex items-center gap-2 rounded-md border border-slate-800 bg-slate-900 p-2"
                >
                  <div
                    className={`h-2 w-2 rounded-full ${
                      alert.priority === "high"
                        ? "bg-red-400"
                        : alert.priority === "medium"
                          ? "bg-amber-400"
                          : "bg-cyan-400"
                    }`}
                  ></div>
                  <div className="flex-grow">
                    <p className="text-sm text-white">{alert.message}</p>
                    <p className="text-xs text-slate-400">{alert.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>

      {/* Goals */}
      <Card className="border-slate-800 bg-slate-900/50 shadow-lg">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg font-light tracking-wide text-white">Active Goals</CardTitle>
          <CardDescription>Current objectives and progress</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2">
            {goals.map((goal) => (
              <div key={goal.id} className="space-y-1">
                <div className="flex items-center justify-between">
                  <h4 className="text-sm font-medium text-white">{goal.title}</h4>
                  <span className="text-xs text-cyan-300">{goal.progress}%</span>
                </div>
                <Progress value={goal.progress} className="h-1 bg-slate-800" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
