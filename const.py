ANSI_CODE: dict[str, dict[str, str]] = {
    'cursor': {
        'reset': '\033[H'
    },
    'charstyle': {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'faint': '\033[2m',
        'italic': '\033[3m',
        'underline': '\033[4m',
        'blink': '\033[5m',
        'reverse': '\033[7m',
        'conceal': '\033[8m',
        'strike': '\033[9m'
    },
    'foreground': {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m'
    },
    'background': {
        'black': '\033[40m',
        'red': '\033[41m',
        'green': '\033[42m',
        'yellow': '\033[43m',
        'blue': '\033[44m',
        'magenta': '\033[45m',
        'cyan': '\033[46m',
        'white': '\033[47m'
    }
}

SYMBOLS: dict[str, dict[str, str]] = {
    'alpha': {
        'dead': 'D',
        'alive': 'A'
    },
    'binary': {
        'dead': '0',
        'alive': '1'
    },
    'block': {
        'dead': ' ',
        'alive': '█'
    },
    'emoji': {
        'dead': '😅😇🤪🤗🤭😴🤕🤢🤮🤧🥶😵🤯😨😰😭😱😖😡😠🤬😈👿🤡👻',
        'alive': '😄😁😆🤣😊🥰😍😘😚😋🤤🥵🥳😳😤'
    },
    'legacy': {
        'dead': '⬜',
        'alive': '⬛'
    },
}
