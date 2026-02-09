// Main data loader
// Combines lecture metadata with code snapshots loaded from files

import { lectures as lecturesMeta } from './lectures-meta.js';

// Import all files from lecture snapshot directories using Vite's glob import
const modules = import.meta.glob('./lectures/*/snapshots/**/*', {
  query: '?raw',
  eager: true
});

// Separately import .env files since glob doesn't include hidden files by default
const envModules = import.meta.glob('./lectures/*/snapshots/**/.env', {
  query: '?raw',
  eager: true
});

// Import markdown files for content, how to run, and expected output
const markdownModules = import.meta.glob('./lectures/*/snapshots/**/__*.md', {
  query: '?raw',
  eager: true
});

// Import screenshot images from __screenshots/ folders
const screenshotModules = import.meta.glob('./lectures/*/snapshots/**/__screenshots/**/*.{png,jpg,jpeg,gif,webp}', {
  eager: true
});

// Helper function to extract lecture ID and snapshot ID from file path
function parsePath(path) {
  const match = path.match(/lectures\/([^/]+)\/snapshots\/([^/]+)\//);
  return match ? { lectureId: match[1], snapshotId: match[2] } : null;
}

// Helper function to extract filename from path
function getFilename(path) {
  const parts = path.split('/');
  return parts[parts.length - 1];
}

// Build code snapshots grouped by lecture and snapshot
const codeSnapshots = {};

// Process regular files
Object.keys(modules).forEach(path => {
  const parsed = parsePath(path);
  const filename = getFilename(path);

  // Skip generated_code.py and temp_data.csv files
  if (filename === 'generated_code.py' || filename === 'temp_data.csv') {
    return;
  }

  // Skip files from __screenshots/ directory
  if (path.includes('__screenshots/')) {
    return;
  }

  if (parsed && filename) {
    if (!codeSnapshots[parsed.lectureId]) {
      codeSnapshots[parsed.lectureId] = {};
    }
    if (!codeSnapshots[parsed.lectureId][parsed.snapshotId]) {
      codeSnapshots[parsed.lectureId][parsed.snapshotId] = {};
    }
    codeSnapshots[parsed.lectureId][parsed.snapshotId][filename] = modules[path].default || '';
  }
});

// Process .env files separately
Object.keys(envModules).forEach(path => {
  const parsed = parsePath(path);
  const filename = getFilename(path);

  if (parsed && filename) {
    if (!codeSnapshots[parsed.lectureId]) {
      codeSnapshots[parsed.lectureId] = {};
    }
    if (!codeSnapshots[parsed.lectureId][parsed.snapshotId]) {
      codeSnapshots[parsed.lectureId][parsed.snapshotId] = {};
    }
    codeSnapshots[parsed.lectureId][parsed.snapshotId][filename] = envModules[path].default || '';
  }
});

// Build markdown content by lecture and snapshot
const markdownContent = {};

Object.keys(markdownModules).forEach(path => {
  const parsed = parsePath(path);
  const filename = getFilename(path);

  if (parsed && filename) {
    if (!markdownContent[parsed.lectureId]) {
      markdownContent[parsed.lectureId] = {};
    }
    if (!markdownContent[parsed.lectureId][parsed.snapshotId]) {
      markdownContent[parsed.lectureId][parsed.snapshotId] = {};
    }

    // Map markdown files to their corresponding fields
    if (filename === '__content.md') {
      markdownContent[parsed.lectureId][parsed.snapshotId].content = markdownModules[path].default || '';
    } else if (filename === '__how_to_run.md') {
      markdownContent[parsed.lectureId][parsed.snapshotId].howToRun = markdownModules[path].default || '';
    } else if (filename === '__expected_output.md') {
      markdownContent[parsed.lectureId][parsed.snapshotId].expectedOutput = markdownModules[path].default || '';
    }
  }
});

// Build screenshots by lecture and snapshot
const screenshots = {};

Object.keys(screenshotModules).forEach(path => {
  const parsed = parsePath(path);
  const filename = getFilename(path);

  if (parsed && filename) {
    if (!screenshots[parsed.lectureId]) {
      screenshots[parsed.lectureId] = {};
    }
    if (!screenshots[parsed.lectureId][parsed.snapshotId]) {
      screenshots[parsed.lectureId][parsed.snapshotId] = [];
    }

    screenshots[parsed.lectureId][parsed.snapshotId].push({
      url: screenshotModules[path].default,
      filename: filename
    });
  }
});

// Combine metadata with code snapshots and markdown content
export const lectures = lecturesMeta.map(lecture => ({
  ...lecture,
  sections: lecture.sections.map(meta => ({
    ...meta,
    content: markdownContent[lecture.id]?.[meta.id]?.content || '',
    howToRun: markdownContent[lecture.id]?.[meta.id]?.howToRun || null,
    expectedOutput: markdownContent[lecture.id]?.[meta.id]?.expectedOutput || null,
    codeSnapshot: codeSnapshots[lecture.id]?.[meta.id] || {},
    screenshots: screenshots[lecture.id]?.[meta.id] || []
  }))
}));
