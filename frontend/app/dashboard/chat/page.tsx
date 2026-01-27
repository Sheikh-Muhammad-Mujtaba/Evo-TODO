"use client"

import { useState, useRef, useEffect, useCallback } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useSession } from '@/lib/auth-client';
import { useTheme } from '@/lib/hooks/useTheme';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const { data: session } = useSession();
  const { theme } = useTheme();

  useEffect(() => {
    if (session) {
      const greeting = `Welcome back! You have ${session.user.stats?.pending ?? 0} open tasks across ${session.user.stats?.conversations ?? 0} conversations. How can I help?`;
      setMessages([{ role: 'assistant', content: greeting }]);
    }
  }, [session]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = useCallback(async () => {
    if (!input.trim() || isLoading || !session) return;

    const userMsg: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch(`/api/chat/${session.user.id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.token}`,
        },
        body: JSON.stringify({
          message: input,
          conversation_id: session.conversationId || undefined,
        }),
      });

      if (!res.ok) throw new Error('Chat API error');

      const { response, conversation_id } = await res.json();
      setMessages(prev => [...prev, { role: 'assistant', content: response }]);
      // Update session conversationId if new
    } catch (error) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, something went wrong. Try again.' }]);
    } finally {
      setIsLoading(false);
    }
  }, [input, isLoading, session]);

  return (
    <div className={`flex flex-col h-screen ${theme === 'dark' ? 'bg-gray-900' : 'bg-white'}`}>
      <div className="p-4 border-b flex-shrink-0">
        <h1 className="text-2xl font-bold text-foreground">AI Chat Assistant</h1>
      </div>
      <ScrollArea className="flex-1 p-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <p>Chat starts when you send a message...</p>
          </div>
        ) : (
          messages.map((msg, index) => (
            <div key={index} className={`mb-6 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-md p-4 rounded-2xl shadow-lg ${msg.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
                <p>{msg.content}</p>
              </div>
            </div>
          ))
        )}
        <div ref={scrollRef} />
      </ScrollArea>
      <div className="p-4 border-t flex gap-2 bg-background">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
          placeholder="Type your message... (e.g., 'add buy milk')"
          className="flex-1"
          disabled={isLoading}
        />
        <Button onClick={sendMessage} disabled={!input.trim() || isLoading}>
          {isLoading ? '...' : 'Send'}
        </Button>
      </div>
    </div>
  );
}

// T304: Responsive Shadcn Chat UI (XIII UI consistency, light/dark)
