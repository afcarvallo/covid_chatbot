# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.core import MessageFactory, CardFactory
from botbuilder.dialogs import (
    WaterfallDialog,
    DialogTurnResult,
    WaterfallStepContext,
    ComponentDialog,
)
from botbuilder.dialogs.prompts import PromptOptions, TextPrompt, NumberPrompt

from data_models import UserProfile
from dialogs.review_selection_dialog import ReviewSelectionDialog

from botbuilder.schema import (AnimationCard, MediaUrl)


class TopLevelDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):
        super(TopLevelDialog, self).__init__(dialog_id or TopLevelDialog.__name__)

        # Key name to store this dialogs state info in the StepContext
        self.USER_INFO = "value-userInfo"

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(NumberPrompt(NumberPrompt.__name__))

        self.add_dialog(ReviewSelectionDialog(ReviewSelectionDialog.__name__))

        self.add_dialog(
            WaterfallDialog(
                "WFDialog",
                [
                    self.name_step,
                    self.start_selection_step,
                    self.acknowledgement_step,
                ],
            )
        )

        self.initial_dialog_id = "WFDialog"

    async def name_step(self, step_context: WaterfallStepContext):
        # Create an object in which to collect the user's information within the dialog.
        step_context.values[self.USER_INFO] = UserProfile()

        # Ask the user to enter their name.
        prompt_options = PromptOptions(
            prompt=MessageFactory.text("Hello, what's your name?")
        )

        return await step_context.prompt(TextPrompt.__name__, prompt_options)
    

    async def start_selection_step(self, step_context: WaterfallStepContext):

        # Set the user's name to what they entered in response to the name prompt.
        user_profile = step_context.values[self.USER_INFO]
        user_profile.name = step_context.result

        # We can send messages to the user at any point in the WaterfallStep.
        await step_context.context.send_activity(
            MessageFactory.text(f"Nice to e-meet you {step_context.result.capitalize()}")
        )

        # show covid card
        reply = MessageFactory.list([])
        reply.attachments.append(self.create_animation_card())
        await step_context.context.send_activity(reply)

        # start the review selection dialog.
        return await step_context.begin_dialog(ReviewSelectionDialog.__name__)

    async def acknowledgement_step(self, step_context: WaterfallStepContext):
        
        # Set the user's company selection to what they entered in the review-selection dialog.
        user_profile: UserProfile = step_context.values[self.USER_INFO]
        user_profile.companies_to_review = step_context.result

        # Thank them for participating.
        await step_context.context.send_activity(
            MessageFactory.text(f"Bye {user_profile.name.capitalize()}, have a nice day.")
        )

        # Exit the dialog, returning the collected user information.
        return await step_context.end_dialog(user_profile)
    
    # CREATE CARD FUNCTION 
    def create_animation_card(self):
        card = AnimationCard(
            media=[MediaUrl(url="https://media4.s-nbcnews.com/j/newscms/2020_26/3392002/antimicrobial-face-masks-kr-2x1-tease-200623_2597ed8310508184ab2a3fdba151fded.fit-1240w.gif")],
            title="Learn how to use your mask :)",
            subtitle="For your protection against COVID-19",
        )
        return CardFactory.animation_card(card)

