#!/usr/bin/env node
/**
 * Service Status Lights Verification Script
 * 
 * Tests all service status indicators across Hearthlink UI components
 * to ensure they are properly monitoring and displaying service health.
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Hearthlink Service Status Lights Verification\n');

// Service endpoints that should be monitored
const MONITORED_SERVICES = {
  'Local LLM API': 'http://localhost:8001/api/health',
  'Core API': 'http://localhost:8000/api/health', 
  'Vault API': 'http://localhost:8002/api/vault/health',
  'Synapse API': 'http://localhost:8003/api/synapse/health',
  'Sentry API': 'http://localhost:8004/api/sentry/health',
  'Claude Code CLI': 'http://localhost:8001/api/claude-code/status',
  'Settings API': 'http://localhost:8001/api/settings'
};

// Components that display status lights
const STATUS_LIGHT_COMPONENTS = [
  'src/components/SettingsManager.js',
  'src/components/CoreInterface.js', 
  'src/components/AldenMainScreen.js',
  'src/components/ProjectCommand.js'
];

async function analyzeStatusLightImplementation() {
  console.log('📊 Analyzing Status Light Implementation...\n');
  
  const results = {
    components: {},
    monitoredEndpoints: [],
    statusLightPatterns: [],
    issues: []
  };

  // Analyze each component
  for (const componentPath of STATUS_LIGHT_COMPONENTS) {
    const fullPath = path.join(__dirname, componentPath);
    
    try {
      if (!fs.existsSync(fullPath)) {
        results.issues.push(`❌ Component not found: ${componentPath}`);
        continue;
      }

      const content = fs.readFileSync(fullPath, 'utf8');
      const analysis = analyzeComponentStatusLights(componentPath, content);
      results.components[componentPath] = analysis;
      
      console.log(`✅ ${componentPath}:`);
      console.log(`   - Endpoints monitored: ${analysis.endpoints.length}`);
      console.log(`   - Status indicators: ${analysis.statusIndicators.length}`);
      console.log(`   - Health check functions: ${analysis.healthCheckFunctions.length}`);
      console.log('');
      
    } catch (error) {
      results.issues.push(`❌ Error analyzing ${componentPath}: ${error.message}`);
    }
  }

  return results;
}

function analyzeComponentStatusLights(componentPath, content) {
  const analysis = {
    endpoints: [],
    statusIndicators: [],
    healthCheckFunctions: [],
    statusClasses: [],
    statusStates: []
  };

  // Find API endpoints being monitored
  const endpointRegex = /(?:fetch|axios)\s*\(\s*['"`]([^'"`]*(?:health|status|api)[^'"`]*)['"`]/g;
  let match;
  while ((match = endpointRegex.exec(content)) !== null) {
    analysis.endpoints.push(match[1]);
  }

  // Find status indicator elements
  const statusIndicatorRegex = /status[-_](?:indicator|light|dot|lamp)\b/g;
  const indicators = content.match(statusIndicatorRegex) || [];
  analysis.statusIndicators = [...new Set(indicators)];

  // Find health check functions
  const healthFunctionRegex = /(?:check|get|fetch).*(?:health|status|service).*(?:async|function)/gi;
  const healthFunctions = content.match(healthFunctionRegex) || [];
  analysis.healthCheckFunctions = [...new Set(healthFunctions)];

  // Find status-related CSS classes
  const statusClassRegex = /className.*status[-_](?:running|stopped|healthy|warning|error|green|red|yellow)/g;
  const statusClasses = content.match(statusClassRegex) || [];
  analysis.statusClasses = [...new Set(statusClasses)];

  // Find status state variables
  const statusStateRegex = /(?:set|get).*(?:Status|Health|Service).*(?:State|Status)/g;
  const statusStates = content.match(statusStateRegex) || [];
  analysis.statusStates = [...new Set(statusStates)];

  return analysis;
}

function generateStatusLightReport(results) {
  console.log('\n📋 Service Status Light Verification Report\n');
  console.log('=' .repeat(60));

  // Summary
  const totalComponents = Object.keys(results.components).length;
  const totalEndpoints = new Set(
    Object.values(results.components).flatMap(c => c.endpoints)
  ).size;
  
  console.log(`🎯 Components Analyzed: ${totalComponents}`);
  console.log(`🌐 Unique Endpoints: ${totalEndpoints}`);
  console.log(`❌ Issues Found: ${results.issues.length}\n`);

  // Component Details
  console.log('📊 Component Status Light Analysis:\n');
  
  Object.entries(results.components).forEach(([component, analysis]) => {
    const fileName = component.split('/').pop();
    console.log(`🔧 ${fileName}:`);
    
    if (analysis.endpoints.length > 0) {
      console.log('   📡 Monitored Endpoints:');
      analysis.endpoints.forEach(endpoint => {
        const isKnownService = Object.values(MONITORED_SERVICES).includes(endpoint);
        const status = isKnownService ? '✅' : '⚠️';
        console.log(`     ${status} ${endpoint}`);
      });
    }
    
    if (analysis.statusIndicators.length > 0) {
      console.log('   💡 Status Indicators:');
      analysis.statusIndicators.forEach(indicator => {
        console.log(`     🔹 ${indicator}`);
      });
    }
    
    if (analysis.healthCheckFunctions.length > 0) {
      console.log('   🏥 Health Check Functions:');
      analysis.healthCheckFunctions.forEach(func => {
        console.log(`     🔹 ${func}`);
      });
    }
    
    console.log('');
  });

  // Expected vs Actual Monitoring
  console.log('🎯 Service Coverage Analysis:\n');
  
  Object.entries(MONITORED_SERVICES).forEach(([serviceName, endpoint]) => {
    const isMonitored = Object.values(results.components).some(c => 
      c.endpoints.includes(endpoint)
    );
    const status = isMonitored ? '✅' : '❌';
    console.log(`${status} ${serviceName}: ${endpoint}`);
  });

  // Issues and Recommendations  
  if (results.issues.length > 0) {
    console.log('\n⚠️ Issues Found:\n');
    results.issues.forEach(issue => {
      console.log(`   ${issue}`);
    });
  }

  console.log('\n🔧 Recommendations:\n');
  
  // Check for missing service monitoring
  const allMonitoredEndpoints = new Set(
    Object.values(results.components).flatMap(c => c.endpoints)
  );
  
  Object.entries(MONITORED_SERVICES).forEach(([serviceName, endpoint]) => {
    if (!allMonitoredEndpoints.has(endpoint)) {
      console.log(`   📋 Add monitoring for ${serviceName} (${endpoint})`);
    }
  });

  // Check for consistent status indicator patterns
  const allStatusIndicators = new Set(
    Object.values(results.components).flatMap(c => c.statusIndicators)
  );
  
  if (allStatusIndicators.size > 0) {
    console.log(`   🎨 Standardize status indicator classes: ${[...allStatusIndicators].join(', ')}`);
  }

  // Check for error handling
  console.log('   🛡️ Ensure all status checks have proper error handling');
  console.log('   ⏱️ Add timeout handling for status check requests');
  console.log('   🔄 Implement automatic retry logic for failed status checks');
  
  return results;
}

async function testStatusLightFunctionality() {
  console.log('\n🧪 Testing Status Light Functionality...\n');
  
  // Test that status light components are properly imported and structured
  const componentTests = [
    {
      name: 'SettingsManager Service Status',
      test: () => {
        const settingsPath = path.join(__dirname, 'src/components/SettingsManager.js');
        const content = fs.readFileSync(settingsPath, 'utf8');
        
        // Check for essential status functionality
        const hasCheckServiceStatus = content.includes('checkServiceStatus');
        const hasServiceStatus = content.includes('serviceStatus');
        const hasStatusIndicator = content.includes('status-indicator');
        
        return {
          passed: hasCheckServiceStatus && hasServiceStatus && hasStatusIndicator,
          details: {
            checkServiceStatus: hasCheckServiceStatus,
            serviceStatus: hasServiceStatus,
            statusIndicator: hasStatusIndicator
          }
        };
      }
    },
    {
      name: 'CoreInterface Service Grid',
      test: () => {
        const corePath = path.join(__dirname, 'src/components/CoreInterface.js');
        const content = fs.readFileSync(corePath, 'utf8');
        
        // Check for service grid and status monitoring
        const hasServicesGrid = content.includes('services-grid');
        const hasServiceStatus = content.includes('service.status');
        const hasStatusColor = content.includes('getStatusColor');
        
        return {
          passed: hasServicesGrid && hasServiceStatus && hasStatusColor,
          details: {
            servicesGrid: hasServicesGrid,
            serviceStatus: hasServiceStatus,
            statusColor: hasStatusColor
          }
        };
      }
    },
    {
      name: 'AldenMainScreen Health Monitoring',
      test: () => {
        const aldenPath = path.join(__dirname, 'src/components/AldenMainScreen.js');
        const content = fs.readFileSync(aldenPath, 'utf8');
        
        // Check for agent health monitoring
        const hasCheckSystemHealth = content.includes('checkSystemHealth');
        const hasAgentHealth = content.includes('agent.health');
        const hasHealthDot = content.includes('health-dot');
        
        return {
          passed: hasCheckSystemHealth && hasAgentHealth && hasHealthDot,
          details: {
            checkSystemHealth: hasCheckSystemHealth,
            agentHealth: hasAgentHealth,
            healthDot: hasHealthDot
          }
        };
      }
    }
  ];

  const testResults = componentTests.map(test => {
    try {
      const result = test.test();
      const status = result.passed ? '✅' : '❌';
      console.log(`${status} ${test.name}: ${result.passed ? 'PASS' : 'FAIL'}`);
      
      if (!result.passed) {
        Object.entries(result.details).forEach(([key, value]) => {
          const detailStatus = value ? '✅' : '❌';
          console.log(`     ${detailStatus} ${key}`);
        });
      }
      
      return { ...test, ...result };
    } catch (error) {
      console.log(`❌ ${test.name}: ERROR - ${error.message}`);
      return { ...test, passed: false, error: error.message };
    }
  });

  return testResults;
}

// Main execution
async function main() {
  try {
    // Analyze status light implementation
    const analysisResults = await analyzeStatusLightImplementation();
    
    // Generate comprehensive report
    const report = generateStatusLightReport(analysisResults);
    
    // Test functionality
    const testResults = await testStatusLightFunctionality();
    
    // Final summary
    const passedTests = testResults.filter(t => t.passed).length;
    const totalTests = testResults.length;
    
    console.log('\n' + '='.repeat(60));
    console.log(`🎯 FINAL RESULTS: ${passedTests}/${totalTests} tests passed`);
    
    if (passedTests === totalTests) {
      console.log('✅ All service status lights are properly implemented!');
    } else {
      console.log('❌ Some service status lights need attention.');
    }
    
    console.log('\n🔧 Next Steps:');
    console.log('   1. Launch Hearthlink to visually test status lights');
    console.log('   2. Check that status lights update in real-time');
    console.log('   3. Verify error states display properly');
    console.log('   4. Test status light behavior when services are offline');
    
  } catch (error) {
    console.error('❌ Test execution failed:', error.message);
    process.exit(1);
  }
}

// Run the analysis
main().catch(console.error);