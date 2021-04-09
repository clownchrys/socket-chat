import termcolor


def highlight(string, color):
    return termcolor.colored(string, color, attrs=['bold'])
