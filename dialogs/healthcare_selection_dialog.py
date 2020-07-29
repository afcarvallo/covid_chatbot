# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import requests
import json
from collections import Counter 
import random
import os
import base64

from botbuilder.core import CardFactory, MessageFactory

from botbuilder.schema import (
    HeroCard,
    ThumbnailCard,
    MediaUrl,
    Attachment,
    CardImage,
    CardAction,
    Activity,
    ActionTypes,
    ActivityTypes, 
    AnimationCard
)


from typing import List

from botbuilder.dialogs import (
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
    ComponentDialog,
)
from botbuilder.dialogs.prompts import ChoicePrompt, PromptOptions, TextPrompt
from botbuilder.dialogs.choices import Choice, FoundChoice
from botbuilder.core import MessageFactory


class HealthSelectionDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None, new_country = True):

        super(HealthSelectionDialog, self).__init__(dialog_id or HealthSelectionDialog.__name__)

        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__, [
                    self.selection_step,
                    self.loop_step]
            )
        )
    
        self.initial_dialog_id = WaterfallDialog.__name__
    

    async def selection_step(self, step_context: WaterfallStepContext):

        return await step_context.prompt(
        ChoicePrompt.__name__,
        PromptOptions(
            prompt=MessageFactory.text("Please indicate what do you want to know, or choose done to exit."),
            choices=[Choice('Covid-19 Social Distance'),
                     Choice('Covid-19 Mask Instructions'),
                     Choice("Done")],
        ),
    )
       
    async def loop_step(self, step_context: WaterfallStepContext):

        # If they chose an option execute script
        if step_context.result.value == 'Covid-19 Social Distance':
            # show covid card
            reply = MessageFactory.list([])
            reply.attachments.append(self.create_distance_animation_card())
            await step_context.context.send_activity(reply)
            

        if step_context.result.value == 'Covid-19 Mask Instructions':
            # show covid card
            reply = MessageFactory.list([])
            reply.attachments.append(self.create_mask_animation_card())
            await step_context.context.send_activity(reply)
        
        if step_context.result.value == 'Done':
            return await step_context.end_dialog()
            


        # Otherwise, repeat this dialog, passing in the selections from this iteration.
        return await step_context.replace_dialog(HealthSelectionDialog.__name__)
        
    
    # CREATE CARD FUNCTION 
    def create_mask_animation_card(self):
        card = AnimationCard(
            media=[MediaUrl(url="https://media4.s-nbcnews.com/j/newscms/2020_26/3392002/antimicrobial-face-masks-kr-2x1-tease-200623_2597ed8310508184ab2a3fdba151fded.fit-1240w.gif")],
            title="Learn how to use your mask :)",
            subtitle="For your protection against COVID-19",
        )
        return CardFactory.animation_card(card)

    # CREATE CARD FUNCTION 
    def create_distance_animation_card(self):
        card = AnimationCard(
            media=[MediaUrl(url="https://www.verywellmind.com/thmb/W4VojprlVzyEMentRI2IMaEHDQU=/900x900/smart/filters:no_upscale()/social-distancing-color021-4c03a3a03b1a4eb9bde32a49596d4d9b.gif")],
            title="Learn about social distance :)",
            subtitle="For your protection against COVID-19",
        )
        return CardFactory.animation_card(card)
    