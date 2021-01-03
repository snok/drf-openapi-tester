GOOD_TEST_DATA = [
    {
        "url": "/cars/correct",
        "expected_response": [
            {"name": "Saab", "color": "Yellow", "height": "Medium height", "width": "Very wide", "length": "2 meters"},
            {"name": "Volvo", "color": "Red", "height": "Medium height", "width": "Not wide", "length": "2 meters"},
            {"name": "Tesla", "color": "black", "height": "Medium height", "width": "Wide", "length": "2 meters"},
        ],
    },
    {
        "url": "/trucks/correct",
        "expected_response": [
            {"name": "Saab", "color": "Yellow", "height": "Medium height", "width": "Very wide", "length": "2 meters"},
            {"name": "Volvo", "color": "Red", "height": "Medium height", "width": "Not wide", "length": "2 meters"},
            {"name": "Tesla", "color": "black", "height": "Medium height", "width": "Wide", "length": "2 meters"},
        ],
    },
]

I18N_DATA = [
    {
        "url": "/i18n",
        "lang": "en",
        "expected_response": {
            "languages": ["French", "Spanish", "Greek", "Italian", "Portuguese"],
        },
    },
    {
        "url": "/i18n",
        "lang": "de",
        "expected_response": {
            "languages": ["Französisch", "Spanisch", "Griechisch", "Italienisch", "Portugiesisch"],
        },
    },
]

BAD_TEST_DATA = [
    {
        "url": "/cars/incorrect",
        "expected_response": [
            {"name": "Saab", "color": "Yellow", "height": "Medium height"},
            {"name": "Volvo", "color": "Red", "width": "Not very wide", "length": "2 meters"},
            {"name": "Tesla", "height": "Medium height", "width": "Medium width", "length": "2 meters"},
        ],
    },
    {
        "url": "/trucks/incorrect",
        "expected_response": [
            {"name": "Saab", "color": "Yellow", "height": "Medium height"},
            {"name": "Volvo", "color": "Red", "width": "Not very wide", "length": "2 meters"},
            {"name": "Tesla", "height": "Medium height", "width": "Medium width", "length": "2 meters"},
        ],
    },
]
