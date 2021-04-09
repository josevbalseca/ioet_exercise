from setuptools import setup  # type: ignore

setup(
    name="employee_payments",
    version="1.0",
    description="calculate amout to pay by each employee in a txt file where the worked hours by day is defined",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "employee_payments=employee_payments:main",
        ]
    },
)
