import React, { useState } from 'react';
import axios from 'axios';

interface Neo4jExplorerProps {
    onLoadGraph: (nodes: any[], edges: any[]) => void;
}

const Neo4jExplorer: React.FC<Neo4jExplorerProps> = ({ onLoadGraph }) => {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleLoadAllGraph = async () => {
        setIsLoading(true);
        setError(null);
        try {
            const response = await axios.get('/api/neo4j/all');
            onLoadGraph(response.data.nodes, response.data.edges);
        } catch (err) {
            setError('Failed to load all graph data from Neo4j.');
            console.error(err);
        }
        setIsLoading(false);
    };

    const handleSemanticSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);
        setSearchResults([]);
        try {
            const response = await axios.post('/api/neo4j/search', { query: searchQuery });
            setSearchResults(response.data);
        } catch (err) {
            setError('Failed to perform semantic search.');
            console.error(err);
        }
        setIsLoading(false);
    };

    return (
        <div className="neo4j-explorer">
            <h3>Neo4j Data Explorer</h3>
            <button onClick={handleLoadAllGraph} disabled={isLoading}>
                {isLoading ? 'Loading...' : 'Load All Graph from Neo4j'}
            </button>

            <form onSubmit={handleSemanticSearch} className="semantic-search-form">
                <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Semantic search query..."
                    disabled={isLoading}
                />
                <button type="submit" disabled={isLoading}>
                    {isLoading ? 'Searching...' : 'Search Similar Concepts'}
                </button>
            </form>

            {error && <p className="error-message">{error}</p>}

            {searchResults.length > 0 && (
                <div className="search-results">
                    <h4>Search Results:</h4>
                    <ul>
                        {searchResults.map((result) => (
                            <li key={result.id}>
                                <strong>{result.label}</strong> (Score: {result.score.toFixed(4)})
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default Neo4jExplorer;
