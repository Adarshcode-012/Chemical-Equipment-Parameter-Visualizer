import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import './App.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

// Hardcoded credentials to match Desktop App (Basic Auth Only spec)
const AUTH_CREDENTIALS = {
  username: 'admin',
  password: 'admin123'
};

function App() {
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await axios.get('/api/history/', {
        auth: AUTH_CREDENTIALS
      });
      setHistory(response.data);
    } catch (err) {
      console.error("Failed to fetch history", err);
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
    setMessage(null);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a CSV file first.");
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    setError(null);
    setMessage(null);
    setSummary(null);

    try {
      const response = await axios.post('/api/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        auth: AUTH_CREDENTIALS
      });
      setSummary(response.data);
      setMessage("Upload successful!");
      fetchHistory(); // Refresh history
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError("An unexpected error occurred during upload.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/report/', {
        responseType: 'blob', // Important for PDF
        auth: AUTH_CREDENTIALS
      });

      // Create a blob URL and trigger download
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;

      // Extract filename from header if possible, else default
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'report.pdf';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
        if (filenameMatch.length === 2)
          filename = filenameMatch[1];
      }

      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();

      // Cleanup
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
      setLoading(false);
    } catch (err) {
      console.error("Download failed", err);
      setError("Failed to download PDF report. Ensure backend is running.");
      setLoading(false);
    }
  };

  const chartData = summary ? {
    labels: Object.keys(summary.type_distribution),
    datasets: [
      {
        label: 'Equipment Count',
        data: Object.values(summary.type_distribution),
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
      },
    ],
  } : null;

  return (
    <div className="dashboard-container">
      <nav className="dashboard-nav">
        <div className="nav-brand">
          <span className="brand-icon">⚡</span>
          <h1>Chemical Visualizer</h1>
        </div>
        <div className="nav-actions">
          {/* Placeholder for future nav items */}
        </div>
      </nav>

      <main className="dashboard-main">
        {/* Top Control Bar */}
        <section className="control-bar panel">
          <div className="upload-widget">
            <h3>Data Upload</h3>
            <form onSubmit={handleUpload} className="upload-form">
              <label className="file-input-label">
                <input type="file" accept=".csv" onChange={handleFileChange} />
                <span className="file-cta">
                  {file ? file.name : "Choose CSV File..."}
                </span>
              </label>
              <button type="submit" className="btn-primary" disabled={loading || !file}>
                {loading ? 'Processing...' : 'Upload & Analyze'}
              </button>
            </form>
          </div>
          {error && <div className="alert alert-error">{error}</div>}
          {message && <div className="alert alert-success">{message}</div>}
        </section>

        {summary && (
          <div className="dashboard-grid">
            {/* KPI Metrics Row */}
            <div className="metrics-row">
              <div className="metric-card accent-blue">
                <span className="metric-label">Total Equipment</span>
                <div className="metric-value">{summary.total_count}</div>
              </div>
              <div className="metric-card accent-green">
                <span className="metric-label">Avg Flowrate</span>
                <div className="metric-value">{summary.avg_flowrate} <small>L/min</small></div>
              </div>
              <div className="metric-card accent-orange">
                <span className="metric-label">Avg Pressure</span>
                <div className="metric-value">{summary.avg_pressure} <small>PSI</small></div>
              </div>
              <div className="metric-card accent-red">
                <span className="metric-label">Avg Temp</span>
                <div className="metric-value">{summary.avg_temperature} <small>°C</small></div>
              </div>
            </div>

            {/* Main Content Area: Chart + History */}
            <div className="analytics-row">
              <section className="panel chart-panel">
                <div className="panel-header">
                  <h3>Equipment Type Distribution</h3>
                  <button onClick={handleDownloadReport} className="btn-outline" disabled={loading}>
                    {loading ? 'Downloading...' : 'Download PDF'}
                  </button>
                </div>
                <div className="chart-container">
                  <Bar data={chartData} options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: { position: 'bottom' }
                    }
                  }} />
                </div>
              </section>

              <section className="panel history-panel">
                <div className="panel-header">
                  <h3>Recent Uploads</h3>
                </div>
                <div className="table-responsive">
                  {history.length === 0 ? (
                    <p className="empty-state">No history recorded.</p>
                  ) : (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Filename</th>
                          <th>Time</th>
                          <th>Count</th>
                          <th>Flow</th>
                          <th>Pressure</th>
                          <th>Temp</th>
                        </tr>
                      </thead>
                      <tbody>
                        {history.map((item, index) => (
                          <tr key={index}>
                            <td className="font-medium">{item.file_name}</td>
                            <td className="text-muted">{new Date(item.uploaded_at).toLocaleTimeString()}</td>
                            <td><span className="badge">{item.total_equipment}</span></td>
                            <td>{item.avg_flowrate}</td>
                            <td>{item.avg_pressure}</td>
                            <td>{item.avg_temperature}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </section>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
