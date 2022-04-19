import asyncio

from dude import select


@select(selector="a", group_css=".g")
async def result_url(element, page):
    handle = await element.getProperty("href")
    return {"url": await handle.jsonValue()}


@select(css="h3:nth-child(2)", group_css=".g")
async def result_title(element, page):
    return {"title": await page.evaluate("(element) => element.textContent", element)}


@select(css="div[style='-webkit-line-clamp\\3A 2']", group_css=".g")
async def result_description(element, page):
    return {"description": await page.evaluate("(element) => element.textContent", element)}


@select(css="#L2AGLb > div", setup=True)
async def agree(element, page):
    await asyncio.gather(
        page.waitForNavigation(),
        element.click(),
    )


@select(css="#pnnext", navigate=True)
async def next_page(element, page):
    await asyncio.gather(
        page.waitForNavigation(),
        element.click(),
    )


if __name__ == "__main__":
    import dude

    dude.run(
        urls=["https://www.google.com/search?q=deepfake&hl=en"],
        parser="pyppeteer",
        output="data.json",
        headless=False,
        pages=2,
    )
