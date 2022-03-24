# Disinfo_radar_development

Private repository for DRI employees and sub-contractors to develop and test initial functional ideas for Disinformation Radar project.


## File structure

As of 24.03.2022 (excluding VENV, including gitgnore directories) can be viewed here ![file structure](/file_structure.txt)
(to-do: automate updating)

## Data

Data folders are set to gitignore. Sharing and syncing of data must be coordinated. 
In the past Syncthing folders embedded in a GitHub directory work well.

## Dependencies

In addition to the requirments.txt the following commands can install other anticipated dependencies:
- nltk.download('stopwords'): run in notebook
- python -m spacy download en_core_web_sm: run in terminal


## Conceptual flow

![DRAP_1 drawio](https://user-images.githubusercontent.com/59825124/159930897-7b2c24dd-4504-42d3-a84f-1f7e20ec7bb9.svg)
