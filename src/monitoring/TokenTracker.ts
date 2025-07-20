export interface TokenUsage {
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
}

export interface TokenUsageRecord {
  timestamp: string;
  usage: TokenUsage;
  agentId?: string;
  module?: string;
  model?: string;
  cost?: number;
  requestId?: string;
}

export interface TokenStats {
  totalPromptTokens: number;
  totalCompletionTokens: number;
  totalTokens: number;
  totalRequests: number;
  averageTokensPerRequest: number;
  totalCost: number;
  timeWindow: {
    start: string;
    end: string;
  };
}

export class TokenTracker {
  private backend: string;
  private records: TokenUsageRecord[] = [];
  private maxRecords: number = 10000;
  private costPerInputToken: number = 0.00000057; // $0.57 per 1M tokens
  private costPerOutputToken: number = 0.0000023; // $2.30 per 1M tokens

  constructor(backend: string, options?: {
    maxRecords?: number;
    costPerInputToken?: number;
    costPerOutputToken?: number;
  }) {
    this.backend = backend;
    if (options) {
      this.maxRecords = options.maxRecords || this.maxRecords;
      this.costPerInputToken = options.costPerInputToken || this.costPerInputToken;
      this.costPerOutputToken = options.costPerOutputToken || this.costPerOutputToken;
    }
  }

  trackUsage(usage: TokenUsage, metadata?: {
    agentId?: string;
    module?: string;
    model?: string;
    requestId?: string;
  }): void {
    const cost = this.calculateCost(usage);
    
    const record: TokenUsageRecord = {
      timestamp: new Date().toISOString(),
      usage,
      cost,
      ...metadata
    };

    this.records.push(record);

    // Keep only the most recent records
    if (this.records.length > this.maxRecords) {
      this.records = this.records.slice(-this.maxRecords);
    }

    // Log usage for monitoring
    this.logUsage(record);
  }

  trackError(error: Error, metadata?: {
    agentId?: string;
    module?: string;
    requestId?: string;
  }): void {
    const errorRecord = {
      timestamp: new Date().toISOString(),
      error: error.message,
      errorType: error.constructor.name,
      backend: this.backend,
      ...metadata
    };

    console.error('Token tracker error:', errorRecord);
    
    // In production, this would send to your monitoring service
  }

  private calculateCost(usage: TokenUsage): number {
    const inputCost = usage.promptTokens * this.costPerInputToken;
    const outputCost = usage.completionTokens * this.costPerOutputToken;
    return inputCost + outputCost;
  }

  private logUsage(record: TokenUsageRecord): void {
    const logData = {
      backend: this.backend,
      timestamp: record.timestamp,
      promptTokens: record.usage.promptTokens,
      completionTokens: record.usage.completionTokens,
      totalTokens: record.usage.totalTokens,
      cost: record.cost,
      agentId: record.agentId,
      module: record.module,
      model: record.model,
      requestId: record.requestId
    };

    console.log('Token usage:', logData);
  }

  getStats(timeWindow?: { start: Date; end: Date }): TokenStats {
    let filteredRecords = this.records;

    if (timeWindow) {
      filteredRecords = this.records.filter(record => {
        const recordTime = new Date(record.timestamp);
        return recordTime >= timeWindow.start && recordTime <= timeWindow.end;
      });
    }

    const totalPromptTokens = filteredRecords.reduce((sum, record) => sum + record.usage.promptTokens, 0);
    const totalCompletionTokens = filteredRecords.reduce((sum, record) => sum + record.usage.completionTokens, 0);
    const totalTokens = totalPromptTokens + totalCompletionTokens;
    const totalRequests = filteredRecords.length;
    const averageTokensPerRequest = totalRequests > 0 ? totalTokens / totalRequests : 0;
    const totalCost = filteredRecords.reduce((sum, record) => sum + (record.cost || 0), 0);

    return {
      totalPromptTokens,
      totalCompletionTokens,
      totalTokens,
      totalRequests,
      averageTokensPerRequest,
      totalCost,
      timeWindow: {
        start: timeWindow?.start.toISOString() || 'N/A',
        end: timeWindow?.end.toISOString() || 'N/A'
      }
    };
  }

  getStatsByAgent(agentId: string, timeWindow?: { start: Date; end: Date }): TokenStats {
    let filteredRecords = this.records.filter(record => record.agentId === agentId);

    if (timeWindow) {
      filteredRecords = filteredRecords.filter(record => {
        const recordTime = new Date(record.timestamp);
        return recordTime >= timeWindow.start && recordTime <= timeWindow.end;
      });
    }

    const totalPromptTokens = filteredRecords.reduce((sum, record) => sum + record.usage.promptTokens, 0);
    const totalCompletionTokens = filteredRecords.reduce((sum, record) => sum + record.usage.completionTokens, 0);
    const totalTokens = totalPromptTokens + totalCompletionTokens;
    const totalRequests = filteredRecords.length;
    const averageTokensPerRequest = totalRequests > 0 ? totalTokens / totalRequests : 0;
    const totalCost = filteredRecords.reduce((sum, record) => sum + (record.cost || 0), 0);

    return {
      totalPromptTokens,
      totalCompletionTokens,
      totalTokens,
      totalRequests,
      averageTokensPerRequest,
      totalCost,
      timeWindow: {
        start: timeWindow?.start.toISOString() || 'N/A',
        end: timeWindow?.end.toISOString() || 'N/A'
      }
    };
  }

  getStatsByModule(module: string, timeWindow?: { start: Date; end: Date }): TokenStats {
    let filteredRecords = this.records.filter(record => record.module === module);

    if (timeWindow) {
      filteredRecords = filteredRecords.filter(record => {
        const recordTime = new Date(record.timestamp);
        return recordTime >= timeWindow.start && recordTime <= timeWindow.end;
      });
    }

    const totalPromptTokens = filteredRecords.reduce((sum, record) => sum + record.usage.promptTokens, 0);
    const totalCompletionTokens = filteredRecords.reduce((sum, record) => sum + record.usage.completionTokens, 0);
    const totalTokens = totalPromptTokens + totalCompletionTokens;
    const totalRequests = filteredRecords.length;
    const averageTokensPerRequest = totalRequests > 0 ? totalTokens / totalRequests : 0;
    const totalCost = filteredRecords.reduce((sum, record) => sum + (record.cost || 0), 0);

    return {
      totalPromptTokens,
      totalCompletionTokens,
      totalTokens,
      totalRequests,
      averageTokensPerRequest,
      totalCost,
      timeWindow: {
        start: timeWindow?.start.toISOString() || 'N/A',
        end: timeWindow?.end.toISOString() || 'N/A'
      }
    };
  }

  getTopAgents(limit: number = 10, timeWindow?: { start: Date; end: Date }): Array<{
    agentId: string;
    stats: TokenStats;
  }> {
    let filteredRecords = this.records;

    if (timeWindow) {
      filteredRecords = this.records.filter(record => {
        const recordTime = new Date(record.timestamp);
        return recordTime >= timeWindow.start && recordTime <= timeWindow.end;
      });
    }

    const agentStats = new Map<string, TokenUsageRecord[]>();
    
    filteredRecords.forEach(record => {
      if (record.agentId) {
        if (!agentStats.has(record.agentId)) {
          agentStats.set(record.agentId, []);
        }
        agentStats.get(record.agentId)!.push(record);
      }
    });

    const results = Array.from(agentStats.entries())
      .map(([agentId, records]) => ({
        agentId,
        stats: this.calculateStatsFromRecords(records, timeWindow)
      }))
      .sort((a, b) => b.stats.totalTokens - a.stats.totalTokens)
      .slice(0, limit);

    return results;
  }

  private calculateStatsFromRecords(records: TokenUsageRecord[], timeWindow?: { start: Date; end: Date }): TokenStats {
    const totalPromptTokens = records.reduce((sum, record) => sum + record.usage.promptTokens, 0);
    const totalCompletionTokens = records.reduce((sum, record) => sum + record.usage.completionTokens, 0);
    const totalTokens = totalPromptTokens + totalCompletionTokens;
    const totalRequests = records.length;
    const averageTokensPerRequest = totalRequests > 0 ? totalTokens / totalRequests : 0;
    const totalCost = records.reduce((sum, record) => sum + (record.cost || 0), 0);

    return {
      totalPromptTokens,
      totalCompletionTokens,
      totalTokens,
      totalRequests,
      averageTokensPerRequest,
      totalCost,
      timeWindow: {
        start: timeWindow?.start.toISOString() || 'N/A',
        end: timeWindow?.end.toISOString() || 'N/A'
      }
    };
  }

  exportData(format: 'json' | 'csv' = 'json', timeWindow?: { start: Date; end: Date }): string {
    let filteredRecords = this.records;

    if (timeWindow) {
      filteredRecords = this.records.filter(record => {
        const recordTime = new Date(record.timestamp);
        return recordTime >= timeWindow.start && recordTime <= timeWindow.end;
      });
    }

    if (format === 'json') {
      return JSON.stringify(filteredRecords, null, 2);
    } else {
      // CSV format
      const headers = ['timestamp', 'agentId', 'module', 'model', 'promptTokens', 'completionTokens', 'totalTokens', 'cost', 'requestId'];
      const csvRows = [
        headers.join(','),
        ...filteredRecords.map(record => [
          record.timestamp,
          record.agentId || '',
          record.module || '',
          record.model || '',
          record.usage.promptTokens,
          record.usage.completionTokens,
          record.usage.totalTokens,
          record.cost || 0,
          record.requestId || ''
        ].join(','))
      ];
      return csvRows.join('\n');
    }
  }

  clearData(): void {
    this.records = [];
  }

  getRecordCount(): number {
    return this.records.length;
  }

  getLatestRecord(): TokenUsageRecord | null {
    return this.records.length > 0 ? this.records[this.records.length - 1] : null;
  }
}