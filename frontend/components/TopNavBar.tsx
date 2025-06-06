'use client';

import { useState } from 'react';

interface TopNavBarProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
}

export default function TopNavBar({ activeSection, onSectionChange }: TopNavBarProps) {
  const sections = [
    { id: 'chatbot', label: 'Chat Assistant', icon: '💬' },
    { id: 'agents', label: 'AI Agents', icon: '🤖' },
    { id: 'knowledge', label: 'Knowledge Docs', icon: '📚' },
  ];

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">AF</span>
            </div>
            <h1 className="text-xl font-semibold text-gray-900">AgentFlo</h1>
          </div>
          
          <div className="flex space-x-1">
            {sections.map((section) => (
              <button
                key={section.id}
                onClick={() => onSectionChange(section.id)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  activeSection === section.id
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                <span>{section.icon}</span>
                <span>{section.label}</span>
              </button>
            ))}
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>Online</span>
          </div>
        </div>
      </div>
    </nav>
  );
}