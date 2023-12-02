import discord
from discord import ui
from Database import Database

class DeleteMaterialButton(ui.Button):
    def __init__(self, bot, semester: str, course: str, material_id: int, material_title: str, week: int):
        super().__init__(style=discord.ButtonStyle.red, label=f"#{material_id} {material_title}", custom_id=f"delete_material_{material_id}")
        self.semester = semester
        self.course = course
        self.material_title = material_title
        self.material_id = material_id
        self.week = week
        self.bot = bot
        self.db: Database = bot.database
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        if self.db.delete_material(self.semester, self.course, self.material_id):
            await interaction.followup.send(f"`Material deleted successfully.`")
            await self.bot.send_logs(interaction, self.material_title, self.week, self.course, "Material Deleted")
        else:
            await interaction.followup.send(f"`Material deletion failed.`")
            await self.bot.send_logs(interaction, self.material_title, self.week, self.course, "Failed to Delete Material")

class DeleteMaterialView(ui.View):
    def __init__(self, bot, semester: str, course: str, materials, week: int):
        super().__init__(timeout=None)

        self.materials = materials
        if len(self.materials) == 0:
            return
        for material in self.materials:
            self.add_item(DeleteMaterialButton(bot, semester, course, material['id'], material['title'], week))