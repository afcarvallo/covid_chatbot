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
    MediaUrl,
    Attachment,
    CardImage,
    CardAction,
    Activity,
    ActionTypes,
    ActivityTypes
)

# ENDPOINT COVID 
url = "https://covid-193.p.rapidapi.com/statistics"

headers = {
    'x-rapidapi-host': "covid-193.p.rapidapi.com",
    'x-rapidapi-key': ""
    }

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


class StatsSelectionDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None, new_country = True):

        super(StatsSelectionDialog, self).__init__(dialog_id or StatsSelectionDialog.__name__)

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
            choices=[Choice("Covid-19 Cases"), 
                     Choice("Covid-19 Deaths"), 
                     Choice("Covid-19 Tests"),
                     Choice("Done")],
        ),
    )
       
    async def loop_step(self, step_context: WaterfallStepContext):

        country = step_context.values["country"].capitalize()
        
        # If they chose an option execute script
        if step_context.result.value == 'Covid-19 Cases':

            await step_context.context.send_activity(MessageFactory.text("Wait a moment..."))

            querystring = {"country":"{}".format(country)}
            response = requests.request("GET", url, headers=headers, params=querystring)
            response_json = json.loads(response.text)

            new_cases = response_json['response'][0]['cases']['new']
            active_cases = response_json['response'][0]['cases']['active']
            recovered_cases = response_json['response'][0]['cases']['recovered']

            await step_context.context.send_activity(
                MessageFactory.text(
                    f"COVID-19 Cases from {country} \n\n"
                    f"New Cases {new_cases} \n\n"
                    f"Active Cases {active_cases} \n\n"
                    f"Recovered Cases {recovered_cases} \n\n"
                    )
                )   
            
            reply = Activity(type=ActivityTypes.message)
            reply.attachments = [self._get_inline_attachment(country)]
            await step_context.context.send_activity(reply)

        
        if step_context.result.value == 'Covid-19 Deaths':
            await step_context.context.send_activity(MessageFactory.text("Wait a moment..."))

            querystring = {"country":"{}".format(country)}
            response = requests.request("GET", url, headers=headers, params=querystring)
            response_json = json.loads(response.text)

            new_deaths = response_json['response'][0]['deaths']['new']
            m_deaths = response_json['response'][0]['deaths']['1M_pop']
            total_deaths = response_json['response'][0]['deaths']['total']

            await step_context.context.send_activity(
                MessageFactory.text(
                    f"COVID-19 Deaths from {country} \n\n"
                    f"New Deaths {new_deaths} \n\n"
                    f"1M_pop Deaths {m_deaths} \n\n"
                    f"Total Deaths {total_deaths} \n\n"
                    )
                )   
        
        if step_context.result.value == 'Covid-19 Tests':
            await step_context.context.send_activity(MessageFactory.text("Wait a moment..."))

            querystring = {"country":"{}".format(country)}
            response = requests.request("GET", url, headers=headers, params=querystring)
            response_json = json.loads(response.text)

            m_tests = response_json['response'][0]['tests']['1M_pop']
            total_tests = response_json['response'][0]['tests']['total']

            await step_context.context.send_activity(
                MessageFactory.text(
                    f"COVID-19 PCR Tests from {country} \n\n"
                    f"New Tests {m_tests} \n\n"
                    f"Total PCR Tests {total_tests} \n\n"
                    )
                )  

        # If they're done, exit and return their list.
        elif step_context.result.value == 'Done':
            return await step_context.end_dialog()

        # Otherwise, repeat this dialog, passing in the selections from this iteration.
        return await step_context.replace_dialog(StatsSelectionDialog.__name__)
        
    # CREATE CARD FUNCTION 
    def HeroCard(self):
        
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