# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import requests
import json
import tweepy
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
    ActivityTypes
)

## tweepy authentication
access_token = ""
access_token_secret = ""
consumer_key = ""
consumer_secret = ""

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

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


class SocialMediaSelectionDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None, new_country = True):

        super(SocialMediaSelectionDialog, self).__init__(dialog_id or SocialMediaSelectionDialog.__name__)

        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))

        self.new_country = new_country

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__, [
                    self.country_step,
                    self.selection_step,
                    self.loop_step]
            )
        )
    
        self.initial_dialog_id = WaterfallDialog.__name__
    
    async def country_step(self, step_context: WaterfallStepContext):
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("What's your country?")),
        )

    async def selection_step(self, step_context: WaterfallStepContext):

        self.new_country = False

        step_context.values["country"] = step_context.result

        return await step_context.prompt(
        ChoicePrompt.__name__,
        PromptOptions(
            prompt=MessageFactory.text("Please indicate what do you want to know, or choose done to exit."),
            choices=[Choice('Covid-19 Twitter'),
                     Choice('Covid-19 Meme'),
                     Choice("Done")],
        ),
    )
       
    async def loop_step(self, step_context: WaterfallStepContext):

        country = step_context.values["country"].capitalize()
        
        # If they chose an option execute script
        if step_context.result.value == 'Covid-19 Twitter':
            
            await step_context.context.send_activity(MessageFactory.text("Obtaining last tweets in your country related to COVID-19 wait a moment..."))

            result = []

            query = f'{country} AND covid OR covid-19 OR coronavirus OR Covid-19'

            for tweet in tweepy.Cursor(api.search, q=query).items(5):
                reply = MessageFactory.list([])
                reply.attachments.append(self.create_tweet_card(tweet))
                await step_context.context.send_activity(reply)

        if step_context.result.value == 'Covid-19 Meme':
            # show covid meme
            reply = MessageFactory.list([])
            reply.attachments.append(self.create_hero_card())
            await step_context.context.send_activity(reply)

        # If they're done, exit and return their list.
        elif step_context.result.value == 'Done':
            return await step_context.end_dialog()

        # Otherwise, repeat this dialog, passing in the selections from this iteration.
        return await step_context.replace_dialog(SocialMediaSelectionDialog.__name__)
        
    # CREATE TWEET CARD FUNCTION 
    def create_tweet_card(self, tweet):
        card = ThumbnailCard(
            title=tweet.user.name,
            subtitle="@"+tweet.user.screen_name,
            text=tweet.text,
            images=[
                CardImage(
                    url=tweet.user.profile_image_url
                )
            ]
        )
        
        return CardFactory.thumbnail_card(card)

    # CREATE CARD FUNCTION 
    def create_hero_card(self):
        
        memes_list = ['https://images3.memedroid.com/images/UPLOADED826/5e6ea59356326.jpeg',
                    'https://i.pinimg.com/originals/8c/04/87/8c04877aad35b1b0dad8376f7899d878.png',
                    'https://starecat.com/content/wp-content/uploads/im-no-expert-on-covid-19-but-this-is-the-cure-literally-band.jpg',
                    'https://images3.memedroid.com/images/UPLOADED86/5e2cc3aeec5c0.jpeg',
                    
        ]

        card = HeroCard(
            title="",
            images=[
                CardImage(
                    url=random.choice(memes_list)
                )
            ]
        )
        
        return CardFactory.hero_card(card)
    
    def _get_inline_attachment(self, country):
        
        plot_country = ''

        if country == 'Chile':
            plot_country = 'chile'
        
        elif country == 'Pakistan':
            plot_country = 'pakistan'
        
        else:
            plot_country = 'usa'

        file_path = os.path.join(os.getcwd(), f"images/{plot_country}_plot.png")
        
        with open(file_path, "rb") as in_file:
            base64_image = base64.b64encode(in_file.read()).decode()

        return Attachment(
            name="chile_plot.png",
            content_type="image/png",
            content_url=f"data:image/png;base64,{base64_image}",
        )