import React from 'react';

interface NodeDetailPanelProps {
    node: any; // Consider defining a specific type for the node
    onExpand: (nodeId: string) => void;
    onDelete: (nodeId: string) => void;
    isLoading: boolean;
}

const NodeDetailPanel: React.FC<NodeDetailPanelProps> = ({ node, onExpand, onDelete, isLoading }) => {
    if (!node) {
        return null;
    }

    return (
        <div className="node-detail-panel">
            <h3>Node Details</h3>
            <p><strong>ID:</strong> {node.id}</p>
            <p><strong>Label:</strong> {node.data.label}</p>
            <div className="node-actions">
                <button onClick={() => onExpand(node.id)} disabled={isLoading}>
                    {isLoading ? 'Expanding...' : 'Expand'}
                </button>
                <button onClick={() => onDelete(node.id)} disabled={isLoading} className="delete-button">
                    Delete
                </button>
            </div>
        </div>
    );
};

export default NodeDetailPanel;
