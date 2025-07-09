import { Bell, User, Settings, Activity } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function UtilityStrip() {
  return (
    <div className="flex w-16 flex-col items-center border-l border-slate-800 bg-slate-900/50 py-4">
      <div className="mb-8 flex flex-col items-center gap-6">
        <Button variant="ghost" size="icon" className="text-slate-400 hover:text-cyan-300">
          <Bell className="h-5 w-5" />
          <span className="sr-only">Notifications</span>
        </Button>
        <Button variant="ghost" size="icon" className="text-slate-400 hover:text-cyan-300">
          <User className="h-5 w-5" />
          <span className="sr-only">Profile</span>
        </Button>
        <Button variant="ghost" size="icon" className="text-slate-400 hover:text-cyan-300">
          <Settings className="h-5 w-5" />
          <span className="sr-only">Settings</span>
        </Button>
      </div>

      <div className="mt-auto flex flex-col items-center gap-2">
        <div className="h-16 w-1 rounded-full bg-slate-800">
          <div className="h-[60%] w-full rounded-full bg-gradient-to-t from-cyan-300 to-cyan-400 glow"></div>
        </div>
        <span className="text-xs text-slate-400">60%</span>
        <Activity className="h-4 w-4 text-cyan-300" />
      </div>
    </div>
  )
}
