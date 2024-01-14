from tqdm.asyncio import tqdm_asyncio
from tqdm import tqdm
from pathlib import Path
import asyncio
import argparse
import aiofiles
import httpx
import re

async def download(semaphore: asyncio.Semaphore, session: httpx.AsyncClient, url: str, path: Path) -> None:
    async with semaphore, session.stream("GET", url) as response, aiofiles.open(path, "wb") as write:
        total = int(response.headers["Content-Length"])
        with tqdm_asyncio(total=total, unit_scale=True, unit_divisor=1024, unit="B", desc=path.name) as progress:
            num_bytes_downloaded = response.num_bytes_downloaded
            async for chunk in response.aiter_bytes():
                await write.write(chunk)
                progress.update(response.num_bytes_downloaded - num_bytes_downloaded)
                num_bytes_downloaded = response.num_bytes_downloaded

async def fetch_page(semaphore: asyncio.Semaphore, session: httpx.AsyncClient, url: str):
    async with semaphore:
        return await session.get(url)

async def main() -> None:
    parser = argparse.ArgumentParser(prog="Rapidgator Download")
    parser.add_argument("-u", "--user", help="Value of your `user__` cookie.", required=True)
    parser.add_argument("-d", "--dir", "--directory", help="The directory to write the files to.", default=".")
    parser.add_argument("-c", "--concurency", default=50, type=int, help="The max amount of file to download at the same time.")
    parser.add_argument("urls", nargs="*", help="The urls to download. Can also be just the hash.")
    args = vars(parser.parse_args())

    session = httpx.AsyncClient(cookies={"user__": args["user"]})
    response = await session.get("https://rapidgator.net/profile/index")
    if response.status_code == 302:
        parser.error("The session is not logged in !")

    sem = asyncio.Semaphore(args["concurency"])
    path = Path(args["dir"])

    urls: list[str] = []
    for x, url_item in enumerate(args["urls"]):
        if "\n" in url_item:
            url_chunk = [item for item in url_item.split("\n") if item]
        else:
            url_chunk = [url_item]
        for url in [item.strip() for item in url_chunk]:
            if url.startswith("https://rapidgator.net/file/"):
                urls.append(url)
            elif re.match(r"[a-z0-9]{32}", url):
                urls.append(f"https://rapidgator.net/file/{url}")
            else:
                raise ValueError(f'url {x} "{url}" is not a file hash nor url towars rapidgator file !')

    valid_urls: list[tuple[str, str]] = []
    for response in tqdm_asyncio.as_completed([fetch_page(sem, session, url) for url in urls], desc="Fetching pages ..."):
        response = await response
        if response.status_code == 200:
            match = re.search(r'<a href="(https:\/\/.+\.rapidgator.net\/download\/[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})">\s+(\S+)\s+<\/a>', response.text)
            if match:
                valid_urls.append(match.groups())
                continue
        print(f"Issue with with url {response.url}, continuing ...")

    if valid_urls:
        await asyncio.gather(*[download(sem, session, url, path / name) for url, name in valid_urls])
    else:
        print("There was no valid urls left !")

if __name__ == "__main__":
    asyncio.run(main())