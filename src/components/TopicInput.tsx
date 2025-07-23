import React from 'react';

interface TopicInputProps {
    onSubmit: (topic: string) => void;
    isLoading: boolean;
}

const TopicInput: React.FC<TopicInputProps> = ({ onSubmit, isLoading }) => {
    const [topic, setTopic] = React.useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (topic.trim()) {
            onSubmit(topic.trim());
        }
    };

    return (
        <form onSubmit={handleSubmit} className="topic-input-form">
            <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="Enter a topic to visualize..."
                disabled={isLoading}
            />
            <button type="submit" disabled={isLoading}>
                {isLoading ? 'Generating...' : 'Generate Graph'}
            </button>
        </form>
    );
};

export default TopicInput;
