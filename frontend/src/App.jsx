import React, { useState, useEffect, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import {
  Upload,
  Play,
  FolderOpen,
  Users,
  Copy,
  Trash2,
  CheckCircle,
  AlertCircle,
  Loader,
  ChevronDown,
  FileSpreadsheet,
  RefreshCw,
  Settings,
  X,
  Folder,
  StopCircle
} from 'lucide-react';

const API_BASE = 'http://127.0.0.1:8765';

// Assignment types
const ASSIGNMENTS = [
  { id: 'MA1', label: 'MA1 - Major Assignment 1', available: true },
  { id: 'MA2', label: 'MA2 - Major Assignment 2', available: false },
  { id: 'MA3', label: 'MA3 - Major Assignment 3', available: true },
];

// Pipeline steps for progress display
const STEPS = [
  { id: 1, label: 'Workspace' },
  { id: 2, label: 'Folders' },
  { id: 3, label: 'Import' },
  { id: 4, label: 'Sheets' },
  { id: 5, label: 'Grade' },
  { id: 6, label: 'Charts' },
  { id: 7, label: 'Insert' },
  { id: 8, label: 'Master' },
];

function App() {
  // State
  const [assignment, setAssignment] = useState('MA1');
  const [courseLabel, setCourseLabel] = useState(() => {
    return localStorage.getItem('ma-grader-course') || 'MAT-144-501';
  });
  const [zipPath, setZipPath] = useState('');
  const [workspacePath, setWorkspacePath] = useState(() => {
    return localStorage.getItem('ma-grader-workspace') || '';
  });
  const [state, setState] = useState({
    status: 'idle',
    current_step: null,
    progress: 0,
    logs: [],
    error: null,
    output_path: null
  });
  const [showLogs, setShowLogs] = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  // Save preferences to localStorage
  useEffect(() => {
    localStorage.setItem('ma-grader-course', courseLabel);
  }, [courseLabel]);

  useEffect(() => {
    localStorage.setItem('ma-grader-workspace', workspacePath);
  }, [workspacePath]);

  // Prevent default drag behavior at document level (Electron fix)
  useEffect(() => {
    const preventDefaults = (e) => {
      e.preventDefault();
      e.stopPropagation();
    };
    
    // Prevent browser from opening dropped files
    document.addEventListener('dragover', preventDefaults);
    document.addEventListener('drop', preventDefaults);
    
    return () => {
      document.removeEventListener('dragover', preventDefaults);
      document.removeEventListener('drop', preventDefaults);
    };
  }, []);

  // Poll for state updates when running
  useEffect(() => {
    let interval;
    if (state.status === 'running') {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`${API_BASE}/state`);
          const data = await res.json();
          setState(data);
        } catch (err) {
          console.error('Failed to fetch state:', err);
        }
      }, 500);
    }
    return () => clearInterval(interval);
  }, [state.status]);

  // File drop handler - works with both react-dropzone and native Electron drag
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      // In Electron, files have a path property
      const filePath = acceptedFiles[0].path || acceptedFiles[0].name;
      if (filePath && filePath.endsWith('.zip')) {
        setZipPath(filePath);
      }
    }
  }, []);

  // Native drag and drop handler for Electron
  const handleNativeDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const files = e.dataTransfer?.files;
    if (files && files.length > 0) {
      const file = files[0];
      // Electron provides the full path
      const filePath = file.path || file.name;
      if (filePath && filePath.toLowerCase().endsWith('.zip')) {
        setZipPath(filePath);
      }
    }
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/zip': ['.zip'] },
    multiple: false,
    noClick: false,
    noKeyboard: false
  });

  // Browse for ZIP file
  const handleBrowseZip = async () => {
    if (window.electronAPI) {
      const path = await window.electronAPI.openFile({
        filters: [{ name: 'ZIP Files', extensions: ['zip'] }]
      });
      if (path) setZipPath(path);
    }
  };

  // Browse for workspace folder
  const handleBrowseWorkspace = async () => {
    if (window.electronAPI) {
      const path = await window.electronAPI.openDirectory();
      if (path) setWorkspacePath(path);
    }
  };

  // Start grading pipeline
  const handleRunPipeline = async () => {
    if (!zipPath || !courseLabel) return;

    try {
      const res = await fetch(`${API_BASE}/grade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          zip_path: zipPath,
          course_label: courseLabel,
          assignment_type: assignment,
          workspace_path: workspacePath || null
        })
      });
      
      if (res.ok) {
        setState(prev => ({ ...prev, status: 'running', progress: 0, logs: [] }));
      } else {
        const err = await res.json();
        alert(`Error: ${err.detail}`);
      }
    } catch (err) {
      alert(`Connection error: ${err.message}`);
    }
  };

  // Reset state
  const handleReset = async () => {
    try {
      await fetch(`${API_BASE}/reset`, { method: 'POST' });
      setState({
        status: 'idle',
        current_step: null,
        progress: 0,
        logs: [],
        error: null,
        output_path: null
      });
      setZipPath('');
    } catch (err) {
      console.error('Reset failed:', err);
    }
  };

  // Cancel running pipeline
  const handleCancel = async () => {
    try {
      const res = await fetch(`${API_BASE}/cancel`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        console.log('Cancel response:', data);
      }
    } catch (err) {
      console.error('Cancel failed:', err);
    }
  };

  // Open folder
  const handleOpenFolder = (path) => {
    if (window.electronAPI && path) {
      window.electronAPI.openPath(path);
    }
  };

  // Copy path to clipboard
  const handleCopyPath = () => {
    if (window.electronAPI && state.output_path) {
      window.electronAPI.copyToClipboard(state.output_path);
    }
  };

  // Status badge
  const StatusBadge = () => {
    const configs = {
      idle: { color: 'bg-dark-500', text: 'Ready', icon: null },
      running: { color: 'bg-accent-yellow', text: 'Running', icon: <Loader className="w-4 h-4 animate-spin" /> },
      cancelled: { color: 'bg-orange-500', text: 'Cancelled', icon: <StopCircle className="w-4 h-4" /> },
      completed: { color: 'bg-accent-green', text: 'Complete', icon: <CheckCircle className="w-4 h-4" /> },
      error: { color: 'bg-accent-red', text: 'Error', icon: <AlertCircle className="w-4 h-4" /> },
    };
    const config = configs[state.status] || configs.idle;

    return (
      <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full ${config.color} text-white text-sm font-medium`}>
        {config.icon}
        {config.text}
      </div>
    );
  };

  // Progress steps
  const ProgressSteps = () => (
    <div className="flex items-center justify-between px-2">
      {STEPS.map((step, i) => {
        const isComplete = state.progress > step.id;
        const isCurrent = state.progress === step.id;
        const isPending = state.progress < step.id;

        return (
          <React.Fragment key={step.id}>
            <div className="flex flex-col items-center">
              <div className={`
                w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium
                transition-all duration-300
                ${isComplete ? 'bg-accent-green text-white' : ''}
                ${isCurrent ? 'bg-accent-yellow text-dark-900 ring-2 ring-accent-yellow/50' : ''}
                ${isPending ? 'bg-dark-600 text-dark-300' : ''}
              `}>
                {isComplete ? <CheckCircle className="w-4 h-4" /> : step.id}
              </div>
              <span className={`text-xs mt-1 ${isCurrent ? 'text-dark-100' : 'text-dark-400'}`}>
                {step.label}
              </span>
            </div>
            {i < STEPS.length - 1 && (
              <div className={`flex-1 h-0.5 mx-1 ${isComplete ? 'bg-accent-green' : 'bg-dark-600'}`} />
            )}
          </React.Fragment>
        );
      })}
    </div>
  );

  return (
    <div className="min-h-screen bg-dark-900">
      {/* Title bar drag region */}
      <div className="h-8 drag-region" />

      <div className="max-w-4xl mx-auto px-6 pb-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <img src="./logo.png" alt="ATLAS" className="w-16 h-16" />
            <div>
              <h1 className="text-2xl font-bold text-dark-50">MA Grader</h1>
              <p className="text-dark-300 text-sm">Excel Assignment Auto-Grader</p>
            </div>
          </div>

          {/* Settings + Assignment dropdown */}
          <div className="flex items-center gap-3 no-drag">
            <button
              onClick={() => setShowSettings(true)}
              className="p-2 bg-dark-700 rounded-lg border border-dark-500 hover:border-dark-400 transition-colors"
              title="Settings"
            >
              <Settings className="w-5 h-5 text-dark-300" />
            </button>
            <div className="relative">
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="flex items-center gap-2 px-4 py-2 bg-dark-700 rounded-lg border border-dark-500 hover:border-dark-400 transition-colors"
              >
                <span className="font-medium">{assignment}</span>
                <ChevronDown className="w-4 h-4 text-dark-300" />
              </button>
            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-64 bg-dark-700 rounded-lg border border-dark-500 shadow-xl z-10">
                {ASSIGNMENTS.map((a) => (
                  <button
                    key={a.id}
                    disabled={!a.available}
                    onClick={() => {
                      if (a.available) {
                        setAssignment(a.id);
                        setDropdownOpen(false);
                      }
                    }}
                    className={`
                      w-full px-4 py-3 text-left text-sm
                      ${a.available ? 'hover:bg-dark-600 text-dark-100' : 'text-dark-400 cursor-not-allowed'}
                      ${a.id === assignment ? 'bg-dark-600' : ''}
                      first:rounded-t-lg last:rounded-b-lg
                    `}
                  >
                    {a.label}
                    {!a.available && <span className="ml-2 text-xs text-dark-400">(Coming soon)</span>}
                  </button>
                ))}
              </div>
            )}
            </div>
          </div>
        </div>

        {/* Settings Modal */}
        {showSettings && (
          <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
            <div className="bg-dark-800 rounded-2xl border border-dark-600 w-full max-w-lg mx-4 shadow-2xl">
              <div className="flex items-center justify-between p-6 border-b border-dark-600">
                <h2 className="text-xl font-semibold text-dark-50">Settings</h2>
                <button
                  onClick={() => setShowSettings(false)}
                  className="p-2 hover:bg-dark-700 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-dark-300" />
                </button>
              </div>
              <div className="p-6 space-y-6">
                {/* Workspace Location */}
                <div>
                  <label className="block text-dark-200 text-sm font-medium mb-2">
                    Workspace Location
                  </label>
                  <p className="text-dark-400 text-sm mb-3">
                    All grading output will be saved to this folder. Leave empty to use default location.
                  </p>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={workspacePath}
                      onChange={(e) => setWorkspacePath(e.target.value)}
                      placeholder="e.g., /Users/you/Documents/MAT-144"
                      className="flex-1 px-4 py-3 bg-dark-700 border border-dark-500 rounded-lg text-dark-100 placeholder-dark-400 focus:outline-none focus:border-accent-blue transition-colors font-mono text-sm"
                    />
                    <button
                      onClick={handleBrowseWorkspace}
                      className="px-4 py-3 bg-dark-700 border border-dark-500 rounded-lg hover:border-dark-400 transition-colors"
                    >
                      <Folder className="w-5 h-5 text-dark-300" />
                    </button>
                  </div>
                  {workspacePath && (
                    <p className="text-accent-green text-xs mt-2 flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" />
                      Output will be saved to: {workspacePath}
                    </p>
                  )}
                </div>

                {/* Default Course Label */}
                <div>
                  <label className="block text-dark-200 text-sm font-medium mb-2">
                    Default Course Label
                  </label>
                  <p className="text-dark-400 text-sm mb-3">
                    Pre-fills the course label field when you start the app.
                  </p>
                  <input
                    type="text"
                    value={courseLabel}
                    onChange={(e) => setCourseLabel(e.target.value)}
                    placeholder="e.g., MAT-144-501"
                    className="w-full px-4 py-3 bg-dark-700 border border-dark-500 rounded-lg text-dark-100 placeholder-dark-400 focus:outline-none focus:border-accent-blue transition-colors"
                  />
                </div>
              </div>
              <div className="p-6 border-t border-dark-600 flex justify-end">
                <button
                  onClick={() => setShowSettings(false)}
                  className="px-6 py-2 bg-accent-blue hover:bg-blue-600 text-white rounded-lg font-medium transition-colors"
                >
                  Done
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Status card */}
        <div className="bg-dark-800 rounded-xl border border-dark-600 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <span className="text-dark-300 text-sm font-medium">Pipeline Status</span>
            <StatusBadge />
          </div>
          {state.status === 'running' && (
            <div className="mt-4">
              <p className="text-sm text-dark-200 mb-4">{state.current_step || 'Starting...'}</p>
              <ProgressSteps />
            </div>
          )}
          {state.status === 'completed' && (
            <p className="text-accent-green text-sm">✓ Grading complete! Output ready.</p>
          )}
          {state.status === 'cancelled' && (
            <p className="text-orange-400 text-sm">⊘ Pipeline cancelled by user.</p>
          )}
          {state.status === 'error' && (
            <p className="text-accent-red text-sm">✕ {state.error}</p>
          )}
        </div>

        {/* Drop zone */}
        <div
          {...getRootProps()}
          onDrop={handleNativeDrop}
          onDragOver={handleDragOver}
          className={`
            bg-dark-800 rounded-xl border-2 border-dashed p-8 mb-6 text-center cursor-pointer
            transition-all duration-200
            ${isDragActive ? 'border-accent-blue bg-accent-blue/5' : 'border-dark-500 hover:border-dark-400'}
          `}
        >
          <input {...getInputProps()} />
          <Upload className={`w-12 h-12 mx-auto mb-4 ${isDragActive ? 'text-accent-blue' : 'text-dark-400'}`} />
          {zipPath ? (
            <div>
              <p className="text-dark-100 font-medium mb-1">Selected file:</p>
              <p className="text-dark-300 text-sm font-mono truncate max-w-lg mx-auto">{zipPath}</p>
            </div>
          ) : (
            <div>
              <p className="text-dark-100 font-medium mb-1">Drop ZIP file here</p>
              <p className="text-dark-400 text-sm">or click to browse</p>
            </div>
          )}
        </div>

        {/* Course label input */}
        <div className="bg-dark-800 rounded-xl border border-dark-600 p-6 mb-6">
          <label className="block text-dark-300 text-sm font-medium mb-2">Course Label</label>
          <input
            type="text"
            value={courseLabel}
            onChange={(e) => setCourseLabel(e.target.value)}
            placeholder="e.g., MAT-144-501"
            className="w-full px-4 py-3 bg-dark-700 border border-dark-500 rounded-lg text-dark-100 placeholder-dark-400 focus:outline-none focus:border-accent-blue transition-colors"
          />
        </div>

        {/* Main action buttons */}
        <div className="flex gap-3">
          <button
            onClick={handleRunPipeline}
            disabled={!zipPath || !courseLabel || state.status === 'running'}
            className={`
              flex-1 py-4 rounded-xl font-semibold text-lg flex items-center justify-center gap-3
              transition-all duration-200
              ${!zipPath || !courseLabel || state.status === 'running'
                ? 'bg-dark-600 text-dark-400 cursor-not-allowed'
                : 'bg-accent-red hover:bg-accent-red-hover text-white shadow-lg shadow-accent-red/25'
              }
            `}
          >
            {state.status === 'running' ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                Run Pipeline
              </>
            )}
          </button>
          
          {/* Cancel button - only shown when running */}
          {state.status === 'running' && (
            <button
              onClick={handleCancel}
              className="px-6 py-4 rounded-xl font-semibold text-lg flex items-center justify-center gap-2 bg-orange-600 hover:bg-orange-700 text-white transition-all duration-200"
              title="Cancel the current grading operation"
            >
              <StopCircle className="w-5 h-5" />
              Cancel
            </button>
          )}
        </div>

        {/* Quick actions */}
        <div className="grid grid-cols-4 gap-3 mt-6">
          <button
            onClick={() => handleOpenFolder(state.output_path)}
            disabled={!state.output_path}
            className="flex flex-col items-center gap-2 p-4 bg-dark-800 rounded-xl border border-dark-600 hover:border-dark-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <FolderOpen className="w-5 h-5 text-dark-300" />
            <span className="text-sm text-dark-200">Output</span>
          </button>
          <button
            onClick={() => {/* TODO: Open student groups */}}
            disabled={!state.output_path}
            className="flex flex-col items-center gap-2 p-4 bg-dark-800 rounded-xl border border-dark-600 hover:border-dark-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Users className="w-5 h-5 text-dark-300" />
            <span className="text-sm text-dark-200">Groups</span>
          </button>
          <button
            onClick={handleCopyPath}
            disabled={!state.output_path}
            className="flex flex-col items-center gap-2 p-4 bg-dark-800 rounded-xl border border-dark-600 hover:border-dark-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Copy className="w-5 h-5 text-dark-300" />
            <span className="text-sm text-dark-200">Copy Path</span>
          </button>
          <button
            onClick={handleReset}
            disabled={state.status === 'running'}
            className="flex flex-col items-center gap-2 p-4 bg-dark-800 rounded-xl border border-dark-600 hover:border-dark-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <RefreshCw className="w-5 h-5 text-dark-300" />
            <span className="text-sm text-dark-200">Reset</span>
          </button>
        </div>

        {/* Logs section */}
        <div className="mt-6">
          <button
            onClick={() => setShowLogs(!showLogs)}
            className="flex items-center gap-2 text-dark-300 hover:text-dark-100 text-sm mb-2"
          >
            <ChevronDown className={`w-4 h-4 transition-transform ${showLogs ? 'rotate-180' : ''}`} />
            {showLogs ? 'Hide' : 'Show'} Logs ({state.logs.length})
          </button>
          {showLogs && (
            <div className="bg-dark-800 rounded-xl border border-dark-600 p-4 max-h-64 overflow-y-auto font-mono text-sm">
              {state.logs.length === 0 ? (
                <p className="text-dark-400">No logs yet.</p>
              ) : (
                state.logs.map((log, i) => (
                  <div key={i} className="text-dark-200 py-0.5">{log}</div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
