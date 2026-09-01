import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Alerts from './pages/Alerts';
import Entity from './pages/Entity';
import Clusters from './pages/Clusters';
import { DatasetProvider } from './context/DatasetContext.jsx';
import ErrorBoundary from './components/ErrorBoundary.jsx';
import './App.css';

function App() {
  return (
    <Router><ErrorBoundary><DatasetProvider>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/entities/:walletId" element={<Entity />} />
          <Route path="/clusters" element={<Clusters />} />
          <Route path="/clusters/:clusterId" element={<Clusters />} />
          <Route path="*" element={<Dashboard />} />
        </Routes>
      </Layout>
    </DatasetProvider></ErrorBoundary></Router>
  );
}

export default App;
