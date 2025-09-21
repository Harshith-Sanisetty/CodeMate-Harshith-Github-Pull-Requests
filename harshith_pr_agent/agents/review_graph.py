# harshith_pr_agent/agents/review_graph.py

import os
from typing import TypedDict
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END

from .prompts import BASE_PROMPT_TEMPLATE, PERSONAS, SYNTHESIS_PROMPT, PRReviewPanel


class GraphState(TypedDict):
    pr_url: str
    title: str
    description: str
    diff: str
    reviews: dict 
    synthesis: str 

def create_review_graph():
    """Creates the LangGraph agent for the expert panel review."""
    
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    
   
    def run_expert_reviewer(state: GraphState, persona_name: str) -> dict:
        """Runs a single expert reviewer persona."""
        print(f"--- Running {persona_name} Expert ---")
        persona_details = PERSONAS[persona_name]
        
        
        structured_llm = llm.with_structured_output(PRReviewPanel)
        
        
        prompt_template = ChatPromptTemplate.from_template(BASE_PROMPT_TEMPLATE)

        
        chain = prompt_template | structured_llm
        
        # 3. Prepare the input variables for the template
        input_data = {
            "persona": persona_details["persona"],
            "persona_description": persona_details["persona_description"],
            "title": state["title"],
            "description": state["description"],
            "diff": state["diff"]
        }
        
        
        review_panel = chain.invoke(input_data)
       

        review_dicts = [r.dict() for r in review_panel.reviews]
        
        current_reviews = state.get("reviews", {})
        current_reviews[persona_name] = review_dicts
        return {"reviews": current_reviews}

    def run_maintainability_reviewer(state: GraphState):
        return run_expert_reviewer(state, "Maintainability")

    def run_performance_reviewer(state: GraphState):
        return run_expert_reviewer(state, "Performance")

    def run_security_reviewer(state: GraphState):
        return run_expert_reviewer(state, "Security")

    def run_synthesizer(state: GraphState):
        """Synthesizes the reviews from all experts."""
        print("--- Synthesizing All Reviews ---")
        reviews = state["reviews"]
        
        
        text_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
        
       
        synthesis_prompt_template = ChatPromptTemplate.from_template(SYNTHESIS_PROMPT)

        
        synthesis_chain = synthesis_prompt_template | text_llm
        
       
        synthesis_input = {
            "maintainability_feedback": reviews.get("Maintainability", "No feedback."),
            "performance_feedback": reviews.get("Performance", "No feedback."),
            "security_feedback": reviews.get("Security", "No feedback.")
        }
        
        
        synthesis_result = synthesis_chain.invoke(synthesis_input).content
        # ===================================================================================

        return {"synthesis": synthesis_result}

   
    workflow = StateGraph(GraphState)

   
    workflow.add_node("maintainability", run_maintainability_reviewer)
    workflow.add_node("performance", run_performance_reviewer)
    workflow.add_node("security", run_security_reviewer)
    workflow.add_node("synthesizer", run_synthesizer)
    
    
    workflow.set_entry_point("maintainability")
    workflow.add_edge("maintainability", "performance")
    workflow.add_edge("performance", "security")
    workflow.add_edge("security", "synthesizer")
    workflow.add_edge("synthesizer", END)

    return workflow.compile()