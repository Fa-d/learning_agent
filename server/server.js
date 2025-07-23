const express = require('express');
const { GoogleGenerativeAI } = require('@google/generative-ai');
const dotenv = require('dotenv');
const cors = require('cors');
const neo4j = require('neo4j-driver');

dotenv.config();

const app = express();
const port = 3001;

app.use(cors());
app.use(express.json());

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

// Neo4j Driver Initialization
const driver = neo4j.driver(
    process.env.NEO4J_URI,
    neo4j.auth.basic(process.env.NEO4J_USERNAME, process.env.NEO4J_PASSWORD),
    { encrypted: 'ENCRYPTION_OFF' }
);

driver.verifyConnectivity()
    .then(() => console.log('Neo4j connection established.'))
    .catch((error) => console.error('Neo4j connection failed:', error));

const generationConfig = {
    temperature: 0.2,
    topK: 1,
    topP: 1,
    maxOutputTokens: 8192,
    responseMimeType: "application/json",
};

const safetySettings = [
    {
        category: "HARM_CATEGORY_HARASSMENT",
        threshold: "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        category: "HARM_CATEGORY_HATE_SPEECH",
        threshold: "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        category: "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        threshold: "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        category: "HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold: "BLOCK_MEDIUM_AND_ABOVE"
    },
];

async function generateGraph(prompt) {
    try {
        const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash", generationConfig, safetySettings });
        const result = await model.generateContent(prompt);
        const response = await result.response;
        const text = response.text();
        return JSON.parse(text);
    } catch (error) {
        console.error("Error generating graph:", error);
        throw new Error("Failed to generate graph from API.");
    }
}

async function getEmbedding(text) {
    try {
        const model = genAI.getGenerativeModel({ model: "embedding-001" });
        const result = await model.embedContent({ content: { parts: [{ text: text }] } });
        return result.embedding.values;
    } catch (error) {
        console.error("Error generating embedding:", error);
        // Return a placeholder or throw an error based on desired behavior
        return []; // Return empty array if embedding fails
    }
}

async function saveGraphToNeo4j(nodes, edges) {
    const session = driver.session();
    try {
        for (const node of nodes) {
            const embedding = await getEmbedding(node.data.label);
            await session.run(
                `MERGE (n:Concept {id: $id})
                 ON CREATE SET n.label = $label, n.embedding = $embedding
                 ON MATCH SET n.label = $label, n.embedding = $embedding`,
                { id: node.id, label: node.data.label, embedding: embedding }
            );
        }

        for (const edge of edges) {
            await session.run(
                `MATCH (a:Concept {id: $sourceId})
                 MATCH (b:Concept {id: $targetId})
                 MERGE (a)-[r:RELATES_TO {id: $edgeId, label: $label}]->(b)`,
                { sourceId: edge.source, targetId: edge.target, edgeId: edge.id, label: edge.data.label }
            );
        }
        console.log('Graph data saved to Neo4j.');
    } catch (error) {
        console.error('Error saving graph to Neo4j:', error);
    } finally {
        await session.close();
    }
}

app.post('/api/generate', async (req, res) => {
    const { topic } = req.body;
    if (!topic) {
        return res.status(400).json({ error: 'Topic is required' });
    }

    const prompt = `
        You are an API that generates knowledge graphs.
        Based on the topic "${topic}", generate a conceptual graph.
        The graph should have nodes and edges.
        Each node must have an id (string), a data object with a label (string), and a position object with x and y coordinates (number).
        Each edge must have an id (string), a source (string, node id), a target (string, node id), and a data object with a label (string) describing the relationship.
        The output must be a JSON object with two keys: "nodes" and "edges".
        Do not include any explanations, just the JSON object.
        Example format:
        {
          "nodes": [
            { "id": "1", "data": { "label": "Central Concept" }, "position": { "x": 250, "y": 250 } }
          ],
          "edges": [
            { "id": "edge-1-2", "source": "1", "target": "2", "data": { "label": "relates to" } }
          ]
        }
    `;

    try {
        const graphData = await generateGraph(prompt);
        // Save initial graph to Neo4j
        await saveGraphToNeo4j(graphData.nodes, graphData.edges);
        res.json(graphData);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.post('/api/expand', async (req, res) => {
    const { fullGraph, selectedNodeId } = req.body;

    if (!fullGraph || !selectedNodeId) {
        return res.status(400).json({ error: 'Full graph and selected node ID are required' });
    }

    const selectedNode = fullGraph.nodes.find(n => n.id === selectedNodeId);
    if (!selectedNode) {
        return res.status(404).json({ error: 'Selected node not found in the graph' });
    }

    const prompt = `
        You are an API that generates knowledge graphs.
        You will be given a full graph and a selected node to expand upon.
        Your task is to generate *only the new nodes and edges* required to expand the selected node's concept.

        - **DO NOT** return the full graph.
        - **ONLY** return the new nodes and edges to be added.
        - New nodes must have unique IDs that do not exist in the current graph.
        - New edges can connect new nodes to each other, or connect new nodes to existing nodes in the graph. Each new edge must also include a data object with a label property describing the relationship.
        - The output must be a JSON object with two keys: "nodes" and "edges", containing only the additions.
        - If there are no new concepts to add, return an empty "nodes" and "edges" array.

        Example format:
        {
          "nodes": [
            { "id": "new_node_1", "data": { "label": "New Concept" }, "position": { "x": 100, "y": 100 } }
          ],
          "edges": [
            { "id": "new_edge_1", "source": "existing_node_id", "target": "new_node_1", "data": { "label": "causes" } }
          ]
        }

        Current Graph:
        ${JSON.stringify(fullGraph, null, 2)}

        Selected Node to Expand:
        ${JSON.stringify(selectedNode, null, 2)}
    `;

    try {
        const graphData = await generateGraph(prompt);
        // Save expanded graph data to Neo4j
        await saveGraphToNeo4j(graphData.nodes, graphData.edges);
        res.json(graphData);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// New API endpoint to fetch all nodes and relationships from Neo4j
app.get('/api/neo4j/all', async (req, res) => {
    const session = driver.session();
    try {
        const result = await session.run(
            `MATCH (n:Concept)
             OPTIONAL MATCH (n)-[r]->(m:Concept)
             RETURN n, r, m`
        );

        const nodes = {};
        const edges = {};

        result.records.forEach(record => {
            const node = record.get('n');
            nodes[node.properties.id] = {
                id: node.properties.id,
                data: { label: node.properties.label },
                position: { x: Math.random() * 500, y: Math.random() * 500 } // Random position for visualization
            };

            const relationship = record.get('r');
            const targetNode = record.get('m');

            if (relationship && targetNode) {
                edges[relationship.properties.id] = {
                    id: relationship.properties.id,
                    source: relationship.properties.source || node.properties.id,
                    target: relationship.properties.target || targetNode.properties.id,
                    data: { label: relationship.properties.label } // Include label for edges from Neo4j
                };
            }
        });

        res.json({ nodes: Object.values(nodes), edges: Object.values(edges) });
    } catch (error) {
        console.error('Error fetching all graph data from Neo4j:', error);
        res.status(500).json({ error: 'Failed to fetch all graph data from Neo4j.' });
    }
    finally {
        await session.close();
    }
});

// New API endpoint for semantic search in Neo4j
app.post('/api/neo4j/search', async (req, res) => {
    const { query } = req.body;
    if (!query) {
        return res.status(400).json({ error: 'Search query is required' });
    }

    const session = driver.session();
    try {
        const queryEmbedding = await getEmbedding(query);

        // Ensure the vector index 'node_embeddings' exists and is configured for 768 dimensions
        const result = await session.run(
            `CALL db.index.vector.queryNodes('node_embeddings', $limit, $queryEmbedding)
             YIELD node, score
             RETURN node.id AS id, node.label AS label, score`,
            { limit: 10, queryEmbedding: queryEmbedding }
        );

        const searchResults = result.records.map(record => ({
            id: record.get('id'),
            label: record.get('label'),
            score: record.get('score'),
        }));

        res.json(searchResults);
    } catch (error) {
        console.error('Error performing semantic search in Neo4j:', error);
        res.status(500).json({ error: 'Failed to perform semantic search in Neo4j. Ensure vector index is created.' });
    }
    finally {
        await session.close();
    }
});


app.listen(port, () => {
    console.log(`Server listening at http://localhost:${port}`);
});
