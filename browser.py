import os
import sys
from collections import deque

from colorama import init, Fore, Style
from bs4 import BeautifulSoup as bs
from bs4 import Tag
import requests
from requests.exceptions import HTTPError

init(autoreset=True)

directory = ''

command_stack = deque()

command_last = ''


def parse_page(page_content):
    """
    parse page and get text from tags (p, headers, a, ul, ol, li)
    :param page_content
    :return: text within tags of page content
    """
    tags = (u'p', u'a', u'h1', u'h2', u'h3', u'h4', u'h5', u'h6',
            u'title', u'ul', u'ol', u'li')
    text = ''
    bs_object = bs(page_content, 'html.parser')
    for child in bs_object.descendants:
        if isinstance(child, Tag):
            if child.name in tags:
                tag_string = child.string
                if tag_string:
                    if child.name == u'a':
                        text += Fore.BLUE + tag_string \
                                + ' ' + Style.RESET_ALL
                    else:
                        text += tag_string + '\n'
    return text


def get_page(page_url):
    """
    get page text from url
    return: text
    """
    headers = {'User-Agent':
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362'
               }
    try:
        response = requests.get(page_url, headers=headers)
        response.raise_for_status()
    except HTTPError as http_error:
        return f'HTTP error occurred: {http_error}'
    else:
        return parse_page(response.text)


def show_web(page_url):
    """get page from url"""
    page_text = get_page(page_url)
    print(page_text)
    if directory:
        save_file(page_url, page_text)


def show_file(file_name):
    """print file from directory"""
    file_path = os.path.join(directory, file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            print(file.read())
    else:
        print('Error: Incorrect URL')


def save_file(url, content):
    """save file to directory from URL"""
    dot_pos = url.rfind('.')
    if dot_pos > -1:
        # file name from url without https:// and letters after last dot
        file_name = url[8:dot_pos]
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)


def check_command(command):
    if '.' in command:
        if command.startswith('https://'):
            web_address = command
        else:
            web_address = 'https://' + command
        show_web(web_address)
    else:
        show_file(command)


def save_command():
    if command_last:
        command_stack.append(command_last)


# get arguments of program
args = sys.argv
if len(args) > 1:
    directory = args[1]
    if not os.path.exists(directory):
        os.makedirs(directory)


while True:
    request = input('> ')
    if request == 'back':
        if len(command_stack):
            prev_request = command_stack.pop()
            check_command(prev_request)
        save_command()
        command_last = ''
    elif request == 'exit':
        break
    else:
        save_command()
        command_last = request
        check_command(request)


