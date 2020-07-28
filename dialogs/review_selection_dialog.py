# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import requests
import json

# ENDPOINT COVID 
# https://rapidapi.com/api-sports/api/covid-193/endpoints

url = "https://covid-193.p.rapidapi.com/statistics"


headers = {
    'x-rapidapi-host': "api host",
    'x-rapidapi-key': "api key"
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


class ReviewSelectionDialog(ComponentDialog):
    def __init__(self, dialog_id: str = None, new_country = True):

        super(ReviewSelectionDialog, self).__init__(dialog_id or ReviewSelectionDialog.__name__)

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
            choices=[Choice("Covid-19 Cases"), Choice("Covid-19 Deaths"), Choice("Country Demographics"), Choice("Done")],
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

        # If they're done, exit and return their list.
        if step_context.result.value == 'Done':
            return await step_context.end_dialog()

        # Otherwise, repeat this dialog, passing in the selections from this iteration.
        return await step_context.replace_dialog(ReviewSelectionDialog.__name__)
