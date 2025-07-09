"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Home, Brain, LineChart, MessageSquare, X, User, Settings } from "lucide-react"
import { cn } from "@/lib/utils"

type Screen = "hub" | "cognition" | "development" | "interaction" | "settings" | "profile"

interface RadialMenuProps {
  onNavigate: (screen: Screen) => void
  activeScreen: Screen
}

export default function RadialMenu({ onNavigate, activeScreen }: RadialMenuProps) {
  const [isOpen, setIsOpen] = useState(false)

  const toggleMenu = () => {
    setIsOpen(!isOpen)
  }

  const handleNavigate = (screen: Screen) => {
    onNavigate(screen)
    setIsOpen(false)
  }

  const menuItems = [
    {
      id: "hub",
      icon: Home,
      label: "Hub",
      angle: 0, // 12 o'clock
    },
    {
      id: "cognition",
      icon: Brain,
      label: "Memory",
      angle: 45, // 3 o'clock
    },
    {
      id: "development",
      icon: LineChart,
      label: "Growth",
      angle: 90, // 6 o'clock
    },
    {
      id: "interaction",
      icon: MessageSquare,
      label: "Interaction",
      angle: 135, // 9 o'clock
    },
    {
      id: "settings",
      icon: Settings,
      label: "Settings",
      angle: 180,
    },
    {
      id: "profile",
      icon: User,
      label: "User Profile",
      angle: 225,
    },
  ]

  const getItemPosition = (angle: number, radius: number) => {
    const radian = (angle * Math.PI) / 180
    const x = Math.cos(radian - Math.PI / 2) * radius
    const y = Math.sin(radian - Math.PI / 2) * radius
    return { x, y }
  }

  return (
    <>
      {/* Main radial button - stays in original position */}
      <Button
        onClick={toggleMenu}
        className={cn(
          "relative z-50 h-12 w-12 rounded-full border border-cyan-400/30 bg-slate-900 p-0 text-cyan-300 transition-all duration-500 shadow-lg",
          isOpen ? "glow animate-pulse-glow shadow-cyan-400/50" : "hover:glow-hover shadow-slate-900/50",
        )}
      >
        <span className="sr-only">Menu</span>
        <div className="flex h-full w-full items-center justify-center">
          {isOpen ? (
            <X className="h-5 w-5 transition-all duration-300" />
          ) : (
            <div className={cn("h-2 w-2 rounded-full bg-cyan-300", !isOpen && "animate-pulse")}></div>
          )}
        </div>
      </Button>

      {/* Enhanced overlay backdrop with more transparent blur */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-lg transition-all duration-700"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Large circular menu overlay - centered on screen with increased size */}
      {isOpen && (
        <div className="fixed left-1/2 top-1/2 z-40 -translate-x-1/2 -translate-y-1/2">
          {/* Multiple layered glow rings for depth - enhanced dimension with slower pulse */}
          <div className="absolute left-1/2 top-1/2 h-[600px] w-[600px] -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-cyan-400/5 bg-gradient-radial from-cyan-400/3 via-cyan-400/1 to-transparent animate-[pulse_4s_ease-in-out_infinite] shadow-[0_0_100px_rgba(0,255,255,0.1)] backdrop-blur-sm"></div>
          <div className="absolute left-1/2 top-1/2 h-[500px] w-[500px] -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-cyan-400/10 bg-gradient-radial from-cyan-400/6 via-cyan-400/3 to-transparent animate-[pulse_3.5s_ease-in-out_infinite] shadow-[0_0_80px_rgba(0,255,255,0.15)] backdrop-blur-sm"></div>
          <div className="absolute left-1/2 top-1/2 h-[400px] w-[400px] -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-cyan-400/20 bg-gradient-radial from-cyan-400/10 via-cyan-400/5 to-transparent animate-[pulse_3s_ease-in-out_infinite] shadow-[0_0_60px_rgba(0,255,255,0.2)] backdrop-blur-sm"></div>

          {/* Orbital electrons - like atoms */}
          {/* Outer orbit */}
          <div className="absolute left-1/2 top-1/2 h-[480px] w-[480px] -translate-x-1/2 -translate-y-1/2 animate-[spin_8s_linear_infinite]">
            <div className="absolute left-1/2 top-0 h-3 w-3 -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-300/80 shadow-lg shadow-cyan-400/50"></div>
          </div>
          <div className="absolute left-1/2 top-1/2 h-[480px] w-[480px] -translate-x-1/2 -translate-y-1/2 animate-[spin_8s_linear_infinite_reverse]">
            <div className="absolute left-1/2 bottom-0 h-2 w-2 -translate-x-1/2 translate-y-1/2 rounded-full bg-cyan-400/60 shadow-md shadow-cyan-400/40"></div>
          </div>

          {/* Middle orbit */}
          <div className="absolute left-1/2 top-1/2 h-[360px] w-[360px] -translate-x-1/2 -translate-y-1/2 animate-[spin_6s_linear_infinite]">
            <div className="absolute right-0 top-1/2 h-2.5 w-2.5 -translate-y-1/2 translate-x-1/2 rounded-full bg-cyan-200/70 shadow-lg shadow-cyan-400/50"></div>
          </div>
          <div className="absolute left-1/2 top-1/2 h-[360px] w-[360px] -translate-x-1/2 -translate-y-1/2 animate-[spin_6s_linear_infinite_reverse]">
            <div className="absolute left-0 top-1/2 h-2 w-2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-300/50 shadow-md shadow-cyan-400/40"></div>
          </div>

          {/* Inner orbit */}
          <div className="absolute left-1/2 top-1/2 h-[240px] w-[240px] -translate-x-1/2 -translate-y-1/2 animate-[spin_4s_linear_infinite]">
            <div className="absolute left-1/2 top-0 h-2 w-2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-100/80 shadow-lg shadow-cyan-400/50"></div>
          </div>
          <div className="absolute left-1/2 top-1/2 h-[240px] w-[240px] -translate-x-1/2 -translate-y-1/2 animate-[spin_4s_linear_infinite_reverse]">
            <div className="absolute left-1/2 bottom-0 h-1.5 w-1.5 -translate-x-1/2 translate-y-1/2 rounded-full bg-cyan-200/60 shadow-md shadow-cyan-400/40"></div>
          </div>

          {/* Menu items with increased radius */}
          {menuItems.map((item, index) => {
            const { x, y } = getItemPosition(item.angle, 180) // Increased radius from 120px to 180px
            const isActive = activeScreen === item.id
            return (
              <div
                key={item.id}
                className="absolute transition-all duration-700 ease-out"
                style={{
                  transform: `translate(${x}px, ${y}px) translate(-50%, -50%)`,
                  transitionDelay: `${index * 100}ms`,
                }}
              >
                <Button
                  onClick={() => handleNavigate(item.id as Screen)}
                  className={cn(
                    "relative h-24 w-24 rounded-full border-2 bg-gradient-to-br from-slate-800 via-slate-900 to-slate-950 p-0 text-cyan-300 transition-all duration-300 hover:scale-110 shadow-2xl",
                    isActive
                      ? "border-cyan-300 glow animate-[pulse-glow_8s_infinite] shadow-cyan-400/50 bg-gradient-to-br from-slate-700 via-slate-800 to-slate-900"
                      : "border-cyan-400/40 hover:border-cyan-400/60 hover:shadow-cyan-400/30 shadow-slate-900/80",
                  )}
                  aria-label={item.label}
                >
                  {/* Inner glow effect for active items */}
                  {isActive && (
                    <div className="absolute inset-0 rounded-full bg-gradient-to-br from-cyan-400/20 via-transparent to-cyan-400/10 animate-[pulse_6s_ease-in-out_infinite]"></div>
                  )}

                  {/* Content with larger icons */}
                  <div className="relative z-10 flex flex-col items-center gap-1.5">
                    <item.icon className={cn("h-8 w-8 transition-all duration-300", isActive && "drop-shadow-lg")} />
                    <span
                      className={cn(
                        "text-sm font-light transition-all duration-300",
                        isActive && "text-cyan-200 drop-shadow-sm",
                      )}
                    >
                      {item.label}
                    </span>
                  </div>

                  {/* Hover glow effect */}
                  <div className="absolute inset-0 rounded-full bg-gradient-to-br from-cyan-400/0 via-cyan-400/0 to-cyan-400/0 transition-all duration-300 hover:from-cyan-400/10 hover:via-cyan-400/5 hover:to-cyan-400/10"></div>
                </Button>

                {/* Pulsating dots along the connection line for active item - adjusted positions */}
                {isActive && (
                  <>
                    <div
                      className="absolute left-1/2 top-1/2 h-2 w-2 rounded-full bg-cyan-300 animate-[ping_6s_infinite] shadow-lg shadow-cyan-400/50"
                      style={{
                        transform: `translate(-50%, -50%) rotate(${item.angle}deg) translateX(60px) rotate(-${item.angle}deg)`,
                        transitionDelay: `${index * 100 + 400}ms`,
                      }}
                    />
                    <div
                      className="absolute left-1/2 top-1/2 h-1.5 w-1.5 rounded-full bg-cyan-300 animate-[ping_5s_infinite] shadow-md shadow-cyan-400/50"
                      style={{
                        transform: `translate(-50%, -50%) rotate(${item.angle}deg) translateX(120px) rotate(-${item.angle}deg)`,
                        transitionDelay: `${index * 100 + 600}ms`,
                      }}
                    />
                  </>
                )}
              </div>
            )
          })}

          {/* Enhanced center pulse indicator with multiple layers - 2D consistent with circles */}
          <div className="absolute left-1/2 top-1/2 h-16 w-16 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-cyan-400/30 bg-gradient-radial from-cyan-300/40 to-cyan-400/10 animate-[ping_6s_infinite] shadow-[0_0_40px_rgba(0,255,255,0.3)] backdrop-blur-sm"></div>
          <div className="absolute left-1/2 top-1/2 h-12 w-12 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-cyan-400/50 bg-gradient-radial from-cyan-300/60 to-cyan-400/20 animate-[pulse_8s_ease-in-out_infinite] shadow-[0_0_30px_rgba(0,255,255,0.4)] backdrop-blur-sm"></div>
          <div className="absolute left-1/2 top-1/2 h-8 w-8 -translate-x-1/2 -translate-y-1/2 rounded-full border border-cyan-300/70 bg-cyan-300/80 shadow-[0_0_20px_rgba(0,255,255,0.5)]"></div>
        </div>
      )}
    </>
  )
}
