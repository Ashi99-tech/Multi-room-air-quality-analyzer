import React, { useState } from 'react';
import axios from 'axios';

function QuestionForm() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const askQuestion = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setAnswer('');

    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/ask`, { question });
      setAnswer(response.data.answer);
    } catch (error) {
      setAnswer("Error contacting server.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: 'auto' }}>
      <textarea
        rows="4"
        placeholder="Ask a question about room air quality..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        style={{ width: '100%', padding: '10px', fontSize: '1rem' }}
      />
      <button onClick={askQuestion} style={{ marginTop: '10px', padding: '10px 20px', fontSize: '1rem' }}>
        {loading ? 'Asking...' : 'Ask AI'}
      </button>

      {answer && (
        <div style={{ marginTop: '20px', textAlign: 'left', whiteSpace: 'pre-wrap' }}>
          <h3>AI's Response:</h3>
          <div>{answer}</div>
        </div>
      )}
    </div>
  );
}

export default QuestionForm;
