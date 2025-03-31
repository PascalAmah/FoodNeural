"""Food alternatives data with environmental impact metrics"""

FOOD_ALTERNATIVES = {
    "dairy": [
        {
            "name": "Oat Milk",
            "explanation": "Oat milk reduces water usage by 60% compared to dairy milk.",
            "impact": {
                "breakdown": {
                    "carbon": 0.5,
                    "water": 150,
                    "energy": 0.4,
                    "waste": 0.05,
                    "deforestation": 0.1
                }
            },
            "nutrition": {
                "protein": 3.0,
                "fat": 2.0,
                "carbs": 16.0,
                "fiber": 2.0
            },
            "sustainability_improvement": 80.0,
            "similarity_score": 85.0
        },
        {
            "name": "Soy Milk",
            "explanation": "Soy milk has high protein content and 70% lower carbon footprint than dairy milk.",
            "impact": {
                "breakdown": {
                    "carbon": 0.4,
                    "water": 130,
                    "energy": 0.3,
                    "waste": 0.04,
                    "deforestation": 3.0
                }
            },
            "nutrition": {
                "protein": 7.0,
                "fat": 4.0,
                "carbs": 4.0,
                "fiber": 0.4
            },
            "sustainability_improvement": 70.0,
            "similarity_score": 90.0
        },
        {
            "name": "Almond Milk",
            "explanation": "Almond milk produces 80% less greenhouse gases than dairy milk.",
            "impact": {
                "breakdown": {
                    "carbon": 0.3,
                    "water": 300,
                    "energy": 0.3,
                    "waste": 0.03,
                    "deforestation": 0.2
                }
            },
            "nutrition": {
                "protein": 1.0,
                "fat": 3.0,
                "carbs": 1.0,
                "fiber": 0.5
            },
            "sustainability_improvement": 65.0,
            "similarity_score": 85.0
        }
    ],

    "meat": [
        {
            "name": "Tofu",
            "explanation": "Tofu has a 96% lower carbon footprint than beef.",
            "impact": {
                "breakdown": {
                    "carbon": 2.0,
                    "water": 300,
                    "energy": 2.0,
                    "waste": 0.2,
                    "deforestation": 1.0
                }
            },
            "nutrition": {
                "protein": 8.0,
                "fat": 4.0,
                "carbs": 2.0,
                "fiber": 0.3
            },
            "sustainability_improvement": 90.0,
            "similarity_score": 75.0
        },
        {
            "name": "Lentils",
            "explanation": "Lentils use 99% less water than beef and have minimal environmental impact.",
            "impact": {
                "breakdown": {
                    "carbon": 0.9,
                    "water": 180,
                    "energy": 1.5,
                    "waste": 0.1,
                    "deforestation": 0.1
                }
            },
            "nutrition": {
                "protein": 9.0,
                "fat": 0.4,
                "carbs": 20.0,
                "fiber": 8.0
            },
            "sustainability_improvement": 95.0,
            "similarity_score": 65.0
        },
        {
            "name": "Beyond Meat",
            "explanation": "Plant-based meat alternatives generate 90% less greenhouse gas emissions than beef.",
            "impact": {
                "breakdown": {
                    "carbon": 3.5,
                    "water": 350,
                    "energy": 2.5,
                    "waste": 0.3,
                    "deforestation": 0.5
                }
            },
            "nutrition": {
                "protein": 20.0,
                "fat": 14.0,
                "carbs": 7.0,
                "fiber": 2.0
            },
            "sustainability_improvement": 85.0,
            "similarity_score": 90.0
        }
    ],

    "vegetables": [
        {
            "name": "Local Seasonal Vegetables",
            "explanation": "Local seasonal vegetables reduce transportation emissions by up to 90%.",
            "impact": {
                "breakdown": {
                    "carbon": 0.2,
                    "water": 20,
                    "energy": 0.1,
                    "waste": 0.02,
                    "deforestation": 0.0
                }
            },
            "nutrition": {
                "protein": 2.0,
                "fat": 0.3,
                "carbs": 5.0,
                "fiber": 2.5
            },
            "sustainability_improvement": 75.0,
            "similarity_score": 85.0
        }
    ],

    "grains": [
        {
            "name": "Quinoa",
            "explanation": "Quinoa is drought-resistant and has a 30% lower carbon footprint than other grains.",
            "impact": {
                "breakdown": {
                    "carbon": 0.4,
                    "water": 90,
                    "energy": 0.3,
                    "waste": 0.02,
                    "deforestation": 0.1
                }
            },
            "nutrition": {
                "protein": 4.4,
                "fat": 1.9,
                "carbs": 21.3,
                "fiber": 2.8
            },
            "sustainability_improvement": 55.0,
            "similarity_score": 75.0
        }
    ],

    "default": [
        {
            "name": "Local Produce",
            "explanation": "Local produce reduces transportation emissions by up to 90%.",
            "impact": {
                "breakdown": {
                    "carbon": 0.3,
                    "water": 40,
                    "energy": 0.2,
                    "waste": 0.1,
                    "deforestation": 0.1
                }
            },
            "nutrition": {
                "protein": 2.0,
                "fat": 0.5,
                "carbs": 5.0,
                "fiber": 2.0
            },
            "sustainability_improvement": 70.0,
            "similarity_score": 60.0
        }
    ]
}