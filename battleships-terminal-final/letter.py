'''
A class to create colored letters.

Letter('a', 'red') creates a red 'a'. So you can print(Letter('a', 'red'))

Only 'red', 'green' or 'yellow' colors are currently supported
'''
class Letter:
    def __init__(self, ch, color):
        self.ch = ch
        self.color = color

    def __str__(self):
        ch = self.ch
        # 256-color mode
        # foreground ESC[38;5;#m
        # background ESC[48;5;#m
        # https://en.wikipedia.org/wiki/ANSI_escape_code
        if self.color == 'green':
            # bold green
            ch = u'\u001b[1m\u001b[38;5;34m{}\u001b[0m'.format(self.ch)
        elif self.color == 'yellow':
            # bold yellow
            ch = u'\u001b[1m\u001b[38;5;226m{}\u001b[0m'.format(self.ch)
        elif self.color == 'red':
            # light gray
            ch = u'\u001b[1m\u001b[38;5;196m{}\u001b[0m'.format(self.ch)
        return str(ch)
    