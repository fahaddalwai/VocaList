from datetime import datetime
import cohere
from app.models import Task

# Initialize the Cohere client
co = cohere.Client('AnPnuFiUEcnWT4POFYHq3S2UOKDbGZv03E82yVhZ')

def process_speech_to_task(speech_text, user_id):
    """
    Processes the speech text to extract task details using an LLM and includes
    the user's existing tasks for context.
    """
    # Log the speech text
    print(f"Speech-to-text output: {speech_text}")
    today_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Fetch the user's existing tasks
    tasks = Task.query.filter_by(user_id=user_id).order_by(Task.created_at.asc()).all()
    
    task_list = "\n".join([
    f"- Title: {task.title}\n"
    f"  Description: {task.description if task.description else 'No description'}\n"
    f"  Created At: {task.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
    f"  Completed: {'Yes' if task.completed else 'No'}\n"
    f"  Reminder Time: {task.reminder_time.strftime('%Y-%m-%d %H:%M:%S') if task.reminder_time else 'No reminder'}"
    for task in tasks
    ])

    for task in tasks:
        print(task.reminder_time)

    # Prepare the prompt with user's tasks included
    prompt = f"""
The date today is {today_date}. Below is the list of tasks you have:
{task_list}

Based on the given speech input, extract the following details and return them in the exact format specified below:

- Action Type (Add, Update, Delete ONLY)
- Title (Must be a title from the task list provided if Action Type is Update or Delete)
- Description
- Reminder Time (in the format: YYYY-MM-DD HH:MM:SS)

**IMPORTANT:**
- The output must be in the exact format provided below, with no additional text or variations.
- If the Action Type is 'Update' or 'Delete', you must select the task title from the task list that best matches the user's reference. Do not create new titles or use broad phrases.
- Do not include any tasks not present in the task list.

**Examples:**

Example 1:
Speech Input: 'Please delete the task about buying groceries.'
Return the extracted details in this format:
Action Type: Delete
Title: Buy Groceries
Description:
Reminder Time:

Example 2:
Speech Input: 'I need to update my meeting from yesterday to next week.'
Return the extracted details in this format:
Action Type: Update
Title: Team Meeting
Description: 
Reminder Time: 2024-10-15 10:00:00

Example 3:
Speech Input: 'Add a task to call mom tomorrow evening.'
Return the extracted details in this format:
Action Type: Add
Title: Call Mom
Description:
Reminder Time: 2024-11-12 18:00:00

Now, process the following speech input:

Speech Input: '{speech_text}'
Return the extracted details in this format:
Action Type: Add/Update/Delete
Title: Task Title
Description: Task Description
Reminder Time: YYYY-MM-DD HH:MM:SS
"""
    
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=200,
        temperature=0.5
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
        "reminder_time": reminder_time
    }
