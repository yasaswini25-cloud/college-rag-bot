import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import ConversationSidebar from '../components/ConversationSidebar/ConversationSidebar';
import ChatWindow from '../components/ChatWindow/ChatWindow';
import ChatInput from '../components/ChatInput/ChatInput';
import { useChat } from '../store/chatStore';

export default function ChatPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialPrompt = searchParams.get('prompt') || '';
  const urlConvId = searchParams.get('id');

  const {
    conversations,
    currentConversationId,
    messages,
    sending,
    loadConversations,
    selectConversation,
    sendMessage,
    deleteConversation,
    startNewChat,
  } = useChat();

  useEffect(() => {
    loadConversations().then((convs) => {
      if (urlConvId) {
        selectConversation(urlConvId);
      } else if (initialPrompt) {
        // If initial prompt provided from landing/dashboard, prepare new chat
        startNewChat();
      } else if (convs && convs.length > 0 && !currentConversationId) {
        // Select most recent by default
        selectConversation(convs[0].id);
      }
    });
  }, [urlConvId]);

  const handleSelectConv = (id) => {
    setSearchParams({ id });
    selectConversation(id);
  };

  const handleNewChat = () => {
    setSearchParams({});
    startNewChat();
  };

  const handleSendMessage = async (text, category, department) => {
    const res = await sendMessage(text, category, department);
    if (res && res.conversationId && (!urlConvId || urlConvId !== res.conversationId)) {
      setSearchParams({ id: res.conversationId });
    }
  };

  const handlePromptClick = (prompt) => {
    handleSendMessage(prompt, null, null);
  };

  return (
    <div className="flex-1 flex h-[calc(100vh-4rem-3.5rem)] overflow-hidden bg-slate-950">
      {/* Sidebar for conversations */}
      <ConversationSidebar
        conversations={conversations}
        currentId={currentConversationId}
        onSelectConversation={handleSelectConv}
        onNewChat={handleNewChat}
        onDeleteConversation={deleteConversation}
        onRefresh={loadConversations}
      />

      {/* Main Chat Workspace */}
      <div className="flex-1 flex flex-col min-w-0 bg-slate-950/50">
        <ChatWindow
          messages={messages}
          sending={sending}
          onPromptClick={handlePromptClick}
        />
        <ChatInput
          onSendMessage={handleSendMessage}
          sending={sending}
          initialPrompt={initialPrompt}
        />
      </div>
    </div>
  );
}
