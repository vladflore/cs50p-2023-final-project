from PIL import Image
from io import BytesIO
import base64
from common_fetch_strategy import FetchData, ResponseType, Strategy

from models import Series
from settings import TOKEN, TV_DB_API
from utils import createElement
from datetime import datetime


async def search_series(query: str, fetch_strategy: Strategy) -> list[Series]:
    url = f"{TV_DB_API}/search?query={query}&type=series"
    headers = {"Authorization": f"Bearer {TOKEN}", "accept": "application/json"}

    data = FetchData(url, headers, fetch_strategy)
    content = await data.fetch()

    if not content["data"]:
        return []

    return [
        Series(
            id=s.get("id", ""),
            name=s.get("name", ""),
            status=s.get("status", ""),
            tvdb_id=s.get("tvdb_id", ""),
            thumbnail=s.get("thumbnail", ""),
        )
        for s in content["data"]
    ]


def reverse_date(date: str) -> str:
    return "-".join(date.split("-")[::-1])


def delta_days(date: str) -> int:
    return (datetime.now() - datetime.strptime(date, "%d-%m-%Y")).days


async def render_search_series():
    from pyodide_fetch_strategy import PyodideStrategy

    pyodide_strategy = PyodideStrategy()

    query = Element("search-input").element.value
    series: list[Series] = await search_series(query, fetch_strategy=pyodide_strategy)
    from js import document

    series_table_body = document.getElementById("series")
    if series_table_body.childElementCount > 0:
        series_table_body.innerHTML = ""

    continuing, upcoming, ended = 0, 0, 0
    for s in series:
        if s.status == "Continuing":
            continuing += 1
        elif s.status == "Ended":
            ended += 1
        elif s.status == "Upcoming":
            upcoming += 1

    document.getElementById("total-results-count").textContent = f"{len(series)}"
    document.getElementById("total-continuing-count").textContent = f"{continuing}"
    document.getElementById("total-upcoming-count").textContent = f"{upcoming}"
    document.getElementById("total-ended-count").textContent = f"{ended}"
    document.getElementById("total-results-count").parentElement.classList.remove(
        "d-none"
    )
    document.getElementById("spinner").classList.remove("d-none")
    for s in series:
        new_row = createElement("tr")

        title_cell = createElement("th", f"{s.name}", scope="row")
        new_row.appendChild(title_cell)

        pyodide_strategy.response_type = ResponseType.BYTES
        thumb = await generate_thumbnail(s.thumbnail, fetch_strategy=pyodide_strategy)
        cover_cell = createElement(
            "td",
            inner_html=f'<img src="{thumb}" class="img-fluid" />'
            if thumb
            else "No thumbnail available",
        )
        new_row.appendChild(cover_cell)

        status_cell = createElement("td", text_content=f"{s.status}")
        new_row.appendChild(status_cell)

        pyodide_strategy.response_type = ResponseType.JSON
        aired_data = await get_aired_data(s, fetch_strategy=pyodide_strategy)

        next_aired = aired_data["next_aired"]
        eye_icon = "<i class='bi bi-eye-fill'></i>"

        if next_aired:
            reversed_next_aired = reverse_date(next_aired)
            dd = delta_days(reversed_next_aired)
            if dd < 0:
                cell_html = f"{eye_icon} in {abs(dd)} days ({reversed_next_aired})"
            else:
                cell_html = f"{reversed_next_aired}"
            next_episode_cell = createElement(
                "td",
                inner_html=cell_html,
            )
            next_episode_cell.classList.add("text-success")
        else:
            text_content = f"No upcoming episodes {'yet' if s.status in ['Continuing', 'Upcoming'] else ''}"
            next_episode_cell = createElement("td", text_content=text_content)
        new_row.appendChild(next_episode_cell)

        last_episode_cell = document.createElement("td")
        last_aired = aired_data["last_aired"]
        last_episode_cell = createElement(
            "td", text_content=f"{reverse_date(last_aired) if last_aired else 'N/A'}"
        )
        new_row.appendChild(last_episode_cell)

        if s.status == "Continuing":
            new_row.classList.add("table-success")
        elif s.status == "Ended":
            new_row.classList.add("table-danger")
        elif s.status == "Upcoming":
            new_row.classList.add("table-info")

        series_table_body.appendChild(new_row)
    document.getElementById("spinner").classList.add("d-none")


async def get_aired_data(s: Series, fetch_strategy: Strategy) -> dict[str, str]:
    url = f"{TV_DB_API}/series/{s.tvdb_id}"
    headers = {"Authorization": f"Bearer {TOKEN}", "accept": "application/json"}
    data = FetchData(url, headers, strategy=fetch_strategy)
    content = await data.fetch()
    next_aired = content["data"]["nextAired"]
    last_aired = content["data"]["lastAired"]

    return {
        "next_aired": next_aired if next_aired else None,
        "last_aired": last_aired if last_aired else None,
    }


async def generate_thumbnail(
    thumbnail_url: str, fetch_strategy: Strategy
) -> str | None:
    try:
        data = FetchData(thumbnail_url, {}, strategy=fetch_strategy)
        content = await data.fetch()
        image = Image.open(BytesIO(content))
        image.thumbnail((100, 100))
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return (
            f"data:image/jpeg;base64,{base64.b64encode(buffered.getvalue()).decode()}"
        )
    except Exception:
        js.console.log("Error generating thumbnail")
        return None
