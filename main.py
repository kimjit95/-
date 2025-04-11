import discord
from discord.ext import commands
from discord import app_commands
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

tree = bot.tree  # 슬래시 명령어 관리용

# 설정 저장용 딕셔너리
registered_channels = {}
pair_channels = {}
welcome_channels = {}
thread_channels = {}

RECRUIT_CHANNEL_ID = 123456789012345678  # 예비용 기본값, 명령어로 덮어쓰기됨

DUNGEON_TYPES = [
    ("기타", "🏰"),
    ("심층", "🏰"),
    ("어비스", "🏰"),
    ("퀘스트", "🏰")
]

DUNGEON_LIST = {
    "기타": ["길드전", "보스전"],
    "심층": ["심연 1단계", "심연 2단계"],
    "어비스": ["아크던전", "타락의 심연"],
    "퀘스트": ["영웅 퀘스트", "전설 퀘스트"]
}

DIFFICULTIES = ["쉬움", "보통", "어려움"]

@tree.command(name="권한", description="서버, 직업, 닉네임을 설정하여 적절한 권한을 받습니다.")
async def 권한(interaction: discord.Interaction):
    await interaction.response.send_message("⚙️ 권한 설정 명령어입니다.")

@tree.command(name="권한_명령어동기화", description="봇의 모든 슬래시 명령어를 동기화합니다.")
async def 동기화(interaction: discord.Interaction):
    await tree.sync()
    await interaction.response.send_message("✅ 명령어 동기화 완료", ephemeral=True)

@tree.command(name="닉네임확인", description="등록된 사용자의 서버, 직업, 닉네임 정보를 확인합니다.")
async def 닉네임확인(interaction: discord.Interaction):
    await interaction.response.send_message("🧾 닉네임 정보 확인입니다.")

@tree.command(name="뿔피리_도움말", description="뿔피리봇 도움말을 보여줍니다.")
async def 도움말(interaction: discord.Interaction):
    await interaction.response.send_message("📘 뿔피리봇 도움말입니다. 파티 모집 및 설정 관련 명령어를 안내합니다.")

@tree.command(name="모집등록채널설정", description="모집 등록 양식을 게시할 채널을 설정합니다.")
async def 모집등록채널설정(interaction: discord.Interaction):
    registered_channels[interaction.guild_id] = interaction.channel_id
    await interaction.response.send_message(f"✅ 이 채널을 모집 등록 채널로 설정했습니다.")

@tree.command(name="모집목록", description="서버의 모든 모집 목록을 보여줍니다.")
async def 모집목록(interaction: discord.Interaction):
    await interaction.response.send_message("📋 현재 모집 목록은 아직 구현되지 않았습니다.")

@tree.command(name="모집채널설정", description="모집 공고를 게시할 채널을 설정합니다.")
async def 모집채널설정(interaction: discord.Interaction):
    pair_channels[interaction.guild_id] = {"공지": interaction.channel_id}
    await interaction.response.send_message("📌 이 채널을 모집 공고 채널로 설정했습니다.")

@tree.command(name="모집초기화", description="모집 등록 채널을 초기화합니다.")
async def 모집초기화(interaction: discord.Interaction):
    registered_channels.pop(interaction.guild_id, None)
    await interaction.response.send_message("♻️ 모집 채널 초기화 완료")

@tree.command(name="쓰레드채널설정", description="파티 모집 완료 시 비밀스레드를 생성할 채널을 설정합니다.")
async def 쓰레드채널설정(interaction: discord.Interaction):
    thread_channels[interaction.guild_id] = interaction.channel_id
    await interaction.response.send_message("🧵 이 채널을 스레드용 채널로 설정했습니다.")

@tree.command(name="채널페어목록", description="설정된 채널 페어 목록을 확인합니다.")
async def 채널페어목록(interaction: discord.Interaction):
    info = pair_channels.get(interaction.guild_id)
    if not info:
        await interaction.response.send_message("❌ 설정된 페어링이 없습니다.")
    else:
        await interaction.response.send_message(f"🔗 현재 등록 채널 - 공고 채널 페어: {info}")

@tree.command(name="채널페어삭제", description="등록 채널과 공고 채널의 페어링을 삭제합니다.")
async def 채널페어삭제(interaction: discord.Interaction):
    pair_channels.pop(interaction.guild_id, None)
    await interaction.response.send_message("❌ 채널 페어링 삭제 완료")

@tree.command(name="채널페어설정", description="등록 채널과 공고 채널을 페어링합니다.")
async def 채널페어설정(interaction: discord.Interaction):
    pair_channels[interaction.guild_id] = {"등록": interaction.channel_id, "공지": interaction.channel_id}
    await interaction.response.send_message("🔗 등록/공지 채널 페어링 설정 완료")

@tree.command(name="환영채널설정", description="새 사용자를 환영하는 채널을 설정합니다.")
async def 환영채널설정(interaction: discord.Interaction):
    welcome_channels[interaction.guild_id] = interaction.channel_id
    await interaction.response.send_message("👋 이 채널을 환영채널로 설정했습니다.")

@tree.command(name="test", description="테스트 명령어입니다.")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("✅ 테스트 성공")

@tree.command(name="파티모집", description="파티 모집을 시작합니다")
async def start_party(interaction: discord.Interaction):
    await interaction.response.send_message(embed=discord.Embed(
        title="파티 모집 등록 양식",
        description="1. 던전 유형\n2. 던전 종류\n3. 난이도\n4. 상세 내용\n5. 최대 인원\n모든 항목 작성 후 [모집 등록]을 눌러주세요.",
        color=discord.Color.blue()),
        view=PartyFormView(),
        ephemeral=True
    )

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user}")

import os
bot.run(os.getenv("TOKEN"))
