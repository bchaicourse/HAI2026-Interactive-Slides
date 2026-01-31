import { useState } from 'react';
import './Sidebar.css';
import { partTitles } from '../data/sections-meta.js';

function Sidebar({ sections, currentSectionId, onSectionChange }) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  // Group sections by part
  const groupedSections = sections.reduce((acc, section, index) => {
    const part = section.part || 1;
    if (!acc[part]) {
      acc[part] = [];
    }
    acc[part].push({ ...section, globalIndex: index });
    return acc;
  }, {});

  return (
    <div className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        <h2>Building an Interactive Data Analysis Tool</h2>
        <button
          className="collapse-btn"
          onClick={() => setIsCollapsed(!isCollapsed)}
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? '→' : '←'}
        </button>
      </div>
      <nav className="sidebar-nav">
        {Object.keys(groupedSections).map((part) => (
          <div key={part} className="sidebar-part">
            {!isCollapsed && (
              <div className="part-header">
                Part {part}: {partTitles[part]}
              </div>
            )}
            {groupedSections[part].map((section) => (
              <button
                key={section.id}
                className={`sidebar-item ${currentSectionId === section.id ? 'active' : ''}`}
                onClick={() => onSectionChange(section.id)}
                title={isCollapsed ? section.title : ''}
              >
                <span className="section-number">{section.globalIndex + 1}</span>
                <span className="section-title">{section.title}</span>
              </button>
            ))}
          </div>
        ))}
      </nav>
    </div>
  );
}

export default Sidebar;
