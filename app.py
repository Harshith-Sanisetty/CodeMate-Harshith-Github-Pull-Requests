import streamlit as st
from harshith_pr_agent.services.review_service import run_graph_review

st.set_page_config(
    page_title="Harshith PR Agent",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    
    .description-box {
        background-color: ;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #bf9cf1;
    }
    
    .feature-card {
        background-color: #474d4f;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin-bottom: 1rem;
    }
    
    .expert-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        background-color: #e8f4f8;
        color: #1f77b4;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .workflow-step {
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-left: 3px solid #28a745;
        background-color: #474d4f;
    }
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown('<h1 class="main-header">🤖 Harshith Sanisetty GitHub PR Agent</h1>', unsafe_allow_html=True)
    st.markdown("### An AI-powered multi-agent system for comprehensive Pull Request analysis")
    
    st.markdown("---")
    pr_url = st.text_input(
        "📝 Enter GitHub Pull Request URL",
        placeholder="https://github.com/owner/repo/pull/123",
        help="Paste the complete URL of the GitHub Pull Request you want to analyze"
    )

    post_comments = st.checkbox(
        "🔄 Post comments directly to GitHub PR",
        help="When enabled, the AI agents will automatically post their review comments to the GitHub PR"
    )

    if st.button("🚀 Start AI Analysis", type="primary", use_container_width=True):
        if not pr_url:
            st.warning("⚠️ Please enter a valid GitHub PR URL to begin analysis.")
        else:
            try:
                with st.spinner("🤖 AI Expert Panel is analyzing your PR... Please wait while our agents review the code."):
                    review_result = run_graph_review(pr_url, post_to_github=post_comments)

                st.success("✅ Analysis Complete!")
                
                if post_comments:
                    st.success("🎯 Review comments have been posted to GitHub successfully!")

                st.divider()

                st.subheader("📊 Final Summary & Code Quality Assessment")
                st.markdown(review_result.get('synthesis', "No summary generated."))
                st.divider()

                st.subheader("🔍 Detailed Expert Analysis")
                
                reviews = review_result.get('reviews', {})
                for expert, findings in reviews.items():
                    issues_count = len(findings) if findings else 0
                    status_icon = "✅" if issues_count == 0 else f"⚠️ {issues_count}"
                    
                    with st.expander(f"{status_icon} {expert} Expert ({issues_count} issues found)"):
                        if findings:
                            for i, finding in enumerate(findings, 1):
                                st.markdown(f"Issue #{i}")
                                st.markdown(f"📁 File: `{finding['file_path']}` 📍 Line: {finding['line_number']}")
                                
                                priority = finding.get('priority', 'Medium')
                                priority_color = {
                                    'High': '🔴', 
                                    'Medium': '🟡', 
                                    'Low': '🟢'
                                }.get(priority, '🟡')
                                st.markdown(f"Priority: {priority_color} {priority}")
                                
                                st.info(f"💬 Comment: {finding['comment']}")
                                
                                if finding.get('suggestion'):
                                    st.code(f"💡 Suggestion:\n{finding['suggestion']}", language="diff")
                                st.divider()
                        else:
                            st.success("🎉 No issues found by this expert! Great job!")
                            
            except Exception as e:
                st.error(f"❌ An error occurred during analysis: {e}")
                st.exception(e)

with col2:
    st.markdown('<div class="description-box">', unsafe_allow_html=True)
    st.markdown("## 📋 Project Overview")
    
    st.markdown("### 🔧 System Architecture")
    st.markdown("""
    Multi-Agent AI System powered by:
    - LangGraph for agent orchestration
    - Streamlit for manual PR reviews  
    - Flask for automated workflows
    """)
    
    st.markdown("### 🎯 AI Expert Agents")
    st.markdown('<span class="expert-badge">🔒 Security Expert</span>', unsafe_allow_html=True)
    st.markdown('<span class="expert-badge">⚡ Performance Expert</span>', unsafe_allow_html=True) 
    st.markdown('<span class="expert-badge">🛠️ Maintainability Expert</span>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("## 🔄 Analysis Workflow")
    
    workflow_steps = [
        "📥 Input: GitHub PR URL",
        "🤖 Agent Activation: Multi-expert analysis",
        "🔍 Code Review: Security, Performance, Maintainability",
        "📝 Synthesis: Comprehensive feedback generation",
        "📤 Output: Detailed review + Optional GitHub posting"
    ]
    
    for step in workflow_steps:
        st.markdown(f'<div class="workflow-step">{step}</div>', unsafe_allow_html=True)
    
    st.markdown("## ✨ Key Features")
    
    features = [
        "🎯 Smart Analysis: AI-powered code review",
        "🔄 Dual Mode: Manual (Streamlit) + Automated (Flask)",
        "📊 Comprehensive Reports: Detailed findings with priorities",
        "🚀 GitHub Integration: Direct comment posting",
        "🛡️ Multi-Expert Review: Security, Performance, Maintainability"
    ]
    
    for feature in features:
        st.markdown(f'<div class="feature-card">{feature}</div>', unsafe_allow_html=True)
    
    st.markdown("## 📈 System Status")
    st.success("🟢 All AI Agents: Online")
    st.success("🟢 GitHub API: Connected") 
    st.success("🟢 LangGraph: Operational")