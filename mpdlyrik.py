import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i",  "--ip",       default="127.0.0.1", help="adress of the mpd server"                 )
parser.add_argument("-p",  "--port",     default="6600",      help="port of the mpd server"                   )
parser.add_argument("-pw", "--password", default="",          help="password to the server in plaintext"      )
parser.add_argument("-in", "--interval", default="5",         help="update interval, between 1-255"           )
parser.add_argument("-fr", "--fileroot", default="./",        help="where mpd has it's music root"             )
parser.add_argument("-of", "--offset",   default="4",         help="number of lines to display before current" )
args = parser.parse_args()

from mpd import MPDClient

client = MPDClient()
client.connect(str(args.ip), int(args.port))
if args.password != "":
    client.password(str(args.password))

def loadlyrics(path):
    s = []
    try:
        with open(path) as f: s = f.read().split("\n")
    except:
        return [[0, "the lyrics file could not be loaded"]]
    lyrics = []
    for l in s:
        if l == "": continue
        l = l.split("]")
        t = l[0][1:]
        l = "]".join(l[1:])
        t = t.split(":")
        print(t)
        if t == "":
            t[0] = 0
        t = int(t[0]) * 60 + float(t[1])
        
        lyrics.append([t, l])
    return lyrics

def findCurrent(lyrics, time):
    last = 0
    for i in range(0, len(lyrics)):
        if lyrics[last][0] <= lyrics[i][0]:
            if lyrics[i][0] < time:
                last = i
    return last
        
import curses

def printLyrics(stdscr, lyrics, selected, height, width):
    space = max((0 - selected - int(args.offset) * -1), 0)
    stdscr.addstr("\n"*space)
    for i in range(0, len(lyrics)):
        if i >= max(0, selected - int(args.offset)):
            if i < selected - int(args.offset) + height:
                stdscr.addstr(lyrics[i][1] + "\n", curses.A_STANDOUT * (selected == i))

def main(stdscr):
    curses.halfdelay(int(args.interval))
    
    path = ""
    lyrics = []

    while True:
        status = client.status()

        currentsong = client.currentsong()
        currentpath = currentsong["file"].split(".")
        currentpath[-1] = "lrc"
        currentpath = args.fileroot + ".".join(currentpath)
        if currentpath != path:
            lyrics = loadlyrics(currentpath)
            path = currentpath

        time = float(status["elapsed"])
        currentline = findCurrent(lyrics, time)
        
        stdscr.clear()
        stdscr.addstr(str(time) + " " + str(currentline) + " " + currentsong["title"] + "\n")
        
        size = stdscr.getmaxyx()

        printLyrics(stdscr, lyrics, currentline, size[0] - 4, size[1])

        inp = stdscr.getch()
        if inp != -1:
            if inp == 113:
                break
    pass

curses.wrapper(main)

client.close()
client.disconnect()
