export const lectures = [
  {
    id: 'lecture1',
    title: 'Building an Interactive Data Analysis Tool',
    parts: {
      1: 'API Fundamentals',
      2: 'Analyzing Data with LLMs',
      3: 'Building the UI'
    },
    sections: [
      { id: '01-setup', title: 'Setup: Install Dependencies', part: 1 },
      { id: '02-first-api-call', title: 'Your First API Call', part: 1 },
      { id: '03-conversation-turns', title: 'Multi-turn Conversations', part: 1 },
      { id: '04-temperature-experiment', title: 'Experimenting with Temperature', part: 1 },
      { id: '05-token-counting', title: 'Counting Tokens', part: 1 },
      { id: '06-cost-estimation', title: 'Estimating API Costs', part: 1 },
      { id: '07-free-form-text-problem', title: 'The Problem with Free-Form Text', part: 1 },
      { id: '08-pydantic-solution', title: 'The Solution: Pydantic Models', part: 1 },
      { id: '09-prompt-chaining-intro', title: 'Single Step Problem', part: 2 },
      { id: '10-generate-code', title: 'Step 1: Generate Code', part: 2 },
      { id: '11-execute-code', title: 'Step 2: Execute Code', part: 2 },
      { id: '12-interpret-result', title: 'Step 3: Interpret Result', part: 2 },
      { id: '13-streamlit-intro', title: 'Streamlit - Installation', part: 3 },
      { id: '14-streamlit-concept-1', title: 'Concept 1: Displaying Content', part: 3 },
      { id: '15-streamlit-concept-2', title: 'Concept 2: User Inputs', part: 3 },
      { id: '16-streamlit-concept-3', title: 'Concept 3: Sidebar', part: 3 },
      { id: '17-streamlit-concept-4', title: 'Concept 4: Layout Control', part: 3 },
      { id: '18-load-data-column-selection', title: 'Step 1: Setup Layout & Load Data', part: 3 },
      { id: '19-add-row-filters', title: 'Step 2: Add Visual Filters', part: 3 },
      { id: '20-add-question-input', title: 'Step 3: Add Question Input', part: 3 },
      { id: '21-complete-integration', title: 'Step 4: Complete Integration', part: 3 }
    ]
  },
  {
    id: 'lecture2',
    title: 'From Pipelines to Agents',
    parts: {
      1: 'Function Calling'
    },
    sections: [
      { id: '01-tool-definitions', title: 'Defining Tools', part: 1 },
      { id: '02-tool-selection', title: 'Tool Selection', part: 1 },
      { id: '03-tool-execution', title: 'Tool Execution', part: 1 },
      { id: '04-tool-calling-loop', title: 'Tool Calling Loop', part: 1 }
    ]
  }
];
