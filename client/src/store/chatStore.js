import { useState, useCallback } from 'react';
import api from '../services/api';

export function useChat() {
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);

  const loadConversations = useCallback(async () => {
    try {
      setLoading(true);
      const res = await api.get('/chat/history');
      setConversations(res.data || []);
      return res.data;
    } catch (err) {
      console.error("Failed to load conversations:", err);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  const selectConversation = useCallback(async (conversationId) => {
    setCurrentConversationId(conversationId);
    if (!conversationId) {
      setMessages([]);
      return;
    }
    try {
      setLoading(true);
      const res = await api.get(`/chat/${conversationId}`);
      setMessages(res.data || []);
    } catch (err) {
      console.error("Failed to load messages:", err);
      setError("Failed to load message history.");
    } finally {
      setLoading(false);
    }
  }, []);

  const sendMessage = async (content, category = null, department = null) => {
    if (!content.trim() || sending) return;

    setSending(true);
    setError(null);

    // Optimistic user message
    const tempUserMsg = {
      id: `temp-${Date.now()}`,
      role: 'user',
      content: content.trim(),
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);

    try {
      const res = await api.post('/chat', {
        content: content.trim(),
        conversationId: currentConversationId,
        category,
        department
      });

      const { conversationId, userMessage, assistantMessage } = res.data;
      
      // Update current conversation ID if new
      if (!currentConversationId) {
        setCurrentConversationId(conversationId);
      }

      // Replace temp message with server message and append assistant message
      setMessages((prev) => {
        const filtered = prev.filter((m) => m.id !== tempUserMsg.id);
        return [...filtered, userMessage, assistantMessage];
      });

      // Refresh conversations list
      loadConversations();
      return res.data;
    } catch (err) {
      const msg = err.response?.data?.detail || "Failed to send query. Please try again.";
      setError(msg);
      // Remove optimistic message on hard failure
      setMessages((prev) => prev.filter((m) => m.id !== tempUserMsg.id));
    } finally {
      setSending(false);
    }
  };

  const deleteConversation = async (conversationId) => {
    try {
      await api.delete(`/chat/${conversationId}`);
      setConversations((prev) => prev.filter((c) => c.id !== conversationId));
      if (currentConversationId === conversationId) {
        setCurrentConversationId(null);
        setMessages([]);
      }
    } catch (err) {
      console.error("Failed to delete conversation:", err);
    }
  };

  const startNewChat = () => {
    setCurrentConversationId(null);
    setMessages([]);
    setError(null);
  };

  return {
    conversations,
    currentConversationId,
    messages,
    loading,
    sending,
    error,
    loadConversations,
    selectConversation,
    sendMessage,
    deleteConversation,
    startNewChat,
    setMessages
  };
}
