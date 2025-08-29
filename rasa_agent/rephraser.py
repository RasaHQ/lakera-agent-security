from rasa.core.nlg.contextual_response_rephraser import ContextualResponseRephraser
from rasa.shared.core.trackers import DialogueStateTracker
from rasa.shared.core.events import UserUttered
from typing import Dict, Any, Optional, Text

class CustomContextualResponseRephraser(ContextualResponseRephraser):
    def __init__(self, endpoint_config, domain, max_user_message_length=90):
        """Initialize the custom rephraser with message length limit.

        Args:
            endpoint_config: The endpoint configuration for the LLM.
            domain: The domain of the assistant.
            max_user_message_length: Maximum length for user messages in transcript.
        """
        super().__init__(endpoint_config, domain)
        self.max_user_message_length = max_user_message_length

    def truncate_long_user_inputs(self, tracker: DialogueStateTracker) -> DialogueStateTracker:
        """Create a new tracker with truncated user messages.

        Args:
            tracker: The original tracker.

        Returns:
            A new tracker with long user messages truncated.
        """
        # Create a copy of the tracker to avoid modifying the original
        truncated_tracker = tracker.copy()

        # Process events and truncate long user messages
        for event in truncated_tracker.events:
            if isinstance(event, UserUttered) and event.text:
                if len(event.text) > self.max_user_message_length:
                    truncated_text = event.text[:self.max_user_message_length] + "[truncated]"
                    event.text = truncated_text

        return truncated_tracker

    async def generate(
        self,
        utter_action: Text,
        tracker: DialogueStateTracker,
        output_channel: Text,
        **kwargs: Any,
    ) -> Optional[Dict[Text, Any]]:
        """Generate a response with truncated user messages in the transcript.

        Args:
            utter_action: The name of the utter action to generate a response for.
            tracker: The tracker to use for the generation.
            output_channel: The output channel to use for the generation.
            **kwargs: Additional arguments to pass to the generation.

        Returns:
            The generated response.
        """
        truncated_tracker = self.truncate_long_user_inputs(tracker)
        return await super().generate(utter_action, truncated_tracker, output_channel, **kwargs)
