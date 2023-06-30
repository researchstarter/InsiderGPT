import os
from collections import OrderedDict
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "requirements.txt")) as f:
    dependencies = f.read().strip().split("\n")

setup(
    name="insidergpt",
    version="0.8.0",
    description="InsiderGPT, GPT bilan ta'minlangan qudratli sinov dasturi",
    long_description="""
    InsiderGPT - bu ChatGPT tomonidan quvvatlangan kirishni tekshirish vositasi. U penetratsion test jarayonini avtomatlashtirish uchun mo'ljallangan. U dastlab ChatGPT tepasida prototip qilingan va umumiy rivojlanishda ham, maxsus operatsiyalarda ham penetratsiya testerlarini boshqarish uchun interaktiv rejimda ishlaydi.
    """,
    author="Insider Team",
    license="MIT License",
    packages=["insidergpt"] + find_packages(),
    # packages=find_packages(),
    # scripts=['insidergpt/main.py'],
    install_requires=dependencies,
    entry_points={
        "console_scripts": [
            "insidergpt=insidergpt.main:main",
            "insidergpt-cookie=insidergpt.extract_cookie:main",
            "insidergpt-connection=insidergpt.test_connection:main",
        ]
    },
)
