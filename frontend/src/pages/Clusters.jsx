/**
 * Clusters page showing DBSCAN clustering results.
 */

import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import api from '../api/client.js';
import InvestigationGraph from '../components/graph/InvestigationGraph.jsx';
import { useDataset } from '../context/DatasetContext.jsx';
import './Clusters.css';

export default function Clusters() {
  const { clusterId: routeClusterId } = useParams();
  const { selectedDatasetId, loadingDatasets, datasetsError, refreshDatasets } = useDataset();
  const [clusters, setClusters] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedClusterId, setExpandedClusterId] = useState(() => routeClusterId ? Number(routeClusterId) : null);
  const [graphData, setGraphData] = useState(null);
  const [graphLoading, setGraphLoading] = useState(false);
  const [graphError, setGraphError] = useState(null);
  const [graphRetryToken, setGraphRetryToken] = useState(0);
  const [selectedNode, setSelectedNode] = useState(null);
  const [retryToken, setRetryToken] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [clustersRes, alertsRes] = await Promise.all([
          api.clusters(selectedDatasetId, { signal: controller.signal }),
          api.alerts(selectedDatasetId, { signal: controller.signal }),
        ]);

        if (controller.signal.aborted) return;
        setClusters(clustersRes.data);
        setAlerts(alertsRes.data);
      } catch (err) {
        if (controller.signal.aborted || err.code === 'ERR_CANCELED') return;
        console.error('Failed to fetch clusters:', err);
        setError('Backend unavailable. Unable to fetch cluster data.');
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    };

    if (selectedDatasetId) fetchData(); else if (!loadingDatasets) setLoading(false);
    return () => controller.abort();
  }, [selectedDatasetId, loadingDatasets, retryToken]);

  useEffect(() => {
    setExpandedClusterId(routeClusterId ? Number(routeClusterId) : null);
  }, [routeClusterId]);

  useEffect(() => {
    setGraphData(null);
    setGraphError(null);
    setSelectedNode(null);
  }, [selectedDatasetId]);

  useEffect(() => {
    if (!selectedDatasetId || expandedClusterId === null) return undefined;
    const controller = new AbortController();
    const fetchGraph = async () => {
      setGraphLoading(true);
      setGraphError(null);
      try {
        const { data } = await api.clusterGraph(selectedDatasetId, expandedClusterId, { signal: controller.signal });
        if (!controller.signal.aborted) setGraphData(data);
      } catch (err) {
        if (!controller.signal.aborted && err.code !== 'ERR_CANCELED') setGraphError('Unable to load graph.');
      } finally {
        if (!controller.signal.aborted) setGraphLoading(false);
      }
    };
    fetchGraph();
    return () => controller.abort();
  }, [selectedDatasetId, expandedClusterId, graphRetryToken]);

  if (loading) {
    return (
      <div className="clusters-page">
        <div className="loading">Loading clusters...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="clusters-page">
        <div className="error-state">
          <h2>⚠️ Error</h2>
          <p>{error}</p>
          <button type="button" onClick={() => setRetryToken((value) => value + 1)}>Retry</button>
        </div>
      </div>
    );
  }

  if (clusters.length === 0) {
    return (
      <div className="clusters-page">
        <h1>Clusters</h1>
        <div className="empty-state">
          <p>{datasetsError ? 'Backend unavailable.' : selectedDatasetId ? 'No clustering data available.' : 'No analysis available. Upload a dataset to begin.'}</p>
          {datasetsError && <button type="button" onClick={refreshDatasets}>Retry</button>}
        </div>
      </div>
    );
  }

  const clusterGroups = {};
  clusters.forEach((item) => {
    const cid = item.cluster_id;
    if (!clusterGroups[cid]) {
      clusterGroups[cid] = [];
    }
    clusterGroups[cid].push(item.wallet_id);
  });

  const clusterSummaries = Object.entries(clusterGroups).map(([cid, walletIds]) => {
    const clusterAlerts = alerts.filter((a) => walletIds.includes(a.wallet_id));
    const avgRisk =
      clusterAlerts.length > 0
        ? clusterAlerts.reduce((sum, a) => sum + a.risk_score, 0) / clusterAlerts.length
        : 0;
    const highestRisk = clusterAlerts.length > 0 ? Math.max(...clusterAlerts.map((a) => a.risk_score)) : 0;
    const highestRiskWallet = clusterAlerts.length > 0 ? clusterAlerts.find((a) => a.risk_score === highestRisk) : null;

    return {
      cluster_id: parseInt(cid),
      entity_count: walletIds.length,
      average_risk: avgRisk,
      highest_risk: highestRisk,
      highest_risk_wallet: highestRiskWallet,
      wallets: walletIds,
    };
  });

  clusterSummaries.sort((a, b) => b.average_risk - a.average_risk);

  const toggleExpand = async (cid) => {
    setGraphData(null);
    setExpandedClusterId((current) => current === cid ? null : cid);
  };

  return (
    <div className="clusters-page">
      <h1>Behavioral Clusters</h1>

      <div className="clusters-intro">
        <p>
          Clusters represent groups of wallets with similar behavioral patterns detected by DBSCAN clustering.
          These groupings indicate potential relationships but do NOT confirm actual criminal organizations.
        </p>
      </div>

      <div className="clusters-list">
        {clusterSummaries.map((cluster) => (
          <div key={cluster.cluster_id} className="cluster-card">
            <div className="cluster-header" onClick={() => toggleExpand(cluster.cluster_id)}>
              <div className="cluster-title">
                <h3>Cluster {cluster.cluster_id}</h3>
                <span className="cluster-badge">{cluster.entity_count} entities</span>
              </div>
              <div className="cluster-metrics">
                <div className="metric">
                  <span className="metric-label">Avg Risk</span>
                  <span className="metric-value">{cluster.average_risk.toFixed(2)}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Max Risk</span>
                  <span className={`metric-value risk-${cluster.highest_risk_wallet?.risk_level?.toLowerCase() || 'low'}`}>
                    {cluster.highest_risk.toFixed(2)}
                  </span>
                </div>
              </div>
              <button className="expand-btn">{expandedClusterId === cluster.cluster_id ? '▼' : '▶'}</button>
            </div>

            {expandedClusterId === cluster.cluster_id && (
              <div className="cluster-details">
                {cluster.highest_risk_wallet && (
                  <div className="highest-risk">
                    <h4>🔴 Highest-Risk Entity</h4>
                    <div className="entity-card">
                      <div className="entity-row">
                        <span>Wallet:</span>
                        <code>{cluster.highest_risk_wallet.wallet_id}</code>
                      </div>
                      <div className="entity-row">
                        <span>Risk Score:</span>
                        <strong>{cluster.highest_risk_wallet.risk_score.toFixed(2)}</strong>
                      </div>
                      <div className="entity-row">
                        <span>Risk Level:</span>
                        <span className={`risk-badge risk-${cluster.highest_risk_wallet.risk_level.toLowerCase()}`}>
                          {cluster.highest_risk_wallet.risk_level}
                        </span>
                      </div>
                      <Link to={`/entities/${cluster.highest_risk_wallet.wallet_id}`} className="investigate-link">
                        Investigate →
                      </Link>
                    </div>
                  </div>
                )}

                <div className="entities-in-cluster">
                  <h4>📋 All Entities ({cluster.entity_count})</h4>
                  <div className="entities-grid">
                    {cluster.wallets.map((wallet) => {
                      const alert = alerts.find((a) => a.wallet_id === wallet);
                      return (
                        <div key={wallet} className="entity-badge">
                          <Link to={`/entities/${wallet}`}>{wallet}</Link>
                          {alert && <span className={`risk-tag risk-${alert.risk_level.toLowerCase()}`}>{alert.risk_level}</span>}
                        </div>
                      );
                    })}
                  </div>
                </div>
                <div className="cluster-graph">
                  <h4>Graph</h4>
                  {graphLoading ? <div className="graph-state">Loading graph...</div> : graphError ? <div className="graph-state">{graphError} <button type="button" onClick={() => setGraphRetryToken((value) => value + 1)}>Retry</button></div> : graphData ? <>
                    {graphData.limited && <p className="graph-limit">Graph limited to {graphData.max_nodes} nodes / {graphData.max_edges} relationships for performance.</p>}
                    <InvestigationGraph data={graphData} onNodeSelect={setSelectedNode} />
                    {selectedNode && <div className="node-details"><h4>{selectedNode.type} details</h4><code>{selectedNode.id}</code></div>}
                  </> : <div className="graph-state">No graph data available for this cluster.</div>}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
