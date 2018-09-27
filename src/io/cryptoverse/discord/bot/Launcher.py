import discord
import requests
import re

# TODO
# Change to discord
# Periodically refresh users roles
client = discord.Client()
our_role_name = 'tt_only_owners'
our_channel_name = '_only_owners'


def get_privileges_handles_from_api():
    response = requests.get(
        'https://api.userfeeds.io/ranking/experimental_social_profiles;type=twitter/experimental_author_balance;asset'
        '=ethereum:0xc93058ca0cc2330b847c001c835fc926fedf5a07')
    items = response.json()['items']
    return [social_username(item['target']) for item in items]


def social_username(social_url):
    result = re.match('(:?\w|:)+(/.*)$', social_url)
    if result and result.group(1):
        return result.group(1)
    else:
        return social_url


@client.event
async def on_member_join(member):
    server = member.server
    print(server)
    print(member)
    discord_handles = get_privileges_handles_from_api()
    if member.name in discord_handles:
        print('Assigning our role to new member')
        role = discord.utils.get(server.roles, name=our_role_name)
        await client.add_roles(member, role)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    discord_handles = get_privileges_handles_from_api()
    for server in client.servers:
        role = discord.utils.get(server.roles, name=our_role_name)
        if not role:
            print('Creating role {0} in {1}'.format(our_role_name, server))
            role = await client.create_role(server, name=our_role_name)
        else:
            print('Role {0} found at {1}'.format(our_role_name, server))
        channel = discord.utils.get(client.get_all_channels(), server__name=server.name, name=our_channel_name)
        if not channel:
            print('Creating channel {0} in {1}'.format(our_channel_name, server))
            everyone_perms = discord.PermissionOverwrite(send_messages=False)
            owner_perms = discord.PermissionOverwrite(send_messages=True)
            everyone = discord.ChannelPermissions(target=server.default_role, overwrite=everyone_perms)
            owners = discord.ChannelPermissions(target=role, overwrite=owner_perms)
            await client.create_channel(server, our_channel_name, everyone, owners)
        else:
            print('Channel {0} found at {1}'.format(channel, server))

        for member in server.members:
            if member.name in discord_handles and role not in member.roles:
                print('Adding role to {0} member'.format(member.name))
                await client.add_roles(member, role)
            elif member.name in discord_handles and role in member.roles:
                print('{0} already has our role'.format(member.name))
            else:
                print('{0} does not own our token'.format(member.name))


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)


client.run('SECRET_TOKEN')
