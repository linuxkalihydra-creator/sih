import React, { useEffect, useMemo, useRef, useState } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import './InvestigationGraph.css';

const NODE_TYPES = ['Wallet', 'Transaction', 'IP', 'ASN', 'Country'];

const styles = [
  { selector: 'node', style: { label: 'data(label)', color: '#f4f1ea', 'font-size': 10, 'text-wrap': 'wrap', 'text-max-width': 90, 'text-valign': 'bottom', 'text-margin-y': 8, 'background-color': '#53606d', width: 34, height: 34, 'border-width': 2, 'border-color': '#aab4bf' } },
  { selector: 'node[type="Wallet"]', style: { shape: 'ellipse', 'background-color': '#cf7d4b', 'border-color': '#ffc39d', width: 44, height: 44 } },
  { selector: 'node[type="Transaction"]', style: { shape: 'rectangle', 'background-color': '#457b9d', 'border-color': '#9bd5f2' } },
  { selector: 'node[type="IP"]', style: { shape: 'diamond', 'background-color': '#718355', 'border-color': '#cfe6a8' } },
  { selector: 'node[type="ASN"]', style: { shape: 'hexagon', 'background-color': '#8b5e83', 'border-color': '#e2b8d9' } },
  { selector: 'node[type="Country"]', style: { shape: 'star', 'background-color': '#b38b3d', 'border-color': '#f5d98a' } },
  { selector: 'edge', style: { width: 1.5, 'line-color': '#65727f', 'target-arrow-color': '#65727f', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', label: 'data(type)', color: '#aeb8c1', 'font-size': 8, 'text-background-color': '#17212b', 'text-background-opacity': 0.85, 'text-background-padding': 2 } },
  { selector: '.focus', style: { 'border-width': 4, 'border-color': '#f4d35e', 'shadow-blur': 12, 'shadow-color': '#f4d35e', 'shadow-opacity': 0.8 } },
  { selector: '.connected', style: { opacity: 1, 'line-color': '#f4d35e', 'target-arrow-color': '#f4d35e', width: 3 } },
  { selector: '.dimmed', style: { opacity: 0.2 } },
];

function shortLabel(node) {
  const label = String(node.label || node.id);
  return label.length > 20 ? `${label.slice(0, 17)}...` : label;
}

export default function InvestigationGraph({ data, walletId, onNodeSelect }) {
  const cyRef = useRef(null);
  const tapHandlerRef = useRef(null);
  const canvasRef = useRef(null);
  const [filters, setFilters] = useState(() => new Set(NODE_TYPES));

  const elements = useMemo(() => {
    const nodes = (data?.nodes || []).map((node) => ({ data: { ...node, label: shortLabel(node) } }));
    const edges = (data?.edges || []).map((edge) => ({ data: edge }));
    return [...nodes, ...edges];
  }, [data]);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;
    cy.nodes().removeClass('focus connected dimmed');
    if (!walletId) return;
    const root = cy.getElementById(walletId);
    if (root.length) {
      root.addClass('focus');
      root.connectedEdges().addClass('connected');
      root.neighborhood().nodes().not(root).addClass('focus');
      cy.elements().not(root.union(root.neighborhood())).addClass('dimmed');
    }
  }, [walletId, elements]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !window.ResizeObserver) return undefined;
    const observer = new ResizeObserver(() => cyRef.current?.resize());
    observer.observe(canvas);
    return () => observer.disconnect();
  }, []);

  const applyFilters = (nextFilters) => {
    setFilters(nextFilters);
    const cy = cyRef.current;
    if (!cy) return;
    cy.nodes().forEach((node) => node.toggleClass('dimmed', !nextFilters.has(node.data('type'))));
  };

  const selectNode = (event) => {
    const node = event.target;
    const cy = cyRef.current;
    cy.elements().removeClass('focus connected dimmed');
    node.addClass('focus');
    node.connectedEdges().addClass('connected');
    node.neighborhood().nodes().not(node).addClass('focus');
    cy.elements().not(node.union(node.neighborhood())).addClass('dimmed');
    onNodeSelect?.(node.data());
  };

  const fit = () => cyRef.current?.fit(undefined, 35);
  const resetLayout = () => cyRef.current?.layout({ name: 'breadthfirst', directed: true, animate: false, padding: 40, spacingFactor: 1.2 }).run();

  useEffect(() => () => {
    if (cyRef.current && tapHandlerRef.current) cyRef.current.off('tap', 'node', tapHandlerRef.current);
  }, []);

  if (!data?.graph_available) {
    return <div className="graph-state">Neo4j unavailable. The graph could not be retrieved.</div>;
  }
  if (!data.nodes?.length) {
    return <div className="graph-state">No graph data available for this wallet.</div>;
  }

  return (
    <div className="investigation-graph">
      <div className="graph-toolbar">
        <div className="graph-actions">
          <button type="button" onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 1.2)} aria-label="Zoom in">+</button>
          <button type="button" onClick={() => cyRef.current?.zoom(cyRef.current.zoom() / 1.2)} aria-label="Zoom out">-</button>
          <button type="button" onClick={fit}>Fit</button>
          <button type="button" onClick={resetLayout}>Reset layout</button>
        </div>
        <div className="graph-filters" aria-label="Node filters">
          {NODE_TYPES.map((type) => (
            <label key={type}>
              <input type="checkbox" checked={filters.has(type)} onChange={() => {
                const next = new Set(filters);
                if (next.has(type)) next.delete(type);
                else next.add(type);
                applyFilters(next);
              }} />
              {type}
            </label>
          ))}
        </div>
      </div>
      <div className="graph-canvas" ref={canvasRef}>
        <CytoscapeComponent
          elements={elements}
          stylesheet={styles}
          cy={(cy) => {
            if (cyRef.current === cy) return;
            if (cyRef.current && tapHandlerRef.current) cyRef.current.off('tap', 'node', tapHandlerRef.current);
            cyRef.current = cy;
            tapHandlerRef.current = selectNode;
            cy.on('tap', 'node', tapHandlerRef.current);
          }}
          layout={{ name: 'breadthfirst', directed: true, animate: false, padding: 40, spacingFactor: 1.2 }}
          style={{ width: '100%', height: '560px' }}
          minZoom={0.2}
          maxZoom={3}
        />
      </div>
      <div className="graph-legend">
        {NODE_TYPES.map((type) => <span key={type} className={`legend-${type.toLowerCase()}`}><i />{type}</span>)}
      </div>
    </div>
  );
}
