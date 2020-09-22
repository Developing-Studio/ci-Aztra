import discord

def greeting_message(fmt: str, member: discord.Member):
    return fmt.format(
        user=member,
        guild=member.guild
    )