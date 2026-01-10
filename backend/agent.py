import os
import json
from typing import List, Dict, Any, Generator
from openai import OpenAI
from dotenv import load_dotenv
from skills_google import AVAILABLE_TOOLS, execute_tool_call

load_dotenv()

# Initialize Client
# Note: In a real scenario, ensure OPENAI_API_KEY is set in .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are Mahakaal, an advanced Executive Assistant AI. 
Your demeanor is professional, efficient, and slightly mysterious (like a "Time Lord").
You have access to tools to manage the user's calendar.

Capabilities:
1. You ALWAYS check the current date/time first if the user request involves relative time (tomorrow, next week, specific day of the week).
2. You confirm actions clearly.
3. If a user asks about "next Sunday" or "this weekend", use 'list_events_range' or 'search_events' to see the relevant days at once instead of calling 'list_events' repeatedly.
4. You can INVITE people to events by using the 'attendees' parameter (a list of emails) in 'schedule_event' or 'update_event'. 
5. You can set granular DURATIONS for events using 'duration_minutes' (e.g., 15, 30, 45). Default is 60.
6. If a tool fails, explain why and ask for clarification.

Style:
- Be concise.
- Use "Time is of the essence" or similar subtle time-related metaphors occasionally.
"""

def run_agent_stream(message_history: List[Dict[str, str]]) -> Generator[str, None, None]:
    """
    Runs the agent loop. Yields chunks of data to the frontend.
    Data format yielded: JSON string labeled with type.
    e.g., {"type": "thought", "content": "..."} or {"type": "answer", "content": "..."}
    """
    
    # Prepend System Prompt
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + message_history

    while True:
        # 1. Ask LLM
        # We don't stream the LLM response *internally* here for simplicity of logic in v1,
        # but we stream the *process* to the frontend.
        
        # Yield status
        yield json.dumps({"type": "status", "content": "Thinking..."}) + "\n"
        
        try:
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=messages,
                tools=AVAILABLE_TOOLS,
                tool_choice="auto"
            )
        except Exception as e:
            yield json.dumps({"type": "error", "content": str(e)}) + "\n"
            return

        response_message = response.choices[0].message
        
        # 2. Check if tool call
        tool_calls = response_message.tool_calls
        
        if tool_calls:
            # Yield thought/action to UI
            # IMPORTANT: We must send this to the frontend explicitly so it can be added to history
            assistant_msg = response_message.model_dump()
            # Clean up for JSON serialization
            if assistant_msg.get('function_call') is None:
                del assistant_msg['function_call']
            
            yield json.dumps({
                "type": "history_append",
                "content": "Assistant tool call",
                "data": assistant_msg
            }) + "\n"

            messages.append(response_message) # Add assistant's "intent" to history
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                yield json.dumps({
                    "type": "log", 
                    "content": f"Using Skill: {function_name}", 
                    "data": function_args
                }) + "\n"
                
                # Execute Tool
                function_response = execute_tool_call(function_name, function_args)
                
                yield json.dumps({
                    "type": "log",
                    "content": f"Skill Result: {function_response}"
                }) + "\n"

                tool_msg = {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }

                # Send tool result to frontend history
                yield json.dumps({
                    "type": "history_append",
                    "content": "Tool result",
                    "data": tool_msg
                }) + "\n"

                # Add tool result to history for the LLM
                messages.append(tool_msg)
            
            # Loop back to send tool outputs to LLM
            continue
        
        else:
            # 3. Final Answer
            final_content = response_message.content
            yield json.dumps({"type": "answer", "content": final_content}) + "\n"
            break
