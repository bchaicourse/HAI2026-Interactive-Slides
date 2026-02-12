import { useState, useEffect } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { prism } from 'react-syntax-highlighter/dist/esm/styles/prism';
import * as Diff from 'diff';
import JSZip from 'jszip';
import './CodeViewer.css';

function CodeViewer({ currentSection, prevSection, selectedFile, onFileSelect, diffMode = 'current', label }) {
  // Filter out markdown files that start with __ (metadata files)
  const files = Object.keys(currentSection.codeSnapshot).filter(
    filename => !filename.startsWith('__')
  );
  const [activeFile, setActiveFile] = useState(files[0] || null);
  const [copied, setCopied] = useState(false);

  // Use selectedFile from props when available (for syncing multiple CodeViewers)
  const effectiveFile = (selectedFile && files.includes(selectedFile)) ? selectedFile : activeFile;

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

  const handleCopyFile = async () => {
    await navigator.clipboard.writeText(currentCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const handleDownloadZip = async () => {
    const zip = new JSZip();
    for (const [filename, content] of Object.entries(currentSection.codeSnapshot)) {
      if (!filename.startsWith('__')) {
        zip.file(filename, content);
      }
    }
    const blob = await zip.generateAsync({ type: 'blob' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentSection.id}.zip`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const currentCode = currentSection.codeSnapshot[effectiveFile] || '';
  const prevCode = prevSection?.codeSnapshot?.[effectiveFile] || '';

  // Calculate diff
  const diffResult = Diff.diffLines(prevCode, currentCode);

  const renderDiffCode = () => {
    // In 'previous' mode with no previous section, show empty state
    if (diffMode === 'previous' && !prevSection) {
      return (
        <div className="empty-state">
          <p>No previous version</p>
        </div>
      );
    }

    if (!prevSection || prevCode === currentCode) {
      // No diff needed - show plain code
      const codeToShow = diffMode === 'previous' ? prevCode : currentCode;
      return (
        <SyntaxHighlighter
          language={getLanguageFromFilename(effectiveFile)}
          style={prism}
          showLineNumbers={false}
          customStyle={{
            margin: 0,
            borderRadius: 0,
            background: '#ffffff',
          }}
        >
          {codeToShow}
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

          if (diffMode === 'previous') {
            // Previous mode: show removed (red), hide added
            if (part.added) return null;
          } else {
            // Current mode (default): show added (green), hide removed
            if (part.removed) return null;
          }

          return (
            <div key={index} className={className}>
              <SyntaxHighlighter
                language={getLanguageFromFilename(effectiveFile)}
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

    const prev = prevSection.codeSnapshot?.[filename] || '';
    const curr = currentSection.codeSnapshot[filename] || '';

    if (!prev && curr) {
      return 'new';
    }
    if (prev && curr && prev !== curr) {
      return 'modified';
    }
    return null;
  };

  const getFileBadge = () => {
    const status = getFileStatus(effectiveFile);
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
          <button className="code-action-btn" onClick={handleDownloadZip} title="Download all files as .zip">
            Download All
          </button>
        </div>
        <div className="file-items">
          {files.map((file) => {
            const status = getFileStatus(file);
            return (
              <button
                key={file}
                className={`file-item ${effectiveFile === file ? 'active' : ''} ${status ? `file-${status}` : ''}`}
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
            {label && <span className="code-viewer-label">{label}</span>}
            <span>{effectiveFile}</span>
            {getFileBadge()}
          </div>
          <div className="code-actions">
            <button className="code-action-btn" onClick={handleCopyFile} title="Copy file">
              {copied ? 'Copied!' : 'Copy'}
            </button>
          </div>
        </div>
        <div className="code-body">{renderDiffCode()}</div>
      </div>
    </div>
  );
}

export default CodeViewer;
