import discord
import aiohttp
import os
# ================= CONFIGURAÇÕES =================
TOKEN = os.getenv('DISCORD_TOKEN') 
ID_CANAL_LIBERACAO = 1388213523892535467  # Canal onde os alunos enviam o e-mail
URL_PLANILHA = 'https://script.google.com/macros/s/AKfycbzyogTCbdzgCLp6ky8OocjYmfxk2ma2KGZ_ClegBrWeuAHd2Nux2AW7o-ZZAuhmB1E/exec'  # URL da planilha 

# ================ INTENTS ========================
# Mapeamento de course_id para cargos do Discord
COURSE_ID_TO_ROLE = {
    "FS-EMP-N1-09-25": "estudante-emp-noite1", 
    "FS-EMP-N2-09-25": "estudante-emp-noite2",
    "FS-EMP-M1-09-25": "estudante-emp-manhã1",
    "FS-EMP-M2-09-25": "estudante-emp-manhã2",
    "FE-LOR-M-09-25": "estudante-bit-manhã",
    "FE-LOR-MC-09-25": "estudante-bit-mañana",
    "FE-LOR-N-09-25": "estudante-bit-noite",
   
   
}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)

# ================ FUNÇÃO: BUSCAR DADOS DA PLANILHA ========================
async def carregar_dados():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(URL_PLANILHA) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    print(f"❌ Erro ao buscar planilha: status {resp.status}")
                    return []
    except Exception as e:
        print(f"❌ Erro ao acessar a planilha: {e}")
        return []

# ================ EVENTO: BOT CONECTADO ========================
@client.event
async def on_ready():
    print(f'✅ Bot conectado como {client.user}')
    for guild in client.guilds:
        print(f"📌 Servidor: {guild.name}")
        print("📎 Cargos disponíveis:")
        for role in guild.roles:
            print(f"- {role.name}")

# ================ EVENTO: MENSAGEM RECEBIDA ========================
@client.event
async def on_message(message):
    if message.channel.id != ID_CANAL_LIBERACAO or message.author.bot:
        return

    email_digitado = message.content.strip().lower()
    dados = await carregar_dados()

    aluno = next((a for a in dados if a.get("email", "").lower() == email_digitado), None)

    if not aluno:
        await message.channel.send(f"{message.author.mention}, Você é aluno Empower sua turma ainda não foi liberada ❌")
        print(f"❌ E-mail não encontrado: {email_digitado}")
        return
    

    course_id = aluno.get("course_id", "").strip()
    cargo_nome = COURSE_ID_TO_ROLE.get(course_id)

    if not cargo_nome:
        await message.channel.send(f"{message.author.mention}, curso não reconhecido: `{course_id}` ⚠️")
        print(f"⚠️ course_id inválido ou não mapeado: {course_id}")
        return

    cargo = discord.utils.get(message.guild.roles, name=cargo_nome)
    if cargo:
        await message.author.add_roles(cargo)
        await message.channel.send(f"{message.author.mention}, acesso liberado para **{cargo_nome}**! ✅")
        print(f"✅ Cargo '{cargo_nome}' atribuído para {message.author}")
    else:
        await message.channel.send(f"❌ Cargo '{cargo_nome}' não encontrado no servidor.")
        print(f"❌ Cargo '{cargo_nome}' não encontrado.")

# ================ INICIAR BOT ========================
client.run(TOKEN)