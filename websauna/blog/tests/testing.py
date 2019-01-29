"""Common testing functions and utilities."""

# Standard Library
from typing import Iterable

from splinter.driver import DriverAPI


def pagination_test(browser: DriverAPI, items: Iterable[object], items_per_page: int, title_selector: str):
    """Checks if pagination works correctly."""

    def pagination_element(text: str, disabled=False):
        return browser.find_by_xpath(
            '//div[@class="pagination-wrapper"]//li[@class="{disabled}"]/a[text()[contains(.,"{text}")]]'.format(
                text=text, disabled="disabled" if disabled else ""
            )
        )

    # checking disabled buttons (First and Previous)
    assert pagination_element("First", disabled=True)
    assert pagination_element("Previous", disabled=True)

    # checking not disabled buttons (Next and Last)
    assert pagination_element("Next")
    assert pagination_element("Last")

    # navigating to the last page (checking that Last works correctly)
    pagination_element("Last").click()

    # checking not disabled buttons (First and Previous)
    assert pagination_element("First")
    assert pagination_element("Previous")

    # checking disabled buttons (Next and Last)
    assert pagination_element("Next", disabled=True)
    assert pagination_element("Last", disabled=True)

    # navigating to the first page (checking that First works correctly)
    pagination_element("First").click()

    # checking if "next" works correctly
    posts_titles = set(i.title for i in items)
    for page in range(0, len(items), items_per_page):
        rendered_posts_titles = set(i.text for i in browser.find_by_css(title_selector))
        assert rendered_posts_titles.issubset(posts_titles)
        posts_titles -= rendered_posts_titles
        if page < len(items) - items_per_page:
            pagination_element("Next").click()

    # checking if "prev" works correctly
    posts_titles = set(i.title for i in items)
    for page in range(0, len(items), items_per_page):
        rendered_posts_titles = set(i.text for i in browser.find_by_css(title_selector))
        assert rendered_posts_titles.issubset(posts_titles)
        posts_titles -= rendered_posts_titles
        if page < len(items) - items_per_page:
            pagination_element("Previous").click()
