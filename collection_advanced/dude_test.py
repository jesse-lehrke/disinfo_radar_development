# Imports
import pandas as pd

from dude import select


@select(css="a.url")
def result_url(element):
    return {"url": element.get_attribute("href")}


@select(css=".title")
def result_title(element):
    return {"title": element.text_content()}


@select(css=".description")
def result_description(element):
    return {"description": element.text_content()}

@select(css="h1")
#"main-heading"
def heading(element):
    return {"header": element.text_content()}

if __name__ == "__main__":
      from pathlib import Path

      import dude
      url = "https://us13.campaign-archive.com/home/?u=67bd06787e84d73db24fb0aa5&id=6c9d98ff2c"
      url2 = "https://www.cna.org/centers/cna/sppp/rsp/russia-ai-archive#newsletters"
      url3 = "https://chinai.substack.com/archive?sort=new"
      url4 = "https://www.bbc.com/news/world-europe-61071243"
      #html = f"file://{(Path(__file__).resolve().parent / 'dude.html').absolute()}"
      
      dude.run(urls=[url4])

      #result_description(out)