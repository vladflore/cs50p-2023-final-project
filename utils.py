from models import Series


def createElement(
    tag: str, text_content: str = "", inner_html: str = "", scope: str = ""
):
    from js import document

    element = document.createElement(tag)
    if text_content:
        element.textContent = text_content
    if inner_html:
        element.innerHTML = inner_html
    if scope:
        element.scope = scope
    return element
