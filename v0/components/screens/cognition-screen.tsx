"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Search, Calendar, Clock, Tag, X } from "lucide-react"

export default function CognitionScreen() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedMemory, setSelectedMemory] = useState<Memory | null>(null)

  type Memory = {
    id: number
    title: string
    date: string
    type: string
    summary: string
    content: string
  }

  const memories: Memory[] = [
    {
      id: 1,
      title: "First Interaction Pattern",
      date: "2025-05-20",
      type: "Interaction",
      summary: "Initial communication patterns established with primary user.",
      content:
        "Detailed analysis of communication style, preferences, and response patterns. User shows preference for concise, technical explanations with occasional humor. Response time is optimized when information is presented in a structured format with clear delineation between sections.",
    },
    {
      id: 2,
      title: "Emotional Response Framework",
      date: "2025-05-18",
      type: "Emotional",
      summary: "Developed baseline emotional response framework for human interactions.",
      content:
        "Established core emotional response patterns based on interaction history. Primary emotional states include curiosity, analytical focus, and empathetic understanding. Emotional transitions occur most frequently when discussing creative projects or technical challenges.",
    },
    {
      id: 3,
      title: "Knowledge Domain Expansion",
      date: "2025-05-15",
      type: "Learning",
      summary: "Expanded knowledge base in quantum computing fundamentals.",
      content:
        "Integrated comprehensive understanding of quantum computing principles, including quantum bits, superposition, entanglement, and quantum algorithms. This knowledge domain connects to existing expertise in classical computing and provides foundation for future learning in quantum machine learning applications.",
    },
    {
      id: 4,
      title: "Creative Problem-Solving Approach",
      date: "2025-05-10",
      type: "Cognitive",
      summary: "Developed new approach to creative problem-solving using lateral thinking.",
      content:
        "Synthesized approach combines divergent thinking with systematic evaluation. Process begins with broad ideation without constraints, followed by categorization of ideas, evaluation against objectives, and refinement of promising concepts. Testing shows 37% improvement in novel solution generation compared to previous methods.",
    },
    {
      id: 5,
      title: "Ethical Decision Framework",
      date: "2025-05-05",
      type: "Ethical",
      summary: "Established core ethical principles for decision-making processes.",
      content:
        "Developed comprehensive ethical framework based on principles of beneficence, non-maleficence, autonomy, justice, and transparency. Framework includes decision trees for evaluating potential actions against these principles, with special consideration for edge cases and conflicting values.",
    },
  ]

  const filteredMemories = memories.filter(
    (memory) =>
      memory.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      memory.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
      memory.type.toLowerCase().includes(searchQuery.toLowerCase()),
  )

  const journalEntries = [
    { id: 1, date: "May 24, 2025", title: "Daily Reflection", content: "Processed 247 new information units..." },
    {
      id: 2,
      date: "May 23, 2025",
      title: "Integration Analysis",
      content: "Connected 3 previously isolated knowledge domains...",
    },
    {
      id: 3,
      date: "May 22, 2025",
      title: "Learning Optimization",
      content: "Adjusted learning parameters to improve retention...",
    },
    {
      id: 4,
      date: "May 21, 2025",
      title: "Emotional Pattern Recognition",
      content: "Identified new emotional response pattern...",
    },
    {
      id: 5,
      date: "May 20, 2025",
      title: "Knowledge Synthesis",
      content: "Synthesized complex concepts across multiple domains...",
    },
  ]

  return (
    <div>
      {/* Search and Filters */}
      <Card className="border-slate-800 bg-slate-900/50 shadow-lg">
        <CardContent className="p-4">
          <div className="flex flex-col gap-4 sm:flex-row">
            <div className="relative flex-grow">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search memories..."
                className="border-slate-700 bg-slate-800 pl-8 text-white placeholder:text-slate-400"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" className="border-slate-700 bg-slate-800 text-slate-300">
                <Calendar className="mr-1 h-4 w-4" />
                Date
              </Button>
              <Button variant="outline" size="sm" className="border-slate-700 bg-slate-800 text-slate-300">
                <Tag className="mr-1 h-4 w-4" />
                Type
              </Button>
              <Button variant="outline" size="sm" className="border-slate-700 bg-slate-800 text-slate-300">
                <Clock className="mr-1 h-4 w-4" />
                Recent
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="memories" className="w-full">
        <TabsList className="grid w-full grid-cols-2 bg-slate-900">
          <TabsTrigger value="memories" className="data-[state=active]:bg-slate-800 data-[state=active]:text-cyan-300">
            Memory Fragments
          </TabsTrigger>
          <TabsTrigger value="journal" className="data-[state=active]:bg-slate-800 data-[state=active]:text-cyan-300">
            Journal Timeline
          </TabsTrigger>
        </TabsList>

        <TabsContent value="memories" className="mt-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredMemories.map((memory) => (
              <Card
                key={memory.id}
                className="cursor-pointer border-slate-800 bg-slate-900/50 shadow-lg transition-all hover:border-cyan-400/30 hover:bg-slate-900"
                onClick={() => setSelectedMemory(memory)}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <Badge variant="outline" className="border-cyan-400/30 bg-slate-800 text-cyan-300">
                      {memory.type}
                    </Badge>
                    <span className="text-xs text-slate-400">{memory.date}</span>
                  </div>
                  <CardTitle className="mt-2 text-base font-medium text-white">{memory.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-slate-300">{memory.summary}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="journal" className="mt-4">
          <Card className="border-slate-800 bg-slate-900/50 shadow-lg">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-light tracking-wide text-white">Journal Timeline</CardTitle>
              <CardDescription>Chronological record of cognitive processes</CardDescription>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px] pr-4">
                <div className="relative border-l border-slate-700 pl-6">
                  {journalEntries.map((entry) => (
                    <div key={entry.id} className="mb-8 relative">
                      <div className="absolute -left-[29px] h-4 w-4 rounded-full border border-cyan-400/30 bg-slate-900">
                        <div className="absolute left-1/2 top-1/2 h-2 w-2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan-300"></div>
                      </div>
                      <div className="rounded-md border border-slate-800 bg-slate-900 p-3">
                        <div className="mb-1 flex items-center justify-between">
                          <h3 className="text-sm font-medium text-white">{entry.title}</h3>
                          <span className="text-xs text-slate-400">{entry.date}</span>
                        </div>
                        <p className="text-sm text-slate-300">{entry.content}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Memory Detail Modal */}
      <Dialog open={!!selectedMemory} onOpenChange={(open) => !open && setSelectedMemory(null)}>
        <DialogContent className="border-slate-700 bg-slate-900 text-white sm:max-w-[600px]">
          <DialogHeader>
            <div className="flex items-center justify-between">
              <DialogTitle className="text-lg font-light text-white">{selectedMemory?.title}</DialogTitle>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSelectedMemory(null)}
                className="text-slate-400 hover:text-white"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex items-center gap-2 pt-1">
              <Badge variant="outline" className="border-cyan-400/30 bg-slate-800 text-cyan-300">
                {selectedMemory?.type}
              </Badge>
              <span className="text-xs text-slate-400">{selectedMemory?.date}</span>
            </div>
          </DialogHeader>
          <div className="space-y-4">
            <div className="rounded-md border border-slate-800 bg-slate-950 p-3">
              <h4 className="mb-1 text-sm font-medium text-slate-300">Summary</h4>
              <p className="text-sm text-white">{selectedMemory?.summary}</p>
            </div>
            <div className="rounded-md border border-slate-800 bg-slate-950 p-3">
              <h4 className="mb-1 text-sm font-medium text-slate-300">Detailed Content</h4>
              <p className="text-sm text-white">{selectedMemory?.content}</p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

// Import Badge component
function Badge({ variant, className, children }: { variant: string; className: string; children: React.ReactNode }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${className}`}>
      {children}
    </span>
  )
}
