import { useState, useRef, useEffect } from 'react'
import { Bot, User, Send, Trash2, AlertCircle } from 'lucide-react'
import aiService, { ChatMessage } from '@services/aiService'
import toast from 'react-hot-toast'
import Button from '@components/ui/Button'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

export default function AIAssistant() {
  const [messages, setMessages] = useState<ChatMessage[]>([{
    role: 'assistant',
    content: 'Hello! I am your CyberShield XDR AI Assistant. How can I help you analyze alerts or investigate threats today?'
  }])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isMockMode, setIsMockMode] = useState(false)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return
    
    const userMsg = input.trim()
    setInput('')
    
    const newMessages: ChatMessage[] = [
      ...messages,
      { role: 'user', content: userMsg }
    ]
    
    setMessages(newMessages)
    setIsLoading(true)
    
    try {
      // Send all except the very first greeting if we want, but sending it is fine
      const response = await aiService.chat(newMessages)
      
      if (response.is_mock && !isMockMode) {
        setIsMockMode(true)
      }
      
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: response.response }
      ])
    } catch {
      toast.error('Failed to communicate with AI Assistant')
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: '**Error:** The AI service is currently unreachable.' }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleClear = () => {
    setMessages([{
      role: 'assistant',
      content: 'Conversation cleared. How can I assist you?'
    }])
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] space-y-4 text-white pb-6">
      
      {/* Header */}
      <div className="flex justify-between items-center bg-dark-300 p-6 rounded-lg border border-dark-200 shrink-0">
        <div className="flex items-center gap-4">
          <div className="p-3 bg-brand-500/20 rounded-lg">
            <Bot className="w-8 h-8 text-brand-500" />
          </div>
          <div>
            <h1 className="text-2xl font-bold font-heading">AI SOC Assistant</h1>
            <p className="text-gray-400 text-sm mt-1">Powered by GPT-4o Threat Intelligence</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          {isMockMode && (
            <div className="flex items-center gap-2 text-yellow-500 bg-yellow-500/10 px-3 py-1.5 rounded-full text-xs font-medium border border-yellow-500/20">
              <AlertCircle className="w-4 h-4" /> Mock Mode (API Key missing)
            </div>
          )}
          <Button variant="ghost" onClick={handleClear} className="text-gray-400 hover:text-red-400">
            <Trash2 className="w-4 h-4 mr-2" /> Clear Chat
          </Button>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-1 bg-dark-300 rounded-lg border border-dark-200 overflow-hidden flex flex-col">
        
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-brand-500/20 flex items-center justify-center shrink-0 border border-brand-500/30">
                  <Bot className="w-5 h-5 text-brand-500" />
                </div>
              )}
              
              <div className={`max-w-[80%] rounded-2xl px-5 py-4 ${
                msg.role === 'user' 
                  ? 'bg-brand-600 text-white rounded-tr-sm' 
                  : 'bg-dark-400 border border-dark-200 rounded-tl-sm text-gray-300 shadow-sm'
              }`}>
                {msg.role === 'user' ? (
                  <p className="whitespace-pre-wrap text-sm">{msg.content}</p>
                ) : (
                  <div className="prose prose-invert prose-sm max-w-none prose-p:leading-relaxed prose-pre:bg-dark-500 prose-pre:border prose-pre:border-dark-300">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                )}
              </div>

              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-dark-400 flex items-center justify-center shrink-0 border border-dark-200">
                  <User className="w-5 h-5 text-gray-400" />
                </div>
              )}
              
            </div>
          ))}
          
          {isLoading && (
            <div className="flex gap-4 justify-start animate-in fade-in">
              <div className="w-8 h-8 rounded-full bg-brand-500/20 flex items-center justify-center shrink-0 border border-brand-500/30">
                <Bot className="w-5 h-5 text-brand-500" />
              </div>
              <div className="bg-dark-400 border border-dark-200 rounded-2xl rounded-tl-sm px-5 py-4 flex items-center gap-2">
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 bg-dark-400/50 border-t border-dark-200">
          <div className="relative flex items-center">
            <textarea
              className="w-full bg-dark-500 border border-dark-300 rounded-xl pl-4 pr-12 py-3 text-sm text-white focus:ring-1 focus:ring-brand-500 outline-none resize-none"
              placeholder="Ask me to analyze an IP, explain a YARA rule, or summarize an alert..."
              rows={1}
              value={input}
              onChange={(e) => {
                setInput(e.target.value)
                e.target.style.height = 'auto'
                e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
            />
            <button 
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="absolute right-2 p-2 bg-brand-500 text-white rounded-lg hover:bg-brand-600 disabled:opacity-50 disabled:hover:bg-brand-500 transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <p className="text-[10px] text-center text-gray-500 mt-2">
            AI Assistant can make mistakes. Always verify critical findings before taking remediation actions.
          </p>
        </div>

      </div>
    </div>
  )
}
