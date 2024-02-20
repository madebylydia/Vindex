from prisma.models import Guild


Guild.create_partial('GuildWithLocale', include={'id': True, 'locale': True})
