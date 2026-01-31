// Main sections data structure
// Combines metadata with code snapshots loaded from files

import { sectionsMeta } from './sections-meta.js';

// Import all files from snapshots directories using Vite's glob import
// This automatically loads all files and makes them available as modules
const modules = import.meta.glob('./snapshots/**/*', {
  query: '?raw',
  eager: true
});

// Separately import .env files since glob doesn't include hidden files by default
const envModules = import.meta.glob('./snapshots/**/.env', {
  query: '?raw',
  eager: true
});

// Import markdown files for content, how to run, and expected output
const markdownModules = import.meta.glob('./snapshots/**/__*.md', {
  query: '?raw',
  eager: true
});

// Import screenshot images from __screenshots/ folders
const screenshotModules = import.meta.glob('./snapshots/**/__screenshots/**/*.{png,jpg,jpeg,gif,webp}', {
  eager: true
});

// Helper function to extract snapshot ID from file path
function getSnapshotId(path) {
  const match = path.match(/snapshots\/([^/]+)\//);
  return match ? match[1] : null;
}

// Helper function to extract filename from path
function getFilename(path) {
  const parts = path.split('/');
  return parts[parts.length - 1];
}

// Build code snapshots by grouping files by snapshot ID
const codeSnapshots = {};

// Process regular files
Object.keys(modules).forEach(path => {
  const snapshotId = getSnapshotId(path);
  const filename = getFilename(path);

  // Skip generated_code.py and temp_data.csv files
  if (filename === 'generated_code.py' || filename === 'temp_data.csv') {
    return;
  }

  // Skip files from __screenshots/ directory
  if (path.includes('__screenshots/')) {
    return;
  }

  if (snapshotId && filename) {
    if (!codeSnapshots[snapshotId]) {
      codeSnapshots[snapshotId] = {};
    }
    codeSnapshots[snapshotId][filename] = modules[path].default || '';
  }
});

// Process .env files separately
Object.keys(envModules).forEach(path => {
  const snapshotId = getSnapshotId(path);
  const filename = getFilename(path);

  if (snapshotId && filename) {
    if (!codeSnapshots[snapshotId]) {
      codeSnapshots[snapshotId] = {};
    }
    codeSnapshots[snapshotId][filename] = envModules[path].default || '';
  }
});

// Build markdown content by snapshot ID
const markdownContent = {};

Object.keys(markdownModules).forEach(path => {
  const snapshotId = getSnapshotId(path);
  const filename = getFilename(path);

  if (snapshotId && filename) {
    if (!markdownContent[snapshotId]) {
      markdownContent[snapshotId] = {};
    }

    // Map markdown files to their corresponding fields
    if (filename === '__content.md') {
      markdownContent[snapshotId].content = markdownModules[path].default || '';
    } else if (filename === '__how_to_run.md') {
      markdownContent[snapshotId].howToRun = markdownModules[path].default || '';
    } else if (filename === '__expected_output.md') {
      markdownContent[snapshotId].expectedOutput = markdownModules[path].default || '';
    }
  }
});

// Build screenshots by snapshot ID
const screenshots = {};

Object.keys(screenshotModules).forEach(path => {
  const snapshotId = getSnapshotId(path);
  const filename = getFilename(path);

  if (snapshotId && filename) {
    if (!screenshots[snapshotId]) {
      screenshots[snapshotId] = [];
    }

    // Add screenshot with its URL and filename
    screenshots[snapshotId].push({
      url: screenshotModules[path].default,
      filename: filename
    });
  }
});

// Combine metadata with code snapshots and markdown content
export const sections = sectionsMeta.map(meta => ({
  ...meta,
  content: markdownContent[meta.id]?.content || meta.content || '',
  howToRun: markdownContent[meta.id]?.howToRun || meta.howToRun || null,
  expectedOutput: markdownContent[meta.id]?.expectedOutput || meta.expectedOutput || null,
  codeSnapshot: codeSnapshots[meta.id] || {},
  screenshots: screenshots[meta.id] || []
}));
