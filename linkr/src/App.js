import './App.css';
import UrlCreator from './UrlManager';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Linkr</h1>
        <h2>Shorten your urls</h2>
      </header>
      <main>
        <UrlCreator />
      </main>
    </div>
  );
}

export default App;
