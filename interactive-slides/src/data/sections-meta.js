// Metadata for each tutorial section
// Content, howToRun, and expectedOutput are loaded from markdown files in each snapshot directory

export const partTitles = {
  1: 'API Fundamentals',
  2: 'Analyzing Data with LLMs',
  3: 'Building the UI'
};

export const sectionsMeta = [
  {
    id: '02-setup',
    title: 'Setup: Install Dependencies',
    part: 1
  },
  {
    id: '03-first-api-call',
    title: 'Your First API Call',
    part: 1
  },
  {
    id: '03b-conversation-turns',
    title: 'Multi-turn Conversations',
    part: 1
  },
  {
    id: '04-temperature-experiment',
    title: 'Experimenting with Temperature',
    part: 1
  },
  {
    id: '05-token-counting',
    title: 'Counting Tokens',
    part: 1
  },
  {
    id: '06-cost-estimation',
    title: 'Estimating API Costs',
    part: 1
  },
  {
    id: '07-free-form-text-problem',
    title: 'The Problem with Free-Form Text',
    part: 1
  },
  {
    id: '08-pydantic-solution',
    title: 'The Solution: Pydantic Models',
    part: 1
  },
  {
    id: '09-prompt-chaining-intro',
    title: 'Single Step Problem',
    part: 2
  },
  {
    id: '10-generate-code',
    title: 'Step 1: Generate Code',
    part: 2
  },
  {
    id: '11-execute-code',
    title: 'Step 2: Execute Code',
    part: 2
  },
  {
    id: '12-interpret-result',
    title: 'Step 3: Interpret Result',
    part: 2
  },
  {
    id: '13-streamlit-intro',
    title: 'Streamlit - Installation',
    part: 3
  },
  {
    id: '14a-streamlit-concept-1',
    title: 'Concept 1: Displaying Content',
    part: 3
  },
  {
    id: '14b-streamlit-concept-2',
    title: 'Concept 2: User Inputs',
    part: 3
  },
  {
    id: '15a-streamlit-concept-3',
    title: 'Concept 3: Sidebar',
    part: 3
  },
  {
    id: '15b-streamlit-concept-4',
    title: 'Concept 4: Layout Control',
    part: 3
  },
  {
    id: '16-load-data-column-selection',
    title: 'Step 1: Setup Layout & Load Data',
    part: 3
  },
  {
    id: '17-add-row-filters',
    title: 'Step 2: Add Visual Filters',
    part: 3
  },
  {
    id: '18-add-question-input',
    title: 'Step 3: Add Question Input',
    part: 3
  },
  {
    id: '19-complete-integration',
    title: 'Step 4: Complete Integration',
    part: 3
  }
];
