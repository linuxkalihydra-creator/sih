import React from 'react';
import { Link } from 'react-router-dom';

export default class ErrorBoundary extends React.Component {
  state = { error: null };

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    if (import.meta.env.DEV) {
      console.error('FRONTEND RENDER ERROR', error.message);
      console.error('RENDER STACK', error.stack);
      console.error('COMPONENT STACK', info.componentStack);
    }
  }

  retry = () => this.setState({ error: null });

  render() {
    if (!this.state.error) return this.props.children;

    return (
      <main className="application-error" role="alert">
        <h1>Something went wrong</h1>
        <p>The page could not be displayed. You can try rendering it again or return to the dashboard.</p>
        <div className="application-error-actions">
          <button type="button" onClick={this.retry}>Retry</button>
          <Link to="/">Return to Dashboard</Link>
        </div>
        {import.meta.env.DEV && (
          <small>Development error: {this.state.error?.message || 'Unknown error'}</small>
        )}
      </main>
    );
  }
}
