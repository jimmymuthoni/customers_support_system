from typing import List
from setuptools import find_packages, setup

#function to get all the requirements from requirements file
def get_requirements() -> List:
    requirements: List[str] = []
    try:
        with open("requirements.txt", 'r') as file:
            lines = file.readlines()
            for line in lines:
                requirement = line.strip()
                if requirement and requirement != "-e .":
                    requirements.append(requirement)
    except Exception as e:
        raise "requirements.txt file not found" 
    return requirements

setup(
    author="jimmy",
    name="customer_suport_system",
    author_email="jimmymuthoni26@gmail.com",
    version="0.0.1",
    packages=find_packages(),
    install_requires = get_requirements(),
    python_requires = ">3.10"
    
)

