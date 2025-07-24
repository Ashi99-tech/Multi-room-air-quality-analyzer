import React from 'react';
import './App.css';
import QuestionForm from './components/QuestionForm';

function App() {
  return (
    <div className="App">
      <header>
        <h1>IAQ Analysis Tool</h1>
        <p>Ask any question about indoor temperature, CO₂, or humidity trends</p>
      </header>
      <main>
        <QuestionForm />
      </main>
    </div>
  );
}

export default App;
