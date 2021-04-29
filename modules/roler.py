import discord
from discord.ext import commands

from discord_slash import cog_ext, SlashContext, SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option

from .mongodb import collection

GUILD_IDS = [709954286376976425, 419214713252216848]


class Roler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild_ids = []

    @cog_ext.cog_subcommand(base="role", name="info", description="Information about a role", guild_ids=GUILD_IDS,
                            options=[
                                create_option(
                                    name="role",
                                    description="Role you want info on",
                                    option_type=SlashCommandOptionType.ROLE,
                                    required=True
                                )
                            ])
    async def role_info(self, ctx: SlashContext, role: discord.Role):
        role_info = collection("roles").find_one(role.id)

        e = discord.Embed()

        e.title = role.name

        e.description = "Assignable by:"

        if role_info:
            roles = [ctx.guild.get_role(i).mention for i in role_info["allowed_roles"]]

            e.description += "\n" + "\n".join(roles)

        await ctx.send(embed=e)


    @cog_ext.cog_subcommand(base="role", name="register", description="Registers a role for which people can assign", guild_ids=GUILD_IDS,
                            options=[
                                create_option(
                                    name="role",
                                    description="Role to be registered",
                                    option_type=SlashCommandOptionType.ROLE,
                                    required=True
                                ),
                                create_option(
                                    name="assignable_by",
                                    description="Who can assign this role? Blank = Everyone",
                                    option_type=SlashCommandOptionType.ROLE,
                                    required=False
                                )
                            ])
    @commands.has_permissions(administrator=True)
    async def role_register(self, ctx: SlashContext, role: discord.Role, assignable_by: discord.Role = None):

        if not assignable_by:
            assignable_by = ctx.guild.default_role

        if not collection("roles").find_one(role.id):
            collection("roles").insert_one({
                "_id": role.id,
                "server": ctx.guild_id,
                "allowed_roles": []
                })

        collection("roles").update_one({"_id": role.id}, {"$addToSet": {"allowed_roles": assignable_by.id}})


        await ctx.send(f"{role.mention} is now assignable by anyone with the role {assignable_by.mention}", hidden=True)

    @cog_ext.cog_subcommand(base="role", name="deregister", description="Registers a role for which people can assign", guild_ids=GUILD_IDS,
                            options=[
                                create_option(
                                    name="role",
                                    description="Role to be deregistered",
                                    option_type=SlashCommandOptionType.ROLE,
                                    required=True
                                ),
                                create_option(
                                    name="assignable_by",
                                    description="Who should be deregistered from this role? Blank = Everyone",
                                    option_type=SlashCommandOptionType.ROLE,
                                    required=False
                                )
                            ])
    @commands.has_permissions(administrator=True)
    async def role_deregister(self, ctx: SlashContext, role: discord.Role, assignable_by: discord.Role = None):
        if not assignable_by:
            assignable_by = ctx.guild.default_role

        if not collection("roles").find_one(role.id):
            await ctx.send(f"{role.mention} is no longer assignable by people with the role {assignable_by.mention}", hidden=True)

        collection("roles").update_one({"_id": role.id}, {"$pull": {"allowed_roles": assignable_by.id}})

        await ctx.send(f"{role.mention} is no longer assignable by people with the role {assignable_by.mention}", hidden=True)


    @cog_ext.cog_subcommand(base="role", name="assign", description="Assigns a role to someone", guild_ids=GUILD_IDS,
                            options=[
                                create_option(
                                    name="role",
                                    description="Role to be assigned",
                                    option_type=SlashCommandOptionType.ROLE,
                                    required=True
                                ),
                                create_option(
                                    name="user",
                                    description="User to assign this role to",
                                    option_type=SlashCommandOptionType.USER,
                                    required=True
                                )
                            ])
    async def role_assign(self, ctx: SlashContext, role: discord.Role, user: discord.Member):

        role_info = collection("roles").find_one(role.id)

        if not role_info:
            await ctx.send(f"You do not have permission to assign {role.mention}!", hidden=True)
            return

        valid_role_ids = set(role_info["allowed_roles"])
        author_role_ids = set([r.id for r in ctx.author.roles])

        if not valid_role_ids.intersection(author_role_ids):
            await ctx.send(f"You do not have permission to assign {role.mention}!", hidden=True)
            return

        try:
            roles = user.roles

            if role in user.roles:
                await ctx.send(f"{user.mention} already has {role.mention}", hidden=True)
                return

            roles.append(role)
            await user.edit(roles=roles)
            await ctx.send(f"I have added {role.mention} to {user.mention}.", hidden=True)
        except discord.HTTPException as e:
            print(e)
            await ctx.send(
                "I don't have permissions to edit roles for this member. Make sure that:\n1. I have a role placed higher than the member, and\n2. My role has the **Manage Roles** permission.", hidden=True)

    @cog_ext.cog_subcommand(base="role", name="revoke", description="Revokes a role from someone", guild_ids=GUILD_IDS,
                            options=[
                                create_option(
                                    name="role",
                                    description="Role to be revoked",
                                    option_type=SlashCommandOptionType.ROLE,
                                    required=True
                                ),
                                create_option(
                                    name="user",
                                    description="User to revoke this role from",
                                    option_type=SlashCommandOptionType.USER,
                                    required=True
                                )
                            ])
    async def role_revoke(self, ctx: SlashContext, role: discord.Role, user: discord.Member):

        role_info = collection("roles").find_one(role.id)

        if not role_info:
            await ctx.send(f"You do not have permission to revoke {role.mention}!", hidden=True)
            return

        valid_role_ids = set(role_info["allowed_roles"])
        author_role_ids = set([r.id for r in ctx.author.roles])

        if not valid_role_ids.intersection(author_role_ids):
            await ctx.send(f"You do not have permission to revoke {role.mention}!", hidden=True)
            return

        try:
            roles = user.roles

            if not role in user.roles:
                await ctx.send(f"{user.mention} does not have the role {role.mention}", hidden=True)
                return

            roles.remove(role)
            await user.edit(roles=roles)
            await ctx.send(f"I have removed {role.mention} from {user.mention}.", hidden=True)
        except discord.HTTPException as e:
            print(e)
            await ctx.send(
                "I don't have permissions to edit roles for this member. Make sure that:\n1. I have a role placed higher than the member, and\n2. My role has the **Manage Roles** permission.", hidden=True)


def setup(bot: commands.Bot):
    bot.add_cog(Roler(bot))
