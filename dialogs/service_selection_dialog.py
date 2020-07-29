from typing import List

from botbuilder.dialogs import (
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
    ComponentDialog,
)

from botbuilder.schema import (
    HeroCard,
    ThumbnailCard,
    MediaUrl,
    Attachment,
    CardImage,
    CardAction,
    Activity,
    ActionTypes,
    ActivityTypes
)

from botbuilder.dialogs.prompts import ChoicePrompt, PromptOptions, TextPrompt
from botbuilder.dialogs.choices import Choice, FoundChoice
from botbuilder.core import MessageFactory, CardFactory

from dialogs.stats_selection_dialog import StatsSelectionDialog
from dialogs.social_media_selection_dialog import SocialMediaSelectionDialog
from dialogs.healthcare_selection_dialog import HealthSelectionDialog


class ServiceSelectionDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None):

        super(ServiceSelectionDialog, self).__init__(dialog_id or ServiceSelectionDialog.__name__)

        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__, [
                    self.selection_step,
                    self.loop_step
                    ]
            )
        )
    
        self.initial_dialog_id = WaterfallDialog.__name__
    
    async def selection_step(self, step_context: WaterfallStepContext):

        return await step_context.prompt(
        ChoicePrompt.__name__,
        PromptOptions(
            prompt=MessageFactory.text("Please indicate what do you want to know, or choose done to exit."),
            choices=[Choice("Covid-19 Stats"), 
                     Choice("Covid-19 Social"), 
                     Choice("Covid-19 Health"), 
                     Choice("Covid-19 Donation"),
                     Choice('Covid-19 Places') ,
                     Choice("Done")],
        ),
    )

    async def loop_step(self, step_context: WaterfallStepContext):
        # If they chose an option execute script
        if step_context.result.value == 'Covid-19 Stats':
            await step_context.context.send_activity(
                MessageFactory.text(f"Welcome to the Covid-19 Stats Portal")
            )
            self.add_dialog(StatsSelectionDialog(StatsSelectionDialog.__name__))
            return await step_context.begin_dialog(StatsSelectionDialog.__name__)

        if step_context.result.value == 'Covid-19 Social':
            await step_context.context.send_activity(
                MessageFactory.text(f"Welcome to the Covid-19 Social Media Portal")
            )
            self.add_dialog(SocialMediaSelectionDialog(SocialMediaSelectionDialog.__name__))
            return await step_context.begin_dialog(SocialMediaSelectionDialog.__name__)

        if step_context.result.value == 'Covid-19 Health':
            await step_context.context.send_activity(
                MessageFactory.text(f"Welcome to the Covid-19 Health Portal")
            )
            self.add_dialog(HealthSelectionDialog(HealthSelectionDialog.__name__))
            
            return await step_context.begin_dialog(HealthSelectionDialog.__name__)


        if step_context.result.value == 'Covid-19 Donation':
            await step_context.context.send_activity(
                MessageFactory.text(f"Welcome to the Covid-19 Donation Portal")
            )
            # show covid meme
            reply = MessageFactory.list([])
            reply.attachments.append(self.create_thumbnail_card())
            await step_context.context.send_activity(reply)
        
        if step_context.result.value == 'Covid-19 Places':
            await step_context.context.send_activity(
                MessageFactory.text(f"Welcome to the Covid-19 Places Portal")
            )

        # If they're done, exit and return their list.
        elif step_context.result.value == 'Done':
            return await step_context.end_dialog()

        # Otherwise, repeat this dialog, passing in the selections from this iteration.
        return await step_context.replace_dialog(ServiceSelectionDialog.__name__)


        return await step_context.begin_dialog(ServiceSelectionDialog.__name__)

    def create_thumbnail_card(self):
        card = ThumbnailCard(
            title="Seattle Foundation",
            subtitle="COVID-19 Response Fund",
            text="The COVID-19 Response Fund deploys resources to organizations supporting local "
            " workers and families most impacted by the coronavirus crisis.",
            images=[
                CardImage(
                    url="https://www.seattlefoundation.org/-/media/SeaFdn/Images/Common/sf_logo.gif"
                )
            ],
            buttons=[
                CardAction(
                    type=ActionTypes.open_url,
                    title="Make a donation",
                    value="https://www.seattlefoundation.org/communityimpact/civic-leadership/covid-19-response-fund",
                )
            ],
        )
        return CardFactory.thumbnail_card(card)


          
