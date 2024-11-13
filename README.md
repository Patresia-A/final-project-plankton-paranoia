[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/hkiYfuZI)
# Instructions

This final project involves working in groups of 3 to 5 members to develop a web app. The goal is to apply key software engineering practices discussed throughout the semester. You and your team have the freedom to choose what to implement for this project, as long as the following requirements are met. 

# Requirements 

## Web App Development

* The software must be a web app written in Python, with the capability to create and authenticate users.

## Development Methodology

* Scrum must be used as the software development methodology.
* At least three sprints must be done to complete this project. 

## Project Documentation

* The project must include a vision statement describing the purpose of the software, the problem it aims to solve, and the target audience.
* A use case diagram must be constructed to provide a high-level view of possible user interactions with the system.
* Scrum meeting notes should be taken and shared. 
* A final progress report must be created using the provided burndown template (Excel spreadsheet). 

## User Stories

* Describe at least six user stories in detail, including their acceptance criteria and point estimates.
* User stories must be referred to as US#1, US#2, etc.
* At least one user story, not related to user creation or authentication, must be detailed using a sequence diagram.

## Class Diagram

* A class diagram should be built for the model classes used in the project, including their associations.

## Version Control

* Create a (public) GitHub repository for the project in the [msu-denver](https://github.com/msu-denver/) organization, following the file structure explained later in this document.
* Add all team members and the instructor as collaborators to the project’s GitHub repository.
* There should be two long-lived branches: main (for the stable release) and dev (for the unstable release).
* The main branch must be protected and require a code review before a pull request is approved.

## Code Standards

* All source code must have a consistent header comment with a brief description and its author(s).
* Code must comply with the PEP8 code style standard.
* Code will be inspected for best practices related to commenting, naming, formatting, function decomposition, object-oriented programming (OOP), error handling, and more.

## Testing

* Provide at least one white-box and one black-box test, neither of them related to user creation or authentication.
* Generate a test coverage report using Python’s coverage tool.

## Deployment

* The final product must be deployed using Docker containerization technology.
* All project requirements must be frozen into a **requirements.txt** file.
* The project must have database persistence, using a database other than SQLite. 
* At a minimum, a three-layer software architecture is expected.
* Deploy the project using Docker Compose, with at least two containers.

# GitHub Repository Structure 

You are required to create a (separate) GitHub repository to host this project. The repository should have (at a minimum) the following structure: 

```
README.md
Dockerfile
docker-compose.yml
requirements.txt
src/
tests/
uml/
scrum/
```

Use the provided **README_TEMPLATE.md** for information about the format expected for the project's README file. 

Feel free to add other folders as you see fit. 

# Project Submission

Commit this **README.md** file with the link of your project's GitHub repository below: 

```
GitHub repository: <URL>
```

# Rubric

```
+5 Project's README file: mission statement
+5 Project's README file: use case diagram
+5 Project's README file: sequence diagram 
+10 Project's README file: user stories (~ 6 x 1.5)
+5 Project's README file: class diagram for the model classes
+5 GitHub repository organization, branches, and main branch protection
+10 Scrum notes
+10 implementation (~ 5 x 2)
+5 Code inspection: PEP8 compliance 
+5 Code inspection: comments, naming, functions, formatting, OOP best practices, error handling, etc.
+10 Testing requirements
+5 Project's README file: test coverage report using Python's **coverage**
+5 Project's Deployment
+15 team/self evaluation
-10 user creation not available/working
-10 user authentication not available/working 
-5 penalty for each user story not completed up to 25 points deduction
-5 **main** branch does not have consistent commits 
-5 **dev** branch does not have consistent commmits
-5 no burndown chart was created
```