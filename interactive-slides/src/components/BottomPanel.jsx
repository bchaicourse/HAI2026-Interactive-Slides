import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import './BottomPanel.css';

function BottomPanel({ howToRun, expectedOutput, screenshots }) {
  const [activeTab, setActiveTab] = useState('howToRun');

  const renderMarkdown = (text) => (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '');
          return !inline && match ? (
            <SyntaxHighlighter
              style={vscDarkPlus}
              language={match[1]}
              PreTag="div"
              {...props}
            >
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
          ) : (
            <code className={className} {...props}>
              {children}
            </code>
          );
        },
      }}
    >
      {text}
    </ReactMarkdown>
  );

  // Check if expectedOutput should be rendered as terminal output
  const isTerminalOutput = (text) => {
    if (!text) return false;
    // If it starts with a code block or contains common terminal output patterns
    return text.includes('```') ||
           text.match(/^[A-Za-z0-9_\-\.]+:/m) || // "something:"
           text.match(/^\$\s/m) || // "$ command"
           !text.includes('**'); // If no markdown bold, it's likely plain output
  };

  const renderTerminalOutput = (text) => {
    // Remove markdown code blocks and render as plain terminal text
    const cleanedText = text
      .replace(/```[a-z]*\n/g, '')
      .replace(/```/g, '')
      .trim();

    return <div className="tab-content terminal-output">{cleanedText}</div>;
  };

  if (!howToRun && !expectedOutput && (!screenshots || screenshots.length === 0)) {
    return null;
  }

  return (
    <div className="bottom-panel">
      <div className="bottom-panel-tabs">
        {howToRun && (
          <button
            className={`tab-button ${activeTab === 'howToRun' ? 'active' : ''}`}
            onClick={() => setActiveTab('howToRun')}
          >
            How to Run
          </button>
        )}
        {expectedOutput && (
          <button
            className={`tab-button ${activeTab === 'expectedOutput' ? 'active' : ''}`}
            onClick={() => setActiveTab('expectedOutput')}
          >
            Expected Output
          </button>
        )}
        {screenshots && screenshots.length > 0 && (
          <button
            className={`tab-button ${activeTab === 'screenshots' ? 'active' : ''}`}
            onClick={() => setActiveTab('screenshots')}
          >
            Screenshots
          </button>
        )}
      </div>
      <div className="bottom-panel-content">
        {activeTab === 'howToRun' && howToRun && (
          <div className="tab-content">
            {renderMarkdown(howToRun)}
          </div>
        )}
        {activeTab === 'expectedOutput' && expectedOutput && (
          isTerminalOutput(expectedOutput)
            ? renderTerminalOutput(expectedOutput)
            : <div className="tab-content">{renderMarkdown(expectedOutput)}</div>
        )}
        {activeTab === 'screenshots' && screenshots && screenshots.length > 0 && (
          <div className="tab-content screenshots-container">
            {screenshots.map((screenshot, index) => (
              <div key={index} className="screenshot-item">
                <img
                  src={screenshot.url}
                  alt={screenshot.filename}
                  style={{
                    maxWidth: '100%',
                    height: 'auto',
                    borderRadius: '8px',
                    border: '1px solid #e1e4e8',
                    marginBottom: '16px'
                  }}
                />
                <p style={{ fontSize: '0.9em', color: '#666', marginTop: '-8px', marginBottom: '16px' }}>
                  {screenshot.filename}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default BottomPanel;
