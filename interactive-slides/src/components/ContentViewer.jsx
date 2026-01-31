import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { prism } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import './ContentViewer.css';

function ContentViewer({ section }) {
  const { content } = section;

  const renderMarkdown = (text) => (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '');
          return !inline && match ? (
            <SyntaxHighlighter
              style={prism}
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
        img({ node, ...props }) {
          return (
            <img
              {...props}
              style={{
                maxWidth: '100%',
                height: 'auto',
                borderRadius: '8px',
                border: '1px solid #e1e4e8',
                marginTop: '16px',
                marginBottom: '16px'
              }}
              alt={props.alt || 'Screenshot'}
            />
          );
        },
      }}
    >
      {text}
    </ReactMarkdown>
  );

  return (
    <div className="content-viewer">
      <div className="markdown-body">
        {renderMarkdown(content)}
      </div>
    </div>
  );
}

export default ContentViewer;
