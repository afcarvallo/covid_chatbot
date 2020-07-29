# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from typing import List


class UserProfile:
    def __init__(
        self, name: str = None, country: str = None, covid_options: List[str] = None
    ):
        self.name: str = name
        self.country: str= country
        self.covid_options: List[str] = covid_options
