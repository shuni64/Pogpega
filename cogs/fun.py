import disnake as discord
from disnake.ext import commands
from PIL import Image, ImageSequence
from io import BytesIO
import requests
from cairosvg import svg2png

class Fun(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.you_know_what_that_means = []
        # loop through the frames in the directory
        for i in range(0, 21):
            # open the image
            img = Image.open(f'other/frames/frame_{i}.png')
            # append the image to the list
            self.you_know_what_that_means.append(img)
        print('You know what that means loaded')

    
    @commands.slash_command(name='youknowwhatthatmeans', description='Add an image to the "You know what that means" gif')
    @commands.install_types(guild=True, user=True)
    async def youknowwhatthatmeans(self, 
                  ctx: discord.ApplicationCommandInteraction, 
                  image: discord.Attachment = commands.Param(name='image', description='The image to add'),
                  sticker: bool = commands.Param(name='sticker', description='Resize the gif so it can be made into a discord sticker (default: false)', default=False)):
        await ctx.response.defer()
        # if image.content_type != 'image/png':
        #     await ctx.followup.send('The attachment must be a png image')
        #     return
        response = requests.get(image.url)
        img = Image.open(BytesIO(response.content)).convert('RGBA')
        # await image.save(f'other/frames/{ctx.guild_id}-{ctx.author.id}-{now}.png')
        # img = Image.open(f'other/frames/{ctx.guild_id}-{ctx.author.id}-{now}.png').convert('RGBA')
        youknowwhatthatmeans = self.you_know_what_that_means.copy()
        # Paste the image onto the youknowwhatthatmeans frames
        tmp = img.copy().resize((9, 9))
        youknowwhatthatmeans[6].paste(tmp, (242, 234, 251, 243), tmp)
        tmp = img.copy().resize((13, 13))
        youknowwhatthatmeans[7].paste(tmp, (253, 228, 266, 241), tmp)
        youknowwhatthatmeans[8].paste(tmp, (257, 226, 270, 239), tmp)
        youknowwhatthatmeans[9].paste(tmp, (272, 222, 285, 235), tmp)
        tmp = img.copy().resize((22, 21))
        youknowwhatthatmeans[10].paste(tmp, (280, 215, 302, 236), tmp)
        tmp = img.copy().resize((22, 20))
        youknowwhatthatmeans[11].paste(tmp, (291, 208, 313, 228), tmp)
        youknowwhatthatmeans[12].paste(tmp, (296, 204, 318, 224), tmp)
        tmp = img.copy().resize((27, 25))
        youknowwhatthatmeans[13].paste(tmp, (300, 189, 327, 214), tmp)
        tmp = img.copy().resize((31, 29))
        youknowwhatthatmeans[14].paste(tmp, (307, 185, 338, 214), tmp)
        tmp = img.copy().resize((32, 29))
        youknowwhatthatmeans[15].paste(tmp, (313, 181, 345, 210), tmp)
        tmp = img.copy().resize((36, 33))
        youknowwhatthatmeans[16].paste(tmp, (308, 183, 344, 216), tmp)
        tmp = img.copy().resize((47, 44))
        youknowwhatthatmeans[17].paste(tmp, (309, 169, 356, 213), tmp)
        tmp = img.copy().resize((89, 83))
        youknowwhatthatmeans[18].paste(tmp, (283, 141, 372, 224), tmp)
        tmp = img.copy().resize((110, 115))
        youknowwhatthatmeans[19].paste(tmp, (279, 125, 389, 240), tmp)
        tmp = img.copy().resize((379, 274))
        youknowwhatthatmeans[20].paste(tmp, (0, 102, 379, 376), tmp)

        # Delete the original image from the frames directory
        # os.remove(f'other/frames/{ctx.guild_id}-{ctx.author.id}-{now}.png')
        del img
        del tmp

        if sticker:
            # resize to 320x320
            for i in range(len(youknowwhatthatmeans)):
                youknowwhatthatmeans[i] = youknowwhatthatmeans[i].resize((320, 320))

        with BytesIO() as fp:
            youknowwhatthatmeans[0].save(fp, format='GIF', save_all=True, append_images=youknowwhatthatmeans[1:], duration=0.1, loop=0, optimize=True)
            fp.seek(0)
            # edit the message with an embed
            await ctx.followup.send(files=[discord.File(fp=fp, filename='youknowwhatthatmeans.gif')])

    @commands.slash_command(name='combine', description='Combine two emojis into one')
    @commands.install_types(guild=True, user=True)
    async def combine(self, 
                      ctx: discord.ApplicationCommandInteraction, 
                      emoji1: str = commands.Param(name='emoji1', description='The first emoji'),
                      emoji2: str = commands.Param(name='emoji2', description='The second emoji'),
                      emoji3: str = commands.Param(name='emoji3', description='The third emoji (optional)', default=None),
                      orientation: str = commands.Param(name='orientation', description='The orientation of the emojis (horizontal or vertical, default: horizontal)', choices=['horizontal', 'vertical'], default='horizontal'),
                      frametime: int = commands.Param(name='frametime', description='The time between frames in milliseconds if using gifs (default: 100)', default=100)):
        await ctx.response.defer()
        emote1 = discord.PartialEmoji.from_str(emoji1)
        emote2 = discord.PartialEmoji.from_str(emoji2)
        # Check if the emojis are unicode
        if emote1.id is None:
            ord1 = ''
            for char in emoji1:
                ord1 += "{:x}".format(ord(char)) + '-'
            ord1 = ord1[:-1]  # Remove the last dash
            # print(f"ord1: {ord1}")
            # print(f"emoji1: {emoji1}")
            # print(f"emote1: {emote1}")
            try:
                svg1 = svg2png(url="https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/svg/" + ord1 + ".svg", output_width=128, output_height=128)
                img1 = Image.open(BytesIO(svg1)).convert('RGBA')
            except Exception:
                await ctx.followup.send('Invalid emoji for emoji1')
                return
        else:
            response1 = requests.get(emote1.url)
            img1 = Image.open(BytesIO(response1.content))
        if emote2.id is None:
            ord2 = ''
            for char in emoji2:
                ord2 += "{:x}".format(ord(char)) + '-'
            ord2 = ord2[:-1]  # Remove the last dash
            try:
                svg2 = svg2png(url="https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/svg/" + ord2 + ".svg", output_width=128, output_height=128)
                img2 = Image.open(BytesIO(svg2)).convert('RGBA')
            except Exception:
                await ctx.followup.send('Invalid emoji for emoji2')
                return
        else:
            response2 = requests.get(emote2.url)
            img2 = Image.open(BytesIO(response2.content))
        if emoji3 is not None:
            emote3 = discord.PartialEmoji.from_str(emoji3)
            if emote3.id is None:
                ord3 = ''
                for char in emoji3:
                    ord3 += "{:x}".format(ord(char)) + '-'
                ord3 = ord3[:-1]  # Remove the last dash
                try:
                    svg3 = svg2png(url="https://cdn.jsdelivr.net/gh/twitter/twemoji@latest/assets/svg/" + ord3 + ".svg", output_width=128, output_height=128)
                    img3 = Image.open(BytesIO(svg3)).convert('RGBA')
                except Exception:
                    await ctx.followup.send('Invalid emoji for emoji3')
                    return
            else:
                response3 = requests.get(emote3.url)
                img3 = Image.open(BytesIO(response3.content))
            if emote1.animated or emote2.animated or emote3.animated:
                # print("Combining animated emojis")
                gif_frames = combine_gifs(img1, img2, orientation, img3)
                with BytesIO() as fp:
                    frametime = int(frametime)
                    gif_frames[0].save(fp, format='GIF', save_all=True, append_images=gif_frames[1:], loop=0, duration=frametime, disposal=2)
                    fp.seek(0)
                    await ctx.followup.send(files=[discord.File(fp=fp, filename='combined_emoji.gif')])
                    return
            else:
                # Resize the emojis to 43x128, 42x128, and 43x128
                img1 = img1.convert('RGBA').resize(ori(orientation, (43, 128)))
                img2 = img2.convert('RGBA').resize(ori(orientation, (42, 128)))
                img3 = img3.convert('RGBA').resize(ori(orientation, (43, 128)))
                # Create a new image with the size of 128x128
                combined_img = Image.new('RGBA', (128, 128))
                # Paste the emojis onto the new image
                combined_img.paste(img1, (0, 0), img1)
                combined_img.paste(img2, ori(orientation, (43, 0)), img2)
                combined_img.paste(img3, ori(orientation, (85, 0)), img3)
                # Save the combined image to a BytesIO object
                with BytesIO() as fp:
                    combined_img.save(fp, format='PNG')
                    fp.seek(0)
                    # Send the combined image as a file
                    await ctx.followup.send(files=[discord.File(fp=fp, filename='combined_emoji.png')])
            return
        else:
            if emote1.animated or emote2.animated:
                # print("Combining animated emojis")
                gif_frames = combine_gifs(img1, img2, orientation)
                with BytesIO() as fp:
                    frametime = int(frametime)
                    gif_frames[0].save(fp, format='GIF', save_all=True, append_images=gif_frames[1:], loop=0, duration=frametime, disposal=2)
                    fp.seek(0)
                    await ctx.followup.send(files=[discord.File(fp=fp, filename='combined_emoji.gif')])
                    return
            else:
                # Resize the emojis to 64x128
                img1 = img1.convert('RGBA').resize(ori(orientation, (64, 128)))
                img2 = img2.convert('RGBA').resize(ori(orientation, (64, 128)))
                # Create a new image with the size of 128x128
                combined_img = Image.new('RGBA', (128, 128))
                # Paste the emojis onto the new image
                combined_img.paste(img1, (0, 0), img1)
                combined_img.paste(img2, ori(orientation, (64, 0)), img2)
                # Save the combined image to a BytesIO object
                with BytesIO() as fp:
                    combined_img.save(fp, format='PNG')
                    fp.seek(0)
                    # Send the combined image as a file
                    await ctx.followup.send(files=[discord.File(fp=fp, filename='combined_emoji.png')])
                    return

def combine_gifs(gif1: Image.Image, gif2: Image.Image, o: str, gif3: Image.Image = None) -> list[Image.Image]:
    """
    Combine two GIFs into one by putting them beside each other in a 128x128 square. If they are different lengths, the shorter one will be looped to match the length of the longer one.
    """
    frames1 = [frame.copy() for frame in ImageSequence.Iterator(gif1)]
    frames2 = [frame.copy() for frame in ImageSequence.Iterator(gif2)]
    if gif3 is not None:
        frames3 = [frame.copy() for frame in ImageSequence.Iterator(gif3)]
        # print(f"Combining {len(frames1)} frames from gif1, {len(frames2)} frames from gif2, and {len(frames3)} frames from gif3")
        max_length = max(len(frames1), len(frames2), len(frames3))
    else:
        # print(f"Combining {len(frames1)} frames from gif1 and {len(frames2)} frames from gif2")
        max_length = max(len(frames1), len(frames2))
    combined_frames = []
    for i in range(max_length):
        frame1 = frames1[i % len(frames1)]
        frame2 = frames2[i % len(frames2)]
        combined_frame = Image.new('RGBA', (128, 128))
        if gif3 is not None:
            frame3 = frames3[i % len(frames3)]
            combined_frame.paste(frame1.resize(ori(o, (43, 128))), (0, 0))
            combined_frame.paste(frame2.resize(ori(o, (42, 128))), ori(o, (43, 0)))
            combined_frame.paste(frame3.resize(ori(o, (43, 128))), ori(o, (85, 0)))
        else:
            combined_frame.paste(frame1.resize(ori(o, (64, 128))), (0, 0))
            combined_frame.paste(frame2.resize(ori(o, (64, 128))), ori(o, (64, 0)))
        combined_frames.append(combined_frame)
    # combined_gif = Image.new('RGBA', (128, 128))
    # combined_gif.save('combined.gif', save_all=True, append_images=combined_frames, loop=0, duration=0.1)
    return combined_frames

def ori(orientation: str, coords: tuple[int, int]) -> tuple[int, int]:
    """
    Adjusts the coordinates based on the orientation.
    If orientation is 'horizontal', returns (x, y).
    If orientation is 'vertical', returns (y, x).
    """
    if orientation == 'horizontal':
        return coords
    elif orientation == 'vertical':
        return coords[1], coords[0]

def setup(bot: commands.Bot):
    bot.add_cog(Fun(bot))

def teardown(bot: commands.Bot):
    bot.remove_cog('Fun')