/**
 * Test Setup for React Component Tests
 */

import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

// Extend Vitest's expect with jest-dom matchers
expect.extend(matchers);

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock window.electronAPI for tests
global.window = global.window || {};
window.electronAPI = {
  openFile: vi.fn().mockResolvedValue('/mock/path/to/file.zip'),
  openDirectory: vi.fn().mockResolvedValue('/mock/workspace'),
  openPath: vi.fn(),
  copyToClipboard: vi.fn(),
};

// Mock fetch
global.fetch = vi.fn();

// Mock localStorage
const localStorageMock = {
  store: {},
  getItem: vi.fn((key) => localStorageMock.store[key] || null),
  setItem: vi.fn((key, value) => { localStorageMock.store[key] = value; }),
  removeItem: vi.fn((key) => { delete localStorageMock.store[key]; }),
  clear: vi.fn(() => { localStorageMock.store = {}; }),
};
Object.defineProperty(window, 'localStorage', { value: localStorageMock });
