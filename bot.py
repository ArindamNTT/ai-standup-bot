import json
from datetime import date
from botbuilder.core import ActivityHandler, TurnContext, ConversationState

class StandupBot(ActivityHandler):
    def __init__(self, conversation_state: ConversationState):
        self.conversation_state = conversation_state
        self.standup_questions = [
            "What did you accomplish since the last standup?",
            "What are you working on today?",
            "Are there any blockers?"
        ]
        self.responses = {}
        self.conversation_references = {}

    async def on_message_activity(self, turn_context: TurnContext):
        self._add_conversation_reference(turn_context.activity)
        user_id = turn_context.activity.from_property.id
        username = turn_context.activity.from_property.name

        if user_id not in self.responses:
            self.responses[user_id] = {"step": 0, "answers": []}

        step = self.responses[user_id]["step"]

        if step == 0:
            await turn_context.send_activity(self.standup_questions[0])
            self.responses[user_id]["step"] += 1
        elif step == 1:
            self.responses[user_id]["answers"].append(turn_context.activity.text)
            await turn_context.send_activity(self.standup_questions[1])
            self.responses[user_id]["step"] += 1
        elif step == 2:
            self.responses[user_id]["answers"].append(turn_context.activity.text)
            await turn_context.send_activity(self.standup_questions[2])
            self.responses[user_id]["step"] += 1
        elif step == 3:
            self.responses[user_id]["answers"].append(turn_context.activity.text)
            summary = "\n".join(
                f"{q} {a}" for q, a in zip(self.standup_questions, self.responses[user_id]["answers"])
            )
            await turn_context.send_activity(f"Thank you for your update! Here’s a summary:\n{summary}")

            # Save to JSON
            today = str(date.today())
            standup_entry = {
                "date": today,
                "user_id": user_id,
                "username": username,
                "answers": self.responses[user_id]["answers"]
            }
            with open("standup_replies.json", "a") as f:
                f.write(json.dumps(standup_entry) + "\n")

            # Reset for next standup
            self.responses[user_id] = {"step": 0, "answers": []}
        else:
            await turn_context.send_activity("Let's start your standup update.")
            self.responses[user_id] = {"step": 0, "answers": []}

    def _add_conversation_reference(self, activity):
        conversation_reference = TurnContext.get_conversation_reference(activity)
        self.conversation_references[activity.from_property.id] = conversation_reference