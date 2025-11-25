import os
import sys
from dotenv import load_dotenv
import json
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import streamlit as st
from src.agents.graph import RAGGraph
from src.cache import RedisCache
from src.observability import get_tracker

st.set_page_config(page_title="Self-Correcting RAG", layout="wide")

st.title("🤖 Self-Correcting RAG System")
st.markdown("""
Advanced multi-agent RAG pipeline with self-correction, caching, and full observability.
""")

# Initialize systems
if "graph" not in st.session_state:
    try:
        st.session_state.graph = RAGGraph()
        st.success("✅ System initialized successfully!")
    except Exception as e:
        st.error(f"❌ Failed to initialize: {e}")
        st.stop()

# Sidebar for system stats
with st.sidebar:
    st.header("📊 System Statistics")
    
    # Cache stats
    try:
        cache = RedisCache()
        cache_stats = cache.get_stats()
        st.metric("Cache Hit Rate", f"{cache_stats.get('hit_rate', 0):.1%}")
        st.metric("Total Cached Keys", cache_stats.get('total_keys', 0))
    except:
        st.info("Cache stats unavailable")
    
    # Tracker stats
    try:
        tracker = get_tracker()
        tracker_stats = tracker.get_summary_stats()
        st.metric("Total Queries", tracker_stats.get('total_runs', 0))
        st.metric("Avg Response Time", f"{tracker_stats.get('avg_response_time', 0):.2f}s")
        st.metric("Avg Tokens/Query", f"{tracker_stats.get('avg_tokens_per_run', 0):.0f}")
    except:
        st.info("Tracking stats unavailable")

# Main interface
col1, col2 = st.columns([3, 1])

with col1:
    question = st.text_input("Ask a question:", "What are transformers in AI and how do they work?")

with col2:
    show_logs = st.checkbox("Show Full Logs", value=False)

if st.button("🚀 Run Query", type="primary"):
    if question:
        with st.spinner("Processing..."):
            try:
                result = st.session_state.graph.run(question)
                
                # Get the latest log file
                log_dir = Path("logs")
                if log_dir.exists():
                    log_files = sorted(log_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
                    if log_files:
                        with open(log_files[0], 'r', encoding='utf-8') as f:
                            log_data = json.load(f)
                
                # Display chain-of-thought in tabs
                tab1, tab2, tab3 = st.tabs(["💬 Answer", "🔍 Chain of Thought", "📈 Metrics"])
                
                with tab1:
                    final_answer = result.get("final_answer", "No answer generated")
                    
                    if final_answer != "No answer generated":
                        # Stream the answer
                        answer_placeholder = st.empty()
                        displayed_text = ""
                        
                        import time
                        for char in final_answer:
                            displayed_text += char
                            answer_placeholder.markdown(displayed_text + "▌")
                            time.sleep(0.01)
                        
                        answer_placeholder.markdown(final_answer)
                    else:
                        st.error("I couldn't generate an answer. Please try rephrasing your question.")
                
                with tab2:
                    st.subheader("🔗 Pipeline Execution Flow")
                    
                    if "log_data" in locals():
                        # Show each step
                        for step in log_data.get("steps", []):
                            step_type = step.get("step", "unknown")
                            
                            if step_type == "retrieval":
                                with st.expander("📚 **Step 1: Retrieval**", expanded=True):
                                    st.write(f"**Source:** {step.get('source')}")
                                    st.write(f"**Documents Retrieved:** {step.get('num_results')}")
                                    if show_logs:
                                        for i, doc in enumerate(step.get('results', [])[:3]):
                                            st.markdown(f"**Doc {i+1}:** {doc.get('text', '')[:150]}...")
                            
                            elif step_type == "generation":
                                with st.expander("✍️ **Step 2: Initial Generation**", expanded=True):
                                    st.write(f"**Answer:** {step.get('answer', '')[:200]}...")
                                    st.write(f"**Tokens:** {step.get('tokens', 0)}")
                            
                            elif step_type == "validation":
                                with st.expander("🔍 **Step 3: Self-Critique**", expanded=True):
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        st.metric("Complete", "✓" if step.get('is_complete') else "✗")
                                    with col2:
                                        st.metric("Outdated", "⚠️" if step.get('is_outdated') else "✓")
                                    with col3:
                                        st.metric("Score", f"{step.get('score', 0):.1%}")
                                    
                                    if step.get('gaps'):
                                        st.markdown("**Gaps:**")
                                        for gap in step.get('gaps', []):
                                            st.markdown(f"- {gap}")
                                    
                                    if step.get('reasoning'):
                                        st.info(step.get('reasoning'))
                            
                            elif step_type == "tool_call":
                                with st.expander(f"🔧 **Step 4: Tool Call - {step.get('tool_name')}**", expanded=True):
                                    st.write(f"**Input:** {step.get('input')}")
                                    st.write(f"**Success:** {'✓' if step.get('success') else '✗'}")
                                    if show_logs:
                                        st.code(step.get('result', '')[:300])
                            
                            elif step_type == "synthesis":
                                with st.expander("🎨 **Step 5: Final Synthesis**", expanded=True):
                                    st.write(f"**Sources Used:** {', '.join(step.get('sources_used', []))}")
                                    st.write(f"**Tokens:** {step.get('tokens', 0)}")
                    else:
                        st.info("No detailed logs available for this query.")
                
                with tab3:
                    st.subheader("📊 Query Metrics")
                    
                    if "log_data" in locals():
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Total Time", f"{log_data.get('metrics', {}).get('total_time', 0):.2f}s")
                        with col2:
                            st.metric("Total Tokens", log_data.get('metrics', {}).get('total_tokens', 0))
                        with col3:
                            if log_data.get('cache_hit'):
                                st.metric("Cache", "HIT ✓", delta="Instant response")
                            else:
                                st.metric("Cache", "MISS", delta="Full pipeline")
                
            except Exception as e:
                st.error(f"An error occurred: {e}")
                import traceback
                if show_logs:
                    st.code(traceback.format_exc())
    else:
        st.warning("Please enter a question")

# Footer
st.markdown("---")
st.caption("Self-Correcting RAG with CrossEncoder re-ranking, Redis caching, and full observability")
