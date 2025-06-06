'use client';

export default function AgentsView() {
  const agents = [
    {
      id: 'general-assistant',
      name: 'General AI Assistant',
      description: 'Versatile AI agent that can help with various tasks and queries',
      status: 'active',
      icon: '🤖',
      capabilities: ['Data Analysis', 'Research & Information', 'Task Automation', 'Document Processing']
    },
    {
      id: 'research-agent',
      name: 'Research Agent',
      description: 'Specialized in gathering, analyzing, and synthesizing information',
      status: 'coming-soon',
      icon: '🔍',
      capabilities: ['Web Research', 'Data Collection', 'Report Generation', 'Fact Checking']
    },
    {
      id: 'workflow-agent',
      name: 'Workflow Agent',
      description: 'Automates and optimizes business processes and workflows',
      status: 'coming-soon',
      icon: '⚡',
      capabilities: ['Process Automation', 'Task Scheduling', 'Integration Management', 'Optimization']
    },
    {
      id: 'analytics-agent',
      name: 'Analytics Agent',
      description: 'Advanced data analysis and insights generation',
      status: 'coming-soon',
      icon: '📈',
      capabilities: ['Data Visualization', 'Trend Analysis', 'Predictive Modeling', 'Performance Metrics']
    }
  ];

  return (
    <div className="p-6">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">AI Agents</h2>
        <p className="text-gray-600">Specialized AI agents designed to help with various tasks and workflows</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className={`bg-white rounded-lg border-2 p-6 transition-all duration-200 ${
              agent.status === 'active'
                ? 'border-blue-200 hover:border-blue-300 hover:shadow-lg cursor-pointer'
                : 'border-gray-200 opacity-75'
            }`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="text-3xl">{agent.icon}</div>
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                agent.status === 'active'
                  ? 'bg-green-100 text-green-700'
                  : 'bg-gray-100 text-gray-600'
              }`}>
                {agent.status === 'active' ? 'Active' : 'Coming Soon'}
              </div>
            </div>
            
            <h3 className="text-lg font-semibold text-gray-900 mb-2">{agent.name}</h3>
            <p className="text-gray-600 text-sm mb-4">{agent.description}</p>
            
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-700">Capabilities:</h4>
              <div className="flex flex-wrap gap-1">
                {agent.capabilities.map((capability, index) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md"
                  >
                    {capability}
                  </span>
                ))}
              </div>
            </div>
            
            {agent.status === 'active' && (
              <button className="w-full mt-4 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
                Launch Agent
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}