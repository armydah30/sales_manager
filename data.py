def Rules():
    rules = [
        {
            'id': 1,
            'crop': 'maize',
            'advice': 'Based on the current temperature harvest the corn, and sweep the floor',
            'weather': 'temperature',
            'weather_condition': 'less than',
            'value': 15
        },
        {
            'id': 2,
            'crop': 'maize',
            'advice': 'Based on the current temperature harvest the maize and plant the soil',
            'weather': 'temperature',
            'weather_condition': 'less than',
            'value': 20
        },
        {
            'id': 3,
            'crop': 'sorghum',
            'advice': 'Based on the current temperature harvest the cowpea and plant the soil',
            'weather': 'temperature',
            'weather_condition': 'less than',
            'value': 20
        },
        {
            'id': 4,
            'crop': 'sorghum',
            'advice': 'Based on the current wind harvest the cowpea and plant the soil',
            'weather': 'wind',
            'weather_condition': 'greater than',
            'value': 20
        },
        {
            'id': 5,
            'crop': 'sorghum',
            'advice': 'Based on the current wind harvest the potato and plant the soil',
            'weather': 'wind',
            'weather_condition': 'less than',
            'value': 2
        }

    ]
    return rules
