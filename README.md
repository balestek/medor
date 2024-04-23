# 🐕 medor

<p align="center">
  <img src="https://raw.githubusercontent.com/balestek/medor/master/media/medor.png">
</p>

[![PyPI version](https://badge.fury.io/py/medor.svg)](https://badge.fury.io/py/medor)
![Python minimum version](https://img.shields.io/badge/Python-3.8%2B-brightgreen)
[![Downloads](https://pepy.tech/badge/medor)](https://pepy.tech/project/medor)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/github/license/balestek/medor.svg)](https://github.com/<balestek>/medor/blob/master/LICENSE)

What _medor_'s master can say about him:
> _medor_ is a good dog. Provided you send him far enough, he can come back with a juicy bone 🦴

Medor is an OSINT (Open Source Intelligence) tool that enables you to discover the IP address of a WordPress site, even if it's obscured by a WAF (Web Application Firewall) or located within the darknet (onion services).
It requests xmlrpc.php to get the IP behind the WAF thanks to a webhook provider.

<p align="center">
  <img width="600px" src="https://raw.githubusercontent.com/balestek/medor/master/media/medor.py.png">
</p>

It requires several kibbles to work:
+ a WordPress website with an unsecured xmlrpc.php
+ a post from the WordPress website (not a page!)

_medor_ comes with few features:
+ [X] it works with the domain, the website url or a wp post
+ [x] it can find a blog post with WordPress REST API or the feed
+ [X] it updates and rotates user-agents per request
+ [x] a proxy can be used
+ [X] tor support for .onion
+ [X] option to customize the xmlrpc response webhook URL
+ [ ] _todo : an optional flask server to handle the xmlrpc.php response_
+ [ ] _todo : use list of proxies with random selection per request_
+ [ ] _todo : check an imported list of domains, hosts or url_

## Installation

Python 3.8+ is required.

### pipx (recommended)
```bash
pipx install medor
```

### pipenv
```bash
pipenv install medor
```

### pip
```bash
pip install medor
```

## Usage

### Basic usage

The command to find the IP address associated with a particular item is `find`, followed by the item you want to investigate (such as a domain, a website URL, or a post URL)

```bash
medor find website.com
# or
medor find https://www.website.com
# or
medor find https://www.website.com/a-blog-post/
```
### Proxy

#### With a single proxy

Proxy format should be protocol://user.password@IP:port if you use authentication or 
protocol://IP:port if not. The optional argument is `--proxy=yourproxy` or `-p yourproxy`.

Proxy doesn't work with .onion services as tor is used instead.

Allowed protocols : 
- http
- https
- socks5(h). For socks5h:// use socks5:// (httpx\[socks] uses socks5h by default)

```bash
medor find website.com -p http://user.password@255.255.255.255:8080
# or
medor find https://www.website.com --proxy=socks5://user.password@255.255.255.255:6154
```

### Webhook

By default, _medor_ uses a new webhook from webhook.site ([see credits](#external-webhook-service)) but you can use another service or your own with the option `--webhook=` or `-w` followed by the webhook URL.

```bash
medor find https://www.website.com -w https://website.com/webhook/kjqh4sfkq4sj5h5f
# or
medor find website.com --webhook=https://website.com/webhook/kjqh4sfkq4sj5h5f
```

### Darknet / Onion Services

_medor_ works as well with onion websites.

First, you need to install the Tor daemon, also known as little-t Tor. _medor_ needs the tor path to use tor.

When using an onion item to search for the first time, you will be prompted to enter the path of the Tor binary. If you need to change the path after the initial setup, you can use the command `medor tor_path`.

Note that it does not work with the `--proxy=` option.

The settings for Tor are as follows: the tor port is 9150 and the controller port is 9151.

```bash
medor find rtfjdnrppk7yj0424wa5i1hc6chq4nj6p3w7tu2q5qh47fmf6pi3.onion
# or
medor find http://rtfjdnrppk7yj0424wa5i1hc3chq4nj6p3w7tu2q5qh47fmf6pi3.onion
```

#### Install tor

#### Windows

1. Download Tor

Download the Tor Expert Bundle for your Windows architecture from the following link: https://www.torproject.org/download/tor/.

2. Extract the archive

Extract the tor.exe from the archive to a convenient location on your computer, such as `C:\tor\`.

3. Enter the full path of the tor.exe

When prompted during the first IP search for a .onion website, enter the full path of the tor.exe executable. For example, `C:\tor\tor.exe`.

You can also set the path of the tor executable at any time by using the command `medor tor_path`. 

##### Linux and OSX

1. Setup tor repo and install Tor

To obtain the latest version of Tor, you need to set the Tor package repository. This is important for security reasons.

Instructions for installing Tor can be found here: 
https://community.torproject.org/onion-services/setup/install/

After installing tor, you can test it by opening a terminal and running the command `tor`. This should start the tor process and print some log messages to the terminal. Once you have verified that Tor is working correctly, you can close the terminal or stop the tor process by pressing Ctrl+C in the terminal.

2. Enter the tor command when prompted

When prompted during the first IP search for a .onion website, enter `tor`.

You can also set the path of the tor executable or the tor command at any time by using the command `medor tor_path`.

### Known issues

1) If tor is already running on your system, _medor_ may not be able to launch a new instance of tor. In this case, you may see an error message indicating that. To resolve this issue, you need to stop the existing tor process or kill the tor process. 
2) If you get a "Timeout" error, especially with onion services, it may be a temporary issue with the Tor network. Try again.

### Credits

Strongly [inspired by Dan Nemec's post](https://blog.nem.ec/2020/01/22/discover-cloudflare-wordpress-ip/).

#### Requirements

```
httpx and httpx[socks]
brotlipy
stem
halo
colorama
docopt
lxml
beautifulsoup4
validators
python-dotenv
```

#### External webhook service

[![https://webhook.site](https://raw.githubusercontent.com/balestek/medor/master/media/Webhook.site.png "https://webhook.site")](https://webhook.site)

_medor_ utilizes the excellent webhook service provided by [Simon Fredsted's webhook.site](https://webhook.site). If you require a webhook service with a multitude of features, consider using it.

#### License
GPLv3
