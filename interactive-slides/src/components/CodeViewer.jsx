import { useState, useEffect } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { prism } from 'react-syntax-highlighter/dist/esm/styles/prism';
import * as Diff from 'diff';
import './CodeViewer.css';

function CodeViewer({ currentSection, prevSection, selectedFile, onFileSelect }) {
  // Filter out markdown files that start with __ (metadata files)
  const files = Object.keys(currentSection.codeSnapshot).filter(
    filename => !filename.startsWith('__')
  );
  const [activeFile, setActiveFile] = useState(files[0] || null);

  // Reset active file when section changes
  useEffect(() => {
    const newFiles = Object.keys(currentSection.codeSnapshot).filter(
      filename => !filename.startsWith('__')
    );
    if (newFiles.length > 0) {
      setActiveFile(newFiles[0]);
      onFileSelect(newFiles[0]);
    }
  }, [currentSection.id]);

  const handleFileClick = (file) => {
    setActiveFile(file);
    onFileSelect(file);
  };

  const currentCode = currentSection.codeSnapshot[activeFile] || '';
  const prevCode = prevSection?.codeSnapshot?.[activeFile] || '';

  // Calculate diff
  const diffResult = Diff.diffLines(prevCode, currentCode);

  const renderDiffCode = () => {
    if (!prevSection || prevCode === currentCode) {
      // No diff needed - show plain code
      return (
        <SyntaxHighlighter
          language={getLanguageFromFilename(activeFile)}
          style={prism}
          showLineNumbers={false}
          customStyle={{
            margin: 0,
            borderRadius: 0,
            background: '#ffffff',
          }}
        >
          {currentCode}
        </SyntaxHighlighter>
      );
    }

    // Show diff highlighting
    return (
      <div className="diff-viewer">
        {diffResult.map((part, index) => {
          const className = part.added
            ? 'diff-added'
            : part.removed
            ? 'diff-removed'
            : 'diff-unchanged';

          if (part.removed) return null; // Don't show removed lines in this view

          return (
            <div key={index} className={className}>
              <SyntaxHighlighter
                language={getLanguageFromFilename(activeFile)}
                style={prism}
                showLineNumbers={false}
                customStyle={{
                  margin: 0,
                  padding: '2px 10px',
                  background: 'transparent',
                  fontSize: '14px',
                }}
                wrapLines={true}
                lineProps={{ style: { whiteSpace: 'pre-wrap' } }}
              >
                {part.value}
              </SyntaxHighlighter>
            </div>
          );
        })}
      </div>
    );
  };

  const getLanguageFromFilename = (filename) => {
    if (!filename) return 'text';
    if (filename.endsWith('.py')) return 'python';
    if (filename.endsWith('.txt')) return 'text';
    if (filename.endsWith('.csv')) return 'csv';
    if (filename.endsWith('.env')) return 'bash';
    return 'text';
  };

  const getFileStatus = (filename) => {
    if (!prevSection) return null;

    const prevCode = prevSection.codeSnapshot?.[filename] || '';
    const currentCode = currentSection.codeSnapshot[filename] || '';

    if (!prevCode && currentCode) {
      return 'new';
    }
    if (prevCode && currentCode && prevCode !== currentCode) {
      return 'modified';
    }
    return null;
  };

  const getFileBadge = () => {
    const status = getFileStatus(activeFile);
    if (!status) return null;

    if (status === 'new') {
      return <span className="file-badge new">NEW</span>;
    }
    if (status === 'modified') {
      return <span className="file-badge modified">MODIFIED</span>;
    }
    return null;
  };

  if (files.length === 0) {
    return (
      <div className="code-viewer">
        <div className="empty-state">
          <p>No code files in this section yet.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="code-viewer">
      <div className="file-list">
        <div className="file-list-header">
          <h3>Files</h3>
        </div>
        <div className="file-items">
          {files.map((file) => {
            const status = getFileStatus(file);
            return (
              <button
                key={file}
                className={`file-item ${activeFile === file ? 'active' : ''} ${status ? `file-${status}` : ''}`}
                onClick={() => handleFileClick(file)}
              >
                {status && <span className={`status-indicator ${status}`}></span>}
                <span className="file-name">{file}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div className="code-content">
        <div className="code-header">
          <div className="code-filename">
            <span>{activeFile}</span>
            {getFileBadge()}
          </div>
        </div>
        <div className="code-body">{renderDiffCode()}</div>
      </div>
    </div>
  );
}

export default CodeViewer;
