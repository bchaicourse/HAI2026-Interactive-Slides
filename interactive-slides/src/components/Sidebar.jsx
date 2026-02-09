import { useState } from 'react';
import './Sidebar.css';

function Sidebar({ lectures, currentLectureId, onLectureChange, sections, currentSectionId, onSectionChange }) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const currentLecture = lectures.find(l => l.id === currentLectureId);

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
        <h2>{currentLecture.title}</h2>
        <button
          className="collapse-btn"
          onClick={() => setIsCollapsed(!isCollapsed)}
          aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? '→' : '←'}
        </button>
      </div>

      {!isCollapsed && lectures.length > 1 && (
        <div className="lecture-tabs">
          {lectures.map((lecture, index) => (
            <button
              key={lecture.id}
              className={`lecture-tab ${currentLectureId === lecture.id ? 'active' : ''}`}
              onClick={() => onLectureChange(lecture.id)}
            >
              Lecture {index + 1}
            </button>
          ))}
        </div>
      )}

      <nav className="sidebar-nav">
        {Object.keys(groupedSections).map((part) => (
          <div key={part} className="sidebar-part">
            {!isCollapsed && (
              <div className="part-header">
                Part {part}: {currentLecture.parts[part]}
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
