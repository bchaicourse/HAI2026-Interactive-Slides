# HAI2026 Interactive Tutorial Slides

An interactive web application that presents a step-by-step tutorial for building a data analysis tool. Students can navigate through different sections, view code changes with diff highlighting, and read the educational content side-by-side.

## Features

- **Section Navigation**: Sidebar for easy navigation between tutorial parts
- **Code Viewer with Diff**: View complete code at each step with highlighted changes from the previous section
- **File Browser**: See all project files for each section
- **Content Viewer**: Rich markdown rendering of tutorial content
- **Responsive Design**: Works on desktop and mobile devices

## Structure

```
interactive-slides/
├── src/
│   ├── components/
│   │   ├── Sidebar.jsx          # Section navigation
│   │   ├── Sidebar.css
│   │   ├── CodeViewer.jsx       # Code display with diff highlighting
│   │   ├── CodeViewer.css
│   │   ├── ContentViewer.jsx    # Markdown content renderer
│   │   └── ContentViewer.css
│   ├── data/
│   │   └── sections.js          # Tutorial sections data
│   ├── App.jsx                  # Main application
│   ├── App.css
│   └── index.css
└── reference-code/              # Original tutorial files
```

## Getting Started

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn

### Installation

1. Navigate to the project directory:
   ```bash
   cd interactive-slides
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open your browser to `http://localhost:5173` (or the port shown in terminal)

## How It Works

### Data Structure

Each section in `src/data/sections.js` contains:

- `id`: Unique identifier
- `title`: Section title shown in sidebar
- `content`: Markdown content (tutorial text)
- `codeSnapshot`: Complete code state at this point in the tutorial

### Diff Highlighting

The CodeViewer component compares code between sections using the `diff` library:

- **Green highlight**: New or modified lines
- **No highlight**: Unchanged code
- **Badges**: "NEW" for new files, "MODIFIED" for changed files

### Adding New Sections

To add a new tutorial section:

1. Open `src/data/sections.js`
2. Add a new object to the `sections` array:

```javascript
{
  id: 'new-section',
  title: 'New Section Title',
  content: `# Your markdown content here`,
  codeSnapshot: {
    'file1.py': 'complete code content',
    'file2.txt': 'other file content'
  }
}
```

## Technologies Used

- **React**: UI framework
- **Vite**: Build tool and dev server
- **react-markdown**: Markdown rendering
- **react-syntax-highlighter**: Code syntax highlighting
- **diff**: Text diffing algorithm
- **Prism.js**: Syntax highlighting themes

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Deployment

You can deploy the built application to any static hosting service:

- GitHub Pages
- Netlify
- Vercel
- AWS S3 + CloudFront

## Customization

### Changing Color Scheme

Edit the CSS files in `src/components/` to change colors:

- Sidebar: `Sidebar.css`
- Code viewer: `CodeViewer.css`
- Content: `ContentViewer.css`

### Using Different Syntax Highlighting Theme

In `CodeViewer.jsx` and `ContentViewer.jsx`, import a different theme from `react-syntax-highlighter`:

```javascript
import { dracula } from 'react-syntax-highlighter/dist/esm/styles/prism';
```

## License

MIT

## Reference

Based on the tutorial: "Building an Interactive Data Analysis Tool (Part 1)"
Original code available in `reference-code/` directory.
