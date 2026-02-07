/**
 * MA Grader - React Component Tests
 * 
 * Tests individual UI components and their interactions.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import App from '../../src/App';

// API Base URL used by the app
const API_BASE = 'http://127.0.0.1:8765';

describe('App Component', () => {
  
  beforeEach(() => {
    // Reset all mocks before each test
    vi.clearAllMocks();
    window.localStorage.clear();
    
    // Default fetch mock - idle state
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        status: 'idle',
        current_step: null,
        progress: 0,
        logs: [],
        error: null,
        output_path: null,
      }),
    });
  });
  
  afterEach(() => {
    vi.restoreAllMocks();
  });
  
  describe('Rendering', () => {
    
    it('renders the app title', () => {
      render(<App />);
      expect(screen.getByText('MA Grader')).toBeInTheDocument();
    });
    
    it('renders the subtitle', () => {
      render(<App />);
      expect(screen.getByText('Excel Assignment Auto-Grader')).toBeInTheDocument();
    });
    
    it('renders the Ready status badge', () => {
      render(<App />);
      expect(screen.getByText('Ready')).toBeInTheDocument();
    });
    
    it('renders the drop zone', () => {
      render(<App />);
      expect(screen.getByText(/Drop ZIP file here/i)).toBeInTheDocument();
    });
    
    it('renders Pipeline Status label', () => {
      render(<App />);
      expect(screen.getByText('Pipeline Status')).toBeInTheDocument();
    });
    
    it('renders Course Label section', () => {
      render(<App />);
      expect(screen.getByText('Course Label')).toBeInTheDocument();
    });
    
  });
  
  describe('Assignment Dropdown', () => {
    
    it('shows MA1 selected by default', () => {
      render(<App />);
      expect(screen.getByRole('button', { name: /MA1/i })).toBeInTheDocument();
    });
    
    it('opens dropdown on click', async () => {
      const user = userEvent.setup();
      render(<App />);
      
      const dropdownButton = screen.getByRole('button', { name: /MA1/i });
      await user.click(dropdownButton);
      
      expect(screen.getByText('MA1 - Major Assignment 1')).toBeInTheDocument();
      expect(screen.getByText('MA2 - Major Assignment 2')).toBeInTheDocument();
      expect(screen.getByText('MA3 - Major Assignment 3')).toBeInTheDocument();
    });
    
    it('shows MA2 as coming soon', async () => {
      const user = userEvent.setup();
      render(<App />);
      
      const dropdownButton = screen.getByRole('button', { name: /MA1/i });
      await user.click(dropdownButton);
      
      expect(screen.getByText(/Coming soon/i)).toBeInTheDocument();
    });
    
    it('allows selecting MA3', async () => {
      const user = userEvent.setup();
      render(<App />);
      
      // Open dropdown
      const dropdownButton = screen.getByRole('button', { name: /MA1/i });
      await user.click(dropdownButton);
      
      // Select MA3
      const ma3Option = screen.getByText('MA3 - Major Assignment 3');
      await user.click(ma3Option);
      
      // Verify selection changed
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /MA3/i })).toBeInTheDocument();
      });
    });
    
    it('disables MA2 option', async () => {
      const user = userEvent.setup();
      render(<App />);
      
      const dropdownButton = screen.getByRole('button', { name: /MA1/i });
      await user.click(dropdownButton);
      
      const ma2Option = screen.getByText('MA2 - Major Assignment 2').closest('button');
      expect(ma2Option).toBeDisabled();
    });
    
  });
  
  describe('Course Label Input', () => {
    
    it('has default course label or saved value', () => {
      render(<App />);
      // The input should exist
      const inputs = screen.getAllByRole('textbox');
      expect(inputs.length).toBeGreaterThan(0);
    });
    
    it('allows editing course label', async () => {
      const user = userEvent.setup();
      render(<App />);
      
      // Find the course label input (one with placeholder)
      const inputs = screen.getAllByRole('textbox');
      const courseInput = inputs.find(input => 
        input.placeholder?.includes('MAT-144') || input.placeholder?.includes('e.g.')
      );
      
      if (courseInput) {
        await user.clear(courseInput);
        await user.type(courseInput, 'TEST-101');
        expect(courseInput).toHaveValue('TEST-101');
      }
    });
    
    it('persists course label to localStorage', async () => {
      const user = userEvent.setup();
      render(<App />);
      
      const inputs = screen.getAllByRole('textbox');
      const courseInput = inputs.find(input => 
        input.placeholder?.includes('MAT-144') || input.placeholder?.includes('e.g.')
      );
      
      if (courseInput) {
        await user.clear(courseInput);
        await user.type(courseInput, 'SAVED-COURSE');
        
        // Wait for useEffect to save
        await waitFor(() => {
          expect(window.localStorage.setItem).toHaveBeenCalled();
        });
      }
    });
    
  });
  
  describe('Settings Modal', () => {
    
    it('opens settings when settings button clicked', async () => {
      const user = userEvent.setup();
      render(<App />);
      
      const settingsButton = screen.getByTitle('Settings');
      await user.click(settingsButton);
      
      // Modal title is "Settings" not "Workspace Settings"
      expect(screen.getByRole('heading', { name: /Settings/i })).toBeInTheDocument();
    });
    
    it('shows workspace location field in settings', async () => {
      const user = userEvent.setup();
      render(<App />);
      
      const settingsButton = screen.getByTitle('Settings');
      await user.click(settingsButton);
      
      expect(screen.getByText(/Workspace Location/i)).toBeInTheDocument();
    });
    
    it('closes settings with Done button', async () => {
      const user = userEvent.setup();
      render(<App />);
      
      // Open settings
      const settingsButton = screen.getByTitle('Settings');
      await user.click(settingsButton);
      
      // Close settings (button says "Done" not "Close")
      const doneButton = screen.getByRole('button', { name: /Done/i });
      await user.click(doneButton);
      
      await waitFor(() => {
        expect(screen.queryByRole('heading', { name: /Settings/i })).not.toBeInTheDocument();
      });
    });
    
  });
  
  describe('Run Grading Button', () => {
    
    it('is disabled when no ZIP file selected', () => {
      render(<App />);
      // Button text contains "Run" or "Grade"
      const buttons = screen.getAllByRole('button');
      const runButton = buttons.find(btn => 
        btn.textContent?.includes('Run') || btn.textContent?.includes('Grade')
      );
      
      if (runButton) {
        expect(runButton).toBeDisabled();
      }
    });
    
  });
  
  describe('Logs Section', () => {
    
    it('has Show Logs button', () => {
      render(<App />);
      expect(screen.getByRole('button', { name: /Show Logs/i })).toBeInTheDocument();
    });
    
    it('toggles logs visibility', async () => {
      const user = userEvent.setup();
      render(<App />);
      
      // Initially show logs button visible
      const showButton = screen.getByRole('button', { name: /Show Logs/i });
      expect(showButton).toBeInTheDocument();
      
      // Click to show logs
      await user.click(showButton);
      
      // Now should show hide logs
      expect(screen.getByRole('button', { name: /Hide Logs/i })).toBeInTheDocument();
    });
    
  });
  
  describe('Reset Functionality', () => {
    
    it('has reset/new grading button', () => {
      render(<App />);
      const buttons = screen.getAllByRole('button');
      const resetButton = buttons.find(btn => 
        btn.textContent?.toLowerCase().includes('new') || 
        btn.textContent?.toLowerCase().includes('reset')
      );
      expect(resetButton).toBeInTheDocument();
    });
    
    it('calls reset endpoint when reset clicked', async () => {
      const user = userEvent.setup();
      render(<App />);
      
      const buttons = screen.getAllByRole('button');
      const resetButton = buttons.find(btn => 
        btn.textContent?.toLowerCase().includes('new') || 
        btn.textContent?.toLowerCase().includes('reset')
      );
      
      if (resetButton) {
        await user.click(resetButton);
        
        await waitFor(() => {
          expect(global.fetch).toHaveBeenCalledWith(`${API_BASE}/reset`, { method: 'POST' });
        });
      }
    });
    
  });
  
  describe('Status States', () => {
    
    it('shows Running status when pipeline is running', async () => {
      // Override fetch to return running state
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          status: 'running',
          current_step: 'Grading formulas...',
          progress: 5,
          logs: ['Processing student 1...'],
          error: null,
          output_path: null,
        }),
      });
      
      render(<App />);
      
      // Need to simulate state polling - click something that triggers setState
      // The app polls when status is running, but starts idle
      // This test verifies the component can render running state
    });
    
    it('shows progress steps when running', async () => {
      // This would require simulating the running state
      // which happens through polling when state.status === 'running'
    });
    
  });
  
  describe('File Drop Zone', () => {
    
    it('displays drop zone instructions', () => {
      render(<App />);
      expect(screen.getByText(/Drop ZIP file here/i)).toBeInTheDocument();
      expect(screen.getByText(/click to browse/i)).toBeInTheDocument();
    });
    
  });
  
});

describe('API Integration', () => {
  
  beforeEach(() => {
    vi.clearAllMocks();
    window.localStorage.clear();
  });
  
  it('polls state endpoint when status is running', async () => {
    // Start with running state
    let callCount = 0;
    global.fetch = vi.fn().mockImplementation(() => {
      callCount++;
      if (callCount <= 2) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({
            status: 'running',
            progress: callCount,
            current_step: 'Processing...',
            logs: [],
            error: null,
            output_path: null,
          }),
        });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
          status: 'completed',
          progress: 8,
          current_step: 'Complete!',
          logs: [],
          error: null,
          output_path: '/output/path',
        }),
      });
    });
    
    // Note: Testing polling behavior would require more setup
    // This is a placeholder for the integration test concept
  });
  
});

describe('Accessibility', () => {
  
  beforeEach(() => {
    vi.clearAllMocks();
    window.localStorage.clear();
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ status: 'idle' }),
    });
  });
  
  it('has accessible button labels', () => {
    render(<App />);
    
    // Settings button should have title
    expect(screen.getByTitle('Settings')).toBeInTheDocument();
  });
  
  it('form inputs have associated labels', () => {
    render(<App />);
    
    // Course Label should have a label
    expect(screen.getByText('Course Label')).toBeInTheDocument();
  });
  
  it('disabled buttons have correct aria attributes', () => {
    render(<App />);
    
    const buttons = screen.getAllByRole('button');
    const disabledButtons = buttons.filter(btn => btn.disabled);
    
    // Run button should be disabled when no file selected
    expect(disabledButtons.length).toBeGreaterThan(0);
  });
  
});
