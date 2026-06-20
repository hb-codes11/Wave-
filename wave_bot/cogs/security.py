import discord
from discord import app_commands
from discord.ext import commands

class Security(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Assign global tree error handler for slash commands
        bot.tree.on_error = self.on_app_command_error

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Missing argument: {error.param.name}. Please check the command usage.")
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("Sorry, that command doesn't exist.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have the necessary permissions to use this command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"I don't have the necessary permissions to perform this action. Please grant me: {', '.join(error.missing_permissions)}")
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send("This command cannot be used in private messages.")
        elif isinstance(error, commands.NotOwner):
            await ctx.send("Only the bot owner can use this command.")
        else:
            print(f"Unhandled command error: {error}")
            await ctx.send("An unexpected error occurred. Please try again later.")

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            message = f"⏱️ This command is on cooldown. Try again in {error.retry_after:.2f}s."
        elif isinstance(error, app_commands.MissingPermissions):
            message = "❌ You do not have the required permissions to run this command."
        elif isinstance(error, app_commands.BotMissingPermissions):
            message = f"❌ I am missing permissions to execute this: {', '.join(error.missing_permissions)}"
        else:
            print(f"Unhandled app command error: {error}")
            message = "⚠️ An unexpected error occurred. Please try again later."

        # Send response safely depending on whether interaction has been deferred/responded
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Security(bot))
