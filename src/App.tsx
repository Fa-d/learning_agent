import React, { useState, useCallback } from 'react';
import axios from 'axios';
import { applyNodeChanges, applyEdgeChanges, NodeChange, EdgeChange } from 'reactflow';
import GraphCanvas from './components/GraphCanvas';
import GraphCanvas3D from './components/GraphCanvas3D';
import TopicInput from './components/TopicInput';
import NodeDetailPanel from './components/NodeDetailPanel';
import Neo4jExplorer from './components/Neo4jExplorer';
import ErrorBoundary from './components/ErrorBoundary';
import getLayoutedElements from './utils/layout';
import './index.css';

// Define types for graph elements for better type safety
interface NodeData {
    label: string;
}

interface Node {
    id: string;
    data: NodeData;
    position: { x: number; y: number };
}

interface Edge {
    id: string;
    source: string;
    target: string;
    data?: { label: string };
}

const App: React.FC = () => {
    const [nodes, setNodes] = useState<Node[]>([]);
    const [edges, setEdges] = useState<Edge[]>([]);
    const [selectedNode, setSelectedNode] = useState<Node | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [viewMode, setViewMode] = useState('2d');

    const onNodesChange = useCallback(
        (changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)),
        [setNodes]
    );
    const onEdgesChange = useCallback(
        (changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)),
        [setEdges]
    );

    const handleTopicSubmit = async (topic: string) => {
        setIsLoading(true);
        setError(null);
        setSelectedNode(null);
        try {
            const response = await axios.post<{ nodes: Node[]; edges: Edge[] }>('/api/generate', { topic });
            const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
                response.data.nodes || [],
                response.data.edges || []
            );
            setNodes(layoutedNodes);
            setEdges(layoutedEdges);
        } catch (err) {
            setError('Failed to generate graph. Please try again.');
            console.error(err);
        }
        setIsLoading(false);
    };

    const handleExpandNode = async (nodeId: string) => {
        setIsLoading(true);
        setError(null);
        try {
            const fullGraph = { nodes, edges };
            const response = await axios.post<{ nodes: Node[]; edges: Edge[] }>('/api/expand', {
                fullGraph,
                selectedNodeId: nodeId,
            });

            const { nodes: newNodes, edges: newEdges } = response.data;

            const updatedNodes = [...nodes];
            const updatedEdges = [...edges];

            const existingNodeIds = new Set(updatedNodes.map(n => n.id));
            const existingEdgeIds = new Set(updatedEdges.map(e => e.id));

            (newNodes || []).forEach(newNode => {
                if (!existingNodeIds.has(newNode.id)) {
                    updatedNodes.push(newNode);
                }
            });

            (newEdges || []).forEach(newEdge => {
                if (!existingEdgeIds.has(newEdge.id)) {
                    updatedEdges.push(newEdge);
                }
            });

            const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
                updatedNodes,
                updatedEdges
            );

            setNodes(layoutedNodes);
            setEdges(layoutedEdges);

        } catch (err) {
            setError('Failed to expand node. Please try again.');
            console.error(err);
        }
        setIsLoading(false);
    };

    const handleDeleteNode = (nodeId: string) => {
        setNodes((prevNodes) => prevNodes.filter((n) => n.id !== nodeId));
        setEdges((prevEdges) => prevEdges.filter((e) => e.source !== nodeId && e.target !== nodeId));
        setSelectedNode(null);
    };

    const handleNodeClick = useCallback((node: Node) => {
        setSelectedNode(node);
    }, []);

    const handleLoadGraphFromNeo4j = (loadedNodes: any[], loadedEdges: any[]) => {
        const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
            loadedNodes,
            loadedEdges
        );
        setNodes(layoutedNodes);
        setEdges(layoutedEdges);
        setSelectedNode(null);
    };

    return (
        <div className="app-container">
            <header className="app-header">
                <div className="header-content">
                    <h1>VizLearn</h1>
                    <p>Your visual learning companion</p>
                </div>
                <button onClick={() => setViewMode(viewMode === '2d' ? '3d' : '2d')} className="view-toggle-button">
                    Switch to {viewMode === '2d' ? '3D' : '2D'} View
                </button>
            </header>
            <main className="main-content">
                <div className="left-panel">
                    <TopicInput onSubmit={handleTopicSubmit} isLoading={isLoading} />
                    {error && <p className="error-message">{error}</p>}
                    {selectedNode && (
                        <NodeDetailPanel
                            node={selectedNode}
                            onExpand={handleExpandNode}
                            onDelete={handleDeleteNode}
                            isLoading={isLoading}
                        />
                    )}
                    <Neo4jExplorer onLoadGraph={handleLoadGraphFromNeo4j} />
                </div>
                <div className="graph-panel">
                    <ErrorBoundary>
                        {viewMode === '2d' ? (
                            <GraphCanvas 
                                nodes={nodes} 
                                edges={edges} 
                                onNodesChange={onNodesChange}
                                onEdgesChange={onEdgesChange}
                                onNodeClick={handleNodeClick} 
                            />
                        ) : (
                            <GraphCanvas3D nodes={nodes} edges={edges} onNodeClick={handleNodeClick} />
                        )}
                    </ErrorBoundary>
                </div>
            </main>
        </div>
    );
};

export default App;