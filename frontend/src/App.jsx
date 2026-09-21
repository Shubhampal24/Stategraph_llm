import React, { useMemo, useState } from "react";
import {
  CheckCircle2,
  CircleDot,
  GitBranch,
  Play,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Workflow,
  XCircle,
} from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [threadId, setThreadId] = useState(
    () => sessionStorage.getItem("stateflow_thread") || "demo-001"
  );
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [trace, setTrace] = useState([]);
  const [state, setState] = useState(null);
  const [pending, setPending] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  const [history, setHistory] = useState([]);
  
  React.useEffect(() => {
    fetchHistory();
  }, []);
  
  async function fetchHistory() {
    try {
      const response = await fetch(`${API_URL}/api/threads`);
      if (response.ok) {
        const data = await response.json();
        setHistory(data);
      }
    } catch (err) {
      console.error("Could not fetch history", err);
    }
  }
  
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState("");
  const [selectedModel, setSelectedModel] = useState("");

  React.useEffect(() => {
    fetch(`${API_URL}/api/models`)
      .then(r => r.json())
      .then(data => {
        if (data.providers && data.providers.length > 0) {
          setProviders(data.providers);
          setSelectedProvider(data.providers[0].id);
          setSelectedModel(data.providers[0].models[0]);
        }
      })
      .catch(console.error);
  }, []);

  const handleProviderChange = (e) => {
    const p = e.target.value;
    setSelectedProvider(p);
    const pObj = providers.find(x => x.id === p);
    if (pObj && pObj.models.length > 0) {
      setSelectedModel(pObj.models[0]);
    } else {
      setSelectedModel("");
    }
  };

  const graphStatus = useMemo(() => {
    if (pending) return "Human approval required";
    if (loading) return "Running graph";
    return "Ready";
  }, [loading, pending]);

  async function refreshState(id = threadId) {
    const response = await fetch(`${API_URL}/api/state/${encodeURIComponent(id)}`);
    if (!response.ok) throw new Error("Could not load thread state.");
    const data = await response.json();
    setState(data);
    setTrace(data.values?.trace || []);
    setPending(data.pending_interrupt ? { type: "human_approval" } : null);
    setMessages(data.messages || data.values?.messages || []);
  }

  async function loadThread(id) {
    setThreadId(id);
    sessionStorage.setItem("stateflow_thread", id);
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/api/threads/${encodeURIComponent(id)}`);
      if (!response.ok) throw new Error("Could not load thread.");
      const data = await response.json();
      setState(data.state || null);
      setTrace(data.state?.values?.trace || []);
      setPending(data.state?.pending_interrupt ? { type: "human_approval" } : null);
      setMessages(data.messages || data.state?.values?.messages || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function sendMessage() {
    const text = message.trim();
    if (!text || loading) return;

    setLoading(true);
    setError("");
    sessionStorage.setItem("stateflow_thread", threadId);

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          thread_id: threadId, 
          message: text,
          provider: selectedProvider,
          model: selectedModel 
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail?.message || data.detail || "Request failed.");
      }

      setMessage("");
      setState({
        thread_id: data.thread_id,
        values: data.state,
        next_nodes: data.next_nodes,
        pending_interrupt: Boolean(data.pending_interrupt),
      });
      setMessages(data.state?.messages || []);
      setTrace(data.trace || []);
      setPending(data.pending_interrupt || null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      fetchHistory();
    }
  }

  async function resume(decision) {
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/api/resume`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          thread_id: threadId, 
          decision,
          provider: selectedProvider,
          model: selectedModel 
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail?.message || data.detail || "Resume failed.");
      }

      setState({
        thread_id: data.thread_id,
        values: data.state,
        next_nodes: data.next_nodes,
        pending_interrupt: Boolean(data.pending_interrupt),
      });
      setMessages(data.state?.messages || []);
      setTrace(data.trace || []);
      setPending(data.pending_interrupt || null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      fetchHistory();
    }
  }

  function newThread() {
    const next = `demo-${Date.now().toString().slice(-6)}`;
    setThreadId(next);
    sessionStorage.setItem("stateflow_thread", next);
    setMessages([]);
    setTrace([]);
    setState(null);
    setPending(null);
    setError("");
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark"><Workflow size={20} /></div>
          <div>
            <div className="brand-name">StateFlow</div>
            <div className="brand-subtitle">L2-05 · Stateful LangGraph Agent</div>
          </div>
        </div>
        <div className="status-pill">
          <span className={`status-dot ${pending ? "warning" : ""}`} />
          {graphStatus}
        </div>
      </header>

      <main className="workspace">
        <section className="hero">
          <div>
            <span className="eyebrow">OS3 AI ENGINEER EVALUATION</span>
            <h1>Stateful conversation, explicit orchestration.</h1>
            <p>
              A focused LangGraph StateGraph with conditional routing,
              persistent thread checkpoints, and real human-in-the-loop
              interruption.
            </p>
          </div>
          <div className="hero-badge">
            <GitBranch size={17} />
            StateGraph
          </div>
        </section>

        <section className="control-row">
          <label>
            <span>Provider</span>
            <select value={selectedProvider} onChange={handleProviderChange}>
              {providers.map(p => (
                <option key={p.id} value={p.id}>{p.id}</option>
              ))}
            </select>
          </label>
          <label>
            <span>Model</span>
            <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
              {(providers.find(p => p.id === selectedProvider)?.models || []).map(m => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </label>
          <label>
            <span>Thread ID</span>
            <input value={threadId} onChange={(e) => setThreadId(e.target.value)} />
          </label>
          <button className="secondary" onClick={() => refreshState()} disabled={loading}>
            <RefreshCw size={16} />
            Load state
          </button>
          <button className="secondary" onClick={newThread}>
            New thread
          </button>
        </section>

        <section className="main-grid">
          <aside className="panel history-panel">
            <div className="panel-heading compact">
              <div>
                <span className="panel-kicker">HISTORY</span>
                <h2>Conversations</h2>
              </div>
            </div>
            <div className="thread-list">
              {history.length === 0 ? (
                <div className="muted" style={{ padding: "10px" }}>No past conversations</div>
              ) : (
                history.map((t) => (
                  <div 
                    key={t.thread_id} 
                    className={`thread-item ${t.thread_id === threadId ? "active" : ""}`}
                    onClick={() => loadThread(t.thread_id)}
                  >
                    <div className="thread-item-title">{t.title || "Untitled Conversation"}</div>
                    <div className="thread-item-date">{new Date(t.updated_at).toLocaleString()}</div>
                  </div>
                ))
              )}
            </div>
          </aside>

          <div className="panel chat-panel">
            <div className="panel-heading">
              <div>
                <span className="panel-kicker">CONVERSATION</span>
                <h2>Thread {threadId}</h2>
              </div>
              <Sparkles size={19} />
            </div>

            <div className="messages">
              {messages.length === 0 ? (
                <div className="empty-state">
                  <CircleDot size={28} />
                  <strong>No messages yet</strong>
                  <span>Send a message to start the graph.</span>
                </div>
              ) : (
                messages.map((item, index) => (
                  <div key={`${index}-${item.content}`} className={`message ${item.role}`}>
                    <span className="message-role">
                      {item.role === "user" ? "YOU" : "STATEFLOW"}
                    </span>
                    <p>{item.content}</p>
                  </div>
                ))
              )}
            </div>

            {pending && (
              <div className="approval-card">
                <div className="approval-icon"><ShieldCheck size={21} /></div>
                <div className="approval-copy">
                  <strong>Human approval required</strong>
                  <span>The graph is paused at the human approval node.</span>
                </div>
                <div className="approval-actions">
                  <button className="approve" onClick={() => resume("approve")} disabled={loading}>
                    <CheckCircle2 size={16} />
                    Approve
                  </button>
                  <button className="reject" onClick={() => resume("reject")} disabled={loading}>
                    <XCircle size={16} />
                    Reject
                  </button>
                </div>
              </div>
            )}

            <div className="composer">
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder="Ask something… or type “Please approve this action.”"
                disabled={loading || Boolean(pending)}
              />
              <button className="send" onClick={sendMessage} disabled={loading || !message.trim() || Boolean(pending)}>
                <Play size={17} />
                {loading ? "Running…" : "Run graph"}
              </button>
            </div>

            {error && <div className="error-box">{error}</div>}
          </div>

          <aside className="side-stack">
            <div className="panel">
              <div className="panel-heading compact">
                <div>
                  <span className="panel-kicker">STATE</span>
                  <h2>Current graph state</h2>
                </div>
              </div>
              <div className="state-list">
                <StateRow label="Thread" value={threadId} />
                <StateRow label="Intent" value={state?.values?.intent || "—"} />
                <StateRow
                  label="Approval"
                  value={state?.values?.requires_human_approval ? "required" : "not required"}
                />
                <StateRow label="Decision" value={state?.values?.human_decision || "—"} />
                <StateRow label="Next" value={state?.next_nodes?.join(", ") || "—"} />
              </div>
            </div>

            <div className="panel">
              <div className="panel-heading compact">
                <div>
                  <span className="panel-kicker">TRACE</span>
                  <h2>Node transitions</h2>
                </div>
              </div>
              <div className="trace">
                {trace.length === 0 ? (
                  <span className="muted">Trace will appear after execution.</span>
                ) : (
                  trace.map((item, index) => (
                    <div className="trace-row" key={`${item}-${index}`}>
                      <span>{String(index + 1).padStart(2, "0")}</span>
                      <strong>{item}</strong>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="panel scope-card">
              <span className="panel-kicker">SCOPE</span>
              <div className="scope-grid">
                <span>✓ StateGraph</span>
                <span>✓ Routing</span>
                <span>✓ Checkpointing</span>
                <span>✓ HITL</span>
                <span>✓ Resume</span>
                <span>✓ Pluggable LLM</span>
              </div>
            </div>
          </aside>
        </section>
      </main>
    </div>
  );
}

function StateRow({ label, value }) {
  return (
    <div className="state-row">
      <span>{label}</span>
      <strong title={value}>{value}</strong>
    </div>
  );
}

export default App;
