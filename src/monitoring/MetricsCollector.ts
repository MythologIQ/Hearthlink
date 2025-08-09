export interface MetricValue {
  value: number;
  timestamp: number;
  labels?: Record<string, string>;
}

export interface CounterMetric {
  name: string;
  value: number;
  labels?: Record<string, string>;
}

export interface HistogramMetric {
  name: string;
  values: number[];
  buckets?: number[];
  labels?: Record<string, string>;
}

export interface GaugeMetric {
  name: string;
  value: number;
  labels?: Record<string, string>;
}

export class MetricsCollector {
  private namespace: string;
  private counters: Map<string, CounterMetric> = new Map();
  private histograms: Map<string, HistogramMetric> = new Map();
  private gauges: Map<string, GaugeMetric> = new Map();
  private startTime: number = Date.now();

  constructor(namespace: string) {
    this.namespace = namespace;
  }

  // Counter methods
  increment(name: string, labels?: Record<string, string>): void {
    this.incrementBy(name, 1, labels);
  }

  incrementBy(name: string, value: number, labels?: Record<string, string>): void {
    const key = this.getMetricKey(name, labels);
    const existing = this.counters.get(key);
    
    if (existing) {
      existing.value += value;
    } else {
      this.counters.set(key, {
        name,
        value,
        labels: labels || {}
      });
    }
  }

  getCounter(name: string, labels?: Record<string, string>): number {
    const key = this.getMetricKey(name, labels);
    return this.counters.get(key)?.value || 0;
  }

  // Histogram methods
  histogram(name: string, value: number, labels?: Record<string, string>): void {
    const key = this.getMetricKey(name, labels);
    const existing = this.histograms.get(key);
    
    if (existing) {
      existing.values.push(value);
    } else {
      this.histograms.set(key, {
        name,
        values: [value],
        labels: labels || {}
      });
    }
  }

  getHistogram(name: string, labels?: Record<string, string>): number[] {
    const key = this.getMetricKey(name, labels);
    return this.histograms.get(key)?.values || [];
  }

  getHistogramAverage(name: string, labels?: Record<string, string>): number {
    const values = this.getHistogram(name, labels);
    if (values.length === 0) return 0;
    return values.reduce((sum, val) => sum + val, 0) / values.length;
  }

  getHistogramSum(name: string, labels?: Record<string, string>): number {
    const values = this.getHistogram(name, labels);
    return values.reduce((sum, val) => sum + val, 0);
  }

  getHistogramMedian(name: string, labels?: Record<string, string>): number {
    const values = this.getHistogram(name, labels).sort((a, b) => a - b);
    if (values.length === 0) return 0;
    
    const middle = Math.floor(values.length / 2);
    if (values.length % 2 === 0) {
      return (values[middle - 1] + values[middle]) / 2;
    }
    return values[middle];
  }

  getHistogramPercentile(name: string, percentile: number, labels?: Record<string, string>): number {
    const values = this.getHistogram(name, labels).sort((a, b) => a - b);
    if (values.length === 0) return 0;
    
    const index = Math.ceil((percentile / 100) * values.length) - 1;
    return values[Math.max(0, Math.min(index, values.length - 1))];
  }

  // Gauge methods
  gauge(name: string, value: number, labels?: Record<string, string>): void {
    const key = this.getMetricKey(name, labels);
    this.gauges.set(key, {
      name,
      value,
      labels: labels || {}
    });
  }

  getGauge(name: string, labels?: Record<string, string>): number {
    const key = this.getMetricKey(name, labels);
    return this.gauges.get(key)?.value || 0;
  }

  // Utility methods
  private getMetricKey(name: string, labels?: Record<string, string>): string {
    const labelString = labels ? Object.entries(labels)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([k, v]) => `${k}=${v}`)
      .join(',') : '';
    
    return `${this.namespace}.${name}${labelString ? `{${labelString}}` : ''}`;
  }

  // Export methods
  exportPrometheusFormat(): string {
    const lines: string[] = [];
    
    // Export counters
    for (const [key, counter] of this.counters) {
      const labelString = this.formatPrometheusLabels(counter.labels);
      lines.push(`# TYPE ${this.namespace}_${counter.name} counter`);
      lines.push(`${this.namespace}_${counter.name}${labelString} ${counter.value}`);
    }
    
    // Export histograms
    for (const [key, histogram] of this.histograms) {
      const labelString = this.formatPrometheusLabels(histogram.labels);
      const values = histogram.values;
      
      if (values.length > 0) {
        lines.push(`# TYPE ${this.namespace}_${histogram.name} histogram`);
        lines.push(`${this.namespace}_${histogram.name}_count${labelString} ${values.length}`);
        lines.push(`${this.namespace}_${histogram.name}_sum${labelString} ${values.reduce((a, b) => a + b, 0)}`);
        
        // Add percentile buckets
        const percentiles = [50, 90, 95, 99];
        for (const percentile of percentiles) {
          const value = this.getHistogramPercentile(histogram.name, percentile, histogram.labels);
          lines.push(`${this.namespace}_${histogram.name}_p${percentile}${labelString} ${value}`);
        }
      }
    }
    
    // Export gauges
    for (const [key, gauge] of this.gauges) {
      const labelString = this.formatPrometheusLabels(gauge.labels);
      lines.push(`# TYPE ${this.namespace}_${gauge.name} gauge`);
      lines.push(`${this.namespace}_${gauge.name}${labelString} ${gauge.value}`);
    }
    
    return lines.join('\n');
  }

  private formatPrometheusLabels(labels?: Record<string, string>): string {
    if (!labels || Object.keys(labels).length === 0) return '';
    
    const labelPairs = Object.entries(labels)
      .map(([key, value]) => `${key}="${value}"`)
      .join(',');
    
    return `{${labelPairs}}`;
  }

  exportJSON(): any {
    const now = Date.now();
    const uptime = now - this.startTime;
    
    const counters: any = {};
    for (const [key, counter] of this.counters) {
      counters[key] = {
        value: counter.value,
        labels: counter.labels
      };
    }
    
    const histograms: any = {};
    for (const [key, histogram] of this.histograms) {
      const values = histogram.values;
      histograms[key] = {
        count: values.length,
        sum: values.reduce((a, b) => a + b, 0),
        average: values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0,
        median: this.getHistogramMedian(histogram.name, histogram.labels),
        p90: this.getHistogramPercentile(histogram.name, 90, histogram.labels),
        p95: this.getHistogramPercentile(histogram.name, 95, histogram.labels),
        p99: this.getHistogramPercentile(histogram.name, 99, histogram.labels),
        labels: histogram.labels
      };
    }
    
    const gauges: any = {};
    for (const [key, gauge] of this.gauges) {
      gauges[key] = {
        value: gauge.value,
        labels: gauge.labels
      };
    }
    
    return {
      namespace: this.namespace,
      timestamp: now,
      uptime,
      counters,
      histograms,
      gauges
    };
  }

  // Reset methods
  reset(): void {
    this.counters.clear();
    this.histograms.clear();
    this.gauges.clear();
    this.startTime = Date.now();
  }

  resetCounter(name: string, labels?: Record<string, string>): void {
    const key = this.getMetricKey(name, labels);
    this.counters.delete(key);
  }

  resetHistogram(name: string, labels?: Record<string, string>): void {
    const key = this.getMetricKey(name, labels);
    this.histograms.delete(key);
  }

  resetGauge(name: string, labels?: Record<string, string>): void {
    const key = this.getMetricKey(name, labels);
    this.gauges.delete(key);
  }

  // Health check
  getHealth(): any {
    const now = Date.now();
    const uptime = now - this.startTime;
    
    return {
      status: 'healthy',
      namespace: this.namespace,
      uptime,
      metrics: {
        counters: this.counters.size,
        histograms: this.histograms.size,
        gauges: this.gauges.size
      },
      timestamp: now
    };
  }

  // Time-series helpers
  recordTiming<T>(name: string, fn: () => T, labels?: Record<string, string>): T;
  recordTiming<T>(name: string, fn: () => Promise<T>, labels?: Record<string, string>): Promise<T>;
  recordTiming<T>(name: string, fn: () => T | Promise<T>, labels?: Record<string, string>): T | Promise<T> {
    const start = Date.now();
    
    try {
      const result = fn();
      
      if (result instanceof Promise) {
        return result.then(
          (value) => {
            this.histogram(name, Date.now() - start, labels);
            return value;
          },
          (error) => {
            this.histogram(name, Date.now() - start, { ...labels, error: 'true' });
            throw error;
          }
        );
      } else {
        this.histogram(name, Date.now() - start, labels);
        return result;
      }
    } catch (error) {
      this.histogram(name, Date.now() - start, { ...labels, error: 'true' });
      throw error;
    }
  }

  // Periodic metric collection
  startPeriodicCollection(intervalMs: number = 60000): NodeJS.Timer {
    return setInterval(() => {
      this.collectSystemMetrics();
    }, intervalMs);
  }

  private collectSystemMetrics(): void {
    // Collect basic system metrics
    const memoryUsage = process.memoryUsage();
    
    this.gauge('memory_heap_used', memoryUsage.heapUsed);
    this.gauge('memory_heap_total', memoryUsage.heapTotal);
    this.gauge('memory_rss', memoryUsage.rss);
    this.gauge('memory_external', memoryUsage.external);
    
    const cpuUsage = process.cpuUsage();
    this.gauge('cpu_user', cpuUsage.user);
    this.gauge('cpu_system', cpuUsage.system);
    
    this.gauge('uptime', process.uptime());
  }
}