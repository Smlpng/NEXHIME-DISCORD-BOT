from discord.ext import commands


class _ResponseProxy:
    def __init__(self, adapter):
        self.adapter = adapter

    async def send_message(self, *args, **kwargs):
        interaction = self.adapter.interaction
        if interaction is not None:
            if interaction.response.is_done():
                kwargs.setdefault("wait", True)
                self.adapter._original_message = await interaction.followup.send(*args, **kwargs)
            else:
                await interaction.response.send_message(*args, **kwargs)
                self.adapter._original_message = await interaction.original_response()
            return self.adapter._original_message

        kwargs.pop("ephemeral", None)
        kwargs.pop("wait", None)
        self.adapter._original_message = await self.adapter.ctx.send(*args, **kwargs)
        return self.adapter._original_message


class _FollowupProxy:
    def __init__(self, adapter):
        self.adapter = adapter

    async def send(self, *args, **kwargs):
        interaction = self.adapter.interaction
        if interaction is not None:
            kwargs.setdefault("wait", True)
            return await interaction.followup.send(*args, **kwargs)

        kwargs.pop("ephemeral", None)
        kwargs.pop("wait", None)
        return await self.adapter.ctx.send(*args, **kwargs)


class CommandContextAdapter:
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        self.interaction = getattr(ctx, "interaction", None)
        self.user = ctx.author
        self.guild = getattr(ctx, "guild", None)
        self.channel = getattr(ctx, "channel", None)
        self.response = _ResponseProxy(self)
        self.followup = _FollowupProxy(self)
        self._original_message = None

    async def original_response(self):
        if self.interaction is not None:
            if self._original_message is None:
                self._original_message = await self.interaction.original_response()
            return self._original_message
        return self._original_message

    async def delete_original_response(self):
        message = await self.original_response()
        if message is not None:
            await message.delete()
