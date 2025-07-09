
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './frontend/Command-Console/App'; // Use @ alias for robust path resolution

const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);