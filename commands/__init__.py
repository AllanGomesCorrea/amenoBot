from .hello import hello
from .play_song import add_song, play_pause, skip, queue, exit

def register_commands(bot):
    bot.tree.add_command(hello)
    bot.tree.add_command(add_song)
    bot.tree.add_command(play_pause)
    bot.tree.add_command(skip)
    bot.tree.add_command(queue)
    bot.tree.add_command(exit) 