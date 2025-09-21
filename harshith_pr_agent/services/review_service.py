

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from harshith_pr_agent.connectors.github_connector import GitHubConnector
from harshith_pr_agent.agents.review_graph import create_review_graph
from harshith_pr_agent.agents.prompts import CHATBOT_PROMPT

load_dotenv()


BOT_SIGNATURE = ""

def format_review_as_markdown(review_result: dict) -> str:
    """Helper function to format the entire review result into a single Markdown string."""
    summary = review_result.get('synthesis', "No summary generated.")
    reviews = review_result.get('reviews', {})

    markdown_report = f"## Harshith PR Agent Review\n\n"
    markdown_report += f"### 📜 Final Summary & Code Quality Score\n{summary}\n\n"
    markdown_report += "---\n\n### 🔬 Detailed Feedback from the Expert Panel\n\n"

    for expert, findings in reviews.items():
        markdown_report += f"#### 🕵️‍♂️ {expert} Expert Feedback ({len(findings)} issues found)\n"
        if findings:
            for finding in findings:
                markdown_report += f"- **File:** `{finding['file_path']}` (Line: {finding['line_number']})\n"
                markdown_report += f"  - **Priority:** {finding['priority']}\n"
                markdown_report += f"  - **Comment:** {finding['comment']}\n"
                if finding.get('suggestion'):
                    markdown_report += f"  - **Suggestion:**\n    ```suggestion\n    {finding['suggestion']}\n    ```\n"
            markdown_report += "\n"
        else:
            markdown_report += "_No issues found by this expert._\n\n"
    
    
    markdown_report += f"\n{BOT_SIGNATURE}"
    return markdown_report

def run_graph_review(pr_url: str, post_to_github: bool = False) -> dict:
    if not os.getenv("GOOGLE_API_KEY"): raise ValueError("GOOGLE_API_KEY not found.")
    
    print("--- Fetching PR Data from GitHub ---")
    connector = GitHubConnector()
    metadata = connector.get_pr_metadata(pr_url)
    diff = connector.get_pr_diff(pr_url)
    print("--- Data Fetched Successfully ---")

    app = create_review_graph()
    initial_state = {"pr_url": pr_url, "title": metadata.get("title"), "description": metadata.get("description"), "diff": diff}
    final_state = app.invoke(initial_state)

    if post_to_github:
        full_report = format_review_as_markdown(final_state)
        connector.post_comment(pr_url, full_report)
            
    return final_state

def run_chatbot_response(pr_url: str, question: str):
    if not os.getenv("GOOGLE_API_KEY"): raise ValueError("GOOGLE_API_KEY not found.")
    
    print(f"--- Running chatbot for question: '{question}' ---")
    connector = GitHubConnector()
    
    diff = connector.get_pr_diff(pr_url)
    comments = connector.get_pr_comments(pr_url)
    
    initial_report = ""
    for comment in reversed(comments):
        if BOT_SIGNATURE in comment.get('body', ''):
            initial_report = comment['body']
            break
            
    if not initial_report:
        initial_report = "Could not find the initial report. Please answer based on the code changes alone."

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)
    prompt_template = ChatPromptTemplate.from_template(CHATBOT_PROMPT)
    chain = prompt_template | llm
    
    answer = chain.invoke({
        "diff": diff,
        "initial_report": initial_report,
        "question": question
    }).content
    
    
    final_answer = f"{answer}\n\n{BOT_SIGNATURE}"
    connector.post_comment(pr_url, final_answer)
    print("--- Chatbot response posted successfully ---")