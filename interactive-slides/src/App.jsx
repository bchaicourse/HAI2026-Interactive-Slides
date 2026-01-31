import { useState, useRef, useEffect } from 'react';
import './App.css';
import { sections } from './data/sections';
import Sidebar from './components/Sidebar';
import CodeViewer from './components/CodeViewer';
import ContentViewer from './components/ContentViewer';
import BottomPanel from './components/BottomPanel';

function App() {
  const [currentSectionId, setCurrentSectionId] = useState(sections[0].id);
  const [selectedFile, setSelectedFile] = useState(null);
  const [bottomHeight, setBottomHeight] = useState(30); // percentage
  const [isDragging, setIsDragging] = useState(false);
  const [mobileTab, setMobileTab] = useState('content'); // 'code', 'content', 'info'
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const containerRef = useRef(null);

  const currentSection = sections.find(s => s.id === currentSectionId);
  const prevSection = sections[sections.findIndex(s => s.id === currentSectionId) - 1];

  const handleMouseDown = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isDragging || !containerRef.current) return;

      const containerRect = containerRef.current.getBoundingClientRect();
      const containerHeight = containerRect.height;
      const mouseY = e.clientY - containerRect.top;
      const newBottomHeight = ((containerHeight - mouseY) / containerHeight) * 100;

      // Constrain between 10% and 70%
      const clampedHeight = Math.min(Math.max(newBottomHeight, 10), 70);
      setBottomHeight(clampedHeight);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  const hasBottomPanel = currentSection.howToRun || currentSection.expectedOutput || (currentSection.screenshots && currentSection.screenshots.length > 0);

  return (
    <div className="app">
      {/* Mobile hamburger button */}
      <button className="mobile-menu-btn" onClick={() => setSidebarOpen(!sidebarOpen)}>
        ☰
      </button>

      {/* Sidebar with mobile drawer */}
      <div className={`sidebar-wrapper ${sidebarOpen ? 'open' : ''}`}>
        <Sidebar
          sections={sections}
          currentSectionId={currentSectionId}
          onSectionChange={(id) => {
            setCurrentSectionId(id);
            setSidebarOpen(false);
          }}
        />
      </div>

      {/* Overlay for mobile drawer */}
      {sidebarOpen && <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)}></div>}

      <div className="main-content" ref={containerRef}>
        {/* Mobile tab navigation */}
        <div className="mobile-tabs">
          <button
            className={`mobile-tab ${mobileTab === 'content' ? 'active' : ''}`}
            onClick={() => setMobileTab('content')}
          >
            Content
          </button>
          <button
            className={`mobile-tab ${mobileTab === 'code' ? 'active' : ''}`}
            onClick={() => setMobileTab('code')}
          >
            Code
          </button>
          {hasBottomPanel && (
            <button
              className={`mobile-tab ${mobileTab === 'info' ? 'active' : ''}`}
              onClick={() => setMobileTab('info')}
            >
              Info
            </button>
          )}
        </div>

        {/* Desktop layout */}
        <div
          className="top-panels desktop-only"
          style={{
            height: hasBottomPanel ? `${100 - bottomHeight}%` : '100%',
          }}
        >
          <div className="column code-column">
            <CodeViewer
              currentSection={currentSection}
              prevSection={prevSection}
              selectedFile={selectedFile}
              onFileSelect={setSelectedFile}
            />
          </div>

          <div className="column content-column">
            <ContentViewer section={currentSection} />
          </div>
        </div>

        {/* Mobile tab content */}
        <div className="mobile-tab-content">
          {mobileTab === 'code' && (
            <div className="mobile-panel">
              <CodeViewer
                currentSection={currentSection}
                prevSection={prevSection}
                selectedFile={selectedFile}
                onFileSelect={setSelectedFile}
              />
            </div>
          )}
          {mobileTab === 'content' && (
            <div className="mobile-panel">
              <ContentViewer section={currentSection} />
            </div>
          )}
          {mobileTab === 'info' && hasBottomPanel && (
            <div className="mobile-panel">
              <BottomPanel
                howToRun={currentSection.howToRun}
                expectedOutput={currentSection.expectedOutput}
                screenshots={currentSection.screenshots}
              />
            </div>
          )}
        </div>

        {/* Desktop bottom panel */}
        {hasBottomPanel && (
          <>
            <div
              className={`resize-handle desktop-only ${isDragging ? 'dragging' : ''}`}
              onMouseDown={handleMouseDown}
            >
              <div className="resize-handle-line"></div>
            </div>
            <div
              className="bottom-panel-wrapper desktop-only"
              style={{
                height: `${bottomHeight}%`,
              }}
            >
              <BottomPanel
                howToRun={currentSection.howToRun}
                expectedOutput={currentSection.expectedOutput}
                screenshots={currentSection.screenshots}
              />
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
