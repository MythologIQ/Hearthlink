# SPEC-2 Task Management UI - Local Verification Guide

This guide provides step-by-step instructions to verify the Task Management UI implementation locally, including all CRUD operations, license validation, and testing capabilities.

## Prerequisites

Before running the verification, ensure you have:

- Node.js 18+ installed
- Python 3.10+ installed  
- All dependencies installed (`npm install`)
- Playwright browsers installed (`npm run test:e2e:install`)

## Quick Start Verification

### 1. Start Development Environment

```bash
# Terminal 1: Start Python backend services
npm run services:start

# Terminal 2: Start React development server
npm run start:react

# Terminal 3: Start Tauri native application
npm run native
```

Wait for all services to be running:
- React dev server: http://localhost:3000
- Python API: http://localhost:8000  
- Static assets: http://localhost:3001

### 2. Navigate to Task Dashboard

Open your browser and go to:
```
http://localhost:3000/task-dashboard?userId=test-user&focusFormulaLicenseToken=SA-2025-TEST-MOCK-VALID
```

You should see:
- ✅ Task Management Dashboard header
- ✅ Two tabs: "Tasks" and "Templates"
- ✅ License status indicator (green "Valid" badge)
- ✅ Create Task button

### 3. Verify License Integration

**Test Valid License:**
1. Click on "Templates" tab
2. Verify you see both templates:
   - "Alden Productivity Task" (unlicensed)
   - "🧠 Steve August Focus Formula" (with license badge)
3. Verify the Steve August template shows:
   - Licensed badge
   - Credit link: "Steve August – ADHD Coaching"

**Test Invalid License:**
1. Change URL to remove license token:
   ```
   http://localhost:3000/task-dashboard?userId=test-user
   ```
2. Refresh page
3. Click "Templates" tab
4. Verify Steve August template is NOT shown
5. Only "Alden Productivity Task" should be visible

### 4. Test Steve August Template Creation

**Multi-Step Form Workflow:**
1. Use valid license URL
2. Click "Templates" tab
3. Click "Use Template" on Steve August Focus Formula
4. Verify 4-step form opens:

**Step 1 - Basic Information:**
- Fill in "Title": "Weekly Focus - August 5th"
- Fill in "Week Of": "2025-08-05"
- Click "Next Step"

**Step 2 - Priorities & Brain Dump:**
- Add priorities in text areas
- Add brain dump options (Goal, Rock/Obstacle, Next Step)
- Click "Next Step"

**Step 3 - Vision & Direction:**
- Fill "Magnetic North": "Focus on high-impact deliverables"
- Fill "Vision": "Complete all priority tasks successfully"
- Fill "Values": "Focus, efficiency, self-care"
- Click "Next Step"

**Step 4 - Habits & Schedule:**
- Set habit tracker (check/uncheck days)
- Fill daily priorities for each weekday
- Add decisions with deadlines
- Click "Create Task"

**Expected Results:**
- ✅ Task appears immediately in Tasks tab (optimistic update)
- ✅ Success message displayed
- ✅ Steve August credit link visible in task card
- ✅ Form closes automatically

### 5. Test CRUD Operations

**Create Regular Task:**
1. Click "Create Task" button
2. Fill basic information
3. Select "Alden Productivity" template
4. Complete form and save
5. Verify immediate appearance (optimistic update)

**Update Task:**
1. Click edit icon on any task
2. Modify title or description
3. Save changes
4. Verify immediate update in UI

**Delete Task:**
1. Click delete icon on any task
2. Confirm deletion
3. Verify immediate removal from UI

### 6. Test Error Handling & Rollback

**Simulate API Failure:**
1. Open browser developer tools
2. Go to Network tab
3. Enable "Offline" mode or block requests to `/api/vault/tasks`
4. Try creating a new task
5. Expected behavior:
   - ✅ Task appears initially (optimistic update)
   - ✅ Error message appears after API timeout
   - ✅ Task is removed from UI (rollback)
   - ✅ Error message: "Failed to create task. Please try again."

## Automated Testing Verification

### 1. Run Unit Tests

```bash
npm run test
```

Expected output:
```
✅ All tests passing
✅ No console errors
✅ Coverage reports generated
```

### 2. Run E2E Tests - UI Components

```bash
npm run test:e2e:ui
```

This runs the comprehensive UI test suite covering:
- ✅ Dashboard loading and navigation
- ✅ License validation (valid/invalid/trial scenarios)
- ✅ Steve August template workflow (all 4 steps)
- ✅ Form validation and error messages
- ✅ CRUD operations with optimistic updates
- ✅ Error handling and rollback scenarios
- ✅ Accessibility compliance

### 3. Run E2E Tests - API Integration

```bash
npm run test:e2e:api
```

This tests backend API integration:
- ✅ Template CRUD endpoints
- ✅ License validation API
- ✅ Vault storage operations
- ✅ Audit logging
- ✅ Error handling (401, 404, 422 responses)
- ✅ Performance and concurrency

### 4. Run Full E2E Test Suite

```bash
npm run test:e2e
```

**Expected Results:**
```
✅ All UI tests passing (15+ test cases)
✅ All API tests passing (20+ test cases)
✅ No flaky tests
✅ HTML report generated in playwright-report/
```

### 5. View Test Reports

```bash
npm run test:e2e:report
```

Opens detailed HTML report showing:
- Test execution timeline
- Screenshots of failures (if any)
- Network activity logs
- Performance metrics

## Manual Validation Checklist

### UI/UX Verification
- [ ] **Dashboard Layout**: Clean, responsive layout with proper spacing
- [ ] **License Status**: Clear visual indication of license validity
- [ ] **Navigation**: Smooth tab switching between Tasks/Templates
- [ ] **Form UX**: Intuitive multi-step workflow with progress indicators
- [ ] **Error Messages**: Clear, helpful error messages with recovery options
- [ ] **Accessibility**: Proper ARIA labels, keyboard navigation support

### Functional Verification
- [ ] **License Integration**: Template visibility based on license token
- [ ] **Steve August Form**: All 4 steps function correctly
- [ ] **Credit Attribution**: "Steve August – ADHD Coaching" link visible
- [ ] **CRUD Operations**: Create, read, update, delete work as expected
- [ ] **Optimistic Updates**: Immediate UI feedback before API confirmation
- [ ] **Error Rollback**: Failed operations revert UI state properly

### Data Persistence Verification
- [ ] **Vault Storage**: Tasks persisted to encrypted vault storage
- [ ] **Audit Logging**: All operations logged for compliance
- [ ] **Session Management**: Data survives page refresh
- [ ] **License Validation**: Server-side validation enforced

## Troubleshooting Common Issues

### Services Not Starting
```bash
# Check port conflicts
lsof -i :3000 -i :8000 -i :3001

# Kill conflicting processes
kill -9 $(lsof -t -i:3000)

# Restart services
npm run services:start
```

### Test Failures
```bash
# Clear test cache
rm -rf test-results/ playwright-report/

# Update Playwright browsers
npm run test:e2e:install

# Run tests with debug info
npm run test:e2e:debug
```

### API Connection Issues
```bash
# Verify Python backend status
curl http://localhost:8000/api/templates/

# Check backend logs
tail -f logs/hearthlink_service_*.log
```

### Frontend Build Issues
```bash
# Clear build cache
rm -rf node_modules/ build/ dist/

# Reinstall dependencies
npm install

# Rebuild
npm run build
```

## Performance Verification

### Expected Performance Metrics
- **Page Load**: < 2 seconds for initial dashboard load
- **API Response**: < 500ms for CRUD operations
- **Form Submission**: < 1 second for task creation
- **License Validation**: < 300ms for token verification

### Load Testing
```bash
# Run concurrent API tests
npm run test:e2e:api

# Monitor during test execution
htop  # Check CPU/memory usage
```

## Security Verification

### License Protection
- [ ] **Token Validation**: Invalid tokens properly rejected
- [ ] **Template Access**: Licensed templates hidden without valid token
- [ ] **API Security**: Unauthorized requests return 401
- [ ] **Input Sanitization**: XSS protection in form inputs

### Data Protection
- [ ] **Vault Encryption**: Task data encrypted at rest
- [ ] **Audit Trail**: All operations logged with user attribution
- [ ] **Session Security**: Tokens properly managed and validated

## Next Steps

After successful local verification:

1. **Phase 2 Implementation**: Key rotation and environment consolidation
2. **Production Deployment**: Environment-specific configuration
3. **User Acceptance Testing**: Stakeholder validation
4. **Performance Optimization**: Based on load testing results

## Support

If you encounter issues during verification:

1. **Check Logs**: Review console output and log files
2. **Test Environment**: Ensure all prerequisites are met
3. **Documentation**: Refer to component JSDoc and inline comments
4. **Debug Mode**: Use `npm run test:e2e:debug` for step-by-step test execution

---

**Verification Complete**: ✅ Task Management UI with Steve August ADHD coaching integration, license validation, and comprehensive CRUD operations with audit logging.