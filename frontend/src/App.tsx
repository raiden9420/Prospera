import { useState } from 'react';
import { MessageSquare, BarChart3, LogOut, PieChart } from 'lucide-react';
import { Auth } from './components/Auth';
import { Chat } from './components/Chat';
import { Dashboard } from './components/Dashboard';
import { VisualizationChat } from './components/VisualizationChat';
import { useChat } from './context/ChatContext';
import type { User } from './types';

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'chat' | 'visualization'>('dashboard');
  const { setChatQuery } = useChat();

  const handleLogin = (userData: User) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
    setActiveTab('dashboard');
  };

  const handleQuickAction = (query: string) => {
    setChatQuery(query);
    setActiveTab('chat');
  };

  if (!user) {
    return <Auth onLogin={handleLogin} />;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">Prospera</h1>
              <span className="ml-2 text-sm text-gray-500">AI Financial Assistant</span>
            </div>

            {/* Navigation */}
            <nav className="flex space-x-4">
              <button
                onClick={() => setActiveTab('dashboard')}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${activeTab === 'dashboard'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                  }`}
              >
                <BarChart3 className="h-4 w-4 mr-2" />
                Dashboard
              </button>
              <button
                onClick={() => setActiveTab('chat')}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${activeTab === 'chat'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                  }`}
              >
                <MessageSquare className="h-4 w-4 mr-2" />
                Chat
              </button>
              <button
                onClick={() => setActiveTab('visualization')}
                className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${activeTab === 'visualization'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                  }`}
              >
                <PieChart className="h-4 w-4 mr-2" />
                Visualization
              </button>
            </nav>

            {/* User Menu */}
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Session: {user.sessionId}
              </span>
              <button
                onClick={handleLogout}
                className="flex items-center text-gray-500 hover:text-gray-700"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto">
        {activeTab === 'dashboard' ? (
          <Dashboard onQuickAction={handleQuickAction} />
        ) : activeTab === 'chat' ? (
          <div className="h-[calc(100vh-4rem)]">
            <Chat />
          </div>
        ) : (
          <div className="h-[calc(100vh-4rem)]">
            <VisualizationChat />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
