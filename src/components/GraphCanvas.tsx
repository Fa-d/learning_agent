import React, { useCallback } from 'react';
import ReactFlow, { Controls, Background, MiniMap, OnNodesChange, OnEdgesChange, useNodesState, useEdgesState, addEdge } from 'reactflow';
import 'reactflow/dist/style.css';
import CustomEdge from './CustomEdge';

const edgeTypes = { custom: CustomEdge };

interface GraphCanvasProps {
    nodes: any[];
    edges: any[];
    onNodesChange: OnNodesChange;
    onEdgesChange: OnEdgesChange;
    onNodeClick: (node: any) => void;
}

const GraphCanvas: React.FC<GraphCanvasProps> = ({ nodes, edges, onNodesChange, onEdgesChange, onNodeClick }) => {

    return (
        <div style={{ height: '100%' }}>
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onNodeClick={(_event, node) => onNodeClick(node)}
                edgeTypes={edgeTypes}
                fitView
            >
                <Controls />
                <MiniMap />
                <Background />
            </ReactFlow>
        </div>
    );
};

export default GraphCanvas;
