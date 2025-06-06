'use client';

import { useState } from 'react';
import TopNavBar from '../components/TopNavBar';
import ChatView from '../components/ChatView';
import AgentsView from '../components/AgentsView';

export default function Home() {
  const [activeSection, setActiveSection] = useState('chatbot');

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <TopNavBar 
        activeSection={activeSection} 
        onSectionChange={setActiveSection} 
      />
      
      <div className="flex-1 overflow-hidden">
        {activeSection === 'chatbot' && <ChatView />}
        {activeSection === 'agents' && <AgentsView />}
      </div>
    </div>
  );
}