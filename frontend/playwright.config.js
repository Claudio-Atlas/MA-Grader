/**
 * Playwright E2E Configuration for MA Grader Electron App
 */

const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  retries: 1,
  
  use: {
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  
  projects: [
    {
      name: 'electron',
      testMatch: '**/*.e2e.test.js',
    },
  ],
  
  reporter: [
    ['list'],
    ['html', { outputFolder: 'test-results/e2e-report' }],
  ],
});
