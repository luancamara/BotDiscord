import datetime
import os
import pprint
import asyncio
import json
import time
from datetime import date

import discord
from discord.ext import commands

from youtube_dl import YoutubeDL
import re

URL_REG = re.compile(r'https?://(?:www\.)?.+')
YOUTUBE_VIDEO_REG = re.compile(r"(https?://)?(www\.)?youtube\.(com|nl)/watch\?v=([-\w]+)")


class blacklist(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="blacklist", help="Blacklista um jogador", aliases=["bl"])
    async def blacklist(self, ctx: commands.Context, *, query: str = ""):
        data = f"{datetime.date.today().day}/{datetime.date.today().month}/{datetime.date.today().year}"
        embedvc = discord.Embed(colour=12255232)
        blacklist = get_blacklist()
        player_valido = False

        if not blacklist.keys():
            id = str(0)
        else:
            id = str(len(blacklist.keys()))

        player = query.split("-")

        if len(player) != 2:
            embedvc.description = "Está faltando informação, favor verificar"
        else:
            if verifica_bl(player[0].strip()):
                embedvc.description = "Jogador já está blacklistado"
            else:
                d = {id: {"jogador": player[0].strip(), "motivo": player[1].strip(), "data": data}}
                embedvc.description = f"""
                                                    Você blacklistou o jogador **{d[id]['jogador']}**

                                                    **Motivo**: {d[id]['motivo']}
                                                    **Data**: {d[id]['data']}

Reaja com ✅ para confirmar e ❌ para cancelar"""
                player_valido = True

        embedvc.colour = 1646116
        msg = await ctx.reply(embed=embedvc)
        if player_valido:
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            try:
                reaction, user = await self.client.wait_for('reaction_add', check=lambda reaction, user: user != self.client.user, timeout=10)
            except asyncio.TimeoutError:
                await msg.delete()
                await ctx.reply("Expirou o tempo de confirmação")
            else:
                if check(reaction):
                    blacklist.update(d)
                    salvar(blacklist)
                    embedvc.description = "Confirmado!"
                    await ctx.reply(embed=embedvc)
                else:
                    embedvc.description = "Cancelado!"
                    await ctx.reply(embed=embedvc)

    @commands.command(name="check_blacklist", help="Checka a Blacklist de um jogador",
                      aliases=["cbl", "checkbl", "checkblacklist", "check"])
    async def check_blacklist(self, ctx: commands.Context, *, query: str = ""):

        embedvc = discord.Embed(colour=12255232)
        jogador = query

        embedvc.colour = 1646116
        if jogador.strip() == "":
            embedvc.description = "Nenhum jogador foi informado"
        else:
            if verifica_bl(jogador):
                embedvc.description = f"O nick **{jogador}** está na blacklist"
            else:
                embedvc.description = f"O nick **{jogador}** está limpo"

        await ctx.reply(embed=embedvc)

    @commands.command(name="unblacklist", help="Remove um jogador da blacklist", aliases=["unbl"])
    async def unblacklist(self, ctx: commands.Context, *, query: str = ""):
        embedvc = discord.Embed(colour=12255232)
        blacklist = get_blacklist()

        if verifica_bl(query.strip()):
            embedvc.description = f"""Deseja remover o jogador **{query.strip()}** da blacklist?
            
            Reaja com ✅ para confirmar e ❌ para cancelar"""
            msg = await ctx.reply(embed=embedvc, delete_after=15)
            await msg.add_reaction("✅")
            await msg.add_reaction("❌")
            try:
                reaction, user = await self.client.wait_for('reaction_add', check=lambda reaction, user: user != self.client.user, timeout=10)
            except asyncio.TimeoutError:
                await msg.delete()
                embedvc.description = "Expirou o tempo de confirmação"
            else:
                if check(reaction):
                    blacklist.pop(id_bl(query))
                    corrige_ids(blacklist)
                    embedvc.description = "Jogador removido da blacklist"
                else:
                    embedvc.description = "Cancelado, jogador não removido da blacklist!"
        else:
            embedvc.description = "Jogador não está na blacklist"
            embedvc.colour = 1646116
        await ctx.reply(embed=embedvc)

    @commands.command(name="allbl", help="Retorna toda a blacklist")
    async def allbl(self, ctx: commands.Context, *, query: str = ""):
        embedvc = discord.Embed(colour=12255232)
        embedvc.colour = 1646116
        msg = get_bl()
        if msg ==    '':
            msg = "Blacklist Vazia"
        embedvc.description = msg
        await ctx.reply(embed=embedvc)


def setup(client):
    client.add_cog(blacklist(client))

def check(reaction):
    if reaction.emoji == '✅':
        return True
    if reaction.emoji == '❌':
        return False

def verifica_bl(jogador):
    arquivo_bl = open("blacklist.json", "r+")
    blacklist = dict(eval(arquivo_bl.readline()))
    for key in blacklist:
        if blacklist[key]['jogador'] == jogador:
            return True
    return False

def get_bl():
    arquivo_bl = open("blacklist.json", "r+")
    blacklist = dict(eval(arquivo_bl.readline()))
    msg = ""
    for key in blacklist:
        msg = msg + f"**Jogador:** {blacklist[key]['jogador']}\n**Motivo:** {blacklist[key]['motivo']}\n**Data:** {blacklist[key]['data']}\n\n"
    return msg


def id_bl(jogador):
    arquivo_bl = open("blacklist.json", "r+")
    blacklist = dict(eval(arquivo_bl.readline()))
    for key in blacklist:
        if blacklist[key]['jogador'] == jogador:
            return key
    return ""


def corrige_ids(blacklist):
    bl_new = dict()
    i = 0
    for key in blacklist.keys():
        bl_new[str(i)] = blacklist[key]
        i += 1
    salvar(bl_new)


def salvar(bl):
    arquivo_bl = open("blacklist.json", "r+")
    arquivo_bl.truncate(0)
    arquivo_bl.seek(0)
    arquivo_bl.write(json.dumps(bl))


def get_blacklist():
    arquivo_bl = open("blacklist.json", "r+")
    blacklist = dict(eval(arquivo_bl.readline()))
    return blacklist
