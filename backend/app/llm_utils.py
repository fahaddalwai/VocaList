import cohere
from datetime import datetime
# Initialize the Cohere client
co = cohere.Client('AnPnuFiUEcnWT4POFYHq3S2UOKDbGZv03E82yVhZ')

# Function to process speech into task
def process_speech_to_task(speech_text):
    # Log the speech text
    print(f"Speech-to-text output: {speech_text}")
    today_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    prompt = f"""The date today is {today_date}. If you do not have all the details provided to you then return that part as blank. Extract the action type (add, update, delete), title, description, and reminder time (in the format: 2024-10-01 17:49:35) from this speech: '{speech_text}' in this format:
        Action Type: Add
        Title: Buy Groceries
        Description: Buy milk, eggs, and bread.
        Reminder Time: 2024-10-02 14:00:00
    """
    
    response = co.generate(
        model='command-xlarge-nightly',  # Use your desired Cohere model
        prompt=prompt,
        max_tokens=150, 
        temperature=0.7
    )

    task_text = response.generations[0].text.strip()

    # Log the LLM output
    print(f"LLM Output: {task_text}")

    # Parse the response text to extract action type, title, description, and reminder time
    lines = task_text.split('\n')
    
    action_type = None
    title = None
    description = None
    reminder_time = None

    for line in lines:
        if line.startswith("Action Type:"):
            action_type = line.split(":", 1)[1].strip()
        elif line.startswith("Title:"):
            title = line.split(":", 1)[1].strip()
        elif line.startswith("Description:"):
            description = line.split(":", 1)[1].strip()
        elif line.startswith("Reminder Time:"):
            reminder_time = line.split(":", 1)[1].strip()
    
    return {
        "action_type": action_type,
        "title": title,
        "description": description,
        "reminder_time": reminder_time  # Return reminder time as string, convert later
    }
