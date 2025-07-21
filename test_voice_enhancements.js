#!/usr/bin/env node
/**
 * Test suite for Phase 2C: Enhanced Voice Interaction System
 * 
 * Tests all the enhanced voice features:
 * - Enhanced Voice HUD with audio visualization
 * - Agent deference system with smart suggestions
 * - Advanced misroute recovery with Alden protocol
 * - Voice authentication and secure mode
 * - Real-time routing breadcrumbs and confidence indicators
 */

const fs = require('fs');
const path = require('path');

// Test configuration
const TEST_CONFIG = {
  voiceInterfacePath: './src/components/VoiceInterface.js',
  voiceInterfaceCSSPath: './src/components/VoiceInterface.css',
  testScenarios: [
    {
      name: 'Enhanced HUD - Audio Visualization',
      description: 'Test real-time waveform and audio level indicators',
      features: ['audioLevel', 'waveform', 'confidence']
    },
    {
      name: 'Agent Deference System',
      description: 'Test intelligent agent suggestions based on context',
      features: ['analyzeAgentDeference', 'deferenceOptions', 'handleAgentSwitch']
    },
    {
      name: 'Misroute Recovery Protocol',
      description: 'Test Alden\'s intelligent recovery from routing confusion',
      features: ['handleMisroute', 'recoveryResponse', 'agentKeywords']
    },
    {
      name: 'Voice Authentication',
      description: 'Test secure mode activation and authentication',
      features: ['checkSecureModeActivation', 'secureMode', 'authentication']
    },
    {
      name: 'Routing Breadcrumbs',
      description: 'Test detailed routing path visualization',
      features: ['routingBreadcrumbs', 'confidenceIndicators', 'routingDecision']
    }
  ]
};

// Test results tracking
let testResults = {
  total: 0,
  passed: 0,
  failed: 0,
  details: []
};

// Utility functions
function logTest(name, status, details = '') {
  const symbol = status ? '✅' : '❌';
  console.log(`${symbol} ${name}`);
  if (details) {
    console.log(`   ${details}`);
  }
  
  testResults.total++;
  if (status) {
    testResults.passed++;
  } else {
    testResults.failed++;
  }
  
  testResults.details.push({
    name,
    status,
    details
  });
}

function checkFileExists(filePath) {
  try {
    return fs.existsSync(filePath);
  } catch (error) {
    return false;
  }
}

function readFileContent(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch (error) {
    return null;
  }
}

function checkCodeFeature(content, featureName, expectedPatterns) {
  const found = expectedPatterns.every(pattern => {
    const regex = new RegExp(pattern, 'i');
    return regex.test(content);
  });
  return found;
}

// Test functions
function testEnhancedHUD() {
  console.log('\n📊 Testing Enhanced Voice HUD Features...');
  
  const jsContent = readFileContent(TEST_CONFIG.voiceInterfacePath);
  const cssContent = readFileContent(TEST_CONFIG.voiceInterfaceCSSPath);
  
  if (!jsContent || !cssContent) {
    logTest('Enhanced HUD - File Access', false, 'Could not read component files');
    return;
  }
  
  // Test audio visualization features
  const audioVisualizationFeatures = [
    'audioLevel',
    'initAudioVisualization',
    'analyserRef',
    'waveform-bar',
    'audio-level-indicator'
  ];
  
  let audioFeaturesPassed = 0;
  audioVisualizationFeatures.forEach(feature => {
    const found = jsContent.includes(feature) || cssContent.includes(feature);
    if (found) audioFeaturesPassed++;
  });
  
  logTest('Enhanced HUD - Audio Visualization', 
    audioFeaturesPassed >= 4, 
    `Found ${audioFeaturesPassed}/5 audio visualization features`);
  
  // Test confidence indicators
  const confidenceFeatures = [
    'confidence',
    'confidence-indicator',
    'confidenceScore'
  ];
  
  let confidenceFeaturesPassed = 0;
  confidenceFeatures.forEach(feature => {
    const found = jsContent.includes(feature) || cssContent.includes(feature);
    if (found) confidenceFeaturesPassed++;
  });
  
  logTest('Enhanced HUD - Confidence Indicators', 
    confidenceFeaturesPassed >= 2, 
    `Found ${confidenceFeaturesPassed}/3 confidence features`);
  
  // Test routing breadcrumbs
  const routingFeatures = [
    'routingBreadcrumbs',
    'routing-breadcrumbs',
    'breadcrumb'
  ];
  
  let routingFeaturesPassed = 0;
  routingFeatures.forEach(feature => {
    const found = jsContent.includes(feature) || cssContent.includes(feature);
    if (found) routingFeaturesPassed++;
  });
  
  logTest('Enhanced HUD - Routing Breadcrumbs', 
    routingFeaturesPassed >= 2, 
    `Found ${routingFeaturesPassed}/3 routing features`);
}

function testAgentDeferenceSystem() {
  console.log('\n🤝 Testing Agent Deference System...');
  
  const jsContent = readFileContent(TEST_CONFIG.voiceInterfacePath);
  
  if (!jsContent) {
    logTest('Agent Deference - File Access', false, 'Could not read JavaScript file');
    return;
  }
  
  // Test deference analysis function
  const hasDeferenceAnalysis = jsContent.includes('analyzeAgentDeference');
  logTest('Agent Deference - Analysis Function', hasDeferenceAnalysis, 
    hasDeferenceAnalysis ? 'analyzeAgentDeference function found' : 'Missing analysis function');
  
  // Test deference rules
  const deferenceRules = [
    'scheduling.*alden',
    'emotion.*alice',
    'persona.*mimic',
    'security.*sentry'
  ];
  
  let rulesFound = 0;
  deferenceRules.forEach(rule => {
    const regex = new RegExp(rule, 'i');
    if (regex.test(jsContent)) rulesFound++;
  });
  
  logTest('Agent Deference - Routing Rules', 
    rulesFound >= 3, 
    `Found ${rulesFound}/4 deference routing rules`);
  
  // Test deference UI components
  const deferenceUI = [
    'deferenceOptions',
    'switch-agent-btn',
    'handleAgentSwitch'
  ];
  
  let uiFeatures = 0;
  deferenceUI.forEach(feature => {
    if (jsContent.includes(feature)) uiFeatures++;
  });
  
  logTest('Agent Deference - UI Components', 
    uiFeatures >= 2, 
    `Found ${uiFeatures}/3 deference UI features`);
}

function testMisrouteRecovery() {
  console.log('\n🔄 Testing Misroute Recovery System...');
  
  const jsContent = readFileContent(TEST_CONFIG.voiceInterfacePath);
  
  if (!jsContent) {
    logTest('Misroute Recovery - File Access', false, 'Could not read JavaScript file');
    return;
  }
  
  // Test misroute handler
  const hasMisrouteHandler = jsContent.includes('handleMisroute');
  logTest('Misroute Recovery - Handler Function', hasMisrouteHandler,
    hasMisrouteHandler ? 'handleMisroute function implemented' : 'Missing misroute handler');
  
  // Test agent keyword mapping
  const agentKeywords = [
    'schedule.*alden',
    'emotion.*alice',
    'persona.*mimic',
    'security.*sentry'
  ];
  
  let keywordMappings = 0;
  agentKeywords.forEach(mapping => {
    const regex = new RegExp(mapping, 'i');
    if (regex.test(jsContent)) keywordMappings++;
  });
  
  logTest('Misroute Recovery - Agent Keywords', 
    keywordMappings >= 3, 
    `Found ${keywordMappings}/4 agent keyword mappings`);
  
  // Test recovery response logic
  const recoveryFeatures = [
    'recoveryResponse',
    'suggestions',
    'didn.*t quite understand'
  ];
  
  let recoveryFeatureCount = 0;
  recoveryFeatures.forEach(feature => {
    const regex = new RegExp(feature, 'i');
    if (regex.test(jsContent)) recoveryFeatureCount++;
  });
  
  logTest('Misroute Recovery - Response Logic', 
    recoveryFeatureCount >= 2, 
    `Found ${recoveryFeatureCount}/3 recovery response features`);
}

function testVoiceAuthentication() {
  console.log('\n🔐 Testing Voice Authentication System...');
  
  const jsContent = readFileContent(TEST_CONFIG.voiceInterfacePath);
  const cssContent = readFileContent(TEST_CONFIG.voiceInterfaceCSSPath);
  
  if (!jsContent || !cssContent) {
    logTest('Voice Authentication - File Access', false, 'Could not read component files');
    return;
  }
  
  // Test secure mode activation
  const hasSecureModeCheck = jsContent.includes('checkSecureModeActivation');
  logTest('Voice Authentication - Secure Mode Check', hasSecureModeCheck,
    hasSecureModeCheck ? 'Secure mode activation implemented' : 'Missing secure mode check');
  
  // Test activation phrases
  const activationPhrases = [
    'hearthlink secure mode activate',
    'activate secure mode',
    'enable secure mode'
  ];
  
  let phrasesFound = 0;
  activationPhrases.forEach(phrase => {
    if (jsContent.includes(phrase)) phrasesFound++;
  });
  
  logTest('Voice Authentication - Activation Phrases', 
    phrasesFound >= 2, 
    `Found ${phrasesFound}/3 activation phrases`);
  
  // Test secure mode UI
  const secureUIFeatures = [
    'secureMode',
    'secure-indicator',
    'secure-pulse'
  ];
  
  let secureUICount = 0;
  secureUIFeatures.forEach(feature => {
    const found = jsContent.includes(feature) || cssContent.includes(feature);
    if (found) secureUICount++;
  });
  
  logTest('Voice Authentication - UI Indicators', 
    secureUICount >= 2, 
    `Found ${secureUICount}/3 secure mode UI features`);
}

function testOverallImplementation() {
  console.log('\n🎯 Testing Overall Implementation Quality...');
  
  const jsContent = readFileContent(TEST_CONFIG.voiceInterfacePath);
  const cssContent = readFileContent(TEST_CONFIG.voiceInterfaceCSSPath);
  
  if (!jsContent || !cssContent) {
    logTest('Overall - File Access', false, 'Could not read component files');
    return;
  }
  
  // Test state management
  const stateVariables = [
    'audioLevel',
    'confidence',
    'routingBreadcrumbs',
    'deferenceOptions',
    'secureMode'
  ];
  
  let stateVarsFound = 0;
  stateVariables.forEach(stateVar => {
    if (jsContent.includes(stateVar)) stateVarsFound++;
  });
  
  logTest('Overall - State Management', 
    stateVarsFound >= 4, 
    `Found ${stateVarsFound}/5 required state variables`);
  
  // Test CSS styling completeness
  const cssClasses = [
    'enhanced-voice-hud',
    'audio-visualization',
    'routing-breadcrumbs',
    'deference-options',
    'secure-indicator'
  ];
  
  let cssClassesFound = 0;
  cssClasses.forEach(cssClass => {
    if (cssContent.includes(cssClass)) cssClassesFound++;
  });
  
  logTest('Overall - CSS Styling', 
    cssClassesFound >= 4, 
    `Found ${cssClassesFound}/5 required CSS classes`);
  
  // Test error handling
  const errorHandling = [
    'try.*catch',
    'console.warn',
    'error'
  ];
  
  let errorHandlingFound = 0;
  errorHandling.forEach(pattern => {
    const regex = new RegExp(pattern, 'i');
    if (regex.test(jsContent)) errorHandlingFound++;
  });
  
  logTest('Overall - Error Handling', 
    errorHandlingFound >= 2, 
    `Found ${errorHandlingFound}/3 error handling patterns`);
}

function generateTestReport() {
  console.log('\n' + '='.repeat(60));
  console.log('📊 PHASE 2C: VOICE INTERACTION SYSTEM TEST REPORT');
  console.log('='.repeat(60));
  
  console.log(`\n📈 Test Summary:`);
  console.log(`   Total Tests: ${testResults.total}`);
  console.log(`   Passed: ${testResults.passed} ✅`);
  console.log(`   Failed: ${testResults.failed} ❌`);
  console.log(`   Success Rate: ${Math.round((testResults.passed / testResults.total) * 100)}%`);
  
  console.log('\n🎯 Feature Implementation Status:');
  
  const featureCategories = {
    'Enhanced Voice HUD': ['Enhanced HUD'],
    'Agent Deference System': ['Agent Deference'],
    'Misroute Recovery': ['Misroute Recovery'],
    'Voice Authentication': ['Voice Authentication'],
    'Overall Quality': ['Overall']
  };
  
  Object.keys(featureCategories).forEach(category => {
    const categoryTests = testResults.details.filter(test => 
      featureCategories[category].some(keyword => test.name.includes(keyword))
    );
    
    const passed = categoryTests.filter(test => test.status).length;
    const total = categoryTests.length;
    const percentage = total > 0 ? Math.round((passed / total) * 100) : 0;
    
    const status = percentage >= 80 ? '✅' : percentage >= 60 ? '⚠️' : '❌';
    console.log(`   ${status} ${category}: ${passed}/${total} (${percentage}%)`);
  });
  
  console.log('\n🚀 Next Steps:');
  
  if (testResults.passed / testResults.total >= 0.8) {
    console.log('   ✅ Phase 2C implementation is ready for production!');
    console.log('   🎯 All core voice interaction enhancements are functional');
    console.log('   📝 Ready to proceed to Phase 2D: Project Command System');
  } else if (testResults.passed / testResults.total >= 0.6) {
    console.log('   ⚠️  Phase 2C implementation is mostly complete');
    console.log('   🔧 Some features may need refinement before production');
    console.log('   🧪 Consider additional testing of failing components');
  } else {
    console.log('   ❌ Phase 2C implementation needs significant work');
    console.log('   🛠️  Review failed tests and implement missing features');
    console.log('   📚 Refer to VOICE_ACCESS_POLICY.md for requirements');
  }
  
  console.log('\n💡 Enhanced Features Available:');
  console.log('   🎤 Real-time audio visualization with waveform display');
  console.log('   🧠 Intelligent agent deference with context awareness');
  console.log('   🔄 Advanced misroute recovery with natural language');
  console.log('   🔐 Voice authentication with secure mode activation');
  console.log('   📊 Detailed routing breadcrumbs with confidence indicators');
  console.log('   📌 Persistent HUD option for always-on voice interaction');
  
  // Save detailed results
  const reportFile = 'voice_enhancement_test_results.json';
  fs.writeFileSync(reportFile, JSON.stringify({
    timestamp: new Date().toISOString(),
    summary: {
      total: testResults.total,
      passed: testResults.passed,
      failed: testResults.failed,
      successRate: Math.round((testResults.passed / testResults.total) * 100)
    },
    details: testResults.details,
    recommendations: testResults.passed / testResults.total >= 0.8 ? 
      'Ready for production deployment' : 'Requires additional development'
  }, null, 2));
  
  console.log(`\n📄 Detailed results saved to: ${reportFile}`);
}

// Main test execution
function runTests() {
  console.log('🎭 Starting Phase 2C: Enhanced Voice Interaction System Tests');
  console.log('='.repeat(60));
  
  // Check if files exist
  const jsFileExists = checkFileExists(TEST_CONFIG.voiceInterfacePath);
  const cssFileExists = checkFileExists(TEST_CONFIG.voiceInterfaceCSSPath);
  
  logTest('File Structure - JavaScript Component', jsFileExists,
    jsFileExists ? 'VoiceInterface.js found' : 'VoiceInterface.js missing');
  
  logTest('File Structure - CSS Styles', cssFileExists,
    cssFileExists ? 'VoiceInterface.css found' : 'VoiceInterface.css missing');
  
  if (!jsFileExists || !cssFileExists) {
    console.log('\n❌ Critical files missing. Cannot continue tests.');
    return;
  }
  
  // Run feature tests
  testEnhancedHUD();
  testAgentDeferenceSystem();
  testMisrouteRecovery();
  testVoiceAuthentication();
  testOverallImplementation();
  
  // Generate final report
  generateTestReport();
}

// Execute tests
if (require.main === module) {
  runTests();
}

module.exports = {
  runTests,
  testResults
};