import discord
from discord import ui
from Database import Database

# TODO: Fetch links and link titles from the description
class MaterialWeeksView(ui.View):
    def __init__(self, bot, semester: str):
        super().__init__(timeout=None)
        self.add_item(MaterialWeeksDropDown(bot, semester))

class MaterialWeeksDropDown(ui.Select):
    def __init__(self, bot, semester: str):
        super().__init__(placeholder="Select Week", min_values=1, max_values=1, options=[], custom_id=f"week_select-{semester}")
        self.semester = semester
        self.bot = bot
        self.db: Database = bot.database
        self.weeks = sorted(set(self.db.get_semester_weeks(self.semester)))
        for week in self.weeks:
            self.add_option(label=f"Week {week}", value=week)
    
    async def callback(self, interaction: discord.Interaction):
        selected_week = int(self.values[0])
        await interaction.response.defer(ephemeral=True, thinking=True)
        embed = discord.Embed(title=f"Material for Week {selected_week}", description=f"Select a course to view its material for Week {selected_week}", color=discord.Color.blurple())
        coursesView = MaterialCoursesView(self.bot, self.semester, selected_week)
        await interaction.followup.send(embed=embed, view=coursesView)

class MaterialCoursesView(ui.View):
    def __init__(self, bot, semester: str, week: int):
        super().__init__(timeout=None)
        self.add_item(MaterialCoursesDropDown(bot, semester, week))

class MaterialCoursesDropDown(ui.Select):
    def __init__(self, bot, semester: str, week: int):
        super().__init__(placeholder="Select Course", min_values=1, max_values=1, options=[], custom_id="course_select")
        self.semester = semester
        self.bot = bot
        self.db: Database = bot.database
        self.week = week
        self.courses = self.db.get_semester_courses(self.semester)
        for course in self.courses:
            self.add_option(label=f"{course}", value=course)
    
    async def callback(self, interaction: discord.Interaction):
        selected_course = self.values[0]
        await interaction.response.defer(ephemeral=True, thinking=True)
        materials_view = MaterialsView(self.bot, self.semester, self.week, selected_course)
        materials = materials_view.materials
        available_materials_text = ""
        for material in materials:
            available_materials_text += f"• {material['title']}\n"
        if available_materials_text == "":
            available_materials_text = "No materials available for this week."
        else:
            available_materials_text += "\n**Select a material to view it**"

        embed = discord.Embed(title=f"Material for Week {self.week} - {selected_course}", description=f"**Available Materials:**\n{available_materials_text}", color=discord.Color.blurple())
        await interaction.followup.send(embed=embed, view=materials_view)


class MaterialsView(ui.View):
    def __init__(self, bot, semester: str, week: int, course: str):
        super().__init__(timeout=None)
        self.db: Database = bot.database
        self.materials = self.db.get_semester_course_materials_byweek(semester, course, week)
        if len(self.materials) == 0:
            return
        self.dropdown = MaterialsDropDown(bot, semester, week, course, self.materials)
        self.add_item(self.dropdown)

class MaterialsDropDown(ui.Select):
    def __init__(self, bot, semester: str, week: int, course: str, materials):
        super().__init__(placeholder="Select Material", min_values=1, max_values=1, options=[], custom_id="material_select")
        self.semester = semester
        self.bot = bot
        self.db: Database = bot.database
        self.week = week
        self.course = course
        self.materials = materials
        
        for material in self.materials:
            self.add_option(label=f"{material['title']}", value=material['id'])
    
    async def callback(self, interaction: discord.Interaction):
        selected_material = int(self.values[0])
        await interaction.response.defer(ephemeral=True, thinking=True) 
        material = self.db.get_semester_course_material(self.semester, self.course, selected_material)
        if material is None:
            await interaction.followup.send("`Material not found.`", ephemeral=True)
            return
        embed = discord.Embed(title=material['title'], description=f"Material for {self.course} - Week {self.week}", color=discord.Color.blurple())
        embed.set_footer(text="CUFE CMP 27")
        embed.set_thumbnail(url=interaction.guild.icon.url)
        if len(material['links']) > 0:
            link = material['links'][0]['link']
            if not link.startswith("http"):
                link = f"https://{link}"
            embed.add_field(name="Main Link", value=f"[{material['links'][0]['title']}]({link})", inline=False)

        if 'description' in material and len(material['description']) > 0:
            embed.add_field(name="Description (And other links)", value=material['description'], inline=False)

        await interaction.followup.send(embed=embed, view=SaveMaterialView(self.bot, embed, self.week, self.course, material['title']))

        await self.bot.send_logs(interaction, material['title'], self.week, self.course)
        
class SaveMaterialView(ui.View):
    def __init__(self, bot, embed: discord.Embed, week: int, course: str, material: str):
        super().__init__(timeout=None)
        self.add_item(SaveMaterialButton(bot, embed, week, course, material))

class SaveMaterialButton(ui.Button):
    def __init__(self, bot, embed: discord.Embed, week: int, course: str, material: str):
        super().__init__(style=discord.ButtonStyle.green, label="Save Material", custom_id="save_material")
        self.bot = bot
        self.embed = embed
        self.week = week
        self.course = course
        self.material = material
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            await interaction.user.send(content="Here's a copy of the requested material.", embed=self.embed)
            await interaction.followup.send("`The material has been saved to your DMs.`", ephemeral=True)
            await self.bot.send_logs(interaction, self.material, self.week, self.course, "saved")
        except:
            await interaction.followup.send("`You should enable your DMs to receive the material.`", ephemeral=True)
            await self.bot.send_logs(interaction, self.material, self.week, self.course, "failed to save")
            return