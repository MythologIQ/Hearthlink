"use client"

import { useState } from "react"
import RadialMenu from "@/components/radial-menu"
import HubScreen from "@/components/screens/hub-screen"
import CognitionScreen from "@/components/screens/cognition-screen"
import DevelopmentScreen from "@/components/screens/development-screen"
import InteractionScreen from "@/components/screens/interaction-screen"

type Screen = "hub" | "cognition" | "development" | "interaction"

export default function Dashboard() {
  const [activeScreen, setActiveScreen] = useState<Screen>("hub")

  const getPageTitle = () => {
    switch (activeScreen) {
      case "hub":
        return (
          <>
            <span className="text-cyan-300 glow-text">Alden's</span> Hub
          </>
        )
      case "cognition":
        return (
          <>
            Cognition & <span className="text-cyan-300 glow-text">Memory</span>
          </>
        )
      case "development":
        return (
          <>
            Development & <span className="text-cyan-300 glow-text">Directives</span>
          </>
        )
      case "interaction":
        return (
          <>
            <span className="text-cyan-300 glow-text">Interaction</span> Console
          </>
        )
      default:
        return (
          <>
            <span className="text-cyan-300 glow-text">Alden's</span> Hub
          </>
        )
    }
  }

  const renderScreen = () => {
    switch (activeScreen) {
      case "hub":
        return <HubScreen />
      case "cognition":
        return <CognitionScreen />
      case "development":
        return <DevelopmentScreen />
      case "interaction":
        return <InteractionScreen />
      default:
        return <HubScreen />
    }
  }

  return (
    <div className="flex h-screen w-full overflow-hidden bg-slate-950 text-white relative">
      {/* Radial Menu Button - Left Side */}
      <div className="absolute left-6 top-6 z-30">
        <RadialMenu onNavigate={setActiveScreen} activeScreen={activeScreen} />
      </div>

      {/* Centered Page Title */}
      <div className="absolute left-1/2 top-6 z-20 transform -translate-x-1/2">
        <h1 className="text-2xl font-light tracking-wider text-white whitespace-nowrap">{getPageTitle()}</h1>
      </div>

      {/* Center Panel */}
      <div className="flex-grow overflow-auto p-6 pt-20 relative z-10">
        <div className="animate-fade-in">{renderScreen()}</div>
      </div>
    </div>
  )
}
