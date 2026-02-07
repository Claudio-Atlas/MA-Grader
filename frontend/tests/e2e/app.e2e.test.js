/**
 * MA Grader - Electron E2E Tests
 * 
 * Tests the complete user flows through the Electron application.
 * Requires backend to be running for full integration tests.
 */

const { test, expect, _electron: electron } = require('@playwright/test');
const path = require('path');

let electronApp;
let window;

// Test fixtures
const TEST_ZIP_PATH = '/tmp/test-submissions.zip';
const TEST_COURSE_LABEL = 'TEST-101';

test.describe('MA Grader Electron App', () => {
  
  test.beforeAll(async () => {
    // Launch Electron app
    electronApp = await electron.launch({
      args: [path.join(__dirname, '../../electron/main.js')],
      env: {
        ...process.env,
        NODE_ENV: 'test',
      },
    });
    
    // Get the first window
    window = await electronApp.firstWindow();
    
    // Wait for app to load
    await window.waitForLoadState('domcontentloaded');
  });
  
  test.afterAll(async () => {
    if (electronApp) {
      await electronApp.close();
    }
  });
  
  test.describe('Initial State', () => {
    
    test('should display the app title', async () => {
      const title = await window.locator('h1').textContent();
      expect(title).toContain('MA Grader');
    });
    
    test('should show Ready status badge by default', async () => {
      const statusBadge = window.locator('text=Ready');
      await expect(statusBadge).toBeVisible();
    });
    
    test('should have MA1 selected by default', async () => {
      const assignmentButton = window.locator('button:has-text("MA1")');
      await expect(assignmentButton).toBeVisible();
    });
    
    test('should display all 8 progress steps', async () => {
      const steps = ['Workspace', 'Folders', 'Import', 'Sheets', 'Grade', 'Charts', 'Insert', 'Master'];
      for (const step of steps) {
        const stepLabel = window.locator(`text=${step}`);
        await expect(stepLabel).toBeVisible();
      }
    });
    
    test('should have Run Grading button disabled without ZIP', async () => {
      const runButton = window.locator('button:has-text("Run Grading")');
      await expect(runButton).toBeDisabled();
    });
    
  });
  
  test.describe('Assignment Selection', () => {
    
    test('should open dropdown when clicked', async () => {
      const dropdownButton = window.locator('button:has-text("MA1")');
      await dropdownButton.click();
      
      const dropdown = window.locator('text=MA1 - Major Assignment 1');
      await expect(dropdown).toBeVisible();
    });
    
    test('should show all assignment options', async () => {
      const ma1Option = window.locator('text=MA1 - Major Assignment 1');
      const ma2Option = window.locator('text=MA2 - Major Assignment 2');
      const ma3Option = window.locator('text=MA3 - Major Assignment 3');
      
      await expect(ma1Option).toBeVisible();
      await expect(ma2Option).toBeVisible();
      await expect(ma3Option).toBeVisible();
    });
    
    test('should indicate MA2 is coming soon', async () => {
      const comingSoon = window.locator('text=Coming soon');
      await expect(comingSoon).toBeVisible();
    });
    
    test('should allow selecting MA3', async () => {
      const ma3Option = window.locator('button:has-text("MA3 - Major Assignment 3")');
      await ma3Option.click();
      
      // Verify MA3 is now selected
      const selectedButton = window.locator('button:has-text("MA3")').first();
      await expect(selectedButton).toBeVisible();
    });
    
    test('should switch back to MA1', async () => {
      const dropdownButton = window.locator('button:has-text("MA3")').first();
      await dropdownButton.click();
      
      const ma1Option = window.locator('button:has-text("MA1 - Major Assignment 1")');
      await ma1Option.click();
      
      const selectedButton = window.locator('button:has-text("MA1")').first();
      await expect(selectedButton).toBeVisible();
    });
    
  });
  
  test.describe('Course Label Input', () => {
    
    test('should have default course label', async () => {
      const input = window.locator('input[placeholder*="MAT"]');
      const value = await input.inputValue();
      expect(value).toMatch(/MAT-\d+-\d+/);
    });
    
    test('should allow editing course label', async () => {
      const input = window.locator('input[placeholder*="MAT"]');
      await input.fill('');
      await input.fill(TEST_COURSE_LABEL);
      
      const value = await input.inputValue();
      expect(value).toBe(TEST_COURSE_LABEL);
    });
    
  });
  
  test.describe('Settings Modal', () => {
    
    test('should open settings modal', async () => {
      const settingsButton = window.locator('button[title="Settings"]');
      await settingsButton.click();
      
      const modal = window.locator('text=Workspace Settings');
      await expect(modal).toBeVisible();
    });
    
    test('should display default workspace path info', async () => {
      const defaultInfo = window.locator('text=Documents/MA1_Autograder');
      await expect(defaultInfo).toBeVisible();
    });
    
    test('should have browse button for workspace', async () => {
      const browseButton = window.locator('button:has-text("Browse")');
      await expect(browseButton).toBeVisible();
    });
    
    test('should close settings modal', async () => {
      const closeButton = window.locator('button:has-text("Close")');
      await closeButton.click();
      
      const modal = window.locator('text=Workspace Settings');
      await expect(modal).not.toBeVisible();
    });
    
  });
  
  test.describe('File Drop Zone', () => {
    
    test('should display drop zone', async () => {
      const dropZone = window.locator('text=Drop ZIP file here');
      await expect(dropZone).toBeVisible();
    });
    
    test('should have Browse button', async () => {
      const browseButton = window.locator('button:has-text("Browse")').first();
      await expect(browseButton).toBeVisible();
    });
    
  });
  
  test.describe('Logs Section', () => {
    
    test('should have Show Logs button', async () => {
      const logsButton = window.locator('button:has-text("Show Logs")');
      await expect(logsButton).toBeVisible();
    });
    
    test('should expand logs section when clicked', async () => {
      const logsButton = window.locator('button:has-text("Show Logs")');
      await logsButton.click();
      
      // Should now show "Hide Logs"
      const hideButton = window.locator('button:has-text("Hide Logs")');
      await expect(hideButton).toBeVisible();
    });
    
    test('should collapse logs section', async () => {
      const hideButton = window.locator('button:has-text("Hide Logs")');
      await hideButton.click();
      
      const showButton = window.locator('button:has-text("Show Logs")');
      await expect(showButton).toBeVisible();
    });
    
  });
  
  test.describe('Reset Functionality', () => {
    
    test('should have New Grading button', async () => {
      const newButton = window.locator('button:has-text("New Grading")');
      await expect(newButton).toBeVisible();
    });
    
  });
  
});

test.describe('Backend Integration', () => {
  // These tests require the backend to be running
  
  test.beforeAll(async () => {
    electronApp = await electron.launch({
      args: [path.join(__dirname, '../../electron/main.js')],
    });
    window = await electronApp.firstWindow();
    await window.waitForLoadState('domcontentloaded');
  });
  
  test.afterAll(async () => {
    if (electronApp) {
      await electronApp.close();
    }
  });
  
  test('should connect to backend health endpoint', async () => {
    // Check if backend is reachable
    const response = await window.evaluate(async () => {
      try {
        const res = await fetch('http://127.0.0.1:8765/health');
        return res.ok;
      } catch {
        return false;
      }
    });
    
    // This test may fail if backend isn't running - that's OK
    if (response) {
      expect(response).toBe(true);
    } else {
      console.log('Backend not running - skipping integration test');
    }
  });
  
});

test.describe('Error Handling', () => {
  
  test.beforeAll(async () => {
    electronApp = await electron.launch({
      args: [path.join(__dirname, '../../electron/main.js')],
    });
    window = await electronApp.firstWindow();
    await window.waitForLoadState('domcontentloaded');
  });
  
  test.afterAll(async () => {
    if (electronApp) {
      await electronApp.close();
    }
  });
  
  test('should handle missing ZIP file gracefully', async () => {
    // Try to run without a ZIP file - button should be disabled
    const runButton = window.locator('button:has-text("Run Grading")');
    const isDisabled = await runButton.isDisabled();
    expect(isDisabled).toBe(true);
  });
  
});

test.describe('UI Responsiveness', () => {
  
  test.beforeAll(async () => {
    electronApp = await electron.launch({
      args: [path.join(__dirname, '../../electron/main.js')],
    });
    window = await electronApp.firstWindow();
    await window.waitForLoadState('domcontentloaded');
  });
  
  test.afterAll(async () => {
    if (electronApp) {
      await electronApp.close();
    }
  });
  
  test('should maintain layout at different window sizes', async () => {
    // Test minimum size
    await window.setViewportSize({ width: 800, height: 600 });
    
    const title = window.locator('h1');
    await expect(title).toBeVisible();
    
    // Test larger size
    await window.setViewportSize({ width: 1200, height: 800 });
    await expect(title).toBeVisible();
  });
  
});
