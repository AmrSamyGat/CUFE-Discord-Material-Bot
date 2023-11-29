import discord
from discord import ui
from Database import Database

# TODO: Fetch links and link titles from the description

class PushMaterialModal(ui.Modal):
    def __init__(self, bot, semester: str, course: str, week: int):
        super().__init__(timeout=None, title=f"Push new material for {course.title()}")
        self.semester = semester
        self.bot = bot
        self.course = course
        self.week = week
    mtitle = ui.TextInput(label='Material Title', placeholder='Enter the title of your material', style=discord.TextStyle.short)
    mlink = ui.TextInput(label='Material Link', placeholder='Link', style=discord.TextStyle.short)
    mlink_title = ui.TextInput(label='Link Title', placeholder='Link Title', style=discord.TextStyle.short)
    mdesc = ui.TextInput(label='Description', placeholder='Description of your material\nTo add more links add link_title:url\nEx. link_Lecture 2: link.com', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        db: Database = self.bot.database
        db.push_material(self.semester, self.course, self.mtitle.value, self.mdesc.value, self.week, [{"link":self.mlink.value, "title":self.mlink_title.value}])
        await interaction.response.send_message(f'Material pushed successfully to Week {self.week} For Course: `{self.course}`')
