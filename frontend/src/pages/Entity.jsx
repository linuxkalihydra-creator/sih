/**
 * Entity investigation page with evidence and transaction timeline.
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/client.js';
import { useDataset } from '../context/DatasetContext.jsx';
import './Entity.css';

export default function Entity() {
  const { walletId } = useParams();
  const navigate = useNavigate();
  const { selectedDatasetId, loadingDatasets } = useDataset();
  const [entity, setEntity] = useState(null);
  const [evidence, setEvidence] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (loadingDatasets) return undefined;
    if (!selectedDatasetId) {
      setEntity(null);
      setEvidence(null);
      setTransactions([]);
      setError('No dataset uploaded.');
      setLoading(false);
      return undefined;
    }

    const controller = new AbortController();
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [entityRes, evidenceRes, txRes] = await Promise.all([
          api.entity(walletId, selectedDatasetId, { signal: controller.signal }),
          api.entityEvidence(walletId, selectedDatasetId, { signal: controller.signal }).catch(() => ({ data: null })),
          api.entityTransactions(walletId, selectedDatasetId, { signal: controller.signal }).catch(() => ({ data: [] })),
        ]);

        if (controller.signal.aborted) return;
        setEntity(entityRes.data);
        setEvidence(evidenceRes.data);
        setTransactions(txRes.data || []);
      } catch (err) {
        if (controller.signal.aborted || err.code === 'ERR_CANCELED') return;
        console.error('Failed to fetch entity data:', err);
        setError('Unable to fetch entity details.');
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    };

    fetchData();
    return () => controller.abort();
  }, [walletId, selectedDatasetId, loadingDatasets]);

  if (loading) {
    return (
      <div className="entity-page">
        <button className="back-btn" onClick={() => navigate('/alerts')}>
          ← Back to Alerts
        </button>
        <div className="loading">Loading entity details...</div>
      </div>
    );
  }

  if (error || !entity) {
    return (
      <div className="entity-page">
        <button className="back-btn" onClick={() => navigate('/alerts')}>
          ← Back to Alerts
        </button>
        <div className="error-state">
          <h2>⚠️ Not Found</h2>
          <p>{error || 'Entity could not be loaded.'}</p>
        </div>
      </div>
    );
  }

  const sortedTransactions = [...transactions].sort(
    (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
  );

  return (
    <div className="entity-page">
      <button className="back-btn" onClick={() => navigate('/alerts')}>
        ← Back to Alerts
      </button>

      <div className="entity-header">
        <div>
          <h1>Wallet Investigation</h1>
          <p className="wallet-id">{walletId}</p>
        </div>
        <div className="risk-summary">
          <div className="risk-card">
            <div className="risk-label">Risk Score</div>
            <div className={`risk-value risk-${entity.risk_level.toLowerCase()}`}>
              {entity.risk_score.toFixed(2)}
            </div>
          </div>
          <div className="risk-card">
            <div className="risk-label">Risk Level</div>
            <div className={`risk-value risk-${entity.risk_level.toLowerCase()}`}>
              {entity.risk_level}
            </div>
          </div>
          <div className="risk-card">
            <div className="risk-label">Confidence</div>
            <div className="risk-value">{(entity.confidence * 100).toFixed(0)}%</div>
          </div>
          <div className="risk-card">
            <div className="risk-label">Cluster</div>
            <div className="risk-value">{entity.cluster_id ?? 'N/A'}</div>
          </div>
        </div>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab ${activeTab === 'evidence' ? 'active' : ''}`}
          onClick={() => setActiveTab('evidence')}
        >
          Why Flagged?
        </button>
        <button
          className={`tab ${activeTab === 'timeline' ? 'active' : ''}`}
          onClick={() => setActiveTab('timeline')}
        >
          Transaction Timeline
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'overview' && (
          <div className="tab-pane">
            <div className="statistics-grid">
              <div className="stat-section">
                <h3>Transaction Statistics</h3>
                <div className="stat-item">
                  <span>Total Transactions:</span>
                  <strong>{entity.transaction_statistics.transaction_count}</strong>
                </div>
                <div className="stat-item">
                  <span>Incoming:</span>
                  <strong>{entity.transaction_statistics.incoming_transaction_count}</strong>
                </div>
                <div className="stat-item">
                  <span>Outgoing:</span>
                  <strong>{entity.transaction_statistics.outgoing_transaction_count}</strong>
                </div>
              </div>

              <div className="stat-section">
                <h3>Network Statistics</h3>
                <div className="stat-item">
                  <span>Unique IPs:</span>
                  <strong>{entity.network_statistics.unique_ips}</strong>
                </div>
                <div className="stat-item">
                  <span>Unique Counterparties:</span>
                  <strong>{entity.network_statistics.unique_counterparties}</strong>
                </div>
                <div className="stat-item">
                  <span>Graph Degree:</span>
                  <strong>{entity.network_statistics.graph_degree}</strong>
                </div>
              </div>

              <div className="stat-section">
                <h3>ML Information</h3>
                <div className="stat-item">
                  <span>Anomaly Score:</span>
                  <strong>{entity.ml_information.anomaly_score.toFixed(4)}</strong>
                </div>
                <div className="stat-item">
                  <span>Anomaly Label:</span>
                  <strong>{entity.ml_information.anomaly_label === -1 ? 'Anomalous' : 'Normal'}</strong>
                </div>
              </div>
            </div>

            {entity.related_entities && entity.related_entities.length > 0 && (
              <div className="related-entities">
                <h3>Related Network Observations</h3>
                <div className="entity-list">
                  {entity.related_entities.map((ip, idx) => (
                    <div key={idx} className="entity-item">
                      {ip}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'evidence' && (
          <div className="tab-pane evidence-pane">
            <div className="evidence-disclaimer">
              <strong>⚠️ Important:</strong> The following represents investigative leads based on dataset analysis.
              This is NOT proof of illegal activity, identity, or asset ownership.
            </div>

            {evidence ? (
              <div className="evidence-panel">
                <div className="evidence-section">
                  <h3>🔍 Observed Evidence</h3>
                  {evidence.observed_fact ? (
                    <ul className="evidence-list">
                      {Object.entries(evidence.observed_fact).map(([key, value]) => (
                        <li key={key}>
                          <strong>{key}:</strong> {JSON.stringify(value)}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p>No specific evidence recorded.</p>
                  )}
                </div>

                <div className="evidence-section">
                  <h3>💡 Inference</h3>
                  <p>{evidence.inference || 'No inference available.'}</p>
                </div>

                <div className="evidence-section">
                  <h3>🔎 Investigative Lead</h3>
                  <p>{evidence.investigative_lead || 'No specific investigative lead.'}</p>
                </div>
              </div>
            ) : (
              <div className="empty-message">No evidence data available.</div>
            )}
          </div>
        )}

        {activeTab === 'timeline' && (
          <div className="tab-pane timeline-pane">
            {sortedTransactions.length === 0 ? (
              <div className="empty-message">No transactions recorded for this wallet.</div>
            ) : (
              <div className="timeline">
                {sortedTransactions.map((tx, idx) => (
                  <div key={idx} className="timeline-entry">
                    <div className="timeline-marker"></div>
                    <div className="timeline-content">
                      <div className="tx-header">
                        <strong>{tx.txid}</strong>
                        <span className="tx-time">
                          {new Date(tx.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <div className="tx-details">
                        <div className="tx-row">
                          <span>From:</span>
                          <code>{tx.src_ip}</code>
                        </div>
                        <div className="tx-row">
                          <span>To:</span>
                          <code>{tx.dst_ip}</code>
                        </div>
                        {tx.input_addresses && tx.input_addresses.length > 0 && (
                          <div className="tx-row">
                            <span>Inputs:</span>
                            <div className="address-list">
                              {tx.input_addresses.map((addr, i) => (
                                <code key={i}>{addr}</code>
                              ))}
                            </div>
                          </div>
                        )}
                        {tx.output_addresses && tx.output_addresses.length > 0 && (
                          <div className="tx-row">
                            <span>Outputs:</span>
                            <div className="address-list">
                              {tx.output_addresses.map((addr, i) => (
                                <code key={i}>{addr}</code>
                              ))}
                            </div>
                          </div>
                        )}
                        {tx.fee && (
                          <div className="tx-row">
                            <span>Fee:</span>
                            <strong>{tx.fee}</strong>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
