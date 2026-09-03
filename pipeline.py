from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

def run_research_pipeline(topic: str) -> dict:
    state = {}

    # Step 1 - Search Agent
    print("\n" + "="*50)
    print("Step 1 - Search agent is working ...")
    print("="*50)

    search_agent = build_search_agent()
    try:
        search_result = search_agent.invoke({
            "messages": [("user", 
                f"Find recent, reliable and detailed information about: {topic}. "
                f"IMPORTANT: You MUST list the exact source URLs at the VERY TOP of your response, followed by your detailed findings."
            )]
        })
        state["search_results"] = search_result['messages'][-1].content
    except Exception as e:
        print(f"Search failed: {e}")
        return {"error": "Pipeline halted at search phase."}
    
    print("\nSearch Result:\n", state['search_results'])

    # Step 2 - Reader Agent
    print("\n" + "="*50)
    print("Step 2 - Reader agent is scraping top resources ...")
    print("="*50)

    reader_agent = build_reader_agent()
    try:
        reader_result = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{state['search_results'][:800]}" # The 800-character limit is active
            )]
        })
        state['scraped_content'] = reader_result['messages'][-1].content
    except Exception as e:
        print(f"Scraping failed: {e}")
        state['scraped_content'] = "No additional scraped content available due to an error."

    print("\nScraped Content:\n", state['scraped_content'])

    # Step 3 - Writer Chain
    print("\n" + "="*50)
    print("Step 3 - Writer is drafting the report ...")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    print("\nFinal Report:\n", state['report'])

    # Step 4 - Critic Chain
    print("\n" + "="*50)
    print("Step 4 - Critic is reviewing the report ...")
    print("="*50)

    state["feedback"] = critic_chain.invoke({
        "report": state['report']
    })

    print("\nCritic Report:\n", state['feedback'])

    return state

if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")
    run_research_pipeline(topic)