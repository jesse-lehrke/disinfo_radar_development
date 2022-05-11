# Disinfo_radar_development

Private repository for DRI employees and sub-contractors to develop and test initial functional ideas for Disinformation Radar project.

The "pipe" folder should be kept clean and is for final MVP code (i.e. deployment ready with only debugging remaining)


## File structure

As of 11.05.2022 (excluding VENV, including gitgnore directories) can be viewed here ![file structure](/file_structure.txt)
(to-do: automate updating)

## Data

Data folders are set to gitignore except in "pipe". Sharing and syncing of data must be coordinated. 
In the past Syncthing folders embedded in a GitHub directory work well.

## Dependencies

In addition to the requirments.txt the following commands can install other anticipated dependencies:
- nltk.download('stopwords'): run in notebook
- python -m spacy download en_core_web_sm: run in terminal


## Conceptual flow

![DRAP_1 drawio](https://user-images.githubusercontent.com/59825124/167805479-17be45b3-d474-4b88-8476-975933a2d5c1.svg)
