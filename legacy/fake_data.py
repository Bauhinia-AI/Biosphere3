from fastapi import FastAPI, HTTPException
from model import FreelanceJob, PublicJob, GameSubject
from typing import Optional, List

# 多样化的工作数据
freelance_jobs_data = [
    FreelanceJob(
        jobname="Apple Picker",
        jobid=1,
        workhours="10:00-16:00",
        wageperhour=15.5,
        wagemerchant="Apples",
        wagemerchantperhour=10,
        merchantspend="Tools",
        merchantspendperhour=2,
        cashspend=20
    ),
    FreelanceJob(
        jobname="Orange Picker",
        jobid=2,
        workhours="08:00-14:00",
        wageperhour=14.0,
        wagemerchant="Oranges",
        wagemerchantperhour=8,
        merchantspend="Equipment",
        merchantspendperhour=3,
        cashspend=18
    ),
    FreelanceJob(
        jobname="Banana Picker",
        jobid=3,
        workhours="09:00-17:00",
        wageperhour=13.5,
        wagemerchant="Bananas",
        wagemerchantperhour=9,
        merchantspend="Gloves",
        merchantspendperhour=1,
        cashspend=22
    ),
    FreelanceJob(
        jobname="Software Developer",
        jobid=4,
        workhours="09:00-18:00",
        wageperhour=50.0,
        wagemerchant="Code",
        wagemerchantperhour=20,
        merchantspend="Licenses",
        merchantspendperhour=5,
        cashspend=100
    ),
    FreelanceJob(
        jobname="Lawyer",
        jobid=5,
        workhours="09:00-19:00",
        wageperhour=75.0,
        wagemerchant="Legal Advice",
        wagemerchantperhour=15,
        merchantspend="Research",
        merchantspendperhour=7,
        cashspend=150
    )
]

# 公共职业数据
public_jobs_data = [
    PublicJob(
        jobname="Civil Servant",
        jobid=1,
        workhours="09:00-17:00",
        wageperhour=30.0,
        cvday="3",
        voteday="5",
        jobamount=10,
        jobavailable=2
    ),
    PublicJob(
        jobname="Postal Worker",
        jobid=2,
        workhours="08:00-16:00",
        wageperhour=20.0,
        cvday="2",
        voteday="4",
        jobamount=15,
        jobavailable=5
    ),
    PublicJob(
        jobname="Police Officer",
        jobid=3,
        workhours="07:00-15:00",
        wageperhour=35.0,
        cvday="1",
        voteday="6",
        jobamount=8,
        jobavailable=1
    ),
    PublicJob(
        jobname="Firefighter",
        jobid=4,
        workhours="10:00-18:00",
        wageperhour=32.0,
        cvday="4",
        voteday="7",
        jobamount=12,
        jobavailable=3
    ),
    PublicJob(
        jobname="Public School Teacher",
        jobid=5,
        workhours="08:00-16:00",
        wageperhour=28.0,
        cvday="5",
        voteday="3",
        jobamount=20,
        jobavailable=4
    )
]

# 活动数据
game_subjects_data = [
    GameSubject(
        subjectname="Sleep",
        subjectid=1,
        availablehours="22:00-06:00",
        requirements={"energy": 10},
        spendings={"time": 1, "food": 1},
        rewards={"energy": 5, "mood": 2}
    ),
    GameSubject(
        subjectname="Study",
        subjectid=2,
        availablehours="06:00-22:00",
        requirements={"intelligence": 5},
        spendings={"time": 1, "energy": 2},
        rewards={"knowledge": 3, "intelligence": 1}
    ),
    GameSubject(
        subjectname="Medical Treatment",
        subjectid=3,
        availablehours="08:00-18:00",
        requirements={"health": 20},
        spendings={"money": 50, "time": 2},
        rewards={"health": 10, "energy": 3}
    ),
    GameSubject(
        subjectname="Socializing",
        subjectid=4,
        availablehours="18:00-23:00",
        requirements={"mood": 5},
        spendings={"time": 2, "energy": 3},
        rewards={"mood": 4, "social": 3}
    )
]

item_dict = {
    "1": {
        "item_id": "potion_001",
        "name": "Strength Potion",
        "description": "A potion that temporarily increases strength.",
        "effects": [
            {
                "attribute": "strength",
                "modifier": 10,
                "duration": 600,
                "type": "temporary",
            },
            {
                "attribute": "health_regen",
                "modifier": 5,
                "duration": 300,
                "type": "temporary",
            },
        ],
        "side_effects": [
            {
                "attribute": "agility",
                "modifier": -2,
                "duration": 600,
                "type": "temporary",
            }
        ],
        "cooldown": 1200,
    },
    "2": {
        "item_id": "potion_002",
        "name": "Agility Elixir",
        "description": "An elixir that temporarily boosts agility.",
        "effects": [
            {
                "attribute": "agility",
                "modifier": 15,
                "duration": 600,
                "type": "temporary",
            },
            {
                "attribute": "dodge_chance",
                "modifier": 10,
                "duration": 300,
                "type": "temporary",
            },
        ],
        "side_effects": [
            {
                "attribute": "strength",
                "modifier": -3,
                "duration": 600,
                "type": "temporary",
            }
        ],
        "cooldown": 1500,
    },
    "3": {
        "item_id": "potion_003",
        "name": "Health Tonic",
        "description": "A tonic that greatly restores health over time.",
        "effects": [
            {
                "attribute": "health_regen",
                "modifier": 20,
                "duration": 300,
                "type": "temporary",
            }
        ],
        "side_effects": [
            {
                "attribute": "mana_regen",
                "modifier": -5,
                "duration": 300,
                "type": "temporary",
            }
        ],
        "cooldown": 900,
    },
}