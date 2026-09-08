import { useEffect, useRef, useState, type MouseEvent, type ReactNode } from "react";
import { Link } from "react-router-dom";

import NeuralBackground from "../components/background/NeuralBackground";
import CursorEffects from "../components/background/CursorEffects";

const MEMORY_LAYERS = [
  {
    tag: "Semantic",
    title: "Facts that stay",
    body: "Preferences, goals, and stable details you share — retrieved by meaning, not keyword.",
  },
  {
    tag: "Episodic",
    title: "Moments that matter",
    body: "Decisions and milestones from conversation, so the assistant can recall what happened — not just what was said.",
  },
  {
    tag: "Procedural",
    title: "How you want it to act",
    body: "Behavioural instructions live in their own layer and sit high in the prompt, so tone and format persist.",
  },
  {
    tag: "Documents",
    title: "Your knowledge base",
    body: "Upload .txt files. They are chunked, embedded, and searched with both BM25 and vectors.",
  },
  {
    tag: "Graph",
    title: "Who relates to what",
    body: "Subject–relation–object triples form a per-user graph. Queries pull a 2-hop neighbourhood around named entities.",
  },
  {
    tag: "Session",
    title: "The rolling window",
    body: "The last few turns stay in short-term memory so the current chat still feels like a conversation.",
  },
];

const PIPELINE = [
  { step: "01", label: "Query", hint: "Your message" },
  { step: "02", label: "BM25", hint: "Keyword hits" },
  { step: "03", label: "Vectors", hint: "Semantic hits" },
  { step: "04", label: "Memory", hint: "Facts & habits" },
  { step: "05", label: "Graph", hint: "2-hop facts" },
  { step: "06", label: "Ollama", hint: "Grounded answer" },
];

const SURFACES = [
  {
    name: "Chat",
    path: "/login",
    copy: "Grounded replies assembled from documents, memories, and graph facts.",
  },
  {
    name: "Documents",
    path: "/login",
    copy: "Ingest text, watch it become searchable chunks and graph triples.",
  },
  {
    name: "Memories",
    path: "/login",
    copy: "Inspect what the assistant stored — semantic, episodic, procedural.",
  },
  {
    name: "Graph",
    path: "/login",
    copy: "Pan and zoom the relationship map extracted from your world.",
  },
];

function TiltCard({
  className,
  children,
}: {
  className?: string;
  children: ReactNode;
}) {
  const ref = useRef<HTMLDivElement>(null);

  function onMove(event: MouseEvent<HTMLDivElement>) {
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const px = (event.clientX - rect.left) / rect.width;
    const py = (event.clientY - rect.top) / rect.height;
    el.style.setProperty("--tilt-x", `${(py - 0.5) * -8}deg`);
    el.style.setProperty("--tilt-y", `${(px - 0.5) * 10}deg`);
    el.style.setProperty("--spot-x", `${px * 100}%`);
    el.style.setProperty("--spot-y", `${py * 100}%`);
  }

  function onLeave() {
    const el = ref.current;
    if (!el) return;
    el.style.setProperty("--tilt-x", "0deg");
    el.style.setProperty("--tilt-y", "0deg");
  }

  return (
    <div
      ref={ref}
      className={className}
      onMouseMove={onMove}
      onMouseLeave={onLeave}
    >
      {children}
    </div>
  );
}

function Home() {
  const [activeStep, setActiveStep] = useState(0);
  const [paused, setPaused] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    function onScroll() {
      setScrolled(window.scrollY > 16);
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    if (paused) return;
    const id = window.setInterval(() => {
      setActiveStep((current) => (current + 1) % PIPELINE.length);
    }, 1600);
    return () => window.clearInterval(id);
  }, [paused]);

  useEffect(() => {
    const nodes = document.querySelectorAll(".home-reveal");
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
          }
        }
      },
      { threshold: 0.16, rootMargin: "0px 0px -8% 0px" },
    );
    nodes.forEach((node) => observer.observe(node));
    return () => observer.disconnect();
  }, []);

  return (
    <div className="home-page">
      <NeuralBackground />
      <CursorEffects />

      <header className={`home-nav${scrolled ? " is-scrolled" : ""}`}>
        <a href="#top" className="home-brand">
          <span className="home-logo" aria-hidden>
            ✦
          </span>
          <span>Mnemos</span>
        </a>

        <nav className="home-nav-links" aria-label="Page sections">
          <a href="#memory">Memory</a>
          <a href="#pipeline">How it works</a>
          <a href="#surfaces">Surfaces</a>
        </nav>

        <Link to="/login" className="home-nav-login">
          Login
        </Link>
      </header>

      <main>
        <section className="home-hero" id="top">
          <div className="home-hero-orb home-hero-orb-a" aria-hidden />
          <div className="home-hero-orb home-hero-orb-b" aria-hidden />

          <p className="home-kicker">Memory-augmented AI</p>
          <h1>
            An assistant that
            <span> remembers you.</span>
          </h1>
          <p className="home-lede">
            Mnemos combines hybrid retrieval, a personal knowledge graph, and
            layered memory — then asks a local model to answer from that
            context, not from thin air.
          </p>

          <div className="home-hero-actions">
            <Link to="/login" className="home-cta">
              Get started
            </Link>
            <a href="#pipeline" className="home-cta-ghost">
              See the pipeline
            </a>
          </div>

          <div className="home-hero-stats">
            <div>
              <strong>3</strong>
              <span>long-term memory types</span>
            </div>
            <div>
              <strong>2</strong>
              <span>retrievers, fused by rank</span>
            </div>
            <div>
              <strong>1</strong>
              <span>graph per person</span>
            </div>
          </div>
        </section>

        <section className="home-section" id="memory">
          <div className="home-section-head home-reveal">
            <p className="home-kicker">What it keeps</p>
            <h2>Six layers of context, one reply.</h2>
            <p>
              Hover a card. Each layer is a real subsystem in the backend —
              not a marketing metaphor.
            </p>
          </div>

          <div className="home-grid">
            {MEMORY_LAYERS.map((layer) => (
              <TiltCard key={layer.tag} className="home-card home-reveal">
                <span className="home-card-tag">{layer.tag}</span>
                <h3>{layer.title}</h3>
                <p>{layer.body}</p>
              </TiltCard>
            ))}
          </div>
        </section>

        <section className="home-section" id="pipeline">
          <div className="home-section-head home-reveal">
            <p className="home-kicker">How a message is answered</p>
            <h2>Retrieve, compose, then generate.</h2>
            <p>
              The chat endpoint is a black box on the client. Inside, this is
              the path every turn takes.
            </p>
          </div>

          <ol
            className="home-pipeline home-reveal"
            onMouseEnter={() => setPaused(true)}
            onMouseLeave={() => setPaused(false)}
          >
            {PIPELINE.map((item, index) => (
              <li key={item.step}>
                {index > 0 && <span className="home-pipeline-join" aria-hidden />}
                <button
                  type="button"
                  className={`home-pipe${activeStep === index ? " is-active" : ""}`}
                  onMouseEnter={() => {
                    setPaused(true);
                    setActiveStep(index);
                  }}
                  onFocus={() => {
                    setPaused(true);
                    setActiveStep(index);
                  }}
                >
                  <span className="home-pipe-step">{item.step}</span>
                  <span className="home-pipe-label">{item.label}</span>
                  <span className="home-pipe-hint">{item.hint}</span>
                </button>
              </li>
            ))}
          </ol>
        </section>

        <section className="home-section" id="surfaces">
          <div className="home-section-head home-reveal">
            <p className="home-kicker">Inside the app</p>
            <h2>Four rooms. One identity.</h2>
            <p>
              Sign in once. Chat, documents, memories, and the graph all
              filter by you.
            </p>
          </div>

          <div className="home-surfaces">
            {SURFACES.map((surface) => (
              <TiltCard key={surface.name} className="home-surface home-reveal">
                <h3>{surface.name}</h3>
                <p>{surface.copy}</p>
                <Link to={surface.path}>Enter via login →</Link>
              </TiltCard>
            ))}
          </div>
        </section>
      </main>

      <footer className="home-footer">
        <span>Mnemos</span>
        <Link to="/login">Login</Link>
      </footer>
    </div>
  );
}

export default Home;
