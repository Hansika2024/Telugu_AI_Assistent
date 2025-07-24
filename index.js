import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

if (process.env.NODE_ENV === 'development') {
  const logPerformance = () => {
    if ('performance' in window && 'getEntriesByType' in performance) {
      const navigationTiming = performance.getEntriesByType('navigation')[0];
      if (navigationTiming) {
        console.log('App Performance Metrics:');
        console.log(`DOM Content Loaded: ${navigationTiming.domContentLoadedEventEnd}ms`);
        console.log(`Load Complete: ${navigationTiming.loadEventEnd}ms`);
      }
    }
  };

  window.addEventListener('load', () => {
    setTimeout(logPerformance, 100);
  });
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
