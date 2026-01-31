# Interactive Tutorial Slides

An interactive web-based tutorial platform for teaching LLM API fundamentals and building data analysis tools with Streamlit.

## Overview

This project provides an interactive learning experience for the HAI2026 course tutorial on building data analysis tools with LLM APIs. Students can:

- Navigate through 19 tutorial sections step-by-step
- View code snapshots with diff highlighting showing incremental changes
- See "How to Run" instructions and expected outputs for each section
- Follow along with the tutorial content in an intuitive 3-column layout

## Features

### 📚 Tutorial Navigation
- **Collapsible Sidebar**: Browse all 19 tutorial sections with section numbers and titles
- **Visual Indicators**: Green dots for new files, blue dots for modified files in code tabs
- **Progressive Learning**: Each section builds upon the previous one

### 💻 Code Viewer
- **Multi-file Support**: View multiple files per section with tab navigation
- **Diff Highlighting**: See exactly what changed from the previous section
- **Syntax Highlighting**: Code displayed with VS Code-style syntax highlighting
- **File Status Badges**: NEW/MODIFIED badges for easy tracking

### 📖 Content Viewer
- **Markdown Support**: Rich tutorial content with code examples and explanations
- **Clear Structure**: Well-organized sections with headings and bullet points

### 🔧 Bottom Panel (VS Code Terminal Style)
- **Compact Design**: Terminal-like interface for execution details
- **Two Tabs**:
  - **How to Run**: Step-by-step execution instructions
  - **Expected Output**: Actual execution results from running the code
- **Resizable**: Drag the handle to adjust panel height (10%-70%)

## Project Structure

```
interactive-slides/
├── src/
│   ├── components/
│   │   ├── Sidebar.jsx/css          # Collapsible navigation sidebar
│   │   ├── CodeViewer.jsx/css       # Code display with diff highlighting
│   │   ├── ContentViewer.jsx/css    # Tutorial content display
│   │   └── BottomPanel.jsx/css      # How to Run + Expected Output tabs
│   ├── data/
│   │   ├── sections.js              # Main data loader (uses Vite glob imports)
│   │   ├── sections-meta.js         # Tutorial metadata (19 sections)
│   │   └── snapshots/               # Code snapshots for each section
│   │       ├── 01-intro/
│   │       ├── 02-setup/
│   │       ├── ...
│   │       └── 19-complete-integration/
│   ├── App.jsx                      # Main app layout
│   └── index.jsx                    # Entry point
└── package.json
```

## Tutorial Sections

### Part 1: API Fundamentals
1. Introduction
2. Setup: Install Dependencies
3. Your First API Call
4. Experimenting with Temperature
5. Counting Tokens
6. Estimating API Costs

### Part 2: Structured Outputs
7. The Problem with Free-Form Text
8. The Solution: Pydantic Models

### Part 3: Prompt Chaining
9. Single Step Problem
10. Step 1: Generate Code
11. Step 2: Execute Code
12. Step 3: Interpret Result

### Part 4: Streamlit Crash Course
13. Streamlit Installation
14. Streamlit Basics: Display & Input
15. Streamlit Layout: Sidebar & Columns

### Part 5: Building the Data Filtering Interface
16. Load Data & Column Selection
17. Add Row Filters
18. Add Question Input & Layout

### Part 6: Complete Integration
19. Connecting to the LLM Pipeline

## Getting Started

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn

### Installation

```bash
# Clone the repository
cd interactive-slides

# Install dependencies
npm install

# Start the development server
npm run dev
```

The application will open at `http://localhost:5173` (or the next available port).

### Building for Production

```bash
npm run build
```

## Technology Stack

- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **react-markdown**: Markdown rendering with GitHub-flavored markdown support
- **react-syntax-highlighter**: Code syntax highlighting with Prism themes
- **diff**: File comparison and diff generation
- **CSS**: Custom styling with VS Code-inspired dark theme

## Key Features Explained

### File-Based Code Snapshots
Instead of hardcoding code strings, each tutorial section has a dedicated folder in `src/data/snapshots/` containing actual files:
- `app.py` - Main Python code
- `requirements.txt` - Python dependencies
- `.env` - Environment variables
- Additional files as needed (CSV files, etc.)

This approach:
- Avoids template literal escaping issues
- Makes code easier to maintain and update
- Provides realistic file structure for students

### Vite Glob Imports
The project uses Vite's `import.meta.glob` to automatically load all snapshot files:

```javascript
const modules = import.meta.glob('./snapshots/**/*', {
  query: '?raw',
  eager: true
});
```

This allows for dynamic loading without manual imports.

### Diff Highlighting
The `diff` library compares consecutive snapshots and highlights:
- **Added lines**: Green background with left border
- **Removed lines**: Hidden (not shown in this view)
- **Unchanged lines**: Normal display

### Resizable Bottom Panel
Users can drag the resize handle to adjust the bottom panel height between 10% and 70% of the viewport.

## Development Notes

### Adding New Sections

1. Create a new snapshot folder in `src/data/snapshots/`
2. Add the necessary files (app.py, requirements.txt, etc.)
3. Update `sections-meta.js` with the new section metadata:
   - `id`: Section identifier
   - `title`: Section title
   - `content`: Tutorial content (markdown)
   - `howToRun`: Execution instructions (markdown)
   - `expectedOutput`: Expected output (in code blocks)

### Code Block Format for Expected Output

All expected outputs should follow this format:

```javascript
expectedOutput: `\`\`\`
[actual terminal/execution output]
\`\`\`

Note: [optional explanatory notes]`
```

### Installation Instructions Format

Use consistent format for pip installation:

```
Install via requirements.txt OR pip install [packages]
```

## License

This project is part of the HAI2026 course materials.

## Acknowledgments

Based on the tutorial "Building an Interactive Data Analysis Tool" which teaches:
- OpenAI API integration
- Structured outputs with Pydantic
- Prompt chaining techniques
- Building hybrid UI with Streamlit
