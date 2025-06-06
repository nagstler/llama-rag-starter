'use client';

import { useState, useCallback, useRef, useEffect } from 'react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  reasoning?: ReasoningStep[];
  fullText?: string;
  isAnimating?: boolean;
}

interface ReasoningStep {
  type: string;
  content?: string;
  reasoning?: string;
  tool?: string;
  input?: string;
}

export default function ChatView() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showReasoningSteps, setShowReasoningSteps] = useState(true);
  const [isStreaming, setIsStreaming] = useState(false);
  const processedEvents = useRef(new Set<string>());
  const currentContent = useRef('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isLoading) return;

    console.log('Starting sendMessage for:', text);
    
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    processedEvents.current.clear();

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '',
      reasoning: [],
      fullText: '',
    };

    setMessages(prev => [...prev, assistantMessage]);

    try {
      const apiHost = process.env.NEXT_PUBLIC_API_HOST || 'http://localhost:8000';
      const response = await fetch(`${apiHost}/agent/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error('No response stream');

      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            
            try {
              const parsed = JSON.parse(data);
              console.log('SSE Event:', parsed.type, parsed.chunk || parsed.step?.type || 'no-data');
              
              if (parsed.type === 'reasoning') {
                setMessages(prev => {
                  const newMessages = [...prev];
                  const lastMessage = newMessages[newMessages.length - 1];
                  if (lastMessage.role === 'assistant') {
                    const existing = lastMessage.reasoning || [];
                    const stepKey = `${parsed.step.type}-${parsed.step.reasoning || parsed.step.content || ''}`;
                    const isDuplicate = existing.some(step => 
                      `${step.type}-${step.reasoning || step.content || ''}` === stepKey
                    );
                    
                    if (!isDuplicate) {
                      lastMessage.reasoning = [...existing, parsed.step];
                    }
                  }
                  return newMessages;
                });
              } else if (parsed.type === 'content_start') {
                currentContent.current = '';
                setIsStreaming(true);
                setMessages(prev => {
                  const newMessages = [...prev];
                  const lastMessage = newMessages[newMessages.length - 1];
                  if (lastMessage.role === 'assistant') {
                    lastMessage.content = '';
                    lastMessage.isAnimating = true;
                  }
                  return newMessages;
                });
              } else if (parsed.type === 'content_char') {
                const eventId = parsed.id;
                
                if (eventId && processedEvents.current.has(eventId)) {
                  return;
                }
                if (eventId) {
                  processedEvents.current.add(eventId);
                }
                
                currentContent.current += parsed.char;
                
                setMessages(prev => {
                  const newMessages = [...prev];
                  const lastMessage = newMessages[newMessages.length - 1];
                  if (lastMessage.role === 'assistant' && lastMessage.isAnimating) {
                    lastMessage.content = currentContent.current;
                  }
                  return newMessages;
                });
              } else if (parsed.type === 'content_end') {
                setIsStreaming(false);
                setMessages(prev => {
                  const newMessages = [...prev];
                  const lastMessage = newMessages[newMessages.length - 1];
                  if (lastMessage.role === 'assistant') {
                    lastMessage.isAnimating = false;
                  }
                  return newMessages;
                });
              }
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => {
        const newMessages = [...prev];
        const lastMessage = newMessages[newMessages.length - 1];
        if (lastMessage.role === 'assistant') {
          lastMessage.content = 'Sorry, an error occurred while processing your request.';
        }
        return newMessages;
      });
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
    }
  }, []);

  const handleExampleClick = (example: string) => {
    sendMessage(example);
  };

  return (
    <div className="flex h-full bg-white">
      {/* Sidebar */}
      <div className="w-64 sidebar">
        <h2 className="sidebar-title">Chat Controls</h2>
        
        <div className="space-y-4">
          <button
            onClick={() => setMessages([])}
            className="clear-button"
          >
            Clear Chat
          </button>
          
          <div className="bg-white rounded-lg p-3 border border-gray-200">
            <div className="text-sm text-gray-600">
              Messages: <span className="font-medium text-gray-800">{messages.length}</span>
            </div>
          </div>
          
          <div className="border-t pt-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={showReasoningSteps}
                onChange={(e) => setShowReasoningSteps(e.target.checked)}
                className="rounded"
              />
              <span className="text-sm text-gray-700">Show Reasoning Steps</span>
            </label>
            <p className="text-xs text-gray-500 mt-1">
              View the agent's thinking process
            </p>
          </div>
          
          <div className="border-t pt-4">
            <h3 className="font-medium mb-3 text-gray-800">Example Questions</h3>
            <div className="space-y-2">
              {[
                "Help me analyze this data",
                "Research information about...",
                "Create a summary of...",
                "What insights can you provide?"
              ].map((question, i) => (
                <button
                  key={i}
                  onClick={() => handleExampleClick(question)}
                  disabled={isLoading}
                  className="example-button"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        <header className="chat-header">
          <h1 className="chat-header-title">AI Assistant</h1>
          <p className="chat-header-subtitle">Ask me anything - I can help with analysis, research, and various tasks.</p>
        </header>
        
        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-4">
          {messages.length === 0 && (
            <div className="welcome-container">
              <div className="welcome-icon">🤖</div>
              <h2 className="welcome-title">AI Assistant</h2>
              <p className="welcome-subtitle">
                I'm here to help with various tasks including data analysis, research, document processing, and more.
              </p>
              <div className="welcome-tip">
                💡 Try asking about anything you need help with, or click an example question in the sidebar.
              </div>
            </div>
          )}
          
          {messages.map((message) => (
            <div
              key={message.id}
              className={`mb-6 flex message-fade-in ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`${
                  message.role === 'user'
                    ? 'user-message'
                    : 'assistant-message'
                }`}
              >
                
                {/* Reasoning Steps */}
                {message.role === 'assistant' && showReasoningSteps && message.reasoning && message.reasoning.length > 0 && (
                  <div className="reasoning-container">
                    <div className="reasoning-title">
                      Reasoning Process
                    </div>
                    <div className="reasoning-timeline">
                      {Array.from(new Map(message.reasoning.map(step => [
                        `${step.type}-${step.reasoning || step.content || ''}`, step
                      ])).values()).map((step, index, array) => (
                        <div 
                          key={index} 
                          className={`reasoning-step ${index === array.length - 1 ? 'active' : 'completed'}`}
                        >
                          <div className="reasoning-step-content">
                            <div className="reasoning-step-header">
                              <span className="reasoning-icon">{getStepIcon(step.type)}</span>
                              <span className="reasoning-label">
                                {getStepLabel(step.type)}
                              </span>
                            </div>
                            <div className="reasoning-content">
                              {step.reasoning || step.content || formatStepContent(step)}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Message Content */}
                <div className={`message-content ${
                  message.role === 'assistant' && isStreaming && messages.indexOf(message) === messages.length - 1 
                    ? 'typing-cursor' 
                    : ''
                }`}>
                  {message.content}
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start mb-6">
              <div className="loading-indicator">
                <div className="loading-spinner"></div>
                <span className="text-gray-700">Agent is thinking...</span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        {/* Input */}
        <div className="border-t bg-white px-6 py-6">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              sendMessage(input);
            }}
            className="flex gap-3 max-w-4xl mx-auto"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
              placeholder="Ask me anything..."
              className="flex-1 chat-input"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="send-button"
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

function getStepIcon(type: string): string {
  const icons: Record<string, string> = {
    thinking: '🤔',
    tool_decision: '🔧',
    tool_execution: '🔍',
    tool_result: '✅',
    conclusion: '💡'
  };
  return icons[type] || '📝';
}

function getStepLabel(type: string): string {
  const labels: Record<string, string> = {
    thinking: 'Analyzing',
    tool_decision: 'Tool Selection',
    tool_execution: 'Executing',
    tool_result: 'Result',
    conclusion: 'Conclusion'
  };
  return labels[type] || 'Processing';
}

function formatStepContent(step: ReasoningStep): string {
  if (step.tool) {
    return `Using ${step.tool} tool${step.input ? ` with: ${step.input}` : ''}`;
  }
  return 'Processing...';
}