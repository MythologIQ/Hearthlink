/**
 * Project Command Integration Test Suite
 * Tests the complete integration of ProjectTemplateEngine with ProjectCommand component
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ProjectCommand from '../components/ProjectCommand';
import ProjectTemplateEngine from '../utils/ProjectTemplateEngine';

// Mock the TaskDelegationService
jest.mock('../services/TaskDelegationService', () => ({
  getServiceStatus: jest.fn().mockResolvedValue({
    'claude-code': { available: true },
    'google-ai': { available: true },
    'ollama': { available: false }
  }),
  delegateTask: jest.fn().mockResolvedValue({
    success: true,
    service_used: 'claude-code',
    response: 'Task completed successfully'
  })
}));

describe('Project Command Integration Tests', () => {
  const mockProps = {
    accessibilitySettings: { highContrast: false },
    onVoiceCommand: jest.fn(),
    currentAgent: 'Alden'
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders Project Command interface with all navigation tabs', () => {
    render(<ProjectCommand {...mockProps} />);
    
    expect(screen.getByText('PROJECT COMMAND')).toBeInTheDocument();
    expect(screen.getByText('📊 Dashboard')).toBeInTheDocument();
    expect(screen.getByText('⚡ Templates')).toBeInTheDocument();
    expect(screen.getByText('🎯 Methodology')).toBeInTheDocument();
    expect(screen.getByText('📈 Retrospective')).toBeInTheDocument();
    expect(screen.getByText('🤖 AI Delegation')).toBeInTheDocument();
  });

  test('displays template selection interface when Templates tab is clicked', async () => {
    render(<ProjectCommand {...mockProps} />);
    
    const templatesTab = screen.getByText('⚡ Templates');
    fireEvent.click(templatesTab);
    
    await waitFor(() => {
      expect(screen.getByText('⚡ Project Templates')).toBeInTheDocument();
      expect(screen.getByText('Choose from pre-built project templates with intelligent task generation')).toBeInTheDocument();
    });
  });

  test('shows all available templates in template selection', async () => {
    render(<ProjectCommand {...mockProps} />);
    
    fireEvent.click(screen.getByText('⚡ Templates'));
    
    await waitFor(() => {
      expect(screen.getByText('Full-Stack Web Application')).toBeInTheDocument();
      expect(screen.getByText('AI Integration Project')).toBeInTheDocument();
      expect(screen.getByText('Data Analytics Dashboard')).toBeInTheDocument();
      expect(screen.getByText('Microservices Architecture')).toBeInTheDocument();
      expect(screen.getByText('Mobile App MVP')).toBeInTheDocument();
    });
  });

  test('opens project creation modal when template is selected', async () => {
    render(<ProjectCommand {...mockProps} />);
    
    fireEvent.click(screen.getByText('⚡ Templates'));
    
    await waitFor(() => {
      const selectButtons = screen.getAllByText('Select Template');
      fireEvent.click(selectButtons[0]); // Select first template
    });
    
    await waitFor(() => {
      expect(screen.getByText(/Create Project:/)).toBeInTheDocument();
      expect(screen.getByText('Template Overview')).toBeInTheDocument();
      expect(screen.getByText('Project Details')).toBeInTheDocument();
    });
  });

  test('creates new project from template with proper data structure', async () => {
    render(<ProjectCommand {...mockProps} />);
    
    fireEvent.click(screen.getByText('⚡ Templates'));
    
    await waitFor(() => {
      const selectButtons = screen.getAllByText('Select Template');
      fireEvent.click(selectButtons[0]);
    });
    
    await waitFor(() => {
      // Fill in project details
      const nameInput = screen.getByPlaceholderText('Enter project name...');
      fireEvent.change(nameInput, { target: { value: 'Test Project' } });
      
      const descriptionInput = screen.getByPlaceholderText('Describe your project...');
      fireEvent.change(descriptionInput, { target: { value: 'Test project description' } });
      
      // Click create button
      fireEvent.click(screen.getByText('Create Project'));
    });
    
    await waitFor(() => {
      // Should return to dashboard with new project
      expect(screen.getByText('Test Project')).toBeInTheDocument();
    });
  });

  test('shows project analytics for template-generated projects', async () => {
    render(<ProjectCommand {...mockProps} />);
    
    // Create a project first
    fireEvent.click(screen.getByText('⚡ Templates'));
    
    await waitFor(() => {
      const selectButtons = screen.getAllByText('Select Template');
      fireEvent.click(selectButtons[0]);
    });
    
    await waitFor(() => {
      const nameInput = screen.getByPlaceholderText('Enter project name...');
      fireEvent.change(nameInput, { target: { value: 'Analytics Test Project' } });
      fireEvent.click(screen.getByText('Create Project'));
    });
    
    await waitFor(() => {
      // Click on the created project to see analytics
      const projectCard = screen.getByText('Analytics Test Project');
      fireEvent.click(projectCard.closest('.project-card'));
      
      // Should show analytics panel
      expect(screen.getByText(/Project Analysis:/)).toBeInTheDocument();
      expect(screen.getByText('Task Breakdown')).toBeInTheDocument();
      expect(screen.getByText('Resource Utilization')).toBeInTheDocument();
      expect(screen.getByText('Phase Timeline')).toBeInTheDocument();
    });
  });

  test('shows template recommendations based on requirements', async () => {
    render(<ProjectCommand {...mockProps} />);
    
    fireEvent.click(screen.getByText('⚡ Templates'));
    
    await waitFor(() => {
      // Set category requirement
      const categorySelect = screen.getByDisplayValue('');
      fireEvent.change(categorySelect, { target: { value: 'development' } });
    });
    
    await waitFor(() => {
      expect(screen.getByText('🎯 Recommended for Your Requirements')).toBeInTheDocument();
    });
  });

  test('integrates with task delegation system', async () => {
    render(<ProjectCommand {...mockProps} />);
    
    fireEvent.click(screen.getByText('🤖 AI Delegation'));
    
    await waitFor(() => {
      expect(screen.getByText('🤖 AI Task Delegation')).toBeInTheDocument();
      expect(screen.getByText('Available AI Agents')).toBeInTheDocument();
      expect(screen.getByText('Claude Code')).toBeInTheDocument();
      expect(screen.getByText('Google Gemini')).toBeInTheDocument();
      expect(screen.getByText('Ollama LLM')).toBeInTheDocument();
    });
  });

  test('handles project creation with different methodologies', async () => {
    render(<ProjectCommand {...mockProps} />);
    
    fireEvent.click(screen.getByText('⚡ Templates'));
    
    await waitFor(() => {
      const selectButtons = screen.getAllByText('Select Template');
      fireEvent.click(selectButtons[1]); // Select AI Integration template
    });
    
    await waitFor(() => {
      // Change methodology
      const methodologySelect = screen.getByDisplayValue('agile');
      fireEvent.change(methodologySelect, { target: { value: 'kanban' } });
      
      const nameInput = screen.getByPlaceholderText('Enter project name...');
      fireEvent.change(nameInput, { target: { value: 'Kanban AI Project' } });
      
      fireEvent.click(screen.getByText('Create Project'));
    });
    
    await waitFor(() => {
      expect(screen.getByText('Kanban AI Project')).toBeInTheDocument();
      expect(screen.getByText('KANBAN')).toBeInTheDocument();
    });
  });

  test('displays template complexity levels correctly', async () => {
    render(<ProjectCommand {...mockProps} />);
    
    fireEvent.click(screen.getByText('⚡ Templates'));
    
    await waitFor(() => {
      expect(screen.getByText('HIGH')).toBeInTheDocument(); // Full-stack app
      expect(screen.getByText('MEDIUM')).toBeInTheDocument(); // AI Integration
      expect(screen.getByText('VERY-HIGH')).toBeInTheDocument(); // Microservices
    });
  });

  test('shows proper resource allocation in project analytics', async () => {
    const testTemplate = ProjectTemplateEngine.getAvailableTemplates()[0];
    const generatedProject = ProjectTemplateEngine.generateProject(testTemplate.id, {
      name: 'Resource Test Project'
    });
    
    expect(generatedProject.resources).toBeDefined();
    expect(Object.keys(generatedProject.resources).length).toBeGreaterThan(0);
    
    // Check that resources have proper allocation
    Object.values(generatedProject.resources).forEach(allocation => {
      expect(allocation.tasks).toBeDefined();
      expect(allocation.estimatedHours).toBeGreaterThan(0);
      expect(allocation.utilization).toBeGreaterThanOrEqual(0);
    });
  });

  test('validates project creation form requirements', async () => {
    render(<ProjectCommand {...mockProps} />);
    
    fireEvent.click(screen.getByText('⚡ Templates'));
    
    await waitFor(() => {
      const selectButtons = screen.getAllByText('Select Template');
      fireEvent.click(selectButtons[0]);
    });
    
    await waitFor(() => {
      // Try to create without name
      const createButton = screen.getByText('Create Project');
      expect(createButton).toBeDisabled();
      
      // Add name, button should be enabled
      const nameInput = screen.getByPlaceholderText('Enter project name...');
      fireEvent.change(nameInput, { target: { value: 'Valid Project Name' } });
      
      expect(createButton).not.toBeDisabled();
    });
  });
});

// Integration Test for ProjectTemplateEngine
describe('ProjectTemplateEngine Integration', () => {
  test('generates complete project structure from template', () => {
    const template = ProjectTemplateEngine.getAvailableTemplates()[0];
    const project = ProjectTemplateEngine.generateProject(template.id, {
      name: 'Integration Test Project',
      description: 'Test project for integration'
    });
    
    expect(project).toHaveProperty('id');
    expect(project).toHaveProperty('name', 'Integration Test Project');
    expect(project).toHaveProperty('phases');
    expect(project).toHaveProperty('tasks');
    expect(project).toHaveProperty('resources');
    expect(project).toHaveProperty('metrics');
    
    expect(project.phases.length).toBeGreaterThan(0);
    expect(project.tasks.length).toBeGreaterThan(0);
    expect(project.metrics.totalTasks).toEqual(project.tasks.length);
  });
  
  test('properly assigns resources to tasks', () => {
    const template = ProjectTemplateEngine.getAvailableTemplates()[0];
    const project = ProjectTemplateEngine.generateProject(template.id);
    
    project.tasks.forEach(task => {
      expect(task.assignedAgent).toBeDefined();
      expect(['alden', 'alice', 'mimic', 'sentry']).toContain(task.assignedAgent);
    });
  });
  
  test('calculates realistic effort estimates', () => {
    const template = ProjectTemplateEngine.getAvailableTemplates()[0];
    const project = ProjectTemplateEngine.generateProject(template.id);
    
    expect(project.metrics.estimatedEffort).toBeGreaterThan(0);
    
    const manualTotal = project.tasks.reduce((total, task) => total + task.estimatedHours, 0);
    expect(project.metrics.estimatedEffort).toBeGreaterThan(manualTotal); // Should include complexity buffer
  });
  
  test('provides template recommendations based on requirements', () => {
    const requirements = {
      category: 'development',
      complexity: 'high',
      skills: ['frontend', 'backend']
    };
    
    const recommendations = ProjectTemplateEngine.recommendTemplates(requirements);
    
    expect(recommendations.length).toBeGreaterThan(0);
    expect(recommendations[0]).toHaveProperty('score');
    expect(recommendations[0]).toHaveProperty('template');
    expect(recommendations[0]).toHaveProperty('reason');
    
    // Recommendations should be sorted by score
    for (let i = 1; i < recommendations.length; i++) {
      expect(recommendations[i-1].score).toBeGreaterThanOrEqual(recommendations[i].score);
    }
  });
});

// Performance Tests
describe('Project Command Performance Tests', () => {
  test('template generation completes within reasonable time', () => {
    const startTime = Date.now();
    const template = ProjectTemplateEngine.getAvailableTemplates()[0];
    const project = ProjectTemplateEngine.generateProject(template.id);
    const endTime = Date.now();
    
    expect(endTime - startTime).toBeLessThan(1000); // Should complete within 1 second
    expect(project).toBeDefined();
  });
  
  test('handles multiple concurrent project generations', async () => {
    const templates = ProjectTemplateEngine.getAvailableTemplates().slice(0, 3);
    
    const startTime = Date.now();
    const projectPromises = templates.map(template => 
      Promise.resolve(ProjectTemplateEngine.generateProject(template.id, {
        name: `Concurrent Project ${template.id}`
      }))
    );
    
    const projects = await Promise.all(projectPromises);
    const endTime = Date.now();
    
    expect(projects.length).toBe(3);
    expect(endTime - startTime).toBeLessThan(2000); // Should complete within 2 seconds
    
    projects.forEach(project => {
      expect(project).toHaveProperty('id');
      expect(project.tasks.length).toBeGreaterThan(0);
    });
  });
});

export default {
  testSuiteName: 'Project Command Integration Tests',
  totalTests: 15,
  description: 'Comprehensive integration tests for Project Command system with template engine',
  coverage: {
    components: ['ProjectCommand', 'ProjectTemplateEngine'],
    features: ['template selection', 'project creation', 'analytics', 'resource allocation'],
    integrations: ['task delegation', 'methodology selection', 'UI interactions']
  }
};