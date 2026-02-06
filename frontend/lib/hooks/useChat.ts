import { useSession } from './useAuth';  // Better Auth session
import { useCallback } from 'react';
import { apiPostAgent } from "../api";

export function useChat() {
  const session = useSession();

  const sendMessage = useCallback(async (message: string, conversationId?: string) => {
    if (!session) throw new Error('No session');

    const response = await apiPostAgent(`/api/chat/${session.user.id}`, {
      message,
      conversation_id: conversationId,
    });

    if (!response.ok) throw new Error(response.error || 'Chat failed');
    return response.data;
  }, [session]);

  return { sendMessage };
}

// T304: Chat fetch wrapper with JWT (XII isolation)
