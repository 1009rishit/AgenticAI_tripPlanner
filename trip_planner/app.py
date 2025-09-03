import streamlit as st
from orchestration import ConversationalOrchestrator
from datetime import date

st.set_page_config(page_title="AI Trip Planner", page_icon=":airplane:")

st.title("🌍 AI Trip Planner")
st.markdown("Ask me anything about your trip, and I'll help you plan it!")

# Initialize ConversationalOrchestrator and session state
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = ConversationalOrchestrator()
    st.session_state.initial_details_collected = False
    st.session_state.chat_submitted = False # Initialize chat_submitted

# --- Initial Trip Details Collection ---
if not st.session_state.initial_details_collected:
    st.header("Let's start by planning your trip!")
    
    with st.form("initial_trip_form"):
        destination = st.text_input("Where are you going?", key="initial_destination")
        start_date = st.date_input("Start Date", key="initial_start_date")
        end_date = st.date_input("End Date", key="initial_end_date")
        travelers = st.number_input("Number of Travelers", min_value=1, value=1, key="initial_travelers")
        
        submit_initial_details = st.form_submit_button("Plan My Trip")
        
        if submit_initial_details:
            if destination:
                st.session_state.orchestrator.context["destination"] = destination
                st.session_state.orchestrator.context["start_date"] = start_date.strftime("%Y-%m-%d")
                st.session_state.orchestrator.context["end_date"] = end_date.strftime("%Y-%m-%d")
                st.session_state.orchestrator.context["travelers"] = travelers
                st.session_state.initial_details_collected = True
                st.success("Trip details saved! You can now chat with the AI planner.")
                st.rerun() # Rerun to switch to chat interface
            else:
                st.error("Please enter a destination to plan your trip.")

# --- Main Chat Interface ---
if st.session_state.initial_details_collected:
    # Display chat messages from history on app rerun
    for message in st.session_state.orchestrator.conversation_history:
        with st.chat_message("user" if message["role"] == "user" else "assistant"):
            st.markdown(message["content"])

    # React to user input
    user_input = st.chat_input("Ask me about your trip:")

    if user_input:
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Process user input and get response
        result = st.session_state.orchestrator.process_user_input(user_input)
        intent = result["intent"]
        response = result["response"]
        context_summary = st.session_state.orchestrator.get_context_summary()

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
            st.markdown(context_summary)
        
        # Add to conversation history for display
        st.session_state.orchestrator.conversation_history.append({"role": "user", "content": user_input})
        st.session_state.orchestrator.conversation_history.append({"role": "assistant", "content": f"{response}\n{context_summary}"})
        st.session_state.chat_submitted = False # Reset for next input
        st.rerun() # Rerun to clear input and update display
