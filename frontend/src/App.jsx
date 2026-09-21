import React, { useMemo, useRef, useEffect, useState } from "react";
import {
  CheckCircle2,
  CircleDot,
  GitBranch,
  LayoutDashboard,
  MessageSquare,
  Play,
  Plus,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  Workflow,
  XCircle,
  Clock,
  CheckCheck,
} from "lucide-react";
import "./styles.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

/* ── Small helpers ─────────────────────────────────────────── */
function Badge({ children, variant = "gray" }) {
  return <span className={`badge badge-${variant}`}>{children}</span>;
}

function StateRow({ label, children }) {
  return (
    <div className="state-row">
      <span className="state-row-key">{label}</span>
      <span className="state-row-value">{children}</span>
    </div>
  );
}

function IntentBadge({ intent }) {
  if (!intent || intent === "—") return <Badge variant="gray">—</Badge>;
  const map = { general: "blue", clarification: "amber", human_approval: "red" };
  return <Badge variant={map[intent] || "gray"}>{intent}</Badge>;
}

function ApprovalBadge({ required }) {
  if (required) return <Badge variant="amber">required</Badge>;
  return <Badge variant="green">not required</Badge>;
}

function DecisionBadge({ decision }) {
  if (!decision || decision === "—") return <Badge variant="gray">—</Badge>;
  if (decision === "approved") return <Badge variant="green">approved</Badge>;
  if (decision === "rejected") return <Badge variant="red">rejected</Badge>;
  return <Badge variant="gray">{decision}</Badge>;
}

/* ── Main App ──────────────────────────────────────────────── */
function App() {
  /* Thread state */
  const [threadId, setThreadId] = useState(
    () => sessionStorage.getItem("stateflow_thread") || "demo-001"
  );
  const [message, setMessage]   = useState("");
  const [messages, setMessages] = useState([]);
  const [trace, setTrace]       = useState([]);
  const [graphState, setGraphState] = useState(null);
  const [pending, setPending]   = useState(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");

  /* History */
  const [history, setHistory]   = useState([]);

  /* Providers / models */
  const [providers, setProviders]           = useState([]);
  const [selectedProvider, setSelectedProvider] = useState("");
  const [selectedModel, setSelectedModel]   = useState("");
  const [prevModel, setPrevModel]           = useState("");
  const [modelSwitched, setModelSwitched]   = useState(false);

  /* Inspector tab */
  const [inspTab, setInspTab] = useState("state");

  /* auto-scroll chat */
  const messagesEndRef = useRef(null);
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  /* load models */
  useEffect(() => {
    fetch(`${API_URL}/api/models`)
      .then((r) => r.json())
      .then((data) => {
        if (data.providers?.length > 0) {
          setProviders(data.providers);
          // Default to openrouter if available, else first
          const or = data.providers.find((p) => p.id === "openrouter");
          const def = or || data.providers[0];
          setSelectedProvider(def.id);
          setSelectedModel(def.models[0] || "");
          setPrevModel(def.models[0] || "");
        }
      })
      .catch(console.error);
  }, []);

  /* load history */
  useEffect(() => {
    fetchHistory();
  }, []);

  async function fetchHistory() {
    try {
      const r = await fetch(`${API_URL}/api/threads`);
      if (r.ok) setHistory(await r.json());
    } catch (e) { console.error("History error", e); }
  }

  /* computed status */
  const graphStatus = useMemo(() => {
    if (pending) return "Awaiting approval";
    if (loading) return "Running graph…";
    return "Ready";
  }, [loading, pending]);

  const statusDotClass = pending ? "warning" : loading ? "warning" : "";

  /* provider change */
  const handleProviderChange = (e) => {
    const p = e.target.value;
    setSelectedProvider(p);
    const pObj = providers.find((x) => x.id === p);
    const firstModel = pObj?.models[0] || "";
    setSelectedModel(firstModel);
  };

  /* model change with switch indicator */
  const handleModelChange = (e) => {
    const m = e.target.value;
    if (m !== selectedModel) {
      setPrevModel(selectedModel);
      setSelectedModel(m);
      setModelSwitched(true);
      setTimeout(() => setModelSwitched(false), 3500);
    }
  };

  /* refresh state */
  async function refreshState(id = threadId) {
    const r = await fetch(`${API_URL}/api/state/${encodeURIComponent(id)}`);
    if (!r.ok) throw new Error("Could not load thread state.");
    const data = await r.json();
    setGraphState(data);
    setTrace(data.values?.trace || []);
    setPending(data.pending_interrupt ? { type: "human_approval" } : null);
    setMessages(data.messages || data.values?.messages || []);
  }

  /* load thread from history */
  async function loadThread(id) {
    setThreadId(id);
    sessionStorage.setItem("stateflow_thread", id);
    setLoading(true);
    setError("");
    try {
      const r = await fetch(`${API_URL}/api/threads/${encodeURIComponent(id)}`);
      if (!r.ok) throw new Error("Could not load thread.");
      const data = await r.json();
      setGraphState(data.state || null);
      setTrace(data.state?.values?.trace || []);
      setPending(data.state?.pending_interrupt ? { type: "human_approval" } : null);
      setMessages(data.messages || data.state?.values?.messages || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  /* send message */
  async function sendMessage() {
    const text = message.trim();
    if (!text || loading) return;
    setLoading(true);
    setError("");
    sessionStorage.setItem("stateflow_thread", threadId);
    try {
      const r = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          thread_id: threadId,
          message: text,
          provider: selectedProvider,
          model: selectedModel,
        }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail?.message || data.detail || "Request failed.");
      setMessage("");
      setGraphState({
        thread_id: data.thread_id,
        values: data.state,
        next_nodes: data.next_nodes,
        pending_interrupt: Boolean(data.pending_interrupt),
      });
      setMessages(data.state?.messages || []);
      setTrace(data.trace || []);
      setPending(data.pending_interrupt || null);
      if (data.pending_interrupt) setInspTab("hitl");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
      fetchHistory();
    }
  }

  /* resume HITL */
  async function resume(decision) {
    setLoading(true);
    setError("");
    try {
      const r = await fetch(`${API_URL}/api/resume`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          thread_id: threadId,
          decision,
          provider: selectedProvider,
          model: selectedModel,
        }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail?.message || data.detail || "Resume failed.");
      setGraphState({
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

  /* new thread */
  function newThread() {
    const next = `demo-${Date.now().toString().slice(-6)}`;
    setThreadId(next);
    sessionStorage.setItem("stateflow_thread", next);
    setMessages([]);
    setTrace([]);
    setGraphState(null);
    setPending(null);
    setError("");
  }

  const currentModels = providers.find((p) => p.id === selectedProvider)?.models || [];
  const isMock = selectedProvider === "mock";

  /* ── Render ─────────────────────────────────────────────── */
  return (
    <div className="app-shell">

      {/* ── Header ─────────────────────────────────────────── */}
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark"><Workflow size={17} /></div>
          <div className="brand-text">
            <span className="brand-name">StateFlow</span>
            <span className="brand-sub">L2-05 · Stateful LangGraph Agent</span>
          </div>
        </div>

        <div className="header-center">
          <div className="hero-desc">
            Conditional routing, persistent checkpoints, and human-in-the-loop control
            <span className="badge badge-blue" style={{ gap: 5 }}>
              <GitBranch size={9} /> StateGraph
            </span>
          </div>
        </div>

        <div className="status-pill">
          <span className={`status-dot ${statusDotClass}`} />
          {graphStatus}
        </div>
      </header>

      {/* ── Workspace ──────────────────────────────────────── */}
      <div className="workspace">

        {/* ── Control Bar ──────────────────────────────────── */}
        <div className="control-bar">

          {/* Conversation controls */}
          <span className="ctrl-label">THREAD</span>
          <input
            className="thread-input"
            value={threadId}
            onChange={(e) => setThreadId(e.target.value)}
            placeholder="thread-id"
            aria-label="Thread ID"
          />
          <button
            className="btn btn-ghost"
            onClick={() => refreshState()}
            disabled={loading}
            title="Load saved graph state"
            aria-label="Load state"
          >
            <RefreshCw size={13} />
            Load state
          </button>
          <button
            className="btn btn-ghost"
            onClick={newThread}
            title="Start a new conversation thread"
            aria-label="New thread"
          >
            <Plus size={13} />
            New thread
          </button>

          <div className="ctrl-divider" />

          {/* LLM controls */}
          <span className="ctrl-label">PROVIDER</span>
          <select
            className={`custom-select provider-${selectedProvider}`}
            value={selectedProvider}
            onChange={handleProviderChange}
            aria-label="Select provider"
          >
            {providers.map((p) => (
              <option key={p.id} value={p.id}>
                {p.id === "openrouter" ? "OpenRouter" :
                 p.id === "mock"       ? "Mock (test)" :
                 p.id === "ollama"     ? "Ollama" :
                 p.id === "gemini"     ? "Gemini" : p.id}
              </option>
            ))}
          </select>

          <span className="ctrl-label">MODEL</span>
          <select
            className="custom-select"
            value={selectedModel}
            onChange={handleModelChange}
            aria-label="Select model"
          >
            {currentModels.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>

          {/* Active model badge */}
          {selectedModel && (
            <div className={`model-badge ${isMock ? "mock" : ""}`} title={`${selectedProvider} / ${selectedModel}`}>
              {isMock ? "mock" : selectedModel}
            </div>
          )}
        </div>

        {/* loading bar */}
        {loading && <div className="loading-bar" />}

        {/* ── 3-Column Main Grid ────────────────────────────── */}
        <div className="main-grid">

          {/* ── Col 1: History ─────────────────────────────── */}
          <aside className="panel history-col">
            <div className="panel-header">
              <div>
                <span className="panel-kicker">HISTORY</span>
                <span className="panel-title">Conversations</span>
              </div>
            </div>
            <div className="history-actions">
              <button className="btn btn-ghost" style={{ width: "100%", justifyContent: "flex-start" }} onClick={newThread}>
                <Plus size={13} /> New conversation
              </button>
            </div>
            <div className="thread-scroll" role="list">
              {history.length === 0 ? (
                <div className="history-empty">
                  <MessageSquare size={22} />
                  <span>No conversations yet</span>
                </div>
              ) : (
                history.map((t) => (
                  <div
                    key={t.thread_id}
                    className={`thread-item ${t.thread_id === threadId ? "active" : ""}`}
                    onClick={() => loadThread(t.thread_id)}
                    role="listitem"
                    tabIndex={0}
                    onKeyDown={(e) => e.key === "Enter" && loadThread(t.thread_id)}
                    aria-label={`Load thread: ${t.title || t.thread_id}`}
                  >
                    <div className="thread-item-title">{t.title || "Untitled"}</div>
                    <div className="thread-item-date">
                      {new Date(t.updated_at).toLocaleString(undefined, {
                        month: "short", day: "numeric",
                        hour: "2-digit", minute: "2-digit",
                      })}
                    </div>
                  </div>
                ))
              )}
            </div>
          </aside>

          {/* ── Col 2: Chat ────────────────────────────────── */}
          <div className="panel chat-col">
            <div className="panel-header">
              <div className="chat-header-info">
                <span className="panel-kicker">CONVERSATION</span>
                <span className="panel-title">
                  Thread <span className="chat-thread-id">{threadId}</span>
                </span>
              </div>
              {selectedModel && (
                <div className={`model-badge ${isMock ? "mock" : ""}`} style={{ fontSize: 10 }}>
                  {selectedProvider === "openrouter" ? "OpenRouter" : selectedProvider}
                  {" · "}{selectedModel}
                </div>
              )}
            </div>

            {/* model switched toast */}
            {modelSwitched && (
              <div className="model-switch-toast">
                <CheckCheck size={11} />
                Model switched to {selectedModel} — thread preserved
              </div>
            )}

            {/* messages */}
            <div className="messages" role="log" aria-live="polite">
              {messages.length === 0 ? (
                <div className="empty-state">
                  <div className="empty-state-icon"><CircleDot size={28} /></div>
                  <strong>No messages yet</strong>
                  <span>Send a message to start the graph.</span>
                </div>
              ) : (
                messages.map((item, i) => (
                  <div key={`${i}-${item.content?.slice(0,20)}`} className={`message ${item.role}`}>
                    <span className="message-role">{item.role === "user" ? "YOU" : "STATEFLOW"}</span>
                    <p>{item.content}</p>
                  </div>
                ))
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* HITL card inside chat */}
            {pending && (
              <div className="hitl-card" role="alert">
                <ShieldAlert size={18} className="hitl-icon" />
                <div className="hitl-body">
                  <div className="hitl-title">GRAPH PAUSED — Human approval required</div>
                  <div className="hitl-sub">The graph is interrupted at the human approval node.</div>
                </div>
                <div className="hitl-actions">
                  <button className="btn btn-approve" onClick={() => resume("approve")} disabled={loading} aria-label="Approve">
                    <CheckCircle2 size={13} /> Approve
                  </button>
                  <button className="btn btn-reject" onClick={() => resume("reject")} disabled={loading} aria-label="Reject">
                    <XCircle size={13} /> Reject
                  </button>
                </div>
              </div>
            )}

            {/* error */}
            {error && <div className="error-box" role="alert">{error}</div>}

            {/* composer */}
            <div className="composer">
              <div className="composer-inner">
                <textarea
                  className="composer-input"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                  placeholder='Ask something…'
                  disabled={loading || Boolean(pending)}
                  aria-label="Message input"
                  rows={2}
                />
                <button
                  className="btn btn-primary"
                  onClick={sendMessage}
                  disabled={loading || !message.trim() || Boolean(pending)}
                  aria-label="Run graph"
                  style={{ height: 44, alignSelf: "flex-end" }}
                >
                  <Play size={14} />
                  {loading ? "Running…" : "Run graph"}
                </button>
              </div>
              <div className="composer-hint">
                Tip: type "Please approve this action." to trigger HITL · Shift+Enter for new line
              </div>
            </div>
          </div>

          {/* ── Col 3: Graph Inspector ──────────────────────── */}
          <aside className="panel inspector-col">
            <div className="panel-header">
              <div>
                <span className="panel-kicker">GRAPH INSPECTOR</span>
                <span className="panel-title">LangGraph Monitor</span>
              </div>
              <LayoutDashboard size={15} style={{ color: "var(--blue)" }} />
            </div>

            {/* Tabs */}
            <div className="inspector-tabs" role="tablist">
              {[
                { id: "state", label: "STATE" },
                { id: "trace", label: "TRACE" },
                { id: "hitl",  label: "HITL",  extra: pending ? "has-pending" : "" },
              ].map((tab) => (
                <button
                  key={tab.id}
                  className={`inspector-tab ${tab.id === "hitl" ? "hitl-tab" : ""} ${tab.extra || ""} ${inspTab === tab.id ? "active" : ""}`}
                  onClick={() => setInspTab(tab.id)}
                  role="tab"
                  aria-selected={inspTab === tab.id}
                  aria-label={`${tab.label} inspector`}
                >
                  {tab.label}
                  {tab.id === "hitl" && pending && (
                    <span style={{ marginLeft: 4, color: "var(--amber)", fontSize: 10 }}>●</span>
                  )}
                </button>
              ))}
            </div>

            {/* Tab bodies */}
            <div className="inspector-body" role="tabpanel">

              {/* STATE tab */}
              {inspTab === "state" && (
                <>
                  <div className="state-section-title">CURRENT STATE</div>
                  <StateRow label="Thread">
                    <span style={{ fontFamily: "var(--mono)", fontSize: 10 }}>{threadId}</span>
                  </StateRow>
                  <StateRow label="Intent">
                    <IntentBadge intent={graphState?.values?.intent || "—"} />
                  </StateRow>
                  <StateRow label="Approval">
                    <ApprovalBadge required={graphState?.values?.requires_human_approval} />
                  </StateRow>
                  <StateRow label="Decision">
                    <DecisionBadge decision={graphState?.values?.human_decision || "—"} />
                  </StateRow>
                  <StateRow label="Next">
                    {graphState?.next_nodes?.join(", ") ? (
                      <Badge variant="blue">{graphState.next_nodes.join(", ")}</Badge>
                    ) : <Badge variant="gray">—</Badge>}
                  </StateRow>

                  {/* Scope summary */}
                  <div className="scope-section">
                    <div className="state-section-title">L2-05 SCOPE</div>
                    <div className="scope-grid">
                      {[
                        "StateGraph", "Routing", "Checkpointing",
                        "HITL", "Resume", "Pluggable LLM",
                      ].map((f) => (
                        <div key={f} className="scope-item">
                          <CheckCircle2 size={10} /> {f}
                        </div>
                      ))}
                    </div>
                  </div>
                </>
              )}

              {/* TRACE tab */}
              {inspTab === "trace" && (
                <>
                  <div className="state-section-title">NODE TRANSITIONS</div>
                  {trace.length === 0 ? (
                    <span className="muted">Trace will appear after graph execution.</span>
                  ) : (
                    <div className="trace-flow">
                      {trace.map((node, i) => (
                        <React.Fragment key={`${node}-${i}`}>
                          <div className="trace-node">
                            <div className="trace-node-num">{i + 1}</div>
                            <span className={`trace-node-name ${node === "INTERRUPT" ? "interrupt" : ""}`}>
                              {node}
                            </span>
                          </div>
                          {i < trace.length - 1 && (
                            <div className="trace-arrow">↓</div>
                          )}
                        </React.Fragment>
                      ))}
                    </div>
                  )}
                </>
              )}

              {/* HITL tab */}
              {inspTab === "hitl" && (
                <>
                  <div className="state-section-title">HUMAN-IN-THE-LOOP</div>

                  {!pending && !graphState?.values?.human_decision && (
                    <div className="hitl-status-idle">
                      <ShieldCheck size={26} />
                      <strong style={{ color: "var(--text-3)", fontSize: 12 }}>Human approval not required</strong>
                      <span>Send a message that requires approval to trigger HITL.</span>
                    </div>
                  )}

                  {pending && (
                    <>
                      <div className="hitl-interrupt-banner">
                        <div className="hitl-interrupt-label">GRAPH PAUSED</div>
                        <div className="hitl-interrupt-title">Human approval required</div>
                        <div className="hitl-interrupt-sub">
                          The LangGraph execution is interrupted at the human_approval node.
                        </div>
                      </div>
                      <div className="hitl-action-row">
                        <button
                          className="btn btn-approve"
                          onClick={() => resume("approve")}
                          disabled={loading}
                          aria-label="Approve action"
                        >
                          <CheckCircle2 size={15} /> Approve
                        </button>
                        <button
                          className="btn btn-reject"
                          onClick={() => resume("reject")}
                          disabled={loading}
                          aria-label="Reject action"
                        >
                          <XCircle size={15} /> Reject
                        </button>
                      </div>
                    </>
                  )}

                  {!pending && graphState?.values?.human_decision && (
                    <div className="hitl-decision-card">
                      <div className="hitl-decision-label">LAST DECISION</div>
                      <DecisionBadge decision={graphState.values.human_decision} />
                      <div style={{ fontSize: 10, color: "var(--text-3)", marginTop: 8 }}>
                        Graph resumed successfully.
                      </div>
                    </div>
                  )}
                </>
              )}

            </div>
          </aside>

        </div>{/* end main-grid */}
      </div>{/* end workspace */}
    </div>
  );
}

export default App;
