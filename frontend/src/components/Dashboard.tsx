import React, { useEffect, useState } from 'react';
import { TrendingUp, DollarSign, CreditCard, Target, Calendar, BarChart2 } from 'lucide-react';
import { apiService } from '../services/api';
import type { InsightsResponse, QuickInsight } from '../types';

interface DashboardProps {
  onQuickAction: (query: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onQuickAction }) => {
  console.log("Dashboard component rendered");
  const [insights, setInsights] = useState<InsightsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchInsights();
  }, []);

  const fetchInsights = async () => {
    try {
      setLoading(true);
      const data = await apiService.getQuickInsights();
      console.log("Fetched insights:", data);
      setInsights(data);
    } catch (err) {
      setError('Failed to load financial insights');
      console.error('Error fetching insights:', err);
    } finally {
      setLoading(false);
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'net_worth':
        return <DollarSign className="h-6 w-6" />;
      case 'monthly_spend':
        return <CreditCard className="h-6 w-6" />;
      case 'credit_score':
        return <TrendingUp className="h-6 w-6" />;
      case 'goal_progress':
        return <Target className="h-6 w-6" />;
      case 'next_payment':
        return <Calendar className="h-6 w-6" />;
      case 'top_category':
        return <BarChart2 className="h-6 w-6" />;
      default:
        return <DollarSign className="h-6 w-6" />;
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-600">{error}</p>
          <button 
            onClick={fetchInsights}
            className="mt-2 text-red-700 hover:text-red-900 underline"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-1">Financial Overview</h2>
        <p className="text-gray-600">Your latest financial insights</p>
      </div>

      {/* Insights Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {insights?.insights.map((insight: QuickInsight, index: number) => (
          <div key={index} className="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
            <div className="flex items-center space-x-3">
              <div className="text-blue-600">
                {getIcon(insight.type)}
              </div>
              <div className="flex-1">
                <h3 className="font-medium text-gray-900">{insight.title}</h3>
                <p className="text-lg font-semibold text-gray-900">{insight.value}</p>
                {insight.subtitle && (
                  <p className="text-sm text-gray-500">{insight.subtitle}</p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {insights?.quick_actions.map((action, index) => (
            <button
              key={index}
              onClick={() => onQuickAction(action.query)}
              className="bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg p-3 text-left transition-colors"
            >
              <span className="text-blue-700 font-medium">{action.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Refresh Button */}
      <div className="flex justify-end">
        <button
          onClick={fetchInsights}
          className="text-blue-600 hover:text-blue-700 text-sm font-medium"
        >
          Refresh Data
        </button>
      </div>
    </div>
  );
};