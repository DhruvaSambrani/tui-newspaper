#!/usr/bin/env python3

import art
import curses
from curses import wrapper
import os
import random
import time


class Article:
    def __init__(self, filename):
        self.content = open(filename).read().replace("\n", "\n ")
        self.title = filename.name.split(".")[0].strip()

    def getcontent(self, width):
        words = self.content.split(" ")
        lines = []
        i = 0
        while i < len(words):
            line = ""
            while i < len(words) and (len(line + words[i]) + 1 < width):
                line = line + " " + words[i]
                i = i + 1
                if line[-1] == "\n":
                    break
            lines.append(line)
        return " " + "\n".join(lines).strip()

    def small(self, anum, height, width):
        c = str(anum) + ". " + self.title + "\n" + "=" * \
            (width - 1) + "\n" + self.getcontent(width)
        lines = c.split("\n")
        if len(lines) > height:
            lines = lines[:height]
            lines[-1] = lines[-1][:-15] + "... Read More"
        text = "\n".join(lines).strip()
        return text


def printall(articles, stdscr, minheight, yoffset, numcols):
    colwidth = int(curses.COLS // numcols) - 1
    heights = [0 for _ in range(numcols)]
    for i in range(len(articles)):
        column = min((val, idx) for (idx, val) in enumerate(heights))[1]
        height = minheight + random.randint(-6, 6)
        subwin = stdscr.subpad(
            height,
            colwidth,
            heights[column] + yoffset,
            (colwidth + 1) * (column))
        heights[column] += height
        contentwin = subwin.derwin(height - 2, colwidth - 2, 1, 1)
        contentwin.addstr(
            articles[i].small(
                chr(ord("a") + i),
                height - 2,
                colwidth - 2),
            curses.color_pair(1))
        subwin.border()
    return max(heights) + yoffset


def makeheading(page, heading, color):
    header = page.subwin(6, curses.COLS - 1, 0, 0)
    head_lines = art.text2art(heading, "cybermedium").split("\r\n")
    head_lines = [line.center(curses.COLS - 2) for line in head_lines]
    art_heading = "\n".join(head_lines)
    header.addstr("\n" + art_heading, curses.color_pair(color) | curses.A_BOLD)
    header.box()
    return header


def printone(article_idx, articles, page, stdscr):
    page.clear()
    makeheading(page, articles[article_idx].title, 4)
    content = articles[article_idx].getcontent(curses.COLS - 4)
    height = content.count("\n") + 1
    subwin = page.subpad(height + 2, curses.COLS - 1, 6, 0)
    contentwin = subwin.derwin(height, curses.COLS - 3, 1, 1)
    contentwin.addstr(content, curses.color_pair(2))
    subwin.border()
    return height + 8


def frontpage(articles, page):
    page.clear()
    makeheading(page, "The IISER Times", 3)
    return printall(articles, page, 12, 7, 3)


def refresh_loop(page, stdscr, articles):
    maxheight = frontpage(articles, page)
    scroll_pos = 0
    page.refresh(scroll_pos, 0, 0, 0, curses.LINES - 1, curses.COLS - 1)
    key = stdscr.getch()
    while(True):
        if key == curses.KEY_DOWN:
            scroll_pos = min(scroll_pos + 2, maxheight - curses.LINES)
        elif key == curses.KEY_UP:
            scroll_pos = max(scroll_pos - 2, 0)
        elif key in range(ord("a"), ord("a") + len(articles)):
            maxheight = printone(key - ord("a"), articles, page, stdscr)
            scroll_pos = 0
        elif key == ord("0"):
            maxheight = frontpage(articles, page)
            scroll_pos = 0
        elif key == ord(":"):
            break
        else:
            pass
        page.touchwin()
        page.refresh(scroll_pos, 0, 0, 0, curses.LINES - 1, curses.COLS - 1)
        key = stdscr.getch()


def main(stdscr):
    stdscr.refresh()
    curses.curs_set(False)
    curses.init_pair(1, curses.COLOR_GREEN, 0)
    curses.init_pair(2, curses.COLOR_BLUE, 0)
    curses.init_pair(3, curses.COLOR_YELLOW, 0)
    curses.init_pair(4, curses.COLOR_RED, 0)
    stdscr.bkgd(" ", curses.color_pair(1))
    stdscr.refresh()
    articles = []
    with os.scandir("./articles") as dirs:
        for entry in dirs:
            articles.append(Article(entry))
    page = curses.newpad(1000, curses.COLS - 1)
    refresh_loop(page, stdscr, articles)


wrapper(main)
