import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle, Shield, Zap, FileText, TrendingUp, Radio } from 'lucide-react';
import { io } from 'socket.io-client';

const FLASK_BACKEND = 'http://127.0.0.1:5000';
const API_BASE_URL = `${FLASK_BACKEND}/api`;
const SOCKET_URL = FLASK_BACKEND;

export default function FakeNewsDetector() {
  const [text, setText] = useState('');
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('text');
  const [liveFeed, setLiveFeed] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE_URL}/health`)
      .then((res) => res.json())
      .then((data) => console.log('✅ Flask Health:', data))
      .catch((err) => console.error('❌ Flask connection failed:', err));
  }, []);

  const analyzeText = async () => {
    if (!text.trim() && !url.trim()) {
      setError('Please enter text or URL to analyze');
      return;
    }
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const endpoint = activeTab === 'text' ? '/analyze' : '/analyze-url';
      const body = activeTab === 'text' ? { text: text.trim() } : { url: url.trim() };
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await response.json();
      if (response.ok) setResults(data);
      else setError(data.error || 'Analysis failed');
    } catch (err) {
      console.error('❌ Error analyzing text:', err);
      setError('Unable to connect to Flask backend. Please ensure it’s running.');
    } finally {
      setLoading(false);
    }
  };

  const clearResults = () => {
    setText('');
    setUrl('');
    setResults(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Shield className="w-12 h-12 text-blue-400" />
            <h1 className="text-5xl font-bold text-white">Fake News Detector</h1>
          </div>
          <p className="text-blue-200 text-lg">AI-Powered News Verification & Authenticity Analysis</p>
        </div>

        <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => setActiveTab('text')}
              className={`flex-1 px-6 py-4 font-semibold transition-colors ${
                activeTab === 'text'
                  ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <FileText className="w-5 h-5 inline mr-2" /> Text Analysis
            </button>
            <button
              onClick={() => setActiveTab('url')}
              className={`flex-1 px-6 py-4 font-semibold transition-colors ${
                activeTab === 'url'
                  ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <TrendingUp className="w-5 h-5 inline mr-2" /> URL Analysis
            </button>
          </div>

          <div className="p-8">
            {activeTab === 'text' ? (
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Enter News Article Text</label>
                <textarea
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder="Paste the news article text here for analysis..."
                  className="w-full h-48 p-4 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none resize-none text-gray-800"
                />
              </div>
            ) : (
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Enter Article URL</label>
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com/article"
                  className="w-full p-4 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none text-gray-800"
                />
              </div>
            )}

            {error && (
              <div className="mt-4 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded">
                <p className="font-semibold">Error</p>
                <p className="text-sm">{error}</p>
              </div>
            )}

            <div className="flex gap-4 mt-6">
              <button
                onClick={analyzeText}
                disabled={loading || (!text.trim() && !url.trim())}
                className="flex-1 bg-blue-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-5 h-5 border-3 border-white border-t-transparent rounded-full animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Zap className="w-5 h-5" />
                    Analyze Article
                  </>
                )}
              </button>
              {(results || error) && (
                <button
                  onClick={clearResults}
                  className="px-8 py-4 rounded-lg font-semibold border-2 border-gray-300 text-black hover:bg-gray-100 transition-colors"
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          {results && (
            <div className="border-t border-gray-200 bg-gray-50 p-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Analysis Results</h2>
              <div className="grid md:grid-cols-2 gap-6 mb-6">
                <div className="bg-white rounded-xl p-6 shadow-md border-2 border-gray-200">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-gray-800">News Authenticity</h3>
                    {results.fakeNews.prediction === 'Real News' ? (
                      <CheckCircle className="w-8 h-8 text-green-500" />
                    ) : (
                      <AlertCircle className="w-8 h-8 text-red-500" />
                    )}
                  </div>
                  <div
                    className={`text-3xl font-bold mb-2 ${
                      results.fakeNews.prediction === 'Real News' ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {results.fakeNews.prediction}
                  </div>
                  <div className="mb-4">
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                      <span>Confidence</span>
                      <span className="font-semibold">{results.fakeNews.confidence}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className={`h-3 rounded-full ${
                          results.fakeNews.prediction === 'Real News' ? 'bg-green-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${results.fakeNews.confidence}%` }}
                      />
                    </div>
                  </div>
                </div>

                <div className="bg-white rounded-xl p-6 shadow-md border-2 border-gray-200">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-gray-800">Content Authorship</h3>
                    <Shield
                      className={`w-8 h-8 ${
                        results.aiGenerated.prediction === 'Human Written' ? 'text-blue-500' : 'text-purple-500'
                      }`}
                    />
                  </div>
                  <div
                    className={`text-3xl font-bold mb-2 ${
                      results.aiGenerated.prediction === 'Human Written' ? 'text-blue-600' : 'text-purple-600'
                    }`}
                  >
                    {results.aiGenerated.prediction}
                  </div>
                  <div className="mb-4">
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                      <span>Confidence</span>
                      <span className="font-semibold">{results.aiGenerated.confidence}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className={`h-3 rounded-full ${
                          results.aiGenerated.prediction === 'Human Written' ? 'bg-blue-500' : 'bg-purple-500'
                        }`}
                        style={{ width: `${results.aiGenerated.confidence}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-md border-2 border-gray-200">
                <h3 className="text-lg font-bold text-gray-800 mb-3">Analysis Metadata</h3>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600 block">Word Count</span>
                    <span className="font-semibold text-lg text-black">{results.metadata.wordCount}</span>
                  </div>
                  <div>
                    <span className="text-gray-600 block">Analysis Time</span>
                    <span className="font-semibold text-lg text-black">{results.metadata.analysisTime.toFixed(2)}s</span>
                  </div>
                  <div>
                    <span className="text-gray-600 block">Timestamp</span>
                    <span className="font-semibold text-lg text-black">
                      {new Date(results.metadata.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="text-center mt-12">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Radio className="text-red-500 animate-pulse" />
            <h2 className="text-2xl font-semibold text-white">📡 Live Real-Time News Feed</h2>
          </div>
          <div className="max-w-4xl mx-auto text-left space-y-4">
            {liveFeed.map((item, index) => (
              <div
                key={index}
                className="p-4 bg-slate-800 text-white rounded-lg shadow-md border border-slate-700 hover:bg-slate-700 transition"
              >
                <h3 className="font-bold text-blue-400">{item.headline}</h3>
                <p className="text-sm text-gray-400">
                  {item.source} | {item.timestamp}
                </p>
                <p className="text-sm text-gray-300 mt-1">
                  🧠 {item.fakeNews?.prediction} ({item.fakeNews?.confidence}%)
                </p>
                <p className="text-sm text-gray-500">
                  ✍️ {item.aiGenerated?.prediction} ({item.aiGenerated?.confidence}%)
                </p>
                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 underline text-sm mt-2 inline-block"
                >
                  Read more →
                </a>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
