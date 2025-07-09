

import React, { useState, useEffect } from 'react';
import { InsightDataPoint } from '../types';
import { Button } from './common/Button';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface InsightsPanelProps {
  initialMetrics: InsightDataPoint[];
  isLoading: boolean;
  onRefresh: () => void;
  onPopoutClick?: () => void;
  onClose?: () => void; 
}

export const InsightsPanel: React.FC<InsightsPanelProps> = ({ initialMetrics, isLoading, onRefresh, onPopoutClick, onClose }) => {
  const [chartData, setChartData] = useState<InsightDataPoint[]>(initialMetrics);

  useEffect(() => {
    setChartData(initialMetrics);
  }, [initialMetrics]);


  return (
    <div className="p-3 flex flex-col h-full">
      <div className="flex justify-between items-center mb-3 flex-shrink-0">
        <h4 className="text-sm font-semibold text-[var(--brand-text-secondary)] uppercase tracking-wider">System Performance</h4>
        <Button 
          size="sm" 
          variant="secondary" 
          onClick={onRefresh} 
          disabled={isLoading}
          className="!px-2 !py-1"
        >
          {isLoading ? 'Loading...' : 'Refresh Metrics'}
        </Button>
      </div>

      <div className="h-56 sm:h-64 mb-4 flex-grow">
        {isLoading && chartData.length === 0 ? ( 
             <div className="w-full h-full flex items-center justify-center text-[var(--brand-text-secondary)]">Loading metrics chart...</div>
        ) : chartData.length === 0 && !isLoading ? (
            <div className="w-full h-full flex items-center justify-center text-[var(--brand-text-secondary)]">No metrics data available.</div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 20, left: -25, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.2} stroke="var(--brand-border)" />
              <XAxis dataKey="name" tick={{ fill: 'var(--brand-text-secondary)', fontSize: 12 }} />
              <YAxis tick={{ fill: 'var(--brand-text-secondary)', fontSize: 12 }} />
              <Tooltip 
                  contentStyle={{ backgroundColor: 'var(--brand-primary-bg)', border: '1px solid var(--brand-border)', borderRadius: '0.25rem' }} 
                  labelStyle={{ color: 'var(--brand-text-primary)' }}
                  itemStyle={{ color: 'var(--brand-accent1)' }}
              />
              <Legend wrapperStyle={{fontSize: "12px", color: "var(--brand-text-secondary)"}}/>
              <Line type="monotone" dataKey="CPU Load (%)" stroke="var(--brand-accent1)" strokeWidth={2} activeDot={{ r: 6, fill: 'var(--brand-accent1)' }} dot={{fill: "var(--brand-accent1)", strokeWidth:0}} name="CPU Load" />
              <Line type="monotone" dataKey="Memory Usage (%)" stroke="var(--brand-accent2)" strokeWidth={2} activeDot={{ r: 6, fill: 'var(--brand-accent2)' }} dot={{fill: "var(--brand-accent2)", strokeWidth:0}} name="Memory Usage" />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
      <div className="grid grid-cols-2 gap-3 flex-shrink-0">
        <div className="p-3 bg-[var(--brand-primary-bg)] rounded-md shadow">
          <p className="text-xs text-[var(--brand-text-secondary)]">Active Tasks (Mock)</p>
          <p className="text-xl font-semibold text-[var(--brand-text-primary)]">12</p>
        </div>
        <div className="p-3 bg-[var(--brand-primary-bg)] rounded-md shadow">
          <p className="text-xs text-[var(--brand-text-secondary)]">Memory Usage (Mock)</p>
          <p className="text-xl font-semibold text-[var(--brand-text-primary)]">65%</p>
        </div>
      </div>
    </div>
  );
};
