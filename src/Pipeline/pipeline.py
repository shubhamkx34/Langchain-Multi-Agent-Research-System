from src.Agents.Agents import build_search_agent, build_reader_agent, writer_chain, critic_chain

def run_research_pipeline(topic : str) -> dict:

    state = {}

    #search agent working 
    print("\n"+" ="*50)
    print("Search agent is working ...")
    print("="*50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}. You MUST use the 'web_search' tool. In your final output, you MUST explicitly copy the ENTIRE 'Top Target URLs for Deep Scraping' section AND the 'All Search Results & Snippets' section exactly as the tool provides them.")]
    })
    state["search_results"] = search_result['messages'][-1].content

    print("\n search result ",state['search_results'])


    #step 2 - reader agent 
    print("\n"+" ="*50)
    print("Reader agent is scraping top resources ...")
    print("="*50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"From the search results below for '{topic}', locate the 'Top Target URLs for Deep Scraping'. "
            f"You MUST use the 'scrape_url' tool to read them. "
            f"CRITICAL INSTRUCTION: After the tool returns the text, you MUST write a detailed, multi-paragraph synthesis of the extracted information in your final response. Do not output raw HTML or empty text.\n\n"
            f"Search Results:\n{state['search_results']}"
        )]
    })

    state['scraped_content'] = reader_result['messages'][-1].content

    # Fallback to ensure the pipeline doesn't break if the AI still returns a blank string
    if not state['scraped_content'].strip():
        state['scraped_content'] = "The Reader Agent failed to summarize the scraped content. Rely on the broad search snippets provided."
    print("\nscraped content: \n", state['scraped_content'])

    #step 3 - writer chain 

    print("\n"+" ="*50)
    print("Writer is drafting the report ...")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS (Broad Context) : \n {state['search_results']} \n\n"
        f"DETAILED SCRAPED CONTENT (Deep Evidence) : \n {state['scraped_content']}"
    )
    state["report"] = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })

    print("\n Final Report\n",state['report'])


    #critic report 

    print("\n"+" ="*50)
    print("Critic is reviewing the report ")
    print("="*50)

    state["feedback"] = critic_chain.invoke({
        "report": state['report']
    })

    print("\n critic report \n", state['feedback'])

    return state
