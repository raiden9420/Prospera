export interface QuickInsight {
  type: string;
  title: string;
  value: string;
  subtitle?: string;
  icon: string;
}

export interface QuickAction {
  label: string;
  query: string;
}

export interface InsightsResponse {
  insights: QuickInsight[];
  quick_actions: QuickAction[];
  timestamp: string;
}

export interface ChatMessage {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

export interface AIResponse {
  query: string;
  response: any;
  analysis: {
    intent: string;
    data_sources_used: string[];
    time_period?: string;
    specific_focus?: string;
  };
  performance: {
    apis_called: number;
    selective_fetching: boolean;
    response_optimized: boolean;
  };
  timestamp: string;
}

export interface User {
  sessionId: string;
  phoneNumber: string;
  isAuthenticated: boolean;
}