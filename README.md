<img src="https://i.imgur.com/a1xgOQJ.png" width="152" height="152" align="left">

# Winston
[![](https://img.shields.io/github/license/MrArkon/JukeBox?style=for-the-badge&colorA=2B2424&colorB=F5EDED)](https://github.com/MrArkon/Winston/blob/rewrite/LICENSE)
[![](https://img.shields.io/discord/735831202799419454?label=discord&logo=discord&logoColor=white&style=for-the-badge&colorA=2B2424&colorB=F5EDED)](https://discord.gg/hzJCjzQpYr)
[![](https://img.shields.io/badge/discord.py-v2.1.0-A5CCFE?style=for-the-badge&logo=python&logoColor=white&colorA=2B2424&colorB=F5EDED)](https://github.com/Rapptz/discord.py/)

<br>

Winston is an open-source bot for discord written in [python](https://python.org/) with the help of [discord.py](https://github.com/Rapptz/discord.py/). It offers numerous utilities and moderation tools to enhance the experience of users on your discord server.

## Running
Before proceeding please ensure you have installed [python](https://python.org/) and [poetry](https://python-poetry.org/).

1. Install the project dependencies with the following command:

   ```bash
   poetry install
   ```
2. Rename the `config.toml.example` file to `config.toml` and fill in the required details.
3. Run the bot with the following command:
  
   ```bash
   poetry run python -m bot
   ```
## Contributing
I whole heartedly welcome all contributions to this project. When contributing please ensure to follow the guidelines listed below:

1. When creating a new file please paste the license summary at the top of the file.
2. This project uses black and isort to format the code. Please make sure you run the following command to format the code:

   ```bash
   black bot ; isort bot
   ```

## License
This project is licensed under the AGPL-3.0 license. See the file [`LICENSE`](https://github.com/MrArkon/Winston/blob/rewrite/LICENSE) for more information. 
If you plan to use any part of this source code in your own discord bot, I would be really grateful if you include some form of credit somewhere. 
