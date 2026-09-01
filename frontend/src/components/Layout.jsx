/**
 * Main layout component with navigation sidebar.
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Layout.css';

export default function Layout({ children }) {
  const location = useLocation();

  const isActive = (path) => location.pathname === path || location.pathname.startsWith(path + '/');

  return (
    <div className="layout">
      <header className="header">
        <div className="header-brand">
          <h1>Bitcoin Investigation Platform</h1>
          <p className="subtitle">Investigation Dashboard</p>
        </div>
      </header>

      <div className="main-container">
        <nav className="sidebar">
          <ul className="nav-menu">
            <li>
              <Link to="/" className={`nav-link ${isActive('/') && location.pathname === '/' ? 'active' : ''}`}>
                📊 Dashboard
              </Link>
            </li>
            <li>
              <Link to="/alerts" className={`nav-link ${isActive('/alerts') ? 'active' : ''}`}>
                ⚠️ Alerts
              </Link>
            </li>
            <li>
              <Link to="/clusters" className={`nav-link ${isActive('/clusters') ? 'active' : ''}`}>
                🔗 Clusters
              </Link>
            </li>
          </ul>
        </nav>

        <main className="content">
          {children}
        </main>
      </div>

      <footer className="footer">
        <p>Results represent investigative leads, not proof of identity, ownership, or criminal activity.</p>
      </footer>
    </div>
  );
}
