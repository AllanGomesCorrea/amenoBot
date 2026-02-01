from .hello import hello
from .play_song import add_song, play_pause, skip, queue, exit, now_playing, favorite_playlist, play_next, remove_song_from_queue
from .help_commands import comandos

def register_commands(bot):
    bot.tree.add_command(hello)
    bot.tree.add_command(add_song)
    bot.tree.add_command(play_next)
    bot.tree.add_command(play_pause)
    bot.tree.add_command(skip)
    bot.tree.add_command(queue)
    bot.tree.add_command(remove_song_from_queue)
    bot.tree.add_command(exit)
    bot.tree.add_command(now_playing)
    bot.tree.add_command(favorite_playlist)
    bot.tree.add_command(comandos)