# 支持网址：https://www.52bqg.net/
import asyncio
import os
import time

import aiofiles
import aiohttp
from lxml import html


async def prepare_url(c_url, href):
    timeout = aiohttp.ClientTimeout(total=7)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(c_url) as page:
            tree = html.fromstring(await page.read())
            url = []
            reach_or_not = False
            for u in tree.xpath('//dd/a/@href'):
                if reach_or_not == False:
                    if u == href:
                        reach_or_not = True
                    else:
                        continue
                url.append(c_url + u)
            print("小说网址准备完成")
            return url


async def download(url, file_num):
    try:
        timeout = aiohttp.ClientTimeout(total=7)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as page:
                tree = html.fromstring(await page.read())
                title = tree.xpath('//*[@class="bookname"]/h1/text()')[0]
                async with aiofiles.open(cache_path + "/" + file_num + ".txt",
                                         "a") as file:
                    await file.write(title + "\n")
                    for c in tree.xpath('//*[@id="content"]/text()'):
                        await file.write(c.lstrip() + "\n")
                    print(title + "下载完成")
    except Exception:
        return url, file_num


async def async_door():
    s_url = input("请输入小说第一章的网址：")
    s_time = time.time()

    c_url = ""
    for i in s_url.split("/")[:-1]:
        c_url += i + '/'

    task = []
    i = 0
    for u in await prepare_url(c_url, s_url.split("/")[-1]):
        task.append(asyncio.create_task(download(u, str(i))))
        i += 1

    while True:
        aga_item = []
        for t in task:
            await t
            if t.result():
                aga_item.append(t.result())

        if not aga_item:
            break

        task = []
        for im in aga_item:
            task.append(asyncio.create_task(download(im[0], im[1])))

    return s_time


def integrate():
    print("文件整合中......")
    content = []
    for i in range(len(os.listdir(cache_path))):
        with open(cache_path + "/" + str(i) + ".txt", "r") as r_file:
            content.append(r_file.read())

    with open(output_path, "w") as w_file:
        for c in content:
            w_file.write(c)

    print("文件整合完成")


def begin():
    if os.path.exists(cache_path):
        if os.path.getsize(cache_path):
            for f in os.listdir(cache_path):
                os.remove(cache_path + "/" + f)
    else:
        os.mkdir(cache_path)
    s_time = asyncio.run(async_door())
    integrate()
    print("运行成功")
    print("总用时：", time.time() - s_time, "秒")


if __name__ == "__main__":
    cache_path = "./cache"
    output_path = "./ebook.txt"
    begin()
