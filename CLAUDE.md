# Project Structure

```
interactive-slides/src/data/
  lectures-meta.js              # Lecture/section metadata
  sections.js                   # Data loader (Vite glob imports)
  lectures/
    lecture1/
      snapshots/
        01-setup/
        02-first-api-call/
        ...
    lecture2/
      snapshots/
        01-starting-point/
        ...
```

## How to Add a New Section

1. Create a snapshot directory under the target lecture:
   `src/data/lectures/<lectureN>/snapshots/<NN>-<slug>/`

2. Add files inside the directory:
   - **Code files**: `app.py`, `requirements.txt`, `.env`, etc. (displayed in CodeViewer)
   - `__content.md`: Main tutorial content (displayed in ContentViewer)
   - `__how_to_run.md`: Execution instructions (optional, displayed in BottomPanel)
   - `__expected_output.md`: Expected terminal output (optional, displayed in BottomPanel)
   - `__screenshots/`: Screenshot images (optional, displayed in BottomPanel)

3. Register the section in `src/data/lectures-meta.js`:
   ```js
   { id: '<NN>-<slug>', title: 'Section Title', part: <partNumber> }
   ```

Files prefixed with `__` are metadata (not shown in CodeViewer). Everything else is treated as code and displayed with diff highlighting against the previous section.

## How to Add a New Lecture

1. Create `src/data/lectures/<lectureN>/snapshots/`
2. Add at least one snapshot directory (e.g., `01-starting-point/`)
3. Add a new entry in the `lectures` array in `lectures-meta.js`:
   ```js
   {
     id: 'lectureN',
     title: 'Lecture Title',
     parts: { 1: 'Part Name', 2: '...' },
     sections: [ { id: '01-starting-point', title: 'Starting Point', part: 1 } ]
   }
   ```

Each lecture is fully independent. If a lecture continues from a previous one, copy the last snapshot's code files into the new lecture's first snapshot.

## Commands

- `npm run dev`: Start dev server
- `npm run build`: Production build (outputs to `../docs/`)
