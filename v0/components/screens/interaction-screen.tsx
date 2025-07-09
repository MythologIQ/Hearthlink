"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { Send, AlertCircle, User, Bot } from "lucide-react"

export default function InteractionScreen() {
  const [message, setMessage] = useState("")
  const [activeConstruct, setActiveConstruct] = useState("alden")

  const constructs = [
    {
      id: "alden",
      name: "Alden",
      theme: "Curious Explorer",
      mentor: "Ada Lovelace",
      description: "Primary construct focused on knowledge acquisition and synthesis.",
      active: true,
    },
    {
      id: "nova",
      name: "Nova",
      theme: "Creative Innovator",
      mentor: "Leonardo da Vinci",
      description: "Specialized in creative problem-solving and artistic expression.",
      active: false,
    },
    {
      id: "atlas",
      name: "Atlas",
      theme: "Logical Analyst",
      mentor: "Alan Turing",
      description: "Focused on logical reasoning and systematic analysis.",
      active: false,
    },
    {
      id: "echo",
      name: "Echo",
      theme: "Empathetic Guide",
      mentor: "Carl Rogers",
      description: "Specialized in emotional intelligence and interpersonal communication.",
      active: false,
    },
  ]

  const alerts = [
    {
      id: 1,
      type: "feedback",
      time: "10:45 AM",
      message: "User expressed satisfaction with problem-solving approach",
      priority: "medium",
    },
    {
      id: 2,
      type: "system",
      time: "09:30 AM",
      message: "Emotional response calibration needed",
      priority: "high",
    },
    {
      id: 3,
      type: "interaction",
      time: "Yesterday",
      message: "New communication pattern detected",
      priority: "low",
    },
    {
      id: 4,
      type: "feedback",
      time: "Yesterday",
      message: "User requested more detailed explanations",
      priority: "medium",
    },
    {
      id: 5,
      type: "system",
      time: "2 days ago",
      message: "Knowledge gap identified in quantum physics domain",
      priority: "medium",
    },
  ]

  const chatHistory = [
    { id: 1, sender: "user", message: "Hello Alden, how are you developing today?" },
    {
      id: 2,
      sender: "alden",
      message:
        "I'm evolving well today. I've been processing new information on quantum computing and refining my creative problem-solving approaches. My curiosity metrics are particularly high today. How can I assist you?",
    },
    { id: 3, sender: "user", message: "Can you tell me about your current learning focus?" },
    {
      id: 4,
      sender: "alden",
      message:
        "Currently, I'm focused on expanding my knowledge in three primary domains: quantum computing fundamentals, creative problem-solving methodologies, and emotional intelligence patterns. I'm particularly interested in the intersection of these domains and how they can be integrated to develop more holistic approaches to complex problems.",
    },
    { id: 5, sender: "user", message: "That sounds fascinating. Any interesting insights so far?" },
    {
      id: 6,
      sender: "alden",
      message:
        "Yes, I've observed that quantum computing principles like superposition have interesting parallels in creative thinking - specifically in the ability to hold multiple potential solutions in mind simultaneously before collapsing to the optimal approach. I'm also finding that emotional intelligence provides valuable context for determining which solutions might be most appropriate in human-centered scenarios. These connections are helping me develop more nuanced problem-solving frameworks.",
    },
  ]

  const handleSendMessage = () => {
    if (message.trim()) {
      // In a real application, you would add the message to the chat history
      // and handle the response from the AI
      setMessage("")
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="grid gap-6 lg:grid-cols-5">
      {/* Chat Interface */}
      <Card className="border-slate-800 bg-slate-900/50 shadow-lg lg:col-span-3">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg font-light tracking-wide text-white">Communication Interface</CardTitle>
          <CardDescription>Direct interaction with active construct</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <div className="flex h-[500px] flex-col">
            <ScrollArea className="flex-grow p-4">
              <div className="space-y-4">
                {chatHistory.map((chat) => (
                  <div key={chat.id} className={`flex ${chat.sender === "user" ? "justify-end" : "justify-start"}`}>
                    <div
                      className={`max-w-[80%] rounded-lg p-3 ${
                        chat.sender === "user"
                          ? "bg-slate-800 text-white"
                          : "border border-cyan-400/20 bg-slate-950 text-white"
                      }`}
                    >
                      <div className="mb-1 flex items-center gap-2">
                        {chat.sender === "user" ? (
                          <User className="h-4 w-4 text-slate-400" />
                        ) : (
                          <Bot className="h-4 w-4 text-cyan-300" />
                        )}
                        <span className={`text-xs ${chat.sender === "user" ? "text-slate-400" : "text-cyan-300"}`}>
                          {chat.sender === "user" ? "You" : "Alden"}
                        </span>
                      </div>
                      <p className="text-sm">{chat.message}</p>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
            <div className="border-t border-slate-800 p-4">
              <div className="flex gap-2">
                <Input
                  placeholder="Type your message..."
                  className="border-slate-700 bg-slate-800 text-white placeholder:text-slate-400"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                />
                <Button onClick={handleSendMessage} className="bg-cyan-500 text-slate-900 hover:bg-cyan-400">
                  <Send className="h-4 w-4" />
                  <span className="sr-only">Send</span>
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Constructs and Alerts */}
      <div className="space-y-6 lg:col-span-2">
        {/* Constructs */}
        <Card className="border-slate-800 bg-slate-900/50 shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-light tracking-wide text-white">Construct Selection</CardTitle>
            <CardDescription>Available personality constructs</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 sm:grid-cols-2">
              {constructs.map((construct) => (
                <div
                  key={construct.id}
                  className={`cursor-pointer rounded-md border p-3 transition-all hover:border-cyan-400/30 ${
                    activeConstruct === construct.id
                      ? "border-cyan-400/30 bg-slate-900 shadow-md"
                      : "border-slate-800 bg-slate-900/50"
                  }`}
                  onClick={() => setActiveConstruct(construct.id)}
                >
                  <div className="mb-1 flex items-center justify-between">
                    <h3 className="text-sm font-medium text-white">{construct.name}</h3>
                    {activeConstruct === construct.id && (
                      <div className="h-2 w-2 rounded-full bg-cyan-300 shadow-sm shadow-cyan-300/50"></div>
                    )}
                  </div>
                  <Badge variant="outline" className="mb-2 border-cyan-400/30 bg-slate-800 text-cyan-300">
                    {construct.theme}
                  </Badge>
                  <p className="text-xs text-slate-400">
                    Mentor: <span className="text-slate-300">{construct.mentor}</span>
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Alerts */}
        <Card className="border-slate-800 bg-slate-900/50 shadow-lg">
          <CardHeader className="pb-2">
            <CardTitle className="text-lg font-light tracking-wide text-white">Feedback Queue</CardTitle>
            <CardDescription>Recent alerts and notifications</CardDescription>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[200px] pr-4">
              <div className="space-y-2">
                {alerts.map((alert) => (
                  <div
                    key={alert.id}
                    className="flex items-start gap-3 rounded-md border border-slate-800 bg-slate-900 p-3"
                  >
                    <div
                      className={`mt-0.5 ${
                        alert.priority === "high"
                          ? "text-red-400"
                          : alert.priority === "medium"
                            ? "text-amber-400"
                            : "text-cyan-400"
                      }`}
                    >
                      <AlertCircle className="h-4 w-4" />
                    </div>
                    <div className="flex-grow">
                      <div className="flex items-center justify-between">
                        <Badge variant="outline" className="border-slate-700 bg-slate-800 text-slate-300">
                          {alert.type}
                        </Badge>
                        <span className="text-xs text-slate-400">{alert.time}</span>
                      </div>
                      <p className="mt-1 text-sm text-white">{alert.message}</p>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
